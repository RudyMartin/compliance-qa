"""
Temperature Router
==================
Routes inference requests based on temperature to appropriate reasoning engines.

Temperature controls the reasoning mode:
- T = 0.0: Pure symbolic (certifiable, rule-based)
- 0.0 < T < 0.5: Hybrid (combines rules + embeddings)
- T >= 0.5: Analogical (pure embedding-based)
"""

from typing import Optional, Dict, Any
from .inference_result import ReasoningMode, ProvenanceType


class TemperatureRouter:
    """
    Routes reasoning requests based on temperature parameter.

    The temperature metaphor comes from statistical mechanics and
    is used here to control the "rigidity" of reasoning:
    - Low T = rigid, deterministic (symbolic logic)
    - High T = flexible, probabilistic (neural analogies)
    """

    # Temperature thresholds
    SYMBOLIC_THRESHOLD = 0.001      # T <= 0.001 is pure symbolic
    HYBRID_THRESHOLD = 0.5          # T < 0.5 is hybrid
    # T >= 0.5 is pure analogical

    def __init__(
        self,
        symbolic_threshold: float = SYMBOLIC_THRESHOLD,
        hybrid_threshold: float = HYBRID_THRESHOLD
    ):
        """
        Initialize the temperature router.

        Args:
            symbolic_threshold: Max temperature for pure symbolic mode
            hybrid_threshold: Temperature threshold for hybrid/analogical split
        """
        self.symbolic_threshold = symbolic_threshold
        self.hybrid_threshold = hybrid_threshold

    def route(self, temperature: float) -> ReasoningMode:
        """
        Determine reasoning mode based on temperature.

        Args:
            temperature: Temperature value (0.0-1.0+)

        Returns:
            ReasoningMode enum value

        Examples:
            >>> router = TemperatureRouter()
            >>> router.route(0.0)
            ReasoningMode.SYMBOLIC
            >>> router.route(0.2)
            ReasoningMode.HYBRID
            >>> router.route(0.7)
            ReasoningMode.ANALOGICAL
        """
        # Clamp temperature to reasonable range
        temperature = max(0.0, min(temperature, 2.0))

        if temperature <= self.symbolic_threshold:
            return ReasoningMode.SYMBOLIC
        elif temperature < self.hybrid_threshold:
            return ReasoningMode.HYBRID
        else:
            return ReasoningMode.ANALOGICAL

    def get_provenance(self, mode: ReasoningMode) -> ProvenanceType:
        """
        Get provenance type for a reasoning mode.

        Args:
            mode: The reasoning mode

        Returns:
            ProvenanceType enum value
        """
        if mode == ReasoningMode.SYMBOLIC:
            return ProvenanceType.DEDUCTIVE
        elif mode == ReasoningMode.HYBRID:
            return ProvenanceType.HYBRID
        else:
            return ProvenanceType.ANALOGICAL

    def is_certifiable(
        self,
        mode: ReasoningMode,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Determine if a result can be certified based on reasoning mode.

        Pure symbolic reasoning is always certifiable.
        Hybrid/analogical may be certifiable if confidence is very high.

        Args:
            mode: The reasoning mode
            context: Optional context with additional info

        Returns:
            True if result can be certified
        """
        if mode == ReasoningMode.SYMBOLIC:
            return True

        # Hybrid/analogical requires additional checks
        if context:
            # Check if we have very high confidence
            confidence = context.get('confidence', 0.0)
            if confidence >= 0.95:
                return True

            # Check if symbolic rules strongly support the conclusion
            rule_support = context.get('rule_support', 0.0)
            if rule_support >= 0.9:
                return True

        return False

    def get_similarity_threshold(self, temperature: float) -> float:
        """
        Convert temperature to similarity threshold for embedding search.

        Higher temperature = lower threshold = more analogies considered.
        Lower temperature = higher threshold = only very similar cases.

        Args:
            temperature: Temperature value (0.0-1.0+)

        Returns:
            Similarity threshold (0.0-1.0)

        Examples:
            >>> router = TemperatureRouter()
            >>> router.get_similarity_threshold(0.0)
            1.0
            >>> router.get_similarity_threshold(0.5)
            0.5
            >>> router.get_similarity_threshold(1.0)
            0.0
        """
        # Clamp temperature
        temperature = max(0.0, min(temperature, 1.0))

        # Linear mapping: T=0 -> threshold=1.0, T=1 -> threshold=0.0
        return 1.0 - temperature

    def get_reasoning_weights(
        self,
        temperature: float
    ) -> Dict[str, float]:
        """
        Get weights for combining symbolic and analogical reasoning.

        Args:
            temperature: Temperature value (0.0-1.0)

        Returns:
            Dict with 'symbolic' and 'analogical' weights that sum to 1.0

        Examples:
            >>> router = TemperatureRouter()
            >>> router.get_reasoning_weights(0.0)
            {'symbolic': 1.0, 'analogical': 0.0}
            >>> router.get_reasoning_weights(0.25)
            {'symbolic': 0.75, 'analogical': 0.25}
            >>> router.get_reasoning_weights(0.5)
            {'symbolic': 0.5, 'analogical': 0.5}
        """
        # Clamp temperature
        temperature = max(0.0, min(temperature, 1.0))

        mode = self.route(temperature)

        if mode == ReasoningMode.SYMBOLIC:
            return {'symbolic': 1.0, 'analogical': 0.0}
        elif mode == ReasoningMode.ANALOGICAL:
            return {'symbolic': 0.0, 'analogical': 1.0}
        else:
            # Hybrid: interpolate based on temperature
            # At T=0.25: 75% symbolic, 25% analogical
            # At T=0.4: 20% symbolic, 80% analogical
            analogical_weight = temperature / self.hybrid_threshold
            symbolic_weight = 1.0 - analogical_weight
            return {
                'symbolic': symbolic_weight,
                'analogical': analogical_weight
            }

    def get_description(self, temperature: float) -> str:
        """
        Get human-readable description of reasoning mode for temperature.

        Args:
            temperature: Temperature value

        Returns:
            Description string
        """
        mode = self.route(temperature)

        descriptions = {
            ReasoningMode.SYMBOLIC: (
                f"Symbolic reasoning (T={temperature:.3f}): "
                "Pure rule-based, certifiable, deterministic"
            ),
            ReasoningMode.HYBRID: (
                f"Hybrid reasoning (T={temperature:.3f}): "
                "Combines compliance rules with similar case analysis"
            ),
            ReasoningMode.ANALOGICAL: (
                f"Analogical reasoning (T={temperature:.3f}): "
                "Learns from similar entities, exploratory"
            )
        }

        return descriptions[mode]

    def validate_temperature(self, temperature: float) -> bool:
        """
        Validate that temperature is in acceptable range.

        Args:
            temperature: Temperature to validate

        Returns:
            True if valid, False otherwise
        """
        return 0.0 <= temperature <= 2.0

    def suggest_temperature(
        self,
        use_case: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Suggest appropriate temperature for a use case.

        Args:
            use_case: Description of use case (e.g., "compliance_check")
            context: Optional context information

        Returns:
            Suggested temperature value
        """
        # Predefined suggestions for common use cases
        suggestions = {
            'compliance_check': 0.0,           # Must be certifiable
            'risk_screening': 0.1,             # Mostly rules, some flexibility
            'risk_analysis': 0.3,              # Balanced hybrid
            'exploratory_research': 0.7,       # Broad analogical search
            'entity_classification': 0.4,      # Moderate hybrid
            'document_review': 0.2,            # Mostly rule-based
            'similarity_search': 0.8,          # Heavy analogical
        }

        # Get suggestion or default to hybrid
        suggested = suggestions.get(use_case.lower(), 0.3)

        # Adjust based on context if provided
        if context:
            # If high stakes, reduce temperature
            if context.get('high_stakes', False):
                suggested *= 0.5

            # If regulatory, force symbolic
            if context.get('regulatory', False):
                suggested = 0.0

            # If exploratory flag, increase temperature
            if context.get('exploratory', False):
                suggested = min(suggested * 1.5, 1.0)

        return suggested

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TemperatureRouter("
            f"symbolic<={self.symbolic_threshold}, "
            f"hybrid<{self.hybrid_threshold})"
        )
