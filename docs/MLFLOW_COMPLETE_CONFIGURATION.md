# MLflow Complete Configuration Guide

## MLflow is MORE Than Just a Database!

MLflow needs configuration for:
1. **Tracking Server** (where experiments are logged)
2. **Backend Store** (database for metadata)
3. **Artifact Store** (S3/filesystem for models/files)
4. **UI Server** (web interface)
5. **Gateway** (model serving)
6. **Integration Settings** (circuit breakers, pooling, etc.)

---

## Complete MLflow Configuration

```yaml
mlflow:
  # 1. TRACKING - Where MLflow clients connect
  tracking_uri: http://localhost:5000  # Can be HTTP, database URI, or file://

  # 2. BACKEND STORE - Metadata storage (experiments, runs, parameters)
  backend_store_uri: postgresql://mlflow_user:pass@host:5432/mlflow_db
  # OR
  # backend_store_uri: sqlite:///mlflow.db
  # OR
  # backend_store_uri: mysql+pymysql://user:pass@host/db

  # 3. ARTIFACT STORE - Model/file storage
  artifact_store: s3://nsc-mvp1/onboarding-test/mlflow/
  # OR
  # artifact_store: ./mlruns  # Local filesystem
  # OR
  # artifact_store: gs://bucket/path  # Google Cloud
  # OR
  # artifact_store: azure://container/path

  # 4. SERVER CONFIGURATION - MLflow UI/API server
  server:
    host: 0.0.0.0
    port: 5000
    workers: 4  # Number of gunicorn workers
    static_prefix: /mlflow  # URL prefix for UI
    serve_artifacts: true  # Serve artifacts through tracking server

  # 5. EXPERIMENT SETTINGS
  default_experiment: "Default"
  experiment_name: "my-project"

  # 6. AUTHENTICATION (if enabled)
  auth:
    enabled: false
    database_uri: postgresql://mlflow_auth:pass@host/mlflow_auth
    admin_username: admin
    admin_password: ${MLFLOW_ADMIN_PASSWORD}

  # 7. INTEGRATION SETTINGS (from your config)
  integration_config:
    circuit_breaker: true       # Prevent cascade failures
    health_monitoring: true     # Monitor MLflow health
    metrics_collection: true    # Collect performance metrics
    pool_client_name: mlflow_integration
    use_shared_pool: true      # Share connection pool

  # 8. MODEL REGISTRY
  registry:
    enabled: true
    backend_store: ${backend_store_uri}  # Usually same as tracking

  # 9. MODEL SERVING/GATEWAY
  gateway:
    enabled: false
    uri: http://localhost:5001
    routes:
      - name: sentiment-analysis
        model_uri: models:/sentiment/production
      - name: fraud-detection
        model_uri: s3://models/fraud/latest
```

---

## The Four Ways to Configure MLflow (Your Examples)

### 1. ✅ Tracking URI (Client Configuration)
```yaml
# For MLflow clients to connect
mlflow:
  tracking_uri: http://localhost:5000
  experiment_name: "demo_experiment"
```

**Use in Python**:
```python
import mlflow
mlflow.set_tracking_uri(config["mlflow"]["tracking_uri"])
mlflow.set_experiment(config["mlflow"]["experiment_name"])

with mlflow.start_run():
    mlflow.log_metric("accuracy", 0.95)
```

### 2. ✅ Environment Variables (Auto-pickup)
```yaml
# Export as environment variables
environment:
  MLFLOW_TRACKING_URI: http://localhost:5000
  MLFLOW_EXPERIMENT_NAME: demo_experiment
  MLFLOW_S3_ENDPOINT_URL: https://s3.amazonaws.com
  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
```

**MLflow automatically uses these** - no code needed!

### 3. ✅ CLI Configuration
```yaml
# For MLflow CLI commands
cli:
  tracking_uri: http://localhost:5000
  backend_store_uri: postgresql://user:pass@host/mlflow_db
  artifact_root: s3://bucket/path
```

**Use with CLI**:
```bash
mlflow server \
  --backend-store-uri $(yq .cli.backend_store_uri settings.yaml) \
  --default-artifact-root $(yq .cli.artifact_root settings.yaml)
```

