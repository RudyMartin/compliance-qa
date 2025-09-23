#!/usr/bin/env python3
"""
Start MLflow Server with Optimized Connection Pooling
=====================================================

This script starts MLflow server with proper connection pooling configured
to minimize latency when working with AWS RDS PostgreSQL.

Key optimizations:
- Connection pooling with 10 persistent connections
- Pre-ping to detect dead connections
- Connection recycling every 30 minutes
- TCP keepalives for long-running connections
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def start_pooled_mlflow_server():
    """Start MLflow server with optimized pooling configuration."""

    print("Starting MLflow Server with Connection Pooling")
    print("=" * 60)

    # First configure the pooling environment
    from configure_mlflow_pooling import configure_mlflow_pooling
    db_uri, pooling_config = configure_mlflow_pooling()

    print("\n" + "=" * 60)
    print("Starting MLflow Server...")
    print("-" * 60)

    # Get artifact store from config
    from infrastructure.yaml_loader import SettingsLoader
    loader = SettingsLoader()
    mlflow_config = loader.get_mlflow_config()
    artifact_store = mlflow_config.get('artifact_store', 's3://nsc-mvp1/onboarding-test/mlflow/')

    # Build MLflow server command with all optimizations
    cmd = [
        sys.executable, '-m', 'mlflow', 'server',
        '--backend-store-uri', db_uri,
        '--default-artifact-root', artifact_store,
        '--host', '0.0.0.0',
        '--port', '5000'
    ]

    # On Linux/Mac, we could add gunicorn options for more workers:
    # '--workers', '4',
    # '--gunicorn-opts', '--timeout 120 --keep-alive 5 --max-requests 1000'
    # But on Windows, we use the default waitress server

    print("Command:", " ".join([c if 'password' not in c.lower() else '***' for c in cmd]))
    print("\nMLflow UI will be available at: http://localhost:5000")
    print("\nConnection Pool Status:")
    print(f"  - {pooling_config['MLFLOW_SQLALCHEMY_POOL_SIZE']} warm connections maintained")
    print(f"  - Up to {pooling_config['MLFLOW_SQLALCHEMY_MAX_OVERFLOW']} additional connections during bursts")
    print(f"  - Connections tested before use (pre-ping enabled)")
    print(f"  - Stale connections recycled every 30 minutes")
    print("\nExpected Query Latency: 2-10ms (vs 50-200ms without pooling)")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 60)

    try:
        # Start the server
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nMLflow server stopped by user")
    except Exception as e:
        print(f"Error starting MLflow server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    start_pooled_mlflow_server()