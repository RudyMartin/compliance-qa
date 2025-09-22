# The Real Problem: We Created Stateful Coupling

## What We Did Wrong

We stored the infrastructure delegate as an instance variable (`self.infra`) everywhere:

```python
class SomeAdapter:
    def __init__(self):
        self.infra = get_infra_delegate()  # ❌ WRONG - Stateful coupling

    def some_method(self):
        conn = self.infra.get_db_connection()
```

## Why This Is Bad

1. **Stateful Coupling**: Each class now holds a reference to infrastructure
2. **Testing Nightmare**: Need to mock `self.infra` on every instance
3. **Hidden Dependencies**: Constructor doesn't show infrastructure dependency
4. **Lifecycle Issues**: What if infra delegate needs to be refreshed?

## What We Should Have Done

### Option 1: Dependency Injection (BEST)
```python
class SomeAdapter:
    def __init__(self, infra_delegate=None):
        self.infra = infra_delegate or get_infra_delegate()
```

### Option 2: Stateless Calls (SIMPLE)
```python
class SomeAdapter:
    def some_method(self):
        infra = get_infra_delegate()  # Get fresh each time
        conn = infra.get_db_connection()
        try:
            # work
        finally:
            infra.return_db_connection(conn)
```

### Option 3: Direct Pattern (SIMPLEST)
```python
# For scripts, just use psycopg2 directly with good practices
import psycopg2

def get_connection():
    # Read config
    return psycopg2.connect(...)
```

## The Wrapper Anti-Pattern

We created multiple wrapper classes to adapt interfaces:

```python
class DelegatePool:  # ❌ Unnecessary wrapper
    def __init__(self, infra):
        self.infra = infra

    def getconn(self):
        return self.infra.get_db_connection()

    def putconn(self, conn):
        self.infra.return_db_connection(conn)
```

This is a code smell - we're creating adapters for adapters!

## Import Path Confusion

We also confused relative imports:
- `from ..infra_delegate` - Wrong, goes up too far
- `from .infra_delegate` - Right for same directory
- `from infrastructure.infra_delegate` - Clear absolute import

## The Real Fix Needed

### 1. Remove Instance Variables
Change from:
```python
self.infra = get_infra_delegate()
```

To either dependency injection or stateless calls.

### 2. Remove Wrapper Classes
Don't create `DelegatePool`, `ConnectionWrapper`, etc. Either:
- Update calling code to use new interface
- Or keep old interface (psycopg2) for simplicity

### 3. Clarify Import Strategy
- Use absolute imports for clarity
- Avoid deep relative imports (`....`)

## Recommendation: Strategic Rollback

### Keep:
✅ Infrastructure delegate concept (it's good)
✅ Error handling improvements
✅ Documentation improvements

### Fix:
⚠️ Remove `self.infra` pattern - use dependency injection
⚠️ Remove unnecessary wrapper classes
⚠️ Simplify import paths

### Revert:
❌ Complex wrappers in scripts
❌ Forced delegate usage where psycopg2 is simpler

## The Lesson

**Perfect architecture < Pragmatic code**

We tried to force a pattern everywhere instead of applying it judiciously. The infrastructure delegate is a good pattern, but we implemented it poorly by:
1. Creating stateful coupling with `self.infra`
2. Building wrapper classes instead of updating interfaces
3. Overcomplicating simple scripts

The fix is not to abandon the pattern, but to implement it correctly with proper dependency injection and without unnecessary adapters.