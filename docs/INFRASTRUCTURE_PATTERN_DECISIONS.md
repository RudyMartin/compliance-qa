# Infrastructure Pattern Decisions

## Patterns We're Keeping

### 1. self.infra Pattern ✅

We're intentionally keeping the `self.infra = get_infra_delegate()` pattern in our adapters.

**Why it's good:**
- **Cleaner Code**: No need to call `get_infra_delegate()` in every method
- **Better Performance**: Single instance per adapter, not recreated each time
- **Dependency Injection Ready**: Can pass mock/test infra in constructor
- **Consistent Interface**: All adapters follow same pattern
- **Stateful Operations**: Some adapters need persistent infrastructure reference

**Example:**
```python
class SomeAdapter:
    def __init__(self, infra_delegate=None):
        self.infra = infra_delegate or get_infra_delegate()

    def some_method(self):
        conn = self.infra.get_db_connection()
        # Clean, simple, readable
```

### 2. DelegatePool Wrapper Pattern ✅

We're keeping the DelegatePool wrapper that adapts infra delegate to pool interface.

**Why it's good:**
- **Backward Compatibility**: Existing code expecting pool interface still works
- **Migration Path**: Smooth transition from psycopg2.pool to infra delegate
- **Interface Adapter**: Follows adapter pattern for interface compatibility
- **No Breaking Changes**: Don't need to rewrite all pool-using code

**Example:**
```python
class DelegatePool:
    def __init__(self, infra):
        self.infra = infra

    def getconn(self):
        return self.infra.get_db_connection()

    def putconn(self, conn):
        self.infra.return_db_connection(conn)
```

## What We Fixed

### Connection Management Pattern ✅

Changed from incorrect context manager usage to proper get/return pattern:

**Before (Wrong):**
```python
with self.infra.get_db_connection() as conn:  # ❌ Not a context manager!
    cursor = conn.cursor()
```

**After (Correct):**
```python
conn = self.infra.get_db_connection()
try:
    cursor = conn.cursor()
    # work
finally:
    self.infra.return_db_connection(conn)
```

### Import Paths ✅

Fixed relative imports that went too far up:

**Before (Wrong):**
```python
from ....infrastructure.infra_delegate import get_infra_delegate  # ❌ Too many dots!
```

**After (Correct):**
```python
from infrastructure.infra_delegate import get_infra_delegate  # ✅ Clear absolute import
```

## Architecture Benefits

### Hexagonal Architecture Compliance
- Infrastructure access only through delegate
- Clear separation of concerns
- Testable boundaries

### Practical Implementation
- Not overly purist - pragmatic choices
- Wrapper patterns where they make sense
- Instance variables for cleaner code

### Migration Strategy
- DelegatePool allows gradual migration
- No need to rewrite everything at once
- Backward compatibility maintained

## Summary

We're keeping both `self.infra` and `DelegatePool` patterns because they:
1. Make code cleaner and more maintainable
2. Provide backward compatibility
3. Enable proper dependency injection
4. Follow hexagonal architecture principles pragmatically
5. Don't force unnecessary rewrites

The key insight: **Good architecture is pragmatic, not dogmatic**. These patterns serve real purposes and make our codebase better.