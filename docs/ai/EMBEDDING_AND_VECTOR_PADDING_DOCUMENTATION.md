# Embedding and Vector Padding Documentation
*Updated for AWS Bedrock Integration and pgvector Compatibility*

## Overview

This document provides comprehensive documentation for the embedding standardization system, vector padding functionality, and AWS Bedrock model integration within the TidyLLM V2 architecture.

## 🎯 CRYSTAL CLEAR MODEL MAPPING

### What You Currently Have:
- **Text Models**: 4 Claude models configured ✅
- **Embedding Models**: **NONE configured** ❌

### What You Need to Add:
- **Recommended**: `amazon.titan-embed-text-v2:0` (native 1024D)
- **Alternative**: `cohere.embed-english-v3` (native 1024D)
- **Avoid**: `amazon.titan-embed-text-v1` (1536D requires truncation)

### Your Database Setup:
- **Database**: vectorqa (PostgreSQL + pgvector)
- **Standard Dimension**: 1024D
- **Host**: [AWS RDS PostgreSQL cluster]

## System Architecture

### Database Configuration
- **Database**: vectorqa on AWS RDS
- **Host**: [AWS RDS PostgreSQL cluster]
- **Engine**: PostgreSQL with pgvector extension
- **Standard Dimension**: 1024D (standardized across all models)

### Key Components

1. **EmbeddingStandardizer** (`packages/tidyllm/knowledge_systems/embedding_config.py`)
2. **VectorManager** (`packages/tidyllm/knowledge_systems/vector_manager.py`)
3. **AWS Bedrock Integration** (Portal setup configuration)

## Current Model Configuration vs Available Options

### CURRENTLY CONFIGURED TEXT MODELS (in settings.yaml)

**Default Model (Line 74):**
- `anthropic.claude-3-sonnet-20240229-v1:0`

**Current Model Mappings (Lines 75-79):**
| Friendly Name | Bedrock Model ID |
|---------------|------------------|
| `claude-3-5-sonnet` | `anthropic.claude-3-5-sonnet-20240620-v1:0` |
| `claude-3-haiku` | `anthropic.claude-3-haiku-20240307-v1:0` |
| `claude-3-opus` | `anthropic.claude-3-opus-20240229-v1:0` |
| `claude-3-sonnet` | `anthropic.claude-3-sonnet-20240229-v1:0` |

**⚠️ IMPORTANT**: You currently have **NO EMBEDDING MODELS** configured in settings.yaml!

### AVAILABLE BEDROCK EMBEDDING MODELS (For Configuration)

| Model ID | Native Dimensions | Max Tokens | Padding Strategy | Recommended |
|----------|------------------|------------|------------------|-------------|
| `amazon.titan-embed-text-v1` | **1536** | 8192 | **Truncate to 1024D** | ❌ |
| `amazon.titan-embed-text-v2:0` | **1024** | 8192 | **None needed** | ✅ **BEST** |
| `cohere.embed-english-v3` | **1024** | 512 | **None needed** | ✅ |
| `cohere.embed-multilingual-v3` | **1024** | 512 | **None needed** | ✅ |

### Recommendation for Your Setup

**Add this to your settings.yaml:**
```yaml
credentials:
  bedrock_llm:
    # Your existing settings...

    # ADD EMBEDDING CONFIGURATION:
    embedding_config:
      default_model: amazon.titan-embed-text-v2:0  # Native 1024D
      model_mapping:
        titan-v1: amazon.titan-embed-text-v1       # 1536D → truncate
        titan-v2: amazon.titan-embed-text-v2:0     # 1024D → perfect
        cohere-en: cohere.embed-english-v3         # 1024D → perfect
        cohere-multi: cohere.embed-multilingual-v3 # 1024D → perfect
      target_dimension: 1024
```

## Existing Functions and Classes

### 1. EmbeddingWorker (packages/tidyllm/infrastructure/workers/embedding_worker.py)

The EmbeddingWorker is a comprehensive async worker for vector embedding generation with built-in standardization:

