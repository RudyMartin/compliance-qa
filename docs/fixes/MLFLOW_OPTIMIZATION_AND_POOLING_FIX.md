# MLflow Optimization and Connection Pooling Fix

## Issue Summary
**Date**: September 23, 2025
**Severity**: High
**Impact**: 2000ms+ latency on MLflow operations from home network to AWS RDS

## Problem Description

### Symptoms
- MLflow operations timing out with 2000ms timeout threshold
- Each MLflow logging request taking 2000-2600ms from home network
- Multiple database writes per request causing compound delays
- Large text artifacts being uploaded to S3 on every request

### Root Causes

1. **No Connection Pooling**: Each MLflow operation created a new database connection
   - Connection setup: ~2000ms from home to AWS RDS
   - Query execution: ~150ms network round trip
   - Total: ~2200ms per operation

2. **Inefficient Database Writes**: Multiple separate calls per request
   - Individual `log_metric()` calls for each metric
   - Separate `log_param()` calls
   - Multiple `log_text()` calls creating S3 uploads

3. **Duplicate Configuration**: Multiple `set_tracking_uri()` calls

## Solution Implemented

### 1. Connection Pooling Configuration

Created pooling configuration scripts to set SQLAlchemy environment variables:

```python
# Connection Pool Settings
MLFLOW_SQLALCHEMY_POOL_SIZE = 10           # Keep 10 connections warm
MLFLOW_SQLALCHEMY_MAX_OVERFLOW = 20        # Allow 20 more during bursts
MLFLOW_SQLALCHEMY_POOL_TIMEOUT = 30        # Wait 30s for connection
MLFLOW_SQLALCHEMY_POOL_RECYCLE = 1800      # Recycle after 30 min
MLFLOW_SQLALCHEMY_POOL_PRE_PING = true     # Test connections before use
```

### 2. Batched Metrics Logging

Optimized `mlflow_safe_wrapper.py` to batch operations:

**Before** (4+ database writes):
```python
self._mlflow_client.log_metric("reward_signal", value1)
self._mlflow_client.log_metric("value_estimation", value2)
self._mlflow_client.log_metric("processing_time_ms", value3)
self._mlflow_client.log_metric("success", value4)
```

**After** (1 database write):
```python
metrics_batch = {
    "processing_time_ms": entry['processing_time'],
    "success": 1.0 if entry['success'] else 0.0,
    "reward_signal": rl_data['reward_signal'],
    "value_estimation": rl_data['value_estimation']
}
self._mlflow_client.log_metrics(metrics_batch)  # Single batch call
```

### 3. Reduced Text Artifact Logging

Added size limits to prevent large S3 uploads:

```python
MAX_TEXT_SIZE = 1000  # Avoid large S3 uploads
if len(entry['prompt']) <= MAX_TEXT_SIZE:
    self._mlflow_client.log_text(entry['prompt'], "prompt.txt")
else:
    # Log truncated version as param instead
    self._mlflow_client.log_param("prompt_truncated", entry['prompt'][:100] + "...")
```

### 4. Eliminated Duplicate Tracking URI Calls

Enhanced `enhanced_mlflow_service.py` to check before setting:

```python
current_uri = os.environ.get('MLFLOW_TRACKING_URI')
if current_uri != backend_uri:
    # Only set if different to avoid redundant calls
    os.environ['MLFLOW_TRACKING_URI'] = backend_uri
    mlflow.set_tracking_uri(backend_uri)
```

### 5. DataNormalizer Integration

Added RL-specific normalization methods to ensure consistent data structure:

```python
@staticmethod
def normalize_rl_data(rl_data: Any) -> Dict[str, Any]:
    """Normalize RL data to ensure consistent structure across components."""
    default_rl = {
        'policy_info': {'method': 'epsilon_greedy', 'epsilon': 0.1},
        'exploration_data': {'exploration_rate': 0.1, 'strategy': 'adaptive'},
        'value_estimation': 0.0,
        'reward_signal': 0.0,
        'rl_metrics': {'episode': 0, 'total_reward': 0.0},
        'rl_state': {'initialized': False},
        'learning_feedback': {'gradient_norm': 0.0, 'loss': 0.0}
    }
    # ... normalization logic
```

## Results

### Performance Improvements

**Before Optimization:**
- First query: ~2240ms
- Subsequent queries: ~2200ms (no connection reuse)
- Multiple database writes per request
- Large S3 uploads on every request

**After Optimization:**
- First query: ~2240ms (initial connection setup)
- Subsequent queries: **~150ms** (pooled connections)
- **15x improvement** after first connection
- Single batched database write per request
- Conditional S3 uploads only for small texts

### Latency Breakdown

**Home to AWS (current):**
- Without pooling: 2000ms setup + 150ms RTT = 2150ms
- With pooling: 0ms reuse + 150ms RTT = 150ms

**AWS to AWS (production):**
- Without pooling: 5ms setup + 3ms RTT = 8ms
- With pooling: 0ms reuse + 3ms RTT = 3ms

## Files Modified

1. **Created:**
   - `configure_mlflow_pooling.py` - Pooling configuration script
   - `start_mlflow_server_pooled.py` - Server startup with pooling
   - `verify_mlflow_pooling.py` - Verification script
   - `test_mlflow_latency.py` - Latency testing script
   - `test_mlflow_optimized.py` - Optimization testing
   - `docs/database/CONNECTION_POOL_INITIALIZATION.md` - Documentation

2. **Modified:**
   - `infrastructure/services/enhanced_mlflow_service.py` - Added pooling config
   - `packages/tidyllm/infrastructure/reliability/mlflow_safe_wrapper.py` - Batched metrics
   - `packages/tidyllm/gateways/corporate_llm_gateway.py` - DataNormalizer integration
   - `common/utilities/data_normalizer.py` - Added RL normalization methods

## Security Enhancements

### Credential Masking

Modified output to hide sensitive information:

```python
# Mask database credentials
if '@' in value:
    masked = value.split('@')[0].split('://')[0] + '://***:***@' + value.split('@')[1]

# Mask AWS access keys
if 'ACCESS_KEY_ID' in key:
    masked = value[:4] + '*' * (len(value) - 4)
```

**Output now shows:**
- Database: `postgresql+psycopg2://***:***@host...`
- AWS Key: `AKIA****************`
- Passwords: `***`

## Deployment Notes

### For Development (Home Network)
1. Run `python configure_mlflow_pooling.py` to set environment
2. Start server with `python start_mlflow_server_pooled.py`
3. Expect ~150ms latency due to network distance

### For Production (AWS SageMaker)
1. Pooling configuration auto-applied via `enhanced_mlflow_service.py`
2. Expected latency: <5ms for all operations
3. 50x faster than home network deployment

## Monitoring

Use `verify_mlflow_pooling.py` to check:
- Pool configuration status
- Connection latency
- Pool health metrics

## Lessons Learned

1. **Connection pooling is critical** for remote database access
2. **Batch operations** significantly reduce database load
3. **Network latency** dominates performance from home networks
4. **Text artifacts** should be size-limited to avoid S3 overhead
5. **Environment variables** must be set before MLflow initialization

## Future Improvements

1. Consider local MLflow server as proxy to RDS
2. Implement async logging queue with batching
3. Add connection pool monitoring metrics
4. Consider read replicas for query operations