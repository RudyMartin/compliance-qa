# TidyLLM Current Directory Structure

After refactoring, here's what remains in `packages/tidyllm/`:

## Directories (23 total)

### ✅ CORE - Should Stay
1. **infrastructure/** - Delegates (bedrock, s3, aws)
2. **services/** - Application services (UnifiedChatManager, UnifiedRAGManager)
3. **gateways/** - External service gateways (CorporateLLMGateway)
4. **validators/** - Input/output validation
5. **utils/** - Utility functions
6. **adapters/** - Interface adapters
7. **knowledge_systems/** - RAG and knowledge management
8. **interfaces/** - API interfaces (MCP, CLI)

### ⚠️ QUESTIONABLE - Consider Moving
9. **data/** - Data files (should move to /data or /resources)
10. **domain/** - Domain logic (should be in main /domain)
11. **domain_rag_system/** - Specific RAG implementation
12. **flow/** - Workflow definitions
13. **portals/** - Empty or minimal (already moved main files)
14. **presentation/** - UI/presentation layer
15. **rag2dag/** - Specific accelerator implementation
16. **review/** - Review related code
17. **scripts/** - Empty (files already moved)
18. **tests/** - Empty (files already moved)
19. **web/** - Web interface code
20. **workflow_configs/** - Configuration files
21. **workflows/** - Workflow implementations

### 🗑️ CAN REMOVE
22. **__pycache__/** - Python cache (auto-generated)
23. **tidyllm.egg-info/** - Package metadata (auto-generated)

## Status After Refactoring

### ✅ Already Moved:
- **admin/** → `migrated/tidyllm_admin/` (just moved)
- **scripts/** → `/scripts/tidyllm/`, `/scripts/demos/`, etc.
- **tests/** → `/tests/tidyllm/`, `/tests/integration/`
- **portals/** → `/portals/dspy/` (main files)
- **domain/services/** → `/domain/services/`

### 📁 Empty/Minimal Directories:
- **scripts/** - Empty (contents moved)
- **tests/** - Empty (contents moved)
- **portals/** - May be empty or minimal

## Recommendations

### High Priority - Move These:
1. **data/** → `/data/` or `/resources/`
2. **domain/** → Merge with main `/domain/`
3. **workflow_configs/** → `/configs/workflows/`
4. **workflows/** → `/workflows/`

### Medium Priority - Review & Decide:
1. **domain_rag_system/** - Is this core to tidyllm or separate?
2. **flow/** - Core feature or separate module?
3. **presentation/** - Should UI be in package?
4. **web/** - Web interface in package or separate?
5. **review/** - What is this for?

### Keep These (Core Functionality):
- ✅ infrastructure/
- ✅ services/
- ✅ gateways/
- ✅ validators/
- ✅ utils/
- ✅ adapters/
- ✅ knowledge_systems/
- ✅ interfaces/

## Final Structure Goal

```
packages/tidyllm/
├── infrastructure/     # Delegates only
├── services/          # App services
├── gateways/          # External gateways
├── validators/        # Validation
├── utils/            # Utilities
├── adapters/         # Adapters
├── knowledge_systems/ # RAG systems
└── interfaces/       # APIs (MCP, CLI)
```

Only 8 core directories instead of current 23!