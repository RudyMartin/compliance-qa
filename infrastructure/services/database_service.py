"""
Unified Database Service - Parent Infrastructure
================================================
Manages ALL database connections including postgres_std and postgres_mlflow.
Uses the existing ResilientPoolManager for connection pooling.
"""

import os
import logging
from typing import Dict, Any, Optional, Union, List
from contextlib import contextmanager
from enum import Enum

logger = logging.getLogger(__name__)

# Import the existing pool manager
try:
    from .resilient_pool_manager import ResilientPoolManager
    POOL_MANAGER_AVAILABLE = True
except ImportError:
    POOL_MANAGER_AVAILABLE = False
    logger.warning("ResilientPoolManager not available")

# Conditional database imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    from sqlalchemy import create_engine, text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class DatabaseType(Enum):
    """Available database types."""
    POSTGRES_STD = "postgres_std"      # Standard PostgreSQL for application data
    POSTGRES_MLFLOW = "postgres_mlflow" # PostgreSQL for MLflow tracking
    POSTGRES_VECTOR = "postgres_vector" # PostgreSQL with pgvector for embeddings


class DatabaseService:
    """
    Unified database service for the entire infrastructure.
    Manages multiple database connections with pooling.
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialize database service with configuration."""
        self.config = config or {}

        # Pool managers for each database type
        self._pool_managers = {}

        # SQLAlchemy engines (for compatibility)
        self._engines = {}

        # Database configurations
        self._db_configs = self._load_database_configs()

        # Initialize pools
        self._initialize_pools()

    def _load_database_configs(self) -> Dict[str, Dict]:
        """Load database configurations from config or environment."""
        configs = {}

        # Standard PostgreSQL configuration
        configs[DatabaseType.POSTGRES_STD] = {
            'host': self.config.get('postgres_host', os.getenv('POSTGRES_HOST', 'localhost')),
            'port': int(self.config.get('postgres_port', os.getenv('POSTGRES_PORT', '5432'))),
            'database': self.config.get('postgres_database', os.getenv('POSTGRES_DATABASE', 'tidyllm_db')),
            'username': self.config.get('postgres_username', os.getenv('POSTGRES_USERNAME', 'tidyllm_user')),
            'password': self.config.get('postgres_password', os.getenv('POSTGRES_PASSWORD', '')),
            'ssl_mode': self.config.get('postgres_ssl_mode', os.getenv('POSTGRES_SSL_MODE', 'prefer'))
        }

        # MLflow PostgreSQL configuration
        configs[DatabaseType.POSTGRES_MLFLOW] = {
            'host': self.config.get('mlflow_postgres_host',
                                   os.getenv('MLFLOW_POSTGRES_HOST', configs[DatabaseType.POSTGRES_STD]['host'])),
            'port': int(self.config.get('mlflow_postgres_port',
                                       os.getenv('MLFLOW_POSTGRES_PORT', configs[DatabaseType.POSTGRES_STD]['port']))),
            'database': self.config.get('mlflow_postgres_database',
                                       os.getenv('MLFLOW_POSTGRES_DATABASE', 'mlflow_db')),
            'username': self.config.get('mlflow_postgres_username',
                                       os.getenv('MLFLOW_POSTGRES_USERNAME', configs[DatabaseType.POSTGRES_STD]['username'])),
            'password': self.config.get('mlflow_postgres_password',
                                       os.getenv('MLFLOW_POSTGRES_PASSWORD', configs[DatabaseType.POSTGRES_STD]['password'])),
            'ssl_mode': self.config.get('mlflow_postgres_ssl_mode',
                                       os.getenv('MLFLOW_POSTGRES_SSL_MODE', configs[DatabaseType.POSTGRES_STD]['ssl_mode']))
        }

        # Vector database configuration (pgvector)
        configs[DatabaseType.POSTGRES_VECTOR] = {
            'host': self.config.get('vector_postgres_host',
                                   os.getenv('VECTOR_POSTGRES_HOST', configs[DatabaseType.POSTGRES_STD]['host'])),
            'port': int(self.config.get('vector_postgres_port',
                                       os.getenv('VECTOR_POSTGRES_PORT', configs[DatabaseType.POSTGRES_STD]['port']))),
            'database': self.config.get('vector_postgres_database',
                                       os.getenv('VECTOR_POSTGRES_DATABASE', 'vector_db')),
            'username': self.config.get('vector_postgres_username',
                                       os.getenv('VECTOR_POSTGRES_USERNAME', configs[DatabaseType.POSTGRES_STD]['username'])),
            'password': self.config.get('vector_postgres_password',
                                       os.getenv('VECTOR_POSTGRES_PASSWORD', configs[DatabaseType.POSTGRES_STD]['password'])),
            'ssl_mode': self.config.get('vector_postgres_ssl_mode',
                                       os.getenv('VECTOR_POSTGRES_SSL_MODE', configs[DatabaseType.POSTGRES_STD]['ssl_mode']))
        }

        return configs

    def _initialize_pools(self):
        """Initialize connection pools for each database."""
        if not POOL_MANAGER_AVAILABLE:
            logger.warning("Pool manager not available - pooling disabled")
            return

        for db_type, db_config in self._db_configs.items():
            if self._is_database_configured(db_config):
                try:
                    # Create a credential carrier for this specific database
                    credential_carrier = self._create_credential_carrier(db_config)

                    # Create pool manager
                    pool_manager = ResilientPoolManager(credential_carrier)
                    self._pool_managers[db_type] = pool_manager

                    logger.info(f"Initialized pool for {db_type.value}")
                except Exception as e:
                    logger.warning(f"Could not initialize pool for {db_type.value}: {e}")

    def _is_database_configured(self, db_config: Dict) -> bool:
        """Check if database configuration is complete."""
        required = ['host', 'database', 'username', 'password']
        return all(db_config.get(key) for key in required)

    def _create_credential_carrier(self, db_config: Dict):
        """Create a credential carrier for the pool manager."""
        # Simple credential carrier for the pool manager
        class SimpleCredentialCarrier:
            def __init__(self, config):
                self.config = config

            def get_database_credentials(self):
                return self.config

        return SimpleCredentialCarrier(db_config)

    def get_connection_string(self, db_type: DatabaseType = DatabaseType.POSTGRES_STD) -> str:
        """Get connection string for a database."""
        db_config = self._db_configs.get(db_type)
        if not db_config:
            raise ValueError(f"No configuration for {db_type.value}")

        return (
            f"postgresql://{db_config['username']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            f"?sslmode={db_config['ssl_mode']}"
        )

    def get_mlflow_tracking_uri(self) -> str:
        """Get MLflow tracking URI using postgres_mlflow."""
        return self.get_connection_string(DatabaseType.POSTGRES_MLFLOW)

    @contextmanager
    def get_connection(self, db_type: DatabaseType = DatabaseType.POSTGRES_STD):
        """
        Get a database connection from the pool.

        Args:
            db_type: Which database to connect to

        Yields:
            Database connection object
        """
        pool_manager = self._pool_managers.get(db_type)

        if pool_manager:
            # Use the resilient pool manager
            with pool_manager.get_connection() as conn:
                yield conn
        elif PSYCOPG2_AVAILABLE:
            # Fallback to direct connection
            conn_string = self.get_connection_string(db_type)
            conn = psycopg2.connect(conn_string)
            try:
                yield conn
            finally:
                conn.close()
        else:
            raise RuntimeError(f"No connection available for {db_type.value}")

    def get_engine(self, db_type: DatabaseType = DatabaseType.POSTGRES_STD):
        """
        Get SQLAlchemy engine for a database (compatibility layer).

        Args:
            db_type: Which database to connect to

        Returns:
            SQLAlchemy engine
        """
        if not SQLALCHEMY_AVAILABLE:
            raise RuntimeError("SQLAlchemy not available")

        if db_type not in self._engines:
            conn_string = self.get_connection_string(db_type)
            self._engines[db_type] = create_engine(
                conn_string,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )

        return self._engines[db_type]

    def execute_query(self,
                     query: str,
                     params: Optional[Dict] = None,
                     db_type: DatabaseType = DatabaseType.POSTGRES_STD,
                     fetch: bool = True) -> Optional[List[Dict]]:
        """
        Execute a query on a database.

        Args:
            query: SQL query to execute
            params: Query parameters
            db_type: Which database to query
            fetch: Whether to fetch results

        Returns:
            Query results if fetch=True, None otherwise
        """
        with self.get_connection(db_type) as conn:
            with conn.cursor(cursor_factory=RealDictCursor if PSYCOPG2_AVAILABLE else None) as cursor:
                cursor.execute(query, params)

                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return None

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all databases."""
        health = {
            'databases': {}
        }

        for db_type in DatabaseType:
            try:
                # Try to connect and run simple query
                with self.get_connection(db_type) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        health['databases'][db_type.value] = {
                            'status': 'healthy',
                            'pool_available': db_type in self._pool_managers
                        }
            except Exception as e:
                health['databases'][db_type.value] = {
                    'status': 'error',
                    'message': str(e),
                    'pool_available': db_type in self._pool_managers
                }

        return health

    def close_all(self):
        """Close all connections and pools."""
        # Close pool managers
        for pool_manager in self._pool_managers.values():
            try:
                pool_manager.shutdown()
            except:
                pass

        # Dispose engines
        for engine in self._engines.values():
            try:
                engine.dispose()
            except:
                pass


# Singleton instance
_database_service = None

def get_database_service(config: Optional[Dict] = None) -> DatabaseService:
    """
    Get the singleton database service instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        DatabaseService instance
    """
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService(config)
    return _database_service

def inject_database_config(config: Dict):
    """
    Inject database configuration for child packages.

    This is called by child packages like TidyLLM to set up databases.
    """
    global _database_service
    _database_service = DatabaseService(config)
    return _database_service