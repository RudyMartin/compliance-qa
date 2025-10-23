# Use Case: Recycled Embeddings

## The Problem Being Solved

When you have a **large case base** and need to query it **multiple times**, you don't want to recompute embeddings every single time.

### Without Caching (Inefficient)

```python
# Query 1
results = analogical_reasoning("Query 1?", cases)  # Computes embeddings

# Query 2
results = analogical_reasoning("Query 2?", cases)  # Recomputes SAME embeddings

# Query 3
results = analogical_reasoning("Query 3?", cases)  # Recomputes AGAIN
```

**Problem:** Each query recomputes LSA/TF-IDF embeddings for the entire case base, wasting CPU time.

### With Caching (Efficient)

```python
# Compute embeddings ONCE
embeddings, model = lsa_fit_transform(cases)

# Reuse for multiple queries
results1 = analogical_reasoning("Query 1?", cases, embeddings=embeddings, model=model)
results2 = analogical_reasoning("Query 2?", cases, embeddings=embeddings, model=model)
results3 = analogical_reasoning("Query 3?", cases, embeddings=embeddings, model=model)
```

**Solution:** Pre-compute embeddings once, then reuse the cached embeddings and fitted model for all subsequent queries.

---

## Real-World Example

In the compliance-qa adapter, the `TidyLLMEmbeddingAdapter`:

1. **Stores a persistent case base** of entities (could be hundreds/thousands)
2. **Receives many queries** asking "is this new entity compliant?"
3. **Needs to compare** the new entity against the entire case base each time

Without caching, it would regenerate LSA embeddings for all entities on every query - **very expensive**!

### Performance Impact

| Scenario | Without Caching | With Caching | Speedup |
|----------|----------------|--------------|---------|
| 100 cases, 1 query | 500ms | 500ms | 1x |
| 100 cases, 10 queries | 5000ms | 550ms | **9x faster** |
| 100 cases, 100 queries | 50000ms | 950ms | **53x faster** |
| 1000 cases, 100 queries | 500000ms | 6000ms | **83x faster** |

*Estimated times based on typical LSA computation costs*

---

## How We Protected This Feature

### 1. Backward Compatibility in Import

```python
try:
    from tidyllm_sentence import (
        lsa_fit_transform,
        cosine_similarity,
        preprocess_for_embeddings,
        # NEW: High-level reasoning functions (Tensor Logic)
        analogical_reasoning,
        case_retrieval,
        temperature_sweep
    )
    TIDYLLM_SENTENCE_AVAILABLE = True
    TENSOR_LOGIC_AVAILABLE = True
except ImportError as e:
    # FALLBACK: Try without new functions (backwards compatibility)
    try:
        from tidyllm_sentence import (
            lsa_fit_transform,
            cosine_similarity,
            preprocess_for_embeddings
        )
        TIDYLLM_SENTENCE_AVAILABLE = True
        TENSOR_LOGIC_AVAILABLE = False  # Old version without reasoning
        logging.warning("tidyllm-sentence available but Tensor Logic functions not found")
    except ImportError:
        TIDYLLM_SENTENCE_AVAILABLE = False
        TENSOR_LOGIC_AVAILABLE = False
        logging.warning("tidyllm-sentence not available, using fallback implementation")
```

**Protection:** If someone has an older version of `tidyllm-sentence` without the new reasoning functions, the adapter still works!

### 2. Optional Enhancement Pattern

```python
def get_similar_entities(self, entity_id, threshold, top_k=10):
    # USE NEW HIGH-LEVEL FUNCTION if available (simpler, optimized)
    if TENSOR_LOGIC_AVAILABLE and query_text:
        return self._get_similar_entities_tensor_logic(
            query_text, entity_id, threshold, top_k
        )

    # FALLBACK: Original manual implementation
    # ... old code still works ...
```

**Protection:** The adapter prefers the new high-level functions when available, but falls back to the original manual implementation if they're not.

### 3. API Compatibility in Reasoning Functions

Look at the `analogical_reasoning()` signature:

```python
def analogical_reasoning(
    query,
    cases,
    embeddings=None,  # OPTIONAL - can pre-compute
    model=None,       # OPTIONAL - reuse fitted model
    top_k=5,
    temperature=1.0,
    method='lsa'
):
    # If embeddings provided, use them
    if embeddings is None:
        # Otherwise compute on-the-fly
        if method == 'lsa':
            embeddings, model = lsa_fit_transform(cases)
```

**Protection:**
- **Simple use**: Just pass `query` and `cases` - function handles everything
- **Advanced use**: Pre-compute embeddings for efficiency when querying repeatedly

### 4. Consistent Return Format

```python
# lsa_fit_transform ALWAYS returns (embeddings, model) tuple
embeddings, model = lsa_fit_transform(cases)
```

**Protection:** We fixed the adapter bug where it was expecting just `embeddings` instead of the tuple. Now it properly unpacks:

```python
# BEFORE (broken):
embeddings = lsa_fit_transform(self.corpus_texts)

# AFTER (fixed):
embeddings, self.vectorizer = lsa_fit_transform(self.corpus_texts)
```

---

## The Complete Caching Pattern

Here's how the adapter uses it:

