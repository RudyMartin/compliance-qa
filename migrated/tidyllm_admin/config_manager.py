"""
TidyLLM Configuration Manager - PURE LIBRARY APPROACH

This module provides configuration interfaces for TidyLLM.
The actual configuration is injected by the application layer.
TidyLLM itself has NO infrastructure dependencies.
"""

import os
from typing import Dict, Any, Optional

# Global configuration instance - set by application layer
_config_instance = None

class DatabaseConfig:
    """Database configuration interface."""

    def __init__(self, config_dict: Optional[Dict] = None):
        """Initialize from dictionary or environment variables."""
        if config_dict:
            self.postgres_host = config_dict.get('host', 'localhost')
            self.postgres_port = config_dict.get('port', 5432)
            self.postgres_database = config_dict.get('database', 'tidyllm_db')
            self.postgres_username = config_dict.get('username', 'tidyllm_user')
            self.postgres_password = config_dict.get('password', '')
            self.postgres_ssl_mode = config_dict.get('ssl_mode', 'prefer')
        else:
            # Fallback to environment variables
            self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
            self.postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
            self.postgres_database = os.getenv('POSTGRES_DATABASE', 'tidyllm_db')
            self.postgres_username = os.getenv('POSTGRES_USERNAME', 'tidyllm_user')
            self.postgres_password = os.getenv('POSTGRES_PASSWORD', '')
            self.postgres_ssl_mode = os.getenv('POSTGRES_SSL_MODE', 'prefer')

        # MLFlow settings
        self.mlflow_tracking_uri = os.getenv('MLFLOW_TRACKING_URI', '')
        self.mlflow_backend_store_uri = self.mlflow_tracking_uri
        self.mlflow_artifact_root = os.getenv('MLFLOW_ARTIFACT_ROOT', '')

class GatewayConfig:
    """Gateway configuration interface."""

    def __init__(self, config_dict: Optional[Dict] = None):
        """Initialize from dictionary or environment variables."""
        if config_dict:
            self.base_url = config_dict.get('base_url', 'http://localhost:8000')
            self.api_key = config_dict.get('api_key', '')
            self.timeout = config_dict.get('timeout', 30)
        else:
            self.base_url = os.getenv('GATEWAY_BASE_URL', 'http://localhost:8000')
            self.api_key = os.getenv('GATEWAY_API_KEY', '')
            self.timeout = int(os.getenv('GATEWAY_TIMEOUT', '30'))

class AWSConfig:
    """AWS configuration interface."""

    def __init__(self, config_dict: Optional[Dict] = None):
        """Initialize from dictionary or environment variables."""
        if config_dict:
            self.access_key_id = config_dict.get('access_key_id', '')
            self.secret_access_key = config_dict.get('secret_access_key', '')
            self.region = config_dict.get('region', 'us-east-1')
            self.bedrock_endpoint = config_dict.get('bedrock_endpoint', '')
        else:
            self.access_key_id = os.getenv('AWS_ACCESS_KEY_ID', '')
            self.secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
            self.region = os.getenv('AWS_REGION', 'us-east-1')
            self.bedrock_endpoint = os.getenv('BEDROCK_ENDPOINT', '')

class TidyLLMConfig:
    """
    Main configuration class for TidyLLM.

    This is a pure data class with no infrastructure dependencies.
    The application layer is responsible for providing configuration.
    """

    def __init__(self,
                 database_config: Optional[Dict] = None,
                 gateway_config: Optional[Dict] = None,
                 aws_config: Optional[Dict] = None):
        """
        Initialize configuration.

        Args:
            database_config: Database configuration dictionary
            gateway_config: Gateway configuration dictionary
            aws_config: AWS configuration dictionary
        """
        self.database = DatabaseConfig(database_config)
        self.gateway = GatewayConfig(gateway_config)
        self.aws = AWSConfig(aws_config)

        # Optional: environment manager can be injected
        self.env_manager = None

    def get_connection_string(self) -> str:
        """Build database connection string from configuration."""
        db = self.database
        return (
            f"postgresql://{db.postgres_username}:{db.postgres_password}"
            f"@{db.postgres_host}:{db.postgres_port}/{db.postgres_database}"
            f"?sslmode={db.postgres_ssl_mode}"
        )

    def validate_credentials(self) -> bool:
        """
        Basic validation that required fields are present.

        Real validation should be done by the application layer.
        """
        # Check if essential fields are present
        has_db = bool(self.database.postgres_host and self.database.postgres_database)
        has_gateway = bool(self.gateway.base_url)

        return has_db or has_gateway

    @classmethod
    def from_environment(cls):
        """Create config from environment variables."""
        return cls()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """
        Create config from a dictionary.

        This is the preferred method for the application layer
        to inject configuration.
        """
        return cls(
            database_config=config_dict.get('database'),
            gateway_config=config_dict.get('gateway'),
            aws_config=config_dict.get('aws')
        )

def get_config() -> TidyLLMConfig:
    """
    Get the global configuration instance.

    Returns a default config if none has been set.
    The application layer should call set_config() first.
    """
    global _config_instance
    if _config_instance is None:
        # Return default config from environment
        _config_instance = TidyLLMConfig.from_environment()
    return _config_instance

def set_config(config: TidyLLMConfig):
    """
    Set the global configuration instance.

    This should be called by the application layer to inject configuration.
    """
    global _config_instance
    _config_instance = config

def inject_config(config_dict: Dict[str, Any]):
    """
    Convenience method for the application layer to inject configuration.

    Args:
        config_dict: Configuration dictionary from the application layer
    """
    config = TidyLLMConfig.from_dict(config_dict)
    set_config(config)

# Compatibility functions for old code
def get_database_config():
    """Get database configuration."""
    return get_config().database

def get_gateway_config():
    """Get gateway configuration."""
    return get_config().gateway

def get_aws_config():
    """Get AWS configuration."""
    return get_config().aws

def validate_all_credentials():
    """Validate all credentials."""
    return get_config().validate_credentials()