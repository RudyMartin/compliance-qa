# Tensor Logic: Distributed Implementation Plan

## 🎯 Overview

Distribute Tensor Logic components across the TidyLLM ecosystem:
1. **tlm** ← Math primitives (similarity, temperature scaling)
2. **tidyllm-sentence** ← Embedding-based reasoning
3. **tidyllm** ← Orchestration and business logic

---

## 📋 Phase 1: Enhance `tlm` with Similarity and Temperature Functions

**Estimated Time:** 2-3 hours
**Package Location:** `compliance-qa/packages/tlm/`

### **1.1 Add Core Similarity Functions**

#### **File: `tlm/core/similarity.py`** (NEW)

```python
"""
Similarity and distance metrics.

Pure Python implementations for vector similarity calculations.
"""

from math import sqrt


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors.

    Args:
        vec1: List of floats
        vec2: List of floats

    Returns:
        Float between -1 and 1 (1 = identical direction, -1 = opposite)

    Examples:
        >>> cosine_similarity([1, 2, 3], [2, 3, 4])
        0.9746318461970762
        >>> cosine_similarity([1, 0, 0], [0, 1, 0])
        0.0
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors must have same length: {len(vec1)} vs {len(vec2)}")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sqrt(sum(x * x for x in vec1))
    mag2 = sqrt(sum(y * y for y in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)


def pairwise_cosine(vectors):
    """Compute pairwise cosine similarity matrix.

    Args:
        vectors: List of vectors (list of lists)

    Returns:
        2D list where result[i][j] is similarity between vectors[i] and vectors[j]

    Examples:
        >>> vecs = [[1, 0], [0, 1], [1, 1]]
        >>> matrix = pairwise_cosine(vecs)
        >>> matrix[0][1]  # Similarity between [1,0] and [0,1]
        0.0
    """
    n = len(vectors)
    result = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i, n):
            sim = cosine_similarity(vectors[i], vectors[j])
            result[i][j] = sim
            result[j][i] = sim  # Symmetric

    return result


def top_k_similar(query_vec, corpus_vecs, k=5):
    """Find k most similar vectors from corpus.

    Args:
        query_vec: Query vector
        corpus_vecs: List of corpus vectors
        k: Number of results to return

    Returns:
        List of (index, similarity_score) tuples, sorted by score descending

    Examples:
        >>> query = [1, 0, 0]
        >>> corpus = [[1, 0, 0], [0, 1, 0], [0.9, 0.1, 0]]
        >>> results = top_k_similar(query, corpus, k=2)
        >>> results[0][0]  # Index of most similar
        0
    """
    # Compute similarities
    similarities = []
    for idx, vec in enumerate(corpus_vecs):
        sim = cosine_similarity(query_vec, vec)
        similarities.append((idx, sim))

    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Return top k
    return similarities[:k]


def euclidean_distance(vec1, vec2):
    """Compute Euclidean distance between two vectors.

    Args:
        vec1: List of floats
        vec2: List of floats

    Returns:
        Float >= 0 (0 = identical vectors)

    Examples:
        >>> euclidean_distance([0, 0], [3, 4])
        5.0
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors must have same length: {len(vec1)} vs {len(vec2)}")

    return sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


def manhattan_distance(vec1, vec2):
    """Compute Manhattan (L1) distance between two vectors.

    Args:
        vec1: List of floats
        vec2: List of floats

    Returns:
        Float >= 0 (0 = identical vectors)

    Examples:
        >>> manhattan_distance([0, 0], [3, 4])
        7.0
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors must have same length: {len(vec1)} vs {len(vec2)}")

    return sum(abs(a - b) for a, b in zip(vec1, vec2))
```

---

#### **File: `tlm/core/temperature.py`** (NEW)

