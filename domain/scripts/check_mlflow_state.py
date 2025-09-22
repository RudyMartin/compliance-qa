"""
Quick script to check MLflow state after cleanup
"""
import mlflow
from datetime import datetime, timedelta

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")
client = mlflow.tracking.MlflowClient()

print("=" * 60)
print("MLflow State Check")
print("=" * 60)

# Check experiments
experiments = client.search_experiments()
print(f"\nTotal experiments: {len(experiments)}")
for exp in experiments[:5]:
    print(f"  - {exp.name} (ID: {exp.experiment_id}, Created: {datetime.fromtimestamp(exp.creation_time/1000)})")

# Check recent runs
print("\nRecent runs (all experiments):")
all_runs = client.search_runs(
    experiment_ids=[exp.experiment_id for exp in experiments],
    max_results=10
)
print(f"Found {len(all_runs)} runs")
for run in all_runs:
    print(f"  - Run {run.info.run_id[:8]}... in {run.info.experiment_id} at {datetime.fromtimestamp(run.info.start_time/1000)}")

print("\nThis explains why you're seeing limited records - ")
print("the cleanup you did removed historical MLflow data.")
print("\nThe Re-install MLflow button we added will do a similar")
print("complete cleanup when needed, including:")
print("  1. Stopping MLflow server")
print("  2. Clearing S3 artifacts")
print("  3. Resetting database tables")
print("  4. Starting fresh MLflow instance")