# Architecture Rules for QA-Shipping

## Core Principle: Strict Layer Separation

### Rule 1: NO Infrastructure Imports Outside Infrastructure Layer

**The Rule:**
```
Application Layer (Services/Managers) → CANNOT import from infrastructure
Domain Layer → CANNOT import from infrastructure
Packages (tidyllm) → CANNOT import from infrastructure (except delegates)
```

**Allowed Pattern: Use Delegates**
```
Application/Domain/Package → Delegate → Infrastructure
```

## Layer Rules

### 1. Domain Layer (Pure Business Logic)
- ❌ CANNOT import from infrastructure
- ❌ CANNOT import from adapters
- ❌ CANNOT import boto3 or any AWS SDK
- ✅ CAN define port interfaces
- ✅ CAN use dependency injection

### 2. Application Layer (Use Cases/Orchestration)
- ❌ CANNOT import from infrastructure directly
- ✅ CAN import from domain
- ✅ CAN use delegates (tidyllm.infrastructure.*_delegate)
- ✅ CAN orchestrate between services

### 3. Infrastructure Layer
- ✅ CAN import boto3 and AWS SDKs
- ✅ CAN implement ports
- ❌ CANNOT import from domain services
- ✅ CAN import from domain ports

### 4. Package Layer (tidyllm)
- ❌ CANNOT import from parent infrastructure
- ✅ MUST use delegates for infrastructure access
- ✅ CAN define its own infrastructure delegates

## The Delegate Pattern (Our Standard)

### What is a Delegate?
A delegate is a thin wrapper that provides infrastructure access without direct imports:

```python
# WRONG - Direct infrastructure import
from infrastructure.services.bedrock_service import get_bedrock_service
service = get_bedrock_service()

# RIGHT - Use delegate
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate
delegate = get_bedrock_delegate()
```

### Current Delegates
1. `bedrock_delegate.py` - Bedrock/LLM operations
2. `s3_delegate.py` - S3 storage operations
3. `aws_delegate.py` - General AWS operations

## Examples

### ❌ WRONG - Application importing infrastructure
```python
# packages/tidyllm/services/unified_chat_manager.py
from infrastructure.services.aws_service import get_aws_service  # VIOLATION!
```

### ✅ RIGHT - Application using delegate
```python
# packages/tidyllm/services/unified_chat_manager.py
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate
delegate = get_bedrock_delegate()
response = delegate.invoke_model(message, model_id)
```

### ❌ WRONG - Domain importing infrastructure
```python
# domain/services/some_service.py
from infrastructure.yaml_loader import get_settings_loader  # VIOLATION!
```

### ✅ RIGHT - Domain using dependency injection
```python
# domain/services/some_service.py
class SomeService:
    def __init__(self, dependencies: SomeDependenciesPort):
        self.deps = dependencies  # Injected, not imported
```

## Enforcement

### Validation Script
Run regularly to check compliance:
```bash
python functionals/validate_architecture_compliance.py
```

### CI/CD Check
Add to pipeline to prevent violations:
```yaml
- name: Architecture Compliance Check
  run: |
    python functionals/validate_architecture_compliance.py
    if [ $? -ne 0 ]; then
      echo "Architecture violations detected!"
      exit 1
    fi
```

## Benefits of This Approach

1. **Testability**: Can mock delegates easily
2. **Package Independence**: tidyllm works without parent infrastructure
3. **Clear Boundaries**: Each layer has clear responsibilities
4. **Maintainability**: Changes don't cascade across layers
5. **Consistency**: One pattern throughout the codebase

## Current Violations to Fix

1. ✅ ~~domain/services/setup_service.py~~ (FIXED - moved to migrated/)
2. ❌ packages/tidyllm/services/unified_chat_manager.py (lines 173-174)
3. ❌ infrastructure/container.py (imports from adapters)
4. ❌ infrastructure/script_generator.py (imports from adapters)

## Remember

**When in doubt, use a delegate!**

If you need infrastructure access from application or domain layers, create or use a delegate. Never import infrastructure directly.