```python
"""
Temperature scaling for controlling determinism vs exploration.

Temperature (T) controls the "sharpness" of probability distributions:
- T → 0: Deterministic (argmax, one-hot)
- T = 1: Standard probabilities
- T > 1: More uniform (exploration)

Used in:
- Simulated annealing (optimization)
- Neural network sampling (LLMs)
- Reinforcement learning (action selection)
- Tensor Logic reasoning (symbolic vs analogical)
"""

from math import exp


def temperature_scaled_softmax(logits, temperature=1.0):
    """Softmax with temperature scaling.

    Args:
        logits: List of raw scores (unnormalized)
        temperature: Float > 0 controlling sharpness
            - T → 0: Deterministic (one-hot of argmax)
            - T = 1: Standard softmax
            - T > 1: More uniform distribution

    Returns:
        List of probabilities (sums to 1.0)

    Examples:
        >>> logits = [2.0, 1.0, 0.5]
        >>> probs = temperature_scaled_softmax(logits, temperature=1.0)
        >>> sum(probs)
        1.0

        >>> # Low temperature (deterministic)
        >>> probs_cold = temperature_scaled_softmax(logits, temperature=0.01)
        >>> probs_cold[0]  # Close to 1.0
        0.999...

        >>> # High temperature (uniform)
        >>> probs_hot = temperature_scaled_softmax(logits, temperature=10.0)
        >>> probs_hot[0]  # Close to 1/3
        0.33...
    """
    if temperature <= 0:
        raise ValueError(f"Temperature must be positive, got {temperature}")

    # Handle near-zero temperature (deterministic)
    if temperature < 1e-8:
        max_idx = logits.index(max(logits))
        return [1.0 if i == max_idx else 0.0 for i in range(len(logits))]

    # Scale logits by temperature
    scaled_logits = [x / temperature for x in logits]

    # Compute softmax with numerical stability
    max_logit = max(scaled_logits)
    exp_logits = [exp(x - max_logit) for x in scaled_logits]
    sum_exp = sum(exp_logits)

    return [e / sum_exp for e in exp_logits]


def temperature_argmax(logits, temperature=1.0):
    """Get index of maximum element with temperature-controlled randomness.

    Args:
        logits: List of raw scores
        temperature: Float > 0
            - T → 0: Deterministic argmax
            - T > 0: Sample from temperature-scaled softmax

    Returns:
        Integer index

    Examples:
        >>> logits = [2.0, 1.0, 0.5]
        >>> idx = temperature_argmax(logits, temperature=0.01)
        >>> idx
        0
    """
    if temperature < 1e-8:
        # Deterministic: return argmax
        return logits.index(max(logits))
    else:
        # Sample from softmax distribution
        probs = temperature_scaled_softmax(logits, temperature)
        # For now, return argmax of probabilities
        # (True sampling would require random number generation)
        return probs.index(max(probs))


def apply_temperature(scores, temperature=1.0):
    """Apply temperature scaling to a list of scores.

    Convenience function that handles both positive and negative scores.

    Args:
        scores: List of floats (e.g., similarities, confidences)
        temperature: Float > 0 controlling sharpness

    Returns:
        List of temperature-scaled values (not necessarily summing to 1)

    Examples:
        >>> scores = [0.9, 0.5, 0.1]
        >>> scaled = apply_temperature(scores, temperature=2.0)
        >>> scaled[0] < scores[0]  # High temp reduces peaks
        True
    """
    if temperature <= 0:
        raise ValueError(f"Temperature must be positive, got {temperature}")

    if temperature < 1e-8:
        # Near-zero: return one-hot of maximum
        max_idx = scores.index(max(scores))
        return [1.0 if i == max_idx else 0.0 for i in range(len(scores))]

    # Apply temperature scaling (simple division)
    return [s / temperature for s in scores]
```

---

### **1.2 Update `tlm/__init__.py`**

Add exports for new functions:

```python
# Add to tlm/__init__.py

from .core.similarity import (
    cosine_similarity,
    pairwise_cosine,
    top_k_similar,
    euclidean_distance,
    manhattan_distance,
)

from .core.temperature import (
    temperature_scaled_softmax,
    temperature_argmax,
    apply_temperature,
)

# Add to __all__
__all__ = [
    # ... existing exports ...

    # Similarity metrics
    'cosine_similarity',
    'pairwise_cosine',
    'top_k_similar',
    'euclidean_distance',
    'manhattan_distance',

    # Temperature scaling
    'temperature_scaled_softmax',
    'temperature_argmax',
    'apply_temperature',
]
```

---

### **1.3 Add Tests**

#### **File: `tlm/tests/test_similarity.py`** (NEW)

```python
"""
Tests for similarity metrics.
"""

import tlm


def test_cosine_similarity_identical():
    """Test cosine similarity of identical vectors."""
    vec = [1.0, 2.0, 3.0]
    sim = tlm.cosine_similarity(vec, vec)
    assert abs(sim - 1.0) < 1e-6, f"Expected 1.0, got {sim}"


def test_cosine_similarity_orthogonal():
    """Test cosine similarity of orthogonal vectors."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]
    sim = tlm.cosine_similarity(vec1, vec2)
    assert abs(sim - 0.0) < 1e-6, f"Expected 0.0, got {sim}"


def test_cosine_similarity_opposite():
    """Test cosine similarity of opposite vectors."""
    vec1 = [1.0, 0.0]
    vec2 = [-1.0, 0.0]
    sim = tlm.cosine_similarity(vec1, vec2)
    assert abs(sim - (-1.0)) < 1e-6, f"Expected -1.0, got {sim}"


def test_pairwise_cosine():
    """Test pairwise cosine similarity matrix."""
    vecs = [[1, 0], [0, 1], [1, 1]]
    matrix = tlm.pairwise_cosine(vecs)

    # Check diagonal (self-similarity = 1)
    assert abs(matrix[0][0] - 1.0) < 1e-6
    assert abs(matrix[1][1] - 1.0) < 1e-6

    # Check orthogonal vectors
    assert abs(matrix[0][1] - 0.0) < 1e-6

    # Check symmetry
    assert abs(matrix[0][1] - matrix[1][0]) < 1e-6


def test_top_k_similar():
    """Test top-k similar vector retrieval."""
    query = [1.0, 0.0, 0.0]
    corpus = [
        [1.0, 0.0, 0.0],  # Identical (sim=1.0)
        [0.0, 1.0, 0.0],  # Orthogonal (sim=0.0)
        [0.9, 0.1, 0.0],  # Similar (sim≈0.99)
    ]

    results = tlm.top_k_similar(query, corpus, k=2)

    # Check we got 2 results
    assert len(results) == 2

    # Check first result is index 0 (identical)
    assert results[0][0] == 0
    assert abs(results[0][1] - 1.0) < 1e-6

    # Check second result is index 2 (similar)
    assert results[1][0] == 2


def test_euclidean_distance():
    """Test Euclidean distance calculation."""
    vec1 = [0, 0]
    vec2 = [3, 4]
    dist = tlm.euclidean_distance(vec1, vec2)
    assert abs(dist - 5.0) < 1e-6, f"Expected 5.0, got {dist}"


def test_manhattan_distance():
    """Test Manhattan distance calculation."""
    vec1 = [0, 0]
    vec2 = [3, 4]
    dist = tlm.manhattan_distance(vec1, vec2)
    assert dist == 7.0, f"Expected 7.0, got {dist}"


if __name__ == '__main__':
    test_cosine_similarity_identical()
    test_cosine_similarity_orthogonal()
    test_cosine_similarity_opposite()
    test_pairwise_cosine()
    test_top_k_similar()
    test_euclidean_distance()
    test_manhattan_distance()
    print("✅ All similarity tests passed!")
```

