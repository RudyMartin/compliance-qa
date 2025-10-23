"""
Tensor Logic Factory
====================
Factory for creating and configuring tensor logic services.

Handles:
- Dependency injection
- Environment configuration
- Service lifecycle
- Convenience constructors
"""

import os
import logging
from typing import Optional

from application.services.tensor_logic_application_service import (
    TensorLogicApplicationService
)
from domain.services.tensor_logic import TensorLogicService
from adapters.secondary.tensor_logic import (
    ComplianceRulesAdapter,
    TidyLLMEmbeddingAdapter,
    TidyLLMTrustworthinessAdapter,
    MockTrustworthinessAdapter,
    SmartHybridAdapter
)


logger = logging.getLogger(__name__)


class TensorLogicFactory:
    """
    Factory for creating tensor logic services.

    Provides multiple configuration options (ALL using YOUR packages - NO external APIs!):
    - create_default() - Standard configuration (YRSN trustworthiness)
    - create_with_tidyllm() - Full TidyLLM stack (recommended)
    - create_with_mock_trustworthiness() - For testing
    - create_minimal() - Domain service only (no application layer)
    """

    @staticmethod
    def create_default(
        embedding_method: str = 'lsa',
        use_tidyllm: bool = True
    ) -> TensorLogicApplicationService:
        """
        Create tensor logic application service with default configuration.

        Uses TidyLLM trustworthiness (YRSN framework) by default.
        NO external APIs required!

        Args:
            embedding_method: Embedding method ('lsa', 'tfidf', 'transformer')
            use_tidyllm: Use TidyLLM YRSN trustworthiness (default: True)

        Returns:
            Configured application service
        """
        logger.info("Creating tensor logic service with TidyLLM YRSN trustworthiness")

        return TensorLogicApplicationService(
            use_mock_trustworthiness=not use_tidyllm,
            embedding_method=embedding_method
        )

    @staticmethod
    def create_with_mock_trustworthiness(
        embedding_method: str = 'lsa'
    ) -> TensorLogicApplicationService:
        """
        Create service with mock trustworthiness (no API needed).

        Perfect for:
        - Development
        - Testing
        - Demos without API key

        Args:
            embedding_method: Embedding method

        Returns:
            Service with mock trustworthiness
        """
        logger.info("Creating tensor logic service with mock trustworthiness")

        return TensorLogicApplicationService(
            use_mock_trustworthiness=True,
            embedding_method=embedding_method
        )

    @staticmethod
    def create_with_tidyllm(
        embedding_method: str = 'lsa'
    ) -> TensorLogicApplicationService:
        """
        Create service with full TidyLLM stack (RECOMMENDED).

        Uses YOUR packages exclusively:
        - packages/tlm/ for ML scoring
        - packages/tidyllm-sentence/ for embeddings
        - YRSN framework for trustworthiness

        NO external APIs or paid services!

        Args:
            embedding_method: Embedding method ('lsa', 'tfidf', 'transformer')

        Returns:
            Service with TidyLLM YRSN trustworthiness
        """
        logger.info("Creating tensor logic service with full TidyLLM stack (YRSN)")

        return TensorLogicApplicationService(
            use_mock_trustworthiness=False,  # Use TidyLLM YRSN, not mock
            embedding_method=embedding_method
        )

    @staticmethod
    def create_minimal(
        use_tidyllm: bool = True
    ) -> TensorLogicService:
        """
        Create minimal tensor logic domain service.

        Returns bare domain service without application layer.
        Useful for low-level control or custom orchestration.

        Args:
            use_tidyllm: Use TidyLLM YRSN trustworthiness (default: True)

        Returns:
            TensorLogicService (domain layer)
        """
        logger.info("Creating minimal tensor logic domain service")

        # Create adapters (all YOUR packages!)
        symbolic = ComplianceRulesAdapter()
        embedding = TidyLLMEmbeddingAdapter()

        if use_tidyllm:
            trustworthiness = TidyLLMTrustworthinessAdapter()  # YRSN framework
        else:
            trustworthiness = MockTrustworthinessAdapter()  # Simple mock

        # Create domain service
        return TensorLogicService(
            symbolic_engine=symbolic,
            embedding_engine=embedding,
            trustworthiness_scorer=trustworthiness
        )

    @staticmethod
    def create_custom(
        symbolic_engine,
        embedding_engine,
        trustworthiness_scorer,
        hybrid_engine=None
    ) -> TensorLogicService:
        """
        Create tensor logic service with custom adapters.

        For advanced users who want complete control over configuration.

        Args:
            symbolic_engine: Custom symbolic reasoning adapter
            embedding_engine: Custom embedding reasoning adapter
            trustworthiness_scorer: Custom trustworthiness adapter
            hybrid_engine: Optional custom hybrid adapter

        Returns:
            TensorLogicService with custom adapters
        """
        logger.info("Creating tensor logic service with custom adapters")

        return TensorLogicService(
            symbolic_engine=symbolic_engine,
            embedding_engine=embedding_engine,
            trustworthiness_scorer=trustworthiness_scorer,
            hybrid_engine=hybrid_engine
        )


# Convenience functions
def create_tensor_logic_service(
    mode: str = 'auto',
    **kwargs
) -> TensorLogicApplicationService:
    """
    Convenience function to create tensor logic service.

    Uses YOUR TidyLLM packages exclusively - NO external APIs!

    Args:
        mode: Creation mode ('auto'/'tidyllm', 'mock', 'minimal')
        **kwargs: Additional arguments passed to factory method

    Returns:
        TensorLogicApplicationService

    Examples:
        >>> # TidyLLM YRSN (recommended, NO external APIs)
        >>> service = create_tensor_logic_service()

        >>> # Force TidyLLM
        >>> service = create_tensor_logic_service(mode='tidyllm')

        >>> # Mock for testing
        >>> service = create_tensor_logic_service(mode='mock')

        >>> # Minimal domain service
        >>> service = create_tensor_logic_service(mode='minimal')
    """
    factory = TensorLogicFactory()

    if mode == 'auto' or mode == 'tidyllm':
        return factory.create_with_tidyllm(**kwargs)
    elif mode == 'mock':
        return factory.create_with_mock_trustworthiness(**kwargs)
    elif mode == 'minimal':
        return factory.create_minimal(**kwargs)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'tidyllm', 'mock', or 'minimal'.")


def get_default_service() -> TensorLogicApplicationService:
    """
    Get default tensor logic service (auto-configured).

    Returns:
        TensorLogicApplicationService with auto-detected configuration
    """
    return TensorLogicFactory.create_default()
