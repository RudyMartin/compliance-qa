#!/usr/bin/env python3
"""
Unified Session Management System - MOVED TO ADAPTERS LAYER

Originally from tidyllm/infrastructure/session/unified.py
Now properly positioned in the 4-layer clean architecture as an adapter.

SOLUTION TO SCATTERED SESSION CHAOS:
------------------------------------
This consolidates ALL scattered session management across:
- S3 (3 different implementations found)
- PostgreSQL (multiple psycopg2 patterns)
- Bedrock (mixed credential approaches)

ONE SESSION MANAGER TO RULE THEM ALL - NO MORE GOING IN CIRCLES!

Features:
- Single credential discovery for all services
- Unified connection pooling and health checks
- Consistent error handling and fallback patterns
- Environment-based configuration with sane defaults
- Session sharing across all Streamlit demos
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import time

# Core AWS imports
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound
    from botocore.config import Config
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# PostgreSQL imports - now using infrastructure delegate
POSTGRES_AVAILABLE = True  # Always available through infra delegate

# Configuration imports
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

logger = logging.getLogger("unified_sessions")
logger.setLevel(logging.INFO)

class ServiceType(Enum):
    """Supported service types"""
    S3 = "s3"
    BEDROCK = "bedrock"
    POSTGRESQL = "postgresql"
    PROJECT_PATHS = "project_paths"

class CredentialSource(Enum):
    """Sources for credentials (ordered by security priority)"""
    IAM_ROLE = "iam_role"
    AWS_PROFILE = "aws_profile"
    ENVIRONMENT = "environment"
    SETTINGS_FILE = "settings_file"
    NOT_FOUND = "not_found"

@dataclass
class ServiceConfig:
    """Unified configuration for all services"""
    # S3 Configuration
    s3_region: str = "us-east-1"
    s3_default_bucket: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None

    # Bedrock Configuration
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # PostgreSQL Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "tidyllm_db"
    postgres_username: str = "postgres"
    postgres_password: Optional[str] = None
    postgres_pool_size: int = 10

    # AWS Profile
    aws_profile: Optional[str] = None

    # Project Path Configuration
    root_path: Optional[str] = None
    workflows_path: Optional[str] = None
    projects_path: Optional[str] = None

    # Credential source tracking
    credential_source: CredentialSource = CredentialSource.NOT_FOUND

@dataclass
class ConnectionHealth:
    """Health status for service connections"""
    service: ServiceType
    healthy: bool = False
    last_check: Optional[datetime] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class UnifiedSessionManager:
    """
    ONE SESSION MANAGER TO END THE CHAOS

    Consolidates all scattered session management patterns.
    Now properly positioned as an adapter in clean architecture.
    """

    def __init__(self, config: ServiceConfig = None):
        self.config = config or ServiceConfig()

        # Service clients
        self._s3_client = None
        self._s3_resource = None
        self._bedrock_client = None
        self._bedrock_runtime_client = None
        self._postgres_pool = None

        # Health tracking
        self.health_status: Dict[ServiceType, ConnectionHealth] = {
            ServiceType.S3: ConnectionHealth(ServiceType.S3),
            ServiceType.BEDROCK: ConnectionHealth(ServiceType.BEDROCK),
            ServiceType.POSTGRESQL: ConnectionHealth(ServiceType.POSTGRESQL),
            ServiceType.PROJECT_PATHS: ConnectionHealth(ServiceType.PROJECT_PATHS)
        }

        # Auto-discover credentials
        self._discover_credentials()

        # Initialize connections LAZILY - only when actually needed
        # self._initialize_connections()  # Disabled for performance

    def _discover_credentials(self):
        """Discover credentials from environment and settings"""
        # Check if we already have a fully configured setup
        if (self.config.postgres_password and
            self.config.postgres_host != "localhost" and
            self.config.s3_access_key_id):
            logger.info("[TARGET] Configuration already provided - skipping auto-discovery")
            return

        logger.info("[SEARCH] Discovering credentials for all services...")

        # Store original config values to avoid overwriting intentional settings
        original_postgres_host = self.config.postgres_host if self.config.postgres_host != "localhost" else None
        original_postgres_database = self.config.postgres_database if self.config.postgres_database != "tidyllm_db" else None
        original_postgres_username = self.config.postgres_username if self.config.postgres_username != "postgres" else None
        original_postgres_password = self.config.postgres_password

        # Load from environment first
        self._load_from_environment()

        # Load from settings file if available (now looks for qa-shipping config)
        self._load_from_settings()

        # Restore original config if it was intentionally set
        if original_postgres_host:
            self.config.postgres_host = original_postgres_host
        if original_postgres_database:
            self.config.postgres_database = original_postgres_database
        if original_postgres_username:
            self.config.postgres_username = original_postgres_username
        if original_postgres_password:
            self.config.postgres_password = original_postgres_password

        # Test IAM role availability
        self._test_iam_role()

        # Apply discovered credentials to environment for reuse
        self._apply_credentials_to_environment()

    def _apply_credentials_to_environment(self):
        """Apply discovered credentials to environment variables for reuse by other components"""
        # Only set environment variables if they're not already set
        if self.config.s3_access_key_id and not os.getenv('AWS_ACCESS_KEY_ID'):
            os.environ['AWS_ACCESS_KEY_ID'] = self.config.s3_access_key_id
            logger.info("[APPLIED] AWS_ACCESS_KEY_ID to environment")

        if self.config.s3_secret_access_key and not os.getenv('AWS_SECRET_ACCESS_KEY'):
            os.environ['AWS_SECRET_ACCESS_KEY'] = self.config.s3_secret_access_key
            logger.info("[APPLIED] AWS_SECRET_ACCESS_KEY to environment")

        if self.config.s3_region and not os.getenv('AWS_DEFAULT_REGION'):
            os.environ['AWS_DEFAULT_REGION'] = self.config.s3_region
            logger.info(f"[APPLIED] AWS_DEFAULT_REGION to environment: {self.config.s3_region}")

        if self.config.aws_profile and not os.getenv('AWS_PROFILE'):
            os.environ['AWS_PROFILE'] = self.config.aws_profile
            logger.info(f"[APPLIED] AWS_PROFILE to environment: {self.config.aws_profile}")

        # Apply PostgreSQL credentials
        if self.config.postgres_password and not os.getenv('POSTGRES_PASSWORD'):
            os.environ['POSTGRES_PASSWORD'] = self.config.postgres_password
            logger.info("[APPLIED] POSTGRES_PASSWORD to environment")

    def _load_from_environment(self):
        """Load credentials from environment variables"""
        # AWS credentials
        self.config.s3_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.config.s3_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.config.aws_profile = os.getenv('AWS_PROFILE')

        # PostgreSQL credentials
        postgres_password = os.getenv('POSTGRES_PASSWORD') or os.getenv('POSTGRESQL_PASSWORD')
        if postgres_password:
            self.config.postgres_password = postgres_password
            self.config.credential_source = CredentialSource.ENVIRONMENT
            logger.info("[OK] Found PostgreSQL password in environment")

        # Database URL override
        database_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRESQL_URL')
        if database_url:
            self._parse_database_url(database_url)

        if self.config.s3_access_key_id and self.config.s3_secret_access_key:
            self.config.credential_source = CredentialSource.ENVIRONMENT
            logger.info("[OK] Found AWS credentials in environment")

    def _load_from_settings(self):
        """Load from qa-shipping configuration system"""
        try:
            # Try to use qa-shipping environment manager
            from core.config.environment_manager import get_environment_manager
            env_manager = get_environment_manager()

            # Get database config
            db_config = env_manager.get_database_config()
            self.config.postgres_host = db_config.host
            self.config.postgres_port = db_config.port
            self.config.postgres_database = db_config.database
            self.config.postgres_username = db_config.username
            self.config.postgres_password = db_config.password

            # Get AWS config
            aws_config = env_manager.get_aws_config()
            self.config.s3_region = aws_config.region
            self.config.bedrock_region = aws_config.region
            self.config.s3_access_key_id = aws_config.access_key_id
            self.config.s3_secret_access_key = aws_config.secret_access_key
            self.config.aws_profile = aws_config.profile

            logger.info("[OK] Loaded configuration from qa-shipping environment manager")
            self.config.credential_source = CredentialSource.SETTINGS_FILE
            return

        except ImportError:
            logger.debug("qa-shipping environment manager not available, falling back to legacy settings")
        except Exception as e:
            logger.warning(f"Failed to load from qa-shipping environment manager: {e}")

        # Fallback to original settings loading
        self._load_from_settings_direct()

    def _test_iam_role(self):
        """Test if IAM role credentials are available"""
        if not AWS_AVAILABLE:
            return False

        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials and not credentials.access_key:
                # IAM role detected
                self.config.credential_source = CredentialSource.IAM_ROLE
                logger.info("[OK] Using IAM role credentials")
                return True
        except:
            pass
        return False

    def _parse_database_url(self, url: str):
        """Parse DATABASE_URL into components"""
        try:
            # Format: postgresql://username:password@host:port/database
            if url.startswith('postgresql://'):
                url = url.replace('postgresql://', '')
                if '@' in url:
                    auth, location = url.split('@', 1)
                    if ':' in auth:
                        self.config.postgres_username, self.config.postgres_password = auth.split(':', 1)

                    if '/' in location:
                        host_port, database = location.split('/', 1)
                        self.config.postgres_database = database.split('?')[0]  # Remove query params

                        if ':' in host_port:
                            self.config.postgres_host, port_str = host_port.split(':', 1)
                            self.config.postgres_port = int(port_str)
                        else:
                            self.config.postgres_host = host_port
        except Exception as e:
            logger.warning(f"[WARNING]  Could not parse DATABASE_URL: {e}")

    def _load_from_settings_direct(self):
        """Direct settings loading (legacy fallback)"""
        # Start from current directory and search upward for settings.yaml
        current_dir = Path.cwd()
        settings_file = None

        # Search up to 5 levels up from current directory
        for _ in range(5):
            potential_paths = [
                current_dir / "tidyllm" / "admin" / "settings.yaml",
                current_dir / "admin" / "settings.yaml",
                current_dir / "settings.yaml",
            ]

            for path in potential_paths:
                if path.exists():
                    settings_file = path
                    break

            if settings_file:
                break

            # Move up one directory
            parent = current_dir.parent
            if parent == current_dir:  # Reached root
                break
            current_dir = parent

        # If not found by searching up, settings file not available
        # (Removed legacy tidyllm fallback paths - not relevant to qa-shipping)

        if settings_file and settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = yaml.safe_load(f) if YAML_AVAILABLE else {}

                    # Dynamic AWS settings extraction - auto-detect all AWS fields
                    aws_config = settings.get('aws', {})

                    # Dynamically load any AWS-related fields
                    for key, value in aws_config.items():
                        if value:  # Only set non-empty values
                            # Map common variations to standardized config fields
                            if key in ['access_key_id', 'aws_access_key_id', 'access_key']:
                                self.config.s3_access_key_id = value
                            elif key in ['secret_access_key', 'aws_secret_access_key', 'secret_key']:
                                self.config.s3_secret_access_key = value
                            elif key in ['region', 'aws_region', 'default_region', 'aws_default_region']:
                                self.config.s3_region = value
                                self.config.bedrock_region = value
                            elif key in ['default_bucket', 's3_bucket', 'bucket']:
                                self.config.s3_default_bucket = value
                            elif key == 'bedrock':
                                # Handle nested bedrock config
                                if isinstance(value, dict):
                                    self.config.bedrock_region = value.get('region', self.config.bedrock_region)
                                    self.config.bedrock_model_id = value.get('default_model', self.config.bedrock_model_id)

                    # Also check api_keys section for AWS credentials (legacy support)
                    api_keys = settings.get('api_keys', {})
                    if not self.config.s3_access_key_id:
                        self.config.s3_access_key_id = api_keys.get('aws_access_key_id') or api_keys.get('access_key_id')
                    if not self.config.s3_secret_access_key:
                        self.config.s3_secret_access_key = api_keys.get('aws_secret_access_key') or api_keys.get('secret_access_key')

                    # Set credential source if we found credentials
                    if self.config.s3_access_key_id and self.config.s3_secret_access_key:
                        self.config.credential_source = CredentialSource.SETTINGS_FILE
                        logger.info("[OK] Loaded AWS credentials from settings file")

                    # Extract PostgreSQL settings - check multiple possible config sections
                    db_config = settings.get('postgres', {}) or settings.get('database', {}) or settings.get('postgresql', {})
                    if db_config:
                        self.config.postgres_host = db_config.get('host', self.config.postgres_host)
                        self.config.postgres_port = db_config.get('port', self.config.postgres_port)
                        # Handle both field name formats
                        self.config.postgres_database = db_config.get('db_name', db_config.get('database', self.config.postgres_database))
                        self.config.postgres_username = db_config.get('db_user', db_config.get('username', self.config.postgres_username))
                        password = db_config.get('db_password', db_config.get('password'))
                        if password:
                            self.config.postgres_password = password

                        logger.info(f"[OK] PostgreSQL config loaded: {self.config.postgres_host}:{self.config.postgres_port}/{self.config.postgres_database}")

                logger.info(f"[OK] Loaded settings from {settings_file}")
            except Exception as e:
                logger.warning(f"[WARNING]  Could not load settings from {settings_file}: {e}")

    def _initialize_connections(self):
        """Initialize all service connections"""
        logger.info("[LAUNCH] Initializing service connections...")

        # Initialize S3
        if AWS_AVAILABLE:
            self._init_s3()

        # Initialize Bedrock
        if AWS_AVAILABLE:
            self._init_bedrock()

        # Initialize PostgreSQL
        if POSTGRES_AVAILABLE and self.config.postgres_password:
            self._init_postgresql()

    def _init_s3(self):
        """Initialize S3 connection"""
        try:
            start_time = time.time()

            if self.config.credential_source == CredentialSource.IAM_ROLE:
                session = boto3.Session()
            elif self.config.credential_source in [CredentialSource.ENVIRONMENT, CredentialSource.SETTINGS_FILE]:
                # Use credentials from environment or settings file
                session = boto3.Session(
                    aws_access_key_id=self.config.s3_access_key_id,
                    aws_secret_access_key=self.config.s3_secret_access_key,
                    region_name=self.config.s3_region
                )
            else:
                # Try default profile
                session = boto3.Session(profile_name=self.config.aws_profile)

            self._s3_client = session.client('s3', region_name=self.config.s3_region)
            self._s3_resource = session.resource('s3', region_name=self.config.s3_region)

            # Test connection
            self._s3_client.list_buckets()

            latency = (time.time() - start_time) * 1000
            self.health_status[ServiceType.S3] = ConnectionHealth(
                service=ServiceType.S3,
                healthy=True,
                last_check=datetime.now(),
                latency_ms=latency
            )

            logger.info(f"[OK] S3 connection established ({latency:.1f}ms)")

        except Exception as e:
            self.health_status[ServiceType.S3] = ConnectionHealth(
                service=ServiceType.S3,
                healthy=False,
                last_check=datetime.now(),
                error=str(e)
            )
            logger.warning(f"[ERROR] S3 connection failed: {e}")

    def _init_bedrock(self):
        """Initialize Bedrock connection"""
        try:
            start_time = time.time()

            if self.config.credential_source == CredentialSource.IAM_ROLE:
                session = boto3.Session()
            elif self.config.credential_source in [CredentialSource.ENVIRONMENT, CredentialSource.SETTINGS_FILE]:
                # Use credentials from environment or settings file
                session = boto3.Session(
                    aws_access_key_id=self.config.s3_access_key_id,
                    aws_secret_access_key=self.config.s3_secret_access_key,
                    region_name=self.config.bedrock_region
                )
            else:
                session = boto3.Session(profile_name=self.config.aws_profile)

            # Create both bedrock and bedrock-runtime clients
            self._bedrock_client = session.client('bedrock', region_name=self.config.bedrock_region)
            self._bedrock_runtime_client = session.client('bedrock-runtime', region_name=self.config.bedrock_region)

            # Test with a simple list models call (lightweight)
            try:
                self._bedrock_client.list_foundation_models()
            except:
                pass  # May not have permissions, but client works

            latency = (time.time() - start_time) * 1000
            self.health_status[ServiceType.BEDROCK] = ConnectionHealth(
                service=ServiceType.BEDROCK,
                healthy=True,
                last_check=datetime.now(),
                latency_ms=latency
            )

            logger.info(f"[OK] Bedrock connection established ({latency:.1f}ms)")

        except Exception as e:
            self.health_status[ServiceType.BEDROCK] = ConnectionHealth(
                service=ServiceType.BEDROCK,
                healthy=False,
                last_check=datetime.now(),
                error=str(e)
            )
            logger.warning(f"[ERROR] Bedrock connection failed: {e}")

    def _init_postgresql(self):
        """Initialize PostgreSQL connection pool"""
        try:
            start_time = time.time()

            # Use infrastructure delegate instead of direct pool
            from infrastructure.infra_delegate import get_infra_delegate
            self._infra_delegate = get_infra_delegate()
            self._postgres_pool = None  # No longer using direct pool

            # Test connection
            conn = self._infra_delegate.get_db_connection()
            if not conn:
                raise Exception("No database connection available from infrastructure")
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()
            finally:
                self._infra_delegate.return_db_connection(conn)

            latency = (time.time() - start_time) * 1000
            self.health_status[ServiceType.POSTGRESQL] = ConnectionHealth(
                service=ServiceType.POSTGRESQL,
                healthy=True,
                last_check=datetime.now(),
                latency_ms=latency,
                metadata={"version": str(version) if version else "unknown"}
            )

            logger.info(f"[OK] PostgreSQL connection established ({latency:.1f}ms)")

        except Exception as e:
            self.health_status[ServiceType.POSTGRESQL] = ConnectionHealth(
                service=ServiceType.POSTGRESQL,
                healthy=False,
                last_check=datetime.now(),
                error=str(e)
            )
            logger.warning(f"[ERROR] PostgreSQL connection failed: {e}")

    # Service Client Access Methods
    def get_s3_client(self):
        """Get S3 client (thread-safe) - lazy initialization"""
        if self._s3_client is None:
            self._init_s3()
        return self._s3_client

    def get_s3_resource(self):
        """Get S3 resource (thread-safe)"""
        return self._s3_resource

    def get_bedrock_client(self):
        """Get Bedrock client (thread-safe) - lazy initialization"""
        if self._bedrock_client is None:
            self._init_bedrock()
        return self._bedrock_client

    def get_bedrock_runtime_client(self):
        """Get Bedrock Runtime client (thread-safe) - lazy initialization"""
        if self._bedrock_runtime_client is None:
            self._init_bedrock()
        return self._bedrock_runtime_client

    def get_postgres_connection(self):
        """Get PostgreSQL connection from infrastructure delegate"""
        if hasattr(self, '_infra_delegate'):
            return self._infra_delegate.get_db_connection()
        # Initialize if not already done
        from infrastructure.infra_delegate import get_infra_delegate
        self._infra_delegate = get_infra_delegate()
        return self._infra_delegate.get_db_connection()

    def return_postgres_connection(self, conn):
        """Return PostgreSQL connection to infrastructure delegate"""
        if hasattr(self, '_infra_delegate') and conn:
            self._infra_delegate.return_db_connection(conn)

    def test_connection(self, service: str = "all") -> Dict[str, Any]:
        """Test connections to specified services with detailed results."""
        results = {}

        if service in ["all", "s3"]:
            results["s3"] = self._test_s3_connection()

        if service in ["all", "bedrock"]:
            results["bedrock"] = self._test_bedrock_connection()

        if service in ["all", "postgres"]:
            results["postgres"] = self._test_postgres_connection()

        return results

    def _test_s3_connection(self) -> Dict[str, Any]:
        """Test S3 connection with timing and details."""
        start_time = time.time()

        try:
            s3_client = self.get_s3_client()
            response = s3_client.list_buckets()
            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": round(duration_ms, 1),
                "bucket_count": len(response.get("Buckets", [])),
                "message": f"S3 connected successfully ({duration_ms:.1f}ms)"
            }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "failed",
                "duration_ms": round(duration_ms, 1),
                "error": str(e),
                "message": f"S3 connection failed: {str(e)}"
            }

    def _test_bedrock_connection(self) -> Dict[str, Any]:
        """Test Bedrock connection with timing and details."""
        start_time = time.time()

        try:
            bedrock_client = self.get_bedrock_client()
            if bedrock_client is None:
                return {
                    "status": "no_client",
                    "duration_ms": 0,
                    "error": "Bedrock client not available",
                    "message": "Bedrock client not initialized - check AWS credentials"
                }
            # Test with a minimal model list call
            response = bedrock_client.list_foundation_models()
            duration_ms = (time.time() - start_time) * 1000

            return {
                "status": "success",
                "duration_ms": round(duration_ms, 1),
                "model_count": len(response.get("modelSummaries", [])),
                "message": f"Bedrock connected successfully ({duration_ms:.1f}ms)"
            }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_str = str(e)

            # Handle specific permission errors with helpful guidance
            if "AccessDeniedException" in error_str and "bedrock:ListFoundationModels" in error_str:
                return {
                    "status": "corporate_restricted",
                    "duration_ms": round(duration_ms, 1),
                    "error": error_str,
                    "message": "Bedrock connection: Corporate policy restricts ListFoundationModels",
                    "solution": "This is normal in corporate environments. Bedrock runtime access may still work.",
                    "corporate_mode": True
                }
            else:
                return {
                    "status": "failed",
                    "duration_ms": round(duration_ms, 1),
                    "error": error_str,
                    "message": f"Bedrock connection failed: {error_str}"
                }

    def _test_postgres_connection(self) -> Dict[str, Any]:
        """Test PostgreSQL connection with timing and details."""
        start_time = time.time()

        try:
            conn = self.get_postgres_connection()

            # Better error message if connection is None
            if conn is None:
                duration_ms = (time.time() - start_time) * 1000
                return {
                    "status": "failed",
                    "duration_ms": round(duration_ms, 1),
                    "error": "get_postgres_connection() returned None",
                    "message": "PostgreSQL connection failed: Connection pool not initialized or database credentials missing.",
                    "troubleshooting": [
                        "Set environment variables: DB_HOST, DB_PORT, DB_NAME, DB_USERNAME, DB_PASSWORD",
                        "Or configure via qa-shipping environment manager",
                        "Check if PostgreSQL server is running and accessible"
                    ]
                }

            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            self.return_postgres_connection(conn)

            duration_ms = (time.time() - start_time) * 1000
            return {
                "status": "success",
                "duration_ms": round(duration_ms, 1),
                "test_query": "SELECT 1",
                "result": result[0] if result else None,
                "message": f"PostgreSQL connected successfully ({duration_ms:.1f}ms)"
            }
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_message = str(e)

            return {
                "status": "failed",
                "duration_ms": round(duration_ms, 1),
                "error": error_message,
                "message": f"PostgreSQL connection failed: {error_message}"
            }

    def cleanup(self):
        """Clean up connections"""
        # Infrastructure delegate handles connection cleanup
        logger.info("[CLEANUP] Connections managed by infrastructure delegate")

# Global session manager instance
_global_session_manager = None

def get_global_session_manager() -> UnifiedSessionManager:
    """Get or create global session manager instance"""
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = UnifiedSessionManager()
    return _global_session_manager

def reset_global_session_manager():
    """Reset global session manager (for testing)"""
    global _global_session_manager
    if _global_session_manager:
        _global_session_manager.cleanup()
    _global_session_manager = None

# Convenience functions for demos
def get_s3_client():
    """Get S3 client from global session manager"""
    return get_global_session_manager().get_s3_client()

def get_bedrock_client():
    """Get Bedrock client from global session manager"""
    return get_global_session_manager().get_bedrock_client()

def get_postgres_connection():
    """Get PostgreSQL connection from global session manager"""
    return get_global_session_manager().get_postgres_connection()

def return_postgres_connection(conn):
    """Return PostgreSQL connection to global session manager"""
    return get_global_session_manager().return_postgres_connection(conn)

# Export the ServiceType enum for compatibility
__all__ = ['UnifiedSessionManager', 'ServiceType', 'CredentialSource', 'ServiceConfig',
           'ConnectionHealth', 'get_global_session_manager', 'reset_global_session_manager',
           'get_s3_client', 'get_bedrock_client', 'get_postgres_connection',
           'return_postgres_connection']

if __name__ == "__main__":
    # Demo the unified session manager
    print("TidyLLM Unified Session Manager Demo")
    print("=" * 50)

    # Create session manager
    session_mgr = UnifiedSessionManager()

    # Test connections
    print("Testing connections...")
    test_results = session_mgr.test_connection("all")
    for service, result in test_results.items():
        status_icon = "[OK]" if result.get("status") == "success" else "[FAIL]"
        print(f"{status_icon} {service}: {result.get('message', 'Unknown')}")

    # Cleanup
    session_mgr.cleanup()
    print("Demo complete!")