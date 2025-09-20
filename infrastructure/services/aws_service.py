"""
Unified AWS Service - Parent Infrastructure
===========================================
Single service for ALL AWS operations (S3, Bedrock, STS, etc.)
This is the ONLY place where boto3 is imported in the infrastructure.
"""

import os
import json
import logging
import tempfile
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
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

    # Meta Llama models
    LLAMA2_13B_CHAT = "meta.llama2-13b-chat-v1"
    LLAMA2_70B_CHAT = "meta.llama2-70b-chat-v1"

    # Mistral models
    MISTRAL_7B = "mistral.mistral-7b-instruct-v0:2"
    MIXTRAL_8X7B = "mistral.mixtral-8x7b-instruct-v0:1"


class AWSService:
    """
    Unified AWS service for the entire infrastructure.
    Manages S3, Bedrock, STS, and any other AWS services.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize AWS service with configuration."""
        self.config = config or {}

        # AWS clients (lazy initialized)
        self._s3_client = None
        self._s3_resource = None
        self._bedrock_client = None
        self._bedrock_runtime_client = None
        self._sts_client = None

        # Configuration
        self.region = self.config.get('region', os.getenv('AWS_REGION', 'us-east-1'))
        self.s3_bucket = self.config.get('bucket', os.getenv('S3_BUCKET'))
        self.default_model = self.config.get('default_model', BedrockModel.CLAUDE_3_HAIKU.value)

        # Session management
        self._session = None

        if BOTO3_AVAILABLE:
            self._initialize_session()

    def _initialize_session(self):
        """Initialize AWS session with credentials."""
        try:
            if 'access_key_id' in self.config:
                self._session = boto3.Session(
                    aws_access_key_id=self.config['access_key_id'],
                    aws_secret_access_key=self.config['secret_access_key'],
                    region_name=self.region
                )
            else:
                # Use default credentials (IAM role, env vars, etc.)
                self._session = boto3.Session(region_name=self.region)

            logger.info(f"AWS session initialized for region: {self.region}")
        except Exception as e:
            logger.warning(f"Could not initialize AWS session: {e}")
            self._session = None

    def is_available(self) -> bool:
        """Check if AWS services are available."""
        return BOTO3_AVAILABLE and self._session is not None

    # ==================== S3 Operations ====================

    def get_s3_client(self):
        """Get or create S3 client (lazy initialization)."""
        if not self.is_available():
            return None

        if self._s3_client is None:
            self._s3_client = self._session.client('s3', region_name=self.region)
            self._s3_resource = self._session.resource('s3', region_name=self.region)
        return self._s3_client

    def upload_file(self, file_path: str, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Upload a file to S3."""
        client = self.get_s3_client()
        if not client:
            logger.warning("S3 client not available")
            return False

        bucket = bucket or self.s3_bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            client.upload_file(file_path, bucket, s3_key)
            logger.info(f"Uploaded {file_path} to s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def download_file(self, s3_key: str, local_path: str, bucket: Optional[str] = None) -> bool:
        """Download a file from S3."""
        client = self.get_s3_client()
        if not client:
            logger.warning("S3 client not available")
            return False

        bucket = bucket or self.s3_bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            client.download_file(bucket, s3_key, local_path)
            logger.info(f"Downloaded s3://{bucket}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            return False

    def list_s3_objects(self, prefix: str = "", bucket: Optional[str] = None) -> List[str]:
        """List objects in S3 bucket."""
        client = self.get_s3_client()
        if not client:
            logger.warning("S3 client not available")
            return []

        bucket = bucket or self.s3_bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return []

        try:
            response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []

    def read_json_from_s3(self, s3_key: str, bucket: Optional[str] = None) -> Optional[Dict]:
        """Read a JSON file from S3."""
        client = self.get_s3_client()
        if not client:
            return None

        bucket = bucket or self.s3_bucket
        if not bucket:
            return None

        try:
            response = client.get_object(Bucket=bucket, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to read JSON from S3: {e}")
            return None

    def write_json_to_s3(self, data: Dict, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Write JSON data to S3."""
        client = self.get_s3_client()
        if not client:
            return False

        bucket = bucket or self.s3_bucket
        if not bucket:
            return False

        try:
            json_data = json.dumps(data, indent=2)
            client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            logger.info(f"Wrote JSON to s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON to S3: {e}")
            return False

    def s3_object_exists(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Check if an S3 object exists."""
        client = self.get_s3_client()
        if not client:
            return False

        bucket = bucket or self.s3_bucket
        if not bucket:
            return False

        try:
            client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking S3 object: {e}")
            return False

    def delete_s3_object(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """Delete an S3 object."""
        client = self.get_s3_client()
        if not client:
            return False

        bucket = bucket or self.s3_bucket
        if not bucket:
            return False

        try:
            client.delete_object(Bucket=bucket, Key=s3_key)
            logger.info(f"Deleted s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    def get_s3_presigned_url(self, s3_key: str, expires_in: int = 3600, bucket: Optional[str] = None) -> Optional[str]:
        """Generate a presigned URL for S3 object."""
        client = self.get_s3_client()
        if not client:
            return None

        bucket = bucket or self.s3_bucket
        if not bucket:
            return None

        try:
            url = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    # ==================== Bedrock Operations ====================

    def get_bedrock_client(self):
        """Get or create Bedrock client (lazy initialization)."""
        if not self.is_available():
            return None

        if self._bedrock_client is None:
            self._bedrock_client = self._session.client('bedrock', region_name=self.region)
        return self._bedrock_client

    def get_bedrock_runtime_client(self):
        """Get or create Bedrock Runtime client (lazy initialization)."""
        if not self.is_available():
            return None

        if self._bedrock_runtime_client is None:
            self._bedrock_runtime_client = self._session.client('bedrock-runtime', region_name=self.region)
        return self._bedrock_runtime_client

    def list_foundation_models(self) -> List[Dict]:
        """List available foundation models."""
        client = self.get_bedrock_client()
        if not client:
            return []

        try:
            response = client.list_foundation_models()
            return response.get('modelSummaries', [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def invoke_model(self, prompt: str, model_id: Optional[str] = None, **kwargs) -> Optional[str]:
        """Invoke a Bedrock model."""
        client = self.get_bedrock_runtime_client()
        if not client:
            return None

        model_id = model_id or self.default_model

        try:
            # Format request based on model type
            if 'claude' in model_id.lower():
                request_body = self._format_claude_request(prompt, **kwargs)
            elif 'titan' in model_id.lower():
                request_body = self._format_titan_request(prompt, **kwargs)
            else:
                request_body = {"prompt": prompt, "max_tokens": kwargs.get('max_tokens', 1000)}

            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )

            response_body = json.loads(response['body'].read())
            return self._extract_text_from_response(response_body, model_id)

        except Exception as e:
            logger.error(f"Failed to invoke model: {e}")
            return None

    def _format_claude_request(self, prompt: str, **kwargs) -> Dict:
        """Format request for Claude models."""
        max_tokens = kwargs.get('max_tokens', 1000)
        temperature = kwargs.get('temperature', 0.7)

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

    def _format_titan_request(self, prompt: str, **kwargs) -> Dict:
        """Format request for Titan models."""
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7)
            }
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
        else:
            return response_body.get('completion', '') or response_body.get('text', '')

    def create_embedding(self, text: str, model_id: Optional[str] = None) -> Optional[List[float]]:
        """Create text embedding using Titan Embed model."""
        client = self.get_bedrock_runtime_client()
        if not client:
            return None

        model_id = model_id or BedrockModel.TITAN_EMBED_TEXT.value

        try:
            request_body = {"inputText": text}
            response = client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', None)
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None

    # ==================== STS Operations ====================

    def get_sts_client(self):
        """Get or create STS client (lazy initialization)."""
        if not self.is_available():
            return None

        if self._sts_client is None:
            self._sts_client = self._session.client('sts', region_name=self.region)
        return self._sts_client

    def get_caller_identity(self) -> Optional[Dict]:
        """Get caller identity from STS."""
        client = self.get_sts_client()
        if not client:
            return None

        try:
            return client.get_caller_identity()
        except Exception as e:
            logger.error(f"Failed to get caller identity: {e}")
            return None

    def assume_role(self, role_arn: str, session_name: str) -> Optional[Dict]:
        """Assume an IAM role."""
        client = self.get_sts_client()
        if not client:
            return None

        try:
            response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name
            )
            return response.get('Credentials')
        except Exception as e:
            logger.error(f"Failed to assume role: {e}")
            return None

    # ==================== Health Checks ====================

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all AWS services."""
        health = {
            'available': self.is_available(),
            'region': self.region,
            'services': {}
        }

        if self.is_available():
            # Check S3
            try:
                client = self.get_s3_client()
                if client:
                    client.list_buckets()
                    health['services']['s3'] = {'status': 'healthy'}
            except Exception as e:
                health['services']['s3'] = {'status': 'error', 'message': str(e)}

            # Check Bedrock
            try:
                client = self.get_bedrock_client()
                if client:
                    client.list_foundation_models()
                    health['services']['bedrock'] = {'status': 'healthy'}
            except Exception as e:
                health['services']['bedrock'] = {'status': 'error', 'message': str(e)}

            # Check STS
            try:
                identity = self.get_caller_identity()
                if identity:
                    health['services']['sts'] = {
                        'status': 'healthy',
                        'account': identity.get('Account')
                    }
            except Exception as e:
                health['services']['sts'] = {'status': 'error', 'message': str(e)}

        return health


# Singleton instance
_aws_service = None

def get_aws_service(config: Optional[Dict] = None) -> AWSService:
    """
    Get the singleton AWS service instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        AWSService instance
    """
    global _aws_service
    if _aws_service is None:
        _aws_service = AWSService(config)
    return _aws_service

def inject_aws_config(config: Dict):
    """
    Inject AWS configuration for child packages.

    This is called by child packages like TidyLLM to set up AWS.
    """
    global _aws_service
    _aws_service = AWSService(config)
    return _aws_service