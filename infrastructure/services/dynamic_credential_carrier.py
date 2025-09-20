"""
Dynamic Credential Carrier Service
===================================
Next-generation Resource Carrier Pattern implementation for dynamic credential management.

FIXES THE ARCHITECTURAL PROBLEM:
- Dynamic discovery of ALL credential sources in settings.yaml
- Support for multiple databases, services, and integrations
- Automatic detection of new credential types
- No hardcoded credential types

REPLACES: Static hardcoded 'aws' and 'database' approach
WITH: Dynamic discovery of all sections: credentials, databases, services, integrations
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicCredentialDiscovery:
    """Discovers all credential sources from settings.yaml dynamically"""

    def __init__(self, settings_loader=None):
        self._settings_loader = settings_loader
        self._raw_settings = None

    def discover_all_credential_sources(self) -> Dict[str, Dict[str, Any]]:
        """Dynamically discover ALL credential sources in settings.yaml"""

        if not self._settings_loader:
            from infrastructure.yaml_loader import get_settings_loader
            self._settings_loader = get_settings_loader()

        # Get raw settings dict (not the flattened dataclass)
        self._raw_settings = self._settings_loader._load_settings()

        discovered = {}

        # 1. Discover direct credentials section
        if 'credentials' in self._raw_settings:
            creds = self._raw_settings['credentials']
            for source_name, config in creds.items():
                if isinstance(config, dict):
                    discovered[f"cred_{source_name}"] = {
                        'type': 'credential',
                        'source': 'credentials',
                        'name': source_name,
                        'config': config,
                        'category': self._categorize_credential(source_name, config)
                    }

        # 2. Discover database configurations
        if 'databases' in self._raw_settings:
            dbs = self._raw_settings['databases']
            for db_name, config in dbs.items():
                if isinstance(config, dict):
                    discovered[f"db_{db_name}"] = {
                        'type': 'database',
                        'source': 'databases',
                        'name': db_name,
                        'config': config,
                        'category': config.get('engine', 'unknown')
                    }

        # 3. Discover service configurations with credentials
        if 'services' in self._raw_settings:
            services = self._raw_settings['services']
            for service_name, config in services.items():
                if isinstance(config, dict):
                    # Special handling for AWS services that contain Bedrock
                    if service_name == 'aws' and 'bedrock' in config:
                        discovered[f"svc_{service_name}"] = {
                            'type': 'service',
                            'source': 'services',
                            'name': service_name,
                            'config': config,
                            'category': 'llm_service'  # Categorize as LLM service
                        }
                    elif self._has_credential_data(config):
                        discovered[f"svc_{service_name}"] = {
                            'type': 'service',
                            'source': 'services',
                            'name': service_name,
                            'config': config,
                            'category': service_name
                        }

        # 4. Discover integration configurations
        if 'integrations' in self._raw_settings:
            integrations = self._raw_settings['integrations']
            for integration_name, config in integrations.items():
                if isinstance(config, dict) and config.get('enabled', False):
                    discovered[f"int_{integration_name}"] = {
                        'type': 'integration',
                        'source': 'integrations',
                        'name': integration_name,
                        'config': config,
                        'category': integration_name
                    }

        logger.info(f"Discovered {len(discovered)} dynamic credential sources")
        return discovered

    def _categorize_credential(self, name: str, config: Dict[str, Any]) -> str:
        """Categorize credential type based on name and config"""
        name_lower = name.lower()

        if 'aws' in name_lower or 'access_key_id' in config:
            return 'aws'
        elif any(key in config for key in ['host', 'database', 'username', 'password']):
            return 'database'
        elif 'api_key' in config or 'token' in config:
            return 'api'
        elif self._is_llm_service(name, config):
            return 'llm_service'
        else:
            return 'generic'

    def _is_llm_service(self, name: str, config: Dict[str, Any]) -> bool:
        """Check if this is an LLM service configuration"""
        llm_indicators = [
            'bedrock', 'model', 'anthropic', 'claude', 'openai', 'gpt',
            'llm', 'ai', 'model_mapping', 'default_model'
        ]

        name_lower = name.lower()
        if any(indicator in name_lower for indicator in llm_indicators):
            return True

        # Check nested config for LLM indicators
        def check_nested_llm(obj, depth=0):
            if depth > 3:
                return False

            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = key.lower()
                    if any(indicator in key_lower for indicator in llm_indicators):
                        return True
                    if isinstance(value, dict):
                        if check_nested_llm(value, depth + 1):
                            return True
                    elif isinstance(value, str) and any(indicator in value.lower() for indicator in ['claude', 'anthropic', 'gpt']):
                        return True

            return False

        return check_nested_llm(config)

    def _has_credential_data(self, config: Dict[str, Any]) -> bool:
        """Check if config contains credential-like data"""
        credential_indicators = [
            'password', 'secret', 'key', 'token', 'credentials',
            'access_key', 'api_key', 'auth', 'username'
        ]

        def check_nested(obj, depth=0):
            if depth > 3:  # Prevent infinite recursion
                return False

            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = key.lower()
                    if any(indicator in key_lower for indicator in credential_indicators):
                        return True
                    if isinstance(value, dict):
                        if check_nested(value, depth + 1):
                            return True

            return False

        return check_nested(config)


class DynamicCredentialCarrier:
    """
    Dynamic Resource Carrier for credentials following the Resource Carrier Pattern.

    REVOLUTIONARY FEATURES:
    - Auto-discovers ALL credential sources in settings.yaml
    - No hardcoded credential types
    - Supports unlimited databases, services, integrations
    - Dynamic adaptation to settings.yaml changes
    """

    def __init__(self, settings_loader=None):
        """Initialize dynamic credential carrier"""
        self._settings_loader = settings_loader
        self._discovery = DynamicCredentialDiscovery(settings_loader)
        self._cached_credentials = {}
        self._credential_sources = {}
        self._discovered_sources = {}
        self._backup_enabled = True
        self._backup_path = Path("infrastructure/dynamic_credential_backup.parquet")

        # Resilient pool management
        self._pool_managers = {}  # Multiple pool managers for different databases

        # Load all credentials dynamically
        self._load_all_credentials()

    def _load_all_credentials(self):
        """Load credentials from ALL discovered sources"""
        logger.info("Loading credentials from all discovered sources...")

        # 1. Discover all sources dynamically
        self._discovered_sources = self._discovery.discover_all_credential_sources()

        # 2. Load from each discovered source
        for source_id, source_info in self._discovered_sources.items():
            try:
                self._load_from_source(source_id, source_info)
            except Exception as e:
                logger.warning(f"Failed to load from {source_id}: {e}")

        # 3. Load from environment variables (override anything)
        self._load_from_environment()

        # 4. Load from AWS IAM roles (where applicable)
        self._load_from_aws_sources()

        # 5. Backup current state
        if self._backup_enabled:
            self._backup_credentials()

    def _load_from_source(self, source_id: str, source_info: Dict[str, Any]):
        """Load credentials from a specific discovered source"""
        config = source_info['config']
        category = source_info['category']
        source_type = source_info['type']

        # Process based on category
        if category == 'aws':
            self._process_aws_credentials(source_id, config)
        elif category == 'database':
            self._process_database_credentials(source_id, config)
        elif category == 'api':
            self._process_api_credentials(source_id, config)
        elif category == 'llm_service':
            self._process_llm_service_credentials(source_id, config)
        else:
            self._process_generic_credentials(source_id, config)

        logger.debug(f"Loaded {source_type} credentials from {source_id}")

    def _process_aws_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process AWS-type credentials"""
        aws_creds = {}

        if 'access_key_id' in config:
            aws_creds['access_key_id'] = config['access_key_id']
        if 'secret_access_key' in config:
            aws_creds['secret_access_key'] = config['secret_access_key']
        if 'default_region' in config:
            aws_creds['region'] = config['default_region']
        elif 'region' in config:
            aws_creds['region'] = config['region']

        if aws_creds:
            self._cached_credentials[source_id] = aws_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_database_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process database-type credentials"""
        db_creds = {}

        for key in ['host', 'port', 'database', 'username', 'password', 'ssl_mode']:
            if key in config:
                db_creds[key] = config[key]

        if db_creds:
            self._cached_credentials[source_id] = db_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_api_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process API-type credentials"""
        api_creds = {}

        for key, value in config.items():
            if any(indicator in key.lower() for indicator in ['key', 'token', 'secret']):
                api_creds[key] = value

        if api_creds:
            self._cached_credentials[source_id] = api_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_llm_service_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process LLM service credentials and configurations"""
        llm_config = {}

        # Extract Bedrock-specific configurations
        if 'bedrock' in config:
            bedrock_config = config['bedrock']
            llm_config['service_type'] = 'bedrock'
            llm_config['default_model'] = bedrock_config.get('default_model')
            llm_config['model_mapping'] = bedrock_config.get('model_mapping', {})
            llm_config['adapter_config'] = bedrock_config.get('adapter_config', {})
            llm_config['region'] = config.get('region', 'us-east-1')

        # Extract any model configurations
        for key, value in config.items():
            if 'model' in key.lower():
                llm_config[key] = value

        # Store the complete config along with processed LLM data
        llm_config['full_config'] = config

        if llm_config:
            self._cached_credentials[source_id] = llm_config
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_generic_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process generic credentials"""
        # Store the entire config for generic types
        self._cached_credentials[source_id] = config
        self._credential_sources[source_id] = 'settings.yaml'

    def _load_from_environment(self):
        """Load/override credentials from environment variables"""
        # This can override any discovered credential
        env_overrides = {}

        # Common environment variable patterns
        env_patterns = {
            'AWS_ACCESS_KEY_ID': ('aws', 'access_key_id'),
            'AWS_SECRET_ACCESS_KEY': ('aws', 'secret_access_key'),
            'AWS_DEFAULT_REGION': ('aws', 'region'),
            'DB_HOST': ('database', 'host'),
            'DB_PORT': ('database', 'port'),
            'DB_NAME': ('database', 'database'),
            'DB_USERNAME': ('database', 'username'),
            'DB_PASSWORD': ('database', 'password'),
        }

        for env_var, (cred_type, cred_key) in env_patterns.items():
            value = os.getenv(env_var)
            if value:
                # Find matching sources to override
                for source_id in self._cached_credentials:
                    if cred_type in source_id or self._is_compatible_source(source_id, cred_type):
                        if source_id not in self._cached_credentials:
                            self._cached_credentials[source_id] = {}
                        self._cached_credentials[source_id][cred_key] = value
                        self._credential_sources[source_id] = 'environment'

    def _load_from_aws_sources(self):
        """Load from AWS IAM roles where applicable"""
        try:
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()

            if credentials:
                # Find AWS-compatible sources
                for source_id in self._cached_credentials:
                    if 'aws' in source_id.lower() and self._credential_sources.get(source_id) not in ['settings.yaml', 'environment']:
                        self._cached_credentials[source_id] = {
                            'access_key_id': credentials.access_key,
                            'secret_access_key': credentials.secret_key,
                            'session_token': credentials.token,
                            'region': session.region_name or 'us-east-1'
                        }
                        self._credential_sources[source_id] = 'iam_role'
        except Exception as e:
            logger.debug(f"No AWS IAM role credentials available: {e}")

    def _is_compatible_source(self, source_id: str, cred_type: str) -> bool:
        """Check if source is compatible with credential type"""
        source_info = self._discovered_sources.get(source_id, {})
        category = source_info.get('category', '')
        return category == cred_type

    def _backup_credentials(self):
        """Backup current credentials to parquet"""
        try:
            if not self._cached_credentials:
                return

            # Prepare backup data with dynamic columns
            backup_data = {'timestamp': [datetime.now().isoformat()]}

            for source_id, creds in self._cached_credentials.items():
                backup_data[f"{source_id}_credentials"] = [str(creds)]

            backup_data['credential_sources'] = [str(self._credential_sources)]
            backup_data['discovered_sources'] = [str(list(self._discovered_sources.keys()))]

            # Create backup directory if needed
            self._backup_path.parent.mkdir(exist_ok=True)

            # Save to parquet
            df = pd.DataFrame(backup_data)
            df.to_parquet(self._backup_path, index=False)

            logger.debug(f"Dynamic credentials backed up to {self._backup_path}")

        except Exception as e:
            logger.warning(f"Could not backup dynamic credentials: {e}")

    # Dynamic API methods
    def get_credentials_by_type(self, cred_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all credentials of a specific type"""
        matching_creds = {}

        for source_id, source_info in self._discovered_sources.items():
            if source_info.get('category') == cred_type:
                creds = self._cached_credentials.get(source_id, {})
                if creds:
                    matching_creds[source_id] = creds

        return matching_creds

    def get_credentials_by_name(self, name: str) -> Dict[str, Any]:
        """Get credentials by source name"""
        # Try exact match first
        for source_id in self._cached_credentials:
            if name in source_id:
                return self._cached_credentials[source_id]

        return {}

    def get_all_discovered_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered credential sources"""
        return self._discovered_sources.copy()

    def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all discovered credentials"""
        status = {}

        for source_id, source_info in self._discovered_sources.items():
            creds = self._cached_credentials.get(source_id, {})
            source = self._credential_sources.get(source_id, 'none')

            status[source_id] = {
                'type': source_info.get('type'),
                'category': source_info.get('category'),
                'available': bool(creds),
                'valid': self._validate_credentials(source_id, creds),
                'source': source,
                'last_updated': datetime.now().isoformat()
            }

        return status

    def _validate_credentials(self, source_id: str, creds: Dict[str, Any]) -> bool:
        """Validate if credentials are complete"""
        if not creds:
            return False

        source_info = self._discovered_sources.get(source_id, {})
        category = source_info.get('category', '')

        if category == 'aws':
            return bool(creds.get('access_key_id'))
        elif category == 'database':
            return bool(creds.get('host') and creds.get('password'))
        elif category == 'llm_service':
            return bool(creds.get('service_type') and creds.get('default_model'))
        else:
            return True  # Generic credentials are valid if present

    # LLM-Specific Convenience Methods
    def get_bedrock_configuration(self) -> Dict[str, Any]:
        """Get Bedrock LLM configuration"""
        llm_services = self.get_credentials_by_type('llm_service')

        for source_id, config in llm_services.items():
            if config.get('service_type') == 'bedrock':
                return {
                    'default_model': config.get('default_model'),
                    'model_mapping': config.get('model_mapping', {}),
                    'adapter_config': config.get('adapter_config', {}),
                    'region': config.get('region', 'us-east-1'),
                    'source': source_id
                }

        return {}

    def get_available_models(self) -> Dict[str, str]:
        """Get all available LLM models from configuration"""
        bedrock_config = self.get_bedrock_configuration()
        return bedrock_config.get('model_mapping', {})

    def get_default_model(self) -> str:
        """Get the default LLM model"""
        bedrock_config = self.get_bedrock_configuration()
        return bedrock_config.get('default_model', '')

    def get_llm_adapter_config(self) -> Dict[str, Any]:
        """Get LLM adapter configuration"""
        bedrock_config = self.get_bedrock_configuration()
        return bedrock_config.get('adapter_config', {})

    def refresh_credentials(self, source_name: str = None) -> bool:
        """Refresh credentials from all or specific sources"""
        try:
            if source_name:
                # Clear specific source
                sources_to_clear = [sid for sid in self._cached_credentials if source_name in sid]
                for sid in sources_to_clear:
                    self._cached_credentials.pop(sid, None)
                    self._credential_sources.pop(sid, None)
            else:
                # Clear all
                self._cached_credentials.clear()
                self._credential_sources.clear()

            # Reload all
            self._load_all_credentials()
            return True

        except Exception as e:
            logger.error(f"Failed to refresh dynamic credentials: {e}")
            return False


# Global instance
_dynamic_credential_carrier = None

def get_dynamic_credential_carrier() -> DynamicCredentialCarrier:
    """Get the global dynamic credential carrier instance"""
    global _dynamic_credential_carrier
    if _dynamic_credential_carrier is None:
        _dynamic_credential_carrier = DynamicCredentialCarrier()
    return _dynamic_credential_carrier

def reset_dynamic_credential_carrier():
    """Reset the global dynamic credential carrier"""
    global _dynamic_credential_carrier
    _dynamic_credential_carrier = None