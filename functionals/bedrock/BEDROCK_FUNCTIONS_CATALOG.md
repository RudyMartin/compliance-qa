# Bedrock Functions Catalog

## Core Bedrock Service Functions (infrastructure/services/bedrock_service.py)

### 1. BedrockService Class

#### Constructor
```python
def __init__(self, config: Optional[Dict] = None)
```
- **Purpose**: Initialize Bedrock service with configuration
- **Parameters**:
  - `config` (Optional[Dict]): Configuration dictionary
- **Config Keys**:
  - `region` (str): AWS region (default: 'us-east-1' or AWS_REGION env)
  - `default_model` (str): Default model ID (default: BedrockModel.CLAUDE_3_HAIKU.value)
  - `access_key_id` (str): AWS access key (optional, uses env if not provided)
  - `secret_access_key` (str): AWS secret key (optional, uses env if not provided)

#### is_available()
```python
def is_available(self) -> bool
```
- **Purpose**: Check if Bedrock service is available
- **Returns**: bool - True if boto3 and clients are initialized

#### list_foundation_models()
```python
def list_foundation_models(self) -> List[Dict]
```
- **Purpose**: List available foundation models
- **Returns**: List[Dict] - List of model information dictionaries
- **Response Structure**: Each dict contains model metadata from AWS Bedrock

#### invoke_model()
```python
def invoke_model(self,
                prompt: str,
                model_id: Optional[str] = None,
                max_tokens: int = 1000,
                temperature: float = 0.7,
                **kwargs) -> Optional[str]
```
- **Purpose**: Invoke a Bedrock model for text generation
- **Parameters**:
  - `prompt` (str): Input prompt text
  - `model_id` (Optional[str]): Model ID to use (defaults to configured model)
  - `max_tokens` (int): Maximum tokens to generate (default: 1000)
  - `temperature` (float): Temperature for generation (default: 0.7)
  - `**kwargs`: Additional model-specific parameters
- **Returns**: Optional[str] - Generated text or None if failed
- **Supported Models**: Claude, Titan, Llama, Mistral/Mixtral

#### invoke_claude()
```python
def invoke_claude(self, prompt: str, **kwargs) -> Optional[str]
```
- **Purpose**: Convenience method to invoke Claude model
- **Parameters**:
  - `prompt` (str): Input prompt
  - `**kwargs`: Additional parameters (model, max_tokens, temperature)
- **Returns**: Optional[str] - Generated text or None

#### invoke_titan()
```python
def invoke_titan(self, prompt: str, **kwargs) -> Optional[str]
```
- **Purpose**: Convenience method to invoke Titan model
- **Parameters**:
  - `prompt` (str): Input prompt
  - `**kwargs`: Additional parameters
- **Returns**: Optional[str] - Generated text or None

#### create_embedding()
```python
def create_embedding(self, text: str, model_id: Optional[str] = None) -> Optional[List[float]]
```
- **Purpose**: Create text embedding using Titan Embed model
- **Parameters**:
  - `text` (str): Text to embed
  - `model_id` (Optional[str]): Embedding model ID (defaults to Titan Embed)
- **Returns**: Optional[List[float]] - Embedding vector or None

#### get_model_info()
```python
def get_model_info(self, model_id: str) -> Optional[Dict]
```
- **Purpose**: Get detailed information about a specific model
- **Parameters**:
  - `model_id` (str): Model identifier
- **Returns**: Optional[Dict] - Model information dictionary or None

### 2. Module Functions

#### get_bedrock_service()
```python
def get_bedrock_service(config: Optional[Dict] = None) -> BedrockService
```
- **Purpose**: Get the singleton Bedrock service instance
- **Parameters**:
  - `config` (Optional[Dict]): Optional configuration dictionary
- **Returns**: BedrockService instance

#### inject_bedrock_config()
```python
def inject_bedrock_config(config: Dict)
```
- **Purpose**: Inject Bedrock configuration for child packages
- **Parameters**:
  - `config` (Dict): Configuration dictionary
- **Returns**: BedrockService instance

### 3. BedrockModel Enum
```python
class BedrockModel(Enum):
    # Claude models
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_2_1 = "anthropic.claude-v2:1"
    CLAUDE_2 = "anthropic.claude-v2"
    CLAUDE_INSTANT = "anthropic.claude-instant-v1"

    # Titan models
    TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_EMBED_TEXT = "amazon.titan-embed-text-v1"
    TITAN_EMBED_IMAGE = "amazon.titan-embed-image-v1"

    # Llama models
    LLAMA2_13B_CHAT = "meta.llama2-13b-chat-v1"
    LLAMA2_70B_CHAT = "meta.llama2-70b-chat-v1"

    # Mistral models
    MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
    MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"
```

## Bedrock Delegate Functions (packages/tidyllm/infrastructure/bedrock_delegate.py)

### BedrockDelegate Class
This class delegates all operations to the parent infrastructure's BedrockService.

