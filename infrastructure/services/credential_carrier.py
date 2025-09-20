"""
Credential Carrier Service
========================
Resource Carrier Pattern implementation for credential management.

Handles multiple credential sources:
- settings.yaml (primary)
- environment variables (runtime)
- AWS IAM roles (dynamic)
- backup parquet files (emergency)
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class CredentialCarrier:
    """
    Resource carrier for credentials following the Resource Carrier Pattern.

    Manages credential lifecycle:
    1. Load from multiple sources (priority order)
    2. Cache credentials in memory
    3. Backup to parquet for emergency recovery
    4. Provide consistent interface to adapters
    """

    def __init__(self, settings_loader=None):
        """Initialize credential carrier with settings loader"""
        self._settings_loader = settings_loader
        self._cached_credentials = {}
        self._credential_sources = {}
        self._backup_enabled = True
        self._backup_path = Path("infrastructure/credential_backup.parquet")

        # Resilient pool management
        self._pool_manager = None

        # Load credentials from all sources
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from multiple sources in priority order"""
        logger.info("Loading credentials from multiple sources...")

        # 1. Try settings.yaml first (highest priority)
        self._load_from_settings()

        # 2. Try environment variables (runtime overrides)
        self._load_from_environment()

        # 3. Try AWS IAM role (dynamic credentials)
        self._load_from_aws_role()

        # 4. Try backup parquet (emergency fallback)
        self._load_from_backup()

        # 5. Backup current state
        if self._backup_enabled:
            self._backup_credentials()

    def _load_from_settings(self):
        """Load credentials from settings.yaml"""
        try:
            if not self._settings_loader:
                from infrastructure.yaml_loader import get_settings_loader
                self._settings_loader = get_settings_loader()

            # Use the settings loader's methods to get properly parsed configs
            aws_config = self._settings_loader.get_aws_config()
            if aws_config.get('access_key_id'):
                self._cached_credentials['aws'] = {
                    'access_key_id': aws_config['access_key_id'],
                    'secret_access_key': aws_config['secret_access_key'],
                    'region': aws_config['region']
                }
                self._credential_sources['aws'] = 'settings.yaml'
                logger.info("AWS credentials loaded from settings.yaml")

            # Database credentials
            db_config = self._settings_loader.get_database_config()
            if db_config.get('host') and db_config.get('password'):
                self._cached_credentials['database'] = {
                    'host': db_config['host'],
                    'port': db_config['port'],
                    'database': db_config['database'],
                    'username': db_config['username'],
                    'password': db_config['password']
                }
                self._credential_sources['database'] = 'settings.yaml'
                logger.info("Database credentials loaded from settings.yaml")

        except Exception as e:
            logger.warning(f"Could not load credentials from settings.yaml: {e}")

    def _load_from_environment(self):
        """Load/override credentials from environment variables"""
        try:
            # AWS environment variables
            aws_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

            if aws_key:
                if 'aws' not in self._cached_credentials:
                    self._cached_credentials['aws'] = {}

                self._cached_credentials['aws'].update({
                    'access_key_id': aws_key,
                    'secret_access_key': aws_secret or '',
                    'region': aws_region
                })
                self._credential_sources['aws'] = 'environment'
                logger.info("AWS credentials loaded/updated from environment")

            # Database environment variables
            db_host = os.getenv('DB_HOST')
            db_password = os.getenv('DB_PASSWORD')

            if db_host:
                if 'database' not in self._cached_credentials:
                    self._cached_credentials['database'] = {}

                self._cached_credentials['database'].update({
                    'host': db_host,
                    'port': int(os.getenv('DB_PORT', 5432)),
                    'database': os.getenv('DB_NAME', ''),
                    'username': os.getenv('DB_USERNAME', ''),
                    'password': db_password or ''
                })
                self._credential_sources['database'] = 'environment'
                logger.info("Database credentials loaded/updated from environment")

        except Exception as e:
            logger.warning(f"Could not load credentials from environment: {e}")

    def _load_from_aws_role(self):
        """Load credentials from AWS IAM role (if available)"""
        try:
            # Try to get credentials from IAM role
            import boto3
            session = boto3.Session()
            credentials = session.get_credentials()

            if credentials:
                if 'aws' not in self._cached_credentials:
                    self._cached_credentials['aws'] = {}

                # Only override if no explicit credentials set
                if self._credential_sources.get('aws') not in ['settings.yaml', 'environment']:
                    self._cached_credentials['aws'].update({
                        'access_key_id': credentials.access_key,
                        'secret_access_key': credentials.secret_key,
                        'session_token': credentials.token,
                        'region': session.region_name or 'us-east-1'
                    })
                    self._credential_sources['aws'] = 'iam_role'
                    logger.info("AWS credentials loaded from IAM role")

        except Exception as e:
            logger.debug(f"No AWS IAM role credentials available: {e}")

    def _load_from_backup(self):
        """Load credentials from backup parquet file (emergency)"""
        try:
            if self._backup_path.exists():
                df = pd.read_parquet(self._backup_path)

                # Only use backup if no other credentials found
                if not self._cached_credentials:
                    backup_data = df.to_dict('records')[0] if len(df) > 0 else {}

                    for service in ['aws', 'database']:
                        service_data = backup_data.get(f'{service}_credentials')
                        if service_data:
                            self._cached_credentials[service] = eval(service_data)
                            self._credential_sources[service] = 'backup_parquet'

                    logger.warning("Credentials loaded from backup parquet (emergency mode)")

        except Exception as e:
            logger.debug(f"No backup credentials available: {e}")

    def _backup_credentials(self):
        """Backup current credentials to parquet for emergency recovery"""
        try:
            if not self._cached_credentials:
                return

            # Prepare backup data
            backup_data = {
                'timestamp': [datetime.now().isoformat()],
                'aws_credentials': [str(self._cached_credentials.get('aws', {}))],
                'database_credentials': [str(self._cached_credentials.get('database', {}))],
                'credential_sources': [str(self._credential_sources)]
            }

            # Create backup directory if needed
            self._backup_path.parent.mkdir(exist_ok=True)

            # Save to parquet
            df = pd.DataFrame(backup_data)
            df.to_parquet(self._backup_path, index=False)

            logger.debug(f"Credentials backed up to {self._backup_path}")

        except Exception as e:
            logger.warning(f"Could not backup credentials: {e}")

    def get_aws_credentials(self) -> Dict[str, str]:
        """Get AWS credentials"""
        creds = self._cached_credentials.get('aws', {})
        if not creds.get('access_key_id'):
            logger.warning("No AWS credentials available")
            return {}

        logger.debug(f"Providing AWS credentials from source: {self._credential_sources.get('aws', 'unknown')}")
        return creds

    def get_database_credentials(self) -> Dict[str, Any]:
        """Get database credentials"""
        creds = self._cached_credentials.get('database', {})
        if not creds.get('host'):
            logger.warning("No database credentials available")
            return {}

        logger.debug(f"Providing database credentials from source: {self._credential_sources.get('database', 'unknown')}")
        return creds

    def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all credentials with sources"""
        status = {}

        for service in ['aws', 'database']:
            creds = self._cached_credentials.get(service, {})
            source = self._credential_sources.get(service, 'none')

            # Check if credentials are present and valid
            if service == 'aws':
                valid = bool(creds.get('access_key_id'))
            else:  # database
                valid = bool(creds.get('host') and creds.get('password'))

            status[service] = {
                'available': bool(creds),
                'valid': valid,
                'source': source,
                'last_updated': datetime.now().isoformat()
            }

        return status

    def refresh_credentials(self, service: str = None) -> bool:
        """Refresh credentials from all sources"""
        try:
            logger.info(f"Refreshing credentials for service: {service or 'all'}")

            if service:
                # Clear specific service credentials
                self._cached_credentials.pop(service, None)
                self._credential_sources.pop(service, None)
            else:
                # Clear all credentials
                self._cached_credentials.clear()
                self._credential_sources.clear()

            # Reload from all sources
            self._load_credentials()

            return True

        except Exception as e:
            logger.error(f"Failed to refresh credentials: {e}")
            return False

    def set_environment_from_credentials(self):
        """Set environment variables from cached credentials (for legacy compatibility)"""
        try:
            # Set AWS environment variables
            aws_creds = self.get_aws_credentials()
            if aws_creds:
                os.environ['AWS_ACCESS_KEY_ID'] = aws_creds.get('access_key_id', '')
                os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds.get('secret_access_key', '')
                os.environ['AWS_DEFAULT_REGION'] = aws_creds.get('region', 'us-east-1')

            # Set database environment variables
            db_creds = self.get_database_credentials()
            if db_creds:
                os.environ['DB_HOST'] = str(db_creds.get('host', ''))
                os.environ['DB_PORT'] = str(db_creds.get('port', 5432))
                os.environ['DB_NAME'] = str(db_creds.get('database', ''))
                os.environ['DB_USERNAME'] = str(db_creds.get('username', ''))
                os.environ['DB_PASSWORD'] = str(db_creds.get('password', ''))

            logger.info("Environment variables set from credential carrier")
            return True

        except Exception as e:
            logger.error(f"Failed to set environment variables: {e}")
            return False

    def get_resilient_database_connection(self, timeout: int = None):
        """Get a resilient database connection with automatic failover"""
        if not self._pool_manager:
            from .resilient_pool_manager import get_resilient_pool_manager
            self._pool_manager = get_resilient_pool_manager(credential_carrier=self)

        return self._pool_manager.get_connection(timeout=timeout)

    def get_pool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all connection pools"""
        if not self._pool_manager:
            return {"error": "Pool manager not initialized"}

        return self._pool_manager.get_pool_status()

    def force_pool_failover(self, from_pool: str, to_pool: str = None):
        """Force failover from one pool to another"""
        if not self._pool_manager:
            logger.warning("Pool manager not initialized for failover")
            return

        self._pool_manager.force_failover(from_pool, to_pool)