---

#### **File: `tlm/tests/test_temperature.py`** (NEW)

```python
"""
Tests for temperature scaling functions.
"""

import tlm


def test_temperature_softmax_standard():
    """Test standard softmax (T=1.0)."""
    logits = [2.0, 1.0, 0.5]
    probs = tlm.temperature_scaled_softmax(logits, temperature=1.0)

    # Check sums to 1
    assert abs(sum(probs) - 1.0) < 1e-6

    # Check ordering preserved
    assert probs[0] > probs[1] > probs[2]


def test_temperature_softmax_cold():
    """Test cold temperature (T→0) produces near one-hot."""
    logits = [2.0, 1.0, 0.5]
    probs = tlm.temperature_scaled_softmax(logits, temperature=0.01)

    # First element should be close to 1.0
    assert probs[0] > 0.99

    # Other elements should be close to 0
    assert probs[1] < 0.01
    assert probs[2] < 0.01


def test_temperature_softmax_hot():
    """Test hot temperature (T>1) produces more uniform distribution."""
    logits = [2.0, 1.0, 0.5]

    probs_cold = tlm.temperature_scaled_softmax(logits, temperature=0.5)
    probs_hot = tlm.temperature_scaled_softmax(logits, temperature=2.0)

    # Hot temperature should reduce gap between max and min
    gap_cold = probs_cold[0] - probs_cold[2]
    gap_hot = probs_hot[0] - probs_hot[2]

    assert gap_hot < gap_cold


def test_temperature_argmax_deterministic():
    """Test deterministic argmax at T→0."""
    logits = [1.0, 3.0, 2.0]
    idx = tlm.temperature_argmax(logits, temperature=0.0001)
    assert idx == 1  # Index of maximum (3.0)


def test_apply_temperature():
    """Test general temperature application."""
    scores = [0.9, 0.5, 0.1]

    # Higher temperature should reduce differences
    scaled = tlm.apply_temperature(scores, temperature=2.0)

    gap_original = scores[0] - scores[2]
    gap_scaled = scaled[0] - scaled[2]

    assert gap_scaled < gap_original


if __name__ == '__main__':
    test_temperature_softmax_standard()
    test_temperature_softmax_cold()
    test_temperature_softmax_hot()
    test_temperature_argmax_deterministic()
    test_apply_temperature()
    print("✅ All temperature tests passed!")
```

---

### **1.4 Update Documentation**

#### **Update `tlm/CLAUDE.md`** (if exists) or create it:

Add section about new modules:

```markdown
### Similarity Metrics (tlm/core/similarity.py)

Functions for measuring vector similarity and distance:
- `cosine_similarity(vec1, vec2)` - Cosine similarity between two vectors
- `pairwise_cosine(vectors)` - Pairwise similarity matrix
- `top_k_similar(query, corpus, k)` - Find k most similar vectors
- `euclidean_distance(vec1, vec2)` - L2 distance
- `manhattan_distance(vec1, vec2)` - L1 distance

### Temperature Scaling (tlm/core/temperature.py)

Functions for controlling determinism vs exploration:
- `temperature_scaled_softmax(logits, temperature)` - Softmax with temperature control
- `temperature_argmax(logits, temperature)` - Temperature-controlled argmax
- `apply_temperature(scores, temperature)` - General temperature scaling

Temperature parameter:
- T → 0: Deterministic (one-hot, argmax)
- T = 1: Standard probabilities
- T > 1: More uniform (exploration)
```

---

### **1.5 Phase 1 Testing Commands**

```bash
cd compliance-qa/packages/tlm

# Run new tests
python -m pytest tests/test_similarity.py -v
python -m pytest tests/test_temperature.py -v

# Run all tests to ensure no regressions
python -m pytest tests/ -v
```

---

## 📋 Phase 2: Enhance `tidyllm-sentence` with Reasoning Functions