#### Methods
- `__init__(config: Optional[Dict] = None)`
- `is_available() -> bool`
- `list_foundation_models() -> List[Dict]`
- `invoke_model(prompt: str, model_id: Optional[str] = None, **kwargs) -> Optional[str]`
- `invoke_claude(prompt: str, **kwargs) -> Optional[str]`
- `invoke_titan(prompt: str, **kwargs) -> Optional[str]`
- `create_embedding(text: str, model_id: Optional[str] = None) -> Optional[List[float]]`
- `get_model_info(model_id: str) -> Optional[Dict]`
- `get_bedrock_client()` - Compatibility method
- `get_bedrock_runtime_client()` - Compatibility method

#### Module Function
```python
def get_bedrock_delegate(config: Optional[Dict] = None) -> BedrockDelegate
```

## AWS Service Bedrock Functions (infrastructure/services/aws_service.py)

### AWSService Class Bedrock Methods

#### get_bedrock_client()
```python
def get_bedrock_client(self)
```
- **Purpose**: Get or create Bedrock client (lazy initialization)
- **Returns**: boto3 Bedrock client or None

#### get_bedrock_runtime_client()
```python
def get_bedrock_runtime_client(self)
```
- **Purpose**: Get or create Bedrock Runtime client (lazy initialization)
- **Returns**: boto3 Bedrock Runtime client or None

#### invoke_model()
```python
def invoke_model(self, prompt: str, model_id: Optional[str] = None, **kwargs) -> Optional[str]
```
- **Purpose**: Invoke a Bedrock model
- **Returns**: Generated text or None

#### create_embedding()
```python
def create_embedding(self, text: str, model_id: Optional[str] = None) -> Optional[List[float]]
```
- **Purpose**: Create text embedding using Titan Embed model
- **Returns**: Embedding vector or None

## Unified Session Manager Bedrock Functions (adapters/session/unified_session_manager.py)

### UnifiedSessionManager Class

#### _init_bedrock()
```python
def _init_bedrock(self)
```
- **Purpose**: Initialize Bedrock connection
- **Creates**: _bedrock_client and _bedrock_runtime_client

#### get_bedrock_client()
```python
def get_bedrock_client(self)
```
- **Purpose**: Get Bedrock client (thread-safe) - lazy initialization
- **Returns**: boto3 Bedrock client

#### get_bedrock_runtime_client()
```python
def get_bedrock_runtime_client(self)
```
- **Purpose**: Get Bedrock Runtime client (thread-safe) - lazy initialization
- **Returns**: boto3 Bedrock Runtime client

#### _test_bedrock_connection()
```python
def _test_bedrock_connection(self) -> Dict[str, Any]
```
- **Purpose**: Test Bedrock connection with timing and details
- **Returns**: Dict with status, latency, models_count, error

### Module Function
```python
def get_bedrock_client()
```
- **Purpose**: Get Bedrock client from global session manager
- **Returns**: Bedrock client

## Corporate LLM Gateway Functions (packages/tidyllm/gateways/corporate_llm_gateway.py)

### CorporateLLMGateway Class

#### process_request()
```python
def process_request(self, request: LLMRequest) -> LLMResponse
```
- **Purpose**: Process LLM request with corporate compliance
- **Parameters**:
  - `request` (LLMRequest): Contains prompt, model_id, temperature, max_tokens, etc.
- **Returns**: LLMResponse with content, success status, token usage, etc.

### Data Classes
```python
@dataclass
class LLMRequest:
    prompt: str
    model_id: str = "claude-3-sonnet"
    temperature: float = 0.7
    max_tokens: int = 4000
    user_id: Optional[str] = None
    audit_reason: Optional[str] = None

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

## Configuration Functions

### YAMLSettingsLoader (infrastructure/yaml_loader.py)
```python
def get_bedrock_config(self) -> Dict[str, Any]
```
- **Purpose**: Get Bedrock configuration from settings
- **Returns**: Dict with bedrock configuration from YAML

### DynamicCredentialCarrier (infrastructure/services/dynamic_credential_carrier.py)
```python
def get_bedrock_configuration(self) -> Dict[str, Any]
```
- **Purpose**: Get Bedrock LLM configuration
- **Returns**: Dict with bedrock configuration

## Important Notes

1. **Real vs Mock Implementations**:
   - The main BedrockService (infrastructure/services/bedrock_service.py) is REAL - it uses boto3
   - BedrockDelegate has fallback mocks when parent infrastructure isn't available
   - All functions check BOTO3_AVAILABLE before attempting real operations

2. **Authentication**:
   - Uses AWS credentials from environment variables or configuration
   - Supports IAM roles, access keys, and session tokens

3. **Error Handling**:
   - All functions return None or empty lists on failure
   - Errors are logged but not raised to maintain stability

4. **Thread Safety**:
   - UnifiedSessionManager uses lazy initialization with thread safety
   - Singleton patterns used for service instances

5. **Model Support**:
   - Claude (3 Haiku, Sonnet, Opus, 2.1, 2, Instant)
   - Titan (Text Lite, Express, Embed Text/Image)
   - Llama2 (13B, 70B)
   - Mistral (7B, Mixtral 8x7B)