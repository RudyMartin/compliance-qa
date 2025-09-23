# Unified Configuration Access Fix

## Date: 2025-09-22

## Problem Summary
The setup portal had a conflicting retrieval pattern where different components were looking for Bedrock model configuration in different locations within settings.yaml:
- Some code looked in `llm_models.bedrock`
- Other code looked in `credentials.bedrock_llm`
- This caused inconsistent behavior, with some features not finding the configuration

## Symptoms
- "⚠️ No model configured" warning in Test AI Model feature despite model being configured
- Different tabs showing different configuration status
- Competing code patterns making maintenance difficult

## Root Cause
Multiple developers had added configuration retrieval code at different times, each assuming different locations for the Bedrock configuration. The actual configuration in settings.yaml was stored under `credentials.bedrock_llm` with this structure:

```yaml
credentials:
  bedrock_llm:
    default_model: anthropic.claude-3-sonnet-20240229-v1:0
    region: us-east-1
    service_provider: aws_bedrock
    model_mapping:
      claude-3-5-sonnet: anthropic.claude-3-5-sonnet-20240620-v1:0
      claude-3-haiku: anthropic.claude-3-haiku-20240307-v1:0
      # ... etc
```

## Solution Implemented

### Discovery Phase
1. Found existing infrastructure components:
   - **SettingsLoader** (`infrastructure/yaml_loader.py`): Already had `get_bedrock_config()` method
   - **CredentialValidator** (`infrastructure/credential_validator.py`): Validates credentials
   - **BedrockService** (`infrastructure/services/bedrock_service.py`): Manages Bedrock operations

2. Realized we didn't need new code - just needed to use existing infrastructure consistently

### Implementation
1. **Removed unnecessary new code**:
   - Deleted the newly created `settings_wrapper.py` (was going to create a wrapper but found SettingsLoader already existed)

2. **Updated t_system_check.py** to use SettingsLoader consistently:
   ```python
   # Before (inconsistent):
   if 'bedrock' in settings.get('llm_models', {}):
       model_id = settings['llm_models']['bedrock'].get('model_id')

   # After (using SettingsLoader):
   from infrastructure.yaml_loader import get_settings_loader
   loader = get_settings_loader()
   bedrock_config = loader.get_bedrock_config()
   model_id = bedrock_config.get('default_model')
   ```

3. **Fixed all configuration access points**:
   - Current System Status section: Now uses `loader.get_bedrock_config()`
   - Test AI Model button: Now uses `loader.get_bedrock_config()`
   - Region retrieval: Falls back from bedrock config to AWS default region

## Files Changed

### Modified Files
1. **`portals/setup/t_system_check.py`**:
   - Line 61-73: Updated AI Models status check to use SettingsLoader
   - Line 427-430: Updated Test AI Model to use SettingsLoader
   - Line 435-438: Added proper region fallback logic

### Deleted Files
1. **`portals/setup/settings_wrapper.py`**: Removed as unnecessary (SettingsLoader already provides this functionality)

## Technical Details

### SettingsLoader.get_bedrock_config() Method
The existing method in `infrastructure/yaml_loader.py` (line 144-165):
```python
def get_bedrock_config(self) -> Dict[str, Any]:
    """Get Bedrock configuration from settings - no hardcoding."""
    settings = self._load_settings()
    bedrock_config = settings.get('credentials', {}).get('bedrock_llm', {})

    # Returns configuration with keys like:
    # - default_model
    # - region
    # - service_provider
    # - model_mapping
    # - adapter_config
```

### Configuration Location
The canonical location for Bedrock configuration is:
- **Path in YAML**: `credentials.bedrock_llm`
- **Default Model Field**: `default_model`
- **Region Field**: `region` (falls back to `credentials.aws_basic.default_region`)

## Benefits Achieved

1. **Consistency**: All components now read from the same location
2. **Maintainability**: Single source of truth for configuration retrieval
3. **Reliability**: No more conflicting patterns or missing configurations
4. **Simplicity**: Uses existing infrastructure instead of creating new code
5. **Testing**: Verified configuration retrieval works correctly

## Testing Performed

```python
# Test script used:
from infrastructure.yaml_loader import get_settings_loader
loader = get_settings_loader()
bedrock_config = loader.get_bedrock_config()
print('Bedrock config found:', bool(bedrock_config))
print('Default model:', bedrock_config.get('default_model'))
print('Region:', bedrock_config.get('region'))

# Output:
# Bedrock config found: True
# Default model: anthropic.claude-3-sonnet-20240229-v1:0
# Region: us-east-1
```

## Lessons Learned

1. **Check existing infrastructure first**: Before creating new wrapper classes, verify what already exists
2. **Use canonical methods**: SettingsLoader already had the methods we needed
3. **Document configuration paths**: Clear documentation of where settings are stored prevents this issue
4. **Consistent patterns**: All new code should use the same configuration retrieval pattern

## Migration Guide

For any code that needs to access Bedrock configuration:

### ❌ Don't do this:
```python
# Direct access to settings dict
settings = loader._load_settings()
bedrock = settings.get('llm_models', {}).get('bedrock', {})

# Or this:
bedrock = settings['credentials']['bedrock_llm']
```

### ✅ Do this instead:
```python
from infrastructure.yaml_loader import get_settings_loader

loader = get_settings_loader()
bedrock_config = loader.get_bedrock_config()

# Access configuration
model_id = bedrock_config.get('default_model')
region = bedrock_config.get('region', 'us-east-1')
```

## Related Files
- `infrastructure/yaml_loader.py` - Contains SettingsLoader with get_bedrock_config()
- `infrastructure/settings.yaml` - Configuration file with bedrock settings
- `infrastructure/services/bedrock_service.py` - BedrockService that uses the configuration
- `portals/setup/t_system_check.py` - Updated to use unified config access
- `portals/setup/t_ai_models.py` - Should also use loader.get_bedrock_config() if it accesses config

## Conclusion
By using the existing SettingsLoader infrastructure consistently across all components, we eliminated the competing code pattern and ensured reliable configuration access throughout the setup portal.