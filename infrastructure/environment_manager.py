"""
Environment Manager for qa-shipping Portal System

Centralized environment variable and configuration management.
Eliminates hardcoded credentials and provides secure config access.

Inspired by hexagonal architecture lessons but keeping compatibility.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml

# Import settings loader for YAML configuration
try:
    from .settings_loader import get_settings_loader, setup_environment_from_settings
except ImportError:
    # Fallback if settings_loader not available
    get_settings_loader = None
    setup_environment_from_settings = None

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration container."""
    host: str
    port: int
    database: str
    username: str
    password: str

    @property
    def connection_url(self) -> str:
        """Generate database connection URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class AWSConfig:
    """AWS configuration container."""
    region: str
    access_key_id: Optional[str]
    secret_access_key: Optional[str]
    profile: Optional[str]


@dataclass
class MLflowConfig:
    """MLflow configuration container."""
    tracking_uri: str
    s3_endpoint_url: Optional[str]
    artifact_root: Optional[str]


class EnvironmentManager:
    """
    Centralized environment management for qa-shipping.

    Handles secure credential loading, environment validation,
    and configuration management across all portals.
    """

    def __init__(self):
        self.config_cache: Dict[str, Any] = {}
        self._load_environment()

    def _load_environment(self):
        """Load and validate environment variables."""
        logger.info("Loading environment configuration...")

        # Set default environment if not specified
        if not os.getenv('ENVIRONMENT'):
            os.environ['ENVIRONMENT'] = 'development'
            logger.info("Set default environment: development")

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration from environment."""
        if 'database' not in self.config_cache:
            # Try to load from settings.yaml if environment variables not set
            host = os.getenv('DB_HOST')
            port = os.getenv('DB_PORT')
            database = os.getenv('DB_NAME')
            username = os.getenv('DB_USERNAME')
            password = os.getenv('DB_PASSWORD')

            # Fallback to settings.yaml if not in environment
            if not all([host, port, database, username]):
                try:
                    if get_settings_loader:
                        settings_loader = get_settings_loader()
                        config = settings_loader.load_config()
                        pg_config = getattr(config, 'credentials', {}).get('postgresql', {})

                        host = host or pg_config.get('host', 'localhost')
                        port = port or str(pg_config.get('port', 5432))
                        database = database or pg_config.get('database', 'tidyllm')
                        username = username or pg_config.get('username', 'tidyllm_user')
                        password = password or pg_config.get('password', 'tidyllm_pass')
                except Exception as e:
                    logger.warning(f"Could not load from settings.yaml: {e}")
                    # Use defaults if settings.yaml fails
                    host = host or 'localhost'
                    port = port or '5432'
                    database = database or 'tidyllm'
                    username = username or 'tidyllm_user'
                    password = password or 'tidyllm_pass'

            self.config_cache['database'] = DatabaseConfig(
                host=host,
                port=int(port),
                database=database,
                username=username,
                password=password
            )
        return self.config_cache['database']

    def get_aws_config(self) -> AWSConfig:
        """Get AWS configuration from environment."""
        if 'aws' not in self.config_cache:
            # Try environment variables first
            region = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION')
            access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
            secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            profile = os.getenv('AWS_PROFILE')

            # Fallback to settings.yaml if not in environment
            if not region or not access_key_id:
                try:
                    if get_settings_loader:
                        settings_loader = get_settings_loader()
                        config = settings_loader.load_config()
                        aws_config = getattr(config, 'credentials', {}).get('aws', {})

                        region = region or aws_config.get('default_region', 'us-east-1')
                        access_key_id = access_key_id or aws_config.get('access_key_id')
                        secret_access_key = secret_access_key or aws_config.get('secret_access_key')
                        profile = profile or aws_config.get('profile')
                except Exception as e:
                    logger.warning(f"Could not load AWS config from settings.yaml: {e}")
                    region = region or 'us-east-1'

            self.config_cache['aws'] = AWSConfig(
                region=region,
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
                profile=profile
            )
        return self.config_cache['aws']

    def get_mlflow_config(self) -> MLflowConfig:
        """Get MLflow configuration from environment."""
        if 'mlflow' not in self.config_cache:
            self.config_cache['mlflow'] = MLflowConfig(
                tracking_uri=os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'),
                s3_endpoint_url=os.getenv('MLFLOW_S3_ENDPOINT_URL'),
                artifact_root=os.getenv('MLFLOW_ARTIFACT_ROOT')
            )
        return self.config_cache['mlflow']

    def _get_secure_credential(self, env_var: str, default: str) -> str:
        """
        Get credential from environment with fallback.

        Prioritizes environment variables over hardcoded defaults.
        Logs warning if using fallback credentials.
        """
        value = os.getenv(env_var)
        if value:
            logger.info(f"Using {env_var} from environment")
            return value
        else:
            logger.warning(f"Using default value for {env_var} - consider setting environment variable")
            return default

    def validate_configuration(self) -> Dict[str, bool]:
        """
        Validate all configuration components.

        Returns:
            Dict mapping component names to validation status
        """
        validation_results = {}

        # Validate database config
        try:
            db_config = self.get_database_config()
            validation_results['database'] = bool(
                db_config.host and
                db_config.database and
                db_config.username and
                db_config.password
            )
        except Exception as e:
            logger.error(f"Database config validation failed: {e}")
            validation_results['database'] = False

        # Validate AWS config
        try:
            aws_config = self.get_aws_config()
            # Check both region and credentials for AWS validation
            has_region = bool(aws_config.region)
            has_credentials = bool(aws_config.access_key_id and aws_config.secret_access_key)

            if has_credentials:
                validation_results['aws'] = True
                logger.info("AWS credentials validated")
            elif has_region:
                validation_results['aws'] = True  # Allow default profile/IAM role
                logger.info("AWS region configured - using default profile/IAM role")
            else:
                validation_results['aws'] = False
                logger.warning("AWS not configured properly")
        except Exception as e:
            logger.error(f"AWS config validation failed: {e}")
            validation_results['aws'] = False

        # Validate MLflow config
        try:
            mlflow_config = self.get_mlflow_config()
            validation_results['mlflow'] = bool(mlflow_config.tracking_uri)
        except Exception as e:
            logger.error(f"MLflow config validation failed: {e}")
            validation_results['mlflow'] = False

        return validation_results

    def get_portal_config(self, portal_name: str) -> Dict[str, Any]:
        """
        Get portal-specific configuration.

        Args:
            portal_name: Name of the portal (e.g., 'chat', 'rag', 'flow')

        Returns:
            Portal-specific configuration dict
        """
        base_config = {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        }

        # Portal-specific configurations
        portal_configs = {
            'chat': {
                'max_history': int(os.getenv('CHAT_MAX_HISTORY', '10')),
                'response_timeout': int(os.getenv('CHAT_TIMEOUT', '30'))
            },
            'rag': {
                'max_documents': int(os.getenv('RAG_MAX_DOCS', '100')),
                'chunk_size': int(os.getenv('RAG_CHUNK_SIZE', '1000'))
            },
            'flow': {
                'max_steps': int(os.getenv('FLOW_MAX_STEPS', '50')),
                'execution_timeout': int(os.getenv('FLOW_TIMEOUT', '300'))
            }
        }

        portal_config = base_config.copy()
        if portal_name in portal_configs:
            portal_config.update(portal_configs[portal_name])

        return portal_config

    def get_environment_summary(self) -> Dict[str, Any]:
        """Get summary of current environment configuration."""
        validation_results = self.validate_configuration()

        return {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'validation_results': validation_results,
            'config_sources': {
                'database': 'environment' if os.getenv('DB_PASSWORD') else 'default',
                'aws': 'environment' if os.getenv('AWS_ACCESS_KEY_ID') else 'default/profile',
                'mlflow': 'environment' if os.getenv('MLFLOW_TRACKING_URI') else 'default'
            }
        }


# Global environment manager instance
_env_manager = None

def get_environment_manager() -> EnvironmentManager:
    """Get global environment manager instance."""
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager


# Convenience functions for easy access
def get_db_config() -> DatabaseConfig:
    """Quick access to database configuration."""
    return get_environment_manager().get_database_config()

def get_aws_config() -> AWSConfig:
    """Quick access to AWS configuration."""
    return get_environment_manager().get_aws_config()

def get_mlflow_config() -> MLflowConfig:
    """Quick access to MLflow configuration."""
    return get_environment_manager().get_mlflow_config()

def validate_environment() -> Dict[str, bool]:
    """Quick environment validation."""
    return get_environment_manager().validate_configuration()


if __name__ == "__main__":
    # Test the environment manager
    env_mgr = EnvironmentManager()

    print("Environment Summary:")
    summary = env_mgr.get_environment_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nDatabase Config:")
    db_config = env_mgr.get_database_config()
    print(f"  Host: {db_config.host}")
    print(f"  Database: {db_config.database}")
    print(f"  Username: {db_config.username}")
    print(f"  Password: {'***' if db_config.password else 'Not Set'}")