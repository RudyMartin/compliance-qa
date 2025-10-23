"""
Tensor Logic Application Service
=================================
Application service orchestrating tensor logic use cases.

This service sits in the application layer and coordinates:
- Domain services (TensorLogicService)
- Adapters (via dependency injection)
- Use case workflows
- Cross-cutting concerns (logging, metrics, etc.)
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from domain.services.tensor_logic import (
    TensorLogicService,
    TemperatureRouter,
    InferenceResult,
    BatchInferenceResult,
    ReasoningMode
)
from adapters.secondary.tensor_logic import (
    ComplianceRulesAdapter,
    TidyLLMEmbeddingAdapter,
    TidyLLMTrustworthinessAdapter,
    MockTrustworthinessAdapter
)


logger = logging.getLogger(__name__)


class TensorLogicApplicationService:
    """
    Application service for tensor logic use cases.

    Responsibilities:
    - Orchestrate tensor logic workflows
    - Manage service lifecycle
    - Handle use case coordination
    - Provide simplified API for portals
    """

    def __init__(
        self,
        use_mock_trustworthiness: bool = False,
        embedding_method: str = 'lsa'
    ):
        """
        Initialize application service.

        Uses YOUR TidyLLM packages exclusively - NO external APIs!

        Args:
            use_mock_trustworthiness: Use simple mock instead of YRSN (default: False)
            embedding_method: Embedding method ('lsa', 'tfidf', 'transformer')
        """
        logger.info("Initializing TensorLogicApplicationService (TidyLLM-centric)")

        # Create adapters (all YOUR packages!)
        self.symbolic_adapter = ComplianceRulesAdapter()
        self.embedding_adapter = TidyLLMEmbeddingAdapter(
            embedding_method=embedding_method,
            min_similarity=0.3
        )

        # Choose trustworthiness adapter
        if use_mock_trustworthiness:
            self.trustworthiness_adapter = MockTrustworthinessAdapter(
                default_score=0.8
            )
            logger.info("Using MockTrustworthinessAdapter")
        else:
            self.trustworthiness_adapter = TidyLLMTrustworthinessAdapter()
            logger.info("Using TidyLLMTrustworthinessAdapter (YRSN framework)")

        # Create domain service
        self.tensor_logic_service = TensorLogicService(
            symbolic_engine=self.symbolic_adapter,
            embedding_engine=self.embedding_adapter,
            trustworthiness_scorer=self.trustworthiness_adapter
        )

        # Temperature router for utilities
        self.temperature_router = TemperatureRouter()

        logger.info("TensorLogicApplicationService initialized successfully")

    # =========================================================================
    # Use Case: Compliance Checking
    # =========================================================================

    def check_compliance(
        self,
        document: Dict[str, Any],
        compliance_standard: str = 'MVS_5.4.3',
        temperature: float = 0.0
    ) -> InferenceResult:
        """
        Use case: Check document compliance against standard.

        Args:
            document: Document to check
            compliance_standard: Standard to check against (e.g., 'MVS_5.4.3')
            temperature: Reasoning temperature (default 0.0 for certifiable)

        Returns:
            InferenceResult with compliance assessment
        """
        logger.info(f"Checking compliance: standard={compliance_standard}, T={temperature}")

        result = self.tensor_logic_service.infer(
            query=f"Is this document {compliance_standard} compliant?",
            context={
                'document': document,
                'compliance_standard': compliance_standard
            },
            temperature=temperature,
            compliance_standard=compliance_standard,
            score_trustworthiness=True
        )

        logger.info(
            f"Compliance check complete: answer={result.answer}, "
            f"certifiable={result.certifiable}"
        )

        return result

    def get_remediation_plan(
        self,
        document: Dict[str, Any],
        compliance_standard: str = 'MVS_5.4.3'
    ) -> List[Dict[str, Any]]:
        """
        Use case: Get remediation plan for non-compliant document.

        Args:
            document: Document to assess
            compliance_standard: Compliance standard

        Returns:
            List of remediation items
        """
        logger.info(f"Generating remediation plan: standard={compliance_standard}")

        # First check compliance
        result = self.check_compliance(document, compliance_standard, temperature=0.0)

        # If compliant, no remediation needed
        if result.answer == True or result.answer == 'COMPLIANT':
            return []

        # Get remediation plan from symbolic adapter
        compliance_details = result.reasoning_trace.get('symbolic_result', {}).get('details', {})

        remediation_plan = self.symbolic_adapter.generate_remediation_plan(
            compliance_details
        )

        logger.info(f"Generated {len(remediation_plan)} remediation items")

        return remediation_plan

    # =========================================================================
    # Use Case: Risk Assessment
    # =========================================================================

    def assess_risk(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        temperature: float = 0.3
    ) -> InferenceResult:
        """
        Use case: Assess risk for an entity using hybrid reasoning.

        Args:
            entity_id: Entity identifier
            entity_data: Entity attributes
            temperature: Reasoning temperature (0.2-0.4 recommended for risk)

        Returns:
            InferenceResult with risk assessment
        """
        logger.info(f"Assessing risk: entity={entity_id}, T={temperature}")

        # Ensure entity is in embedding database
        if entity_id not in self.embedding_adapter.entity_db:
            self.embedding_adapter.add_entity(
                entity_id=entity_id,
                entity_data=entity_data,
                outcome=None  # Unknown outcome
            )

        result = self.tensor_logic_service.infer(
            query="What is the risk level for this entity?",
            context={
                'entity_id': entity_id,
                'entity_data': entity_data,
                'document': entity_data
            },
            temperature=temperature,
            score_trustworthiness=True
        )

        logger.info(
            f"Risk assessment complete: confidence={result.confidence:.2f}"
        )

        return result

    # =========================================================================
    # Use Case: Entity Similarity Search
    # =========================================================================

    def find_similar_entities(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        temperature: float = 0.7,
        top_k: int = 10
    ) -> InferenceResult:
        """
        Use case: Find entities similar to the given entity.

        Args:
            entity_id: Entity to find similarities for
            entity_data: Entity attributes
            temperature: Temperature (higher = broader search)
            top_k: Maximum number of similar entities

        Returns:
            InferenceResult with similar entities
        """
        logger.info(f"Finding similar entities: entity={entity_id}, T={temperature}")

        # Ensure entity is in database
        if entity_id not in self.embedding_adapter.entity_db:
            self.embedding_adapter.add_entity(
                entity_id=entity_id,
                entity_data=entity_data,
                outcome=None
            )

        result = self.tensor_logic_service.infer(
            query=f"Find entities similar to {entity_id}",
            context={
                'entity_id': entity_id,
                'entity_data': entity_data
            },
            temperature=temperature,
            score_trustworthiness=False  # Not needed for similarity
        )

        logger.info(
            f"Found {len(result.similar_entities)} similar entities"
        )

        return result

    # =========================================================================
    # Use Case: Batch Processing
    # =========================================================================

    def batch_check_compliance(
        self,
        documents: List[Dict[str, Any]],
        compliance_standard: str = 'MVS_5.4.3',
        temperature: float = 0.0
    ) -> BatchInferenceResult:
        """
        Use case: Check multiple documents in batch.

        Args:
            documents: List of documents
            compliance_standard: Standard to check against
            temperature: Reasoning temperature

        Returns:
            BatchInferenceResult with all results
        """
        logger.info(f"Batch compliance check: {len(documents)} documents")

        queries = [
            f"Is this document {compliance_standard} compliant?"
            for _ in documents
        ]

        contexts = [
            {
                'document': doc,
                'compliance_standard': compliance_standard
            }
            for doc in documents
        ]

        batch_result = self.tensor_logic_service.batch_infer(
            queries=queries,
            contexts=contexts,
            temperature=temperature,
            compliance_standard=compliance_standard
        )

        logger.info(
            f"Batch check complete: success={batch_result.success_count}, "
            f"failed={batch_result.failure_count}"
        )

        return batch_result

    # =========================================================================
    # Training & Management
    # =========================================================================

    def add_training_entity(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        outcome: Any
    ) -> None:
        """
        Add a training entity with known outcome for analogical reasoning.

        Args:
            entity_id: Unique identifier
            entity_data: Entity attributes
            outcome: Known outcome (e.g., 'COMPLIANT', 'HIGH_RISK')
        """
        logger.info(f"Adding training entity: {entity_id} -> {outcome}")

        self.embedding_adapter.add_entity(
            entity_id=entity_id,
            entity_data=entity_data,
            outcome=outcome
        )

    def load_training_data(
        self,
        training_data: List[Dict[str, Any]]
    ) -> None:
        """
        Load multiple training entities at once.

        Args:
            training_data: List of dicts with 'entity_id', 'entity_data', 'outcome'
        """
        logger.info(f"Loading {len(training_data)} training entities")

        for item in training_data:
            self.add_training_entity(
                entity_id=item['entity_id'],
                entity_data=item['entity_data'],
                outcome=item['outcome']
            )

        logger.info("Training data loaded successfully")

    def get_entity_count(self) -> int:
        """Get number of entities in embedding database."""
        return self.embedding_adapter.get_entity_count()

    def clear_training_data(self) -> None:
        """Clear all training entities."""
        logger.info("Clearing training data")
        self.embedding_adapter.clear_entities()

    # =========================================================================
    # Utilities
    # =========================================================================

    def suggest_temperature(
        self,
        use_case: str,
        high_stakes: bool = False,
        regulatory: bool = False
    ) -> float:
        """
        Suggest appropriate temperature for a use case.

        Args:
            use_case: Use case name (e.g., 'compliance_check', 'risk_analysis')
            high_stakes: Whether this is high-stakes decision
            regulatory: Whether this is regulatory compliance

        Returns:
            Suggested temperature
        """
        context = {
            'high_stakes': high_stakes,
            'regulatory': regulatory
        }

        return self.temperature_router.suggest_temperature(use_case, context)

    def get_reasoning_mode(self, temperature: float) -> ReasoningMode:
        """Get reasoning mode for a temperature."""
        return self.temperature_router.route(temperature)

    def get_reasoning_description(self, temperature: float) -> str:
        """Get human-readable description of reasoning mode."""
        return self.temperature_router.get_description(temperature)

    def get_trustworthiness_status(self) -> Dict[str, Any]:
        """Get status of trustworthiness scoring."""
        return self.trustworthiness_adapter.get_api_status()

    # =========================================================================
    # Export/Import
    # =========================================================================

    def export_result(self, result: InferenceResult) -> Dict[str, Any]:
        """
        Export inference result to dictionary.

        Args:
            result: InferenceResult to export

        Returns:
            Dictionary representation
        """
        return result.to_dict()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'service': 'TensorLogicApplicationService',
            'entities_loaded': self.get_entity_count(),
            'trustworthiness_mode': 'mock' if isinstance(
                self.trustworthiness_adapter,
                MockTrustworthinessAdapter
            ) else 'cleanlab',
            'embedding_method': self.embedding_adapter.embedding_method,
            'available_rules': len(self.symbolic_adapter.get_available_rules()),
            'timestamp': datetime.now().isoformat()
        }

    def __repr__(self) -> str:
        """String representation."""
        if isinstance(self.trustworthiness_adapter, MockTrustworthinessAdapter):
            trust_mode = 'mock'
        elif isinstance(self.trustworthiness_adapter, TidyLLMTrustworthinessAdapter):
            trust_mode = 'YRSN'
        else:
            trust_mode = 'unknown'

        return (
            f"TensorLogicApplicationService("
            f"entities={self.get_entity_count()}, "
            f"trust={trust_mode})"
        )
