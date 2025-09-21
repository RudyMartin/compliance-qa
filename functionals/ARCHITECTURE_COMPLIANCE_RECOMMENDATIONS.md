# Architecture Compliance Recommendations

## Executive Summary

After comprehensive analysis of Bedrock and S3 implementations, several critical architecture violations were identified that need immediate remediation to ensure proper hexagonal architecture compliance.

## Critical Violations Found

### 1. Domain Layer Direct Infrastructure Imports

#### **VIOLATION**: SetupService (domain/services/setup_service.py)
- **Severity**: HIGH
- **Issue**: 16 direct imports from infrastructure layer
- **Lines**: 29, 58, 101, 113, 121, 135, 189, 199, 214, 227, 236, 292, 336, 420, 421, 507, 549

```python
# VIOLATIONS:
from infrastructure.yaml_loader import get_settings_loader
from infrastructure.environment_manager import get_environment_manager
from infrastructure.credential_validator import validate_all_credentials
from infrastructure.services.aws_service import get_aws_service
# ... 12 more
```

**Impact**: Complete breakdown of hexagonal architecture - domain is tightly coupled to infrastructure.

### 2. Missing Port Definitions

#### **ISSUE**: Incomplete Port Interfaces
- **Location**: domain/ports/outbound/session_port.py
- **Missing**: UnifiedSessionPort class (referenced but not defined)
- **Impact**: Tests failing, incomplete abstraction layer

### 3. Inconsistent Adapter Patterns

#### **ISSUE**: Mixed Adapter Implementations
- Some services use proper adapters (e.g., UnifiedSessionAdapter)
- Others directly call infrastructure (e.g., SetupService)
- No consistent pattern across the codebase

### 4. Circular Dependencies Risk

#### **WARNING**: TidyLLM Package Dependencies
- TidyLLM delegates import parent infrastructure
- Parent infrastructure could potentially import TidyLLM
- Risk of circular dependency chain

## Recommendations

### Priority 1: Fix Domain Violations (IMMEDIATE)

#### 1.1 Refactor SetupService
**Status**: PARTIALLY COMPLETE
- ✅ Created: `setup_service_refactored.py` with proper dependency injection
- ✅ Created: Port interfaces in `setup_dependencies_port.py`
- ✅ Created: Adapter in `setup_dependencies_adapter.py`
- ❌ **TODO**: Migrate all usages to refactored version
- ❌ **TODO**: Delete original violating file

**Action Items**:
```bash
# 1. Update all imports
find . -name "*.py" -exec sed -i 's/from domain.services.setup_service/from domain.services.setup_service_refactored/g' {} \;

# 2. Run tests to verify
python -m pytest tests/

# 3. Remove old file
rm domain/services/setup_service.py
```

#### 1.2 Audit Other Domain Services
**Action**: Search for violations in all domain services

```python
# Script to find violations
import os
import re

def find_violations():
    violations = []
    domain_path = "domain/"

    for root, dirs, files in os.walk(domain_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    if 'from infrastructure' in content or 'from adapters' in content:
                        violations.append(filepath)

    return violations

# Run this to find all violations
```

### Priority 2: Complete Port Definitions (HIGH)

#### 2.1 Fix Missing UnifiedSessionPort
**Location**: domain/ports/outbound/session_port.py

Add the missing class:
```python
class UnifiedSessionPort(ABC):
    """Unified session port for all AWS services."""

    @abstractmethod
    async def get_s3_client(self) -> Any:
        """Get S3 client"""
        pass

    @abstractmethod
    async def get_bedrock_client(self) -> Any:
        """Get Bedrock client"""
        pass

    @abstractmethod
    async def get_credentials(self) -> Dict[str, Any]:
        """Get AWS credentials"""
        pass
```

#### 2.2 Create Comprehensive Port Registry
Create `domain/ports/port_registry.py`:
```python
"""
Central registry of all port interfaces.
This ensures consistency and prevents missing definitions.
"""

from .outbound.session_port import SessionPort, UnifiedSessionPort
from .outbound.storage_port import StoragePort
from .outbound.llm_port import LLMPort
from .outbound.setup_dependencies_port import SetupDependenciesPort

__all__ = [
    'SessionPort',
    'UnifiedSessionPort',
    'StoragePort',
    'LLMPort',
    'SetupDependenciesPort'
]
```

### Priority 3: Standardize Adapter Pattern (HIGH)

#### 3.1 Create Adapter Template
Create `adapters/adapter_template.py`:
```python
"""
Standard template for all adapters.
Copy this when creating new adapters.
"""

from abc import ABC
from typing import Any
from domain.ports.outbound.base_port import BasePort

class StandardAdapter(BasePort):
    """Standard adapter implementation."""

    def __init__(self, infrastructure_service: Any = None):
        """
        Initialize with optional infrastructure service.

        Args:
            infrastructure_service: The infrastructure service to wrap
        """
        self._service = infrastructure_service

        # Lazy initialization if not provided
        if self._service is None:
            self._service = self._get_default_service()

    def _get_default_service(self) -> Any:
        """Get default infrastructure service."""
        from infrastructure.services.some_service import get_some_service
        return get_some_service()

    # Implement all port methods here
```

