# Hexagonal Architecture Patterns
## Resource Management in Multi-Adapter Systems

### The Resource Exhaustion Problem

**Problem**: Pure hexagonal architecture can lead to resource multiplication:
- Each adapter creates its own database connections
- Multiple AWS client instances
- Credential re-loading from settings files
- N connection pools instead of 1 shared pool

**Result**: Resource exhaustion, performance degradation, configuration drift

### Solution: Resource Carrier Pattern

**Concept**: Infrastructure resources are "carried" by shared services while maintaining port/adapter isolation.

**Key Principle**:
- **Domain isolation** ✅ (hexagonal goal)
- **Infrastructure sharing** ✅ (resource efficiency)
- **Not everything must be isolated** - only domain logic

### Implementation Strategies

#### 1. Resource Carrier Pattern (Original)
```python
# Shared infrastructure carriers
class CredentialCarrier:
    def __init__(self):
        self._credentials = load_once_from_settings()

    def get_aws_creds(self) -> Dict[str, str]:
        return self._credentials['aws']

# Adapters receive carriers
class SessionAdapter:
    def __init__(self, credential_carrier: CredentialCarrier):
        self._creds = credential_carrier
```

#### 2. Shared Infrastructure Services
```python
# Single shared connection pool
class SharedConnectionPool:
    _instance = None

    @classmethod
    def get_pool(cls):
        if not cls._instance:
            cls._instance = create_connection_pool()
        return cls._instance

# Adapters use shared pool
class DatabaseAdapter:
    def __init__(self):
        self._pool = SharedConnectionPool.get_pool()
```

#### 3. DI Container Resource Management
```python
# Container manages shared resources
class DIContainer:
    def wire(self):
        # Create shared resources ONCE
        cred_service = CredentialService()
        connection_pool = ConnectionPool()

        # Inject same instances into all adapters
        db_adapter = DatabaseAdapter(connection_pool, cred_service)
        aws_adapter = AWSAdapter(cred_service)

        return {
            "db": db_adapter,
            "aws": aws_adapter
        }
```

### Benefits

1. **Resource Efficiency**: Single connection pools, shared credentials
2. **Hexagonal Compliance**: Domain still isolated from infrastructure
3. **Configuration Consistency**: Single source of truth for settings
4. **Performance**: No resource multiplication
5. **Testability**: Can inject mock carriers/services

### Anti-Patterns to Avoid

❌ **Direct Settings Loading in Adapters**
```python
class BadAdapter:
    def __init__(self):
        self.settings = load_settings_yaml()  # Violation!
```

❌ **Multiple Connection Pools**
```python
class BadAdapter:
    def __init__(self):
        self.pool = create_new_pool()  # Resource multiplication!
```

❌ **Environment Variable Dependencies**
```python
class BadAdapter:
    def __init__(self):
        self.key = os.getenv('AWS_KEY')  # Fragile!
```

### Naming Convention

- **Resource Carrier**: Service that "carries" infrastructure resources
- **Shared Infrastructure**: Infrastructure components used by multiple adapters
- **Infrastructure Injection**: Passing infrastructure services to adapters
- **Anti-Exhaustion Pattern**: Preventing resource multiplication

### Example: Session Management

**Before (Resource Exhaustion)**:
```
Portal → SessionAdapter → new UnifiedSessionManager()
Portal → DatabaseAdapter → new ConnectionPool()
Portal → AWSAdapter → new AWS clients
```

**After (Resource Carrier)**:
```
Container → SharedCredentialService (load once)
Container → SharedConnectionPool (single pool)
Container → inject shared services into all adapters
```

### Decision Framework

**When to Share**:
- Expensive resources (DB connections, HTTP clients)
- Configuration/credentials
- Stateful infrastructure

**When to Isolate**:
- Domain logic
- Business rules
- Application services
- Domain models

**Remember**: Hexagonal architecture isolates **domain**, not **infrastructure**.