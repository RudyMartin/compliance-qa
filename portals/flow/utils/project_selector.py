"""
Project Selector Component
=========================
Shared component for project selection across all tabs
"""

import streamlit as st
from pathlib import Path
from typing import List, Optional

def render_universal_selector(tab_name: str = "default") -> None:
    """
    Universal project/action selector that appears on every tab

    Args:
        tab_name: Name of the current tab for unique key generation
    """
    # Import path utilities with fallback
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        try:
            from common.utilities.path_manager import get_path_manager
        except ImportError:
            from utils.path_utils import get_path_manager

    # Initialize session states
    if 'navigate_to_create' not in st.session_state:
        st.session_state.navigate_to_create = False
    if 'selected_project' not in st.session_state:
        st.session_state.selected_project = "client_demo"

    # Get available projects
    path_mgr = get_path_manager()
    projects_dir = path_mgr.projects_path

    # Build options list with "Create workflow" as first option
    available_options = ["➕ Create new workflow"]
    available_projects = ["global"]

    if projects_dir.exists():
        available_projects += sorted([d.name for d in projects_dir.iterdir()
                                     if d.is_dir() and not d.name.startswith(".")])

    # Combine all options
    all_options = available_options + available_projects

    # Project selector UI
    col1, col2, col3 = st.columns([2, 3, 3])
    with col1:
        # Find current index based on selected project
        try:
            if st.session_state.selected_project in available_projects:
                current_index = available_projects.index(st.session_state.selected_project) + 1
            else:
                current_index = 0
        except (ValueError, KeyError):
            current_index = 0

        selected = st.selectbox(
            "🔄 **Action/Project**",
            all_options,
            index=current_index,
            key=f"universal_project_selector_{tab_name}",
            help="Select 'Create new workflow' or choose a project to work with"
        )

        # Handle selection
        if selected == "➕ Create new workflow":
            st.session_state.navigate_to_create = True
            st.session_state.show_create_message = True
        else:
            st.session_state.selected_project = selected
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

def render_project_selector() -> str:
    """
    Render project selector and return selected project.
    This maintains state across all tabs.
    """
    # Import path utilities with fallback
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        try:
            from common.utilities.path_manager import get_path_manager
        except ImportError:
            from utils.path_utils import get_path_manager

    path_mgr = get_path_manager()
    projects_dir = path_mgr.projects_path

    # Get available projects
    available_projects = ["global"]  # Always include global
    if projects_dir.exists():
        available_projects += sorted([
            d.name for d in projects_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ])

    # Initialize session state if needed
    if 'selected_project' not in st.session_state:
        # Default to client_demo if it exists, otherwise global
        if "client_demo" in available_projects:
            st.session_state.selected_project = "client_demo"
        else:
            st.session_state.selected_project = "global"

    # Create project selector
    col1, col2, col3 = st.columns([2, 3, 3])

    with col1:
        # Find current index safely
        try:
            current_index = available_projects.index(st.session_state.selected_project)
        except ValueError:
            # If selected project not in list, default to first available
            current_index = 0
            st.session_state.selected_project = available_projects[0]

        selected_project = st.selectbox(
            "📁 **Active Project**",
            available_projects,
            index=current_index,
            key="project_selector",
            help="Select project to work with"
        )

        # Update session state if changed
        if selected_project != st.session_state.selected_project:
            st.session_state.selected_project = selected_project
            st.rerun()

    with col2:
        if st.session_state.selected_project != "global":
            st.info(f"Working in: **{st.session_state.selected_project}**")
        else:
            st.info("Working with **global** workflows")

    with col3:
        # Quick project actions
        if st.button("➕ New Project", key="new_project_btn", use_container_width=True):
            st.info("Project creation coming soon")

    return st.session_state.selected_project

def get_project_workflows_path(project: str = None) -> Path:
    """Get the workflows path for a specific project"""
    if project is None:
        project = st.session_state.get('selected_project', 'global')

    # Import path utilities with fallback
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        try:
            from common.utilities.path_manager import get_path_manager
        except ImportError:
            from utils.path_utils import get_path_manager

    path_mgr = get_path_manager()

    if project == 'global':
        return path_mgr.workflows_path
    else:
        return path_mgr.projects_path / project / "workflows"

def get_project_resources_path(project: str = None, resource_type: str = "uploads") -> Path:
    """Get the resource path for a specific project"""
    if project is None:
        project = st.session_state.get('selected_project', 'global')

    # Import path utilities with fallback
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        try:
            from common.utilities.path_manager import get_path_manager
        except ImportError:
            from utils.path_utils import get_path_manager

    path_mgr = get_path_manager()

    if project == 'global':
        base_path = path_mgr.workflows_path.parent
    else:
        base_path = path_mgr.projects_path / project

    # Map resource types to folder names
    resource_map = {
        "uploads": "uploads",
        "inputs": "uploads",
        "prompts": "prompts",
        "templates": "prompts",
        "criteria": "criteria"
    }

    folder = resource_map.get(resource_type, resource_type)
    return base_path / folder