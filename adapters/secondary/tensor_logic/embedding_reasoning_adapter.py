"""
Embedding Reasoning Adapter
============================
Adapter implementing embedding-based soft reasoning using tidyllm-sentence.

This adapter implements Domingos's soft unification approach:
- Entities are represented as embeddings
- Similarity threshold controlled by temperature
- Inferences "borrowed" from similar entities with weighted voting
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import sys
import os

# Add packages to path
packages_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages', 'tidyllm-sentence')
if packages_path not in sys.path:
    sys.path.insert(0, packages_path)

from domain.ports.reasoning_ports import EmbeddingReasoningPort

# Import tidyllm-sentence (your package)
try:
    from tidyllm_sentence import (
        lsa_fit_transform,
        cosine_similarity,
        preprocess_for_embeddings,
        # NEW: High-level reasoning functions (Tensor Logic)
        analogical_reasoning,
        case_retrieval,
        temperature_sweep
    )
    TIDYLLM_SENTENCE_AVAILABLE = True
    TENSOR_LOGIC_AVAILABLE = True
except ImportError as e:
    # Try without new functions (backwards compatibility)
    try:
        from tidyllm_sentence import (
            lsa_fit_transform,
            cosine_similarity,
            preprocess_for_embeddings
        )
        TIDYLLM_SENTENCE_AVAILABLE = True
        TENSOR_LOGIC_AVAILABLE = False
        logging.warning("tidyllm-sentence available but Tensor Logic functions not found")
    except ImportError:
        TIDYLLM_SENTENCE_AVAILABLE = False
        TENSOR_LOGIC_AVAILABLE = False
        logging.warning("tidyllm-sentence not available, using fallback implementation")


logger = logging.getLogger(__name__)


class TidyLLMEmbeddingAdapter(EmbeddingReasoningPort):
    """
    Embedding-based reasoning adapter using tidyllm-sentence.

    Implements Pedro Domingos's soft unification:
    1. Represent entities as embeddings (LSA, TF-IDF, etc.)
    2. Find similar entities using cosine similarity
    3. Borrow inferences from similar entities
    4. Weight by similarity * (1 + temperature)
    5. Aggregate via weighted voting
    """

    def __init__(
        self,
        embedding_method: str = 'lsa',
        min_similarity: float = 0.3,
        max_similar_entities: int = 10
    ):
        """
        Initialize the embedding reasoning adapter.

        Args:
            embedding_method: Method to use ('lsa', 'tfidf', 'transformer')
            min_similarity: Minimum similarity threshold
            max_similar_entities: Maximum number of similar entities to consider
        """
        self.embedding_method = embedding_method
        self.min_similarity = min_similarity
        self.max_similar_entities = max_similar_entities

        # Entity database: entity_id -> (embedding, outcome, attributes)
        self.entity_db: Dict[str, Dict[str, Any]] = {}

        # Fitted vectorizer for transforming new entities
        self.vectorizer = None
        self.corpus_texts: List[str] = []

        logger.info(
            f"Initialized TidyLLMEmbeddingAdapter with method={embedding_method}"
        )

    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float
    ) -> Dict[str, Any]:
        """
        Execute embedding-based reasoning with temperature control.

        Args:
            query: The question to answer
            context: Context with 'entity_id', 'document', etc.
            temperature: Controls similarity threshold (0.0-1.0)

        Returns:
            Dict containing:
                - answer: The inferred result
                - confidence: Confidence score based on similarity
                - similar_entities: List of similar cases with scores
                - explanation: Natural language explanation
                - reasoning_trace: Details of analogical inference
        """
        logger.debug(f"Executing embedding reasoning for query: {query}, T={temperature}")

        # Get entity from context
        entity_id = context.get('entity_id')
        if not entity_id:
            return self._empty_result("No entity_id provided in context")

        # Get or create entity embedding
        if entity_id not in self.entity_db:
            # Create new entity
            entity_data = context.get('entity_data', context.get('document', {}))
            self.add_entity(entity_id, entity_data)

        # Convert temperature to similarity threshold
        # Higher T = lower threshold = more analogies
        similarity_threshold = max(self.min_similarity, 1.0 - temperature)

        # Find similar entities
        similar_entities = self.get_similar_entities(
            entity_id,
            threshold=similarity_threshold,
            top_k=self.max_similar_entities
        )

        if not similar_entities:
            return self._empty_result(
                f"No similar entities found above threshold {similarity_threshold:.2f}"
            )

        # Perform weighted voting (Domingos's key insight)
        result = self._weighted_inference(similar_entities, temperature, query)

        # Generate explanation
        explanation = self._generate_explanation(
            entity_id,
            similar_entities,
            result,
            temperature
        )

        return {
            'answer': result['answer'],
            'confidence': result['confidence'],
            'similar_entities': similar_entities,
            'explanation': explanation,
            'reasoning_trace': {
                'entity_id': entity_id,
                'similarity_threshold': similarity_threshold,
                'temperature': temperature,
                'num_similar': len(similar_entities),
                'weights': result['weights'],
                'vote_distribution': result['vote_distribution']
            }
        }

    def add_entity(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        outcome: Optional[Any] = None
    ) -> None:
        """
        Add an entity to the embedding database.

        Args:
            entity_id: Unique identifier
            entity_data: Entity attributes for embedding
            outcome: Known outcome (e.g., 'compliant', 'non_compliant')
        """
        # Convert entity to text representation
        entity_text = self._entity_to_text(entity_id, entity_data)

        # Add to entity database first (before recomputing embeddings)
        self.entity_db[entity_id] = {
            'embedding': None,  # Will be computed below
            'outcome': outcome,
            'attributes': entity_data,
            'text': entity_text
        }

        # Build corpus in consistent order
        self.corpus_texts = [
            self.entity_db[ent_id]['text']
            for ent_id in self.entity_db.keys()
        ]

        # Recompute embeddings for entire corpus
        if TIDYLLM_SENTENCE_AVAILABLE:
            # lsa_fit_transform returns (embeddings, model) tuple
            embeddings, self.vectorizer = lsa_fit_transform(self.corpus_texts)
        else:
            # Fallback: simple word overlap
            embeddings = [[1.0] for _ in self.corpus_texts]

        # Update all entities with their new embeddings
        for idx, ent_id in enumerate(self.entity_db.keys()):
            if idx < len(embeddings):
                self.entity_db[ent_id]['embedding'] = embeddings[idx]

        logger.debug(f"Added entity {entity_id} to database (total: {len(self.entity_db)})")

    def get_similar_entities(
        self,
        entity_id: str,
        threshold: float,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find entities similar to the given entity.

        Args:
            entity_id: Entity to find similarities for
            threshold: Minimum similarity score (0.0-1.0)
            top_k: Maximum number of results

        Returns:
            List of dicts with 'entity_id', 'similarity', 'outcome'
        """
        if entity_id not in self.entity_db:
            logger.warning(f"Entity {entity_id} not in database")
            return []

        query_entity = self.entity_db[entity_id]
        query_text = query_entity.get('text', '')

        # USE NEW HIGH-LEVEL FUNCTION if available (simpler, optimized)
        if TENSOR_LOGIC_AVAILABLE and query_text:
            return self._get_similar_entities_tensor_logic(
                query_text, entity_id, threshold, top_k
            )

        # FALLBACK: Original manual implementation
        query_embedding = query_entity['embedding']

        # Calculate similarities to all other entities
        similarities = []
        for ent_id, ent_data in self.entity_db.items():
            if ent_id == entity_id:
                continue  # Skip self

            similarity = self._compute_similarity(
                query_embedding,
                ent_data['embedding']
            )

            if similarity >= threshold:
                similarities.append({
                    'entity_id': ent_id,
                    'similarity': similarity,
                    'outcome': ent_data.get('outcome'),
                    'attributes': ent_data.get('attributes', {}),
                    'text': ent_data.get('text', '')
                })

        # Sort by similarity (descending) and take top k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    def _get_similar_entities_tensor_logic(
        self,
        query_text: str,
        query_entity_id: str,
        threshold: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Find similar entities using new high-level Tensor Logic functions.

        This is simpler and more efficient than manual similarity computation.
        Uses the new case_retrieval() function from tidyllm_sentence.
        """
        # Build case base from all entities except the query entity
        cases = []
        entity_ids = []

        for ent_id, ent_data in self.entity_db.items():
            if ent_id != query_entity_id:
                cases.append(ent_data.get('text', ''))
                entity_ids.append(ent_id)

        if not cases:
            return []

        # Use high-level case_retrieval function
        # This handles embedding generation, similarity computation, and top-k automatically
        results = case_retrieval(
            query=query_text,
            case_base=cases,
            method=self.embedding_method,
            top_k=top_k
        )

        # Convert results to our format and filter by threshold
        similar_entities = []
        for case_text, similarity in results:
            if similarity >= threshold:
                # Find which entity this case belongs to
                case_idx = cases.index(case_text)
                ent_id = entity_ids[case_idx]
                ent_data = self.entity_db[ent_id]

                similar_entities.append({
                    'entity_id': ent_id,
                    'similarity': similarity,
                    'outcome': ent_data.get('outcome'),
                    'attributes': ent_data.get('attributes', {}),
                    'text': case_text
                })

        logger.debug(
            f"Tensor Logic case_retrieval found {len(similar_entities)} "
            f"similar entities above threshold {threshold:.2f}"
        )

        return similar_entities

    def _weighted_inference(
        self,
        similar_entities: List[Dict[str, Any]],
        temperature: float,
        query: str
    ) -> Dict[str, Any]:
        """
        Perform weighted inference from similar entities.

        Implements Domingos's approach:
        - Weight = similarity * (1 + temperature)
        - Higher T = more weight to distant analogies

        Args:
            similar_entities: List of similar entities with scores
            temperature: Temperature value
            query: Original query

        Returns:
            Dict with answer, confidence, weights, vote distribution
        """
        # Calculate weights: similarity * (1 + temperature)
        weights = []
        outcomes = []
        total_weight = 0.0

        for entity in similar_entities:
            similarity = entity['similarity']
            outcome = entity.get('outcome')

            if outcome is None:
                continue  # Skip entities without known outcomes

            # Domingos's weighting: higher T gives more weight to distant analogies
            weight = similarity * (1.0 + temperature)
            weights.append(weight)
            outcomes.append(outcome)
            total_weight += weight

        if total_weight == 0:
            return {
                'answer': None,
                'confidence': 0.0,
                'weights': [],
                'vote_distribution': {}
            }

        # Aggregate outcomes by weighted voting
        vote_distribution = {}
        for outcome, weight in zip(outcomes, weights):
            outcome_str = str(outcome)
            vote_distribution[outcome_str] = vote_distribution.get(outcome_str, 0.0) + weight

        # Find outcome with highest weighted vote
        best_outcome = max(vote_distribution.items(), key=lambda x: x[1])[0]
        best_weight = vote_distribution[best_outcome]

        # Confidence = (best outcome weight) / (total weight)
        confidence = best_weight / total_weight if total_weight > 0 else 0.0

        return {
            'answer': best_outcome,
            'confidence': confidence,
            'weights': weights,
            'vote_distribution': vote_distribution
        }

    def _compute_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0.0-1.0)
        """
        if TIDYLLM_SENTENCE_AVAILABLE:
            # Use tidyllm-sentence cosine similarity
            return cosine_similarity([embedding1], [embedding2])[0][0]
        else:
            # Fallback: simple dot product
            if not embedding1 or not embedding2:
                return 0.0

            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)

    def _entity_to_text(
        self,
        entity_id: str,
        entity_data: Dict[str, Any]
    ) -> str:
        """
        Convert entity data to text representation for embedding.

        Args:
            entity_id: Entity identifier
            entity_data: Entity attributes

        Returns:
            Text representation
        """
        parts = [f"Entity: {entity_id}"]

        # Add all text-like attributes
        for key, value in entity_data.items():
            if isinstance(value, (str, int, float, bool)):
                parts.append(f"{key}: {value}")
            elif isinstance(value, dict):
                # Flatten nested dicts
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, (str, int, float, bool)):
                        parts.append(f"{key}.{subkey}: {subvalue}")

        text = ". ".join(parts)

        # DON'T preprocess here - lsa_fit_transform will handle it
        # preprocess_for_embeddings returns a token list, not a string
        return text

    def _get_entity_ids_in_order(self) -> List[str]:
        """
        Get entity IDs in the same order as corpus_texts.

        Returns:
            List of entity IDs
        """
        # Assumes entities were added in order
        return list(self.entity_db.keys())

    def _generate_explanation(
        self,
        entity_id: str,
        similar_entities: List[Dict[str, Any]],
        result: Dict[str, Any],
        temperature: float
    ) -> str:
        """
        Generate natural language explanation.

        Args:
            entity_id: Query entity ID
            similar_entities: Similar entities found
            result: Inference result
            temperature: Temperature value

        Returns:
            Explanation string
        """
        parts = []

        answer = result.get('answer')
        confidence = result.get('confidence', 0.0)

        parts.append(f"**Analogical Reasoning** (T={temperature:.2f})")
        parts.append(f"Inferred outcome: **{answer}** (confidence: {confidence:.1%})")
        parts.append("")

        parts.append(f"**Similar Entities** (found {len(similar_entities)}):")

        # Show top 3 similar entities
        for i, entity in enumerate(similar_entities[:3], 1):
            ent_id = entity['entity_id']
            similarity = entity['similarity']
            outcome = entity.get('outcome', 'unknown')

            parts.append(f"{i}. `{ent_id}` - Similarity: {similarity:.1%}, Outcome: {outcome}")

        if len(similar_entities) > 3:
            parts.append(f"... and {len(similar_entities) - 3} more similar entities")

        parts.append("")

        # Vote distribution
        vote_dist = result.get('vote_distribution', {})
        if vote_dist:
            parts.append("**Weighted Vote Distribution**:")
            total_weight = sum(vote_dist.values())
            for outcome, weight in sorted(vote_dist.items(), key=lambda x: -x[1]):
                percentage = (weight / total_weight * 100) if total_weight > 0 else 0
                parts.append(f"- {outcome}: {percentage:.1f}%")

        return "\n".join(parts)

    def _empty_result(self, message: str) -> Dict[str, Any]:
        """
        Create empty result with message.

        Args:
            message: Error or info message

        Returns:
            Empty result dict
        """
        return {
            'answer': None,
            'confidence': 0.0,
            'similar_entities': [],
            'explanation': message,
            'reasoning_trace': {}
        }

    def get_entity_count(self) -> int:
        """Get number of entities in database."""
        return len(self.entity_db)

    def clear_entities(self) -> None:
        """Clear all entities from database."""
        self.entity_db.clear()
        self.corpus_texts.clear()
        self.vectorizer = None
        logger.info("Cleared entity database")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TidyLLMEmbeddingAdapter("
            f"method={self.embedding_method}, "
            f"entities={len(self.entity_db)})"
        )