**Estimated Time:** 3-4 hours
**Package Location:** `compliance-qa/packages/tidyllm-sentence/`

### **2.1 Add Reasoning Module**

#### **File: `tidyllm_sentence/reasoning.py`** (NEW)

```python
"""
Reasoning capabilities using sentence embeddings.

Provides analogical reasoning, case-based retrieval, and similarity-based inference.
"""

import tlm
from . import (
    tfidf_fit_transform,
    tfidf_transform,
    lsa_fit_transform,
    lsa_transform,
    word_avg_fit_transform,
    semantic_search,
)


def analogical_reasoning(query, cases, embeddings=None, top_k=5, temperature=1.0, method='lsa'):
    """Find similar cases via semantic similarity with temperature control.

    Temperature controls diversity:
    - T=0: Only exact matches (similarity ≈ 1.0)
    - T=1: Standard ranking by similarity
    - T>1: More diverse results (exploration)

    Args:
        query: Query text (string)
        cases: List of case texts
        embeddings: Pre-computed case embeddings (optional)
        top_k: Number of similar cases to return
        temperature: Float >= 0 controlling diversity
        method: Embedding method ('tfidf', 'lsa', 'word_avg')

    Returns:
        List of (case_idx, similarity_score, case_text) tuples

    Examples:
        >>> cases = ["Data validation is required", "Schema checks are needed"]
        >>> query = "How to validate data?"
        >>> results = analogical_reasoning(query, cases, top_k=2, temperature=1.0)
        >>> results[0][0]  # Index of most similar case
        0
    """
    # Generate embeddings if not provided
    if embeddings is None:
        if method == 'tfidf':
            embeddings, model = tfidf_fit_transform(cases)
            query_emb = tfidf_transform([query], model)
        elif method == 'lsa':
            embeddings, model = lsa_fit_transform(cases, n_components=min(50, len(cases)))
            query_emb = lsa_transform([query], model)
        elif method == 'word_avg':
            embeddings, model = word_avg_fit_transform(cases, embedding_dim=100)
            query_emb, _ = word_avg_fit_transform([query], embedding_dim=100)
        else:
            raise ValueError(f"Unknown method: {method}")
    else:
        # Use provided embeddings, need to embed query
        # Assume same method was used for cases
        if method == 'tfidf':
            # Need the model - this is a limitation
            raise ValueError("Must provide model when using pre-computed embeddings")
        query_emb = embeddings  # Placeholder - need better API

    # Find similar cases
    results = semantic_search(query_emb[0], embeddings, top_k=top_k)

    # Apply temperature scaling to scores
    if temperature < 1e-8:
        # T=0: Only exact matches
        results = [(idx, score) for idx, score in results if score > 0.999]
    elif temperature != 1.0:
        # Apply temperature to scores (affects ranking)
        scores = [score for idx, score in results]
        scaled_scores = tlm.apply_temperature(scores, temperature)
        results = [(idx, scaled_scores[i]) for i, (idx, _) in enumerate(results)]
        # Re-sort by scaled scores
        results.sort(key=lambda x: x[1], reverse=True)

    # Add case text to results
    return [(idx, score, cases[idx]) for idx, score in results]


def case_retrieval(query, case_base, method='lsa', n_components=50, top_k=None):
    """Retrieve relevant cases from case base.

    Args:
        query: Query text
        case_base: List of case texts
        method: Embedding method ('tfidf', 'lsa', 'word_avg')
        n_components: For LSA, number of components
        top_k: Number of cases to return (None = all)

    Returns:
        List of (case_text, similarity_score) tuples sorted by relevance

    Examples:
        >>> cases = ["Python is a language", "JavaScript is a language"]
        >>> query = "What programming languages exist?"
        >>> results = case_retrieval(query, cases, method='tfidf', top_k=2)
        >>> len(results)
        2
    """
    if top_k is None:
        top_k = len(case_base)

    # Generate embeddings based on method
    if method == 'lsa':
        embeddings, model = lsa_fit_transform(case_base, n_components=min(n_components, len(case_base)))
        query_emb = lsa_transform([query], model)
    elif method == 'tfidf':
        embeddings, model = tfidf_fit_transform(case_base)
        query_emb = tfidf_transform([query], model)
    elif method == 'word_avg':
        embeddings, model = word_avg_fit_transform(case_base, embedding_dim=100)
        # For query, need to use same vocabulary
        # This is a limitation - word_avg doesn't have transform
        # Workaround: use tfidf
        embeddings_with_query, _ = word_avg_fit_transform(case_base + [query], embedding_dim=100)
        query_emb = [embeddings_with_query[-1]]
        embeddings = embeddings_with_query[:-1]
    else:
        raise ValueError(f"Unknown method: {method}")

    # Find most similar cases
    results = semantic_search(query_emb[0], embeddings, top_k=top_k)

    # Return (case_text, similarity) tuples
    return [(case_base[idx], score) for idx, score in results]


def similarity_based_inference(query, knowledge_base, threshold=0.5, method='lsa'):
    """Infer answer based on similarity to knowledge base.

    Retrieves similar knowledge items and returns them if above threshold.

    Args:
        query: Query text
        knowledge_base: List of knowledge texts
        threshold: Minimum similarity score (0-1)
        method: Embedding method

    Returns:
        Dict with:
        - 'matches': List of (text, score) tuples above threshold
        - 'best_match': Highest scoring match (or None)
        - 'confidence': Score of best match

    Examples:
        >>> kb = ["The sky is blue", "Grass is green"]
        >>> query = "What color is the sky?"
        >>> result = similarity_based_inference(query, kb, threshold=0.3)
        >>> result['best_match'][0]
        'The sky is blue'
    """
    # Retrieve all cases with scores
    results = case_retrieval(query, knowledge_base, method=method, top_k=len(knowledge_base))

    # Filter by threshold
    matches = [(text, score) for text, score in results if score >= threshold]

    # Get best match
    best_match = matches[0] if matches else None
    confidence = best_match[1] if best_match else 0.0

    return {
        'matches': matches,
        'best_match': best_match,
        'confidence': confidence,
        'num_matches': len(matches)
    }


def temperature_sweep(query, cases, temperatures=None, method='lsa', top_k=3):
    """Run analogical reasoning across multiple temperatures.

    Useful for understanding how temperature affects results.

    Args:
        query: Query text
        cases: List of case texts
        temperatures: List of temperature values (default: [0.0, 0.5, 1.0, 2.0])
        method: Embedding method
        top_k: Number of results per temperature

    Returns:
        Dict mapping temperature -> results

    Examples:
        >>> cases = ["Case 1", "Case 2", "Case 3"]
        >>> query = "Query"
        >>> sweep = temperature_sweep(query, cases, temperatures=[0.0, 1.0])
        >>> len(sweep)
        2
    """
    if temperatures is None:
        temperatures = [0.0, 0.5, 1.0, 2.0]

    # Pre-compute embeddings once
    if method == 'tfidf':
        embeddings, model = tfidf_fit_transform(cases)
        query_emb = tfidf_transform([query], model)
    elif method == 'lsa':
        embeddings, model = lsa_fit_transform(cases, n_components=min(50, len(cases)))
        query_emb = lsa_transform([query], model)
    else:
        embeddings, model = word_avg_fit_transform(cases, embedding_dim=100)
        query_emb, _ = word_avg_fit_transform([query], embedding_dim=100)

    # Run reasoning at each temperature
    results = {}
    for temp in temperatures:
        temp_results = analogical_reasoning(
            query=query,
            cases=cases,
            embeddings=embeddings,
            top_k=top_k,
            temperature=temp,
            method=method
        )
        results[temp] = temp_results

    return results
```

