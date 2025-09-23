# CorporateLLMGateway Integration Architecture

## Overview
The CorporateLLMGateway provides enterprise governance features for all LLM calls in the system. It sits between the domain layer and infrastructure, adding cost tracking, audit trails, and MLflow integration.

## Current Architecture Flow

### Intended Flow (Enterprise Governance)
```
UI (Streamlit Apps)
    ↓
Domain Layer (UnifiedChatManager)
    ↓
CorporateLLMGateway (Governance Layer)
    - Cost tracking ($1000/day budget)
    - Audit trails for compliance
    - MLflow integration for tracking
    - Model ID resolution
    - User tracking
    ↓
Infrastructure (AWS Bedrock)
```

### Current Implementation Status

1. **UnifiedChatManager** (✅ FIXED)
   - Location: `packages/tidyllm/services/unified_chat_manager.py`
   - Status: Now uses CorporateLLMGateway in `_process_direct_chat()`
   - Creates LLMRequest and processes through gateway
   - Returns `gateway_tracked: True` in response

2. **InfrastructureDelegate** (✅ FIXED)
   - Location: `packages/tidyllm/infrastructure/infra_delegate.py`
   - Status: `invoke_bedrock()` now uses CorporateLLMGateway
   - Falls back with error "NO DIRECT AWS CALLS ALLOWED" if gateway unavailable
   - Returns `gateway_tracked` flag in responses

3. **CorporateLLMGateway Features**
   - Location: `packages/tidyllm/gateways/corporate_llm_gateway.py`
   - Cost tracking via CostTracker class
   - Budget limits enforcement
   - MLflow integration for experiment tracking
   - Audit trail generation
   - Model ID mapping from friendly names

## Key Components

### LLMRequest Object
```python
@dataclass
class LLMRequest:
    prompt: str
    model_id: str = "claude-3-sonnet"
    temperature: float = 0.7
    max_tokens: int = 4000
    user_id: Optional[str] = None
    audit_reason: Optional[str] = None
```

### LLMResponse Object
```python
@dataclass
class LLMResponse:
    content: str
    success: bool
    model_used: str
    processing_time_ms: float
    token_usage: Dict[str, int]
    error: Optional[str] = None
    audit_trail: Optional[Dict] = None
```

## MLflow Integration

The gateway integrates with MLflow to track:
- All LLM requests and responses
- Token usage and costs
- Model performance metrics
- Processing times
- Error rates

Configuration from `settings.yaml`:
```yaml
mlflow:
  tracking_uri: http://localhost:5000
  backend_store_uri: postgresql://mlflow_user:pass@host:5432/mlflow_db
  artifact_store: s3://nsc-mvp1/onboarding-test/mlflow/
```

## Cost Tracking

The CostTracker component:
- Enforces daily budget of $1000
- Tracks costs per model and user
- Provides real-time usage reports
- Prevents overspending

## Audit Trail

Every LLM call generates an audit entry with:
- Timestamp
- User ID
- Model used
- Token count
- Cost
- Processing time
- Request/response content (configurable)

## Benefits of Using CorporateLLMGateway

1. **Cost Control**: Prevents unexpected AWS charges
2. **Compliance**: Full audit trail for regulatory requirements
3. **Analytics**: MLflow tracking for model performance analysis
4. **Debugging**: Detailed logging of all LLM interactions
5. **User Tracking**: Per-user usage analytics
6. **Budget Management**: Automatic cutoff at budget limits

## Architecture Principles

1. **No Direct AWS Access**: Domain services must NEVER import boto3 or call AWS directly
2. **Gateway Pattern**: All LLM calls must go through CorporateLLMGateway
3. **Tracking Flag**: All responses include `gateway_tracked` flag
4. **Fallback Behavior**: If gateway unavailable, fail safely (no direct calls)
5. **Hexagonal Compliance**: Gateway acts as port/adapter for infrastructure

## Testing Gateway Integration

To verify gateway is working:

1. Check for `gateway_tracked: true` in responses
2. Monitor MLflow UI at http://localhost:5000 for tracked experiments
3. Review audit logs for all LLM calls
4. Verify cost tracking in gateway logs

## Common Issues and Solutions

### Issue: "NO DIRECT AWS CALLS ALLOWED"
**Solution**: Ensure CorporateLLMGateway is properly initialized in infra_delegate

### Issue: MLflow not tracking calls
**Solution**: Check MLflow service is running and configured in settings.yaml

### Issue: Model ID not recognized
**Solution**: Add model mapping to settings.yaml under `bedrock.model_mapping`

## Summary

The CorporateLLMGateway ensures enterprise-grade governance for all LLM operations. By routing all calls through this gateway, the system maintains:
- Complete audit trails
- Cost control
- Performance tracking
- Compliance requirements

All domain services should use either:
1. `UnifiedChatManager` which uses the gateway internally
2. `InfrastructureDelegate.invoke_bedrock()` which routes through the gateway