```python
class EmbeddingWorker(BaseWorker):
    """Worker for vector embedding generation operations."""

    def __init__(self, default_target_dimension: int = 1024, batch_size: int = 32):
        # Supports multiple TidyLLM providers (bedrock, claude, openai)
        # Built-in dimension standardization
        # Async batch processing

    async def generate_embedding(self, text_id: str, text_content: str,
                                model_provider: str = "default",
                                target_dimension: int = 1024) -> str:
        """Submit single embedding generation task."""

    async def generate_batch_embeddings(self, batch_id: str,
                                       texts: List[Dict[str, str]],
                                       model_provider: str = "default") -> str:
        """Submit batch embedding generation task."""
```

**Key Features:**
- Automatic dimension standardization via `_standardize_dimension()`
- L2 normalization via `_normalize_embedding()`
- Multi-provider support (Bedrock, Claude, OpenAI)
- Async batch processing with configurable batch sizes
- Fallback mock embedding generation for testing

### 2. VectorStorage Facade (packages/tidyllm/knowledge_systems/facades/vector_storage.py)

Simple interface for vector storage with automatic standardization:

```python
class VectorStorage:
    """Simple facade for vector storage with standardized embeddings"""

    def __init__(self, collection_name: str = "default_collection",
                 dimension: int = 1024):
        # Integrates with VectorManager and EmbeddingStandardizer

    def store(self, embedding, text: str, document_id: str,
              model_name: str = None) -> Optional[str]:
        """Store embedding with associated text and metadata"""

    def search(self, query_embedding, limit: int = 10,
               threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar vectors"""

    def search_by_text(self, query_text: str,
                      embedding_model: str = "titan_v2_1024") -> List[Dict[str, Any]]:
        """Search using text query (will be embedded automatically)"""
```

**Key Features:**
- Automatic embedding standardization before storage
- Integration with existing VectorManager backend
- Fallback storage simulation for development
- Built-in health checking and collection statistics

### 3. Dimension Standardization Functions

#### From EmbeddingWorker:
```python
def _standardize_dimension(self, embedding: List[float], target_dimension: int) -> List[float]:
    """Standardize embedding to target dimension."""
    current_dim = len(embedding)

    if current_dim == target_dimension:
        return embedding
    elif current_dim > target_dimension:
        # Truncate
        return embedding[:target_dimension]
    else:
        # Pad with zeros
        return embedding + [0.0] * (target_dimension - current_dim)

def _normalize_embedding(self, embedding: List[float]) -> List[float]:
    """L2 normalize the embedding vector."""
    norm = sum(x*x for x in embedding) ** 0.5
    if norm > 0:
        return [x / norm for x in embedding]
    return embedding
```

#### From VectorStorage (with TLM integration):
```python
def _fallback_standardize(self, embedding):
    """Fallback standardization using TLM (numpy replacement)"""
    current_dim = len(embedding)

    if current_dim == self.dimension:
        return embedding
    elif current_dim < self.dimension:
        # Pad with zeros using TLM
        if TLM_AVAILABLE:
            padding = np.zeros(self.dimension - current_dim)
            return np.concatenate([embedding, padding])
        else:
            # Fallback to Python lists
            padding = [0.0] * (self.dimension - current_dim)
            return list(embedding) + padding
    else:
        # Truncate
        return embedding[:self.dimension] if TLM_AVAILABLE else list(embedding)[:self.dimension]
```

### Padding Strategies

#### 1. Truncation Strategy (Titan v1: 1536D → 1024D)
- **When**: Native dimension > target dimension
- **Method**: Remove excess dimensions from the end
- **Impact**: Minimal loss of semantic information
- **Implementation**: `embedding[:target_dimension]`

#### 2. Zero Padding Strategy (smaller models → 1024D)
- **When**: Native dimension < target dimension
- **Method**: Append zeros to reach target dimension
- **Impact**: No information loss, maintains original semantics
- **Implementation**: `embedding + [0.0] * (target_dimension - current_dim)`

#### 3. No Transformation (Native 1024D)
- **When**: Native dimension == target dimension
- **Method**: Use embedding as-is
- **Models**: Titan v2, Cohere models

