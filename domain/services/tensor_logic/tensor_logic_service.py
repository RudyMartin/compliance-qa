"""
Tensor Logic Service
====================
Core domain service implementing temperature-based reasoning.

This service orchestrates symbolic, hybrid, and analogical reasoning
based on temperature, implementing Pedro Domingos's tensor logic approach.
"""

from typing import Optional, Dict, Any, List
import time
from datetime import datetime

from domain.ports.reasoning_ports import (
    SymbolicReasoningPort,
    EmbeddingReasoningPort,
    TrustworthinessPort,
    HybridReasoningPort
)
from .inference_result import (
    InferenceResult,
    ReasoningMode,
    ProvenanceType,
    RuleEvidence,
    AnalogicalEvidence,
    BatchInferenceResult
)
from .temperature_router import TemperatureRouter


class TensorLogicService:
    """
    Domain service for temperature-based reasoning over compliance data.

    This service implements the core tensor logic approach:
    1. Route by temperature (T) to determine reasoning mode
    2. Execute appropriate reasoning (symbolic, hybrid, or analogical)
    3. Score trustworthiness of all results
    4. Provide complete audit trail

    The service follows hexagonal architecture - it depends on ports
    (interfaces) that are implemented by adapters in the infrastructure layer.
    """

    def __init__(
        self,
        symbolic_engine: Optional[SymbolicReasoningPort] = None,
        embedding_engine: Optional[EmbeddingReasoningPort] = None,
        trustworthiness_scorer: Optional[TrustworthinessPort] = None,
        hybrid_engine: Optional[HybridReasoningPort] = None,
        temperature_router: Optional[TemperatureRouter] = None
    ):
        """
        Initialize the tensor logic service.

        Args:
            symbolic_engine: Port for symbolic reasoning (T=0.0)
            embedding_engine: Port for embedding-based reasoning (T>0.0)
            trustworthiness_scorer: Port for scoring response quality
            hybrid_engine: Optional port for hybrid reasoning
            temperature_router: Optional custom router (uses default if None)
        """
        self.symbolic = symbolic_engine
        self.embedding = embedding_engine
        self.trustworthiness = trustworthiness_scorer
        self.hybrid = hybrid_engine
        self.router = temperature_router or TemperatureRouter()

    def infer(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float = 0.1,
        compliance_standard: Optional[str] = None,
        score_trustworthiness: bool = True
    ) -> InferenceResult:
        """
        Main inference method with temperature-based routing.

        Args:
            query: The question to answer
            context: Context including documents, entities, metadata
            temperature: Controls symbolic vs neural reasoning (0.0-1.0+)
            compliance_standard: E.g., "MVS_5.4.3", "VST_3.0"
            score_trustworthiness: Whether to score result trustworthiness

        Returns:
            InferenceResult with complete reasoning trace

        Examples:
            >>> service = TensorLogicService(symbolic, embedding, scorer)
            >>> result = service.infer(
            ...     "Is this document compliant with MVS 5.4.3?",
            ...     {'document': doc, 'entity_id': 'ent_123'},
            ...     temperature=0.0,
            ...     compliance_standard='MVS_5.4.3'
            ... )
            >>> print(result.answer, result.certifiable)
            True True
        """
        start_time = time.time()

        # Validate temperature
        if not self.router.validate_temperature(temperature):
            raise ValueError(f"Invalid temperature: {temperature}. Must be 0.0-2.0")

        # Determine reasoning mode
        mode = self.router.route(temperature)
        provenance = self.router.get_provenance(mode)

        # Execute appropriate reasoning
        if mode == ReasoningMode.SYMBOLIC:
            result = self._symbolic_reasoning(
                query, context, compliance_standard
            )
        elif mode == ReasoningMode.HYBRID:
            result = self._hybrid_reasoning(
                query, context, temperature, compliance_standard
            )
        else:  # ANALOGICAL
            result = self._analogical_reasoning(
                query, context, temperature
            )

        # Score trustworthiness (if enabled and scorer available)
        if score_trustworthiness and self.trustworthiness:
            trust_score = self._score_trustworthiness(query, result.answer, context)
            result.trustworthiness_score = trust_score['score']
            result.reasoning_trace['trustworthiness_details'] = trust_score

        # Add metadata
        processing_time = (time.time() - start_time) * 1000  # milliseconds
        result.processing_time_ms = processing_time
        result.query = query
        result.timestamp = datetime.now()
        result.metadata.update({
            'compliance_standard': compliance_standard,
            'temperature': temperature,
            'mode_description': self.router.get_description(temperature)
        })

        return result

    def _symbolic_reasoning(
        self,
        query: str,
        context: Dict[str, Any],
        compliance_standard: Optional[str]
    ) -> InferenceResult:
        """
        Pure symbolic reasoning using compliance rules (T=0.0).

        Args:
            query: The question to answer
            context: Context including document, metadata
            compliance_standard: Which standard to check (e.g., "MVS_5.4.3")

        Returns:
            InferenceResult with symbolic reasoning trace
        """
        if not self.symbolic:
            raise RuntimeError("Symbolic reasoning engine not configured")

        # Load compliance rules for standard
        rules = self._load_compliance_rules(compliance_standard, context)

        # Execute symbolic reasoning
        symbolic_result = self.symbolic.execute(query, context, rules)

        # Convert to InferenceResult
        rule_evidences = [
            RuleEvidence(
                rule_id=rule_id,
                rule_name=rule_id,
                fired=True,
                confidence=1.0,
                explanation=f"Rule {rule_id} applied"
            )
            for rule_id in symbolic_result.get('rules_used', [])
        ]

        # Calculate rule coverage
        total_rules = len(rules) if rules else 1
        fired_rules = len(rule_evidences)
        rule_coverage = fired_rules / total_rules if total_rules > 0 else 0.0

        return InferenceResult(
            answer=symbolic_result.get('answer'),
            confidence=1.0,  # Symbolic is deterministic
            reasoning_mode=ReasoningMode.SYMBOLIC,
            temperature=0.0,
            provenance=ProvenanceType.DEDUCTIVE,
            certifiable=True,
            trustworthiness_score=0.0,  # Will be filled if scoring enabled
            rules_applied=rule_evidences,
            similar_entities=[],
            explanation=symbolic_result.get('explanation', ''),
            reasoning_trace={
                'rules_used': symbolic_result.get('rules_used', []),
                'violations': symbolic_result.get('violations', []),
                'symbolic_result': symbolic_result
            },
            rule_coverage=rule_coverage,
            evidence_strength=1.0 if rule_evidences else 0.0,
            consistency_score=1.0
        )

    def _hybrid_reasoning(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float,
        compliance_standard: Optional[str]
    ) -> InferenceResult:
        """
        Hybrid reasoning combining symbolic rules with embedding-based inference.

        Args:
            query: The question to answer
            context: Context including document, entity, etc.
            temperature: Controls symbolic vs analogical balance
            compliance_standard: Which standard to check

        Returns:
            InferenceResult with hybrid reasoning trace
        """
        # If dedicated hybrid engine exists, use it
        if self.hybrid:
            rules = self._load_compliance_rules(compliance_standard, context)
            hybrid_result = self.hybrid.execute(query, context, temperature, rules)

            return self._convert_hybrid_result(hybrid_result, temperature)

        # Otherwise, combine symbolic and embedding engines
        if not self.symbolic or not self.embedding:
            raise RuntimeError("Hybrid reasoning requires both symbolic and embedding engines")

        # Get reasoning weights based on temperature
        weights = self.router.get_reasoning_weights(temperature)

        # First try symbolic
        try:
            rules = self._load_compliance_rules(compliance_standard, context)
            symbolic_result = self.symbolic.execute(query, context, rules)
        except Exception as e:
            # If symbolic fails, record but continue
            symbolic_result = {
                'answer': None,
                'confidence': 0.0,
                'rules_used': [],
                'explanation': f"Symbolic reasoning failed: {str(e)}"
            }

        # Get analogical evidence
        embedding_result = self.embedding.execute(query, context, temperature)

        # Combine results based on weights
        combined_confidence = (
            weights['symbolic'] * symbolic_result.get('confidence', 0.0) +
            weights['analogical'] * embedding_result.get('confidence', 0.0)
        )

        # If symbolic gives definitive answer with high weight, prefer it
        if weights['symbolic'] > 0.7 and symbolic_result.get('confidence', 0) == 1.0:
            final_answer = symbolic_result.get('answer')
            certifiable = True
        else:
            final_answer = embedding_result.get('answer')
            certifiable = False

        # Build evidence lists
        rule_evidences = [
            RuleEvidence(
                rule_id=rule_id,
                rule_name=rule_id,
                fired=True,
                confidence=weights['symbolic'],
                explanation=f"Rule {rule_id} (weight: {weights['symbolic']:.2f})"
            )
            for rule_id in symbolic_result.get('rules_used', [])
        ]

        analogical_evidences = [
            AnalogicalEvidence(
                entity_id=ent['entity_id'],
                similarity_score=ent['similarity'],
                outcome=ent.get('outcome'),
                weight=ent.get('weight', ent['similarity'] * weights['analogical']),
                explanation=f"Similar entity (similarity: {ent['similarity']:.2f})"
            )
            for ent in embedding_result.get('similar_entities', [])
        ]

        # Combine explanations
        combined_explanation = self._combine_explanations(
            symbolic_result.get('explanation', ''),
            embedding_result.get('explanation', ''),
            weights
        )

        return InferenceResult(
            answer=final_answer,
            confidence=combined_confidence,
            reasoning_mode=ReasoningMode.HYBRID,
            temperature=temperature,
            provenance=ProvenanceType.HYBRID,
            certifiable=certifiable,
            trustworthiness_score=0.0,
            rules_applied=rule_evidences,
            similar_entities=analogical_evidences,
            explanation=combined_explanation,
            reasoning_trace={
                'weights': weights,
                'symbolic_result': symbolic_result,
                'embedding_result': embedding_result
            },
            rule_coverage=len(rule_evidences) / max(len(rules), 1) if rules else 0.0,
            evidence_strength=(
                weights['symbolic'] * len(rule_evidences) +
                weights['analogical'] * len(analogical_evidences)
            ) / 10.0,  # Normalize
            consistency_score=0.8  # Hybrid is less consistent than pure symbolic
        )

    def _analogical_reasoning(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float
    ) -> InferenceResult:
        """
        Pure embedding-based analogical reasoning (T >= 0.5).

        Args:
            query: The question to answer
            context: Context including entity_id, etc.
            temperature: Controls similarity threshold

        Returns:
            InferenceResult with analogical reasoning trace
        """
        if not self.embedding:
            raise RuntimeError("Embedding reasoning engine not configured")

        # Execute embedding-based reasoning
        embedding_result = self.embedding.execute(query, context, temperature)

        # Convert similar entities to evidence
        analogical_evidences = [
            AnalogicalEvidence(
                entity_id=ent['entity_id'],
                similarity_score=ent['similarity'],
                outcome=ent.get('outcome'),
                weight=ent.get('weight', ent['similarity']),
                attributes=ent.get('attributes', {}),
                explanation=f"Similar entity with {ent['similarity']:.1%} similarity"
            )
            for ent in embedding_result.get('similar_entities', [])
        ]

        # Calculate evidence strength
        if analogical_evidences:
            avg_similarity = sum(e.similarity_score for e in analogical_evidences) / len(analogical_evidences)
            evidence_strength = avg_similarity
        else:
            evidence_strength = 0.0

        return InferenceResult(
            answer=embedding_result.get('answer'),
            confidence=embedding_result.get('confidence', 0.0),
            reasoning_mode=ReasoningMode.ANALOGICAL,
            temperature=temperature,
            provenance=ProvenanceType.ANALOGICAL,
            certifiable=False,  # Analogical reasoning is not certifiable
            trustworthiness_score=0.0,
            rules_applied=[],
            similar_entities=analogical_evidences,
            explanation=embedding_result.get('explanation', ''),
            reasoning_trace={
                'embedding_result': embedding_result,
                'similarity_threshold': self.router.get_similarity_threshold(temperature)
            },
            rule_coverage=0.0,
            evidence_strength=evidence_strength,
            consistency_score=0.7  # Analogical is exploratory
        )

    def batch_infer(
        self,
        queries: List[str],
        contexts: List[Dict[str, Any]],
        temperature: float = 0.1,
        compliance_standard: Optional[str] = None
    ) -> BatchInferenceResult:
        """
        Perform batch inference over multiple queries.

        Args:
            queries: List of questions
            contexts: List of corresponding contexts
            temperature: Temperature for all queries
            compliance_standard: Compliance standard to check

        Returns:
            BatchInferenceResult with all individual results
        """
        if len(queries) != len(contexts):
            raise ValueError("queries and contexts must have same length")

        start_time = time.time()
        results = []
        success_count = 0
        failure_count = 0

        for query, context in zip(queries, contexts):
            try:
                result = self.infer(query, context, temperature, compliance_standard)
                results.append(result)
                success_count += 1
            except Exception as e:
                # Record failure but continue
                failure_count += 1
                # Could add error result here

        total_time = (time.time() - start_time) * 1000

        return BatchInferenceResult(
            results=results,
            total_processing_time_ms=total_time,
            success_count=success_count,
            failure_count=failure_count
        )

    def _load_compliance_rules(
        self,
        compliance_standard: Optional[str],
        context: Dict[str, Any]
    ) -> List[Any]:
        """
        Load compliance rules for a given standard.

        Args:
            compliance_standard: Standard identifier (e.g., "MVS_5.4.3")
            context: Context that may contain rules

        Returns:
            List of compliance rules
        """
        # Check if rules provided in context
        if 'rules' in context:
            return context['rules']

        # Otherwise, would load from rules repository
        # For now, return empty list (adapter will handle)
        return []

    def _score_trustworthiness(
        self,
        query: str,
        answer: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score trustworthiness of an answer.

        Args:
            query: The original question
            answer: The generated answer
            context: Additional context

        Returns:
            Dict with trustworthiness scoring details
        """
        try:
            return self.trustworthiness.score(query, str(answer), context)
        except Exception as e:
            # If scoring fails, return neutral score
            return {
                'score': 0.5,
                'reliable': False,
                'explanation': f"Trustworthiness scoring failed: {str(e)}",
                'confidence': 0.0
            }

    def _combine_explanations(
        self,
        symbolic_explanation: str,
        analogical_explanation: str,
        weights: Dict[str, float]
    ) -> str:
        """
        Combine symbolic and analogical explanations.

        Args:
            symbolic_explanation: Explanation from symbolic reasoning
            analogical_explanation: Explanation from analogical reasoning
            weights: Reasoning weights

        Returns:
            Combined explanation string
        """
        parts = []

        if weights['symbolic'] > 0 and symbolic_explanation:
            parts.append(
                f"**Symbolic Evidence ({weights['symbolic']:.0%})**:\n"
                f"{symbolic_explanation}"
            )

        if weights['analogical'] > 0 and analogical_explanation:
            parts.append(
                f"**Analogical Evidence ({weights['analogical']:.0%})**:\n"
                f"{analogical_explanation}"
            )

        return "\n\n".join(parts) if parts else "No explanation available"

    def _convert_hybrid_result(
        self,
        hybrid_result: Dict[str, Any],
        temperature: float
    ) -> InferenceResult:
        """Convert hybrid engine result to InferenceResult."""
        return InferenceResult(
            answer=hybrid_result.get('answer'),
            confidence=hybrid_result.get('confidence', 0.0),
            reasoning_mode=ReasoningMode.HYBRID,
            temperature=temperature,
            provenance=ProvenanceType.HYBRID,
            certifiable=hybrid_result.get('certifiable', False),
            trustworthiness_score=0.0,
            rules_applied=[],  # Would parse from hybrid_result
            similar_entities=[],  # Would parse from hybrid_result
            explanation=hybrid_result.get('explanation', ''),
            reasoning_trace=hybrid_result
        )

    def __repr__(self) -> str:
        """String representation."""
        engines = []
        if self.symbolic:
            engines.append("symbolic")
        if self.embedding:
            engines.append("embedding")
        if self.hybrid:
            engines.append("hybrid")
        if self.trustworthiness:
            engines.append("trustworthiness")

        return f"TensorLogicService(engines=[{', '.join(engines)}])"