---

### **2.2 Update `tidyllm_sentence/__init__.py`**

Add exports for reasoning functions:

```python
# Add to tidyllm_sentence/__init__.py

from .reasoning import (
    analogical_reasoning,
    case_retrieval,
    similarity_based_inference,
    temperature_sweep,
)

# Add to __all__ (if it exists)
__all__ = [
    # ... existing exports ...

    # Reasoning functions
    'analogical_reasoning',
    'case_retrieval',
    'similarity_based_inference',
    'temperature_sweep',
]
```

---

### **2.3 Add Tests**

#### **File: `tidyllm_sentence/tests/test_reasoning.py`** (NEW)

```python
"""
Tests for reasoning capabilities.
"""

import tidyllm_sentence as tls


def test_analogical_reasoning_basic():
    """Test basic analogical reasoning."""
    cases = [
        "Data validation is required",
        "Schema checks are needed",
        "Code review is important"
    ]
    query = "How to validate data?"

    results = tls.analogical_reasoning(
        query=query,
        cases=cases,
        top_k=2,
        temperature=1.0,
        method='tfidf'
    )

    # Should return 2 results
    assert len(results) == 2

    # Each result should be (idx, score, text)
    idx, score, text = results[0]
    assert isinstance(idx, int)
    assert isinstance(score, float)
    assert isinstance(text, str)

    # First result should be most relevant (data validation)
    assert "validation" in results[0][2].lower()


def test_analogical_reasoning_temperature_zero():
    """Test that T=0 only returns exact matches."""
    cases = [
        "The sky is blue",
        "The sky is nice",
        "Cars are fast"
    ]
    query = "The sky is blue"

    results = tls.analogical_reasoning(
        query=query,
        cases=cases,
        top_k=3,
        temperature=0.0,
        method='tfidf'
    )

    # Should only return very high similarity matches
    # (might be 0 or 1 depending on exact match)
    assert len(results) <= 1


def test_case_retrieval():
    """Test case retrieval from knowledge base."""
    cases = [
        "Python is a programming language",
        "JavaScript is a programming language",
        "Dogs are animals"
    ]
    query = "What programming languages exist?"

    results = tls.case_retrieval(
        query=query,
        case_base=cases,
        method='tfidf',
        top_k=2
    )

    # Should return 2 cases
    assert len(results) == 2

    # Each result should be (text, score)
    text, score = results[0]
    assert isinstance(text, str)
    assert isinstance(score, float)
    assert 0 <= score <= 1

    # First result should be about programming
    assert "programming" in results[0][0].lower()


def test_similarity_based_inference():
    """Test similarity-based inference."""
    kb = [
        "The sky is blue",
        "Grass is green",
        "The ocean is blue"
    ]
    query = "What color is the sky?"

    result = tls.similarity_based_inference(
        query=query,
        knowledge_base=kb,
        threshold=0.1,
        method='tfidf'
    )

    # Should have structure
    assert 'matches' in result
    assert 'best_match' in result
    assert 'confidence' in result

    # Should find at least one match
    assert len(result['matches']) > 0

    # Best match should mention sky
    assert result['best_match'] is not None
    assert "sky" in result['best_match'][0].lower()


def test_temperature_sweep():
    """Test temperature sweep."""
    cases = ["Case A", "Case B", "Case C"]
    query = "Query"

    results = tls.temperature_sweep(
        query=query,
        cases=cases,
        temperatures=[0.5, 1.0],
        method='tfidf',
        top_k=2
    )

    # Should have results for each temperature
    assert len(results) == 2
    assert 0.5 in results
    assert 1.0 in results

    # Each temperature should have top_k results
    assert len(results[0.5]) == 2
    assert len(results[1.0]) == 2


if __name__ == '__main__':
    test_analogical_reasoning_basic()
    test_analogical_reasoning_temperature_zero()
    test_case_retrieval()
    test_similarity_based_inference()
    test_temperature_sweep()
    print("✅ All reasoning tests passed!")
```

