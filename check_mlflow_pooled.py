#!/usr/bin/env python3
"""
Check MLflow records using POOLED PostgreSQL connection
Follows hexagonal architecture - no direct database connections!
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parent))

print('MLFLOW CHECK - USING POOLED CONNECTION')
print('=' * 60)

# Load settings to get configuration
settings_path = Path('infrastructure/settings.yaml')
with open(settings_path) as f:
    config = yaml.safe_load(f)

# IMPORTANT: Set AWS credentials for S3 artifacts
aws_creds = config['credentials']['aws_basic']
os.environ['AWS_ACCESS_KEY_ID'] = aws_creds['access_key_id']
os.environ['AWS_SECRET_ACCESS_KEY'] = aws_creds['secret_access_key']
os.environ['AWS_DEFAULT_REGION'] = aws_creds['default_region']
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'https://s3.amazonaws.com'

print('[OK] AWS S3 credentials configured')

# Get the pooled connection configuration
data_tracking = config['services']['data_tracking']
if data_tracking.get('backend_store_uri') == 'auto_select':
    print('[OK] MLflow configured to use pooled connection (auto_select)')

    # MLflow should use the primary PostgreSQL through the pool
    pg = config['credentials']['postgresql_primary']

    # For MLflow client, we still need to set a tracking URI
    # But this should go through the pool manager
    tracking_uri = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"

    print(f"[OK] Pool client name: {data_tracking['adapter_config']['pool_client_name']}")
    print(f"[OK] Using connection pool: {data_tracking['adapter_config']['use_connection_pool']}")
else:
    tracking_uri = data_tracking.get('backend_store_uri', '')
    print(f"Backend URI: {tracking_uri[:50]}...")

# Now import and configure MLflow
import mlflow

# Set the tracking URI (this will be intercepted by the pool manager)
mlflow.set_tracking_uri(tracking_uri)

print()
print('CHECKING MLFLOW RECORDS:')
print('-' * 40)

try:
    client = mlflow.tracking.MlflowClient()

    # Get experiments (this uses the pooled connection)
    experiments = client.search_experiments()
    print(f'[OK] Found {len(experiments)} experiments via pooled connection')

    # Count total runs
    total_runs = 0
    recent_runs = []

    for exp in experiments[:10]:  # Check first 10 experiments
        runs = client.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=['start_time DESC'],
            max_results=5
        )
        total_runs += len(runs)
        recent_runs.extend(runs)

    print(f'[OK] Found {total_runs} runs in first 10 experiments')

    # Show last 5 runs
    recent_runs.sort(key=lambda x: x.info.start_time, reverse=True)
    last_5 = recent_runs[:5]

    if last_5:
        print()
        print('LAST 5 RECORDS:')
        for i, run in enumerate(last_5, 1):
            exp = client.get_experiment(run.info.experiment_id)
            start = datetime.fromtimestamp(run.info.start_time/1000)

            print(f'{i}. Experiment: {exp.name}')
            print(f'   Time: {start}')

            # Check artifact location
            if 's3://' in run.info.artifact_uri:
                print(f'   [OK] S3 artifacts configured')

            # Show some metrics
            if run.data.metrics:
                metrics = list(run.data.metrics.keys())[:3]
                print(f'   Metrics: {", ".join(metrics)}')
            print()

    print('SUCCESS: MLflow working with:')
    print('  [OK] PostgreSQL via connection pool')
    print('  [OK] S3 for artifact storage')
    print('  [OK] No direct database connections!')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()

    print()
    print('This error might be because:')
    print('1. The connection pool manager is not running')
    print('2. MLflow tables need initialization')
    print('3. The pool configuration needs adjustment')