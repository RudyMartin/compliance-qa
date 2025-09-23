# Hexagonal-Resilient-Databases Architecture

## Overview
Multi-database architecture with resilient connection pooling, following hexagonal principles.

## Architecture Layers

```
┌──────────────────────────────────────────────────┐
│                  DOMAIN LAYER                     │
│         (Pure Business Logic - No I/O)           │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │           PORTS (Interfaces)               │  │
│  │  • DatabaseSessionPort                     │  │
│  │  • AWSSessionPort                          │  │
│  │  • CredentialPort                          │  │
│  └────────────────────────────────────────────┘  │
└────────────────────▲─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│                ADAPTER LAYER                      │
│        (Implements Ports, Delegates to Infra)    │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │      UnifiedSessionAdapter                 │  │
│  │  • Implements all session ports            │  │
│  │  • Delegates to infrastructure services    │  │
│  └────────────────────────────────────────────┘  │
└────────────────────▲─────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────┐
│            INFRASTRUCTURE LAYER                   │
│         (Actual Database Connections)            │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │         DatabaseService                    │  │
│  │  • Manages multiple database types         │  │
│  │  • Creates pool for each database          │  │
│  └─────────────────┬──────────────────────────┘  │
│                    │                              │
│  ┌─────────────────▼──────────────────────────┐  │
│  │      ResilientPoolManager (x3)             │  │
│  │  • postgres_std pool                       │  │
│  │  • postgres_mlflow pool                    │  │
│  │  • postgres_vector pool                    │  │
│  │  • Each with primary/backup/failover       │  │
│  └─────────────────┬──────────────────────────┘  │
└────────────────────┼──────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
    │Postgres│  │MLflow   │  │Vector  │
    │Standard│  │Database │  │Database│
    └────────┘  └─────────┘  └────────┘
```

## Multiple Database Support

### Database Types
```python
class DatabaseType(Enum):
    POSTGRES_STD = "postgres_std"       # Application data, user records
    POSTGRES_MLFLOW = "postgres_mlflow"  # MLflow tracking, experiments
    POSTGRES_VECTOR = "postgres_vector"  # pgvector embeddings, RAG data
```

### Configuration
Each database has independent configuration:
```yaml
databases:
  postgres_std:
    host: localhost
    port: 5432
    database: tidyllm_db
    username: app_user
    password: ${POSTGRES_PASSWORD}
    pool:
      min_connections: 2
      max_connections: 20

  postgres_mlflow:
    host: localhost
    port: 5432
    database: mlflow_db
    username: mlflow_user
    password: ${MLFLOW_PASSWORD}
    pool:
      min_connections: 1
      max_connections: 10

  postgres_vector:
    host: localhost
    port: 5432
    database: vector_db
    username: vector_user
    password: ${VECTOR_PASSWORD}
    pool:
      min_connections: 2
      max_connections: 15
```

## Resilient Pool Management

### Per-Database Pooling
Each database gets its own ResilientPoolManager:

```python
class DatabaseService:
    def __init__(self):
        self._pool_managers = {}

        # Create separate pool for each database
        for db_type in DatabaseType:
            self._pool_managers[db_type] = ResilientPoolManager(
                credential_carrier=self._create_credential_carrier(db_type)
            )
```

### Pool Features (Per Database)
- **Primary Pool**: Main connection pool
- **Backup Pool**: Failover when primary hangs
- **Failover Pool**: Emergency third pool
- **Health Monitoring**: Automatic detection of hung connections
- **Load Balancing**: Distributes load across healthy pools

### Connection Acquisition
```python
# Get connection for specific database
with database_service.get_connection(DatabaseType.POSTGRES_STD) as conn:
    # Use standard postgres connection

with database_service.get_connection(DatabaseType.POSTGRES_MLFLOW) as conn:
    # Use MLflow database connection

with database_service.get_connection(DatabaseType.POSTGRES_VECTOR) as conn:
    # Use vector database connection
```

## Hexagonal Benefits

### 1. Port Abstraction
```python
class DatabaseSessionPort(ABC):
    @abstractmethod
    async def get_connection(self) -> Any:
        """Get a database connection"""

    @abstractmethod
    async def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a database query"""
```

### 2. Adapter Implementation
```python
class UnifiedSessionAdapter(DatabaseSessionPort):
    def __init__(self):
        self._database_service = get_database_service()

    async def get_connection(self):
        # Delegates to infrastructure
        return self._database_service.get_connection()
```

