# CRITICAL CONNECTION PATTERNS GUIDE
## ⚠️ READ THIS BEFORE MODIFYING ANY CONNECTION CODE ⚠️

**Date**: December 2024
**Status**: STABLE - DO NOT CHANGE WITHOUT UNDERSTANDING
**Critical**: Breaking these patterns WILL cause system-wide failures

---

## Executive Summary

We have **TWO connection patterns** that MUST coexist:
1. **getconn/putconn pattern** (Primary - 90% of code)
2. **Context manager pattern** (Secondary - Critical infrastructure)

Both patterns are **REQUIRED** and **INTENTIONAL**. They serve different purposes and CANNOT be unified without breaking critical functionality.

---

## 🔴 CRITICAL UNDERSTANDING

### The Problem We Solved
We had a **pattern mismatch** where:
- ResilientPoolManager provided context managers
- RAG adapters expected raw connections
- InfraDelegate couldn't translate between them

### The Solution
We added **DUAL INTERFACES** to ResilientPoolManager:
```python
class ResilientPoolManager:
    def getconn(self):     # For RAG adapters (raw connection)
    def putconn(self, conn): # For RAG adapters (manual return)

    @contextmanager
    def get_connection(self): # For infrastructure (auto-cleanup)
```

**BOTH METHODS MUST EXIST** - Removing either breaks the system!

---

## 📘 PRIMARY PATTERN: getconn/putconn (90% of code)

### When to Use
- **ALL application code** (RAG adapters, services, workers)
- **ALL tidyllm package components**
- **Simple database operations**
- **When you need a raw psycopg2 connection**

### How It Works
```python
# ALWAYS use through InfraDelegate
infra = get_infra_delegate()
conn = infra.get_db_connection()  # Internally calls pool.getconn()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table")
    results = cursor.fetchall()
finally:
    infra.return_db_connection(conn)  # Internally calls pool.putconn()
```

### Components Using This Pattern
1. **ALL RAG Adapters**
   - `SMERAGAdapter` - Uses `self.infra.get_db_connection()`
   - `AIPoweredRAGAdapter` - Uses `self.infra.get_db_connection()`
   - `IntelligentRAGAdapter` - Uses `self.infra.get_db_connection()`
   - `PostgresRAGAdapter` - Uses `self.infra.get_db_connection()`

2. **TidyLLM Infrastructure**
   - `UnifiedSessionManager` - Uses infra delegate
   - `IndexingWorker` - Uses infra delegate
   - `VectorManager` - Uses infra delegate

3. **Connection Pool**
   - `TidyLLMConnectionPool` - Exposes getconn/putconn methods
   - Uses real psycopg2.pool internally

