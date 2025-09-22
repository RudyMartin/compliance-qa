"""
Settings Loader - Infrastructure Layer

Reads configuration from settings.yaml to avoid hardcoding credentials.
Provides secure access to configuration with environment variable fallbacks.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SettingsConfig:
    """Configuration loaded from settings.yaml"""
    # Database settings
    db_host: str
    db_port: int
    db_name: str
    db_username: str
    db_password: str

    # AWS settings
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

    # MLflow settings
    mlflow_tracking_uri: str
    mlflow_artifact_store: str

    # S3 settings
    s3_bucket: str
    s3_prefix: str

class SettingsLoader:
    """Loads configuration from settings.yaml with environment fallbacks."""

    def __init__(self, settings_path: Optional[str] = None):
        self.settings_path = settings_path or self._find_settings_file()
        self._settings_cache: Optional[Dict[str, Any]] = None

    def _find_settings_file(self) -> str:
        """Find settings.yaml file in infrastructure directory."""
        # Look in infrastructure directory first
        infrastructure_path = Path(__file__).parent / "settings.yaml"
        if infrastructure_path.exists():
            return str(infrastructure_path)

        # Fallback to tidyllm/admin/settings.yaml if available
        current_dir = Path.cwd()
        for potential_path in [
            current_dir / "tidyllm" / "admin" / "settings.yaml",
            current_dir / "infrastructure" / "settings.yaml",
            current_dir / "settings.yaml"
        ]:
            if potential_path.exists():
                return str(potential_path)

        raise FileNotFoundError("No settings.yaml file found")

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from YAML file with caching."""
        if self._settings_cache is None:
            try:
                with open(self.settings_path, 'r') as f:
                    self._settings_cache = yaml.safe_load(f)
                logger.info(f"Settings loaded from {self.settings_path}")
            except Exception as e:
                logger.error(f"Failed to load settings from {self.settings_path}: {e}")
                raise
        return self._settings_cache

    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration from settings."""
        settings = self._load_settings()

        # Try postgresql_primary first (new structure), then postgresql (old structure)
        creds = settings.get('credentials', {}).get('postgresql_primary', {})
        if not creds:
            creds = settings.get('credentials', {}).get('postgresql', {})

        return {
            'host': os.getenv('DB_HOST', creds.get('host', 'localhost')),
            'port': int(os.getenv('DB_PORT', creds.get('port', 5432))),
            'database': os.getenv('DB_NAME', creds.get('database', 'vectorqa')),
            'username': os.getenv('DB_USERNAME', creds.get('username', 'postgres')),
            'password': os.getenv('DB_PASSWORD', creds.get('password', ''))
        }

    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS configuration from settings."""
        settings = self._load_settings()
        creds = settings.get('credentials', {}).get('aws', {})

        return {
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID', creds.get('access_key_id', '')),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', creds.get('secret_access_key', '')),
            'region': os.getenv('AWS_REGION', creds.get('default_region', 'us-east-1'))
        }

    def get_mlflow_config(self) -> Dict[str, Any]:
        """Get MLflow configuration from settings."""
        settings = self._load_settings()
        mlflow_config = settings.get('integrations', {}).get('mlflow', {})
        services_mlflow = settings.get('services', {}).get('mlflow', {})

        tracking_uri = (
            os.getenv('MLFLOW_TRACKING_URI') or
            mlflow_config.get('tracking_uri') or
            services_mlflow.get('tracking_uri') or
            'http://localhost:5000'
        )

        artifact_store = (
            mlflow_config.get('artifact_store') or
            services_mlflow.get('artifact_store') or
            's3://nsc-mvp1/compliance-qa/mlflow/'
        )

        return {
            'tracking_uri': tracking_uri,
            'artifact_store': artifact_store
        }

    def get_s3_config(self) -> Dict[str, Any]:
        """Get S3 configuration from settings."""
        settings = self._load_settings()
        s3_config = settings.get('services', {}).get('s3', {})

        return {
            'bucket': s3_config.get('bucket', 'nsc-mvp1'),
            'prefix': s3_config.get('prefix', 'compliance-qa/'),
            'region': s3_config.get('region', 'us-east-1')
        }

    def get_bedrock_config(self) -> Dict[str, Any]:
        """Get Bedrock configuration from settings - no hardcoding."""
        settings = self._load_settings()
        bedrock_config = settings.get('credentials', {}).get('bedrock_llm', {})

        # Return exactly what's in settings without hardcoded fallbacks
        result = {}

        # Only include keys that exist in settings
        for key in ['service_provider', 'region', 'default_model', 'model_mapping', 'adapter_config']:
            if key in bedrock_config:
                result[key] = bedrock_config[key]

        # Extract nested adapter_config values if they exist
        adapter_config = bedrock_config.get('adapter_config', {})
        if 'retry_attempts' in adapter_config:
            result['retry_attempts'] = adapter_config['retry_attempts']
        if 'timeout' in adapter_config:
            result['timeout'] = adapter_config['timeout']

        return result

    def get_environment_type(self) -> str:
        """Get environment type from settings."""
        settings = self._load_settings()
        return os.getenv('ENVIRONMENT', settings.get('environment', 'development'))

    def load_config(self) -> SettingsConfig:
        """Load complete configuration as dataclass."""
        db_config = self.get_database_config()
        aws_config = self.get_aws_config()
        mlflow_config = self.get_mlflow_config()
        s3_config = self.get_s3_config()

        return SettingsConfig(
            # Database
            db_host=db_config['host'],
            db_port=db_config['port'],
            db_name=db_config['database'],
            db_username=db_config['username'],
            db_password=db_config['password'],

            # AWS
            aws_access_key_id=aws_config['access_key_id'],
            aws_secret_access_key=aws_config['secret_access_key'],
            aws_region=aws_config['region'],

            # MLflow
            mlflow_tracking_uri=mlflow_config['tracking_uri'],
            mlflow_artifact_store=mlflow_config['artifact_store'],

            # S3
            s3_bucket=s3_config['bucket'],
            s3_prefix=s3_config['prefix']
        )

    def set_environment_variables(self):
        """Set environment variables from settings (for compatibility)."""
        config = self.load_config()

        # Set database environment variables
        os.environ['DB_HOST'] = config.db_host
        os.environ['DB_PORT'] = str(config.db_port)
        os.environ['DB_NAME'] = config.db_name
        os.environ['DB_USERNAME'] = config.db_username
        os.environ['DB_PASSWORD'] = config.db_password

        # Set AWS environment variables
        if config.aws_access_key_id:
            os.environ['AWS_ACCESS_KEY_ID'] = config.aws_access_key_id
        if config.aws_secret_access_key:
            os.environ['AWS_SECRET_ACCESS_KEY'] = config.aws_secret_access_key
        os.environ['AWS_REGION'] = config.aws_region

        # Set MLflow environment variables
        os.environ['MLFLOW_TRACKING_URI'] = config.mlflow_tracking_uri

        logger.info("Environment variables set from settings.yaml")

    def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of loaded settings for display."""
        config = self.load_config()

        return {
            'source_file': self.settings_path,
            'environment': self.get_environment_type(),
            'database': {
                'host': config.db_host,
                'port': config.db_port,
                'database': config.db_name,
                'username': config.db_username,
                'password_set': bool(config.db_password)
            },
            'aws': {
                'region': config.aws_region,
                'credentials_set': bool(config.aws_access_key_id and config.aws_secret_access_key)
            },
            'mlflow': {
                'tracking_uri': config.mlflow_tracking_uri,
                'artifact_store': config.mlflow_artifact_store
            },
            's3': {
                'bucket': config.s3_bucket,
                'prefix': config.s3_prefix
            }
        }


# Global settings loader instance
_settings_loader: Optional[SettingsLoader] = None

def get_settings_loader() -> SettingsLoader:
    """Get global settings loader instance."""
    global _settings_loader
    if _settings_loader is None:
        _settings_loader = SettingsLoader()
    return _settings_loader

def load_settings_config() -> SettingsConfig:
    """Quick access to settings configuration."""
    return get_settings_loader().load_config()

def setup_environment_from_settings():
    """Setup environment variables from settings.yaml."""
    get_settings_loader().set_environment_variables()


if __name__ == "__main__":
    # Demo the settings loader
    print("Compliance-QA Settings Loader Demo")
    print("=" * 40)

    try:
        loader = SettingsLoader()
        summary = loader.get_settings_summary()

        print(f"Settings loaded from: {summary['source_file']}")
        print(f"Environment: {summary['environment']}")
        print(f"Database: {summary['database']['host']}:{summary['database']['port']}")
        print(f"AWS Region: {summary['aws']['region']}")
        print(f"MLflow: {summary['mlflow']['tracking_uri']}")

        # Setup environment variables
        loader.set_environment_variables()
        print("\nEnvironment variables configured!")

    except Exception as e:
        print(f"Error: {e}")