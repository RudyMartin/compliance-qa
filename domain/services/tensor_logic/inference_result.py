"""
Inference Result
================
Data structures for tensor logic inference results.
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
from enum import Enum
from datetime import datetime


class ReasoningMode(Enum):
    """Reasoning mode based on temperature."""
    SYMBOLIC = "symbolic"          # T=0.0 - Pure rule-based
    HYBRID = "hybrid"              # 0.0 < T < 0.5 - Combined
    ANALOGICAL = "analogical"      # T >= 0.5 - Pure embedding-based


class ProvenanceType(Enum):
    """Type of reasoning provenance."""
    DEDUCTIVE = "deductive"        # From logical rules
    ANALOGICAL = "analogical"      # From similar cases
    HYBRID = "hybrid"              # Combined reasoning
    STATISTICAL = "statistical"    # From statistical patterns


@dataclass
class RuleEvidence:
    """Evidence from a symbolic rule."""
    rule_id: str
    rule_name: str
    fired: bool
    confidence: float = 1.0
    explanation: str = ""
    section: Optional[str] = None


@dataclass
class AnalogicalEvidence:
    """Evidence from a similar entity."""
    entity_id: str
    similarity_score: float
    outcome: Any
    weight: float
    attributes: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""


@dataclass
class InferenceResult:
    """
    Result of a tensor logic inference.

    This dataclass captures the complete reasoning trace including:
    - The answer itself
    - Confidence and trustworthiness scores
    - Reasoning mode and provenance
    - Evidence from symbolic and analogical reasoning
    - Audit trail information
    """

    # Core result
    answer: Any
    confidence: float
    reasoning_mode: ReasoningMode
    temperature: float

    # Provenance and traceability
    provenance: ProvenanceType
    certifiable: bool
    trustworthiness_score: float = 0.0

    # Evidence
    rules_applied: List[RuleEvidence] = field(default_factory=list)
    similar_entities: List[AnalogicalEvidence] = field(default_factory=list)

    # Explanation
    explanation: str = ""
    reasoning_trace: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    query: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0.0

    # Quality metrics
    rule_coverage: float = 0.0       # Fraction of rules that fired
    evidence_strength: float = 0.0    # Overall strength of evidence
    consistency_score: float = 1.0    # Internal consistency

    # Audit trail
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'answer': self.answer,
            'confidence': self.confidence,
            'reasoning_mode': self.reasoning_mode.value,
            'temperature': self.temperature,
            'provenance': self.provenance.value,
            'certifiable': self.certifiable,
            'trustworthiness_score': self.trustworthiness_score,
            'rules_applied': [
                {
                    'rule_id': r.rule_id,
                    'rule_name': r.rule_name,
                    'fired': r.fired,
                    'confidence': r.confidence,
                    'explanation': r.explanation
                }
                for r in self.rules_applied
            ],
            'similar_entities': [
                {
                    'entity_id': e.entity_id,
                    'similarity_score': e.similarity_score,
                    'outcome': e.outcome,
                    'weight': e.weight
                }
                for e in self.similar_entities
            ],
            'explanation': self.explanation,
            'reasoning_trace': self.reasoning_trace,
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'processing_time_ms': self.processing_time_ms,
            'rule_coverage': self.rule_coverage,
            'evidence_strength': self.evidence_strength,
            'consistency_score': self.consistency_score,
            'metadata': self.metadata
        }

    def is_reliable(self, threshold: float = 0.7) -> bool:
        """
        Check if the result is reliable based on multiple factors.

        Args:
            threshold: Minimum score for reliability (default 0.7)

        Returns:
            True if result is considered reliable
        """
        # Symbolic reasoning is always reliable if rules fired
        if self.reasoning_mode == ReasoningMode.SYMBOLIC:
            return len(self.rules_applied) > 0

        # For analogical/hybrid, check multiple factors
        factors = [
            self.confidence >= threshold,
            self.trustworthiness_score >= threshold,
            self.evidence_strength >= threshold * 0.8,
            self.consistency_score >= 0.9
        ]

        # Must pass at least 3 out of 4 checks
        return sum(factors) >= 3

    def get_summary(self) -> str:
        """Get a human-readable summary of the result."""
        mode_str = self.reasoning_mode.value.capitalize()
        cert_str = "✓ Certifiable" if self.certifiable else "⚠ Not certifiable"

        summary = f"""
Tensor Logic Inference Result
==============================
Mode: {mode_str} (T={self.temperature:.2f})
Answer: {self.answer}
Confidence: {self.confidence:.1%}
Trustworthiness: {self.trustworthiness_score:.1%}
{cert_str}

Evidence:
- Rules applied: {len(self.rules_applied)}
- Similar cases: {len(self.similar_entities)}
- Evidence strength: {self.evidence_strength:.1%}

{self.explanation}
"""
        return summary.strip()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"InferenceResult(answer={self.answer}, "
            f"confidence={self.confidence:.2f}, "
            f"mode={self.reasoning_mode.value}, "
            f"certifiable={self.certifiable})"
        )


@dataclass
class BatchInferenceResult:
    """Result of batch inference over multiple queries."""
    results: List[InferenceResult]
    total_processing_time_ms: float = 0.0
    success_count: int = 0
    failure_count: int = 0

    def get_average_confidence(self) -> float:
        """Calculate average confidence across all results."""
        if not self.results:
            return 0.0
        return sum(r.confidence for r in self.results) / len(self.results)

    def get_average_trustworthiness(self) -> float:
        """Calculate average trustworthiness across all results."""
        if not self.results:
            return 0.0
        return sum(r.trustworthiness_score for r in self.results) / len(self.results)

    def get_certifiable_count(self) -> int:
        """Count how many results are certifiable."""
        return sum(1 for r in self.results if r.certifiable)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'results': [r.to_dict() for r in self.results],
            'total_processing_time_ms': self.total_processing_time_ms,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'average_confidence': self.get_average_confidence(),
            'average_trustworthiness': self.get_average_trustworthiness(),
            'certifiable_count': self.get_certifiable_count()
        }
