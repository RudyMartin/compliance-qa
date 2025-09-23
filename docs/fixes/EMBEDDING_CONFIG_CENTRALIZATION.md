# Embedding Configuration Centralization Fix

## Problem
Embedding dimensions and model IDs were hardcoded throughout the codebase:
- SmartEmbeddingService: hardcoded `dimensions=1024` and `model_id="titan-embed-v2"`
- EmbeddingDelegate: hardcoded `dimensions=384` (MiniLM)
- EmbeddingWorker: hardcoded `default_target_dimension=1024`
- Settings.yaml had `dimensions: 1024` but it was NOT being respected

## Root Cause
- No centralized configuration management
- Services hardcoding their own defaults
- Settings.yaml values being ignored
- Model IDs using short names instead of full AWS Bedrock format

## Solution

### 1. Enhanced SettingsLoader with YAML Path Lookup
Added new methods to the existing global SettingsLoader singleton:

```python
# infrastructure/yaml_loader.py
class SettingsLoader:
    def get_config_value(self, yaml_path: str, default: Any = None) -> Any:
        """Get configuration value by YAML path with default fallback."""
        # Example: loader.get_config_value('credentials.bedrock_llm.embeddings.dimensions', 1024)

    def get_config_value_or_error(self, yaml_path: str) -> Any:
        """Get configuration value or raise error if not found."""

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration - single source of truth."""

    def get_embedding_dimensions(self) -> Optional[int]:
        """Get configured embedding dimensions."""

    def get_embedding_model_id(self) -> Optional[str]:
        """Get configured embedding model ID."""
```

### 2. Usage Pattern - No More Hardcoding
Services now use the global SettingsLoader:

```python
from infrastructure.yaml_loader import get_settings_loader

loader = get_settings_loader()

# Get with explicit defaults (only used if not in config)
dimensions = loader.get_config_value('credentials.bedrock_llm.embeddings.dimensions', 1024)
model_id = loader.get_config_value('credentials.bedrock_llm.embeddings.model_id', 'amazon.titan-embed-text-v2:0')

# Or require a value (throws error if missing)
api_key = loader.get_config_value_or_error('credentials.aws_basic.access_key_id')
```

### 3. Configuration Hierarchy
The SettingsLoader checks multiple locations in order:
1. `credentials.bedrock_llm.embeddings.*`
2. Root level `embeddings.*`
3. Caller-provided default
4. None (if no default provided)

### 4. Services Updated
- **SmartEmbeddingService**: Now uses `loader.get_embedding_config()`
- **EmbeddingDelegate**: Now uses `loader.get_embedding_dimensions()`
- **EmbeddingWorker**: Uses config values instead of hardcoded defaults
- **CorporateLLMGateway**: Already had model ID mapping

## Key Benefits
1. **Single Source of Truth**: All config comes from SettingsLoader
2. **No Hardcoding**: Defaults are explicit at call site, not buried in code
3. **Flexible Lookups**: Use YAML paths like `a.b.c.d` to access any value
4. **Safe Defaults**: Provide fallbacks only where needed
5. **Future Proof**: When config changes, no code changes needed

## Testing
```bash
python -c "
from infrastructure.yaml_loader import get_settings_loader
loader = get_settings_loader()
print(f'Dimensions: {loader.get_embedding_dimensions()}')  # Returns: 1024
print(f'Model ID: {loader.get_embedding_model_id()}')      # Returns: cohere.embed-english-v3
"
```

## Configuration Values
From settings.yaml:
```yaml
credentials:
  bedrock_llm:
    embeddings:
      dimensions: 1024        # Now respected!
      model_id: cohere.embed-english-v3
      batch_size: 25
      cache_enabled: true
      normalize: true
      timeout: 30
```

## Impact
- Embedding dimensions now correctly use 1024 from config
- Model IDs use full AWS format from config
- Services no longer have hardcoded values
- Configuration changes don't require code changes

## Related Files
- `infrastructure/yaml_loader.py` - Enhanced with new methods
- `packages/tidyllm/services/smart_embedding_service.py` - Updated to use config
- `packages/tidyllm/infrastructure/delegates/embedding_delegate.py` - Updated to use config
- `packages/tidyllm/config/embedding_config_manager.py` - Created but deprecated in favor of SettingsLoader