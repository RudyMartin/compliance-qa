# LLM Gateway Shim Integration Pattern

## Overview
The `LLMGatewayShim` provides a unified interface for different LLM providers, abstracting away API differences between Anthropic's direct API and AWS Bedrock.

## Usage Examples

### 1. Direct Anthropic API
```python
import anthropic
from llm_gateway_shim import LLMGatewayShim
from llm_types import Message

anthropic_client = anthropic.Anthropic(api_key="YOUR_KEY")
gw = LLMGatewayShim(provider="anthropic", client=anthropic_client)

resp = gw.chat(
    model="claude-3-5-sonnet-20240620",
    system="You are concise.",
    messages=[Message(role="user", content="Give me 3 bullet points on PCA.")],
    max_tokens=200,
)
print(resp.text)
```

### 2. AWS Bedrock
```python
import boto3
bedrock_rt = boto3.client("bedrock-runtime", region_name="us-east-1")
gw_bedrock = LLMGatewayShim(provider="bedrock", client=bedrock_rt)

# Simple prompt format (backwards compatible)
resp2 = gw_bedrock.chat(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    prompt="Explain K-fold cross-validation in 2 lines.",
    max_tokens=120,
)

# Or with messages format
resp3 = gw_bedrock.chat(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    messages=[Message(role="user", content="Explain PCA")],
    max_tokens=120,
)
```

## Integration with Existing System

### Current Architecture
```
User Request
    ↓
CorporateLLMGateway (always uses Messages API)
    ↓
AWS Bedrock
```

### Enhanced Architecture with Shim
```
User Request
    ↓
LLMGatewayShim (provider-aware routing)
    ├── provider="anthropic" → Direct Anthropic API
    └── provider="bedrock" → AWS Bedrock
```

## Key Benefits

1. **Provider Abstraction**: Single interface for multiple providers
2. **Format Flexibility**: Supports both `prompt` and `messages` parameters
3. **Backward Compatibility**: Works with legacy prompt-based code
4. **System Message Handling**: Properly separates system messages for Claude 3

## Implementation in CorporateLLMGateway

The existing `CorporateLLMGateway` can be enhanced to use the shim pattern:

```python
class CorporateLLMGateway:
    def __init__(self):
        # Determine provider based on configuration
        if self.use_direct_anthropic:
            client = anthropic.Anthropic(api_key=self.api_key)
            self.shim = LLMGatewayShim(provider="anthropic", client=client)
        else:
            client = boto3.client("bedrock-runtime", region_name=self.region)
            self.shim = LLMGatewayShim(provider="bedrock", client=client)

    def process_request(self, request: LLMRequest):
        # Use shim for actual API calls
        if request.system_message:
            return self.shim.chat(
                model=request.model_id,
                system=request.system_message,
                messages=request.messages,
                max_tokens=request.max_tokens
            )
        else:
            return self.shim.chat(
                model=request.model_id,
                prompt=request.prompt,
                max_tokens=request.max_tokens
            )
```

## Testing Strategy

Your test file shows the correct approach:
1. Mock the transport layer
2. Verify correct payload structure
3. Test both providers
4. Validate response parsing

## Migration Path

1. **Phase 1**: Add `LLMGatewayShim` alongside existing code
2. **Phase 2**: Update components to use shim interface
3. **Phase 3**: Remove direct API calls in favor of shim
4. **Phase 4**: Extend shim for additional providers (OpenAI, Cohere, etc.)

## Configuration

Settings.yaml can specify provider preference:
```yaml
llm_models:
  provider: "bedrock"  # or "anthropic"
  bedrock:
    region: us-east-1
    model_id: anthropic.claude-3-5-sonnet-20240620-v1:0
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    model_id: claude-3-5-sonnet-20240620
```

This pattern ensures consistent behavior across all components while maintaining flexibility for different deployment scenarios.