## Vector Database Integration

### pgvector Configuration

```yaml
# Database configuration in settings.yaml
databases:
  primary:
    credential_ref: postgresql_primary
    engine: postgresql
    connection_pool_size: 5
    features:
      connection_validation: true
      vector_search: true
      pgvector_extension: true
```

### Vector Storage Schema

```sql
-- Standard vector table structure
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content_hash VARCHAR(64) UNIQUE,
    embedding vector(1024),  -- Fixed 1024 dimensions
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops);
```

## Portal Integration

### Advanced Model Configuration

The Setup Portal provides comprehensive model configuration through 4 main tabs:

#### 1. Models Tab
- Default model selection
- Enable/disable specific models
- Model availability status

#### 2. Mappings Tab
- View current model ID mappings
- Add custom friendly name mappings
- Bedrock model ID validation

#### 3. Adapter Settings Tab
- **Timeout**: 10-300 seconds (default: 60)
- **Retry Attempts**: 0-10 (default: 3)
- **Circuit Breaker**: Enable/disable fault tolerance

#### 4. Embeddings Tab
- Model-specific dimension display
- Auto-detection of padding requirements
- Database compatibility checking

### Database Compatibility Check

```python
def check_vector_database_compatibility():
    """Check pgvector database for maximum supported dimensions."""
    try:
        # Query current vector configuration
        result = db_adapter.execute_query(
            "SELECT MAX(vector_dims(embedding)) FROM embeddings"
        )
        max_dimensions = result[0][0] if result else 1024

        return {
            'max_supported_dimensions': max_dimensions,
            'current_standard': 1024,
            'compatible': max_dimensions >= 1024
        }
    except Exception as e:
        return {'error': str(e)}
```

## Implementation Best Practices

### 1. Model Selection
- Prefer native 1024D models (Titan v2, Cohere) to avoid transformations
- Use Titan v1 only when specific features are required
- Consider context window requirements (512 vs 8192 tokens)

### 2. Vector Padding
- Always validate embedding dimensions before storage
- Use consistent padding strategy across all models
- Monitor for dimension mismatches in production

### 3. Database Optimization
- Use appropriate vector similarity indexes (ivfflat, hnsw)
- Partition large embedding tables by model type
- Regular VACUUM and ANALYZE for optimal performance

### 4. Error Handling
- Validate model availability before embedding generation
- Implement fallback models for high availability
- Log dimension mismatches for debugging

## Configuration Examples

### Production Settings

```yaml
# Bedrock LLM Configuration
credentials:
  bedrock_llm:
    default_model: anthropic.claude-3-5-sonnet-20240620-v1:0
    adapter_config:
      timeout: 60
      retry_attempts: 3
      circuit_breaker: true

    # Embedding-specific configuration
    embedding_config:
      default_model: amazon.titan-embed-text-v2:0
      target_dimension: 1024
      padding_strategy: auto
      fallback_model: cohere.embed-english-v3
```

### Development Settings

```yaml
# Development/Testing Configuration
embedding_config:
  debug_mode: true
  validate_dimensions: true
  log_transformations: true
  dimension_tolerance: 0  # Strict dimension checking
```

## Monitoring and Metrics

### Key Metrics to Track
- Embedding dimension consistency
- Padding operation frequency
- Model response times
- Vector storage efficiency
- Search accuracy by model type

### Health Checks
- Database vector dimension limits
- Model availability status
- Embedding generation success rates
- Vector index performance

## Troubleshooting

### Common Issues

1. **Dimension Mismatch Errors**
   - Verify model configuration
   - Check EmbeddingStandardizer settings
   - Validate database schema

2. **Performance Degradation**
   - Review vector index usage
   - Check padding overhead
   - Monitor model response times

3. **Model Availability Issues**
   - Verify AWS credentials
   - Check Bedrock service status
   - Implement fallback mechanisms

### Debug Commands

