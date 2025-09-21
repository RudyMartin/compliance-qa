# Architecture Compliance Action Plan

## Current State: 28.6% Compliance Score

### Critical Metrics
- **Passed**: 2/7 checks (Delegate Pattern, Test Structure)
- **Warnings**: 3/7 checks (Ports, Adapters, Dependencies)
- **Violations**: 2/7 checks (Domain Isolation, Infrastructure Independence)

## IMMEDIATE ACTIONS (Week 1)

### 1. Fix Domain Layer Violations [CRITICAL]

#### Files to Fix:
1. `domain/services/setup_service.py` - 16 infrastructure imports
2. `domain/services/setup_service_refactored.py` - imports from adapters
3. `domain/ports/outbound/setup_dependencies_port.py` - imports from infrastructure

#### Action Steps:
```bash
# Step 1: Remove the import in setup_dependencies_port.py
# The port should only define interfaces, no implementations

# Step 2: Fix setup_service_refactored.py
# Move the adapter import to constructor or factory

# Step 3: Migrate from setup_service.py to setup_service_refactored.py
find . -name "*.py" -exec grep -l "from domain.services.setup_service import" {} \; | xargs sed -i 's/from domain.services.setup_service/from domain.services.setup_service_refactored/g'

# Step 4: Delete old violating file
mv domain/services/setup_service.py domain/services/setup_service.py.backup
```

### 2. Fix Infrastructure Dependencies [CRITICAL]

#### Files to Fix:
1. `infrastructure/container.py` - imports from adapters
2. `infrastructure/script_generator.py` - imports from adapters

#### Solution:
Infrastructure should NEVER import from adapters. Refactor to:
- Use dependency injection
- Pass adapters as parameters
- Or move the functionality to a different layer

## HIGH PRIORITY ACTIONS (Week 2)

### 3. Define Missing Ports [HIGH]

Create these missing port definitions:

#### `domain/ports/outbound/storage_port.py`:
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class StoragePort(ABC):
    """Port for storage operations (S3)."""

    @abstractmethod
    def upload_file(self, file_path: str, key: str) -> bool:
        pass

    @abstractmethod
    def download_file(self, key: str, local_path: str) -> bool:
        pass

    @abstractmethod
    def list_objects(self, prefix: str) -> List[str]:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
```

#### `domain/ports/outbound/llm_port.py`:
```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMPort(ABC):
    """Port for LLM operations (Bedrock)."""

    @abstractmethod
    def invoke_model(self, prompt: str, model_id: Optional[str] = None) -> Optional[str]:
        pass

    @abstractmethod
    def list_models(self) -> List[Dict]:
        pass

    @abstractmethod
    def create_embedding(self, text: str) -> Optional[List[float]]:
        pass
```

### 4. Fix Circular Dependencies [HIGH]

23 files in packages directly import boto3. They should use delegates instead.

#### Most Critical:
- `packages/tidyllm/cli.py`
- `packages/tidyllm/admin/credential_loader.py`
- `packages/tidyllm/gateways/corporate_llm_gateway.py`

#### Solution:
Replace direct boto3 imports with delegate usage:
```python
# WRONG
import boto3
client = boto3.client('s3')

# RIGHT
from tidyllm.infrastructure.s3_delegate import get_s3_delegate
delegate = get_s3_delegate()
```

## MEDIUM PRIORITY ACTIONS (Week 3)

### 5. Improve Adapter Coverage [MEDIUM]

Currently only 2 proper adapters found. Need more:
- Create S3Adapter for StoragePort
- Create BedrockAdapter for LLMPort
- Ensure all ports have corresponding adapters

### 6. Documentation [MEDIUM]

Create architecture documentation:
```
docs/
  architecture/
    README.md - Overview of hexagonal architecture
    PORTS.md - List of all ports and their purpose
    ADAPTERS.md - List of all adapters and what they adapt
    DEPENDENCIES.md - Dependency rules and flow
```

## VALIDATION & MONITORING

### Daily Validation
```bash
# Add to pre-commit hook
python functionals/validate_architecture_compliance.py
```

### CI/CD Integration
```yaml
# .github/workflows/architecture.yml
name: Architecture Compliance
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python functionals/validate_architecture_compliance.py
```

## Success Metrics

### Target: 80%+ Compliance Score

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Domain Isolation | ❌ FAIL | ✅ PASS | CRITICAL |
| Infrastructure Independence | ❌ FAIL | ✅ PASS | CRITICAL |
| Port Definitions | ⚠️ WARN | ✅ PASS | HIGH |
| Adapter Implementation | ⚠️ WARN | ✅ PASS | HIGH |
| Circular Dependencies | ⚠️ WARN | ✅ PASS | MEDIUM |
| Delegate Pattern | ✅ PASS | ✅ PASS | DONE |
| Test Structure | ✅ PASS | ✅ PASS | DONE |

## Risk Assessment

### High Risk Issues
1. **Domain violations**: Makes testing impossible without infrastructure
2. **Circular dependencies**: Can cause runtime failures
3. **Missing ports**: Incomplete abstraction layer

### Medium Risk Issues
1. **Adapter coverage**: Reduces flexibility
2. **boto3 direct usage**: Violates package isolation

### Low Risk Issues
1. **Documentation**: Team confusion
2. **Test coverage**: Quality assurance gaps

## Timeline

### Week 1 (Immediate)
- [ ] Fix domain/services/setup_service.py
- [ ] Fix infrastructure imports
- [ ] Run validation to confirm fixes

### Week 2 (High Priority)
- [ ] Create missing ports
- [ ] Fix circular dependencies
- [ ] Achieve 60% compliance

### Week 3 (Medium Priority)
- [ ] Improve adapter coverage
- [ ] Add documentation
- [ ] Achieve 80% compliance

### Ongoing
- [ ] Daily validation checks
- [ ] Code review enforcement
- [ ] Team training

## Commands to Run

```bash
# 1. Check current compliance
python functionals/validate_architecture_compliance.py

# 2. Find all violations
grep -r "from infrastructure" domain/
grep -r "from domain" infrastructure/
grep -r "import boto3" packages/

# 3. Run tests after fixes
python -m pytest tests/
python functionals/bedrock/test_bedrock_functional.py
python functionals/s3/test_s3_functional.py

# 4. Generate compliance report
python functionals/validate_architecture_compliance.py > compliance_$(date +%Y%m%d).txt
```

## Conclusion

The codebase has working AWS integrations (Bedrock and S3 confirmed as REAL implementations), but the architecture needs significant refactoring:

- **28.6% compliance score** is critically low
- **2 critical violations** must be fixed immediately
- **23 circular dependencies** need resolution

Following this action plan will improve the compliance score to 80%+ within 3 weeks, ensuring maintainable, testable, and scalable architecture.