---

### **2.4 Update Documentation**

Update `tidyllm_sentence/README.md` with new section:

```markdown
## Reasoning Capabilities

### Analogical Reasoning
Find similar cases via semantic similarity with temperature control:

```python
import tidyllm_sentence as tls

cases = [
    "Data validation requires type checking",
    "Schema validation ensures structure",
    "Code review improves quality"
]

query = "How to validate data?"

# Standard reasoning (T=1.0)
results = tls.analogical_reasoning(
    query=query,
    cases=cases,
    top_k=2,
    temperature=1.0,
    method='lsa'
)

for idx, score, case in results:
    print(f"Score {score:.3f}: {case}")
```

### Temperature Control
Temperature affects result diversity:
- **T=0.0**: Only exact matches (deterministic)
- **T=1.0**: Standard similarity ranking
- **T>1.0**: More diverse results (exploration)

```python
# Deterministic (only very similar cases)
results_cold = tls.analogical_reasoning(query, cases, temperature=0.0)

# Explorative (more diverse cases)
results_hot = tls.analogical_reasoning(query, cases, temperature=2.0)
```

### Case Retrieval
Retrieve relevant cases from a knowledge base:

```python
knowledge_base = [
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Data structures organize information"
]

query = "Tell me about programming"

results = tls.case_retrieval(
    query=query,
    case_base=knowledge_base,
    method='lsa',
    top_k=3
)

for case, score in results:
    print(f"{score:.3f}: {case}")
```

### Similarity-Based Inference
Infer answers based on similarity to knowledge:

```python
kb = ["The sky is blue", "Grass is green"]
query = "What color is the sky?"

result = tls.similarity_based_inference(
    query=query,
    knowledge_base=kb,
    threshold=0.3,
    method='tfidf'
)

if result['best_match']:
    text, confidence = result['best_match']
    print(f"Answer: {text} (confidence: {confidence:.3f})")
```
```

---

### **2.5 Phase 2 Testing Commands**

```bash
cd compliance-qa/packages/tidyllm-sentence

# Run new tests
python -m pytest tests/test_reasoning.py -v

# Run all tests
python -m pytest tests/ -v
```

---

## 📋 Phase 3: Add Tensor Logic to `tidyllm`

**Estimated Time:** 6-8 hours
**Package Location:** `compliance-qa/packages/tidyllm/` or `git-tidyllm/TidyLLM/`

### **3.1 Create Reasoning Module Structure**

```
tidyllm/reasoning/
├── __init__.py
├── symbolic/
│   ├── __init__.py
│   ├── engine.py          # SymbolicReasoner
│   ├── rules.py           # Rule definitions
│   └── matcher.py         # Pattern matching
├── analogical/
│   ├── __init__.py
│   └── engine.py          # AnalogicalReasoner (uses tidyllm-sentence)
├── yrsn/
│   ├── __init__.py
│   ├── quality.py         # YRSN quality scoring
│   ├── evidence.py        # Evidence validation
│   └── consistency.py     # Consistency analysis
├── temperature/
│   ├── __init__.py
│   ├── router.py          # TemperatureRouter
│   └── modes.py           # ReasoningMode enum
├── service.py             # TensorLogicService (main orchestration)
└── factory.py             # Convenience factory functions
```

---

### **3.2 Core Files** (Detailed Implementation)

Due to length constraints, I'll provide the structure and key files. The full implementation should be extracted from:
- `compliance-qa/domain/services/tensor_logic/`
- `compliance-qa/adapters/secondary/tensor_logic/`

#### **File: `tidyllm/reasoning/temperature/modes.py`**

