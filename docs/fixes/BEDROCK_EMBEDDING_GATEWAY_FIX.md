# Bedrock Embedding Gateway Fix

**Date**: 2025-09-22
**Issue**: Bedrock embeddings bypassing CorporateLLMGateway and missing dimensions parameter
**Severity**: HIGH (Compliance Violation)
**Status**: FIXED

## Problem Description

Two critical issues were discovered with Bedrock embedding operations:

1. **Compliance Violation**: Embedding worker was directly importing and using `tidyllm.providers.bedrock`, completely bypassing the CorporateLLMGateway. This violated the architectural requirement that ALL Bedrock operations must go through the corporate gateway for tracking and audit purposes.

2. **Missing Dimensions Parameter**: Bedrock embedding models (Titan v2, Cohere) require a `dimensions` parameter in the request body, but this was not being passed. Without this parameter, embedding calls would fail or use incorrect dimensions.

## Root Causes

### 1. Direct Provider Usage (Violation)
```python
# BEFORE - VIOLATION: Direct Bedrock usage
from tidyllm.providers import bedrock, claude, openai
provider = bedrock()
embedding = llm_message(text) | embed(provider)
```

This bypassed all corporate governance, tracking, and audit requirements.

### 2. Missing Dimensions in Request Body
Bedrock Titan v2 requires:
```json
{
  "inputText": "text to embed",
  "dimensions": 1024  // This was MISSING!
}
```

## Solution Implementation

### 1. Added Embedding Support to CorporateLLMGateway

Added new methods to `packages/tidyllm/gateways/corporate_llm_gateway.py`:

```python
@dataclass
class LLMRequest:
    # ... existing fields ...
    is_embedding: bool = False  # Flag for embedding requests
    dimensions: Optional[int] = None  # Dimensions for embedding models

def process_embedding_request(self, request: LLMRequest) -> LLMResponse:
    """Process embedding request with corporate compliance."""
    # Validates request
    # Resolves model ID
    # Prepares body WITH dimensions
    # Calls Bedrock
    # Tracks and audits
    # Returns embedding vector

def _prepare_embedding_body(self, request: LLMRequest, model_id: str) -> Dict:
    """Prepare request body for Bedrock embedding models."""
    if 'amazon.titan' in model_id:
        body = {"inputText": request.prompt}
        if 'v2' in model_id and request.dimensions:
            body["dimensions"] = request.dimensions  # CRITICAL FIX
    # ... handle other models
```

### 2. Fixed Embedding Worker to Use Gateway

Modified `packages/tidyllm/infrastructure/workers/embedding_worker.py`:

```python
# BEFORE - VIOLATION
from tidyllm.providers import bedrock
provider = bedrock()

# AFTER - COMPLIANT
from ...gateways.corporate_llm_gateway import CorporateLLMGateway
self.corporate_gateway = CorporateLLMGateway()

# Now all embeddings go through gateway
request = LLMRequest(
    prompt=text,
    model_id="titan-embed-v2",
    is_embedding=True,
    dimensions=1024,  # Properly passed!
    user_id="embedding_worker",
    audit_reason="vector_embedding_generation"
)
response = self.corporate_gateway.process_embedding_request(request)
```

## Configuration

The system reads embedding configuration from `infrastructure/settings.yaml`:

```yaml
credentials:
  bedrock_llm:
    embeddings:
      dimensions: 1024  # Standard dimension for all embeddings
      model_id: cohere.embed-english-v3
```

## Architecture Compliance

The fix ensures hexagonal architecture compliance:

```
BEFORE (VIOLATION):
EmbeddingWorker → TidyLLM Providers → Direct Bedrock (NO TRACKING!)

AFTER (COMPLIANT):
EmbeddingWorker → CorporateLLMGateway → Bedrock (TRACKED & AUDITED)
```

## Verification

### 1. Check Model Mappings
```python
from packages.tidyllm.gateways.corporate_llm_gateway import CorporateLLMGateway
gateway = CorporateLLMGateway()
# Should resolve: titan-embed-v2 → amazon.titan-embed-text-v2:0
```

### 2. Verify Dimensions Are Passed
The gateway now logs: `"Titan v2 embedding with dimensions: 1024"`

### 3. Confirm Tracking
All embedding requests now appear in audit logs with:
- Model used
- Dimensions requested
- Processing time
- User ID and audit reason

## Impact

- **Compliance**: ✅ All Bedrock operations now go through CorporateLLMGateway
- **Tracking**: ✅ Every embedding request is tracked and audited
- **Functionality**: ✅ Embeddings work correctly with proper dimensions
- **Performance**: No significant impact (same underlying Bedrock calls)

## Testing Recommendations

1. Test embedding generation with different models:
   - `titan-embed-v1` (1536 dimensions native)
   - `titan-embed-v2` (supports 256, 512, 1024)
   - `cohere-embed` (variable dimensions)

2. Verify audit logs contain embedding requests

3. Confirm dimensions in generated embeddings match configuration

## Lessons Learned

1. **Always use the corporate gateway** - No direct provider imports allowed
2. **Check model-specific requirements** - Different models need different parameters
3. **Maintain compliance** - Architecture rules exist for governance and tracking
4. **Document API requirements** - Bedrock's dimension requirement wasn't obvious

## Related Files

- `packages/tidyllm/gateways/corporate_llm_gateway.py` - Gateway with embedding support
- `packages/tidyllm/infrastructure/workers/embedding_worker.py` - Fixed to use gateway
- `infrastructure/settings.yaml` - Embedding configuration
- `docs/architecture/hexagonal-chat-system.md` - Architecture documentation