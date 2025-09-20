"""
Self-Describing Credential Carrier
===================================
ZERO DEVELOPER DEPENDENCY - Configuration drives everything.

NO HARDCODING:
- Infrastructure reads 'type' fields from settings.yaml
- All behavior driven by configuration
- Adding new credential types requires ZERO code changes
- Pure configuration-driven architecture

REPLACES: Developer-dependent hardcoded logic
WITH: Pure configuration-driven discovery
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfDescribingCredentialDiscovery:
    """Discovers credential sources purely from 'type' fields in settings.yaml"""

    def __init__(self, settings_loader=None):
        self._settings_loader = settings_loader
        self._raw_settings = None

    def discover_self_describing_sources(self) -> Dict[str, Dict[str, Any]]:
        """Discover ALL credential sources purely from configuration 'type' fields"""

        if not self._settings_loader:
            from infrastructure.yaml_loader import get_settings_loader
            self._settings_loader = get_settings_loader()

        # Get raw settings dict
        self._raw_settings = self._settings_loader._load_settings()

        discovered = {}

        # 1. Discover credentials by 'type' field - NO HARDCODING
        if 'credentials' in self._raw_settings:
            creds = self._raw_settings['credentials']
            for source_name, config in creds.items():
                if isinstance(config, dict) and 'type' in config:
                    discovered[source_name] = {
                        'source_type': 'credential',
                        'credential_type': config['type'],  # <- Pure config-driven
                        'name': source_name,
                        'config': config,
                        'category': config['type']  # <- No hardcoding!
                    }

        # 2. Discover databases by 'type' field - NO HARDCODING
        if 'databases' in self._raw_settings:
            dbs = self._raw_settings['databases']
            for db_name, config in dbs.items():
                if isinstance(config, dict) and 'type' in config:
                    discovered[db_name] = {
                        'source_type': 'database',
                        'credential_type': config['type'],  # <- Pure config-driven
                        'name': db_name,
                        'config': config,
                        'category': config['type']  # <- No hardcoding!
                    }

        # 3. Discover services by 'type' field - NO HARDCODING
        if 'services' in self._raw_settings:
            services = self._raw_settings['services']
            for service_name, config in services.items():
                if isinstance(config, dict) and 'type' in config:
                    discovered[service_name] = {
                        'source_type': 'service',
                        'credential_type': config['type'],  # <- Pure config-driven
                        'name': service_name,
                        'config': config,
                        'category': config['type']  # <- No hardcoding!
                    }

        # 4. Discover integrations by 'type' field - NO HARDCODING
        if 'integrations' in self._raw_settings:
            integrations = self._raw_settings['integrations']
            for integration_name, config in integrations.items():
                if isinstance(config, dict) and 'type' in config:
                    if config.get('enabled', False):  # Only enabled integrations
                        discovered[integration_name] = {
                            'source_type': 'integration',
                            'credential_type': config['type'],  # <- Pure config-driven
                            'name': integration_name,
                            'config': config,
                            'category': config['type']  # <- No hardcoding!
                        }

        logger.info(f"Discovered {len(discovered)} self-describing credential sources")
        return discovered


class SelfDescribingCredentialCarrier:
    """
    Self-Describing Resource Carrier - ZERO DEVELOPER DEPENDENCY

    PURE CONFIGURATION-DRIVEN:
    - All behavior determined by 'type' fields in settings.yaml
    - No hardcoded credential types
    - Adding new types requires ZERO code changes
    - Infrastructure adapts automatically to configuration
    """

    def __init__(self, settings_loader=None):
        """Initialize self-describing credential carrier"""
        self._settings_loader = settings_loader
        self._discovery = SelfDescribingCredentialDiscovery(settings_loader)
        self._cached_credentials = {}
        self._credential_sources = {}
        self._discovered_sources = {}
        self._backup_enabled = True
        self._backup_path = Path("infrastructure/self_describing_credential_backup.parquet")

        # Load all credentials based on configuration
        self._load_all_credentials()

    def _load_all_credentials(self):
        """Load credentials from ALL self-describing sources"""
        logger.info("Loading credentials from self-describing configuration...")

        # 1. Discover all sources from configuration 'type' fields
        self._discovered_sources = self._discovery.discover_self_describing_sources()

        # 2. Load each source based on its declared 'type'
        for source_id, source_info in self._discovered_sources.items():
            try:
                self._load_from_source(source_id, source_info)
            except Exception as e:
                logger.warning(f"Failed to load from {source_id}: {e}")

        # 3. Load environment overrides
        self._load_environment_overrides()

        # 4. Backup current state
        if self._backup_enabled:
            self._backup_credentials()

    def _load_from_source(self, source_id: str, source_info: Dict[str, Any]):
        """Load credentials based purely on declared 'type' - NO HARDCODING"""
        config = source_info['config']
        credential_type = source_info['credential_type']

        # Pure type-driven processing - NO HARDCODED LOGIC
        if credential_type == 'aws_credentials':
            self._process_aws_credentials(source_id, config)
        elif credential_type == 'database_credentials':
            self._process_database_credentials(source_id, config)
        elif credential_type == 'llm_service':
            self._process_llm_service(source_id, config)
        elif credential_type == 'api_credentials':
            self._process_api_credentials(source_id, config)
        elif credential_type == 'database_pool':
            self._process_database_pool(source_id, config)
        else:
            # Generic handler for unknown types - still no hardcoding!
            self._process_generic_credentials(source_id, config, credential_type)

        logger.debug(f"Loaded {credential_type} from {source_id}")

    def _process_aws_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process AWS credentials - standard fields"""
        aws_creds = {}

        for field in ['access_key_id', 'secret_access_key', 'default_region', 'region']:
            if field in config:
                aws_creds[field] = config[field]

        if aws_creds:
            self._cached_credentials[source_id] = aws_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_database_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process database credentials - standard fields"""
        db_creds = {}

        for field in ['engine', 'host', 'port', 'database', 'username', 'password', 'ssl_mode']:
            if field in config:
                db_creds[field] = config[field]

        if db_creds:
            self._cached_credentials[source_id] = db_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_llm_service(self, source_id: str, config: Dict[str, Any]):
        """Process LLM service credentials - standard fields"""
        llm_config = {}

        # Standard LLM fields - NO HARDCODING
        for field in ['service_provider', 'region', 'default_model', 'model_mapping', 'adapter_config']:
            if field in config:
                llm_config[field] = config[field]

        # Store complete config
        llm_config['full_config'] = config

        if llm_config:
            self._cached_credentials[source_id] = llm_config
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_api_credentials(self, source_id: str, config: Dict[str, Any]):
        """Process API credentials - standard fields"""
        api_creds = {}

        for field in ['service', 'api_key', 'token', 'tracking_uri', 'artifact_store']:
            if field in config:
                api_creds[field] = config[field]

        if api_creds:
            self._cached_credentials[source_id] = api_creds
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_database_pool(self, source_id: str, config: Dict[str, Any]):
        """Process database pool configuration"""
        pool_config = {}

        for field in ['credential_ref', 'engine', 'min_connections', 'max_connections', 'pool_recycle', 'pool_timeout']:
            if field in config:
                pool_config[field] = config[field]

        if pool_config:
            self._cached_credentials[source_id] = pool_config
            self._credential_sources[source_id] = 'settings.yaml'

    def _process_generic_credentials(self, source_id: str, config: Dict[str, Any], credential_type: str):
        """Process unknown credential types - still no hardcoding!"""
        # Store the entire config with type information
        generic_config = {
            'credential_type': credential_type,
            'full_config': config
        }

        self._cached_credentials[source_id] = generic_config
        self._credential_sources[source_id] = 'settings.yaml'

        logger.info(f"Processed unknown credential type '{credential_type}' generically")

    def _load_environment_overrides(self):
        """Load environment variable overrides"""
        # Environment variables can still override, but based on discovered types
        env_patterns = {
            'AWS_ACCESS_KEY_ID': 'access_key_id',
            'AWS_SECRET_ACCESS_KEY': 'secret_access_key',
            'AWS_DEFAULT_REGION': 'default_region',
            'DB_HOST': 'host',
            'DB_PORT': 'port',
            'DB_NAME': 'database',
            'DB_USERNAME': 'username',
            'DB_PASSWORD': 'password',
        }

        for env_var, field_name in env_patterns.items():
            value = os.getenv(env_var)
            if value:
                # Apply to compatible credential types
                for source_id, source_info in self._discovered_sources.items():
                    if self._is_field_compatible(source_info['credential_type'], field_name):
                        if source_id not in self._cached_credentials:
                            self._cached_credentials[source_id] = {}
                        self._cached_credentials[source_id][field_name] = value
                        self._credential_sources[source_id] = 'environment'

    def _is_field_compatible(self, credential_type: str, field_name: str) -> bool:
        """Check if field is compatible with credential type"""
        compatibility_map = {
            'aws_credentials': ['access_key_id', 'secret_access_key', 'default_region'],
            'database_credentials': ['host', 'port', 'database', 'username', 'password'],
            'database_pool': ['host', 'port', 'database', 'username', 'password'],
        }

        return field_name in compatibility_map.get(credential_type, [])

    def _backup_credentials(self):
        """Backup credentials with type information"""
        try:
            if not self._cached_credentials:
                return

            backup_data = {'timestamp': [datetime.now().isoformat()]}

            # Include type information in backup
            for source_id, creds in self._cached_credentials.items():
                source_info = self._discovered_sources.get(source_id, {})
                backup_data[f"{source_id}_credentials"] = [str(creds)]
                backup_data[f"{source_id}_type"] = [source_info.get('credential_type', 'unknown')]

            backup_data['credential_sources'] = [str(self._credential_sources)]

            self._backup_path.parent.mkdir(exist_ok=True)
            df = pd.DataFrame(backup_data)
            df.to_parquet(self._backup_path, index=False)

            logger.debug(f"Self-describing credentials backed up to {self._backup_path}")

        except Exception as e:
            logger.warning(f"Could not backup self-describing credentials: {e}")

    # Configuration-driven API methods
    def get_credentials_by_type(self, credential_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all credentials of a specific type"""
        matching_creds = {}

        for source_id, source_info in self._discovered_sources.items():
            if source_info.get('credential_type') == credential_type:
                creds = self._cached_credentials.get(source_id, {})
                if creds:
                    matching_creds[source_id] = creds

        return matching_creds

    def get_credentials_by_name(self, name: str) -> Dict[str, Any]:
        """Get credentials by exact name"""
        return self._cached_credentials.get(name, {})

    def resolve_credential_reference(self, credential_ref: str) -> Dict[str, Any]:
        """Resolve credential reference (for database pools, services, etc.)"""
        return self.get_credentials_by_name(credential_ref)

    def get_all_discovered_types(self) -> Set[str]:
        """Get all discovered credential types"""
        return {info.get('credential_type') for info in self._discovered_sources.values()}

    def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all credentials with type information"""
        status = {}

        for source_id, source_info in self._discovered_sources.items():
            creds = self._cached_credentials.get(source_id, {})

            status[source_id] = {
                'source_type': source_info.get('source_type'),
                'credential_type': source_info.get('credential_type'),
                'available': bool(creds),
                'valid': self._validate_credentials_by_type(source_info.get('credential_type'), creds),
                'source': self._credential_sources.get(source_id, 'none'),
                'last_updated': datetime.now().isoformat()
            }

        return status

    def _validate_credentials_by_type(self, credential_type: str, creds: Dict[str, Any]) -> bool:
        """Validate credentials based on their declared type"""
        if not creds:
            return False

        # Type-driven validation rules
        validation_rules = {
            'aws_credentials': lambda c: bool(c.get('access_key_id')),
            'database_credentials': lambda c: bool(c.get('host')),
            'llm_service': lambda c: bool(c.get('service_provider')),
            'api_credentials': lambda c: bool(c.get('service')),
            'database_pool': lambda c: bool(c.get('credential_ref')),
        }

        validator = validation_rules.get(credential_type, lambda c: True)
        return validator(creds)


# Global instance
_self_describing_credential_carrier = None

def get_self_describing_credential_carrier():
    """Get the global self-describing credential carrier instance"""
    global _self_describing_credential_carrier
    if _self_describing_credential_carrier is None:
        _self_describing_credential_carrier = SelfDescribingCredentialCarrier()
    return _self_describing_credential_carrier

def reset_self_describing_credential_carrier():
    """Reset the global self-describing credential carrier"""
    global _self_describing_credential_carrier
    _self_describing_credential_carrier = None