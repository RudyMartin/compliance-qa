# Hexagonal Architecture - PostgreSQL with Resilient Connection Pooling

## Overview
The PostgreSQL implementation features a sophisticated resilient connection pooling system that prevents the "single pool hang" problem through a 3-pool failover architecture. This design ensures database availability even under heavy load, network issues, or maintenance scenarios.

## Architecture Diagram

```
         PRIMARY PORTS (Application Side)                    SECONDARY PORTS (Database Side)
    ┌────────────────────────────────────┐                ┌──────────────────────────────┐
    │  Application Services              │                │  IDatabase Interface         │
    │  • MLflow (port 5000)             │                │  • execute_query()           │
    │  • RAG Systems (5 variants)       │                │  • begin_transaction()       │
    │  • Vector Search                  │                │  • commit()                  │
    │  • Workflow Management            │                │  • rollback()                │
    │  (Database Consumers)              │                │  • get_connection()          │
    └──────────┬─────────────────────────┘                └─────────▲────────────────────┘
               │                                                      │
               ▼                                                      │
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                         DOMAIN CORE (Database Access Layer)                         │
    │  ┌───────────────────────────────────────────────────────────────────────────────┐ │
    │  │                     ResilientPoolManager (Core Logic)                         │ │
    │  │  ┌─────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  Resilience Strategies:                                                 │ │ │
    │  │  │  • Primary/Backup/Failover pool architecture                           │ │ │
    │  │  │  • Automatic failover on pool hang (3-pool strategy)                   │ │ │
    │  │  │  • Health monitoring (30-second intervals)                              │ │ │
    │  │  │  • Load balancing between healthy pools                                │ │ │
    │  │  │  • Circuit breaker pattern (3 failures = failover)                     │ │ │
    │  │  │  • Connection retry logic (max 3 retries)                              │ │ │
    │  │  │  • Timeout management (10-second threshold)                            │ │ │
    │  │  └─────────────────────────────────────────────────────────────────────────┘ │ │
    │  │                                                                               │ │
    │  │  ┌─────────────────────────────────────────────────────────────────────────┐ │ │
    │  │  │  Pool Metrics & Monitoring:                                             │ │ │
    │  │  │  • PoolMetrics dataclass (per pool)                                     │ │ │
    │  │  │  • active_connections tracking                                          │ │ │
    │  │  │  • total_requests counting                                              │ │ │
    │  │  │  • failed_requests monitoring                                           │ │ │
    │  │  │  • avg_response_time calculation                                        │ │ │
    │  │  │  • health_status (healthy/degraded/unhealthy)                          │ │ │
    │  │  └─────────────────────────────────────────────────────────────────────────┘ │ │
    │  └───────────────────────────────────────────────────────────────────────────────┘ │
    └──────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                          ┌────────────────┴────────────────┐
                          ▼                                  ▼
```

## Connection Pool Layer

```
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                           CONNECTION POOL LAYER                                      │
    │                                                                                      │
    │  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌───────────────────┐  │
    │  │   PRIMARY POOL          │  │   BACKUP POOL           │  │  FAILOVER POOL    │  │
    │  │  ┌─────────────────┐   │  │  ┌─────────────────┐   │  │ ┌─────────────┐   │  │
    │  │  │ psycopg2 pool   │   │  │  │ psycopg2 pool   │   │  │ │ psycopg2    │   │  │
    │  │  │ • min_conn: 2   │   │  │  │ • min_conn: 1   │   │  │ │ • min: 1    │   │  │
    │  │  │ • max_conn: 20  │   │  │  │ • max_conn: 10  │   │  │ │ • max: 5    │   │  │
    │  │  │ • timeout: 30s  │   │  │  │ • timeout: 30s  │   │  │ │ • timeout:  │   │  │
    │  │  │ • autocommit    │   │  │  │ • autocommit    │   │  │ │   60s       │   │  │
    │  │  └─────────────────┘   │  │  └─────────────────┘   │  │ └─────────────┘   │  │
    │  └─────────────────────────┘  └─────────────────────────┘  └───────────────────┘  │
    │                                                                                      │
    │  ┌─────────────────────────────────────────────────────────────────────────────┐   │
    │  │                    TidyLLMConnectionPool (Base Implementation)              │   │
    │  │  • Connection lifecycle management                                           │   │
    │  │  • Thread-safe connection acquisition                                        │   │
    │  │  • Connection validation and recycling                                       │   │
    │  │  • Query execution with automatic retry                                      │   │
    │  └─────────────────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────────────────┘
```

## Credential and External Infrastructure

