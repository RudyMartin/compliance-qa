# Future Fix Triage Report
Generated: 2025-09-21

## Summary
Found 14 files with `#future_fix` comments indicating technical debt for infrastructure improvements.
All comments relate to: **"Convert to use enhanced service infrastructure"**

## Files by Priority

### HIGH PRIORITY - Core Infrastructure (Fix First)
These are actively used in production and central to the system:

1. **infrastructure/services/resilient_pool_manager.py** (13 occurrences)
   - Central connection pooling service
   - Critical for database operations
   - **Action**: Refactor to use infra_delegate pattern

2. **infrastructure/credential_validator.py** (4 occurrences)
   - Handles all credential validation
   - Security-critical component
   - **Action**: Update to use centralized credential management

3. **adapters/session/unified_session_manager.py** (4 occurrences)
   - Session management for all services
   - **Action**: Integrate with infrastructure delegate

### MEDIUM PRIORITY - Package Infrastructure
Part of TidyLLM package, should be fixed but less urgent:

4. **packages/tidyllm/infrastructure/connection_pool.py** (5 occurrences)
   - TidyLLM's connection pooling
   - **Action**: Align with main infrastructure patterns

5. **packages/tidyllm/infrastructure/tools/mlflow_viewer.py** (2 occurrences)
   - MLflow monitoring tool
   - **Action**: Use infra delegate for connections

6. **packages/tidyllm/infrastructure/tools/mlflow_evidence_checker.py** (2 occurrences)
   - MLflow validation tool
   - **Action**: Use infra delegate for connections

### LOW PRIORITY - Scripts and Tools
Development/utility scripts, already partially fixed:

7. **scripts/tidyllm/execute_robots3_workflow.py** ✅ (Already fixed today)
8. **scripts/tools/verify_mlflow_postgres.py** ✅ (Already fixed today)
9. **scripts/tidyllm/document_database.py** (2 occurrences)
   - Database documentation tool
   - **Action**: Low priority, utility script

10. **scripts/tidyllm/pre_connection_manager.py** (Unknown count)
    - Pre-production connection manager
    - **Action**: May be deprecated, verify if still needed

11. **scripts/tools/collect_evidence.py** (Unknown count)
    - Evidence collection utility
    - **Action**: Low priority, development tool

### IGNORE - Meta Files
12. **add_future_fix_comments.py** - Script that added the comments
13. **debug_mlflow_config.py** - Debug utility
14. **packages/tidyllm/flow/examples/sop_flow.py** - Example code

## Recommended Action Plan

### Phase 1: Core Infrastructure (Week 1)
1. Create enhanced infrastructure service module
2. Refactor resilient_pool_manager.py
3. Update credential_validator.py
4. Modify unified_session_manager.py

### Phase 2: Package Alignment (Week 2)
1. Update TidyLLM connection_pool.py
2. Fix MLflow tools to use delegates

### Phase 3: Scripts Cleanup (As needed)
1. Evaluate which scripts are still needed
2. Update or archive as appropriate

## Pattern to Follow
Replace direct psycopg2 usage with infrastructure delegate:
```python
# OLD
import psycopg2
conn = psycopg2.connect(...)

# NEW
from infrastructure.infra_delegate import get_infra_delegate
infra = get_infra_delegate()
conn = infra.get_db_connection()
# ... use connection
infra.return_db_connection(conn)
```

## Technical Debt Summary
- **Total Files**: 14
- **High Priority**: 3 files
- **Medium Priority**: 3 files
- **Low Priority**: 5 files
- **Already Fixed**: 2 files
- **Can Ignore**: 3 files

## Next Steps
1. Start with HIGH PRIORITY files in main application
2. Ensure all use consistent infrastructure delegate pattern
3. Remove future_fix comments as each is resolved