### ⚠️ What Will Break If Changed
- **ALL RAG adapters** will fail with AttributeError (no .cursor() on context manager)
- **Query execution** will fail (context managers don't have cursor method)
- **Connection reuse** will break (pool won't track connections properly)

---

## 📗 SECONDARY PATTERN: Context Manager (10% of code)

### When to Use
- **Infrastructure-level orchestration** (failover, metrics, health checks)
- **When you need guaranteed cleanup** even during catastrophic failure
- **Database service abstraction layer**
- **Setup and initialization flows**

### How It Works
```python
# Used in infrastructure layer ONLY
with pool_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table")
    results = cursor.fetchall()
# Automatic cleanup, metrics update, failover handling
```

### Components Using This Pattern

1. **ResilientPoolManager** (resilient_pool_manager.py)
   ```python
   @contextmanager
   def get_connection(self):
       # Complex orchestration:
       # 1. Try primary pool
       # 2. Failover to backup if primary fails
       # 3. Create emergency pool if both fail
       # 4. Track metrics for each attempt
       # 5. Update health status
       # 6. GUARANTEE cleanup even if exception
       yield connection
   ```
   **WHY**: Failover logic REQUIRES try/finally guarantees

2. **DatabaseService** (database_service.py)
   ```python
   def get_connection(self):
       if pool_manager:
           with pool_manager.get_connection() as conn:
               yield conn  # Pass through resilient features
       else:
           # Fallback to direct connection
           conn = psycopg2.connect()
           try:
               yield conn
           finally:
               conn.close()  # Guarantee cleanup
   ```
   **WHY**: Abstracts pool vs direct connection decision

3. **Setup Portal** (new_setup_portal.py)
   ```python
   with database_service.get_connection() as conn:
       # Complex setup operations
       # Multiple tables, transactions
       # Must cleanup even if partial failure
   ```
   **WHY**: Setup MUST cleanup resources even during errors

### ⚠️ What Will Break If Changed
- **Failover won't work** - Primary pool failures won't trigger backup
- **Metrics lost** - Connection tracking and health monitoring fails
- **Resource leaks** - Connections won't return to pool on exceptions
- **Setup corruption** - Partial setup without cleanup corrupts state

---

## 🔄 How The Patterns Work Together

```
Application Layer (RAG Adapters)
    ↓
    Uses: infra.get_db_connection() [getconn pattern]
    ↓
InfraDelegate
    ↓
    Calls: pool.getconn() / pool.putconn()
    ↓
ResilientPoolManager (Has BOTH interfaces)
    ├── getconn() / putconn() → For application layer
    └── get_connection() context → For infrastructure layer
    ↓
Underlying Pools (psycopg2.pool or TidyLLMConnectionPool)
```

### The Key Innovation
ResilientPoolManager **bridges both patterns**:
- Exposes getconn/putconn for application code
- Maintains context manager for infrastructure needs
- Both methods share the same underlying pools

---

## ❌ DO NOT ATTEMPT THESE "FIXES"

### 1. "Unify to only context managers"
```python
# WRONG - Will break all RAG adapters
with infra.get_db_connection() as conn:  # ❌ NO!
    cursor = conn.cursor()  # AttributeError!
```

### 2. "Remove context manager from ResilientPoolManager"
```python
# WRONG - Will break failover
class ResilientPoolManager:
    # def get_connection(self): ❌ DELETED - NO!
    def getconn(self):  # Only this
```
**Result**: No failover, no metrics, resource leaks

### 3. "Make InfraDelegate return context managers"
```python
# WRONG - Breaks everything
def get_db_connection(self):
    return self._db_pool.get_connection()  # ❌ Returns context manager
```
**Result**: ALL adapters break, can't call .cursor()

### 4. "Force everything through DatabaseService"
```python
# WRONG - Unnecessary abstraction
adapter.database_service.get_connection()  # ❌ Too many layers
```
**Result**: Tight coupling, harder testing, performance overhead

---

## ✅ CORRECT PATTERNS BY USE CASE

### Use Case 1: Simple Query in Adapter
```python
# CORRECT
conn = self.infra.get_db_connection()
try:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents")
    results = cursor.fetchall()
finally:
    self.infra.return_db_connection(conn)
```

### Use Case 2: Transaction in Service
```python
# CORRECT
conn = self.infra.get_db_connection()
try:
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    cursor.execute("INSERT INTO table1 ...")
    cursor.execute("INSERT INTO table2 ...")
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
finally:
    self.infra.return_db_connection(conn)
```

### Use Case 3: Infrastructure with Failover
```python
# CORRECT - Only in infrastructure layer
with pool_manager.get_connection() as conn:
    # Complex operations with automatic failover
    pass
```

### Use Case 4: Setup Operations
```python
# CORRECT - Guaranteed cleanup critical
with database_service.get_connection() as conn:
    # Setup that MUST cleanup even on failure
    pass
```

---

## 🚨 EMERGENCY REFERENCE

### If RAG Adapters Stop Working
**Symptom**: `AttributeError: 'ContextManager' object has no attribute 'cursor'`
**Cause**: Someone changed InfraDelegate to return context manager
**Fix**: Ensure InfraDelegate.get_db_connection() calls pool.getconn()

### If Failover Stops Working
**Symptom**: Always using primary pool even when it's down
**Cause**: Someone removed context manager from ResilientPoolManager
**Fix**: Restore @contextmanager get_connection() method

### If Connections Leak
**Symptom**: "Too many connections" errors
**Cause**: Not using try/finally with getconn/putconn pattern
**Fix**: Always use try/finally or context managers

### If Tests Break
**Symptom**: Mock connection errors
**Cause**: Tests expect one pattern but code uses another
**Fix**: Mock at InfraDelegate level, not pool level

---

## 📋 Maintenance Checklist

Before modifying connection code:

- [ ] Do you understand why we have two patterns?
- [ ] Have you identified which pattern the component uses?
- [ ] Have you verified both patterns still work after changes?
- [ ] Have you tested failover scenarios?
- [ ] Have you checked RAG adapters still work?
- [ ] Have you verified no resource leaks?
- [ ] Have you updated this documentation?

---

## 🎯 Summary

1. **TWO patterns exist for GOOD REASONS**
2. **getconn/putconn** = Application layer (most code)
3. **Context managers** = Infrastructure layer (critical features)
4. **ResilientPoolManager** = Bridges both patterns
5. **DO NOT UNIFY** = They serve different purposes
6. **DO NOT REMOVE EITHER** = Both are required

**The system is STABLE**. These patterns are the result of careful problem-solving. Changing them without understanding will break production systems.

---

**Last Updated**: December 2024
**Approved By**: System Architecture Team
**Status**: PRODUCTION CRITICAL - DO NOT MODIFY WITHOUT REVIEW