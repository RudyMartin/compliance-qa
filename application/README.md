# Application Layer

## Purpose
The application layer orchestrates the flow of data and coordinates domain operations. It contains application-specific business logic but no domain logic.

## Contents

### Use Cases (`/use_cases`)
Implementation of inbound ports defining application operations:
- `SetupEnvironmentUseCase` - Orchestrates environment setup
- `PortalManagementUseCase` - Manages portal lifecycle
- `ChatUseCase` - Handles chat interactions

### Services (`/services`)
Application services that coordinate multiple use cases:
- `PortalOrchestrator` - Coordinates portal operations
- `SetupOrchestrator` - Manages setup workflow

### DTOs (`/dto`)
Data Transfer Objects for communication between layers.

## Responsibilities

1. **Transaction management** - Coordinate transactions across operations
2. **Use case orchestration** - Implement application workflows
3. **Data transformation** - Convert between domain models and DTOs
4. **Authorization** - Enforce access control (not authentication)
5. **Notification** - Trigger events and notifications

## Rules

1. **No framework code** - Keep framework-specific code in adapters
2. **Thin orchestration** - Delegate business logic to domain
3. **No direct infrastructure access** - Use ports and adapters
4. **Dependency injection** - Accept dependencies via constructor
5. **Stateless services** - No mutable state in services

## Dependencies

- Depends on: Domain layer (models and ports)
- Depended on by: Primary adapters (web, CLI, API)

## Testing

Application services should be tested with:
- Unit tests with mocked repositories
- Integration tests with in-memory adapters