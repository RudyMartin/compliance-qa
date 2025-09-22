# Database Configuration Cleanup

## Current Confusion - Multiple Database Configs Found

### 1. In settings.yaml we have:
- **postgres_primary** - Main PostgreSQL at RDS (vectorqa database)
- **mlflow_alt_db** - Points to non-existent RDS (this is causing failures!)
- **sqlite_backup** - Local SQLite fallback

### 2. In MLflow integration config:
- `backend_store_uri: <<MANAGED_BY_CONNECTION_POOL>>` or `auto_select`
- `tracking_uri: http://localhost:5000`
- Artifact store: S3

### 3. In our new DatabaseService we defined:
- **DatabaseType.POSTGRES_STD** - Standard app database
- **DatabaseType.POSTGRES_MLFLOW** - MLflow database
- **DatabaseType.POSTGRES_VECTOR** - Vector/pgvector database

## The Problem

**TOO MANY PLACES** defining database connections:
1. settings.yaml has multiple database sections
2. MLflow has its own database config
3. Our DatabaseService expects different structure
4. Connection pool has its own expectations

## Recommended Solution

### Option 1: Use ONE PostgreSQL Server (Different Databases)
```yaml
# SINGLE SOURCE OF TRUTH in settings.yaml
databases:
  primary:
    host: vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com
    port: 5432
    username: vectorqa_user
    password: bitcoin-miner-2025
    ssl_mode: require

    # Different databases on same server
    databases:
      app: vectorqa           # Main application
      mlflow: mlflow_db      # MLflow tracking
      vector: vector_db      # Embeddings
```

### Option 2: Separate Servers (Clear Names)
```yaml
databases:
  app_postgres:
    host: vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com
    port: 5432
    database: vectorqa
    username: vectorqa_user
    password: bitcoin-miner-2025

  mlflow_postgres:
    host: localhost  # Or same RDS, different database
    port: 5432
    database: mlflow_db
    username: mlflow_user
    password: mlflow_pass
```

## What's Breaking

1. **MLflow trying to connect to**: `alternative-mlflow-db.us-east-1.rds.amazonaws.com`
   - This host doesn't exist!
   - Falls back to SQLite (that's the warning we saw)

2. **Connection pool expecting**: Different structure than what's in settings

3. **Multiple names for same thing**:
   - postgres_primary vs postgres_std
   - mlflow_alt_db vs postgres_mlflow
   - Too many variations!

## Quick Fix

### Update settings.yaml to use REAL hosts:
```yaml
# Change this:
mlflow_alt_db:
  host: alternative-mlflow-db.us-east-1.rds.amazonaws.com  # DOESN'T EXIST!

# To this:
mlflow_alt_db:
  host: vectorqa-cluster.cluster-cu562e4m02nq.us-east-1.rds.amazonaws.com  # SAME AS MAIN
  database: mlflow_db  # DIFFERENT DATABASE
```

## Clean Architecture Proposal

```
settings.yaml
└── databases:
    ├── main:        # Application database
    ├── mlflow:      # MLflow tracking database
    └── vector:      # Vector/embeddings database

Each can be:
- Same server, different databases
- Different servers
- Mix of local and remote
```

## Action Items

1. **Decide**: One PostgreSQL or multiple?
2. **Standardize**: Use consistent naming
3. **Update**: Fix non-existent hosts in settings.yaml
4. **Document**: Clear mapping of what uses what

The confusion is because we have:
- Legacy configurations
- New service configurations
- MLflow's own configuration style
- Connection pool expectations

All slightly different!