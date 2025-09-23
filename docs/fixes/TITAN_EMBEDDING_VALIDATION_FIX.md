# Titan Embedding Validation Fix

## Problem
Multiple critical issues with Titan embeddings causing validation errors:
- Dimension mismatches between models (v1=768, v2=1024, g1=1536)
- Wrong request format (using "text" instead of "inputText")
- FAISS index pollution from mixed dimensions
- NaN/Inf values crashing downstream processing
- Settings.yaml dimensions (1024) not being respected

## Root Causes
1. **No validation**: Raw embeddings passed without checking
2. **Hardcoded dimensions**: Services hardcoding 1024 instead of reading config
3. **Wrong API field**: Using "text" instead of "inputText" for Titan
4. **Shared FAISS indexes**: All models sharing same index despite different dimensions
5. **No error handling**: NaN/Inf values causing crashes

## Solution

### 1. Titan Adapter with Validation
Created `packages/tidyllm/embedding/titan_adapter.py`:
- Centralized model registry with correct dimensions
- Strict validation for dimensions, NaN/Inf
- Correct request format with "inputText"
- Per-model configuration

```python
# Model registry - single source of truth
TITAN_MODELS = {
    "titan_v1": TitanModel(
        model_id="amazon.titan-embed-text-v1",
        dimensions=768,
        max_input_length=8000
    ),
    "titan_v2": TitanModel(
        model_id="amazon.titan-embed-text-v2:0",
        dimensions=1024,
        max_input_length=8000
    )
}

# Critical: Titan expects 'inputText', not 'text'!
def create_titan_request(text: str, normalize: bool = True) -> Dict[str, Any]:
    request = {
        "inputText": text  # NOT "text" - this is critical!
    }
```

### 2. FAISS Vector Manager with Per-Model Isolation
Created `packages/tidyllm/embedding/faiss_vector_manager.py`:
- Per-model/dimension index isolation
- Strict dimension validation
- Index naming convention: `faiss_{model}_{dims}d.index`

```python
def get_index_name(self, model_key: str, dimensions: int) -> str:
    # Each model+dimension combo needs unique name!
    return f"faiss_{model_key}_{dimensions}d.index"

def _validate_index_dimensions(self, index, expected_dims: int, model_key: str):
    if index.d != expected_dims:
        raise RuntimeError(
            f"FAISS index dimension mismatch for {model_key}: "
            f"index has {index.d}d, expected {expected_dims}d"
        )
```

### 3. Configuration Respect
Updated services to use SettingsLoader.get_config_value():
- SmartEmbeddingService: Uses config dimensions (1024)
- EmbeddingDelegate: Uses config dimensions
- No more hardcoding!

```python
# Use get_config_value with explicit defaults - NO HARDCODING!
dimensions = loader.get_config_value(
    'credentials.bedrock_llm.embeddings.dimensions',
    1024  # Only used if not in config
)
```

## Testing
Both components include comprehensive tests:

```bash
# Test Titan adapter
python packages/tidyllm/embedding/titan_adapter.py

# Test FAISS manager
python packages/tidyllm/embedding/faiss_vector_manager.py
```

## Impact
- Prevents dimension mismatch crashes
- Ensures config dimensions (1024) are respected
- Prevents FAISS index pollution
- Catches NaN/Inf before they crash processing
- Correct Titan API usage

## Key Validations
1. **Dimension Check**: Validates vector dimensions match model
2. **NaN/Inf Check**: Rejects invalid numeric values
3. **Request Format**: Uses "inputText" for Titan
4. **Index Isolation**: Each model gets separate FAISS index
5. **Config Respect**: Reads dimensions from settings.yaml

## Error Messages
Clear error messages for debugging:
```
"Dimension mismatch for titan_v1: got 1024, expected 768"
"FAISS index dimension mismatch: index has 768d, model expects 1024d"
"NaN/Inf at positions [0, 5, 10] for titan_v2"
```

## Files Created/Modified
- Created: `packages/tidyllm/embedding/titan_adapter.py`
- Created: `packages/tidyllm/embedding/faiss_vector_manager.py`
- Modified: `packages/tidyllm/services/smart_embedding_service.py`
- Modified: `packages/tidyllm/infrastructure/delegates/embedding_delegate.py`
- Modified: `infrastructure/yaml_loader.py`

## Architecture Benefits
The solution provides multiple layers of protection:
```
Application Code
    ↓
SmartEmbeddingService (config-driven)
    ↓
Titan Adapter (validation + correct API)
    ↓
FAISS Manager (per-model isolation)
    ↓
Vector Storage (clean, validated data)
```

This layered approach ensures embeddings are always valid and properly dimensioned!