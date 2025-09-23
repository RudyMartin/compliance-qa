# PostgreSQL Connection Pool Initialization Order

## Overview
The system uses multiple PostgreSQL connection pools to manage connections to AWS RDS. Understanding the initialization order is critical for proper configuration and avoiding conflicts.

## Initialization Sequence

### 1. Infrastructure Delegate Pool (FIRST)
**Location**: `infrastructure/infra_delegate.py`
**When**: On first call to `get_infra_delegate()`
**Type**: `TidyLLMConnectionPool` (Singleton)

```python
# Creates the primary connection pool singleton
connection_pool = TidyLLMConnectionPool(
    config['database']['host'],
    config['database']['port'],
    config['database']['username'],
    config['database']['password'],
    config['database']['database']
)
```

**Key Points**:
- This is the FIRST pool to initialize
- Creates a singleton that other components may reuse
- Uses `psycopg2.pool.SimpleConnectionPool`
- Default pool size: 1-10 connections

### 2. Gateway Registration
**Location**: `packages/tidyllm/gateways/corporate_llm_gateway.py`
**When**: After infrastructure delegate initialization
**Action**: Registers with existing infra_delegate

```python
gateway.register_with_infra_delegate(delegate)
```

**Key Points**:
- Does NOT create a new pool
- Uses the existing infra_delegate connection pool
- Shares connections for MLflow logging

### 3. MLflow Service Pool
**Location**: `infrastructure/services/enhanced_mlflow_service.py`
**When**: On MLflow service initialization
**Type**: Can be separate or shared

```python
# Option A: Use existing TidyLLMConnectionPool singleton
self.pool = TidyLLMConnectionPool.get_instance()

# Option B: Create separate MLflow connections
# (Controlled by MLFLOW_SQLALCHEMY_* environment variables)
```

**Key Points**:
- May reuse the singleton pool OR
- Create separate connections via SQLAlchemy
- Configured via environment variables

## Pool Configuration

### TidyLLMConnectionPool Settings
```python
# Default configuration
minconn=1      # Minimum connections
maxconn=10     # Maximum connections
```

### MLflow SQLAlchemy Pool Settings
```bash
# Environment variables (when using separate pool)
MLFLOW_SQLALCHEMY_POOL_SIZE=10           # Base pool size
MLFLOW_SQLALCHEMY_MAX_OVERFLOW=20        # Additional connections
MLFLOW_SQLALCHEMY_POOL_TIMEOUT=30        # Connection wait timeout
MLFLOW_SQLALCHEMY_POOL_RECYCLE=1800      # Connection recycle time
MLFLOW_SQLALCHEMY_POOL_PRE_PING=true     # Test before use
```

## Architecture Boundaries

### Infrastructure Layer ✓
- Connection pool initialization
- Database configuration
- Pool management
- Connection recycling

### Domain Layer ✗
- Should NOT contain pool configuration
- Should NOT manage connections directly
- Accesses data through infrastructure services

## Connection Flow

```
Application Start
    ↓
get_infra_delegate() called
    ↓
TidyLLMConnectionPool singleton created (FIRST POOL)
    ↓
Infrastructure Delegate initialized
    ↓
Gateway registered with delegate
    ↓
MLflow service initialized
    ├→ Option A: Reuse singleton pool
    └→ Option B: Create SQLAlchemy pool
```

## Important Notes

1. **Singleton Pattern**: The TidyLLMConnectionPool uses a singleton pattern, meaning only ONE instance exists across the application.

2. **Pool Sharing**: Multiple components can share the same pool, reducing total connections to the database.

3. **AWS RDS Limits**: Be mindful of RDS connection limits when configuring pool sizes.

4. **Latency Considerations**:
   - Home to AWS: 50-150ms per new connection
   - AWS to AWS: <5ms per new connection
   - Pooled connections: 2-10ms (reuse existing)

## Troubleshooting

### Issue: Too Many Connections
**Symptom**: PostgreSQL error about connection limit
**Solution**: Reduce pool sizes or share pools between components

### Issue: Connection Timeouts
**Symptom**: Timeout errors when acquiring connections
**Solution**: Increase pool size or timeout values

### Issue: Stale Connections
**Symptom**: "Connection closed" errors
**Solution**: Enable pre-ping or reduce recycle time

## Best Practices

1. **Initialize Early**: Start the pool during application startup
2. **Share When Possible**: Reuse the singleton pool across components
3. **Monitor Usage**: Track active vs idle connections
4. **Configure for Environment**: Adjust settings based on deployment location (home vs AWS)
5. **Use Connection Pooling**: Always use pooling for production deployments