```
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                         CREDENTIAL & CONFIG LAYER                                    │
    │  ┌─────────────────────────────────────────────────────────────────────────────┐   │
    │  │                         CredentialCarrier                                    │   │
    │  │  • Loads from settings.yaml                                                  │   │
    │  │  • Manages multiple database credentials:                                    │   │
    │  │    - vectorqa (primary)                                                      │   │
    │  │    - mlflow_alt_db (MLflow tracking)                                        │   │
    │  │    - postgresql_primary (main app DB)                                       │   │
    │  │  • Environment variable fallback                                             │   │
    │  │  • Secure credential storage                                                 │   │
    │  └─────────────────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                          EXTERNAL INFRASTRUCTURE                                     │
    │  ┌─────────────────────────────────────────────────────────────────────────────┐   │
    │  │                      AWS RDS PostgreSQL Instances                            │   │
    │  │  ┌────────────────────────────────────────────────────────────────────┐    │   │
    │  │  │  Primary: vectorqa.czxuk7no9zzp.us-east-1.rds.amazonaws.com       │    │   │
    │  │  │  • PostgreSQL 15.4                                                 │    │   │
    │  │  │  • db.t3.medium (2 vCPU, 4 GB RAM)                                 │    │   │
    │  │  │  • 100 GB SSD storage                                              │    │   │
    │  │  │  • Multi-AZ deployment                                              │    │   │
    │  │  └────────────────────────────────────────────────────────────────────┘    │   │
    │  │                                                                              │   │
    │  │  ┌────────────────────────────────────────────────────────────────────┐    │   │
    │  │  │  Read Replica: vectorqa-read.czxuk7no9zzp.us-east-1.rds...        │    │   │
    │  │  │  • Async replication from primary                                   │    │   │
    │  │  │  • Read-only queries offloading                                    │    │   │
    │  │  └────────────────────────────────────────────────────────────────────┘    │   │
    │  └─────────────────────────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### ResilientPoolManager

The core component implementing the 3-pool failover strategy:

**Resilience Features**:
- Primary pool for normal operations
- Backup pool for failover scenarios
- Failover pool as last resort
- Automatic health monitoring
- Load balancing between healthy pools

**Configuration**:
- Health check interval: 30 seconds
- Timeout threshold: 10 seconds
- Max retries: 3
- Failover threshold: 3 failed requests

### Pool Metrics

Each pool tracks detailed metrics:
- Active connections count
- Total requests processed
- Failed requests count
- Average response time
- Last health check timestamp
- Health status (healthy/degraded/unhealthy)

### Connection Pool Specifications

**Primary Pool**:
- Min connections: 2
- Max connections: 20
- Timeout: 30 seconds
- Role: Main operational pool

**Backup Pool**:
- Min connections: 1
- Max connections: 10
- Timeout: 30 seconds
- Role: First failover option

**Failover Pool**:
- Min connections: 1
- Max connections: 5
- Timeout: 60 seconds
- Role: Emergency fallback

## Failover Sequence

1. **Normal Operation**: PRIMARY pool handles all requests
2. **Primary Degradation**: Detected via health checks (response time > threshold)
3. **Automatic Failover**: Switch to BACKUP pool
4. **Backup Issues**: If backup also fails, switch to FAILOVER pool
5. **Recovery**: Background health checks attempt to restore PRIMARY
6. **Rebalancing**: Gradual shift back to PRIMARY when healthy

## Connection Flow

1. Application requests connection via `ResilientPoolManager.get_connection()`
2. Manager checks active pool health status
3. If healthy: Returns connection from active pool
4. If degraded: Initiates failover sequence
5. Connection wrapped in context manager for automatic cleanup
6. Metrics updated for monitoring and alerting

## Error Handling

### Custom Exceptions
- **PoolTimeoutException**: Connection acquisition timeout
- **PoolHungException**: Pool appears frozen
- **PoolException**: General pool errors

### Recovery Strategies
- Automatic retry with exponential backoff
- Circuit breaker prevents cascade failures
- Background thread attempts pool recovery
- Graceful degradation to backup pools

## Monitoring Metrics

- Connection acquisition time
- Query execution time
- Pool utilization percentage
- Failed connection attempts
- Failover events count
- Health check results
- Average response time per pool

## Thread Safety

- Uses `threading.RLock()` for concurrent access
- Thread-safe connection acquisition
- Atomic pool switching during failover
- Protected metric updates

## Resource Carrier Pattern

The system implements the Resource Carrier Pattern:
- Credentials managed separately from pool logic
- CredentialCarrier provides database configurations
- Clean separation between credentials and connections

## Benefits

1. **High Availability**: 3-tier failover ensures database access
2. **Automatic Recovery**: Self-healing with background monitoring
3. **Performance**: Load balancing optimizes resource usage
4. **Observability**: Comprehensive metrics for monitoring
5. **Thread Safety**: Safe for concurrent applications
6. **Clean Architecture**: Separation of concerns

## Configuration Example

```yaml
# settings.yaml
credentials:
  vectorqa:
    engine: postgresql
    host: vectorqa.czxuk7no9zzp.us-east-1.rds.amazonaws.com
    port: 5432
    database: vectorqa
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
    pool_size: 20
    max_overflow: 10
```

## Implementation Files

- **Core**: `infrastructure/services/resilient_pool_manager.py`
- **Base Pool**: `packages/tidyllm/infrastructure/connection_pool.py`
- **Credentials**: `infrastructure/services/credential_carrier.py`
- **Config**: `infrastructure/settings.yaml`

## Testing Strategy

- **Unit Tests**: Mock pool behavior, test failover logic
- **Integration Tests**: Test with real database connections
- **Load Tests**: Verify behavior under high concurrency
- **Chaos Tests**: Simulate pool failures and recovery

## Use Cases

This architecture ensures database availability during:
- Heavy load periods
- Network instability
- Database maintenance windows
- Connection pool exhaustion
- Unexpected connection drops
- Long-running queries
- Deadlock situations