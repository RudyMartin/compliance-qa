# Flow Portal Tab Versions

## Current Active Portal: flow_portal_v4.py

### V4 Tabs (Current)
- `t_create_flow_v4.py` - Card-based workflow builder
- `t_manage_flows_enhanced.py` - Enhanced CRUD with project resources
- `t_run_flows_v4.py` - Simple workflow execution
- `t_optimize_flows_v4.py` - Workflow optimization
- `t_ask_ai_v4.py` - AI advisor

### V3 Tabs (Legacy)
- `t_create_flow.py` - Original create tab
- `t_manage_flows.py` - Basic manage tab
- `t_run.py` - Original run tab
- `t_optimize.py` - Original optimize tab
- `t_ai_advisor.py` - Original AI advisor

## Script Discovery

The portal now uses `common.utilities.script_discovery` to:
1. Automatically detect which version is running
2. Import the correct tab modules
3. Use appropriate paths via `utils.path_utils`

## Benefits
- No hardcoded paths
- Version awareness
- Easy to switch between v3/v4
- Clean separation of concerns

## Usage

To create a new portal version:
1. Copy flow_portal_v4.py to flow_portal_v5.py
2. Create v5 tab files (t_*_v5.py)
3. Script discovery will automatically load v5 tabs

No need to update imports - it's all automatic!