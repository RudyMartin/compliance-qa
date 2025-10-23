"""
Hybrid Reasoning Adapter
=========================
Adapter combining symbolic and embedding-based reasoning.

This adapter provides optimized hybrid reasoning by intelligently
combining rule-based and analogical approaches.
"""

from typing import Dict, Any, List, Optional
import logging

from domain.ports.reasoning_ports import (
    HybridReasoningPort,
    SymbolicReasoningPort,
    EmbeddingReasoningPort
)


logger = logging.getLogger(__name__)


class SmartHybridAdapter(HybridReasoningPort):
    """
    Smart hybrid reasoning adapter.

    Combines symbolic and embedding reasoning with intelligent fallback:
    1. Try symbolic reasoning first (fast, certifiable)
    2. If symbolic is inconclusive, use embedding reasoning
    3. Combine evidence with temperature-based weighting
    """

    def __init__(
        self,
        symbolic_engine: SymbolicReasoningPort,
        embedding_engine: EmbeddingReasoningPort
    ):
        """
        Initialize hybrid adapter.

        Args:
            symbolic_engine: Symbolic reasoning adapter
            embedding_engine: Embedding reasoning adapter
        """
        self.symbolic = symbolic_engine
        self.embedding = embedding_engine
        logger.info("Initialized SmartHybridAdapter")

    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        temperature: float,
        rules: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute hybrid reasoning with intelligent combination.

        Strategy:
        1. Execute symbolic reasoning (deterministic)
        2. Execute embedding reasoning (probabilistic)
        3. Combine results based on temperature and confidence

        Args:
            query: The question
            context: Context with document, entity_id, etc.
            temperature: Controls symbolic vs analogical balance
            rules: Optional compliance rules

        Returns:
            Dict with hybrid reasoning result
        """
        logger.debug(f"Executing hybrid reasoning, T={temperature}")

        # Calculate weights based on temperature
        # T=0.1 -> 80% symbolic, 20% analogical
        # T=0.4 -> 20% symbolic, 80% analogical
        symbolic_weight = max(0.0, 1.0 - (temperature * 2.0))
        analogical_weight = 1.0 - symbolic_weight

        # Execute symbolic reasoning
        symbolic_result = None
        symbolic_confidence = 0.0

        try:
            symbolic_result = self.symbolic.execute(query, context, rules or [])
            symbolic_confidence = symbolic_result.get('confidence', 0.0)
            logger.debug(f"Symbolic reasoning: confidence={symbolic_confidence}")
        except Exception as e:
            logger.warning(f"Symbolic reasoning failed: {e}")

        # Execute embedding reasoning
        embedding_result = None
        analogical_confidence = 0.0

        try:
            embedding_result = self.embedding.execute(query, context, temperature)
            analogical_confidence = embedding_result.get('confidence', 0.0)
            logger.debug(f"Embedding reasoning: confidence={analogical_confidence}")
        except Exception as e:
            logger.warning(f"Embedding reasoning failed: {e}")

        # Combine results
        if symbolic_result and embedding_result:
            return self._combine_results(
                symbolic_result,
                embedding_result,
                symbolic_weight,
                analogical_weight,
                query
            )
        elif symbolic_result:
            # Only symbolic available
            return self._symbolic_only(symbolic_result)
        elif embedding_result:
            # Only embedding available
            return self._embedding_only(embedding_result)
        else:
            # Both failed
            return self._empty_result("Both symbolic and embedding reasoning failed")

    def _combine_results(
        self,
        symbolic_result: Dict[str, Any],
        embedding_result: Dict[str, Any],
        symbolic_weight: float,
        analogical_weight: float,
        query: str
    ) -> Dict[str, Any]:
        """
        Intelligently combine symbolic and embedding results.

        Args:
            symbolic_result: Result from symbolic reasoning
            embedding_result: Result from embedding reasoning
            symbolic_weight: Weight for symbolic (0.0-1.0)
            analogical_weight: Weight for analogical (0.0-1.0)
            query: Original query

        Returns:
            Combined result dict
        """
        # Calculate combined confidence
        symbolic_conf = symbolic_result.get('confidence', 0.0)
        analogical_conf = embedding_result.get('confidence', 0.0)

        combined_confidence = (
            symbolic_weight * symbolic_conf +
            analogical_weight * analogical_conf
        )

        # Determine answer
        # If symbolic has high weight and high confidence, prefer it
        if symbolic_weight > 0.7 and symbolic_conf >= 0.9:
            final_answer = symbolic_result.get('answer')
            certifiable = True
            explanation_focus = "symbolic"
        # If analogical has high weight, prefer it
        elif analogical_weight > 0.7:
            final_answer = embedding_result.get('answer')
            certifiable = False
            explanation_focus = "analogical"
        # Otherwise, prefer symbolic if it's confident
        elif symbolic_conf > analogical_conf:
            final_answer = symbolic_result.get('answer')
            certifiable = symbolic_conf >= 0.95
            explanation_focus = "symbolic"
        else:
            final_answer = embedding_result.get('answer')
            certifiable = False
            explanation_focus = "analogical"

        # Combine explanations
        explanation = self._combine_explanations(
            symbolic_result.get('explanation', ''),
            embedding_result.get('explanation', ''),
            symbolic_weight,
            analogical_weight,
            explanation_focus
        )

        # Extract evidence
        symbolic_evidence = {
            'rules_used': symbolic_result.get('rules_used', []),
            'violations': symbolic_result.get('violations', []),
            'confidence': symbolic_conf
        }

        analogical_evidence = {
            'similar_entities': embedding_result.get('similar_entities', []),
            'confidence': analogical_conf
        }

        return {
            'answer': final_answer,
            'confidence': combined_confidence,
            'symbolic_evidence': symbolic_evidence,
            'analogical_evidence': analogical_evidence,
            'explanation': explanation,
            'certifiable': certifiable,
            'weights': {
                'symbolic': symbolic_weight,
                'analogical': analogical_weight
            },
            'reasoning_trace': {
                'symbolic_result': symbolic_result,
                'embedding_result': embedding_result,
                'combination_strategy': explanation_focus
            }
        }

    def _combine_explanations(
        self,
        symbolic_explanation: str,
        analogical_explanation: str,
        symbolic_weight: float,
        analogical_weight: float,
        focus: str
    ) -> str:
        """
        Combine symbolic and analogical explanations.

        Args:
            symbolic_explanation: Explanation from symbolic reasoning
            analogical_explanation: Explanation from analogical reasoning
            symbolic_weight: Weight for symbolic
            analogical_weight: Weight for analogical
            focus: Which to focus on ('symbolic' or 'analogical')

        Returns:
            Combined explanation
        """
        parts = []

        parts.append(f"**Hybrid Reasoning** (Symbolic: {symbolic_weight:.0%}, Analogical: {analogical_weight:.0%})")
        parts.append("")

        if focus == "symbolic" and symbolic_explanation:
            parts.append("**Primary Evidence (Symbolic Rules)**:")
            parts.append(symbolic_explanation)
            parts.append("")

            if analogical_explanation:
                parts.append("**Supporting Evidence (Similar Cases)**:")
                # Shortened version
                lines = analogical_explanation.split('\n')
                parts.append('\n'.join(lines[:5]))

        else:  # focus == "analogical"
            if analogical_explanation:
                parts.append("**Primary Evidence (Similar Cases)**:")
                parts.append(analogical_explanation)
                parts.append("")

            if symbolic_explanation:
                parts.append("**Supporting Evidence (Compliance Rules)**:")
                # Shortened version
                lines = symbolic_explanation.split('\n')
                parts.append('\n'.join(lines[:5]))

        return "\n".join(parts)

    def _symbolic_only(self, symbolic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format result when only symbolic reasoning is available."""
        return {
            'answer': symbolic_result.get('answer'),
            'confidence': symbolic_result.get('confidence', 1.0),
            'symbolic_evidence': {
                'rules_used': symbolic_result.get('rules_used', []),
                'violations': symbolic_result.get('violations', []),
                'confidence': symbolic_result.get('confidence', 1.0)
            },
            'analogical_evidence': {},
            'explanation': symbolic_result.get('explanation', ''),
            'certifiable': True,
            'weights': {'symbolic': 1.0, 'analogical': 0.0}
        }

    def _embedding_only(self, embedding_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format result when only embedding reasoning is available."""
        return {
            'answer': embedding_result.get('answer'),
            'confidence': embedding_result.get('confidence', 0.0),
            'symbolic_evidence': {},
            'analogical_evidence': {
                'similar_entities': embedding_result.get('similar_entities', []),
                'confidence': embedding_result.get('confidence', 0.0)
            },
            'explanation': embedding_result.get('explanation', ''),
            'certifiable': False,
            'weights': {'symbolic': 0.0, 'analogical': 1.0}
        }

    def _empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result with error message."""
        return {
            'answer': None,
            'confidence': 0.0,
            'symbolic_evidence': {},
            'analogical_evidence': {},
            'explanation': message,
            'certifiable': False,
            'weights': {'symbolic': 0.0, 'analogical': 0.0}
        }

    def __repr__(self) -> str:
        """String representation."""
        return "SmartHybridAdapter(symbolic+embedding)"
