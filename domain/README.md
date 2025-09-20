# Domain Layer

## Purpose
The domain layer contains the core business logic and rules of the application. It is completely independent of any framework, database, or external service.

## Contents

### Models (`/models`)
Pure domain entities representing core business concepts:
- `Portal` - Portal configuration and management
- `Configuration` - System configuration
- `Credentials` - Authentication and authorization

### Ports (`/ports`)
Interfaces defining how the domain interacts with the outside world:

#### Inbound Ports (`/ports/inbound`)
Use case interfaces that the application layer implements:
- `SetupUseCasePort` - Environment setup operations
- `PortalManagementPort` - Portal lifecycle management
- `ChatUseCasePort` - Chat functionality

#### Outbound Ports (`/ports/outbound`)
Repository interfaces that adapters implement:
- `PortalRepositoryPort` - Portal persistence
- `ConfigurationRepositoryPort` - Configuration storage
- `DocumentRepositoryPort` - Document operations
- `ComplianceRepositoryPort` - Compliance rules

### Value Objects (`/value_objects`)
Immutable objects representing domain concepts without identity.

### Domain Services (`/services`)
Stateless services containing domain logic that doesn't naturally fit in entities.

## Rules

1. **NO framework dependencies** - Pure Python only
2. **NO infrastructure concerns** - No database, file system, or network code
3. **Business logic only** - Focus on what, not how
4. **Immutable when possible** - Use dataclasses and value objects
5. **Rich domain models** - Entities should contain business logic, not just data

## Testing

All domain logic should be testable with simple unit tests that require no mocking of infrastructure concerns.