"""
Create Flow Tab - Modular Component
Extracted from flow_creator_v3.py for easier maintenance
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import actions loader for template integration
try:
    from domain.services.actions_loader_service import get_actions_loader
    ACTIONS_AVAILABLE = True
except ImportError:
    ACTIONS_AVAILABLE = False

def render_create_flow_tab(workflow_manager, registry):
    """Render the Create Flow tab content."""
    st.markdown("## ➕ **Create New Flow**")

    # Add toggle for using action templates
    use_action_templates = st.toggle(
        "🎯 Use Action Templates",
        value=False,
        help="Enable to use pre-defined business workflow actions from actions_spec.json"
    )

    if use_action_templates and ACTIONS_AVAILABLE:
        _render_action_based_flow(workflow_manager, registry)
    else:
        _render_manual_flow(workflow_manager, registry)


def _render_action_based_flow(workflow_manager, registry):
    """Render action-based flow creation."""
    st.markdown("### 🎯 **Action-Based Workflow Creation**")
    st.info("Create workflows using pre-defined business actions with DSPy execution")

    # Load actions
    loader = get_actions_loader()
    actions = loader.get_all_actions()
    action_chains = loader.get_action_chains()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 **Select Action Chain**")

        # Pre-defined chains
        chain_options = ["Custom"] + [f"Chain {i+1}: {' → '.join(chain)}"
                                      for i, chain in enumerate(action_chains)]
        selected_chain = st.selectbox(
            "Choose a pre-defined action chain",
            chain_options,
            help="Select a pre-configured action sequence or build custom"
        )

        if selected_chain == "Custom":
            # Custom action selection
            st.markdown("**Build Custom Chain:**")

            # Group actions by category
            categories = loader.get_action_categories()

            selected_actions = []
            for category, action_types in categories.items():
                with st.expander(f"📁 {category}"):
                    for action_type in action_types:
                        action = loader.get_action(action_type)
                        if action:
                            metadata = loader.get_action_metadata(action_type)
                            if st.checkbox(f"{metadata['icon']} {action.title}", key=f"action_{action_type}"):
                                selected_actions.append(action_type)
        else:
            # Use pre-defined chain
            chain_index = chain_options.index(selected_chain) - 1
            selected_actions = action_chains[chain_index]
            st.success(f"Using pre-defined chain with {len(selected_actions)} actions")

    with col2:
        st.subheader("🔄 **Action Flow**")

        if selected_actions:
            # Validate and display action sequence
            is_valid, errors = loader.validate_action_sequence(selected_actions)

            # Display action flow
            st.markdown("**Workflow Steps:**")
            for i, action_type in enumerate(selected_actions):
                action = loader.get_action(action_type)
                if action:
                    metadata = loader.get_action_metadata(action_type)
                    st.write(f"{i+1}. {metadata['icon']} **{action.title}**")
                    st.caption(f"   Requires: {', '.join(action.requires) if action.requires else 'None'}")
                    st.caption(f"   Produces: {', '.join(action.produces)}")

            if not is_valid:
                st.error("❌ **Validation Errors:**")
                for error in errors:
                    st.write(f"  • {error}")
            else:
                st.success("✅ Action chain is valid!")

                # DSPy signature preview
                with st.expander("🧠 DSPy Signature Preview"):
                    from packages.tidyllm.services.dspy_service import get_dspy_service
                    dspy_service = get_dspy_service()

                    # Generate chain module
                    result = dspy_service.generate_action_chain_module(selected_actions)
                    if result.get("success"):
                        st.code(result["module_code"], language="python")
                    else:
                        st.error(f"Failed to generate DSPy module: {result.get('error')}")

    # Workflow metadata
    st.markdown("---")
    st.subheader("📝 **Workflow Configuration**")

    col_name, col_desc = st.columns([1, 2])
    with col_name:
        workflow_name = st.text_input(
            "Workflow Name",
            value=f"action_flow_{len(selected_actions)}_steps" if selected_actions else "",
            placeholder="e.g., document_risk_assessment"
        )

    with col_desc:
        description = st.text_input(
            "Description",
            value=f"Action-based workflow with {len(selected_actions)} steps" if selected_actions else "",
            placeholder="Brief description of the workflow"
        )

    # Create workflow button
    if st.button("🚀 Create Action Workflow", type="primary", disabled=not selected_actions or not is_valid):
        # Generate workflow from actions
        workflow_steps = []
        for i, action_type in enumerate(selected_actions):
            step = loader.convert_to_workflow_step(action_type, position=i)
            if step:
                workflow_steps.append(step.__dict__)

        # Create workflow configuration
        workflow_config = {
            "workflow_name": workflow_name,
            "workflow_type": "action_based",
            "description": description,
            "steps": workflow_steps,
            "action_chain": selected_actions,
            "dspy_enabled": True,
            "created_at": datetime.now().isoformat()
        }

        # Save workflow
        st.success(f"✅ Created action-based workflow: {workflow_name}")
        st.json(workflow_config)

        # Store in session state for other tabs to access
        st.session_state.last_created_workflow = workflow_config


def _render_manual_flow(workflow_manager, registry):
    """Render the original manual flow creation."""
    # Get available workflow types from registry
    workflow_types = registry.get_workflow_types()

    if not workflow_types or workflow_types == ["unknown"]:
        st.warning("⚠️ No workflow types found in registry. Using defaults.")
        workflow_types = ["mvr", "analysis", "rag_creation", "custom"]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 **Workflow Configuration**")

        # Basic workflow information
        workflow_name = st.text_input(
            "Workflow Name",
            placeholder="e.g., financial_risk_analysis",
            help="Unique name for your workflow"
        )

        workflow_type = st.selectbox(
            "Workflow Type",
            workflow_types,
            help="Choose the type that best fits your use case"
        )

        description = st.text_area(
            "Description",
            placeholder="Describe what this workflow does...",
            help="Brief description of the workflow's purpose"
        )

        # RAG Integration Options
        st.subheader("🧠 **RAG Integration**")
        rag_systems = ["ai_powered", "postgres", "intelligent", "sme", "dspy"]
        selected_rags = st.multiselect(
            "RAG Systems to Integrate",
            rag_systems,
            default=["ai_powered"],
            help="Choose which RAG systems to include"
        )

    with col2:
        st.subheader("📋 **Workflow Steps**")

        if 'workflow_steps' not in st.session_state:
            st.session_state.workflow_steps = [
                {"step_name": "initial_analysis", "step_type": "extraction", "template": ""},
                {"step_name": "detailed_review", "step_type": "analysis", "template": ""},
                {"step_name": "final_output", "step_type": "aggregation", "template": ""}
            ]

        steps = st.session_state.workflow_steps

        # Step configuration
        for i, step in enumerate(steps):
            with st.expander(f"Step {i+1}: {step['step_name']}", expanded=False):
                step['step_name'] = st.text_input(f"Step Name {i+1}", value=step['step_name'], key=f"step_name_{i}")
                step['step_type'] = st.selectbox(
                    f"Step Type {i+1}",
                    ["extraction", "analysis", "aggregation", "validation", "custom"],
                    index=["extraction", "analysis", "aggregation", "validation", "custom"].index(step['step_type']),
                    key=f"step_type_{i}"
                )
                step['template'] = st.text_input(f"Template {i+1}", value=step['template'], key=f"template_{i}")

        # Add/Remove steps
        col_add, col_remove = st.columns(2)
        with col_add:
            if st.button("➕ Add Step"):
                st.session_state.workflow_steps.append({
                    "step_name": f"step_{len(steps)+1}",
                    "step_type": "custom",
                    "template": ""
                })
                st.rerun()

        with col_remove:
            if st.button("➖ Remove Step") and len(steps) > 1:
                st.session_state.workflow_steps.pop()
                st.rerun()

    # Creation controls
    st.markdown("---")
    col_create, col_preview = st.columns([1, 1])

    with col_create:
        if st.button("🚀 **Create Workflow**", type="primary", use_container_width=True):
            if workflow_name and description:
                # Create workflow data structure
                workflow_data = {
                    "workflow_id": workflow_name,
                    "workflow_name": workflow_name.replace('_', ' ').title(),
                    "workflow_type": workflow_type,
                    "description": description,
                    "rag_integration": selected_rags,
                    "steps": st.session_state.workflow_steps,
                    "created_date": datetime.now().isoformat(),
                    "flow_encoding": f"@{workflow_name}#process!analyze@output"
                }

                # Save workflow
                try:
                    workflows_dir = Path("tidyllm/workflows/projects") / workflow_name
                    workflows_dir.mkdir(parents=True, exist_ok=True)

                    config_file = workflows_dir / "project_config.json"
                    from tidyllm.utils.clean_json_io import save_json
                    save_json(config_file, workflow_data)

                    # Create directory structure
                    (workflows_dir / "criteria").mkdir(exist_ok=True)
                    (workflows_dir / "templates").mkdir(exist_ok=True)
                    (workflows_dir / "inputs").mkdir(exist_ok=True)
                    (workflows_dir / "outputs").mkdir(exist_ok=True)
                    (workflows_dir / "resources").mkdir(exist_ok=True)

                    st.success(f"✅ **Created workflow**: {workflow_name}")
                    st.success(f"📁 **Location**: {workflows_dir}")
                    st.balloons()

                    # Clear form
                    del st.session_state.workflow_steps
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ **Creation failed**: {e}")
            else:
                st.warning("⚠️ Please fill in workflow name and description")

    with col_preview:
        if st.button("👁️ **Preview Configuration**", use_container_width=True):
            if workflow_name:
                st.json({
                    "workflow_id": workflow_name,
                    "workflow_type": workflow_type,
                    "description": description,
                    "rag_integration": selected_rags,
                    "steps": st.session_state.workflow_steps
                })
            else:
                st.info("Enter a workflow name to see preview")