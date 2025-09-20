#!/usr/bin/env python3
"""
Enhanced MLflow Service with Backend Isolation
===============================================
Integrates with self-describing configuration system to provide:

1. Backend isolation using alternative database
2. Timeout protections for network calls
3. Proper fallback mechanisms
4. Configuration-driven setup
5. All required methods for system compatibility
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Set MLflow environment variables early to prevent network timeouts
os.environ['DISABLE_MLFLOW_TELEMETRY'] = '1'
os.environ['MLFLOW_TELEMETRY_OPT_OUT'] = '1'
os.environ['MLFLOW_TRACKING_TIMEOUT'] = '5'
os.environ['MLFLOW_HTTP_TIMEOUT'] = '10'
os.environ['REQUESTS_TIMEOUT'] = '10'

logger = logging.getLogger(__name__)

# Try to import MLflow with timeout protection
try:
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("MLflow import timeout")

    # Set timeout for MLflow import (Windows doesn't support signal.alarm)
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        import mlflow
        from mlflow.tracking import MlflowClient
        signal.alarm(0)  # Cancel timeout
        MLFLOW_AVAILABLE = True
        logger.info("✅ MLflow imported successfully with timeout protection")
    except (ImportError, TimeoutError) as e:
        signal.alarm(0)  # Cancel timeout
        MLFLOW_AVAILABLE = False
        logger.warning(f"⚠️ MLflow import failed or timed out: {e}")
except Exception as e:
    # Fallback for Windows or other systems without signal support
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        MLFLOW_AVAILABLE = True
        logger.info("✅ MLflow imported successfully (fallback method)")
    except ImportError as e:
        MLFLOW_AVAILABLE = False
        logger.warning(f"⚠️ MLflow not available: {e}")

@dataclass
class MLflowBackendConfig:
    """Configuration for MLflow backend selection"""
    primary: str = "postgresql_shared_pool"
    alternative: str = "mlflow_alt_db"
    fallback: str = "file://./mlflow_data"
    test_mode: str = "sqlite:///./test_mlflow.db"
    auto_select: bool = True
    s3_artifacts_only: bool = True
    test_backend_on_startup: bool = True
    backend_fallback_enabled: bool = True

class EnhancedMLflowService:
    """
    Enhanced MLflow service with backend isolation and configuration-driven setup.

    Features:
    - Self-describing configuration integration
    - Backend isolation (separate database)
    - Timeout protections
    - Proper fallback mechanisms
    - All required methods for system compatibility
    """

    def __init__(self, credential_carrier=None):
        """Initialize enhanced MLflow service"""
        self.credential_carrier = credential_carrier
        self.backend_config = None
        self.current_backend = None
        self.client = None
        self.is_connected = False
        self.last_error = None
        self.tracking_uri = None
        self.artifact_store = None

        # Load configuration from self-describing system
        self._load_configuration()

        # Initialize with backend selection
        self._initialize_with_backend_selection()

    def _load_configuration(self):
        """Load configuration from self-describing credential carrier"""
        if not self.credential_carrier:
            try:
                from infrastructure.services.self_describing_credential_carrier import get_self_describing_credential_carrier
                self.credential_carrier = get_self_describing_credential_carrier()
                logger.info("✅ Loaded self-describing credential carrier")
            except Exception as e:
                logger.warning(f"⚠️ Could not load credential carrier: {e}")
                self._use_fallback_config()
                return

        # Get MLflow service configuration
        try:
            # Check data_tracking service
            data_tracking_sources = self.credential_carrier._discovered_sources
            data_tracking = data_tracking_sources.get('data_tracking', {})
            mlflow_integration = data_tracking_sources.get('mlflow', {})

            if data_tracking:
                config = data_tracking.get('config', {})
                backend_options = config.get('backend_options', {})

                if backend_options:
                    self.backend_config = MLflowBackendConfig(
                        primary=backend_options.get('primary', 'postgresql_shared_pool'),
                        alternative=backend_options.get('alternative', 'mlflow_alt_db'),
                        fallback=backend_options.get('fallback', 'file://./mlflow_data'),
                        test_mode=backend_options.get('test_mode', 'sqlite:///./test_mlflow.db'),
                        s3_artifacts_only=backend_options.get('s3_artifacts_only', True)
                    )

                    self.tracking_uri = config.get('tracking_uri', 'http://localhost:5000')
                    self.artifact_store = config.get('artifact_store', 's3://nsc-mvp1/onboarding-test/mlflow/')

                    logger.info("✅ MLflow configuration loaded from self-describing system")
                else:
                    self._use_fallback_config()
            else:
                self._use_fallback_config()

        except Exception as e:
            logger.warning(f"⚠️ Failed to load MLflow configuration: {e}")
            self._use_fallback_config()

    def _use_fallback_config(self):
        """Use fallback configuration when self-describing config unavailable"""
        self.backend_config = MLflowBackendConfig()
        self.tracking_uri = 'http://localhost:5000'
        self.artifact_store = 's3://nsc-mvp1/onboarding-test/mlflow/'
        logger.info("📝 Using fallback MLflow configuration")

    def _initialize_with_backend_selection(self):
        """Initialize MLflow with backend selection logic"""
        if not MLFLOW_AVAILABLE:
            logger.warning("⚠️ MLflow not available - cannot initialize client")
            self.last_error = "MLflow library not installed or import timed out"
            return

        if not self.backend_config.auto_select:
            # Use configured backend directly
            backend_uri = self._get_configured_backend_uri()
            self._initialize_client_with_backend(backend_uri)
            return

        # Auto-select best available backend
        backends_to_try = [
            ('primary', self.backend_config.primary),
            ('alternative', self.backend_config.alternative),
            ('fallback', self.backend_config.fallback),
            ('test_mode', self.backend_config.test_mode)
        ]

        for backend_name, backend_id in backends_to_try:
            try:
                backend_uri = self._resolve_backend_uri(backend_id)
                if backend_uri and self._test_backend_connection(backend_uri):
                    self.current_backend = backend_name
                    self._initialize_client_with_backend(backend_uri)
                    logger.info(f"✅ MLflow initialized with {backend_name} backend: {backend_id}")
                    break
            except Exception as e:
                logger.warning(f"⚠️ Backend {backend_name} failed: {e}")
                continue
        else:
            logger.error("❌ All MLflow backends failed - service unavailable")
            self.last_error = "All configured backends unavailable"

    def _resolve_backend_uri(self, backend_id: str) -> Optional[str]:
        """Resolve backend ID to actual connection URI"""
        if backend_id.startswith(('postgresql://', 'sqlite://', 'file://')):
            return backend_id

        if backend_id == 'postgresql_shared_pool':
            # Use shared connection pool
            try:
                # Get PostgreSQL credentials from credential carrier
                pg_creds = self.credential_carrier.get_credentials_by_name('postgresql_primary')
                if pg_creds:
                    host = pg_creds.get('host')
                    port = pg_creds.get('port', 5432)
                    database = pg_creds.get('database')
                    username = pg_creds.get('username')
                    password = pg_creds.get('password')

                    return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            except Exception as e:
                logger.warning(f"⚠️ Could not resolve shared pool connection: {e}")
                return None

        elif backend_id == 'mlflow_alt_db':
            # Use alternative MLflow database
            try:
                alt_creds = self.credential_carrier.get_credentials_by_name('mlflow_alt_db')
                if alt_creds:
                    host = alt_creds.get('host')
                    port = alt_creds.get('port', 5432)
                    database = alt_creds.get('database')
                    username = alt_creds.get('username')
                    password = alt_creds.get('password')

                    return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            except Exception as e:
                logger.warning(f"⚠️ Could not resolve alternative database: {e}")
                return None

        # Unknown backend ID
        logger.warning(f"⚠️ Unknown backend ID: {backend_id}")
        return None

    def _test_backend_connection(self, backend_uri: str) -> bool:
        """Test if backend connection is working"""
        if not MLFLOW_AVAILABLE:
            return False

        try:
            # Create temporary client to test connection
            test_client = MlflowClient(tracking_uri=backend_uri)

            # Test with timeout
            start_time = time.time()
            experiments = test_client.search_experiments()
            test_time = time.time() - start_time

            if test_time > 10:  # More than 10 seconds is too slow
                logger.warning(f"⚠️ Backend test too slow: {test_time:.1f}s")
                return False

            logger.debug(f"✅ Backend test successful: {len(experiments) if experiments else 0} experiments found")
            return True

        except Exception as e:
            logger.debug(f"❌ Backend test failed: {e}")
            return False

    def _initialize_client_with_backend(self, backend_uri: str):
        """Initialize MLflow client with specific backend"""
        try:
            # CRITICAL: Set global MLflow tracking URI first
            # This is what MLflow needs to determine backend behavior
            import mlflow
            mlflow.set_tracking_uri(backend_uri)
            self.tracking_uri = backend_uri

            # Now create client - it will use the global tracking URI
            self.client = MlflowClient(tracking_uri=backend_uri)
            self.is_connected = True
            self.last_error = None
            logger.info(f"✅ MLflow client initialized with global tracking URI: {backend_uri}")
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            logger.error(f"❌ Failed to initialize MLflow client: {e}")

    def _get_configured_backend_uri(self) -> str:
        """Get configured backend URI (non-auto mode)"""
        # This would read from configuration which backend to use
        # For now, default to primary
        return self._resolve_backend_uri(self.backend_config.primary)

    # Required methods for system compatibility
    def log_llm_request(self, model: str, prompt: str, response: str,
                       processing_time: float, token_usage: Dict[str, Any] = None,
                       success: bool = True, **kwargs) -> bool:
        """
        Log LLM request/response for tracking and monitoring.
        """
        if not self.is_available():
            logger.debug("MLflow not available, skipping request logging")
            return False

        try:
            # Create experiment if needed
            experiment_name = kwargs.get('experiment_name', 'llm_requests')

            try:
                experiment = self.client.get_experiment_by_name(experiment_name)
                if not experiment:
                    experiment_id = self.client.create_experiment(experiment_name)
                else:
                    experiment_id = experiment.experiment_id
            except Exception as e:
                logger.warning(f"⚠️ Could not create/get experiment: {e}")
                experiment_id = "0"  # Default experiment

            # Start run and log metrics
            with mlflow.start_run(experiment_id=experiment_id):
                # Log parameters
                mlflow.log_param("model", model)
                mlflow.log_param("prompt_length", len(prompt))
                mlflow.log_param("response_length", len(response))
                mlflow.log_param("success", success)

                # Log metrics
                mlflow.log_metric("processing_time_ms", processing_time)

                if token_usage:
                    mlflow.log_metric("input_tokens", token_usage.get("input", 0))
                    mlflow.log_metric("output_tokens", token_usage.get("output", 0))
                    mlflow.log_metric("total_tokens", token_usage.get("total", 0))

                # Log additional metadata
                for key, value in kwargs.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(key, value)
                    else:
                        mlflow.log_param(key, str(value))

                logger.debug(f"✅ Logged LLM request: {model} ({processing_time:.1f}ms)")
                return True

        except Exception as e:
            logger.warning(f"⚠️ Failed to log LLM request to MLflow: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on MLflow service"""
        connection_ok = self._test_backend_connection(self.tracking_uri) if self.client else False

        return {
            "service": "enhanced_mlflow",
            "healthy": connection_ok,
            "mlflow_available": MLFLOW_AVAILABLE,
            "connected": self.is_connected,
            "current_backend": self.current_backend,
            "tracking_uri": self.tracking_uri,
            "artifact_store": self.artifact_store,
            "last_error": self.last_error,
            "backend_isolation": True
        }

    def is_available(self) -> bool:
        """Check if service is available for use"""
        return MLFLOW_AVAILABLE and self.is_connected and self.client is not None

    def get_status(self) -> str:
        """Get human-readable status"""
        if not MLFLOW_AVAILABLE:
            return "MLflow not installed or import timed out"
        elif self.is_connected:
            return f"Connected to {self.current_backend} backend via {self.tracking_uri}"
        else:
            return f"Disconnected: {self.last_error or 'Unknown error'}"

    def reconnect(self) -> bool:
        """Attempt to reconnect to MLflow"""
        logger.info("🔄 Attempting to reconnect to MLflow...")
        self._initialize_with_backend_selection()
        return self.is_connected

    def switch_backend(self, backend_id: str) -> bool:
        """Switch to a different backend"""
        logger.info(f"🔄 Switching to backend: {backend_id}")

        backend_uri = self._resolve_backend_uri(backend_id)
        if not backend_uri:
            logger.error(f"❌ Could not resolve backend: {backend_id}")
            return False

        if self._test_backend_connection(backend_uri):
            self._initialize_client_with_backend(backend_uri)
            self.current_backend = backend_id
            logger.info(f"✅ Successfully switched to backend: {backend_id}")
            return True
        else:
            logger.error(f"❌ Backend connection test failed: {backend_id}")
            return False

    def get_backend_status(self) -> Dict[str, Any]:
        """Get status of all configured backends"""
        backends = {
            'primary': self.backend_config.primary,
            'alternative': self.backend_config.alternative,
            'fallback': self.backend_config.fallback,
            'test_mode': self.backend_config.test_mode
        }

        status = {}
        for name, backend_id in backends.items():
            backend_uri = self._resolve_backend_uri(backend_id)
            if backend_uri:
                is_available = self._test_backend_connection(backend_uri)
                status[name] = {
                    'backend_id': backend_id,
                    'backend_uri': backend_uri[:50] + "..." if len(backend_uri) > 50 else backend_uri,
                    'available': is_available,
                    'current': (name == self.current_backend)
                }
            else:
                status[name] = {
                    'backend_id': backend_id,
                    'backend_uri': None,
                    'available': False,
                    'current': False
                }

        return status

# Global instance
_enhanced_mlflow_service = None

def get_enhanced_mlflow_service():
    """Get the global enhanced MLflow service instance"""
    global _enhanced_mlflow_service
    if _enhanced_mlflow_service is None:
        _enhanced_mlflow_service = EnhancedMLflowService()
    return _enhanced_mlflow_service

def reset_enhanced_mlflow_service():
    """Reset the global enhanced MLflow service"""
    global _enhanced_mlflow_service
    _enhanced_mlflow_service = None