# Infrastructure Delegates

All delegates are located in this directory for easy discovery.

## Available Delegates

### 1. `bedrock_delegate.py`
**Purpose**: LLM operations via AWS Bedrock
```python
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate
delegate = get_bedrock_delegate()
response = delegate.invoke_model(prompt, model_id)
```

### 2. `s3_delegate.py`
**Purpose**: S3 storage operations
```python
from tidyllm.infrastructure.s3_delegate import get_s3_delegate
delegate = get_s3_delegate()
success = delegate.upload_file(file_path, s3_key)
```

### 3. `aws_delegate.py`
**Purpose**: General AWS operations (STS, session management)
```python
from tidyllm.infrastructure.aws_delegate import get_aws_delegate
delegate = get_aws_delegate()
session = delegate.get_session()
```

## Delegate Pattern Rules

1. **All delegates go HERE** - Don't create delegates elsewhere
2. **Naming convention**: `<service>_delegate.py`
3. **Export pattern**: Always provide `get_<service>_delegate()` function
4. **Fallback behavior**: Delegates handle their own fallbacks when parent infrastructure isn't available

## Why Delegates?

- **No direct infrastructure imports** in application/domain layers
- **Package independence** - tidyllm works without parent infrastructure
- **Single location** - Easy to find all infrastructure access points
- **Consistent pattern** - All delegates work the same way

## Creating a New Delegate

1. Create file here: `packages/tidyllm/infrastructure/<service>_delegate.py`
2. Follow the pattern from existing delegates
3. Always try to import parent infrastructure, fallback to direct boto3 if needed
4. Provide a `get_<service>_delegate()` singleton function

## Using Delegates

### From TidyLLM packages:
```python
from tidyllm.infrastructure.<service>_delegate import get_<service>_delegate
```

### From outside TidyLLM:
```python
from packages.tidyllm.infrastructure.<service>_delegate import get_<service>_delegate
```

## Remember

**When you need infrastructure access, look here FIRST!**
All delegates are in this one directory.