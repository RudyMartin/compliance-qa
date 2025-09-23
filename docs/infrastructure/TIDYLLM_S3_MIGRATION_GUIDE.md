# TidyLLM S3 Migration Guide

## Overview
Migrating TidyLLM from direct boto3 imports to using parent infrastructure S3 service.

## Architecture
```
Compliance-QA (Parent)
├── infrastructure/
│   └── services/
│       └── s3_service.py  # ← All boto3 imports here
│
└── packages/tidyllm/
    └── infrastructure/
        └── s3_delegate.py  # ← Borrows from parent
```

## Migration Pattern

### Before (Direct boto3 import):
```python
import boto3

s3_client = boto3.client('s3')
s3_client.upload_file(file_path, bucket, key)
```

### After (Using parent infrastructure):
```python
from tidyllm.infrastructure.s3_delegate import get_s3_delegate

s3 = get_s3_delegate()
s3.upload_file(file_path, key, bucket)
```

## Files to Update

### Core Files with boto3 imports:
1. `knowledge_systems/adapters/sme_rag/sme_rag_system.py`
2. `infrastructure/session/unified.py`
3. `admin/credential_loader.py`
4. `gateways/corporate_llm_gateway.py`
5. `validators/aws.py`

### Example/Script Files (Lower Priority):
- `flow/examples/sop_flow.py`
- `flow/examples/modeling_flow.py`
- `flow/examples/checklist_flow.py`
- `scripts/s3_flow_parser.py`
- `scripts/check_aws_config.py`

## Step-by-Step Migration

### Step 1: Update imports
Replace:
```python
import boto3
```

With:
```python
from tidyllm.infrastructure.s3_delegate import get_s3_delegate
```

### Step 2: Update client creation
Replace:
```python
s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')
```

With:
```python
s3_delegate = get_s3_delegate()
```

### Step 3: Update method calls
Map boto3 methods to delegate methods:

| boto3 Method | S3 Delegate Method |
|-------------|-------------------|
| `s3_client.upload_file()` | `s3_delegate.upload_file()` |
| `s3_client.download_file()` | `s3_delegate.download_file()` |
| `s3_client.list_objects_v2()` | `s3_delegate.list_objects()` |
| `s3_client.get_object()` | `s3_delegate.read_json()` |
| `s3_client.put_object()` | `s3_delegate.write_json()` |
| `s3_client.head_object()` | `s3_delegate.exists()` |
| `s3_client.delete_object()` | `s3_delegate.delete()` |
| `s3_client.generate_presigned_url()` | `s3_delegate.get_presigned_url()` |

## Benefits

1. **Clean Architecture**: TidyLLM remains a pure library
2. **Centralized Configuration**: All AWS config in parent infrastructure
3. **Better Testing**: Can mock S3 service without boto3
4. **Credential Management**: Single source of truth for AWS credentials
5. **Fallback Support**: Graceful degradation when S3 not available

## Implementation Status

- [x] Created parent S3 service (`infrastructure/services/s3_service.py`)
- [x] Created TidyLLM delegate (`packages/tidyllm/infrastructure/s3_delegate.py`)
- [ ] Update core files to use delegate
- [ ] Update example/script files
- [ ] Remove direct boto3 imports
- [ ] Test migration