### 3. Clean Separation
- **Domain**: Pure business logic, no database details
- **Adapter**: Translates between domain and infrastructure
- **Infrastructure**: Actual database connections and pooling

## Usage Examples

### Application Layer
```python
# In a domain service
class UserService:
    def __init__(self, db_port: DatabaseSessionPort):
        self.db = db_port

    async def get_user(self, user_id: str):
        # Uses port, doesn't know about pools or databases
        conn = await self.db.get_connection()
        return await self.db.execute_query(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )
```

### MLflow Tracking
```python
# Get MLflow database URI
mlflow_uri = database_service.get_mlflow_tracking_uri()
mlflow.set_tracking_uri(mlflow_uri)

# MLflow uses postgres_mlflow pool automatically
with mlflow.start_run():
    mlflow.log_metric("accuracy", 0.95)
```

### Vector Operations
```python
# Vector database operations
with database_service.get_connection(DatabaseType.POSTGRES_VECTOR) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, embedding <-> %s as distance
        FROM documents
        ORDER BY distance
        LIMIT 10
    """, (query_embedding,))
```

## Health Monitoring

### Per-Database Health
```python
health = database_service.health_check()
# Returns:
{
    'databases': {
        'postgres_std': {
            'status': 'healthy',
            'pool_available': True,
            'primary_pool': 'healthy',
            'backup_pool': 'idle',
            'connections': {'active': 3, 'idle': 7}
        },
        'postgres_mlflow': {
            'status': 'healthy',
            'pool_available': True,
            'primary_pool': 'healthy',
            'connections': {'active': 1, 'idle': 4}
        },
        'postgres_vector': {
            'status': 'degraded',
            'pool_available': True,
            'primary_pool': 'hung',
            'backup_pool': 'active',  # Failover active!
            'connections': {'active': 5, 'idle': 0}
        }
    }
}
```

## Failure Scenarios

### Scenario 1: MLflow Database Down
- postgres_std continues working normally
- postgres_vector continues working normally
- Only MLflow tracking fails (graceful degradation)

### Scenario 2: Primary Pool Hangs
- Automatic failover to backup pool
- No service interruption
- Health monitoring detects issue
- Admin alerted for investigation

### Scenario 3: Database Migration
- Can migrate databases independently
- postgres_std on new server while mlflow stays
- Zero-downtime migration per database

## Configuration Management

### Environment Variables
```bash
# Standard database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=tidyllm_db
POSTGRES_USERNAME=app_user
POSTGRES_PASSWORD=secure_password

# MLflow database
MLFLOW_POSTGRES_HOST=mlflow.db.internal
MLFLOW_POSTGRES_PORT=5432
MLFLOW_POSTGRES_DATABASE=mlflow_db
MLFLOW_POSTGRES_USERNAME=mlflow_user
MLFLOW_POSTGRES_PASSWORD=mlflow_password

# Vector database
VECTOR_POSTGRES_HOST=vector.db.internal
VECTOR_POSTGRES_PORT=5432
VECTOR_POSTGRES_DATABASE=vector_db
VECTOR_POSTGRES_USERNAME=vector_user
VECTOR_POSTGRES_PASSWORD=vector_password
```

### Programmatic Configuration
```python
config = {
    'postgres_host': 'localhost',
    'postgres_database': 'app_db',
    'mlflow_postgres_host': 'mlflow.internal',
    'mlflow_postgres_database': 'mlflow_db',
    'vector_postgres_host': 'vector.internal',
    'vector_postgres_database': 'vector_db'
}

database_service = DatabaseService(config)
```

## Benefits

### 1. **Isolation**
- Database failures don't cascade
- Each database has independent pooling
- Can tune pools per workload

### 2. **Scalability**
- Scale databases independently
- Different hardware for different needs
- MLflow can use SSD while vectors use high-memory

### 3. **Maintainability**
- Clear separation of concerns
- Easy to add new database types
- Hexagonal architecture keeps domain clean

### 4. **Resilience**
- Automatic failover per database
- Health monitoring per pool
- Graceful degradation

### 5. **Testing**
- Can mock at port level
- Test with in-memory databases
- Integration tests per database type

## Summary

The Hexagonal-Resilient-Databases architecture provides:
- ✅ **Multiple database support** with independent configuration
- ✅ **Resilient pooling** with automatic failover per database
- ✅ **Hexagonal architecture** keeping domain logic pure
- ✅ **Health monitoring** per database and pool
- ✅ **Clean separation** between business logic and infrastructure

This architecture ensures database operations are reliable, scalable, and maintainable while keeping the domain layer completely independent of infrastructure concerns.