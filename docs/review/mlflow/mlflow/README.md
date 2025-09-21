# MLflow Session Tracking & Activity Monitoring

Comprehensive MLflow integration in TidyLLM for enterprise-grade session tracking, user parameter logging, and activity monitoring.

## Overview

TidyLLM provides complete MLflow integration for tracking:
- **User Session Parameters** (user_id, session_id, audit_reason)
- **Request Metadata** (model, temperature, tokens, timing)
- **Cost Tracking** (input/output/total tokens)
- **Performance Metrics** (processing time, success rates)
- **Audit Trails** (compliance and monitoring)

## Quick Start

### Basic Chat with Session Tracking
```python
import tidyllm

# Chat with full session tracking
response = tidyllm.chat(
    "Your question here",
    chat_type='direct',
    reasoning=True,
    user_id='your_user_123',
    audit_reason='business_query'
)

# Session parameters are automatically logged to MLflow
```

### All Chat Modes Support Session Tracking
```python
# Direct mode (fastest)
tidyllm.chat("Question", chat_type='direct', user_id='user123')

# DSPy mode (reasoning)
tidyllm.chat("Think step by step", chat_type='dspy', user_id='user123')

# RAG mode (knowledge-based)
tidyllm.chat("What's in our docs?", chat_type='rag', user_id='user123')

# Hybrid mode (intelligent routing)
tidyllm.chat("Anything", chat_type='hybrid', user_id='user123')
```

## Session Parameters Captured

### User Context
- **`user_id`** - Unique user identifier for tracking
- **`session_id`** - Session ID for conversation tracking (optional)
- **`audit_reason`** - Business reason for the request

### Request Parameters
- **`model_id`** - LLM model used (e.g., "claude-3-sonnet")
- **`temperature`** - Model temperature setting
- **`max_tokens`** - Maximum token limit
- **`processing_time_ms`** - Request processing time

### Token Metrics
- **`input_tokens`** - Input token count for cost tracking
- **`output_tokens`** - Output token count for cost tracking
- **`total_tokens`** - Total tokens used

### Audit Trail
- **`timestamp`** - Precise request timestamp
- **`success`** - Whether the request succeeded
- **`error`** - Error message if request failed

## MLflow Service Integration

### Check Service Status
```python
from tidyllm.services import MLflowIntegrationService

mlflow_service = MLflowIntegrationService()
print(f"Available: {mlflow_service.is_available()}")
print(f"Connected: {mlflow_service.is_connected}")
```

### Manual Logging (Advanced)
```python
# Log custom request data
result = mlflow_service.log_llm_request(
    model='custom-model',
    prompt='test prompt',
    response='test response',
    processing_time=150.0,
    token_usage={'input': 10, 'output': 20, 'total': 30},
    success=True,
    user_id='custom_user',
    session_id='custom_session',
    audit_reason='manual_test'
)
```

## Activity Monitoring

### View Recent Activity
```python
from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records

# Shows last 5 MLflow records with full session details
show_last_5_mlflow_records()
```

### Check for Missing Evidence
```python
from tidyllm.infrastructure.tools.mlflow_evidence_checker import show_missing_evidence

# Shows missing MLflow evidence for compliance
show_missing_evidence()
```

### Command Line Usage
```bash
# View recent MLflow activity
cd tidyllm
python infrastructure/tools/mlflow_viewer.py

# Check evidence gaps
python infrastructure/tools/mlflow_evidence_checker.py
```

## Example Session Tracking Output

### Successful Chat Response
```python
response = tidyllm.chat(
    "Explain machine learning",
    chat_type='direct',
    reasoning=True,
    user_id='demo_user_123',
    audit_reason='learning_session'
)

# Response includes audit trail:
{
    'content': 'Machine learning is...',
    'audit_trail': {
        'timestamp': '2025-09-17T12:48:58.833628',
        'user_id': 'demo_user_123',
        'audit_reason': 'learning_session',
        'model_id': 'claude-3-sonnet',
        'temperature': 0.7,
        'max_tokens': 4000,
        'processing_time_ms': 3292.046,
        'success': True,
        'error': None
    },
    'token_usage': {
        'input': 10,
        'output': 65,
        'total': 75
    }
}
```

### MLflow Record Example
```
=== MLflow Record ===
RUN IDENTIFICATION:
  User ID: demo_user_123
  Audit Reason: learning_session
  Model: claude-3-sonnet
  Timestamp: 2025-09-17T12:48:58

PARAMETERS:
  model: claude-3-sonnet
  temperature: 0.7
  user_id: demo_user_123
  audit_reason: learning_session

METRICS:
  input_tokens: 10
  output_tokens: 65
  total_tokens: 75
  processing_time_ms: 3292.046
  success: 1.0
```

