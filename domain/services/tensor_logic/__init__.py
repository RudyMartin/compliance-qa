"""
Tensor Logic Domain Service
============================
Temperature-based reasoning service implementing Pedro Domingos's tensor logic.

This module provides:
- TensorLogicService: Main service for temperature-routed reasoning
- TemperatureRouter: Routes inference based on temperature
- InferenceResult: Result dataclasses with complete audit trail
- ReasoningMode: Enum for symbolic/hybrid/analogical modes

Usage:
    from domain.services.tensor_logic import (
        TensorLogicService,
        InferenceResult,
        ReasoningMode
    )
    from domain.ports.reasoning_ports import (
        SymbolicReasoningPort,
        EmbeddingReasoningPort
    )

    # Initialize service with adapters
    service = TensorLogicService(
        symbolic_engine=my_symbolic_adapter,
        embedding_engine=my_embedding_adapter,
        trustworthiness_scorer=my_scorer_adapter
    )

    # Perform inference
    result = service.infer(
        query="Is this document MVS compliant?",
        context={'document': doc},
        temperature=0.0  # Pure symbolic
    )

    print(result.answer)
    print(result.certifiable)
    print(result.explanation)
"""

from .tensor_logic_service import TensorLogicService
from .temperature_router import TemperatureRouter
from .inference_result import (
    InferenceResult,
    BatchInferenceResult,
    ReasoningMode,
    ProvenanceType,
    RuleEvidence,
    AnalogicalEvidence
)

__all__ = [
    'TensorLogicService',
    'TemperatureRouter',
    'InferenceResult',
    'BatchInferenceResult',
    'ReasoningMode',
    'ProvenanceType',
    'RuleEvidence',
    'AnalogicalEvidence'
]

__version__ = '0.1.0'
