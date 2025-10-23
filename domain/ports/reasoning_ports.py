"""
Reasoning Ports
===============
Port interfaces for the Tensor Logic domain service.
Defines contracts for symbolic, embedding-based, and trustworthiness scoring.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class SymbolicReasoningPort(ABC):
    """
    Port for symbolic/rule-based reasoning (T=0.0).

    This port enables deterministic, certifiable reasoning using
    compliance rules, logic programs, and formal specifications.
    """

    @abstractmethod
    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        rules: List[Any]
    ) -> Dict[str, Any]:
        """
        Execute symbolic reasoning over compliance rules.

        Args:
            query: The compliance question to answer
            context: Context including document, entities, metadata
            rules: List of compliance rules to check

        Returns:
            Dict containing:
                - answer: The reasoning result (bool, str, etc.)
                - rules_used: List of rule names that fired
                - violations: List of rule violations found
                - explanation: Natural language explanation
                - confidence: Confidence score (1.0 for symbolic)
        """
        pass


class EmbeddingReasoningPort(ABC):
    """
    Port for embedding-based soft reasoning (T>0.0).

    This port enables analogical reasoning using entity embeddings
    and semantic similarity to borrow inferences from similar cases.
    """

    @abstractmethod
    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float
    ) -> Dict[str, Any]:
        """
        Execute embedding-based reasoning with temperature control.

        Temperature controls the similarity threshold:
        - Higher T = broader similarity (more analogies)
        - Lower T = stricter similarity (fewer, more similar cases)

        Args:
            query: The question to answer
            context: Context including entity_id, document, etc.
            temperature: Controls similarity threshold (0.0-1.0)

        Returns:
            Dict containing:
                - answer: The inferred result
                - confidence: Confidence score based on similarity
                - similar_entities: List of similar cases with scores
                - explanation: Natural language explanation
                - reasoning_trace: Details of the analogical inference
        """
        pass

    @abstractmethod
    def add_entity(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        outcome: Optional[Any] = None
    ) -> None:
        """
        Add an entity to the embedding database.

        Args:
            entity_id: Unique identifier for the entity
            entity_data: Entity attributes for embedding
            outcome: Known outcome for this entity (optional)
        """
        pass

    @abstractmethod
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
        pass


class TrustworthinessPort(ABC):
    """
    Port for trustworthiness scoring.

    This port provides independent validation of AI-generated
    responses using Cleanlab's Trustworthy Language Model.
    """

    @abstractmethod
    def score(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score the trustworthiness of an AI response.

        Args:
            query: The original question
            response: The AI-generated response to validate
            context: Optional context for scoring

        Returns:
            Dict containing:
                - score: Trustworthiness score (0.0-1.0)
                - reliable: Boolean indicating if response is reliable
                - explanation: Explanation of the score
                - confidence: Confidence in the scoring itself
        """
        pass

    @abstractmethod
    def batch_score(
        self,
        queries: List[str],
        responses: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Score multiple query-response pairs in batch.

        Args:
            queries: List of questions
            responses: List of corresponding responses

        Returns:
            List of scoring results (same format as score())
        """
        pass


class HybridReasoningPort(ABC):
    """
    Port for hybrid reasoning combining symbolic and embedding approaches.

    This port enables flexible reasoning that can blend rule-based
    and analogical inference based on available evidence.
    """

    @abstractmethod
    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float,
        rules: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute hybrid reasoning combining symbolic and embedding methods.

        Args:
            query: The question to answer
            context: Context including document, entity, etc.
            temperature: Controls symbolic vs neural balance
            rules: Optional compliance rules

        Returns:
            Dict containing:
                - answer: The hybrid result
                - confidence: Combined confidence score
                - symbolic_evidence: Evidence from rule-based reasoning
                - analogical_evidence: Evidence from similar cases
                - explanation: Natural language explanation
                - certifiable: Whether result can be certified
        """
        pass
