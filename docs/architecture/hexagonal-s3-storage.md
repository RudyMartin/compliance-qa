# Hexagonal Architecture - S3 Storage System

## Overview
The S3 storage system implements a clean hexagonal architecture with delegation pattern. The domain layer (S3Manager) contains business logic for file versioning, path generation, and metadata management, while delegating infrastructure operations through UnifiedSessionManager to the S3Service adapter.

## Architecture Diagram

```
         PRIMARY PORTS (Application Side)                 SECONDARY PORTS (Infrastructure Side)
    ┌──────────────────────────────────┐                ┌────────────────────────────────┐
    │  Domain Scripts                  │                │  IS3Storage Interface          │
    │  • mvr_analysis_s3.py           │                │  • upload_file()               │
    │  • s3_flow_parser.py            │                │  • download_file()             │
    │  • execute_robots3_workflow.py  │                │  • list_objects()              │
    │  (Application Entry Points)      │                │  • delete_object()             │
    └──────────┬───────────────────────┘                └──────────▲─────────────────────┘
               │                                                     │
               ▼                                                     │
    ┌────────────────────────────────────────────────────────────────────────────────────┐
    │                           DOMAIN CORE (S3 Business Logic)                          │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                          S3Manager (Knowledge Systems)                        │ │
    │  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  Core Business Rules:                                                  │ │ │
    │  │  │  • File versioning logic                                              │ │ │
    │  │  │  • Path generation strategies (build_s3_path)                         │ │ │
    │  │  │  • Metadata management                                                │ │ │
    │  │  │  • Content hashing and deduplication                                  │ │ │
    │  │  │  • Knowledge base organization                                        │ │ │
    │  │  └────────────────────────────────────────────────────────────────────────┘ │ │
    │  │                                                                              │ │
    │  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  Domain Models:                                                        │ │ │
    │  │  │  • S3Config (configuration dataclass)                                  │ │ │
    │  │  │  • UploadResult (operation results)                                    │ │ │
    │  │  │  • S3Path (path abstraction)                                          │ │ │
    │  │  └────────────────────────────────────────────────────────────────────────┘ │ │
    │  └──────────────────────────────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
    ┌────────────────────────────────────────────────────────────────────────────────────┐
    │                              ADAPTER LAYER                                         │
    │                                                                                    │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                     UnifiedSessionManager (Delegation Hub)                    │ │
    │  │  • Manages S3 client lifecycle                                               │ │
    │  │  • Handles credential resolution                                              │ │
    │  │  • Provides connection pooling                                                │ │
    │  │  • Routes to appropriate S3 service                                           │ │
    │  └────────────────────────────────┬────────────────────────────────────────────┘ │
    │                                    │                                               │
    │                                    ▼                                               │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                         S3Service (Infrastructure)                            │ │
    │  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  AWS S3 Operations:                                                     │ │ │
    │  │  │  • boto3 client management (_client, _resource)                        │ │ │
    │  │  │  • Direct S3 API calls                                                 │ │ │
    │  │  │  • Error handling (ClientError, NoCredentialsError)                    │ │ │
    │  │  │  • Region and bucket management                                        │ │ │
    │  │  └────────────────────────────────────────────────────────────────────────┘ │ │
    │  │                                                                              │ │
    │  │  ┌────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  Credential Sources (via credential_loader):                            │ │ │
    │  │  │  • settings.yaml configuration                                         │ │ │
    │  │  │  • Environment variables (AWS_ACCESS_KEY_ID, etc.)                     │ │ │
    │  │  │  • IAM role credentials                                                │ │ │
    │  │  │  • AWS CLI profile                                                     │ │ │
    │  │  └────────────────────────────────────────────────────────────────────────┘ │ │
    │  └──────────────────────────────────────────────────────────────────────────────┘ │
    └────────────────────────────────────────────────────────────────────────────────────┘
```

## External Infrastructure

