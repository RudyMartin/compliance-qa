"""
Flow Portal V4 - Simple & Clean Workflow Management
===================================================
Main entry point with 5 easy-to-use tabs:
Create → Manage → Run → Optimize → Ask AI
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import utilities with fallback pattern from tidyllm
try:
    from core.utilities.path_manager import get_path_manager
except ImportError:
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        # Fallback to local utils
        from utils.path_utils import get_path_manager

# Import script discovery with fallback
try:
    from common.utilities.script_discovery import get_script_context, get_tab_import_name
except ImportError:
    # Create local imports if common not available
    from utils.script_discovery import get_script_context, get_tab_import_name

# Page config - clean and simple
st.set_page_config(
    page_title="Flow Portal",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple styling
st.markdown("""
<style>
    /* Clean, readable fonts */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 16px;
        font-weight: 500;
    }
    /* Big, clear headers */
    h1 { font-size: 32px !important; }
    h2 { font-size: 24px !important; margin-top: 20px !important; }
    h3 { font-size: 18px !important; color: #444 !important; }
</style>
""", unsafe_allow_html=True)

# Import script context early
script_context = get_script_context()

# Header with version info
st.title("🔄 Flow Portal")
st.markdown("**Build, manage, and optimize intelligent workflows**")

# Show version info in development mode
if st.sidebar.checkbox("Developer Mode", value=False):
    st.sidebar.info(f"""
    **Script Context:**
    - Portal: {script_context.portal_type}
    - Version: {script_context.script_version}
    - Script: {script_context.script_name}
    """)

# Initialize session state FIRST
if 'current_workflow' not in st.session_state:
    st.session_state.current_workflow = None

# Get path manager early to check available projects
path_mgr = get_path_manager()
projects_dir = path_mgr.projects_path

# Initialize selected_project with smart default
if 'selected_project' not in st.session_state:
    # Check what projects actually exist
    if projects_dir.exists():
        project_dirs = [d.name for d in projects_dir.iterdir()
                       if d.is_dir() and not d.name.startswith(".") and d.name != "global"]
        # Try client_demo first, then any other project, then global
        if "client_demo" in project_dirs:
            st.session_state.selected_project = "client_demo"
        elif project_dirs:
            st.session_state.selected_project = sorted(project_dirs)[0]
        else:
            st.session_state.selected_project = "global"
    else:
        st.session_state.selected_project = "global"

# Load workflows based on selected project
if 'workflows' not in st.session_state or st.session_state.get('reload_workflows', False):
    import json
    selected_project = st.session_state.get('selected_project', 'global')

    if selected_project == 'global':
        workflow_file = path_mgr.workflows_path / "portal_workflows.json"
    else:
        workflow_file = projects_dir / selected_project / "workflows.json"

    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            st.session_state.workflows = data.get('workflows', {})
    else:
        st.session_state.workflows = {}

    st.session_state.reload_workflows = False

# Initialize navigation flag
if 'navigate_to_create' not in st.session_state:
    st.session_state.navigate_to_create = False

# Project selector with "Create workflow" option
# (path_mgr and projects_dir already defined above)

# Build options list with "Create workflow" as first option
available_options = ["➕ Create new workflow"]  # First option
available_projects = ["global"]  # Project options start here

if projects_dir.exists():
    project_dirs = [d.name for d in projects_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".") and d.name != "global"]
    available_projects += sorted(project_dirs)

# Combine all options
all_options = available_options + available_projects

# Project selector UI
col1, col2, col3 = st.columns([2, 3, 3])
with col1:
    # Find current index based on selected project or navigation flag
    try:
        # Check if we should show "Create new workflow"
        if st.session_state.get('navigate_to_create', False):
            current_index = 0  # Show "Create new workflow"
        elif st.session_state.selected_project in available_projects:
            # Find project index (accounting for "Create" option)
            current_index = available_projects.index(st.session_state.selected_project) + 1  # +1 for Create option
        else:
            # Default to first project if exists
            current_index = 1 if len(available_projects) > 0 else 0
    except (ValueError, KeyError):
        current_index = 1  # Default to first project

    selected = st.selectbox(
        "🔄 **Action/Project**",
        all_options,
        index=current_index,
        key="global_project_selector",
        help="Select 'Create new workflow' or choose a project to work with"
    )

    # Handle selection
    if selected == "➕ Create new workflow":
        # Set flag to show create message in Create tab
        st.session_state.navigate_to_create = True
        st.session_state.show_create_message = True
        # Don't change selected_project - keep the current one for the new workflow
    else:
        # Selected a project
        if st.session_state.get('selected_project') != selected:
            st.session_state.selected_project = selected
            # Load workflows for the new project
            import json
            if selected == 'global':
                workflow_file = path_mgr.workflows_path / "portal_workflows.json"
            else:
                workflow_file = projects_dir / selected / "workflows.json"

            if workflow_file.exists():
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    st.session_state.workflows = data.get('workflows', {})
            else:
                st.session_state.workflows = {}

            # Clear current workflow since we're switching projects
            st.session_state.current_workflow = None
            st.rerun()
        st.session_state.navigate_to_create = False
        st.session_state.show_create_message = False

with col2:
    if selected == "➕ Create new workflow":
        st.success("📝 Ready to create new workflow")
    elif st.session_state.selected_project != "global":
        st.info(f"Working in: **{st.session_state.selected_project}**")
    else:
        st.info("Working with **global** workflows")

with col3:
    if selected == "➕ Create new workflow":
        st.caption("Switch to Create tab to build workflow")
    else:
        st.caption("Project context for all tabs")

st.markdown("---")

# Import tab modules dynamically based on script version
TABS_AVAILABLE = False

try:
    # Import the correct version of tabs based on script context
    if script_context.script_version == "v4":
        # V4 tabs with enhanced manage
        from t_create_flow_v4 import render_create_tab
        from t_manage_flows_enhanced import render_manage_tab  # Enhanced version
        from t_run_flows_v4 import render_run_tab
        from t_optimize_flows_v4 import render_optimize_tab
        from t_ask_ai_v4 import render_ask_ai_tab
        TABS_AVAILABLE = True
    elif script_context.script_version == "v3":
        # V3 tabs (if they exist)
        from t_create_flow import render_create_tab
        from t_manage_flows import render_manage_tab
        from t_run import render_run_tab
        from t_optimize import render_optimize_tab
        from t_ask_ai import render_ask_ai_tab
        TABS_AVAILABLE = True
    else:
        # Default fallback
        st.error(f"Unknown portal version: {script_context.script_version}")
except ImportError as e:
    st.error(f"Tab modules not found for {script_context.portal_type}: {e}")

# Main navigation - Simple 5 tabs
tabs = st.tabs(["📝 Create", "📚 Manage", "▶️ Run", "📈 Optimize", "🤖 Ask AI"])

# Render each tab
with tabs[0]:
    if TABS_AVAILABLE:
        render_create_tab()
    else:
        st.info("Create tab loading...")

with tabs[1]:
    if TABS_AVAILABLE:
        render_manage_tab()
    else:
        st.info("Manage tab loading...")

with tabs[2]:
    if TABS_AVAILABLE:
        render_run_tab()
    else:
        st.info("Run tab loading...")

with tabs[3]:
    if TABS_AVAILABLE:
        render_optimize_tab()
    else:
        st.info("Optimize tab loading...")

with tabs[4]:
    if TABS_AVAILABLE:
        render_ask_ai_tab()
    else:
        st.info("Ask AI tab loading...")

# Footer with helpful info
st.markdown("---")
st.markdown("**Quick Help:** Use **Create** to build workflows • **Manage** to organize • **Run** to execute • **Optimize** to improve • **Ask AI** for help")