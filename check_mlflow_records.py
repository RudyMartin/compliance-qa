#!/usr/bin/env python3
"""
Check latest 5 MLflow records using pooled connection
"""

import yaml
import mlflow
from pathlib import Path
from datetime import datetime

# Load credentials for PostgreSQL backend
settings_path = Path('infrastructure/settings.yaml')
with open(settings_path) as f:
    config = yaml.safe_load(f)

# Get PostgreSQL credentials for MLflow
pg_creds = config['credentials']['postgresql_primary']
host = pg_creds['host']
port = pg_creds['port']
database = pg_creds['database']
username = pg_creds['username']
password = pg_creds['password']

# Connect to MLflow with PostgreSQL backend
tracking_uri = f'postgresql://{username}:{password}@{host}:{port}/{database}'
mlflow.set_tracking_uri(tracking_uri)

print('LAST 5 MLFLOW RECORDS FROM POSTGRESQL')
print('=' * 60)

try:
    client = mlflow.tracking.MlflowClient()

    # Get all experiments
    experiments = client.search_experiments()
    print(f'Found {len(experiments)} experiments')

    # Get all runs from all experiments
    all_runs = []
    for exp in experiments:
        runs = client.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=['start_time DESC'],
            max_results=10
        )
        all_runs.extend(runs)

    # Sort by start time and get last 5
    all_runs.sort(key=lambda x: x.info.start_time, reverse=True)
    last_5 = all_runs[:5]

    print(f'Total runs: {len(all_runs)}')
    print(f'Showing last 5 runs:')
    print()

    for i, run in enumerate(last_5, 1):
        experiment = client.get_experiment(run.info.experiment_id)
        start_time = datetime.fromtimestamp(run.info.start_time/1000)

        print(f'Record #{i}:')
        print(f'  Run ID: {run.info.run_id}')
        print(f'  Experiment: {experiment.name}')
        print(f'  Start Time: {start_time}')
        print(f'  Status: {run.info.status}')

        # Show key parameters
        params = run.data.params
        if 'model' in params:
            print(f'  Model: {params["model"]}')
        if 'audit_reason' in params:
            print(f'  Audit Reason: {params["audit_reason"]}')

        # Show key metrics
        metrics = run.data.metrics
        if 'total_tokens' in metrics:
            print(f'  Total Tokens: {int(metrics["total_tokens"])}')
        if 'total_cost' in metrics:
            print(f'  Total Cost: ${metrics["total_cost"]:.4f}')

        print()

except Exception as e:
    print(f'Error: {e}')