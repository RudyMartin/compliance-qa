# Total Database Connection Rewrite Plan

## Current State: Three Incompatible Patterns
1. Raw connections (psycopg2 style)
2. Context managers (Pythonic style)
3. Mixed abstractions (InfraDelegate trying to handle both)

## Phase 1: Immediate Fix (1-2 days)
**Goal:** Stop the bleeding, make everything work with minimal changes

### Actions:
1. Add `getconn()/putconn()` to ResilientPoolManager
2. Update InfraDelegate to only use `getconn()/putconn()`
3. Test all RAG adapters still work
4. Document the temporary fix

## Phase 2: Clean Architecture Design (1 week)
**Goal:** Design the target architecture without implementation

### New Architecture Principles:
1. **Single Connection Interface**: One way to get connections
2. **Explicit Layer Boundaries**: Clear separation between layers
3. **No Hidden Conversions**: What you request is what you get
4. **Testability First**: Easy to mock and test

### Proposed Layers:

```
Application Layer (RAG Adapters, Portals)
    ↓
Service Layer (Connection Service)
    ↓
Infrastructure Layer (Pool Implementations)
    ↓
Database Layer (PostgreSQL)
```

### Key Design Decisions:

#### 1. Connection Service Interface
```python
class DatabaseConnectionService:
    """Single source of truth for ALL database connections"""

    def acquire_connection(self, purpose: str = "general") -> Connection:
        """Get a raw database connection with tracking"""
        pass

    def release_connection(self, conn: Connection) -> None:
        """Return connection to pool"""
        pass

    @contextmanager
    def connection(self, purpose: str = "general"):
        """Context manager for automatic cleanup"""
        conn = self.acquire_connection(purpose)
        try:
            yield conn
        finally:
            self.release_connection(conn)
```

#### 2. Pool Strategy Pattern
```python
class PoolStrategy(ABC):
    """Abstract base for different pooling strategies"""

    @abstractmethod
    def acquire(self) -> Connection:
        pass

    @abstractmethod
    def release(self, conn: Connection) -> None:
        pass

class SimplePoolStrategy(PoolStrategy):
    """Basic psycopg2 pool"""
    pass

class ResilientPoolStrategy(PoolStrategy):
    """Failover, health checks, metrics"""
    pass

class MockPoolStrategy(PoolStrategy):
    """For testing"""
    pass
```

## Phase 3: Migration Path (2 weeks)
**Goal:** Gradual migration without breaking production

### Step 1: Create New Service Alongside Old
- Build DatabaseConnectionService
- Implement all pool strategies
- Full test coverage
- Run in parallel with existing system

### Step 2: Migrate One Component at a Time
Priority order:
1. **Test Systems** - Verify new service works
2. **Scripts/Tools** - Simple, isolated components
3. **RAG Adapters** - One adapter at a time
4. **Portals** - User-facing but manageable
5. **Core Infrastructure** - Last, most critical

### Step 3: Feature Flags for Rollback
```python
if settings.USE_NEW_CONNECTION_SERVICE:
    conn = connection_service.acquire_connection()
else:
    conn = infra.get_db_connection()  # Old way
```

## Phase 4: Cleanup (1 week)
**Goal:** Remove old code and consolidate

### Actions:
1. Remove InfraDelegate database methods
2. Remove DelegatePool wrapper classes
3. Remove connection management from adapters
4. Consolidate all pool configurations
5. Update all documentation

## Phase 5: Enhancement (Ongoing)
**Goal:** Add advanced features now that architecture is clean

### Possible Enhancements:
1. **Connection Pooling by Purpose**
   - Read-only pools
   - Write-heavy pools
   - Long-running query pools

2. **Advanced Monitoring**
   - Connection lifetime tracking
   - Query performance by pool
   - Automatic pool sizing

3. **Multi-Database Support**
   - Different pools for different databases
   - Cross-database transaction support

4. **Circuit Breaker Pattern**
   - Automatic failover
   - Gradual recovery
   - Health-based routing

## Implementation Timeline

### Month 1: Stabilize
- Week 1: Immediate fix (Option 4)
- Week 2: Design review and refinement
- Week 3-4: Build new service in isolation

### Month 2: Migrate
- Week 1-2: Test systems and scripts
- Week 3-4: RAG adapters migration

### Month 3: Complete
- Week 1-2: Portal migration
- Week 3: Core infrastructure
- Week 4: Cleanup and documentation

## Success Criteria

1. **Single Pattern**: All code uses same connection pattern
2. **Zero Downtime**: Migration without service interruption
3. **Better Testing**: 90%+ test coverage on connection layer
4. **Performance**: No degradation, ideally improvement
5. **Maintainability**: New developer can understand in 30 minutes

## Risk Mitigation

### Risk 1: Production Breakage
- **Mitigation**: Feature flags, gradual rollout, instant rollback

### Risk 2: Performance Regression
- **Mitigation**: Load testing, metrics monitoring, parallel run

### Risk 3: Hidden Dependencies
- **Mitigation**: Comprehensive integration tests, staged migration

## Decision Points

1. **Month 1 End**: Go/No-go on new architecture
2. **Month 2 Mid**: Continue migration or rollback?
3. **Month 3 Start**: Ready for full cutover?

## Alternative: Managed Service
Consider using a connection pooling service:
- **PgBouncer**: Production-grade PostgreSQL pooler
- **AWS RDS Proxy**: Managed connection pooling
- **Heimdall Data**: Advanced database proxy

This could eliminate most of our custom code.

## Recommendation

1. **Immediate**: Fix with Option 4 (getconn/putconn)
2. **Short-term**: Design and build new service
3. **Medium-term**: Gradual migration with feature flags
4. **Long-term**: Consider managed service for production

The key is to **fix the immediate problem** while **planning for the proper solution**.