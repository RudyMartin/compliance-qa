# Unified AWS Architecture

## Overview
Single, unified AWS service in parent infrastructure that TidyLLM borrows from.

## Simple Architecture
```
Compliance-QA (Parent Infrastructure)
├── infrastructure/
│   └── services/
│       └── aws_service.py        # ONE service for ALL AWS operations
│
└── packages/tidyllm/
    └── infrastructure/
        └── aws_delegate.py        # ONE delegate that borrows everything
```

## Key Benefits
- **Single Source of Truth**: One file for all AWS operations
- **Easy to Track**: All boto3 imports in one place
- **Easy to Fix**: One service to maintain
- **Clean Separation**: TidyLLM remains pure, infrastructure stays in parent

## The Unified AWS Service

**Location**: `infrastructure/services/aws_service.py`

Manages ALL AWS operations:
- **S3**: Upload, download, list, JSON operations, presigned URLs
- **Bedrock**: Both clients, all models, embeddings
- **STS**: Caller identity, role assumption
- **Future**: Easy to add more AWS services here

## The Unified AWS Delegate

**Location**: `packages/tidyllm/infrastructure/aws_delegate.py`

Single delegate that:
- Borrows ALL functionality from parent
- Never imports boto3
- Provides same interface as AWS clients
- Includes compatibility functions for existing code

## Usage

### In TidyLLM
```python
from tidyllm.infrastructure.aws_delegate import get_aws_delegate

# Get the unified delegate
aws = get_aws_delegate()

# S3 operations
aws.upload_file("file.txt", "key", "bucket")
data = aws.read_json("config.json", "bucket")

# Bedrock operations
response = aws.invoke_claude("What is RAG?")
models = aws.list_foundation_models()

# STS operations
identity = aws.get_caller_identity()

# Health check
health = aws.health_check()
```

### In Parent Infrastructure
```python
from infrastructure.services.aws_service import get_aws_service

# Get the unified service
aws = get_aws_service()

# All the same operations available
aws.upload_file("file.txt", "key", "bucket")
response = aws.invoke_model("prompt", "anthropic.claude-3-haiku")
```

## Configuration

Single configuration for everything:
```python
config = {
    'access_key_id': 'your-key',
    'secret_access_key': 'your-secret',
    'region': 'us-east-1',
    'bucket': 'default-bucket',
    'default_model': 'anthropic.claude-3-haiku'
}

# In TidyLLM
from tidyllm.infrastructure.aws_delegate import get_aws_delegate
aws = get_aws_delegate(config)

# In Parent
from infrastructure.services.aws_service import get_aws_service
aws = get_aws_service(config)
```

## Migration

Old code still works with compatibility functions:
```python
# These all return the same unified delegate
from tidyllm.infrastructure.aws_delegate import get_s3_delegate, get_bedrock_delegate
s3 = get_s3_delegate()      # Works - returns unified delegate
bedrock = get_bedrock_delegate()  # Works - returns unified delegate
```

## Summary

✅ **ONE** AWS service in parent infrastructure
✅ **ONE** AWS delegate in TidyLLM
✅ **ALL** boto3 imports in one file
✅ **EASY** to track, debug, and maintain
✅ **CLEAN** architecture with clear separation