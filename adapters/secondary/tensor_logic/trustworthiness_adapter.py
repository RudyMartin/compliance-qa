"""
Trustworthiness Adapter
========================
Adapter for scoring trustworthiness of AI responses using Cleanlab TLM.

IMPORTANT: This uses Cleanlab's Trustworthy Language Model (TLM),
which is DIFFERENT from the local 'tlm' package (your LLM interface).

- cleanlab_tlm: External service for trustworthiness scoring
- tlm (packages/tlm/): Your local LLM interface for response generation
"""

from typing import Dict, Any, List, Optional
import logging
import os

from domain.ports.reasoning_ports import TrustworthinessPort


logger = logging.getLogger(__name__)


# Try to import Cleanlab TLM (external package)
try:
    from cleanlab_tlm import TLM as CleanlabTLM
    CLEANLAB_TLM_AVAILABLE = True
except ImportError:
    CLEANLAB_TLM_AVAILABLE = False
    logger.warning(
        "cleanlab-tlm not installed. Install with: pip install cleanlab-tlm\n"
        "Trustworthiness adapter will use mock scoring."
    )


class CleanlabTrustworthinessAdapter(TrustworthinessPort):
    """
    Trustworthiness scoring adapter using Cleanlab TLM.

    Cleanlab TLM provides:
    - Trustworthiness scores (0.0-1.0) for LLM responses
    - Hallucination detection
    - Confidence calibration
    - Explanation of scores

    Note: Requires CLEANLAB_API_KEY environment variable.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        quality_preset: str = "medium",
        use_mock: bool = False
    ):
        """
        Initialize the trustworthiness adapter.

        Args:
            api_key: Cleanlab API key (or set CLEANLAB_API_KEY env var)
            quality_preset: Quality level ('low', 'medium', 'high', 'best')
            use_mock: If True, use mock scoring (for testing)
        """
        self.api_key = api_key or os.environ.get('CLEANLAB_API_KEY')
        self.quality_preset = quality_preset
        self.use_mock = use_mock or not CLEANLAB_TLM_AVAILABLE

        if not self.use_mock:
            if not self.api_key:
                logger.warning(
                    "No CLEANLAB_API_KEY found. Using mock scoring.\n"
                    "Set CLEANLAB_API_KEY environment variable to use real scoring."
                )
                self.use_mock = True
            else:
                # Initialize Cleanlab TLM client
                try:
                    self.tlm_client = CleanlabTLM(
                        api_key=self.api_key,
                        options={
                            "log": ["explanation"],
                            "quality_preset": self.quality_preset
                        }
                    )
                    logger.info(
                        f"Initialized Cleanlab TLM with quality preset: {quality_preset}"
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize Cleanlab TLM: {e}")
                    self.use_mock = True

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
            context: Optional context (e.g., source documents)

        Returns:
            Dict containing:
                - score: Trustworthiness score (0.0-1.0)
                - reliable: Boolean indicating if response is reliable
                - explanation: Explanation of the score
                - confidence: Confidence in the scoring itself
        """
        if self.use_mock:
            return self._mock_score(query, response, context)

        try:
            # Call Cleanlab TLM API
            result = self.tlm_client.get_trustworthiness_score(
                prompt=query,
                response=str(response)
            )

            trustworthiness_score = result.get('trustworthiness_score', 0.5)

            return {
                'score': trustworthiness_score,
                'reliable': trustworthiness_score > 0.7,
                'explanation': result.get('explanation', ''),
                'confidence': result.get('confidence_score', 1.0)
            }

        except Exception as e:
            logger.error(f"Cleanlab TLM scoring failed: {e}")
            # Fall back to mock scoring on error
            return self._mock_score(query, response, context)

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
            List of scoring results
        """
        if len(queries) != len(responses):
            raise ValueError("queries and responses must have same length")

        # Score each pair (could be optimized with batch API if available)
        results = []
        for query, response in zip(queries, responses):
            result = self.score(query, response)
            results.append(result)

        return results

    def _mock_score(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mock trustworthiness scoring (for testing/fallback).

        Uses simple heuristics to estimate trustworthiness:
        - Response length
        - Presence of uncertainty markers
        - Consistency with context

        Args:
            query: Question
            response: AI response
            context: Optional context

        Returns:
            Mock scoring result
        """
        response_str = str(response).lower()

        # Base score
        score = 0.6

        # Length check (very short or very long responses less trustworthy)
        response_len = len(response_str)
        if 50 <= response_len <= 500:
            score += 0.1
        elif response_len < 20:
            score -= 0.2

        # Uncertainty markers (reduce score)
        uncertainty_markers = [
            'maybe', 'perhaps', 'possibly', 'might', 'could',
            'not sure', 'unclear', 'uncertain', 'probably'
        ]
        uncertainty_count = sum(
            1 for marker in uncertainty_markers
            if marker in response_str
        )
        score -= min(0.3, uncertainty_count * 0.1)

        # Definitive statements (increase score)
        definitive_markers = [
            'compliant', 'non-compliant', 'satisfies', 'violates',
            'meets', 'fails', 'documented', 'validated'
        ]
        definitive_count = sum(
            1 for marker in definitive_markers
            if marker in response_str
        )
        score += min(0.2, definitive_count * 0.05)

        # Context consistency check
        if context:
            # Check if response mentions context elements
            context_str = str(context).lower()
            context_overlap = any(
                word in response_str
                for word in context_str.split()
                if len(word) > 5  # Only check longer words
            )
            if context_overlap:
                score += 0.1

        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))

        # Generate explanation
        explanation = self._generate_mock_explanation(score, response_str)

        return {
            'score': score,
            'reliable': score > 0.7,
            'explanation': explanation,
            'confidence': 0.6  # Mock scores have lower confidence
        }

    def _generate_mock_explanation(
        self,
        score: float,
        response: str
    ) -> str:
        """
        Generate explanation for mock score.

        Args:
            score: Trustworthiness score
            response: Response text

        Returns:
            Explanation string
        """
        if score >= 0.8:
            return (
                "High trustworthiness: Response appears definitive "
                "with appropriate length and minimal uncertainty."
            )
        elif score >= 0.6:
            return (
                "Moderate trustworthiness: Response is reasonable "
                "but may contain some uncertainty markers."
            )
        else:
            return (
                "Low trustworthiness: Response may be too short, "
                "contain excessive uncertainty, or lack context alignment."
            )

    def is_available(self) -> bool:
        """Check if Cleanlab TLM is available."""
        return CLEANLAB_TLM_AVAILABLE and not self.use_mock

    def get_api_status(self) -> Dict[str, Any]:
        """
        Get status of Cleanlab TLM API connection.

        Returns:
            Status dictionary
        """
        return {
            'available': CLEANLAB_TLM_AVAILABLE,
            'api_key_set': bool(self.api_key),
            'using_mock': self.use_mock,
            'quality_preset': self.quality_preset
        }

    def __repr__(self) -> str:
        """String representation."""
        mode = "mock" if self.use_mock else "real"
        return f"CleanlabTrustworthinessAdapter(mode={mode}, preset={self.quality_preset})"


class MockTrustworthinessAdapter(TrustworthinessPort):
    """
    Simple mock trustworthiness adapter for testing.

    Always returns fixed scores without external dependencies.
    """

    def __init__(self, default_score: float = 0.8):
        """
        Initialize mock adapter.

        Args:
            default_score: Default trustworthiness score
        """
        self.default_score = default_score

    def score(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Return fixed score."""
        return {
            'score': self.default_score,
            'reliable': self.default_score > 0.7,
            'explanation': f"Mock score: {self.default_score}",
            'confidence': 1.0
        }

    def batch_score(
        self,
        queries: List[str],
        responses: List[str]
    ) -> List[Dict[str, Any]]:
        """Return fixed scores for batch."""
        return [self.score(q, r) for q, r in zip(queries, responses)]

    def __repr__(self) -> str:
        """String representation."""
        return f"MockTrustworthinessAdapter(score={self.default_score})"
