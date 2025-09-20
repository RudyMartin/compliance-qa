"""
Bedrock Service - Parent Infrastructure
========================================
Provides AWS Bedrock functionality for all child packages.
TidyLLM and other packages borrow this instead of importing boto3 for Bedrock.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

# Conditional boto3 import - only if available
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    ClientError = Exception
    NoCredentialsError = Exception


class BedrockModel(Enum):
    """Available Bedrock models."""
    # Anthropic Claude models
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_2_1 = "anthropic.claude-v2:1"
    CLAUDE_2 = "anthropic.claude-v2"
    CLAUDE_INSTANT = "anthropic.claude-instant-v1"

    # Amazon Titan models
    TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_EMBED_TEXT = "amazon.titan-embed-text-v1"
    TITAN_EMBED_IMAGE = "amazon.titan-embed-image-v1"

    # Meta Llama models
    LLAMA2_13B_CHAT = "meta.llama2-13b-chat-v1"
    LLAMA2_70B_CHAT = "meta.llama2-70b-chat-v1"

    # Mistral models
    MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
    MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"


class BedrockService:
    """
    Centralized Bedrock service for the infrastructure.
    Manages both bedrock and bedrock-runtime clients.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize Bedrock service with configuration."""
        self.config = config or {}
        self._bedrock_client = None
        self._bedrock_runtime_client = None

        # Get configuration from environment or config
        self.region = self.config.get('region', os.getenv('AWS_REGION', 'us-east-1'))
        self.default_model = self.config.get('default_model', BedrockModel.CLAUDE_3_HAIKU.value)

        if BOTO3_AVAILABLE:
            self._initialize_bedrock()

    def _initialize_bedrock(self):
        """Initialize Bedrock clients if boto3 is available."""
        try:
            # Use environment credentials or config
            if 'access_key_id' in self.config:
                session = boto3.Session(
                    aws_access_key_id=self.config['access_key_id'],
                    aws_secret_access_key=self.config['secret_access_key'],
                    region_name=self.region
                )
            else:
                # Use default credentials (IAM role, env vars, etc.)
                session = boto3.Session(region_name=self.region)

            # Create both client types
            self._bedrock_client = session.client('bedrock', region_name=self.region)
            self._bedrock_runtime_client = session.client('bedrock-runtime', region_name=self.region)

            logger.info(f"Bedrock service initialized for region: {self.region}")
        except Exception as e:
            logger.warning(f"Could not initialize Bedrock: {e}")
            self._bedrock_client = None
            self._bedrock_runtime_client = None

    def is_available(self) -> bool:
        """Check if Bedrock service is available."""
        return BOTO3_AVAILABLE and self._bedrock_runtime_client is not None

    def list_foundation_models(self) -> List[Dict]:
        """
        List available foundation models.

        Returns:
            List of model information dictionaries
        """
        if not self.is_available():
            logger.warning("Bedrock service not available")
            return []

        try:
            response = self._bedrock_client.list_foundation_models()
            return response.get('modelSummaries', [])
        except Exception as e:
            logger.error(f"Failed to list foundation models: {e}")
            return []

    def invoke_model(self,
                    prompt: str,
                    model_id: Optional[str] = None,
                    max_tokens: int = 1000,
                    temperature: float = 0.7,
                    **kwargs) -> Optional[str]:
        """
        Invoke a Bedrock model for text generation.

        Args:
            prompt: Input prompt text
            model_id: Model ID to use (defaults to configured model)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional model-specific parameters

        Returns:
            Generated text or None if failed
        """
        if not self.is_available():
            logger.warning("Bedrock service not available")
            return None

        model_id = model_id or self.default_model

        try:
            # Format request based on model type
            if 'claude' in model_id.lower():
                request_body = self._format_claude_request(prompt, max_tokens, temperature, **kwargs)
            elif 'titan' in model_id.lower():
                request_body = self._format_titan_request(prompt, max_tokens, temperature, **kwargs)
            elif 'llama' in model_id.lower():
                request_body = self._format_llama_request(prompt, max_tokens, temperature, **kwargs)
            elif 'mistral' in model_id.lower() or 'mixtral' in model_id.lower():
                request_body = self._format_mistral_request(prompt, max_tokens, temperature, **kwargs)
            else:
                # Generic format
                request_body = {
                    "prompt": prompt,
                    "max_tokens_to_sample": max_tokens,
                    "temperature": temperature
                }

            # Invoke the model
            response = self._bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            return self._extract_text_from_response(response_body, model_id)

        except Exception as e:
            logger.error(f"Failed to invoke model {model_id}: {e}")
            return None

    def _format_claude_request(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> Dict:
        """Format request for Claude models."""
        # Claude 3 format
        if kwargs.get('use_messages_api', True):
            return {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "anthropic_version": "bedrock-2023-05-31"
            }
        # Claude 2 format
        return {
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }

    def _format_titan_request(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> Dict:
        """Format request for Titan models."""
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": kwargs.get('top_p', 0.9)
            }
        }

    def _format_llama_request(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> Dict:
        """Format request for Llama models."""
        return {
            "prompt": prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get('top_p', 0.9)
        }

    def _format_mistral_request(self, prompt: str, max_tokens: int, temperature: float, **kwargs) -> Dict:
        """Format request for Mistral/Mixtral models."""
        return {
            "prompt": f"<s>[INST] {prompt} [/INST]",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": kwargs.get('top_p', 0.9),
            "top_k": kwargs.get('top_k', 50)
        }

    def _extract_text_from_response(self, response_body: Dict, model_id: str) -> str:
        """Extract generated text from model response."""
        if 'claude' in model_id.lower():
            # Claude 3 format
            if 'content' in response_body:
                return response_body['content'][0]['text']
            # Claude 2 format
            return response_body.get('completion', '')
        elif 'titan' in model_id.lower():
            return response_body.get('results', [{}])[0].get('outputText', '')
        elif 'llama' in model_id.lower():
            return response_body.get('generation', '')
        elif 'mistral' in model_id.lower() or 'mixtral' in model_id.lower():
            return response_body.get('outputs', [{}])[0].get('text', '')
        else:
            # Try common fields
            return (response_body.get('completion', '') or
                   response_body.get('text', '') or
                   response_body.get('output', ''))

    def invoke_claude(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Convenience method to invoke Claude model.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Generated text or None
        """
        model = kwargs.pop('model', BedrockModel.CLAUDE_3_HAIKU.value)
        return self.invoke_model(prompt, model_id=model, **kwargs)

    def invoke_titan(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Convenience method to invoke Titan model.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters

        Returns:
            Generated text or None
        """
        model = kwargs.pop('model', BedrockModel.TITAN_TEXT_EXPRESS.value)
        return self.invoke_model(prompt, model_id=model, **kwargs)

    def create_embedding(self, text: str, model_id: Optional[str] = None) -> Optional[List[float]]:
        """
        Create text embedding using Titan Embed model.

        Args:
            text: Text to embed
            model_id: Embedding model ID (defaults to Titan Embed)

        Returns:
            Embedding vector or None
        """
        if not self.is_available():
            logger.warning("Bedrock service not available")
            return None

        model_id = model_id or BedrockModel.TITAN_EMBED_TEXT.value

        try:
            request_body = {"inputText": text}

            response = self._bedrock_runtime_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', None)

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None

    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model.

        Args:
            model_id: Model identifier

        Returns:
            Model information dictionary or None
        """
        if not self.is_available():
            logger.warning("Bedrock service not available")
            return None

        try:
            response = self._bedrock_client.get_foundation_model(
                modelIdentifier=model_id
            )
            return response.get('modelDetails', None)
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None


# Singleton instance
_bedrock_service = None

def get_bedrock_service(config: Optional[Dict] = None) -> BedrockService:
    """
    Get the singleton Bedrock service instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        BedrockService instance
    """
    global _bedrock_service
    if _bedrock_service is None:
        _bedrock_service = BedrockService(config)
    return _bedrock_service

def inject_bedrock_config(config: Dict):
    """
    Inject Bedrock configuration for child packages.

    This is called by child packages like TidyLLM to set up Bedrock.
    """
    global _bedrock_service
    _bedrock_service = BedrockService(config)
    return _bedrock_service