## Testing & Validation

### Automated Tests
Located in `/tests/mlflow/`:

```bash
# Run session tracking tests
cd tidyllm/tests/mlflow
python test_session_tracking.py

# Run activity viewer tests
python test_activity_viewer.py
```

### Manual Verification
```python
# Test complete pipeline
import tidyllm
from tidyllm.services import MLflowIntegrationService

# 1. Verify MLflow service
mlflow_service = MLflowIntegrationService()
assert mlflow_service.is_available(), "MLflow service not available"

# 2. Generate tracked activity
response = tidyllm.chat(
    "Test session tracking",
    chat_type='direct',
    reasoning=True,
    user_id='verification_user',
    audit_reason='manual_verification'
)

# 3. Verify tracking data
assert 'audit_trail' in response, "Audit trail missing"
assert 'token_usage' in response, "Token usage missing"
assert response['audit_trail']['user_id'] == 'verification_user'

# 4. Check MLflow records
from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records
show_last_5_mlflow_records()  # Should show your test above
```

## Enterprise Features

### Cost Tracking
- **Token-based billing** - Track input/output tokens per user
- **Model usage analytics** - Monitor which models users prefer
- **Processing time metrics** - Identify performance bottlenecks

### Compliance & Auditing
- **Complete audit trails** - Every request logged with context
- **User activity tracking** - Know who did what when
- **Error monitoring** - Track and analyze failures

### Performance Monitoring
- **Response time tracking** - Monitor system performance
- **Success rate analytics** - Track reliability metrics
- **Load analysis** - Understand usage patterns

## Architecture

### Data Flow
```
User Request → Chat Manager → MLflow Integration Service → PostgreSQL Backend
     ↓              ↓                     ↓                      ↓
Session Params → Audit Trail → MLflow Logging → AWS RDS Storage
```

### Integration Points
- **Chat Manager** - Captures user context and parameters
- **MLflow Service** - Handles logging and formatting
- **PostgreSQL Backend** - Stores all tracking data on AWS RDS
- **Viewer Tools** - Query and display activity data

## Configuration

### MLflow Backend
- **Database**: PostgreSQL on AWS RDS
- **Host**: vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com
- **Database**: vectorqa
- **Connection**: Managed through unified sessions

### Required Services
- ✅ **MLflowIntegrationService** - Core logging service
- ✅ **CentralizedDocumentService** - Document processing support
- ✅ **UnifiedChatManager** - Chat orchestration with tracking

## Troubleshooting

### Common Issues

**No Session Data in MLflow**
```python
# Check if service is working
from tidyllm.services import MLflowIntegrationService
service = MLflowIntegrationService()
print(f"Available: {service.is_available()}")
print(f"Connected: {service.is_connected}")
```

**Missing User Parameters**
```python
# Ensure user_id is passed to chat
response = tidyllm.chat(
    "Your question",
    user_id="required_user_id",  # ← Must include this
    audit_reason="business_purpose"
)
```

**MLflow Connection Issues**
- Check PostgreSQL credentials in settings.yaml
- Verify AWS RDS connectivity
- Ensure unified session manager is configured

### Warning Messages

**"Centralized document service not available"**
- This warning is harmless during import
- Service exists and works properly
- Warning appears due to import order during system initialization

## Advanced Usage

### Custom Session Context
```python
import uuid

# Generate unique session for conversation
session_id = str(uuid.uuid4())

# Multi-turn conversation with session tracking
for i, question in enumerate(questions):
    response = tidyllm.chat(
        question,
        chat_type='hybrid',
        user_id='advanced_user',
        session_id=session_id,
        audit_reason=f'conversation_turn_{i+1}'
    )
```

### Batch Request Tracking
```python
import time

users = ['user_1', 'user_2', 'user_3']
questions = ['Q1', 'Q2', 'Q3']

for user_id in users:
    for i, question in enumerate(questions):
        response = tidyllm.chat(
            question,
            chat_type='direct',
            user_id=user_id,
            audit_reason=f'batch_processing_{i+1}'
        )
        time.sleep(1)  # Rate limiting

# View all activity
from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records
show_last_5_mlflow_records()
```

## Summary

TidyLLM's MLflow integration provides enterprise-grade session tracking with:

- ✅ **Complete user session parameter capture**
- ✅ **Automatic token usage and cost tracking**
- ✅ **Comprehensive audit trails for compliance**
- ✅ **Real-time activity monitoring and viewing**
- ✅ **Performance metrics and error tracking**
- ✅ **PostgreSQL backend for reliable storage**

All chat modes (`direct`, `dspy`, `rag`, `hybrid`) support full session tracking out of the box.