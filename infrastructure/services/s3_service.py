"""
S3 Service - Parent Infrastructure
===================================
Provides S3 functionality for all child packages.
TidyLLM and other packages borrow this instead of importing boto3 directly.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import tempfile

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

class S3Service:
    """
    Centralized S3 service for the infrastructure.
    All S3 operations go through this service.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize S3 service with configuration."""
        self.config = config or {}
        self._client = None
        self._resource = None

        # Get configuration from environment or config
        self.region = self.config.get('region', os.getenv('AWS_REGION', 'us-east-1'))
        self.bucket = self.config.get('bucket', os.getenv('S3_BUCKET'))

        if BOTO3_AVAILABLE:
            self._initialize_aws()

    def _initialize_aws(self):
        """Initialize AWS clients if boto3 is available."""
        try:
            # Use environment credentials or config
            if 'access_key_id' in self.config:
                self._client = boto3.client(
                    's3',
                    region_name=self.region,
                    aws_access_key_id=self.config['access_key_id'],
                    aws_secret_access_key=self.config['secret_access_key']
                )
                self._resource = boto3.resource(
                    's3',
                    region_name=self.region,
                    aws_access_key_id=self.config['access_key_id'],
                    aws_secret_access_key=self.config['secret_access_key']
                )
            else:
                # Use default credentials (IAM role, env vars, etc.)
                self._client = boto3.client('s3', region_name=self.region)
                self._resource = boto3.resource('s3', region_name=self.region)

            logger.info(f"S3 service initialized for region: {self.region}")
        except Exception as e:
            logger.warning(f"Could not initialize S3: {e}")
            self._client = None
            self._resource = None

    def is_available(self) -> bool:
        """Check if S3 service is available."""
        return BOTO3_AVAILABLE and self._client is not None

    def upload_file(self, file_path: str, s3_key: str, bucket: Optional[str] = None) -> bool:
        """
        Upload a file to S3.

        Args:
            file_path: Local file path
            s3_key: S3 object key
            bucket: S3 bucket (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return False

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            self._client.upload_file(file_path, bucket, s3_key)
            logger.info(f"Uploaded {file_path} to s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def download_file(self, s3_key: str, local_path: str, bucket: Optional[str] = None) -> bool:
        """
        Download a file from S3.

        Args:
            s3_key: S3 object key
            local_path: Local file path to save to
            bucket: S3 bucket (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return False

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            self._client.download_file(bucket, s3_key, local_path)
            logger.info(f"Downloaded s3://{bucket}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download from S3: {e}")
            return False

    def list_objects(self, prefix: str = "", bucket: Optional[str] = None) -> List[str]:
        """
        List objects in S3 bucket.

        Args:
            prefix: Prefix to filter objects
            bucket: S3 bucket (uses default if not provided)

        Returns:
            List of object keys
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return []

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return []

        try:
            response = self._client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )

            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []

    def read_json(self, s3_key: str, bucket: Optional[str] = None) -> Optional[Dict]:
        """
        Read a JSON file from S3.

        Args:
            s3_key: S3 object key
            bucket: S3 bucket (uses default if not provided)

        Returns:
            Parsed JSON data or None
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return None

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return None

        try:
            response = self._client.get_object(Bucket=bucket, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to read JSON from S3: {e}")
            return None

    def write_json(self, data: Dict, s3_key: str, bucket: Optional[str] = None) -> bool:
        """
        Write JSON data to S3.

        Args:
            data: Data to write as JSON
            s3_key: S3 object key
            bucket: S3 bucket (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return False

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            json_data = json.dumps(data, indent=2)
            self._client.put_object(
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

    def exists(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """
        Check if an S3 object exists.

        Args:
            s3_key: S3 object key
            bucket: S3 bucket (uses default if not provided)

        Returns:
            True if object exists, False otherwise
        """
        if not self.is_available():
            return False

        bucket = bucket or self.bucket
        if not bucket:
            return False

        try:
            self._client.head_object(Bucket=bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking S3 object existence: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking S3: {e}")
            return False

    def delete(self, s3_key: str, bucket: Optional[str] = None) -> bool:
        """
        Delete an S3 object.

        Args:
            s3_key: S3 object key
            bucket: S3 bucket (uses default if not provided)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return False

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return False

        try:
            self._client.delete_object(Bucket=bucket, Key=s3_key)
            logger.info(f"Deleted s3://{bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    def get_presigned_url(self, s3_key: str, expires_in: int = 3600, bucket: Optional[str] = None) -> Optional[str]:
        """
        Generate a presigned URL for S3 object.

        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds
            bucket: S3 bucket (uses default if not provided)

        Returns:
            Presigned URL or None
        """
        if not self.is_available():
            logger.warning("S3 service not available")
            return None

        bucket = bucket or self.bucket
        if not bucket:
            logger.error("No S3 bucket specified")
            return None

        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None


# Singleton instance
_s3_service = None

def get_s3_service(config: Optional[Dict] = None) -> S3Service:
    """
    Get the singleton S3 service instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        S3Service instance
    """
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service(config)
    return _s3_service

def inject_s3_config(config: Dict):
    """
    Inject S3 configuration for child packages.

    This is called by child packages like TidyLLM to set up S3.
    """
    global _s3_service
    _s3_service = S3Service(config)
    return _s3_service