```python
class TidyLLMEmbeddingAdapter:
    def __init__(self):
        self.entity_db = {}      # Stores entities
        self.vectorizer = None   # Cached model
        self.corpus_texts = []   # Text corpus

    def add_entity(self, entity_id, entity_data, outcome):
        # Add entity to database
        self.entity_db[entity_id] = {...}

        # Rebuild corpus
        self.corpus_texts = [self.entity_db[eid]['text'] for eid in self.entity_db.keys()]

        # Recompute embeddings for ALL entities (cache invalidation)
        embeddings, self.vectorizer = lsa_fit_transform(self.corpus_texts)

        # Cache embeddings in entity database
        for idx, ent_id in enumerate(self.entity_db.keys()):
            self.entity_db[ent_id]['embedding'] = embeddings[idx]

    def get_similar_entities(self, entity_id, threshold, top_k):
        # Use NEW high-level function with pre-computed embeddings
        if TENSOR_LOGIC_AVAILABLE:
            return self._get_similar_entities_tensor_logic(...)

        # Or use cached embeddings directly
        query_embedding = self.entity_db[entity_id]['embedding']

        # Compute similarities using cached embeddings (fast!)
        similarities = []
        for ent_id, ent_data in self.entity_db.items():
            if ent_id == entity_id:
                continue
            similarity = cosine_similarity(query_embedding, ent_data['embedding'])
            similarities.append((ent_id, similarity))

        # Sort and filter
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
```

---

## Cache Invalidation Strategy

The adapter uses a **complete rebuild** strategy:

1. **When case base changes** (entity added/removed):
   - Rebuild entire corpus
   - Recompute ALL embeddings
   - Update cache

2. **When case base stable** (multiple queries):
   - Use cached embeddings
   - No recomputation needed

### Alternative Strategies

For very large case bases, consider:

**Incremental Update** (advanced):
```python
# Only compute embedding for new entity
new_embedding = lsa_transform([new_text], self.vectorizer)
# Append to existing embeddings (LSA model stays same)
```

**Periodic Rebuild** (hybrid):
```python
# Quick incremental updates for small changes
# Full rebuild every N entities or time period
```

---

## Benefits

1. **Performance**: Only compute embeddings when case base changes, not on every query
2. **Flexibility**: Can use simple API for one-off queries, or advanced API for batch queries
3. **Backward Compatible**: Works with old and new versions of tidyllm-sentence
4. **Graceful Degradation**: Falls back to manual implementation if new functions unavailable
5. **Memory Efficient**: Embeddings stored alongside entity data (no duplicate storage)
6. **Transparent**: Users don't need to know about caching - it just works

---

## Key Insight

> **Embeddings are expensive to compute but cheap to reuse.**
>
> Cache them and the fitted model for efficiency!

### Cost Analysis

| Operation | Complexity | Time (100 cases) |
|-----------|-----------|------------------|
| LSA fit_transform | O(n²) | ~500ms |
| LSA transform (new query) | O(n) | ~5ms |
| Cosine similarity | O(d) | ~0.01ms |
| Top-K search | O(n log k) | ~0.1ms |

Where:
- n = number of cases
- d = embedding dimensions
- k = number of top results

**Takeaway:** Computing embeddings (fit_transform) is 100x more expensive than using pre-computed embeddings (transform + similarity).

---

## Usage Examples

### Example 1: One-Off Query (Simple)

```python
from tidyllm_sentence import analogical_reasoning

cases = [
    "Data validation is required for compliance",
    "Schema checks must be performed",
    "Code review ensures quality"
]

# Simple API - handles everything automatically
result = analogical_reasoning(
    query="What validation is needed?",
    cases=cases,
    temperature=0.7,
    top_k=2
)

print(result)  # [(0, 0.85, "Data validation..."), (1, 0.72, "Schema checks...")]
```

### Example 2: Batch Queries (Efficient)

```python
from tidyllm_sentence import lsa_fit_transform, analogical_reasoning

cases = [
    "Data validation is required for compliance",
    "Schema checks must be performed",
    "Code review ensures quality"
]

# Pre-compute embeddings ONCE
embeddings, model = lsa_fit_transform(cases)

queries = [
    "What validation is needed?",
    "How to ensure data quality?",
    "What compliance checks exist?"
]

# Reuse for multiple queries (fast!)
for query in queries:
    result = analogical_reasoning(
        query=query,
        cases=cases,
        embeddings=embeddings,  # Reuse!
        model=model,             # Reuse!
        temperature=0.7,
        top_k=2
    )
    print(f"{query}: {result[0][2][:50]}...")
```

### Example 3: Persistent Adapter (Production)

```python
from adapters.secondary.tensor_logic import TidyLLMEmbeddingAdapter

# Create adapter (maintains cache)
adapter = TidyLLMEmbeddingAdapter(embedding_method='lsa')

# Load historical entities (computed once)
for entity_id, entity_data, outcome in historical_data:
    adapter.add_entity(entity_id, entity_data, outcome)

# Process incoming queries (uses cache - fast!)
while True:
    new_entity = get_next_entity()

    # Query uses cached embeddings
    result = adapter.execute(
        query="Is this entity compliant?",
        context={'entity_id': new_entity['id'], 'entity_data': new_entity},
        temperature=0.5
    )

    print(f"Prediction: {result['answer']} ({result['confidence']:.1%})")
```

---

## Testing the Enhancement

See `test_tensor_logic_adapter_enhancement.py` for verification that:

1. ✅ Tensor Logic functions are available
2. ✅ Adapter successfully uses high-level functions when available
3. ✅ Fallback works when Tensor Logic unavailable
4. ✅ Caching pattern maintains performance across multiple queries
5. ✅ Similar entity retrieval works correctly
6. ✅ Temperature-controlled inference functions properly

---

## Related Documentation

- `packages/tidyllm-sentence/examples/` - Example scripts demonstrating embedding reuse
- `TENSOR_LOGIC_VIGNETTE.md` - Complete code examples for Tensor Logic
- `adapters/secondary/tensor_logic/__init__.py` - Adapter architecture documentation
