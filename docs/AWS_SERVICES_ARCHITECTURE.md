# AWS Services Architecture

## Overview
Clean separation of AWS services between parent infrastructure and TidyLLM.

## Architecture Diagram
```
Compliance-QA (Parent Infrastructure)
├── infrastructure/
│   └── services/
│       ├── s3_service.py         # All S3 operations with boto3
│       └── bedrock_service.py    # All Bedrock operations with boto3
│
└── packages/tidyllm/
    └── infrastructure/
        ├── s3_delegate.py         # Borrows S3 from parent
        └── bedrock_delegate.py    # Borrows Bedrock from parent
```

## Key Principles

1. **Parent Infrastructure**: Contains all boto3 imports and AWS service implementations
2. **TidyLLM**: Pure library that delegates AWS operations to parent
3. **No Direct Dependencies**: TidyLLM never imports boto3 directly
4. **Graceful Fallback**: Works even when parent infrastructure unavailable

## Service Architecture

### S3 Service
**Location**: `infrastructure/services/s3_service.py`
- Centralized S3 operations
- Handles credentials and configuration
- Methods: upload, download, list, read/write JSON, presigned URLs

### Bedrock Service
**Location**: `infrastructure/services/bedrock_service.py`
- Manages both `bedrock` and `bedrock-runtime` clients
- Model catalog and configurations
- Methods: invoke models, embeddings, model info

### S3 Delegate
**Location**: `packages/tidyllm/infrastructure/s3_delegate.py`
- Thin wrapper that borrows from parent S3 service
- No boto3 imports
- Same interface as S3 service

### Bedrock Delegate
**Location**: `packages/tidyllm/infrastructure/bedrock_delegate.py`
- Thin wrapper that borrows from parent Bedrock service
- No boto3 imports
- Supports all Bedrock models (Claude, Titan, Llama, Mistral)

## Usage Examples

### In TidyLLM (Using Delegates)
```python
# For S3 operations
from tidyllm.infrastructure.s3_delegate import get_s3_delegate

s3 = get_s3_delegate()
if s3.is_available():
    s3.upload_file("local.txt", "s3-key", "bucket")
    data = s3.read_json("config.json", "bucket")

# For Bedrock operations
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate

bedrock = get_bedrock_delegate()
if bedrock.is_available():
    response = bedrock.invoke_claude("What is RAG?")
    models = bedrock.list_foundation_models()
```

### In Parent Infrastructure (Direct Usage)
```python
# Direct S3 usage
from infrastructure.services.s3_service import get_s3_service

s3 = get_s3_service()
s3.upload_file("file.txt", "key", "bucket")

# Direct Bedrock usage
from infrastructure.services.bedrock_service import get_bedrock_service

bedrock = get_bedrock_service()
response = bedrock.invoke_model("prompt", model_id="anthropic.claude-3-haiku")
```

## Migration Status

### ✅ Completed
- Created S3 service in parent infrastructure
- Created Bedrock service in parent infrastructure
- Created S3 delegate in TidyLLM
- Created Bedrock delegate in TidyLLM
- Updated `infrastructure/session/unified.py`
- Updated `admin/credential_loader.py`
- Updated `gateways/corporate_llm_gateway.py`
- Updated `knowledge_systems/adapters/sme_rag/sme_rag_system.py`

### 🔄 Remaining Files
Example/script files that still import boto3 directly:
- `flow/examples/sop_flow.py`
- `flow/examples/modeling_flow.py`
- `flow/examples/checklist_flow.py`
- `scripts/s3_flow_parser.py`
- `scripts/check_aws_config.py`
- `cli.py`
- `interfaces/cli.py`

## Benefits

1. **Clean Architecture**: Clear separation of concerns
2. **No Infrastructure in TidyLLM**: Remains a pure library
3. **Centralized AWS Management**: Single source of truth for AWS operations
4. **Better Testing**: Can mock services without AWS dependencies
5. **Credential Security**: Centralized credential management
6. **Model Management**: Centralized Bedrock model configurations

## Configuration

### Environment Variables
```bash
# S3 Configuration
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET=your-bucket

# Bedrock Configuration
BEDROCK_REGION=us-east-1
BEDROCK_DEFAULT_MODEL=anthropic.claude-3-haiku
```

### Programmatic Configuration
```python
# Configure S3
from tidyllm.infrastructure.s3_delegate import get_s3_delegate

s3_config = {
    'access_key_id': 'your-key',
    'secret_access_key': 'your-secret',
    'region': 'us-east-1',
    'bucket': 'your-bucket'
}
s3 = get_s3_delegate(s3_config)

# Configure Bedrock
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate

bedrock_config = {
    'access_key_id': 'your-key',
    'secret_access_key': 'your-secret',
    'region': 'us-east-1',
    'default_model': 'anthropic.claude-3-sonnet'
}
bedrock = get_bedrock_delegate(bedrock_config)
```

## Notes

- boto3 is only imported in parent infrastructure services
- Delegates provide same interface as AWS clients for compatibility
- Services handle all error cases gracefully
- Mock implementations available when AWS not accessible