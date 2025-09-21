# Migration Notes

## Date: 2025-09-20

## Purpose
These files were migrated due to hexagonal architecture violations or being outdated implementations.

## Migrated Files

### 1. domain/services/setup_service.py
- **Reason**: Critical hexagonal architecture violation
- **Issues**: 17 direct imports from infrastructure layer
- **Replacement**: domain/services/setup_service_refactored.py
- **Violations**:
  - Imports from infrastructure.yaml_loader
  - Imports from infrastructure.environment_manager
  - Imports from infrastructure.credential_validator
  - Imports from infrastructure.services.aws_service
  - And 13 more infrastructure imports

### 2. Backup Files (.backup)
- **Reason**: Old versions no longer needed
- **Files**:
  - packages/tidyllm/domain/entities/__init__.py.backup
  - packages/tidyllm/domain/services/__init__.py.backup
  - packages/tidyllm/infrastructure/tools/__init__.py.backup
  - packages/tidyllm/interfaces/__init__.py.backup
  - packages/tidyllm/interfaces/controllers/__init__.py.backup
  - packages/tidyllm/interfaces/demos/__init__.py.backup
  - packages/tidyllm/knowledge_systems/flow_agreements/__init__.py.backup
  - packages/tidyllm/workflows/types/__init__.py.backup
  - packages/tidyllm/portals/flow/flow_creator_v3.py.backup

## Architecture Compliance Status

### Before Migration
- Compliance Score: 28.6%
- Critical Violations: 2
- Warnings: 3

### After Migration
- setup_service.py removed from domain layer
- Should use setup_service_refactored.py instead
- Refactored version uses dependency injection

## Action Items for Full Compliance

### Still Needed:
1. Fix domain/services/setup_service_refactored.py (imports from adapters)
2. Fix domain/ports/outbound/setup_dependencies_port.py (imports from infrastructure)
3. Fix infrastructure/container.py (imports from adapters)
4. Fix infrastructure/script_generator.py (imports from adapters)
5. Create missing StoragePort and LLMPort definitions
6. Fix 23 circular dependencies (packages importing boto3 directly)

## Usage Instructions

To use the new setup service:
```python
# OLD (violates architecture):
from domain.services.setup_service import SetupService

# NEW (compliant):
from domain.services.setup_service_refactored import SetupService
from adapters.secondary.setup.setup_dependencies_adapter import SetupDependenciesAdapter

# Use with dependency injection
adapter = SetupDependenciesAdapter()
service = SetupService(adapter)
```

## Notes
- All migrated files are preserved here for reference
- Do not import or use these files in production code
- They serve as examples of what NOT to do in hexagonal architecture