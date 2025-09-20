# Adapters Layer

## Purpose
The adapters layer converts between the application's internal representations and external formats. It implements the ports defined in the domain layer.

## Structure

### Primary Adapters (`/primary`)
Adapters that drive the application (incoming):

#### Web (`/primary/web`)
- Streamlit portals (formerly in `/portals`)
- REST APIs
- WebSocket handlers

#### CLI (`/primary/cli`)
- Command-line interfaces
- Script runners
- Setup utilities

#### API (`/primary/api`)
- REST endpoints
- GraphQL resolvers
- gRPC services

### Secondary Adapters (`/secondary`)
Adapters driven by the application (outgoing):

#### Database (`/secondary/database`)
- PostgreSQL adapters
- MongoDB adapters
- Redis adapters

#### File System (`/secondary/filesystem`)
- File readers/writers
- Script generators
- Configuration loaders

#### External Services (`/secondary/external`)
- AWS service adapters
- Bedrock integration
- Third-party APIs

#### Memory (`/secondary/memory`)
- In-memory repositories
- Cache implementations

#### YAML (`/secondary/yaml`)
- YAML configuration repositories
- Settings persistence

## Responsibilities

1. **Protocol translation** - Convert between internal and external formats
2. **Technology isolation** - Keep framework/library code here
3. **Error handling** - Convert external errors to domain exceptions
4. **Connection management** - Handle database connections, HTTP clients
5. **Data validation** - Validate external input before passing to application

## Rules

1. **Implement ports** - Each adapter must implement a port interface
2. **No business logic** - Only translation and technical concerns
3. **Dependency direction** - Depend on domain, never the reverse
4. **Testable** - Should be testable in isolation
5. **Replaceable** - Should be easily swappable for another implementation

## Testing

- Unit tests with mocked external dependencies
- Integration tests with real external systems (databases, APIs)
- Contract tests to ensure port compliance