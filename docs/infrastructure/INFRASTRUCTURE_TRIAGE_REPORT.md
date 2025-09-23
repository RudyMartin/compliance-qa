# Infrastructure Triage Report

## Status Categories
- 🔴 **BROKEN**: Not working, needs immediate fix
- 🟡 **AT RISK**: Working but fragile, pattern mismatch
- 🟢 **WORKING**: Functioning correctly
- ⚠️ **UNKNOWN**: Needs testing to determine status

---

## 1. CORE INFRASTRUCTURE

### InfraDelegate (`packages/tidyllm/infrastructure/infra_delegate.py`)
- **Status**: 🔴 **BROKEN**
- **Issue**: Returns context manager when calling ResilientPoolManager.get_connection()
- **Impact**: RAG adapters can't use connections (no .cursor() method)
- **Fix Priority**: **CRITICAL** - Everything depends on this

### ResilientPoolManager (`infrastructure/services/resilient_pool_manager.py`)
- **Status**: 🟡 **AT RISK**
- **Issue**: Only provides context manager interface, no getconn/putconn
- **Impact**: Can't be used with code expecting raw connections
- **Fix Priority**: **HIGH** - Add getconn/putconn methods

### ConnectionPool (`packages/tidyllm/infrastructure/connection_pool.py`)
- **Status**: 🟡 **AT RISK**
- **Issue**: DelegatePool wrapper adds unnecessary complexity
- **Impact**: Extra abstraction layer, potential bugs
- **Fix Priority**: **MEDIUM** - Works but should be simplified

### DatabaseService (`infrastructure/services/database_service.py`)
- **Status**: 🟢 **WORKING**
- **Issue**: Uses context manager correctly with `with pool_manager.get_connection()`
- **Impact**: None - this is working as designed
- **Fix Priority**: **NONE** - Leave as is

---

## 2. RAG ADAPTERS

### SME RAG Adapter
- **Status**: 🔴 **BROKEN**
- **Issue**: Expects raw connection, gets context manager
- **Pattern**: `conn = self.infra.get_db_connection(); cursor = conn.cursor()`
- **Fix Priority**: **HIGH** - New adapter, should work

### AI-Powered RAG Adapter
- **Status**: 🔴 **BROKEN**
- **Issue**: Same - expects raw connection
- **Pattern**: `conn = self.infra.get_db_connection()`
- **Fix Priority**: **HIGH** - Core functionality

### Intelligent RAG Adapter
- **Status**: 🔴 **BROKEN**
- **Issue**: Same - expects raw connection
- **Pattern**: Uses `self.infra` instance variable
- **Fix Priority**: **HIGH** - Core functionality

### PostgreSQL RAG Adapter
- **Status**: ⚠️ **UNKNOWN**
- **Issue**: Need to check implementation
- **Fix Priority**: **MEDIUM** - Check if affected

---

## 3. SCRIPTS & TOOLS

### verify_mlflow_postgres.py
- **Status**: 🟢 **WORKING**
- **Issue**: Uses psycopg2 directly (we added error handling)
- **Impact**: None - works independently
- **Fix Priority**: **NONE** - Working fine

### execute_robots3_workflow.py
- **Status**: 🟢 **WORKING**
- **Issue**: Uses psycopg2 directly (we added error handling)
- **Impact**: None - works independently
- **Fix Priority**: **NONE** - Working fine

### MLflow Integration
- **Status**: 🟢 **WORKING**
- **Issue**: Gets connection string, manages own connections
- **Impact**: None - independent connection management
- **Fix Priority**: **NONE** - Leave as is

---

## 4. WRAPPERS & ADAPTERS

### DelegatePool (Multiple Locations)
- **Status**: 🟡 **AT RISK**
- **Issue**: Wrapper to make infra delegate look like psycopg2 pool
- **Locations**:
  - connection_pool.py
  - resilient_pool_manager.py
- **Impact**: Extra complexity, maintenance burden
- **Fix Priority**: **LOW** - Works but not ideal

### ConnectionWrapper
- **Status**: 🟡 **AT RISK**
- **Issue**: Another wrapper pattern
- **Impact**: Complexity
- **Fix Priority**: **LOW** - Works but not ideal

---

## 5. PORTALS

### Setup Portal
- **Status**: 🟢 **WORKING**
- **Issue**: Test code, direct psycopg2 usage is fine
- **Impact**: None
- **Fix Priority**: **NONE**

### Chat Portal
- **Status**: ⚠️ **UNKNOWN**
- **Issue**: Need to check database usage
- **Fix Priority**: **LOW** - Check when time permits

---

## IMMEDIATE ACTION ITEMS

### Critical Fixes (Do First):
1. **Fix InfraDelegate** to handle context manager from ResilientPoolManager
2. **Add getconn/putconn** to ResilientPoolManager
3. **Test RAG adapters** work with fix

### Quick Wins (Do Second):
1. Test PostgreSQL RAG adapter
2. Verify portals still work
3. Document the connection pattern clearly

### Future Cleanup (Do Later):
1. Remove unnecessary DelegatePool wrappers
2. Simplify connection_pool.py
3. Implement proper rewrite plan

---

## ROOT CAUSE SUMMARY

**The Problem**: We have a **pattern impedance mismatch**:
- ResilientPoolManager provides **context managers**
- RAG adapters expect **raw connections**
- InfraDelegate tries to abstract over both but **fails**

**The Solution Path**:
1. **Immediate**: Make ResilientPoolManager provide psycopg2-style interface (getconn/putconn)
2. **Short-term**: Update InfraDelegate to use consistent interface
3. **Long-term**: Rewrite with single, clear pattern

---

## RISK ASSESSMENT

### High Risk Components:
- **InfraDelegate** - Everything depends on it
- **RAG Adapters** - Core business logic

### Medium Risk Components:
- **ResilientPoolManager** - Important but fixable
- **Connection wrappers** - Complexity but working

### Low Risk Components:
- **Scripts** - Independent, working fine
- **MLflow** - Separate connection management
- **Portals** - Limited database usage

---

## RECOMMENDATION

**DO NOW**:
1. Fix InfraDelegate to properly handle ResilientPoolManager's context manager
2. Add getconn/putconn to ResilientPoolManager
3. Test all RAG adapters

**DO NOT**:
1. Don't rewrite everything yet
2. Don't remove working wrappers until new pattern is proven
3. Don't change scripts that are working with psycopg2

**PRINCIPLE**: Fix the critical path first, clean up later.