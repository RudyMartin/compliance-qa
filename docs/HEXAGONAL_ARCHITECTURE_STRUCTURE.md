# Hexagonal Architecture Structure - qa-shipping

## Overview
The qa-shipping portal system now implements proper hexagonal architecture principles with **physical separation** of layers. This structure supports clean boundaries, dependency inversion, and future architectural evolution.

## 🏗️ **Directory Structure**

```
qa-shipping/                    # 🏠 PROJECT ROOT
├── portals/                   # 🎯 PRESENTATION LAYER (External)
│   ├── setup/                 # ⚙️ Setup Portal (8511)
│   │   └── setup_portal.py
│   ├── chat/                  # 💬 Chat Portals (8502)
│   ├── rag/                   # 📚 RAG Portals (8506, 8525)
│   ├── flow/                  # 🔄 Flow Portal (8550)
│   ├── services/              # 🔧 Services Portal (8505)
│   └── dashboard/             # 📊 Dashboard Portal (8501)
│
├── infrastructure/            # ⚙️ INFRASTRUCTURE LAYER
│   ├── environment_manager.py # Centralized env/credential management
│   ├── credential_validator.py# Async validation system
│   └── portal_config.py      # Portal registry & orchestration
│
├── scripts/                   # 🚀 AUTOMATION LAYER
│   ├── validate_environment.py
│   └── portal_startup.py
│
├── common/                    # 🔧 COMMON UTILITIES (Foundational)
│   └── utilities/             # Path management, shared tools
├── tidyllm/                   # 🧠 CORE BUSINESS LOGIC (Package 1)
├── tlm/                       # 🧠 CORE BUSINESS LOGIC (Package 2)
└── tidyllm-sentence/          # 🧠 CORE BUSINESS LOGIC (Package 3)
```

## 🔄 **Hexagonal Architecture Principles**

### 1. **Dependency Inversion** ✅
```
portals/ (Presentation)
    ↓ depends on
config/ (Infrastructure)
    ↓ depends on
tidyllm/, tlm/, tidyllm-sentence/ (Core Business Logic)
```

**NOT the other way around:**
- Core packages **NEVER** depend on portals
- Business logic remains **pure and isolated**
- Infrastructure adapts to business needs

### 2. **Physical Layer Separation** ✅
- **Presentation Layer**: `portals/` - **OUTSIDE** core packages
- **Infrastructure Layer**: `infrastructure/` - Adapters and integration
- **Business Logic**: `tidyllm/`, `tlm/`, `tidyllm-sentence/` - Pure domain
- **Common Layer**: `common/` - Foundational utilities and shared tools

### 3. **Clean Boundaries** ✅
- **Ports**: Defined interfaces in infrastructure layer
- **Adapters**: Implementation in infrastructure layer
- **Domain**: Business logic isolated in core packages

## 🎯 **Portal Layer (Presentation)**

### External Presentation Layer Benefits:
1. **Clean Separation**: UI/UX completely separate from business logic
2. **Testability**: Core logic testable without UI dependencies
3. **Flexibility**: Can replace UI framework without touching core
4. **Scalability**: Multiple UI implementations possible

### Portal Structure:
```python
# Each portal follows this pattern:
portals/{portal_name}/{portal_name}_portal.py

# Import pattern (dependency inversion):
from infrastructure.environment_manager import get_environment_manager
from tidyllm.core_logic import SomeBusinessLogic
```

## ⚙️ **Infrastructure Layer**

### Responsibility:
- **Adapt** external services to business needs
- **Manage** configuration and credentials
- **Provide** clean interfaces to presentation layer

### Components:
- `environment_manager.py`: Configuration adapter
- `credential_validator.py`: Security adapter
- `portal_config.py`: Portal orchestration adapter

## 🧠 **Business Logic Layer (Core Packages)**

### Packages:
- **tidyllm**: Primary business logic
- **tlm**: Core TLM functionality
- **tidyllm-sentence**: Sentence processing logic

### Principles:
- **No dependencies** on presentation or infrastructure
- **Pure business rules** and domain logic
- **Framework agnostic** - can work with any UI/persistence

## 🔄 **Communication Flow**

### 1. **User Interaction**:
```
User → Portal (Presentation) → Config (Infrastructure) → Core (Business Logic)
```

### 2. **Data Flow**:
```
Core Logic → Infrastructure Adapters → Presentation Layer → User
```

### 3. **Dependency Flow** (Inverted):
```
Presentation ←depends on← Infrastructure ←depends on← Core
```

## ✅ **Architecture Validation**

### Setup Portal Example:
The new Setup Portal demonstrates proper hexagonal architecture:

1. **External Location**: `portals/setup/setup_portal.py`
2. **Dependency Inversion**: Imports from `config/` and `tidyllm/`
3. **Clean Interface**: Uses configuration adapters, not direct imports
4. **Business Logic Separation**: UI logic separate from domain logic

### Health Check Endpoint:
```json
{
  "status": "healthy",
  "portal": "setup_portal",
  "port": 8511,
  "architecture": "external_presentation_layer",
  "timestamp": 1726829782.5
}
```

## 🚀 **Benefits Achieved**

### 1. **Maintainability**
- Clear separation of concerns
- Changes in UI don't affect business logic
- Infrastructure changes isolated

### 2. **Testability**
- Core logic testable in isolation
- Mock external dependencies easily
- Unit tests don't require UI

### 3. **Flexibility**
- Multiple UI implementations possible
- Easy to migrate to different frameworks
- A/B testing of different interfaces

### 4. **Scalability**
- Independent deployment of layers
- Horizontal scaling of presentation layer
- Core logic reusable across contexts

## 🎯 **Future Evolution Path**

### Phase 3: Service Layer Enhancement
With proper layer separation, we can now:
1. Add service abstractions between infrastructure and core
2. Implement domain events and messaging
3. Add cross-cutting concerns (logging, monitoring)

### Phase 4: Infrastructure Cleanup
1. Repository pattern implementation
2. External service adapters
3. Configuration management enhancement

### Phase 5: Portal Orchestration System
1. Service discovery
2. Load balancing
3. Health monitoring

## 📊 **Success Metrics**

### ✅ **Achieved**:
- Physical layer separation
- Dependency inversion
- Clean boundaries
- External presentation layer
- Working Setup Portal with architecture compliance

### 🎯 **Next Steps**:
- Migrate remaining portals to external structure
- Standardize portal interfaces
- Add service layer abstractions

---

**Architecture Status**: ✅ **HEXAGONAL COMPLIANT**

The qa-shipping system now follows proper hexagonal architecture principles with physical layer separation, setting the foundation for maintainable, testable, and scalable portal development.