```python
# Validate embedding standardization
standardizer = EmbeddingStandardizer()
test_embedding = generate_test_embedding(model_id)
standardized = standardizer.standardize(test_embedding, model_id)
print(f"Original: {len(test_embedding)}D → Standardized: {len(standardized)}D")

# Check database compatibility
compatibility = check_vector_database_compatibility()
print(f"Database supports up to {compatibility['max_supported_dimensions']}D vectors")
```

## Version History

- **v2.0.0**: Initial Bedrock integration with pgvector
- **v2.1.0**: Added EmbeddingStandardizer with multiple padding strategies
- **v2.2.0**: Portal integration with advanced model configuration
- **v2.3.0**: Enhanced database compatibility checking
- **v2.4.0**: Current version with comprehensive documentation

## Quick Usage Examples

### Using EmbeddingWorker for Production Embedding Generation

```python
from packages.tidyllm.infrastructure.workers.embedding_worker import EmbeddingWorker

# Initialize worker with target dimension
worker = EmbeddingWorker(default_target_dimension=1024, batch_size=32)

# Single embedding generation
task_id = await worker.generate_embedding(
    text_id="doc_123",
    text_content="Your text content here",
    model_provider="bedrock",  # Uses AWS Bedrock Titan v2
    target_dimension=1024
)

# Batch processing for efficiency
texts = [
    {"id": "doc_1", "content": "First document"},
    {"id": "doc_2", "content": "Second document"},
    {"id": "doc_3", "content": "Third document"}
]
batch_task_id = await worker.generate_batch_embeddings(
    batch_id="batch_001",
    texts=texts,
    model_provider="bedrock"
)
```

### Using VectorStorage for Simple Operations

```python
from packages.tidyllm.knowledge_systems.facades.vector_storage import VectorStorage

# Initialize storage with collection
storage = VectorStorage(
    collection_name="my_documents",
    dimension=1024
)

# Store embeddings with automatic standardization
storage_id = storage.store(
    embedding=raw_embedding,  # Any dimension - will be standardized to 1024D
    text="Document content",
    document_id="doc_001",
    metadata={"source": "pdf", "page": 1}
)

# Search similar vectors
results = storage.search(
    query_embedding=query_vector,
    limit=10,
    threshold=0.7
)

# Search by text (auto-embedding)
text_results = storage.search_by_text(
    query_text="What is the capital of France?",
    embedding_model="titan_v2_1024",
    limit=5
)
```

### Standalone Convenience Functions

```python
from packages.tidyllm.knowledge_systems.facades.vector_storage import store_embedding, search_similar

# Quick storage
storage_id = store_embedding(
    embedding=my_embedding,
    text="Content to store",
    document_id="quick_doc",
    collection="default"
)

# Quick search
results = search_similar(
    query_embedding=search_vector,
    limit=5,
    collection="default"
)
```

### Manual Dimension Standardization

```python
# If you need to manually standardize embeddings
def standardize_embedding(embedding, target_dim=1024):
    """Manual standardization function based on EmbeddingWorker implementation."""
    current_dim = len(embedding)

    if current_dim == target_dim:
        return embedding
    elif current_dim > target_dim:
        # Truncate (e.g., Titan v1: 1536D → 1024D)
        return embedding[:target_dim]
    else:
        # Pad with zeros
        return embedding + [0.0] * (target_dim - current_dim)

# Usage
titan_v1_embedding = get_titan_v1_embedding(text)  # Returns 1536D
standardized = standardize_embedding(titan_v1_embedding, 1024)  # Now 1024D
```

## Related Files

- `packages/tidyllm/infrastructure/workers/embedding_worker.py` - Main embedding generation worker
- `packages/tidyllm/knowledge_systems/facades/vector_storage.py` - Vector storage facade
- `packages/tidyllm/knowledge_systems/embedding_config.py` - EmbeddingStandardizer class
- `packages/tidyllm/knowledge_systems/vector_manager.py` - Core vector management
- `portals/setup/new_setup_portal.py` (lines 975-1243) - Portal model configuration
- `infrastructure/settings.yaml` (credentials and service configuration)
- `domain/services/setup_service.py` (test_bedrock_access method)

---

*This documentation is maintained as part of the TidyLLM V2 architecture and should be updated whenever embedding models or vector configurations change.*