### 4. ✅ Server Configuration (Full Setup)
```yaml
# Complete server setup with PostgreSQL + S3
server:
  backend_store_uri: postgresql+psycopg2://mlflow:pass@host:5432/mlflow_db
  default_artifact_root: s3://mlflow-artifacts/
  host: 0.0.0.0
  port: 5000
  serve_artifacts: true
  workers: 4
```

---

## Integration with Database Service

```yaml
databases:
  # MLflow can use its own database settings
  postgres_mlflow:
    host: ${MLFLOW_DB_HOST:-localhost}
    port: ${MLFLOW_DB_PORT:-5432}
    database: mlflow_db
    username: mlflow_user
    password: ${MLFLOW_DB_PASSWORD}

mlflow:
  # Backend store built from postgres_mlflow
  backend_store_uri: postgresql://${databases.postgres_mlflow.username}:${databases.postgres_mlflow.password}@${databases.postgres_mlflow.host}:${databases.postgres_mlflow.port}/${databases.postgres_mlflow.database}

  # Or use the managed connection pool
  backend_store_uri: <<MANAGED_BY_CONNECTION_POOL>>
```

---

## Common MLflow Scenarios

### Scenario 1: Local Development
```yaml
mlflow:
  tracking_uri: ./mlruns  # Local file storage
  backend_store_uri: sqlite:///mlflow.db
  artifact_store: ./mlflow-artifacts
```

### Scenario 2: Team Server (PostgreSQL + S3)
```yaml
mlflow:
  tracking_uri: http://mlflow.team.internal:5000
  backend_store_uri: postgresql://mlflow:pass@db.internal/mlflow
  artifact_store: s3://team-mlflow/artifacts/
```

### Scenario 3: Production (Managed Service)
```yaml
mlflow:
  tracking_uri: https://mlflow.company.com
  # Backend and artifacts managed by platform
```

### Scenario 4: Hybrid (Local Tracking, Remote Storage)
```yaml
mlflow:
  tracking_uri: http://localhost:5000
  backend_store_uri: postgresql://mlflow:pass@remote-db/mlflow
  artifact_store: s3://mlflow-artifacts/
```

---

## Starting MLflow Server

### With All Settings:
```bash
mlflow server \
  --backend-store-uri postgresql://mlflow:pass@localhost/mlflow_db \
  --default-artifact-root s3://mlflow-artifacts/ \
  --host 0.0.0.0 \
  --port 5000 \
  --serve-artifacts \
  --workers 4
```

### Using Configuration:
```python
# load_and_start_mlflow.py
import yaml
import subprocess

with open('settings.yaml') as f:
    config = yaml.safe_load(f)

mlflow_config = config['mlflow']

cmd = [
    'mlflow', 'server',
    '--backend-store-uri', mlflow_config['backend_store_uri'],
    '--default-artifact-root', mlflow_config['artifact_store'],
    '--host', str(mlflow_config['server']['host']),
    '--port', str(mlflow_config['server']['port'])
]

if mlflow_config['server'].get('serve_artifacts'):
    cmd.append('--serve-artifacts')

subprocess.run(cmd)
```

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `MLFLOW_TRACKING_URI` | Where to log runs | `http://localhost:5000` |
| `MLFLOW_EXPERIMENT_NAME` | Default experiment | `my-experiment` |
| `MLFLOW_S3_ENDPOINT_URL` | Custom S3 endpoint | `https://minio.local:9000` |
| `MLFLOW_TRACKING_USERNAME` | Auth username | `user` |
| `MLFLOW_TRACKING_PASSWORD` | Auth password | `pass` |
| `AWS_ACCESS_KEY_ID` | S3 access | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | S3 secret | `secret` |
| `MLFLOW_ARTIFACT_URI` | Override artifact location | `s3://bucket/` |

---

## Troubleshooting MLflow Configuration

### Issue: "Could not connect to tracking server"
```yaml
# Check tracking_uri is accessible
mlflow:
  tracking_uri: http://localhost:5000  # Is server running?
```

### Issue: "Cannot write artifacts"
```yaml
# Check S3 permissions and credentials
mlflow:
  artifact_store: s3://bucket/path/  # Do you have write access?
environment:
  AWS_ACCESS_KEY_ID: your-key
  AWS_SECRET_ACCESS_KEY: your-secret
```

### Issue: "Database connection failed"
```yaml
# Verify PostgreSQL is accessible
mlflow:
  backend_store_uri: postgresql://user:pass@host:5432/mlflow_db
  # Test: psql -U user -h host -d mlflow_db
```

