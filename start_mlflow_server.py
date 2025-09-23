#!/usr/bin/env python3
"""
Start MLflow Server with Connection Pooling
==========================================

This script starts a local MLflow server that manages its own connection pool
to the PostgreSQL backend, solving the timeout issues with direct connections.

The MLflow server acts as a connection pooler between clients and the RDS database.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def start_mlflow_server():
    """Start MLflow server with PostgreSQL backend and S3 artifacts."""

    print("Starting MLflow Server with Connection Pooling")
    print("=" * 60)

    try:
        # Import settings loader
        from infrastructure.yaml_loader import SettingsLoader
        loader = SettingsLoader()

        # Get MLflow configuration
        mlflow_config = loader.get_mlflow_config()

        # Get PostgreSQL connection string for backend
        db_config = loader.get_database_config()
        backend_store_uri = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

        # Get S3 artifact store
        artifact_store = mlflow_config.get('artifact_store', 's3://nsc-mvp1/onboarding-test/mlflow/')

        # Server configuration
        host = '0.0.0.0'
        port = 5000

        print(f"Backend Store: PostgreSQL on AWS RDS")
        print(f"Artifact Store: {artifact_store}")
        print(f"Server: http://localhost:{port}")
        print("-" * 60)

        # Set AWS credentials for S3 access
        try:
            # Set environment variables from loader
            loader.set_environment_variables()
            # AWS credentials should now be in environment
            if not os.environ.get('AWS_ACCESS_KEY_ID'):
                # Try to get from settings directly
                settings = loader.settings
                aws_creds = settings.get('credentials', {}).get('aws_basic', {})
                if aws_creds:
                    os.environ['AWS_ACCESS_KEY_ID'] = aws_creds.get('access_key_id', '')
                    os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds.get('secret_access_key', '')
                    os.environ['AWS_DEFAULT_REGION'] = aws_creds.get('default_region', 'us-east-1')
        except Exception as aws_error:
            print(f"Warning: Could not set AWS credentials: {aws_error}")

        # Build MLflow server command
        # Note: gunicorn not supported on Windows, using default server
        cmd = [
            sys.executable, '-m', 'mlflow', 'server',
            '--backend-store-uri', backend_store_uri,
            '--default-artifact-root', artifact_store,
            '--host', host,
            '--port', str(port)
        ]

        # On Windows, MLflow uses waitress server which also provides connection pooling

        print("Starting MLflow server with command:")
        print(" ".join(cmd))
        print("\nMLflow server will manage connection pooling to RDS")
        print("Clients should connect to: http://localhost:5000")
        print("\nPress Ctrl+C to stop the server")
        print("-" * 60)

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
    start_mlflow_server()