```
    ┌────────────────────────────────────────────────────────────────────────────────────┐
    │                          EXTERNAL INFRASTRUCTURE                                   │
    │  ┌──────────────────────────────────────────────────────────────────────────────┐ │
    │  │                             AWS S3 Service                                    │ │
    │  │  • Buckets: tidyllm-knowledge, vectorqa-artifacts, mlflow-models             │ │
    │  │  • Regions: us-east-1 (primary), us-west-2 (backup)                         │ │
    │  │  • Storage classes: STANDARD, INTELLIGENT_TIERING                           │ │
    │  └──────────────────────────────────────────────────────────────────────────────┘ │
    └────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Domain Core

**S3Manager** - Knowledge systems storage manager:
- File versioning and deduplication
- Path generation strategies
- Metadata management
- Content hashing (MD5/SHA256)
- Knowledge base organization

**Domain Models**:
- `S3Config`: Configuration settings
- `UploadResult`: Operation results with metadata
- `S3Path`: Path abstraction for S3 keys

### Delegation Layer

**UnifiedSessionManager**:
- Central hub for all S3 operations
- Manages boto3 client lifecycle
- Connection pooling for efficiency
- Credential resolution from multiple sources

### Infrastructure Adapter

**S3Service**:
- Direct boto3 integration
- AWS S3 API operations
- Error handling (ClientError, NoCredentialsError)
- Region and bucket management

### Credential Management

**credential_loader**:
- Loads from `settings.yaml`
- Environment variable fallback
- IAM role support
- AWS CLI profile integration

## Dependency Flow

1. Domain scripts → S3Manager (never directly to S3Service)
2. S3Manager → UnifiedSessionManager (delegation pattern)
3. UnifiedSessionManager → S3Service (adapter)
4. S3Service → boto3 → AWS S3

## Key Patterns

### Delegation Pattern
S3Manager delegates all infrastructure operations to UnifiedSessionManager, maintaining clean separation between business logic and infrastructure.

### Abstraction
Domain uses S3Manager's business methods without knowing AWS specifics.

### Configuration
All configuration centralized in `settings.yaml`, loaded via credential_loader.

### Graceful Degradation
System works without boto3 installed (returns mock results for testing).

## Data Flow Example - File Upload

1. **Script calls**: `s3_manager.upload_file("data.json")`
2. **S3Manager**:
   - Generates S3 key using business rules
   - Calculates file hash for deduplication
   - Adds metadata (timestamp, version, tags)
3. **UnifiedSessionManager**:
   - Gets S3 client with proper credentials
   - Manages connection lifecycle
4. **S3Service**:
   - Executes `boto3.upload_file()`
   - Handles AWS-specific errors
5. **Response**: Returns `UploadResult` with operation details

## Business Rules

### Path Generation
```python
def build_s3_path(category, filename, timestamp=None):
    """Generate S3 path with versioning"""
    # Example: knowledge/2024/01/15/document_v1.pdf
    return f"{category}/{date}/{filename}"
```

### Versioning Strategy
- Automatic version numbering
- Timestamp-based organization
- Content hash for deduplication
- Metadata tags for searchability

### File Organization
```
bucket/
├── knowledge/
│   ├── documents/
│   ├── embeddings/
│   └── metadata/
├── artifacts/
│   ├── models/
│   └── datasets/
└── backups/
    └── daily/
```

## Testing Boundaries

- **Domain Tests**: Mock UnifiedSessionManager
- **Integration Tests**: Mock S3Service
- **E2E Tests**: Use LocalStack or test bucket

## Benefits

1. **Domain Independence**: S3Manager contains pure business logic
2. **Infrastructure Flexibility**: Can swap S3 for MinIO, GCS, or local storage
3. **Testability**: Test without AWS credentials
4. **Multi-environment**: Manage dev/staging/prod configurations
5. **Monitoring**: Log and monitor at adapter boundaries

## Configuration Example

```yaml
# settings.yaml
credentials:
  s3_primary:
    service: s3
    region: us-east-1
    bucket: tidyllm-knowledge
    access_key_id: ${AWS_ACCESS_KEY_ID}
    secret_access_key: ${AWS_SECRET_ACCESS_KEY}
```

## Implementation Files

- **Domain**: `packages/tidyllm/knowledge_systems/s3_manager.py`
- **Delegation**: `packages/tidyllm/infrastructure/UnifiedSessionManager.py`
- **Adapter**: `infrastructure/services/s3_service.py`
- **Config**: `infrastructure/settings.yaml`

## Error Handling

- **NoCredentialsError**: Falls back to environment variables
- **ClientError**: Retries with exponential backoff
- **BucketNotFound**: Creates bucket if permissions allow
- **NetworkError**: Uses cached responses when available