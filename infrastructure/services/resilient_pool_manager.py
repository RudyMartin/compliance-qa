"""
Resilient Pool Manager
=====================
Infrastructure service implementing resilient database connection pooling.

Solves the "single pool hang" problem by providing:
- Primary pool for normal operations
- Backup pool for failover when primary hangs
- Automatic load balancing and health monitoring
- Integration with Resource Carrier Pattern

Part of the Resource Carrier Pattern for managing shared infrastructure resources.
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class PoolMetrics:
    """Metrics for pool monitoring"""
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"  # healthy, degraded, unhealthy


class PoolException(Exception):
    """Base exception for pool operations"""
    pass


class PoolTimeoutException(PoolException):
    """Pool timeout exception"""
    pass


class PoolHungException(PoolException):
    """Pool appears to be hung"""
    pass


class ResilientPoolManager:
    """
    Resilient database connection pool manager.

    Implements the Resource Carrier Pattern for database connections with:
    - Primary/backup pool failover
    - Health monitoring and automatic recovery
    - Load balancing between healthy pools
    - Transparent failover for applications
    """

    def __init__(self, credential_carrier=None):
        """Initialize resilient pool manager"""
        self._credential_carrier = credential_carrier
        self._primary_pool = None
        self._backup_pool = None
        self._failover_pool = None

        # Pool management
        self._active_pool = "primary"
        self._pool_metrics = {
            "primary": PoolMetrics(),
            "backup": PoolMetrics(),
            "failover": PoolMetrics()
        }

        # Configuration
        self._health_check_interval = 30  # seconds
        self._timeout_threshold = 10  # seconds
        self._max_retries = 3
        self._failover_threshold = 3  # failed requests before failover

        # Thread safety
        self._lock = threading.RLock()
        self._last_health_check = {}

        # Health monitoring
        self._start_health_monitoring()

    def _get_pool_instance(self, pool_name: str):
        """Get or create a pool instance"""
        try:
            if pool_name == "primary" and not self._primary_pool:
                self._primary_pool = self._create_pool("primary")
            elif pool_name == "backup" and not self._backup_pool:
                self._backup_pool = self._create_pool("backup")
            elif pool_name == "failover" and not self._failover_pool:
                self._failover_pool = self._create_pool("failover")

            pools = {
                "primary": self._primary_pool,
                "backup": self._backup_pool,
                "failover": self._failover_pool
            }

            return pools.get(pool_name)

        except Exception as e:
            logger.error(f"Failed to create {pool_name} pool: {e}")
            return None

    def _create_pool(self, pool_name: str):
        """Create a new connection pool instance"""
        try:
            # Try to use the existing TidyLLM connection pool
            try:
                from packages.tidyllm.infrastructure.connection_pool import TidyLLMConnectionPool

                # Get PostgreSQL config from credential carrier
                if self._credential_carrier:
                    db_creds = self._credential_carrier.get_database_credentials()
                    if not db_creds:
                        raise Exception("No database credentials available")

                    pg_config = {
                        "host": db_creds["host"],
                        "port": db_creds["port"],
                        "database": db_creds["database"],
                        "username": db_creds["username"],
                        "password": db_creds["password"],
                        # Pool-specific settings
                        "min_connections": 2 if pool_name == "primary" else 1,
                        "max_connections": 10 if pool_name == "primary" else 5,
                        "timeout": self._timeout_threshold
                    }
                else:
                    raise Exception("No credential carrier available")

                return TidyLLMConnectionPool(pg_config)

            except ImportError:
                logger.warning("TidyLLM connection pool not available, using fallback")
                return self._create_fallback_pool(pool_name)

        except Exception as e:
            logger.error(f"Failed to create {pool_name} pool: {e}")
            return None

    def _create_fallback_pool(self, pool_name: str):
        """Create fallback connection pool using infrastructure delegate"""
        try:
            # Use infrastructure delegate for connection management
            from ..infra_delegate import get_infra_delegate

            infra = get_infra_delegate()

            # Create a simple pool wrapper using infra delegate
            class DelegatePool:
                def __init__(self, infra_delegate, pool_name):
                    self.infra = infra_delegate
                    self.pool_name = pool_name
                    self.connections = []
                    self.min_conn = 2 if pool_name == "primary" else 1
                    self.max_conn = 10 if pool_name == "primary" else 5

                def getconn(self):
                    """Get connection from infra delegate"""
                    conn = self.infra.get_db_connection()
                    if conn:
                        self.connections.append(conn)
                        return conn
                    raise PoolException("No connection available from infrastructure")

                def putconn(self, conn):
                    """Return connection to infra delegate"""
                    if conn in self.connections:
                        self.connections.remove(conn)
                    self.infra.return_db_connection(conn)

                def closeall(self):
                    """Close all connections"""
                    for conn in self.connections[:]:
                        self.putconn(conn)
                    self.connections.clear()

            pool = DelegatePool(infra, pool_name)
            logger.info(f"Created fallback {pool_name} pool using infrastructure delegate")
            return pool

        except Exception as e:
            logger.error(f"Failed to create fallback {pool_name} pool: {e}")
            raise

    @contextmanager
    def get_connection(self, timeout: int = None):
        """
        Get a database connection with automatic failover.

        Context manager that provides resilient database connections:
        1. Try primary pool first
        2. Failover to backup pool if primary fails
        3. Create emergency failover pool if needed
        4. Update metrics and health status
        """
        timeout = timeout or self._timeout_threshold
        connection = None
        pool_used = None
        start_time = time.time()

        try:
            # Try pools in order of preference
            for pool_name in self._get_pool_priority():
                try:
                    pool = self._get_pool_instance(pool_name)
                    if not pool:
                        continue

                    # Test pool health first
                    if not self._is_pool_healthy(pool_name):
                        logger.warning(f"{pool_name} pool unhealthy, skipping")
                        continue

                    # Get connection from pool
                    connection = self._get_connection_from_pool(pool, timeout)
                    if connection:
                        pool_used = pool_name
                        self._update_metrics(pool_name, "success", time.time() - start_time)
                        break

                except (PoolTimeoutException, PoolHungException) as e:
                    logger.warning(f"{pool_name} pool failed: {e}")
                    self._update_metrics(pool_name, "failure", time.time() - start_time)
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error with {pool_name} pool: {e}")
                    self._update_metrics(pool_name, "error", time.time() - start_time)
                    continue

            if not connection:
                raise PoolException("All pools exhausted - no connections available")

            logger.debug(f"Connection obtained from {pool_used} pool")
            yield connection

        except Exception as e:
            logger.error(f"Connection management error: {e}")
            raise

        finally:
            # Return connection to pool
            if connection and pool_used:
                try:
                    pool = self._get_pool_instance(pool_used)
                    if pool:
                        self._return_connection_to_pool(pool, connection)
                except Exception as e:
                    logger.error(f"Failed to return connection to {pool_used} pool: {e}")

    def _get_pool_priority(self) -> list:
        """Get list of pools in order of preference"""
        # Prioritize healthy pools
        healthy_pools = []
        degraded_pools = []

        for pool_name in ["primary", "backup", "failover"]:
            metrics = self._pool_metrics[pool_name]
            if metrics.health_status == "healthy":
                healthy_pools.append(pool_name)
            elif metrics.health_status == "degraded":
                degraded_pools.append(pool_name)

        return healthy_pools + degraded_pools + ["primary", "backup", "failover"]

    def _get_connection_from_pool(self, pool, timeout: int):
        """Get connection from specific pool with timeout"""
        try:
            if hasattr(pool, 'getconn'):
                # psycopg2 pool interface (preferred)
                return pool.getconn()
            elif hasattr(pool, 'get_connection'):
                # TidyLLM pool interface - try with timeout, fallback without
                try:
                    return pool.get_connection(timeout=timeout)
                except TypeError:
                    # Method doesn't accept timeout parameter
                    return pool.get_connection()
            else:
                raise PoolException(f"Unknown pool interface: {type(pool)}")

        except Exception as e:
            if "timeout" in str(e).lower():
                raise PoolTimeoutException(f"Pool timeout: {e}")
            else:
                raise PoolHungException(f"Pool appears hung: {e}")

    def _return_connection_to_pool(self, pool, connection):
        """Return connection to specific pool"""
        try:
            if hasattr(pool, 'return_connection'):
                # TidyLLM pool interface
                pool.return_connection(connection)
            elif hasattr(pool, 'putconn'):
                # psycopg2 pool interface
                pool.putconn(connection)
            else:
                logger.warning(f"Unknown pool interface for return: {type(pool)}")

        except Exception as e:
            logger.error(f"Failed to return connection: {e}")

    def getconn(self, timeout: int = None):
        """
        Get a raw database connection (psycopg2 pool interface).

        This method provides compatibility with code expecting psycopg2 pool interface.
        It extracts the raw connection from our context manager.

        Returns:
            Raw database connection
        """
        timeout = timeout or self._timeout_threshold
        start_time = time.time()

        # Try pools in order of preference
        for pool_name in self._get_pool_priority():
            try:
                pool = self._get_pool_instance(pool_name)
                if not pool:
                    continue

                # Test pool health first
                if not self._is_pool_healthy(pool_name):
                    logger.warning(f"{pool_name} pool unhealthy, skipping")
                    continue

                # Get connection from pool
                connection = self._get_connection_from_pool(pool, timeout)
                if connection:
                    self._update_metrics(pool_name, "success", time.time() - start_time)

                    # Track which pool this connection came from for putconn
                    if not hasattr(self, '_connection_pool_map'):
                        self._connection_pool_map = {}
                    self._connection_pool_map[id(connection)] = (pool_name, pool)

                    logger.debug(f"Connection obtained from {pool_name} pool via getconn")
                    return connection

            except (PoolTimeoutException, PoolHungException) as e:
                logger.warning(f"{pool_name} pool failed: {e}")
                self._update_metrics(pool_name, "failure", time.time() - start_time)
                continue
            except Exception as e:
                logger.error(f"Unexpected error with {pool_name} pool: {e}")
                self._update_metrics(pool_name, "error", time.time() - start_time)
                continue

        raise PoolException("All pools exhausted - no connections available")

    def putconn(self, connection):
        """
        Return a connection to the pool (psycopg2 pool interface).

        This method provides compatibility with code expecting psycopg2 pool interface.

        Args:
            connection: The connection to return
        """
        if connection is None:
            return

        # Find which pool this connection came from
        if hasattr(self, '_connection_pool_map') and id(connection) in self._connection_pool_map:
            pool_name, pool = self._connection_pool_map.pop(id(connection))
            try:
                self._return_connection_to_pool(pool, connection)
                logger.debug(f"Connection returned to {pool_name} pool via putconn")
            except Exception as e:
                logger.error(f"Failed to return connection to {pool_name} pool: {e}")
        else:
            logger.warning("Connection not tracked, attempting to return to primary pool")
            # Try to return to primary pool as fallback
            try:
                pool = self._get_pool_instance("primary")
                if pool:
                    self._return_connection_to_pool(pool, connection)
            except Exception as e:
                logger.error(f"Failed to return untracked connection: {e}")

    def _is_pool_healthy(self, pool_name: str) -> bool:
        """Check if pool is healthy"""
        metrics = self._pool_metrics[pool_name]

        # Check if recent health check passed
        if metrics.last_health_check:
            age = datetime.now() - metrics.last_health_check
            if age < timedelta(seconds=self._health_check_interval):
                return metrics.health_status in ["healthy", "degraded"]

        # Perform health check
        return self._perform_health_check(pool_name)

    def _perform_health_check(self, pool_name: str) -> bool:
        """Perform health check on specific pool"""
        try:
            pool = self._get_pool_instance(pool_name)
            if not pool:
                self._pool_metrics[pool_name].health_status = "unhealthy"
                return False

            # Quick connection test
            start_time = time.time()
            try:
                with self._get_connection_from_pool(pool, timeout=5) as conn:
                    # Simple query test
                    if hasattr(conn, 'execute'):
                        conn.execute("SELECT 1")
                    elif hasattr(conn, 'cursor'):
                        with conn.cursor() as cur:
                            cur.execute("SELECT 1")

                # Update metrics
                response_time = time.time() - start_time
                metrics = self._pool_metrics[pool_name]
                metrics.last_health_check = datetime.now()
                metrics.avg_response_time = response_time

                if response_time < 1.0:
                    metrics.health_status = "healthy"
                elif response_time < 5.0:
                    metrics.health_status = "degraded"
                else:
                    metrics.health_status = "unhealthy"

                logger.debug(f"{pool_name} pool health check: {metrics.health_status} ({response_time:.2f}s)")
                return metrics.health_status != "unhealthy"

            except Exception as e:
                logger.warning(f"{pool_name} pool health check failed: {e}")
                self._pool_metrics[pool_name].health_status = "unhealthy"
                return False

        except Exception as e:
            logger.error(f"Health check error for {pool_name}: {e}")
            self._pool_metrics[pool_name].health_status = "unhealthy"
            return False

    def _update_metrics(self, pool_name: str, result: str, response_time: float):
        """Update pool metrics"""
        with self._lock:
            metrics = self._pool_metrics[pool_name]
            metrics.total_requests += 1

            if result == "failure" or result == "error":
                metrics.failed_requests += 1

            # Update average response time
            if metrics.avg_response_time == 0:
                metrics.avg_response_time = response_time
            else:
                metrics.avg_response_time = (metrics.avg_response_time * 0.8) + (response_time * 0.2)

    def _start_health_monitoring(self):
        """Start background health monitoring"""
        def health_monitor():
            while True:
                try:
                    for pool_name in ["primary", "backup", "failover"]:
                        if self._get_pool_instance(pool_name):
                            self._perform_health_check(pool_name)

                    time.sleep(self._health_check_interval)

                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(self._health_check_interval)

        monitor_thread = threading.Thread(target=health_monitor, daemon=True)
        monitor_thread.start()
        logger.info("Started resilient pool health monitoring")

    def get_pool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all pools"""
        status = {}

        for pool_name, metrics in self._pool_metrics.items():
            pool = self._get_pool_instance(pool_name)
            status[pool_name] = {
                "available": pool is not None,
                "health_status": metrics.health_status,
                "active_connections": metrics.active_connections,
                "total_requests": metrics.total_requests,
                "failed_requests": metrics.failed_requests,
                "success_rate": (metrics.total_requests - metrics.failed_requests) / max(metrics.total_requests, 1) * 100,
                "avg_response_time": metrics.avg_response_time,
                "last_health_check": metrics.last_health_check.isoformat() if metrics.last_health_check else None
            }

        return status

    def force_failover(self, from_pool: str, to_pool: str = None):
        """Force failover from one pool to another"""
        with self._lock:
            logger.warning(f"Forcing failover from {from_pool} pool")

            # Mark source pool as unhealthy
            self._pool_metrics[from_pool].health_status = "unhealthy"

            # If target pool specified, try to ensure it's healthy
            if to_pool:
                self._perform_health_check(to_pool)

            logger.info(f"Failover completed: {from_pool} -> {to_pool or 'auto'}")

    def close_all_pools(self):
        """Close all connection pools"""
        for pool_name in ["primary", "backup", "failover"]:
            try:
                pool = self._get_pool_instance(pool_name)
                if pool:
                    if hasattr(pool, 'close_all'):
                        pool.close_all()
                    elif hasattr(pool, 'closeall'):
                        pool.closeall()
                    logger.info(f"Closed {pool_name} pool")
            except Exception as e:
                logger.error(f"Failed to close {pool_name} pool: {e}")


# Global instance for shared use (Resource Carrier Pattern)
_resilient_pool_manager = None


def get_resilient_pool_manager(credential_carrier=None) -> ResilientPoolManager:
    """Get the global resilient pool manager instance"""
    global _resilient_pool_manager
    if _resilient_pool_manager is None:
        _resilient_pool_manager = ResilientPoolManager(credential_carrier)
    return _resilient_pool_manager


def reset_resilient_pool_manager():
    """Reset the global pool manager (useful for testing)"""
    global _resilient_pool_manager
    if _resilient_pool_manager:
        _resilient_pool_manager.close_all_pools()
    _resilient_pool_manager = None