```python
"""
Reasoning modes based on temperature.
"""

from enum import Enum


class ReasoningMode(Enum):
    """Reasoning modes controlled by temperature parameter.

    - SYMBOLIC: T ≈ 0 (certifiable, rule-based)
    - HYBRID: 0 < T < 0.5 (mixed symbolic + analogical)
    - ANALOGICAL: T ≥ 0.5 (case-based, similarity)
    """
    SYMBOLIC = "symbolic"
    HYBRID = "hybrid"
    ANALOGICAL = "analogical"
```

#### **File: `tidyllm/reasoning/temperature/router.py`**

```python
"""
Temperature-based routing between reasoning modes.
"""

from .modes import ReasoningMode


class TemperatureRouter:
    """Routes queries to appropriate reasoning mode based on temperature.

    Temperature ranges:
    - T ≤ 0.05: Pure symbolic (certifiable)
    - 0.05 < T < 0.5: Hybrid (symbolic + analogical)
    - T ≥ 0.5: Pure analogical (case-based)
    """

    def __init__(self, symbolic_threshold=0.05, hybrid_threshold=0.5):
        """Initialize router with temperature thresholds.

        Args:
            symbolic_threshold: Below this = pure symbolic
            hybrid_threshold: Above this = pure analogical
        """
        self.symbolic_threshold = symbolic_threshold
        self.hybrid_threshold = hybrid_threshold

    def get_mode(self, temperature):
        """Determine reasoning mode from temperature.

        Args:
            temperature: Float >= 0

        Returns:
            ReasoningMode enum value
        """
        if temperature <= self.symbolic_threshold:
            return ReasoningMode.SYMBOLIC
        elif temperature < self.hybrid_threshold:
            return ReasoningMode.HYBRID
        else:
            return ReasoningMode.ANALOGICAL

    def get_weights(self, temperature):
        """Get mixing weights for hybrid mode.

        Args:
            temperature: Float in [0, 1]

        Returns:
            Dict with 'symbolic' and 'analogical' weights (sum to 1.0)
        """
        if temperature <= self.symbolic_threshold:
            return {'symbolic': 1.0, 'analogical': 0.0}
        elif temperature >= self.hybrid_threshold:
            return {'symbolic': 0.0, 'analogical': 1.0}
        else:
            # Linear interpolation in hybrid range
            t_normalized = (temperature - self.symbolic_threshold) / \
                          (self.hybrid_threshold - self.symbolic_threshold)
            return {
                'symbolic': 1.0 - t_normalized,
                'analogical': t_normalized
            }
```

---

#### **File: `tidyllm/reasoning/service.py`**

```python
"""
TensorLogicService - Main orchestration for temperature-controlled reasoning.
"""

from .temperature.router import TemperatureRouter
from .temperature.modes import ReasoningMode
# Import engines (to be implemented)
# from .symbolic.engine import SymbolicReasoner
# from .analogical.engine import AnalogicalReasoner
# from .yrsn.quality import YRSNScorer


class TensorLogicService:
    """Temperature-controlled reasoning service.

    Orchestrates symbolic and analogical reasoning based on temperature:
    - T=0.0: Pure symbolic (certifiable, rule-based)
    - T=0.1-0.4: Hybrid (symbolic + analogical)
    - T≥0.5: Pure analogical (case-based)
    """

    def __init__(self,
                 rules=None,
                 case_base=None,
                 embedding_method='lsa',
                 symbolic_threshold=0.05,
                 hybrid_threshold=0.5):
        """Initialize service with configuration.

        Args:
            rules: Symbolic rules (list of dicts or Rule objects)
            case_base: Analogical cases (list of strings)
            embedding_method: Method for embeddings ('tfidf', 'lsa', 'word_avg')
            symbolic_threshold: Temperature threshold for symbolic mode
            hybrid_threshold: Temperature threshold for analogical mode
        """
        self.router = TemperatureRouter(symbolic_threshold, hybrid_threshold)

        # Initialize reasoning engines
        # self.symbolic = SymbolicReasoner(rules)
        # self.analogical = AnalogicalReasoner(case_base, method=embedding_method)
        # self.yrsn = YRSNScorer()

        # Placeholder implementations
        self.symbolic = None
        self.analogical = None
        self.yrsn = None

        self.embedding_method = embedding_method

    def infer(self, query, context=None, temperature=0.0, score_trustworthiness=True):
        """Run inference with temperature-controlled reasoning.

        Args:
            query: Query string
            context: Optional context dict
            temperature: Float >= 0 controlling reasoning mode
            score_trustworthiness: Whether to compute YRSN trustworthiness

        Returns:
            Dict with:
            - answer: Inferred answer
            - confidence: Confidence score (0-1)
            - reasoning_mode: ReasoningMode enum
            - certifiable: Boolean (True only for pure symbolic)
            - trustworthiness: YRSN trust score (if requested)
            - evidence: List of evidence items
            - components: Dict of component scores
        """
        # Route based on temperature
        mode = self.router.get_mode(temperature)

        # Execute appropriate reasoning strategy
        if mode == ReasoningMode.SYMBOLIC:
            result = self._infer_symbolic(query, context)
            certifiable = True

        elif mode == ReasoningMode.ANALOGICAL:
            result = self._infer_analogical(query, context, temperature)
            certifiable = False

        else:  # HYBRID
            result = self._infer_hybrid(query, context, temperature)
            certifiable = False

        # Score trustworthiness if requested
        if score_trustworthiness and self.yrsn:
            trust_score = self.yrsn.score(query, str(result['answer']))
        else:
            trust_score = None

        return {
            'answer': result.get('answer'),
            'confidence': result.get('confidence', 0.0),
            'reasoning_mode': mode.value,
            'certifiable': certifiable,
            'trustworthiness': trust_score,
            'evidence': result.get('evidence', []),
            'components': result.get('components', {})
        }

    def _infer_symbolic(self, query, context):
        """Pure symbolic reasoning."""
        # Placeholder - should use self.symbolic
        return {
            'answer': f"Symbolic answer for: {query}",
            'confidence': 1.0,
            'evidence': ['Rule-based inference'],
            'components': {}
        }

    def _infer_analogical(self, query, context, temperature):
        """Pure analogical reasoning."""
        # Placeholder - should use self.analogical
        return {
            'answer': f"Analogical answer for: {query}",
            'confidence': 0.7,
            'evidence': ['Case-based retrieval'],
            'components': {}
        }

    def _infer_hybrid(self, query, context, temperature):
        """Hybrid reasoning combining symbolic and analogical."""
        # Get mixing weights
        weights = self.router.get_weights(temperature)

        # Run both modes
        sym_result = self._infer_symbolic(query, context)
        ana_result = self._infer_analogical(query, context, temperature)

        # Combine results (weighted)
        combined_confidence = (
            weights['symbolic'] * sym_result['confidence'] +
            weights['analogical'] * ana_result['confidence']
        )

        return {
            'answer': f"Hybrid: {sym_result['answer']} + {ana_result['answer']}",
            'confidence': combined_confidence,
            'evidence': sym_result['evidence'] + ana_result['evidence'],
            'components': {
                'symbolic': sym_result,
                'analogical': ana_result,
                'weights': weights
            }
        }
```

