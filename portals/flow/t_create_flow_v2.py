"""
Create Flow Tab - Version 2 with Dynamic 3-Choice Approach
===========================================================

Simplified, clear interface with 3 main paths for workflow creation.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import json

def render_create_flow_tab():
    """Render the Create Flow tab with dynamic 3-choice approach."""

    st.markdown("## 🎯 What would you like to create?")
    st.markdown("Choose your workflow creation path:")

    # Three clear choices with big buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🚀 Quick Start")
        st.markdown("Create a simple workflow in seconds")
        if st.button("Start Simple", key="simple_workflow", use_container_width=True, type="primary"):
            st.session_state.creation_mode = "simple"

    with col2:
        st.markdown("### 🎨 Custom Build")
        st.markdown("Design your workflow step by step")
        if st.button("Build Custom", key="custom_workflow", use_container_width=True, type="primary"):
            st.session_state.creation_mode = "custom"

    with col3:
        st.markdown("### 📄 From Template")
        st.markdown("Use an existing workflow template")
        if st.button("Use Template", key="template_workflow", use_container_width=True, type="primary"):
            st.session_state.creation_mode = "template"

    st.markdown("---")

    # Show the appropriate interface based on choice
    if 'creation_mode' in st.session_state:
        if st.session_state.creation_mode == "simple":
            render_simple_workflow()
        elif st.session_state.creation_mode == "custom":
            render_custom_workflow()
        elif st.session_state.creation_mode == "template":
            render_template_workflow()
    else:
        # Show helpful information when no choice is made
        render_welcome_info()

def render_simple_workflow():
    """Quick start workflow creation - minimal inputs."""
    st.markdown("## 🚀 Quick Start Workflow")

    with st.form("simple_workflow_form"):
        workflow_name = st.text_input(
            "Workflow Name",
            placeholder="my_workflow",
            help="Simple name, no spaces"
        )

        workflow_purpose = st.selectbox(
            "What will this workflow do?",
            [
                "Process documents",
                "Analyze data",
                "Generate reports",
                "Extract information",
                "Other"
            ]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.form_submit_button("✅ Create", type="primary", use_container_width=True):
                if workflow_name:
                    create_simple_workflow(workflow_name, workflow_purpose)
                else:
                    st.error("Please enter a workflow name")

        with col2:
            if st.form_submit_button("🔄 Reset", use_container_width=True):
                if 'creation_mode' in st.session_state:
                    del st.session_state.creation_mode
                st.rerun()

        with col3:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                if 'creation_mode' in st.session_state:
                    del st.session_state.creation_mode
                st.rerun()

def render_custom_workflow():
    """Custom workflow builder with all options."""
    st.markdown("## 🎨 Custom Workflow Builder")

    # Use tabs for organized configuration
    tab1, tab2, tab3 = st.tabs(["📝 Basic Info", "🔧 Steps", "⚙️ Advanced"])

    with tab1:
        workflow_name = st.text_input("Workflow Name", key="custom_name")
        description = st.text_area("Description", key="custom_desc")
        workflow_type = st.selectbox(
            "Workflow Type",
            ["document_processing", "data_analysis", "rag_pipeline", "custom"]
        )

    with tab2:
        st.markdown("### Configure Workflow Steps")

        if 'custom_steps' not in st.session_state:
            st.session_state.custom_steps = []

        # Add step button
        if st.button("➕ Add New Step"):
            st.session_state.custom_steps.append({
                "name": f"Step {len(st.session_state.custom_steps) + 1}",
                "type": "process",
                "config": {}
            })

        # Display existing steps
        for i, step in enumerate(st.session_state.custom_steps):
            with st.expander(f"Step {i+1}: {step['name']}"):
                step['name'] = st.text_input("Name", value=step['name'], key=f"step_name_{i}")
                step['type'] = st.selectbox(
                    "Type",
                    ["process", "analyze", "extract", "validate"],
                    key=f"step_type_{i}"
                )
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.custom_steps.pop(i)
                    st.rerun()

    with tab3:
        st.markdown("### Advanced Settings")
        enable_rag = st.checkbox("Enable RAG Integration")
        enable_ml = st.checkbox("Enable ML Features")
        enable_monitoring = st.checkbox("Enable Monitoring")

    # Action buttons - 3 clear choices
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Create Workflow", type="primary", use_container_width=True):
            if workflow_name:
                create_custom_workflow(workflow_name, description, workflow_type)
            else:
                st.error("Please enter workflow name")

    with col2:
        if st.button("💾 Save Draft", use_container_width=True):
            save_draft(workflow_name)

    with col3:
        if st.button("🔙 Back", use_container_width=True):
            if 'creation_mode' in st.session_state:
                del st.session_state.creation_mode
            st.rerun()

def render_template_workflow():
    """Choose from existing templates."""
    st.markdown("## 📄 Template Library")

    # Template categories
    template_category = st.selectbox(
        "Select Template Category",
        ["Document Processing", "Data Analysis", "RAG Pipelines", "ML Workflows", "All Templates"]
    )

    # Template grid
    templates = get_available_templates(template_category)

    if templates:
        # Display templates in a grid
        cols = st.columns(3)
        for i, template in enumerate(templates):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"### {template['name']}")
                    st.markdown(f"*{template['description'][:50]}...*")
                    st.markdown(f"**Type:** {template['type']}")

                    if st.button(f"Use This", key=f"use_{template['id']}", use_container_width=True):
                        st.session_state.selected_template = template
                        st.rerun()
    else:
        st.info("No templates available in this category")

    # If template is selected, show configuration
    if 'selected_template' in st.session_state:
        st.markdown("---")
        st.markdown(f"### Configuring: {st.session_state.selected_template['name']}")

        workflow_name = st.text_input(
            "New Workflow Name",
            value=f"{st.session_state.selected_template['id']}_copy"
        )

        # Three action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Create from Template", type="primary", use_container_width=True):
                create_from_template(workflow_name, st.session_state.selected_template)

        with col2:
            if st.button("🔧 Customize First", use_container_width=True):
                st.session_state.creation_mode = "custom"
                # Load template into custom mode
                load_template_to_custom(st.session_state.selected_template)
                st.rerun()

        with col3:
            if st.button("🔙 Back", use_container_width=True):
                if 'selected_template' in st.session_state:
                    del st.session_state.selected_template
                st.rerun()

def render_welcome_info():
    """Show helpful information when no choice is made."""
    st.markdown("---")

    # Information cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **🚀 Quick Start** is perfect for:
        - First-time users
        - Simple workflows
        - Quick prototypes
        - Testing ideas
        """)

    with col2:
        st.info("""
        **🎨 Custom Build** is ideal for:
        - Complex workflows
        - Specific requirements
        - Advanced features
        - Full control
        """)

    with col3:
        st.info("""
        **📄 From Template** is best for:
        - Standard processes
        - Best practices
        - Quick deployment
        - Learning examples
        """)

    st.markdown("---")

    # Recent workflows
    st.markdown("### 📊 Recent Workflows")
    recent = get_recent_workflows()
    if recent:
        for workflow in recent[:3]:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{workflow['name']}** - {workflow['type']}")
            with col2:
                st.markdown(f"*{workflow['created']}*")
            with col3:
                if st.button("Open", key=f"open_{workflow['id']}"):
                    st.session_state.open_workflow = workflow['id']
    else:
        st.info("No recent workflows. Create your first one above!")

