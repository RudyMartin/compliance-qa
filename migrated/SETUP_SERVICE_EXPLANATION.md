# Setup Service - What It Does & Why It Was Migrated

## What setup_service.py Does

The `SetupService` is a core domain service that manages system setup and configuration. Its main responsibilities include:

### Key Functions:
1. **Architecture Configuration** - Determines and reports the system architecture pattern (4-Layer Clean, etc.)
2. **Environment Management** - Sets up AWS credentials, regions, and environment variables
3. **Credential Validation** - Validates AWS credentials and performs health checks
4. **Package Installation** - Manages Python package dependencies
5. **Script Generation** - Generates setup scripts for different environments
6. **Portal Configuration** - Manages Streamlit portal settings
7. **System Information** - Provides CPU, hostname, cloud provider info
8. **Service Status** - Checks availability of AWS services (S3, Bedrock, etc.)

## Why It Violates Hexagonal Architecture

### The Problem: 17 Direct Infrastructure Imports

```python
# VIOLATIONS IN DOMAIN LAYER:
from infrastructure.yaml_loader import get_settings_loader
from infrastructure.environment_manager import get_environment_manager
from infrastructure.credential_validator import validate_all_credentials
from infrastructure.services.aws_service import get_aws_service
# ... 13 more infrastructure imports
```

### Why This Is Wrong:

1. **Domain Should Be Pure Business Logic**
   - Domain layer should only contain business rules
   - It should NOT know about infrastructure details

2. **Breaks Dependency Rule**
   - Dependencies should flow: Infrastructure → Domain
   - NOT: Domain → Infrastructure (what setup_service.py does)

3. **Makes Testing Impossible**
   - Can't unit test domain logic without AWS/infrastructure
   - Need real AWS credentials just to test business logic

4. **Tight Coupling**
   - If infrastructure changes, domain breaks
   - Can't swap implementations (e.g., AWS to Azure)

## The Correct Solution: setup_service_refactored.py

The refactored version uses **Dependency Injection** through **Ports and Adapters**:

### Before (Wrong):
```python
class SetupService:
    def get_architecture_info(self):
        # WRONG: Direct infrastructure import
        from infrastructure.yaml_loader import get_settings_loader
        settings_loader = get_settings_loader()
```

### After (Correct):
```python
class SetupService:
    def __init__(self, dependencies: SetupDependenciesPort):
        # RIGHT: Inject dependencies through port interface
        self.deps = dependencies

    def get_architecture_info(self):
        # Uses injected dependency, not direct import
        config = self.deps.load_configuration()
```

## Hexagonal Architecture Layers

```
┌──────────────────────────────────┐
│     Presentation (Portals)        │
├──────────────────────────────────┤
│      Domain (Pure Logic)          │ ← setup_service.py violates this
│   - Should have NO infrastructure │
│   - Only business rules           │
├──────────────────────────────────┤
│        Ports (Interfaces)         │
├──────────────────────────────────┤
│     Adapters (Implementations)    │
├──────────────────────────────────┤
│    Infrastructure (AWS, DB)       │
└──────────────────────────────────┘
```

## Migration Summary

### File Location:
- **Old**: `domain/services/setup_service.py`
- **Migrated To**: `migrated/domain/services/setup_service.py`
- **Replacement**: `domain/services/setup_service_refactored.py`

### Files That Need Updates:
These files still import the old setup_service and need to be updated:
1. portals/setup/new_setup_portal.py
2. portals/setup/lean_setup_portal.py
3. functionals/setup/tests/test_setup_functional.py
4. functionals/setup/tests/test_setup_portal.py
5. test_dependency_check.py
6. test_imports.py

### How to Fix Remaining Files:
```python
# Replace this:
from domain.services.setup_service import SetupService

# With this:
from domain.services.setup_service_refactored import SetupService
from adapters.secondary.setup.setup_dependencies_adapter import SetupDependenciesAdapter

# And use like this:
adapter = SetupDependenciesAdapter()
service = SetupService(adapter)
```

## Impact of Migration

### Before Migration:
- Compliance Score: 28.6%
- Domain Layer: VIOLATED ❌
- Testability: POOR ❌
- Flexibility: NONE ❌

### After Migration:
- Domain violations reduced by 1 major file
- Domain layer can be tested without infrastructure
- Infrastructure can be swapped without changing domain
- Follows proper hexagonal architecture

## Conclusion

The `setup_service.py` was migrated because it's a textbook example of what NOT to do in hexagonal architecture - a domain service directly importing and using infrastructure components. The refactored version properly uses dependency injection through ports and adapters, making the system maintainable, testable, and flexible.