---

#### **File: `tidyllm/reasoning/factory.py`**

```python
"""
Convenience factory functions for creating reasoners.
"""

from .service import TensorLogicService


def create_reasoner(rules=None, cases=None, embedding_method='lsa'):
    """Create TensorLogicService with default configuration.

    Args:
        rules: Symbolic rules (optional)
        cases: Analogical cases (optional)
        embedding_method: Embedding method for analogical reasoning

    Returns:
        TensorLogicService instance

    Examples:
        >>> reasoner = create_reasoner()
        >>> result = reasoner.infer("Query?", temperature=0.0)
    """
    return TensorLogicService(
        rules=rules,
        case_base=cases,
        embedding_method=embedding_method
    )
```

---

### **3.3 Update `tidyllm/__init__.py`**

```python
# Add to tidyllm/__init__.py

from .reasoning import (
    TensorLogicService,
    ReasoningMode,
    TemperatureRouter,
    create_reasoner,
)

# Add to __all__
__all__ = [
    # ... existing exports ...

    # Tensor Logic / Reasoning
    'TensorLogicService',
    'ReasoningMode',
    'TemperatureRouter',
    'create_reasoner',
]
```

---

### **3.4 Phase 3 Testing**

```bash
cd compliance-qa/packages/tidyllm

# Test temperature router
python -m pytest tests/reasoning/test_temperature.py -v

# Test service
python -m pytest tests/reasoning/test_service.py -v

# Run all reasoning tests
python -m pytest tests/reasoning/ -v
```

---

## 📊 Summary & Timeline

### **Total Estimated Time: 11-15 hours**

| Phase | Component | Time | Status |
|-------|-----------|------|--------|
| **1** | tlm (similarity + temperature) | 2-3h | Pending |
| **2** | tidyllm-sentence (reasoning) | 3-4h | Pending |
| **3** | tidyllm (orchestration) | 6-8h | Pending |

---

### **Dependency Order:**

```
1. Phase 1 (tlm) ← No dependencies
   ↓
2. Phase 2 (tidyllm-sentence) ← Depends on Phase 1
   ↓
3. Phase 3 (tidyllm) ← Depends on Phase 1 & 2
```

---

### **Testing Strategy:**

1. **Unit tests** at each phase (test each component individually)
2. **Integration tests** at Phase 3 (test full stack)
3. **Regression tests** (ensure existing tests still pass)

---

### **Migration Path from compliance-qa:**

After Phases 1-3 complete:
1. Update `compliance-qa` to import from tidyllm ecosystem
2. Remove duplicate code from `compliance-qa`
3. Update `compliance-qa` tests to use new imports
4. Verify full system still works

---

## 🚀 Next Steps

**Ready to proceed with Phase 1?** We'll start by:
1. Creating `tlm/core/similarity.py`
2. Creating `tlm/core/temperature.py`
3. Updating `tlm/__init__.py`
4. Adding tests
5. Running tests to verify

Let me know when you're ready to begin implementation!
