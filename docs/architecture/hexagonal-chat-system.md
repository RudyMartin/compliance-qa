# Hexagonal Architecture - Chat System

## Overview
The chat system implements a clean hexagonal architecture pattern with clear separation between UI ports, domain logic, and infrastructure adapters. This design enables testing different chat modes (Direct, RAG, DSPy, Hybrid) while maintaining domain independence from infrastructure concerns.

## Architecture Diagram

```
         PRIMARY PORTS (User Side)                    SECONDARY PORTS (Infrastructure Side)
    ┌─────────────────────────────┐                 ┌──────────────────────────────┐
    │  chat_test_app.py (8520)    │                 │  IBedrock Interface          │
    │  chat_app.py (8502)         │                 │  IRAGSystem Interface        │
    │  (Streamlit UI Ports)       │                 │  IDSPyOptimizer Interface    │
    └──────────┬──────────────────┘                 └────────────▲─────────────────┘
               │                                                  │
               ▼                                                  │
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                         DOMAIN CORE (Application Hexagon)                │
    │  ┌────────────────────────────────────────────────────────────────────┐ │
    │  │                    UnifiedChatManager                              │ │
    │  │  ┌──────────────────────────────────────────────────────────┐    │ │
    │  │  │  Business Rules:                                         │    │ │
    │  │  │  • Chat mode selection (DIRECT/RAG/DSPY/HYBRID/CUSTOM)  │    │ │
    │  │  │  • Message processing logic                              │    │ │
    │  │  │  • Context management                                    │    │ │
    │  │  │  • Response orchestration                                │    │ │
    │  │  └──────────────────────────────────────────────────────────┘    │ │
    │  └────────────────────────────────────────────────────────────────────┘ │
    └──────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                         ADAPTERS (Infrastructure Layer)                   │
    │                                                                           │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐    │
    │  │ BedrockAdapter    │  │ RAGAdapter       │  │ DSPyAdapter        │    │
    │  │ ─────────────────│  │ ─────────────────│  │ ──────────────────│    │
    │  │ • AWS Bedrock     │  │ • ChromaDB       │  │ • Prompt Library   │    │
    │  │ • Claude models   │  │ • PostgreSQL     │  │ • Optimization     │    │
    │  │ • Titan models    │  │ • Vector search  │  │ • Few-shot learns  │    │
    │  └──────────────────┘  └──────────────────┘  └────────────────────┘    │
    │                                                                           │
    │  ┌────────────────────────────────────────────────────────────────────┐ │
    │  │                    InfraDelegate (Adapter Orchestrator)             │ │
    │  │  • Manages all infrastructure connections                           │ │
    │  │  • Connection pooling (ResilientPoolManager)                       │ │
    │  │  • Credential management (from settings.yaml)                      │ │
    │  └────────────────────────────────────────────────────────────────────┘ │
    └──────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Primary Ports (User Interface)
- **chat_test_app.py** (Port 8520): Test interface for chat functionality
- **chat_app.py** (Port 8502): Main production chat interface
- Both implemented as Streamlit web applications

### Domain Core
**UnifiedChatManager** - Central orchestration service containing:
- Chat mode routing logic
- Message processing pipelines
- Context and history management
- Response generation strategies

### Secondary Ports (Infrastructure Interfaces)
- **IBedrock**: Interface for LLM operations
- **IRAGSystem**: Interface for retrieval-augmented generation
- **IDSPyOptimizer**: Interface for prompt optimization

### Adapters
- **BedrockAdapter**: AWS Bedrock integration (Claude, Titan models)
- **RAGAdapter**: Vector database integration (ChromaDB, PostgreSQL)
- **DSPyAdapter**: Prompt optimization and few-shot learning
- **InfraDelegate**: Centralized infrastructure management

## Chat Modes

### 1. DIRECT Mode
- Simple Q&A without additional context
- Direct LLM calls via Bedrock
- Fastest response time

### 2. RAG Mode
- Retrieval-Augmented Generation
- Searches vector database for context
- Enriches responses with relevant information

### 3. DSPy Mode
- Optimized prompts for better responses
- Few-shot learning examples
- Automatic prompt engineering

### 4. HYBRID Mode
- Intelligent mode selection
- Combines multiple approaches
- Optimal for complex queries

### 5. CUSTOM Mode
- User-defined processing chains
- Workflow integration
- Specialized task execution

## Data Flow

1. **User Input** → UI Port (Streamlit app)
2. **UI** → Domain Service (UnifiedChatManager.chat())
3. **Domain** → Port Interface (e.g., IBedrock)
4. **Port** → Adapter Implementation (BedrockAdapter)
5. **Adapter** → External Service (AWS Bedrock)
6. **Response** flows back through same layers

## Dependency Rules

- Dependencies point **INWARD** only
- Domain knows nothing about UI or Infrastructure
- Adapters implement domain interfaces
- UI depends on domain, never on infrastructure directly

## Key Benefits

1. **Testability**: Can swap real adapters with test doubles
2. **Flexibility**: Change infrastructure without touching domain
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Easy to add new chat modes or adapters
5. **Domain Isolation**: Business logic remains pure

## Configuration

Configuration is externalized to `settings.yaml`:
- Model preferences (Claude, GPT, Titan)
- Temperature settings
- API credentials
- Database connections

## Testing Strategy

- **Unit Tests**: Mock adapters, test domain logic
- **Integration Tests**: Test adapter implementations
- **E2E Tests**: Full stack with test infrastructure

## Implementation Files

- **Domain**: `packages/tidyllm/services/unified_chat_manager.py`
- **Adapters**: `infrastructure/services/bedrock_service.py`
- **Ports**: `portals/chat/chat_app.py`, `portals/chat/chat_test_app.py`
- **Config**: `infrastructure/settings.yaml`