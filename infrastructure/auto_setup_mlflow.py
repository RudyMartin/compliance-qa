#!/usr/bin/env python3
"""
Auto-setup MLflow with credentials from settings.yaml
This ensures AWS credentials are loaded for S3 access
"""

import os
import yaml
from pathlib import Path

def setup_mlflow_environment():
    """Set up all environment variables needed for MLflow"""

    # Load settings
    settings_path = Path(__file__).parent / 'settings.yaml'
    if not settings_path.exists():
        print(f"ERROR: settings.yaml not found at {settings_path}")
        return False

    with open(settings_path) as f:
        config = yaml.safe_load(f)

    # Set AWS credentials for S3 artifact storage
    if 'aws_basic' in config.get('credentials', {}):
        aws = config['credentials']['aws_basic']
        os.environ['AWS_ACCESS_KEY_ID'] = aws['access_key_id']
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws['secret_access_key']
        os.environ['AWS_DEFAULT_REGION'] = aws.get('default_region', 'us-east-1')
        os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://s3.amazonaws.com'
        print(f"✓ AWS credentials set (Key: {aws['access_key_id'][:10]}...)")
    else:
        print("WARNING: No AWS credentials found in settings.yaml")

    # Set PostgreSQL backend URI
    if 'postgresql_primary' in config.get('credentials', {}):
        pg = config['credentials']['postgresql_primary']
        tracking_uri = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
        os.environ['MLFLOW_TRACKING_URI'] = tracking_uri
        print(f"✓ PostgreSQL backend configured ({pg['host']})")
    else:
        print("WARNING: No PostgreSQL credentials found")

    # Set MLflow artifact location
    if 'mlflow' in config.get('services', {}):
        mlflow_config = config['services']['mlflow']
        artifact_store = mlflow_config.get('artifact_store', 's3://nsc-mvp1/onboarding-test/mlflow/')
        os.environ['MLFLOW_DEFAULT_ARTIFACT_ROOT'] = artifact_store
        print(f"✓ Artifact store: {artifact_store}")

    return True

# Auto-run setup when imported
if __name__ == "__main__" or True:  # Always run on import
    setup_mlflow_environment()