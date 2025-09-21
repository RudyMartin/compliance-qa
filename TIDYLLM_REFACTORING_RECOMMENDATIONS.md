# TidyLLM Package - Code That Should Move Elsewhere

## Summary
TidyLLM has grown into a monolithic package with 27 top-level directories. Several components should be moved to maintain clean architecture.

## 1. SCRIPTS - Should Move to `/scripts` or `/tools` ❌

**Location**: `packages/tidyllm/scripts/`
**Contains**: 30+ standalone scripts
**Problem**: Scripts are executables, not library code

### Examples that should move:
```
packages/tidyllm/scripts/
├── check_aws_config.py       → /tools/aws/check_config.py
├── demo_mcp_integration.py   → /demos/mcp_integration.py
├── execute_robots3_workflow.py → /workflows/executors/robots3.py
├── test_s3_file_upload.py    → /tests/integration/s3_upload.py
└── pre_connection_manager.py → /tools/connection/pre_manager.py
```

## 2. PORTALS - Should Move to Main `/portals` ❌

**Location**: `packages/tidyllm/portals/`
**Contains**: Portal implementations
**Problem**: Portals are presentation layer, not package code

### Should move:
```
packages/tidyllm/portals/dspy_configurator.py → /portals/dspy/configurator.py
```

## 3. DOMAIN Services - Should Move to `/domain/services` ⚠️

**Location**: `packages/tidyllm/domain/services/`
**Contains**: Business logic services
**Problem**: Domain logic should be in main domain layer, not in package

### Should move:
```
packages/tidyllm/domain/services/
├── compliance_service.py      → /domain/services/compliance_service.py
├── risk_screening_service.py  → /domain/services/risk_screening_service.py
└── model_risk_analysis.py     → /domain/services/model_risk_analysis.py
```

## 4. Direct boto3 Imports - Should Use Delegates ❌

**Files violating delegate pattern** (20+ files):
```python
# WRONG - These files import boto3 directly:
packages/tidyllm/cli.py
packages/tidyllm/admin/credential_loader.py
packages/tidyllm/gateways/corporate_llm_gateway.py
packages/tidyllm/scripts/s3_flow_parser.py

# Should use delegates instead:
from tidyllm.infrastructure.s3_delegate import get_s3_delegate
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate
```

## 5. TEST Files - Should Move to `/tests` ❌

**Scattered test files in package**:
```
packages/tidyllm/tests/           → /tests/tidyllm/
packages/tidyllm/scripts/test_*.py → /tests/integration/
```

## 6. Web/Presentation - Questionable Location ⚠️

**Location**: `packages/tidyllm/web/` and `packages/tidyllm/presentation/`
**Problem**: UI/presentation typically belongs outside core package

## 7. Data Files - Should Move to `/data` or `/resources` ⚠️

**Location**: `packages/tidyllm/data/`
**Problem**: Data files bloat the package

## Recommended New Structure

### What SHOULD Stay in tidyllm Package:
```
packages/tidyllm/
├── infrastructure/      ✅ Delegates and infrastructure interfaces
│   ├── bedrock_delegate.py
│   ├── s3_delegate.py
│   └── aws_delegate.py
├── services/           ✅ Application services (orchestration)
│   ├── unified_chat_manager.py
│   └── unified_rag_manager.py
├── knowledge_systems/  ✅ RAG and knowledge management
├── validators/         ✅ Input/output validation
├── utils/             ✅ Utility functions
├── gateways/          ✅ External service gateways
└── adapters/          ✅ Interface adapters
```

### What SHOULD Move Out:
```
MOVE TO → /scripts/
  - packages/tidyllm/scripts/*

MOVE TO → /portals/
  - packages/tidyllm/portals/*

MOVE TO → /domain/services/
  - packages/tidyllm/domain/services/*

MOVE TO → /tests/
  - packages/tidyllm/tests/*
  - packages/tidyllm/scripts/test_*.py

MOVE TO → /demos/ or /examples/
  - packages/tidyllm/scripts/demo_*.py
  - packages/tidyllm/flow/examples/*

MOVE TO → /data/ or /resources/
  - packages/tidyllm/data/*

CONSIDER MOVING → /workflows/
  - packages/tidyllm/workflows/*
  - packages/tidyllm/workflow_configs/*
```

## Critical Issues to Fix

### 1. boto3 Direct Imports (20+ files)
These violate the delegate pattern and should be fixed:
```python
# Files to fix:
- cli.py
- admin/credential_loader.py
- gateways/corporate_llm_gateway.py
- scripts/s3_flow_parser.py
- knowledge_systems/adapters/judge_rag/judge_rag_adapter.py
# ... and 15+ more
```

### 2. Domain Logic in Package
Domain services should be in main `/domain` layer, not inside package.

### 3. Scripts Mixed with Library Code
Scripts are executables and shouldn't be packaged with library code.

## Impact Assessment

### High Priority (Breaks Architecture):
1. ❌ Direct boto3 imports (use delegates)
2. ❌ Domain services in package (move to /domain)

### Medium Priority (Organization):
1. ⚠️ Scripts in package (move to /scripts)
2. ⚠️ Tests in package (move to /tests)

### Low Priority (Nice to Have):
1. 📁 Data files (move to /data)
2. 📁 Examples/demos (move to /demos)

## Benefits of Refactoring

1. **Smaller Package Size**: Remove scripts, tests, data
2. **Clear Boundaries**: Library vs executables
3. **Better Architecture**: Domain logic in domain layer
4. **Consistent Patterns**: All use delegates, no direct boto3
5. **Easier Testing**: Tests separate from code
6. **Cleaner Imports**: `from tidyllm.services` not `from tidyllm.scripts`

## Migration Plan

### Phase 1: Fix Architecture Violations
- Replace boto3 imports with delegates
- Move domain services to /domain

### Phase 2: Reorganize Structure
- Move scripts to /scripts
- Move tests to /tests
- Move portals to /portals

### Phase 3: Clean Up
- Move data files
- Move examples/demos
- Update all imports

## Conclusion

TidyLLM has become a "kitchen sink" package with 27 directories. To maintain clean architecture:
- **Move out**: Scripts, tests, portals, domain logic, data files
- **Keep in**: Services, validators, utils, delegates, adapters
- **Fix**: 20+ files using boto3 directly instead of delegates

This will create a focused, maintainable package that follows your established patterns.