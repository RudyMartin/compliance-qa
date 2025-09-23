# How to Use SmartEmbeddingService - Developer Guide

**For**: Developers integrating intelligent embeddings into TidyLLM applications
**Level**: Intermediate
**Prerequisites**: Basic understanding of embeddings and TidyLLM architecture

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage](#basic-usage)
3. [Advanced Configuration](#advanced-configuration)
4. [RAG Integration](#rag-integration)
5. [Performance Optimization](#performance-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Migration Guide](#migration-guide)

## Quick Start

### Installation & Setup

SmartEmbeddingService is already included in TidyLLM. No additional installation required.

```python
# Add to your imports
from packages.tidyllm.services.smart_embedding_service import (
    SmartEmbeddingService,
    EmbeddingRequest,
    SmartEmbeddingAdapter
)
```

### 30-Second Example

```python
# Create service
service = SmartEmbeddingService()

# Generate embedding
request = EmbeddingRequest(text="Your text here")
result = service.generate_embedding(request)

print(f"Generated {result.dimensions}D embedding using {result.model_used}")
print(f"Quality: {result.quality_score}, Time: {result.processing_time_ms}ms")
```

## Basic Usage

### 1. Simple Embedding Generation

```python
from packages.tidyllm.services.smart_embedding_service import (
    SmartEmbeddingService, EmbeddingRequest
)

def generate_simple_embedding():
    """Basic embedding generation example."""

    # Initialize service (lazy-loads components)
    service = SmartEmbeddingService()

    # Create request
    request = EmbeddingRequest(
        text="Machine learning enables computers to learn without explicit programming.",
        dimensions=1024,  # Optional: specify dimensions
        use_cache=True    # Optional: enable caching
    )

    # Generate embedding
    result = service.generate_embedding(request)

    # Use the result
    embedding_vector = result.embedding  # List[float]
    model_used = result.model_used       # str
    source = result.source               # 'local' or 'gateway'

    return embedding_vector

# Usage
embedding = generate_simple_embedding()
print(f"Generated embedding with {len(embedding)} dimensions")
```

### 2. High-Quality Embeddings

```python
def generate_high_quality_embedding():
    """Generate high-quality embedding using Bedrock."""

    service = SmartEmbeddingService()

    # Request high-quality embedding (forces Bedrock usage)
    request = EmbeddingRequest(
        text="Legal contract clause requiring careful analysis.",
        require_high_quality=True,  # Forces Bedrock gateway
        model_preference="titan-embed-v2",
        dimensions=1024
    )

    result = service.generate_embedding(request)

    print(f"High-quality embedding:")
    print(f"  Model: {result.model_used}")
    print(f"  Source: {result.source}")  # Should be 'gateway'
    print(f"  Quality: {result.quality_score}")  # Should be 0.95+

    return result.embedding
```

### 3. Context-Aware Embedding

```python
def generate_context_aware_embeddings():
    """Generate embeddings with context hints for better routing."""

    service = SmartEmbeddingService()

    # Different contexts get different treatment
    contexts = [
        {
            "text": "Hello, how are you?",
            "context": "chat",
            "description": "Simple chat message"
        },
        {
            "text": "The Parties hereby agree to the terms and conditions set forth herein.",
            "context": "legal",
            "description": "Legal document"
        },
        {
            "text": "Neural networks with multiple hidden layers for deep feature extraction.",
            "context": "technical",
            "description": "Technical content"
        }
    ]

    results = []
    for item in contexts:
        request = EmbeddingRequest(
            text=item["text"],
            source_context=item["context"],  # Hints for routing
            use_cache=True
        )

        result = service.generate_embedding(request)

        print(f"{item['description']}:")
        print(f"  Strategy: {result.source}")
        print(f"  Model: {result.model_used}")
        print(f"  Quality: {result.quality_score}")
        print()

        results.append(result.embedding)

    return results
```

### 4. Batch Processing

```python
def process_documents_efficiently():
    """Process multiple documents with caching and smart routing."""

    service = SmartEmbeddingService()

    documents = [
        "This is document 1 about machine learning.",
        "This is document 2 about the same topic.",  # Will benefit from cache
        "Legal disclaimer: This contract is binding under law.",
        "Technical specification: API endpoints return JSON.",
        "This is document 1 about machine learning."  # Duplicate - cache hit
    ]

    embeddings = []
    total_time = 0

    for i, doc in enumerate(documents):
        request = EmbeddingRequest(
            text=doc,
            use_cache=True,
            metadata={"doc_id": i}
        )

        result = service.generate_embedding(request)
        embeddings.append(result.embedding)
        total_time += result.processing_time_ms

        print(f"Doc {i}: {result.source}, cached={result.cached}, "
              f"time={result.processing_time_ms:.1f}ms")

    # Show cache effectiveness
    stats = service.get_stats()
    print(f"\nBatch processing complete:")
    print(f"  Total time: {total_time:.1f}ms")
    print(f"  Cache hit rate: {stats['stats']['cache_hit_rate']:.1%}")

    return embeddings
```

## Advanced Configuration

### 1. Custom Strategy Configuration

```python
class CustomSmartEmbeddingService(SmartEmbeddingService):
    """Custom configuration for specific use cases."""

    def __init__(self):
        super().__init__()

        # Adjust thresholds for your use case
        self.complexity_threshold_high = 0.8  # More selective about Bedrock
        self.complexity_threshold_low = 0.2   # Use local more often
        self.text_length_short = 100          # Shorter threshold
        self.text_length_long = 500           # Lower threshold for quality

    def _determine_strategy(self, request):
        """Custom strategy logic."""

        # Always use Bedrock for financial/legal content
        if request.source_context in ['financial', 'legal', 'medical']:
            return EmbeddingStrategy.GATEWAY_BEDROCK

        # Use local for development/testing
        if request.source_context == 'development':
            return EmbeddingStrategy.LOCAL_FAST

        # Fall back to parent logic
        return super()._determine_strategy(request)

# Usage
custom_service = CustomSmartEmbeddingService()
```

### 2. Performance Monitoring

```python
def monitor_embedding_performance():
    """Monitor and optimize embedding performance."""

    service = SmartEmbeddingService()

    # Generate some embeddings
    test_texts = [
        "Short text",
        "This is a longer text that requires more processing time and analysis.",
        "Legal contract with specific terminology and requirements.",
        "Short text"  # Duplicate for cache testing
    ]

    for text in test_texts:
        request = EmbeddingRequest(text=text, use_cache=True)
        result = service.generate_embedding(request)

    # Get detailed statistics
    stats = service.get_stats()

    print("Performance Statistics:")
    print(f"  Total requests: {stats['stats']['total_requests']}")
    print(f"  Cache hits: {stats['stats']['cache_hits']}")
    print(f"  Cache misses: {stats['stats']['cache_misses']}")
    print(f"  Cache hit rate: {stats['stats']['cache_hit_rate']:.1%}")
    print(f"  Cache size: {stats['stats']['cache_size']} items")

    print("\nComponent Status:")
    for component, available in stats['components'].items():
        status = "✓ Available" if available else "✗ Not loaded"
        print(f"  {component}: {status}")

    print("\nConfiguration:")
    for key, value in stats['configuration'].items():
        print(f"  {key}: {value}")
```

## RAG Integration

### 1. Replace EmbeddingDelegate in RAG Adapters

```python
# Before: Using EmbeddingDelegate directly
class OldRAGAdapter:
    def __init__(self):
        from packages.tidyllm.infrastructure.delegates.embedding_delegate import EmbeddingDelegate
        self.embedder = EmbeddingDelegate()

    def process_document(self, text):
        return self.embedder.embed_text(text)

# After: Using SmartEmbeddingAdapter (drop-in replacement)
class NewRAGAdapter:
    def __init__(self):
        from packages.tidyllm.services.smart_embedding_service import SmartEmbeddingAdapter
        self.embedder = SmartEmbeddingAdapter()

    def process_document(self, text):
        # Same interface, smarter backend
        return self.embedder.embed_text(text)
```

### 2. Enhanced RAG with Context Awareness

```python
class EnhancedRAGAdapter:
    """RAG adapter that uses SmartEmbeddingService with context."""

    def __init__(self):
        self.smart_embeddings = SmartEmbeddingService()

    def process_legal_document(self, document):
        """Process legal document with high-quality embeddings."""

        # Chunk document
        chunks = self.chunk_document(document)

        embeddings = []
        for chunk in chunks:
            request = EmbeddingRequest(
                text=chunk,
                source_context="legal",        # Context hint
                require_high_quality=True,    # Force Bedrock
                use_cache=True,               # Cache for reuse
                metadata={
                    "doc_id": document.id,
                    "doc_type": "legal"
                }
            )

            result = self.smart_embeddings.generate_embedding(request)
            embeddings.append(result.embedding)

        return embeddings

    def process_chat_messages(self, messages):
        """Process chat messages with fast local embeddings."""

        embeddings = []
        for message in messages:
            request = EmbeddingRequest(
                text=message,
                source_context="chat",     # Context hint for local processing
                use_cache=True,           # Cache common phrases
                metadata={"type": "chat"}
            )

            result = self.smart_embeddings.generate_embedding(request)
            embeddings.append(result.embedding)

        return embeddings

    def chunk_document(self, document):
        """Simple document chunking."""
        # Implement your chunking logic
        return [document[i:i+500] for i in range(0, len(document), 500)]
```

### 3. Unified RAG Service

```python
class UnifiedRAGService:
    """Complete RAG service using SmartEmbeddingService."""

    def __init__(self):
        self.embeddings = SmartEmbeddingService()
        self.vector_store = {}  # Simplified - use real vector DB

    def ingest_document(self, doc_id, content, doc_type="general"):
        """Ingest document with appropriate embedding strategy."""

        # Determine quality requirement based on document type
        require_quality = doc_type in ["legal", "medical", "financial"]

        request = EmbeddingRequest(
            text=content,
            source_context=doc_type,
            require_high_quality=require_quality,
            use_cache=True,
            metadata={
                "doc_id": doc_id,
                "doc_type": doc_type
            }
        )

        result = self.embeddings.generate_embedding(request)

        # Store in vector database
        self.vector_store[doc_id] = {
            "embedding": result.embedding,
            "content": content,
            "metadata": result.metadata,
            "quality": result.quality_score
        }

        print(f"Ingested {doc_id}: {result.source} embedding, "
              f"quality={result.quality_score:.2f}")

    def search(self, query, top_k=5):
        """Search with query embedding."""

        # Generate query embedding
        request = EmbeddingRequest(
            text=query,
            source_context="search",
            use_cache=True
        )

        query_result = self.embeddings.generate_embedding(request)
        query_embedding = query_result.embedding

        # Simple similarity search (use real vector DB in production)
        scores = []
        for doc_id, doc_data in self.vector_store.items():
            # Cosine similarity (simplified)
            doc_embedding = doc_data["embedding"]
            similarity = self.cosine_similarity(query_embedding, doc_embedding)
            scores.append((doc_id, similarity, doc_data))

        # Return top-k results
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def cosine_similarity(self, a, b):
        """Simple cosine similarity calculation."""
        import math

        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0

        return dot_product / (magnitude_a * magnitude_b)

# Usage example
def rag_example():
    """Complete RAG workflow example."""

    rag = UnifiedRAGService()

    # Ingest different types of documents
    rag.ingest_document("doc1", "Machine learning is a subset of AI.", "technical")
    rag.ingest_document("doc2", "The contract is legally binding.", "legal")
    rag.ingest_document("doc3", "Hello, how can I help you?", "chat")

    # Search
    results = rag.search("What is machine learning?")

    print("\nSearch results:")
    for doc_id, score, doc_data in results:
        print(f"  {doc_id}: {score:.3f} - {doc_data['content'][:50]}...")
```

## Performance Optimization

### 1. Cache Optimization

```python
def optimize_cache_usage():
    """Best practices for cache optimization."""

    service = SmartEmbeddingService()

    # Pre-warm cache with common phrases
    common_phrases = [
        "How can I help you?",
        "Thank you for your inquiry.",
        "Please find the information below.",
        "I agree to the terms and conditions."
    ]

    print("Pre-warming cache...")
    for phrase in common_phrases:
        request = EmbeddingRequest(text=phrase, use_cache=True)
        service.generate_embedding(request)

    # Now these will be instant cache hits
    print("\nTesting cache hits:")
    for phrase in common_phrases:
        request = EmbeddingRequest(text=phrase, use_cache=True)
        result = service.generate_embedding(request)
        print(f"  '{phrase[:30]}...': cached={result.cached}, "
              f"time={result.processing_time_ms:.1f}ms")
```

### 2. Batch Processing Optimization

```python
def optimized_batch_processing():
    """Optimize batch processing with smart strategies."""

    service = SmartEmbeddingService()

    documents = [
        {"text": "Simple chat message", "type": "chat"},
        {"text": "Complex legal document with multiple clauses", "type": "legal"},
        {"text": "Technical documentation", "type": "technical"},
        {"text": "Simple chat message", "type": "chat"},  # Duplicate
    ]

    # Group by type for consistent processing
    by_type = {}
    for doc in documents:
        doc_type = doc["type"]
        if doc_type not in by_type:
            by_type[doc_type] = []
        by_type[doc_type].append(doc["text"])

    # Process each type with appropriate strategy
    results = {}
    for doc_type, texts in by_type.items():
        print(f"Processing {len(texts)} {doc_type} documents...")

        type_results = []
        for text in texts:
            request = EmbeddingRequest(
                text=text,
                source_context=doc_type,
                use_cache=True
            )
            result = service.generate_embedding(request)
            type_results.append(result)

        results[doc_type] = type_results

    # Show efficiency
    stats = service.get_stats()
    print(f"\nBatch processing complete:")
    print(f"  Cache hit rate: {stats['stats']['cache_hit_rate']:.1%}")

    return results
```

## Troubleshooting

### 1. Component Loading Issues

```python
def diagnose_components():
    """Diagnose component loading issues."""

    service = SmartEmbeddingService()

    # Test each component
    print("Component Diagnosis:")

    # Test EmbeddingDelegate
    delegate = service._get_embedding_delegate()
    if delegate:
        print("✓ EmbeddingDelegate loaded successfully")
        try:
            test_embedding = delegate.embed_text("test")
            print(f"  Test embedding: {len(test_embedding)} dimensions")
        except Exception as e:
            print(f"  ✗ Test embedding failed: {e}")
    else:
        print("✗ EmbeddingDelegate failed to load")

    # Test CorporateLLMGateway
    gateway = service._get_corporate_gateway()
    if gateway:
        print("✓ CorporateLLMGateway loaded successfully")
    else:
        print("✗ CorporateLLMGateway failed to load")

    # Test with fallback
    request = EmbeddingRequest(text="test text")
    result = service.generate_embedding(request)
    print(f"Service test: {result.source}, {result.dimensions}D")

# Run diagnosis
diagnose_components()
```

### 2. Performance Issues

```python
def diagnose_performance():
    """Diagnose performance issues."""

    service = SmartEmbeddingService()

    import time

    # Test different scenarios
    scenarios = [
        ("Short text", "Hi"),
        ("Medium text", "This is a medium length text for testing."),
        ("Long text", "This is a very long text " * 50),
        ("Duplicate", "Hi"),  # Should be cached
    ]

    print("Performance Analysis:")
    print("-" * 50)

    for name, text in scenarios:
        start_time = time.time()
        request = EmbeddingRequest(text=text, use_cache=True)
        result = service.generate_embedding(request)
        total_time = (time.time() - start_time) * 1000

        print(f"{name}:")
        print(f"  Strategy: {result.source}")
        print(f"  Cached: {result.cached}")
        print(f"  Service time: {result.processing_time_ms:.1f}ms")
        print(f"  Total time: {total_time:.1f}ms")
        print()
```

## Migration Guide

### From EmbeddingDelegate

```python
# Old code
from packages.tidyllm.infrastructure.delegates.embedding_delegate import EmbeddingDelegate

class OldService:
    def __init__(self):
        self.embedder = EmbeddingDelegate()

    def get_embedding(self, text):
        return self.embedder.embed_text(text)

# New code - Option 1: Direct replacement
from packages.tidyllm.services.smart_embedding_service import SmartEmbeddingAdapter

class NewService:
    def __init__(self):
        self.embedder = SmartEmbeddingAdapter()  # Drop-in replacement

    def get_embedding(self, text):
        return self.embedder.embed_text(text)  # Same interface

# New code - Option 2: Full features
from packages.tidyllm.services.smart_embedding_service import SmartEmbeddingService, EmbeddingRequest

class EnhancedService:
    def __init__(self):
        self.embedder = SmartEmbeddingService()

    def get_embedding(self, text, context=None, high_quality=False):
        request = EmbeddingRequest(
            text=text,
            source_context=context,
            require_high_quality=high_quality,
            use_cache=True
        )
        result = self.embedder.generate_embedding(request)
        return result.embedding
```

### From TidyLLM Providers

```python
# Old code (VIOLATION - direct provider usage)
from tidyllm.providers import bedrock
provider = bedrock()
embedding = provider.embed("text")

# New code (COMPLIANT - through gateway)
from packages.tidyllm.services.smart_embedding_service import SmartEmbeddingService, EmbeddingRequest

service = SmartEmbeddingService()
request = EmbeddingRequest(
    text="text",
    require_high_quality=True  # Will use Bedrock via gateway
)
result = service.generate_embedding(request)
embedding = result.embedding
```

## Best Practices

1. **Use Context Hints**: Always provide `source_context` for better routing
2. **Enable Caching**: Set `use_cache=True` for repeated content
3. **Match Quality to Need**: Use `require_high_quality=True` only when necessary
4. **Monitor Performance**: Regular check `get_stats()` for optimization
5. **Batch Similar Content**: Group similar documents for consistent processing
6. **Test Fallbacks**: Ensure your code handles both local and gateway sources

## Next Steps

- **Phase 2**: PostgreSQL pgvector caching (coming soon)
- **Phase 3**: Quality tracking and learning (planned)
- **Phase 4**: Model evolution and domain specialization (future)

For questions or issues, check the architecture documentation in `docs/future/SMART_EMBEDDING_SERVICE.md`.