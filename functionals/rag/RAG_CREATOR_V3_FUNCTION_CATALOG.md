# RAG Creator V3 Function Catalog
**File**: `packages/tidyllm/knowledge_systems/migrated/portal_rag/rag_creator_v3.py`
**Date**: 2025-09-20
**Architecture Status**: ⚠️ VIOLATES HEXAGONAL ARCHITECTURE

## Function Inventory

### Core Portal Class: `RAGCreatorV3Portal`

#### Initialization & Setup
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `__init__()` | Initialize portal with V2 session state and UnifiedRAGManager | Constructor | None | None |
| `_init_session_manager()` | Initialize USM session manager | Private | `Optional[UnifiedSessionManager]` | None |
| `_get_available_rag_systems()` | Get all available RAG systems with capabilities | Private | `Dict[str, Dict[str, Any]]` | None |

#### Main Rendering Functions
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `render_portal()` | Main portal rendering orchestrator | Public | None | None |
| `_render_custom_css()` | Apply custom CSS styling | Private | None | None |
| `_render_navigation_sidebar()` | Render sidebar navigation menu | Private | None | None |

#### CRUD Operations (Create, Read, Update, Delete)
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `_render_browse_rag_systems()` | Browse/Read RAG systems interface | Private | None | None |
| `_render_create_rag_system()` | Create new RAG system interface | Private | None | None |
| `_render_update_rag_system()` | Update existing RAG system interface | Private | None | None |
| `_render_delete_rag_system()` | Delete RAG system interface | Private | None | None |
| `_create_rag_system(sys_type, config)` | Execute RAG system creation | Private | `Dict[str, Any]` | `RAGSystemType`, `Dict[str, Any]` |
| `_update_rag_system(system_id, config)` | Execute RAG system update | Private | `Dict[str, Any]` | `str`, `Dict[str, Any]` |
| `_delete_rag_system(system_id, action)` | Execute RAG system deletion | Private | `Dict[str, Any]` | `str`, `str` |

#### Health & Monitoring Functions
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `_render_health_dashboard()` | Render health monitoring dashboard | Private | None | None |
| `_check_system_availability(sys_type)` | Check if RAG system is available | Private | `bool` | `RAGSystemType` |
| `_get_system_health(sys_type)` | Get detailed health metrics for system | Private | `Dict[str, Any]` | `RAGSystemType` |
| `_refresh_all_systems()` | Refresh all system health statuses | Private | None | None |
| `_run_comprehensive_health_check()` | Run complete health assessment | Private | None | None |
| `_refresh_system_health(sys_type)` | Refresh single system health | Private | None | `RAGSystemType` |
| `_run_deep_health_check(sys_type)` | Run deep health analysis | Private | None | `RAGSystemType` |

#### Performance & Optimization
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `_render_tailor_optimize()` | Render optimization interface | Private | None | None |
| `_render_performance_tuning(selected_system)` | Render performance tuning UI | Private | None | `Dict[str, Any]` |
| `_render_ab_testing(selected_system)` | Render A/B testing interface | Private | None | `Dict[str, Any]` |
| `_render_custom_configuration(selected_system)` | Render custom config interface | Private | None | `Dict[str, Any]` |
| `_render_optimization_history(selected_system)` | Show optimization history | Private | None | `Dict[str, Any]` |

#### Utility & Helper Functions
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `_render_rag_system_card(sys_type, sys_info, available, detailed)` | Render system info card | Private | None | `RAGSystemType`, `Dict[str, Any]`, `bool`, `bool=False` |
| `_get_system_specific_config(sys_type)` | Get configuration for specific system | Private | `Dict[str, Any]` | `RAGSystemType` |
| `_get_existing_rag_instances()` | Get list of existing RAG instances | Private | `List[Dict[str, Any]]` | None |
| `_display_operation_result(result)` | Display operation result to user | Private | None | `Dict[str, Any]` |
| `_show_system_logs(sys_type)` | Show system logs | Private | None | `RAGSystemType` |
| `_generate_system_report()` | Generate comprehensive system report | Private | None | None |

#### Metrics & Analytics
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `_get_average_response_time()` | Get average response time metric | Private | `int` | None |
| `_get_overall_success_rate()` | Get overall success rate metric | Private | `float` | None |
| `_get_total_queries_today()` | Get today's query count | Private | `int` | None |
| `_get_health_trend_data()` | Get health trend data for charts | Private | `Dict[str, List[float]]` | None |

#### Module Entry Point
| Function | Purpose | Type | Data Type | Required Parameters |
|----------|---------|------|-----------|-------------------|
| `main()` | Module entry point | Module | None | None |

## Architecture Compliance Analysis

### ❌ CRITICAL ARCHITECTURE VIOLATIONS

#### 1. Direct Infrastructure Imports (Lines 22-34)
```python
from tidyllm.core.settings import settings                    # VIOLATION
from tidyllm.core.resources import get_resources              # VIOLATION
from tidyllm.core.state import (...)                         # VIOLATION
from tidyllm.services.unified_rag_manager import ...         # VIOLATION
from tidyllm.infrastructure.session.unified import ...       # VIOLATION
```

**Issue**: Portal (UI layer) directly imports infrastructure and services without using delegates.

#### 2. Missing Delegate Pattern
- No delegate interfaces for infrastructure access
- Direct instantiation of `UnifiedRAGManager` and `UnifiedSessionManager`
- Portal has business logic mixed with UI logic

#### 3. Architectural Layer Violations
- **Portal Layer** → **Infrastructure Layer**: Direct import violation
- **Portal Layer** → **Service Layer**: Direct import violation
- **Portal Layer** → **Core Layer**: Direct import violation

### ✅ POSITIVE ARCHITECTURE ASPECTS

1. **Single Responsibility**: Each function has a clear, specific purpose
2. **Interface Segregation**: Functions are well-separated by concern
3. **Comprehensive CRUD**: Full Create, Read, Update, Delete operations
4. **Health Monitoring**: Robust system health checking
5. **Performance Metrics**: Built-in analytics and monitoring

## Summary

**Total Functions**: 31 functions across 7 functional categories
**Architecture Compliance**: 0% - Complete violation of hexagonal architecture
**Recommended Action**: Refactor to use delegate pattern for all infrastructure access

### Required Refactoring
1. Create RAG portal delegate interfaces
2. Remove all direct infrastructure imports
3. Implement proper dependency injection
4. Separate business logic from UI logic
5. Use delegate pattern for all external service access

**Priority**: HIGH - This portal cannot be used in production without architectural refactoring.