# Global instance for shared use
_credential_carrier = None


def get_credential_carrier() -> CredentialCarrier:
    """Get the global credential carrier instance"""
    global _credential_carrier
    if _credential_carrier is None:
        _credential_carrier = CredentialCarrier()
    return _credential_carrier


def reset_credential_carrier():
    """Reset the global credential carrier (useful for testing)"""
    global _credential_carrier
    _credential_carrier = None


def sync_active_credential_state() -> Dict[str, Any]:
    """
    Infrastructure service to sync active credential state from all sources.

    Returns:
        Dict with sync results and status information
    """
    try:
        # Reset and reload to force fresh sync
        reset_credential_carrier()
        credential_carrier = get_credential_carrier()

        # Force refresh of all credentials from all sources
        refresh_success = credential_carrier.refresh_credentials()

        if not refresh_success:
            return {
                "success": False,
                "error": "Failed to refresh credentials",
                "status": {}
            }

        # Ensure environment variables are set for legacy compatibility
        env_success = credential_carrier.set_environment_from_credentials()

        # Get status after sync
        status = credential_carrier.get_credential_status()

        # Check backup creation
        from pathlib import Path
        backup_path = Path("infrastructure/credential_backup.parquet")
        backup_exists = backup_path.exists()

        return {
            "success": env_success and any(info.get('valid', False) for info in status.values()),
            "status": status,
            "environment_vars_set": env_success,
            "backup_created": backup_exists,
            "backup_path": str(backup_path) if backup_exists else None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": {}
        }