### Issue: "Experiments not persisting"
```yaml
# Using file:// ? Switch to database
mlflow:
  backend_store_uri: postgresql://...  # Not sqlite or file://
```

---

## Telemetry and Timeout Configuration

### Telemetry Settings
```yaml
mlflow:
  telemetry:
    enabled: true
    collection_interval: 60  # seconds
    metrics_to_collect:
      - request_latency
      - model_inference_time
      - artifact_upload_time
      - database_query_time

    # Send telemetry to observability platform
    export_to:
      datadog: ${DATADOG_ENABLED:-false}
      prometheus: ${PROMETHEUS_ENABLED:-true}
      cloudwatch: ${CLOUDWATCH_ENABLED:-false}

    # Performance thresholds for alerts
    thresholds:
      slow_query_ms: 1000
      slow_artifact_upload_s: 30
      slow_model_load_s: 60
```

### Timeout Guidance
```yaml
mlflow:
  timeouts:
    # Client-side timeouts
    client:
      connect_timeout: 10  # seconds to establish connection
      read_timeout: 300    # seconds to read response (5 min for large models)
      write_timeout: 300   # seconds to write request

    # Server-side timeouts
    server:
      request_timeout: 600     # 10 minutes for long operations
      artifact_timeout: 1800   # 30 minutes for large artifact uploads
      query_timeout: 30        # 30 seconds for database queries

    # Integration timeouts
    integration_config:
      circuit_breaker_timeout: 5    # Trip after 5 seconds
      health_check_timeout: 2       # Health check must respond in 2s
      pool_acquisition_timeout: 10  # Max time to get connection from pool
```

### Why These Timeouts Matter

**Too Short** → False failures, interrupted uploads
**Too Long** → Hung connections, poor user experience

**Recommended Timeouts by Operation**:
- Metric logging: 5-10 seconds
- Parameter logging: 5-10 seconds
- Artifact upload (small): 30-60 seconds
- Artifact upload (large models): 10-30 minutes
- Model loading: 1-5 minutes
- Batch inference: 5-30 minutes

### Telemetry Best Practices

1. **Track Key Metrics**:
   ```python
   import mlflow
   import time

   start = time.time()
   mlflow.log_artifact("model.pkl")
   duration = time.time() - start

   # Log as metric for monitoring
   mlflow.log_metric("artifact_upload_time", duration)
   ```

2. **Set Alerts for Timeouts**:
   ```yaml
   alerts:
     - name: mlflow_slow_response
       condition: response_time > 5000ms
       action: notify_oncall
   ```

3. **Monitor Circuit Breaker**:
   ```yaml
   circuit_breaker:
     failure_threshold: 5      # Failures before opening
     timeout: 5000             # ms before considering failure
     reset_timeout: 60000      # ms before trying again
     telemetry:
       log_state_changes: true
       export_metrics: true
   ```

## Best Practices

1. **Separate artifact storage from metadata**:
   - Metadata → PostgreSQL (fast queries)
   - Artifacts → S3 (scalable storage)

2. **Use connection pooling for backend**:
   ```yaml
   backend_store_uri: <<MANAGED_BY_CONNECTION_POOL>>
   ```

3. **Set proper artifact organization**:
   ```yaml
   artifact_store: s3://mlflow/${ENVIRONMENT}/${PROJECT}/
   ```

4. **Enable serve-artifacts for security**:
   - Artifacts served through tracking server
   - No direct S3 access needed by clients

5. **Use environment-specific configs**:
   ```yaml
   development:
     tracking_uri: http://localhost:5000
   production:
     tracking_uri: https://mlflow.company.com
   ```

6. **Configure telemetry for production**:
   - Enable metrics collection
   - Set appropriate timeouts
   - Monitor circuit breaker states
   - Track slow operations

7. **Timeout Strategy**:
   - Short timeouts for metadata operations (5-10s)
   - Long timeouts for artifact operations (5-30min)
   - Circuit breaker for fast failure (5s)
   - Health checks with tight timeouts (2s)

---

## Summary

MLflow configuration involves:
- **Tracking URI**: Where clients connect
- **Backend Store**: Database for metadata
- **Artifact Store**: File/model storage
- **Server Settings**: UI and API configuration
- **Integration**: Circuit breakers, pooling, monitoring
- **Authentication**: Optional security

It's not just database connections - it's a complete tracking and model management system!