#### 3.2 Enforce Adapter Usage
Create validation script:
```python
# validate_architecture.py
def validate_domain_imports():
    """Ensure domain never imports from infrastructure."""
    # Implementation here
    pass

def validate_adapters_exist():
    """Ensure all ports have corresponding adapters."""
    # Implementation here
    pass

# Add to CI/CD pipeline
```

### Priority 4: Fix Circular Dependencies (MEDIUM)

#### 4.1 Dependency Direction Rules
Establish clear rules:
```
Domain → Ports (interfaces only)
Adapters → Domain Ports + Infrastructure
Infrastructure → Nothing from Domain or Adapters
Packages → Infrastructure (through delegates)
```

#### 4.2 Package Isolation
- TidyLLM should NEVER be imported by infrastructure
- Infrastructure should NEVER import from packages
- Use delegates for package → infrastructure communication

### Priority 5: Testing Compliance (MEDIUM)

#### 5.1 Create Architecture Tests
Create `tests/test_architecture_compliance.py`:
```python
import ast
import os

class TestArchitectureCompliance:

    def test_no_infrastructure_imports_in_domain(self):
        """Domain should never import from infrastructure."""
        violations = []
        for filepath in self.get_domain_files():
            if self.has_infrastructure_import(filepath):
                violations.append(filepath)

        assert len(violations) == 0, f"Domain violations: {violations}"

    def test_all_ports_have_adapters(self):
        """Every port should have at least one adapter."""
        ports = self.get_all_ports()
        adapters = self.get_all_adapters()

        for port in ports:
            assert self.has_adapter(port, adapters), f"No adapter for {port}"

    def test_no_circular_dependencies(self):
        """Check for circular dependency chains."""
        # Implementation here
        pass
```

### Priority 6: Documentation (LOW)

#### 6.1 Architecture Decision Records (ADRs)
Create `docs/adr/` directory with:
- ADR-001-hexagonal-architecture.md
- ADR-002-dependency-injection.md
- ADR-003-port-adapter-pattern.md

#### 6.2 Developer Guidelines
Create `ARCHITECTURE_GUIDELINES.md`:
```markdown
# Architecture Guidelines

## Rules
1. Domain NEVER imports from infrastructure
2. All infrastructure access through ports/adapters
3. Use dependency injection for services
4. Mock implementations only for testing

## How to Add New Feature
1. Define port interface in domain/ports
2. Create adapter in adapters/
3. Implement service in infrastructure/
4. Wire together with dependency injection
```

## Implementation Plan

### Phase 1: Critical Fixes (Week 1)
- [ ] Complete SetupService migration
- [ ] Fix UnifiedSessionPort definition
- [ ] Run full test suite

### Phase 2: Compliance Validation (Week 2)
- [ ] Implement architecture validation scripts
- [ ] Add to CI/CD pipeline
- [ ] Fix all discovered violations

### Phase 3: Standardization (Week 3)
- [ ] Create adapter templates
- [ ] Refactor inconsistent adapters
- [ ] Document patterns

### Phase 4: Monitoring (Ongoing)
- [ ] Regular architecture audits
- [ ] Automated compliance checks
- [ ] Team training on patterns

## Success Metrics

1. **Zero Domain Violations**: No infrastructure imports in domain layer
2. **100% Port Coverage**: All ports have corresponding adapters
3. **Test Coverage**: Architecture tests pass 100%
4. **No Circular Dependencies**: Dependency graph is acyclic
5. **Documentation Complete**: All patterns documented

## Risk Mitigation

### Risk: Breaking Changes During Migration
**Mitigation**:
- Keep both versions during transition
- Gradual migration with feature flags
- Comprehensive test coverage

### Risk: Developer Confusion
**Mitigation**:
- Clear documentation
- Code examples
- Architecture workshops

### Risk: Performance Impact
**Mitigation**:
- Benchmark before/after
- Use lazy initialization
- Cache frequently used services

## Conclusion

While the current implementation has real, working AWS integrations (Bedrock and S3), the architecture violations pose significant risks:

1. **Maintainability**: Tight coupling makes changes difficult
2. **Testability**: Cannot unit test domain without infrastructure
3. **Flexibility**: Cannot swap implementations easily
4. **Team Scalability**: Violations set bad precedent

**Recommendation**: Prioritize Phase 1 fixes immediately to prevent further architectural degradation. The refactoring patterns have been proven with `setup_service_refactored.py` and should be applied consistently across the codebase.