# Helper functions
def create_simple_workflow(name, purpose):
    """Create a simple workflow quickly."""
    workflow = {
        "name": name,
        "purpose": purpose,
        "type": "simple",
        "created": datetime.now().isoformat(),
        "steps": [
            {"name": "Input", "type": "input"},
            {"name": "Process", "type": purpose.lower().replace(" ", "_")},
            {"name": "Output", "type": "output"}
        ]
    }

    save_workflow(workflow)
    st.success(f"✅ Created simple workflow: {name}")
    st.balloons()

    # Clear state
    if 'creation_mode' in st.session_state:
        del st.session_state.creation_mode
    st.rerun()

def create_custom_workflow(name, description, workflow_type):
    """Create a custom workflow."""
    workflow = {
        "name": name,
        "description": description,
        "type": workflow_type,
        "created": datetime.now().isoformat(),
        "steps": st.session_state.get('custom_steps', [])
    }

    save_workflow(workflow)
    st.success(f"✅ Created custom workflow: {name}")
    st.balloons()

    # Clear state
    if 'creation_mode' in st.session_state:
        del st.session_state.creation_mode
    if 'custom_steps' in st.session_state:
        del st.session_state.custom_steps
    st.rerun()

def create_from_template(name, template):
    """Create workflow from template."""
    workflow = template.copy()
    workflow['name'] = name
    workflow['created'] = datetime.now().isoformat()
    workflow['based_on_template'] = template['id']

    save_workflow(workflow)
    st.success(f"✅ Created workflow from template: {name}")
    st.balloons()

    # Clear state
    if 'creation_mode' in st.session_state:
        del st.session_state.creation_mode
    if 'selected_template' in st.session_state:
        del st.session_state.selected_template
    st.rerun()

def save_workflow(workflow):
    """Save workflow to disk."""
    workflows_dir = Path("workflows") / workflow['name']
    workflows_dir.mkdir(parents=True, exist_ok=True)

    config_file = workflows_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(workflow, f, indent=2)

    # Create standard directories
    (workflows_dir / "inputs").mkdir(exist_ok=True)
    (workflows_dir / "outputs").mkdir(exist_ok=True)
    (workflows_dir / "templates").mkdir(exist_ok=True)

def save_draft(name):
    """Save workflow as draft."""
    if name:
        drafts_dir = Path("workflows") / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        draft_file = drafts_dir / f"{name}_draft.json"
        draft_data = {
            "name": name,
            "saved": datetime.now().isoformat(),
            "steps": st.session_state.get('custom_steps', [])
        }

        with open(draft_file, 'w') as f:
            json.dump(draft_data, f, indent=2)

        st.success(f"💾 Draft saved: {name}")

def get_available_templates(category):
    """Get available workflow templates."""
    # Mock data - replace with actual template loading
    templates = [
        {
            "id": "doc_processor",
            "name": "Document Processor",
            "description": "Process and analyze documents with AI",
            "type": "Document Processing"
        },
        {
            "id": "data_analyzer",
            "name": "Data Analyzer",
            "description": "Analyze structured and unstructured data",
            "type": "Data Analysis"
        },
        {
            "id": "rag_pipeline",
            "name": "RAG Pipeline",
            "description": "Retrieval-augmented generation workflow",
            "type": "RAG Pipelines"
        }
    ]

    if category == "All Templates":
        return templates
    else:
        return [t for t in templates if t['type'] == category]

def get_recent_workflows():
    """Get recently created workflows."""
    # Mock data - replace with actual workflow loading
    return [
        {"id": "wf1", "name": "Invoice Processor", "type": "document", "created": "2024-01-20"},
        {"id": "wf2", "name": "Data Pipeline", "type": "analysis", "created": "2024-01-19"},
    ]

def load_template_to_custom(template):
    """Load template into custom builder."""
    st.session_state.custom_steps = template.get('steps', [])
    # Additional template loading logic

if __name__ == "__main__":
    # Test standalone
    render_create_flow_tab()