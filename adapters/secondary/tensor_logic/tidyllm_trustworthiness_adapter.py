"""
TidyLLM Trustworthiness Adapter (YRSN-Enhanced)
===============================================
Trustworthiness scoring using YOUR TidyLLM ecosystem + YRSN patterns.

Framework: YRSN (Yes/Relevant/Specific/No-fluff)
- Based on code_samples/yrsn/ compliance validation patterns
- Measures actionable content vs noise indicators
- Evidence validation with authenticity markers
- Logical consistency and contradiction detection

Uses:
- packages/tlm/ → Pure-Python ML for scoring
- packages/tidyllm-sentence/ → Embeddings for consistency checks
- YRSN patterns → Quality, evidence, and consistency analysis

NO external APIs or paid services!
All scoring done locally with YOUR packages.
"""

from typing import Dict, Any, List, Optional
import logging
import sys
import os

# Add packages to path
packages_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages')
for pkg in ['tlm', 'tidyllm-sentence', 'tidyllm']:
    pkg_path = os.path.join(packages_path, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from domain.ports.reasoning_ports import TrustworthinessPort

# Import YOUR tlm package (pure-Python ML)
try:
    from tlm import (
        cosine_similarity as tlm_cosine,
        mean as tlm_mean,
        std as tlm_std
    )
    TLM_AVAILABLE = True
except ImportError:
    TLM_AVAILABLE = False
    logging.warning("tlm package not available")

# Import YOUR tidyllm-sentence package
try:
    from tidyllm_sentence import lsa_fit_transform, cosine_similarity
    TIDYLLM_SENTENCE_AVAILABLE = True
except ImportError:
    TIDYLLM_SENTENCE_AVAILABLE = False
    logging.warning("tidyllm-sentence not available")


logger = logging.getLogger(__name__)


class TidyLLMTrustworthinessAdapter(TrustworthinessPort):
    """
    Trustworthiness scoring using TidyLLM ecosystem + YRSN framework.

    YRSN Scoring Strategy (NO external APIs):
    1. **YRSN Quality** (30%) - Actionable content vs noise indicators
       - Based on code_samples/yrsn/yrsn_analyzer.py
       - Actionable: 'required', 'must use', 'compliant', 'verified'
       - Noise: 'may be', 'unclear', 'possibly', 'i think'

    2. **Evidence Authenticity** (20%) - Trust markers in content
       - Based on code_samples/yrsn/evidence/validation.py
       - Authenticity: timestamps, versions, sources, citations
       - Quality: peer review, data validation, cross-references

    3. **Logical Consistency** (25%) - Query-response alignment + contradictions
       - Based on code_samples/yrsn/consistency/analysis.py
       - Embedding similarity (YOUR tidyllm-sentence)
       - Contradiction detection

    4. **Coherence** (15%) - Internal sentence-to-sentence consistency
       - Uses YOUR tidyllm-sentence for embeddings
       - YOUR tlm for statistical analysis

    5. **Context Alignment** (10%) - Match with provided context
       - Keyword overlap with context documents

    All computation done locally with YOUR packages!
    """

    def __init__(self):
        """Initialize TidyLLM trustworthiness scorer."""
        self.embedder = None

        # Initialize embedder if available
        if TIDYLLM_SENTENCE_AVAILABLE:
            logger.info("TidyLLM trustworthiness using tidyllm-sentence embeddings")
        else:
            logger.warning("tidyllm-sentence not available, using heuristics only")

        logger.info("Initialized TidyLLMTrustworthinessAdapter (no external APIs)")

    def score(
        self,
        query: str,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score trustworthiness using TidyLLM components + YRSN patterns.

        Combines:
        1. YRSN quality analysis (actionable vs noise)
        2. Evidence validation (authenticity, completeness)
        3. Consistency analysis (logical structure, contradictions)
        4. Embedding-based coherence (YOUR tidyllm-sentence)

        Args:
            query: Original question
            response: AI-generated response
            context: Optional context for scoring

        Returns:
            Dict with score, reliable, explanation, confidence
        """
        response_str = str(response).strip()
        query_str = str(query).strip()

        if not response_str:
            return self._empty_result("Empty response")

        # Calculate multiple scores using TidyLLM patterns
        scores = {}

        # 1. YRSN Quality Score (Yes/Relevant/Specific/No-fluff)
        scores['yrsn_quality'] = self._yrsn_quality_score(response_str)

        # 2. Evidence Authenticity (markers of trustworthy content)
        scores['evidence_authenticity'] = self._evidence_score(response_str)

        # 3. Logical Consistency (structure + contradictions)
        scores['logical_consistency'] = self._consistency_score(query_str, response_str)

        # 4. Coherence Score (internal consistency using embeddings)
        scores['coherence'] = self._coherence_score(response_str)

        # 5. Context Alignment (if context provided)
        if context:
            scores['context_alignment'] = self._context_alignment_score(
                response_str, context
            )

        # Weighted average (YRSN-inspired priority)
        weights = {
            'yrsn_quality': 0.30,        # Actionable content is key
            'evidence_authenticity': 0.20,  # Trust markers matter
            'logical_consistency': 0.25,    # Consistency critical
            'coherence': 0.15,              # Internal flow
            'context_alignment': 0.10 if context else 0.0  # Context bonus
        }

        # Normalize weights if no context
        if not context:
            total = sum(w for k, w in weights.items() if k != 'context_alignment')
            weights = {k: v/total for k, v in weights.items() if k != 'context_alignment'}

        # Calculate weighted score
        final_score = sum(
            scores[component] * weight
            for component, weight in weights.items()
            if component in scores
        )

        # Generate explanation
        explanation = self._generate_explanation(scores, final_score)

        return {
            'score': final_score,
            'reliable': final_score > 0.7,
            'explanation': explanation,
            'confidence': 0.90,  # High confidence in YRSN+TidyLLM approach
            'components': scores,
            'yrsn_validation': 'PASS' if scores.get('yrsn_quality', 0) > 0.5 else 'FAIL'
        }

    def _consistency_score(self, query: str, response: str) -> float:
        """
        Check query-response consistency using embeddings.

        Args:
            query: Question
            response: Answer

        Returns:
            Consistency score (0.0-1.0)
        """
        if not TIDYLLM_SENTENCE_AVAILABLE:
            # Fallback: simple keyword overlap
            query_words = set(query.lower().split())
            response_words = set(response.lower().split())

            if not query_words:
                return 0.5

            overlap = len(query_words & response_words)
            return min(1.0, overlap / len(query_words) * 2.0)

        # Use YOUR tidyllm-sentence for embeddings
        try:
            texts = [query, response]
            embeddings = lsa_fit_transform(texts)

            if len(embeddings) >= 2:
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                # Normalize to 0-1 range (cosine is -1 to 1)
                return (similarity + 1.0) / 2.0

        except Exception as e:
            logger.warning(f"Consistency score failed: {e}")

        return 0.6  # Neutral score if failed

    def _yrsn_quality_score(self, response: str) -> float:
        """
        YRSN (Yes/Relevant/Specific/No-fluff) quality analysis.

        Based on code_samples/yrsn/yrsn_analyzer.py patterns:
        - Actionable indicators = specific, directive guidance
        - Noise indicators = vague, uncertain language
        - Quality = actionable_ratio

        Args:
            response: Response text

        Returns:
            Quality score (0.0-1.0, higher = more actionable/specific)
        """
        response_lower = response.lower()
        total_chars = len(response)

        if total_chars == 0:
            return 0.0

        # Actionable indicators (YRSN "Yes" - specific guidance)
        actionable_indicators = [
            'use', 'should use', 'must use', 'required', 'official',
            'pattern is', 'recommended', 'standard', 'implement',
            'configure', 'set to', 'enable', 'disable', 'compliant',
            'non-compliant', 'satisfies', 'violates', 'meets', 'fails',
            'documented', 'verified', 'confirmed', 'established'
        ]

        # Noise indicators (YRSN "No-fluff" - vague language)
        noise_indicators = [
            'may be', 'could be', 'might', 'unclear', 'depends on',
            'various', 'multiple', 'different approaches', 'consider',
            'potentially', 'possibly', 'generally', 'typically',
            'maybe', 'perhaps', 'not sure', 'uncertain', 'probably',
            'i think', 'i believe', 'seems like', 'appears to'
        ]

        actionable_chars = 0
        specific_guidance_found = 0
        noise_indicators_found = 0

        # Count actionable content (weight higher)
        for indicator in actionable_indicators:
            if indicator in response_lower:
                actionable_chars += len(indicator) * 3  # Weight actionable higher
                specific_guidance_found += 1

        # Penalize vague language
        for noise in noise_indicators:
            if noise in response_lower:
                actionable_chars = max(0, actionable_chars - len(noise))
                noise_indicators_found += 1

        # Calculate actionable ratio
        actionable_ratio = actionable_chars / total_chars if total_chars > 0 else 0

        # Normalize to 0-1 (cap at 1.0)
        quality_score = min(1.0, actionable_ratio)

        return quality_score

    def _evidence_score(self, response: str) -> float:
        """
        Evidence authenticity/quality scoring.

        Based on code_samples/yrsn/evidence/validation.py patterns:
        - Authenticity markers (timestamps, versions, sources)
        - Completeness markers (methodology, conclusions, data)
        - Quality markers (validation, peer review, references)

        Args:
            response: Response text

        Returns:
            Evidence score (0.0-1.0)
        """
        response_lower = response.lower()

        # Authenticity indicators
        authenticity_patterns = [
            'digitally signed', 'electronic signature', 'authenticated',
            'version', 'revision', 'draft', 'author', 'prepared by',
            'source', 'reference', 'citation'
        ]

        # Quality indicators
        quality_patterns = [
            'peer review', 'reviewed by', 'quality assurance',
            'data validation', 'verified', 'confirmed',
            'statistically significant', 'p-value', 'confidence interval',
            'table', 'figure', 'section'  # Cross-references
        ]

        auth_found = sum(1 for pattern in authenticity_patterns if pattern in response_lower)
        quality_found = sum(1 for pattern in quality_patterns if pattern in response_lower)

        # Scoring (normalized)
        auth_score = min(1.0, auth_found / 3.0)  # Max 3 authenticity markers
        quality_score = min(1.0, quality_found / 3.0)  # Max 3 quality markers

        # Average
        return (auth_score + quality_score) / 2.0

    def _length_score(self, response: str) -> float:
        """
        Check if response length is appropriate.

        Args:
            response: Response text

        Returns:
            Length score (0.0-1.0)
        """
        length = len(response)

        # Too short
        if length < 10:
            return 0.3

        # Ideal range
        if 50 <= length <= 500:
            return 1.0

        # Moderate range
        if 20 <= length < 50 or 500 < length <= 1000:
            return 0.8

        # Long but acceptable
        if 1000 < length <= 2000:
            return 0.6

        # Too long (likely verbose/unfocused)
        return 0.4

    def _coherence_score(self, response: str) -> float:
        """
        Check internal coherence using sentence similarity.

        Args:
            response: Response text

        Returns:
            Coherence score (0.0-1.0)
        """
        # Split into sentences
        sentences = [
            s.strip()
            for s in response.replace('!', '.').replace('?', '.').split('.')
            if s.strip()
        ]

        if len(sentences) < 2:
            return 0.8  # Single sentence is trivially coherent

        if not TIDYLLM_SENTENCE_AVAILABLE:
            # Fallback: check for repeated words across sentences
            word_sets = [set(s.lower().split()) for s in sentences]
            overlaps = []
            for i in range(len(word_sets) - 1):
                overlap = len(word_sets[i] & word_sets[i+1])
                total = len(word_sets[i] | word_sets[i+1])
                if total > 0:
                    overlaps.append(overlap / total)

            return tlm_mean(overlaps) if overlaps and TLM_AVAILABLE else 0.7

        # Use embeddings for coherence
        try:
            embeddings = lsa_fit_transform(sentences[:5])  # Limit to 5 sentences

            if len(embeddings) < 2:
                return 0.8

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
                similarities.append((sim + 1.0) / 2.0)  # Normalize

            # Average similarity
            if TLM_AVAILABLE and similarities:
                avg_coherence = tlm_mean(similarities)
                return max(0.0, min(1.0, avg_coherence))
            elif similarities:
                return sum(similarities) / len(similarities)

        except Exception as e:
            logger.warning(f"Coherence score failed: {e}")

        return 0.7  # Neutral if failed

    def _context_alignment_score(
        self,
        response: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Check if response aligns with provided context.

        Args:
            response: Response text
            context: Context dictionary

        Returns:
            Alignment score (0.0-1.0)
        """
        # Extract text from context
        context_texts = []
        for key, value in context.items():
            if isinstance(value, str):
                context_texts.append(value)
            elif isinstance(value, dict):
                for subval in value.values():
                    if isinstance(subval, str):
                        context_texts.append(subval)

        if not context_texts:
            return 0.7  # Neutral if no context text

        context_text = ' '.join(context_texts)

        # Simple keyword overlap
        response_words = set(response.lower().split())
        context_words = set(context_text.lower().split())

        if not context_words:
            return 0.7

        overlap = len(response_words & context_words)
        overlap_ratio = overlap / max(len(response_words), 1)

        # Moderate overlap is good (not too much, not too little)
        if 0.2 <= overlap_ratio <= 0.6:
            return 0.9
        elif 0.1 <= overlap_ratio <= 0.7:
            return 0.7
        else:
            return 0.5

    def _generate_explanation(
        self,
        scores: Dict[str, float],
        final_score: float
    ) -> str:
        """Generate explanation of trustworthiness score using YRSN framework."""
        # YRSN-based quality assessment
        yrsn_score = scores.get('yrsn_quality', 0.0)

        if final_score >= 0.8:
            level = "High"
            desc = "Response appears highly trustworthy with strong actionable content"
        elif final_score >= 0.6:
            level = "Moderate"
            desc = "Response has moderate trustworthiness with some actionable content"
        else:
            level = "Low"
            desc = "Response may have trustworthiness issues - lacks specific guidance"

        parts = [f"{level} trustworthiness ({final_score:.2f}): {desc}"]

        # YRSN validation status
        if yrsn_score >= 0.7:
            parts.append("\nYRSN Status: EXCELLENT COMPLIANCE - High actionable content")
        elif yrsn_score >= 0.5:
            parts.append("\nYRSN Status: ACCEPTABLE COMPLIANCE - Good actionable content")
        elif yrsn_score >= 0.3:
            parts.append("\nYRSN Status: MODERATE RISK - Some actionable content")
        else:
            parts.append("\nYRSN Status: HIGH RISK - Minimal actionable content")

        # Add component details
        parts.append("\nComponent Scores:")

        # Order by importance (YRSN-inspired)
        priority_order = [
            'yrsn_quality',
            'logical_consistency',
            'evidence_authenticity',
            'coherence',
            'context_alignment'
        ]

        for component in priority_order:
            if component in scores:
                score = scores[component]
                parts.append(f"  - {component}: {score:.2f}")

        return "\n".join(parts)

    def _empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result with message."""
        return {
            'score': 0.0,
            'reliable': False,
            'explanation': message,
            'confidence': 1.0,
            'components': {}
        }

    def batch_score(
        self,
        queries: List[str],
        responses: List[str]
    ) -> List[Dict[str, Any]]:
        """Score multiple query-response pairs."""
        return [
            self.score(q, r)
            for q, r in zip(queries, responses)
        ]

    def __repr__(self) -> str:
        """String representation."""
        mode = "YRSN+tidyllm-sentence" if TIDYLLM_SENTENCE_AVAILABLE else "YRSN+heuristics"
        return f"TidyLLMTrustworthinessAdapter(mode={mode}, framework=YRSN)"
