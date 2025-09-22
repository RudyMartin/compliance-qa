"""
Create Flow Tab - Modular Component
Extracted from flow_creator_v3.py for easier maintenance
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import json

# Import actions loader for template integration
try:
    from domain.services.actions_loader_service import get_actions_loader
    ACTIONS_AVAILABLE = True
except ImportError:
    ACTIONS_AVAILABLE = False

def render_create_flow_tab(workflow_manager, registry):
    """Render the Create Flow tab content."""
    st.markdown("## ➕ **Create New Flow**")

    # Three simple create buttons at the top
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 **Action Steps**", type="primary", use_container_width=True):
            st.session_state.create_mode = "action_steps"

    with col2:
        if st.button("💡 **Prompts**", type="primary", use_container_width=True):
            st.session_state.create_mode = "prompts"

    with col3:
        if st.button("🤖 **Ask AI**", type="primary", use_container_width=True):
            st.session_state.create_mode = "ask_ai"

    st.markdown("---")

    # Show form based on mode selected
    if 'create_mode' not in st.session_state:
        st.info("👆 Choose a creation method to get started")
        return

    mode = st.session_state.create_mode

    # Show different forms based on mode
    if mode == "action_steps":
        _render_action_steps_flow(workflow_manager, registry)
    elif mode == "prompts":
        _render_prompts_flow(workflow_manager, registry)
    elif mode == "ask_ai":
        _render_ask_ai_flow(workflow_manager, registry)


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


def _render_action_steps_flow(workflow_manager, registry):
    """Render action steps based workflow creation."""
    st.markdown("### 📝 **Action Steps Workflow**")
    st.info("Define your workflow using sequential action steps")

    # Action steps builder
    if 'action_steps' not in st.session_state:
        st.session_state.action_steps = []

    # Workflow name at the top
    workflow_name = st.text_input("Workflow Name", placeholder="my_action_workflow", key="action_workflow_name")

    # Add step interface
    with st.expander("➕ Add New Action Step", expanded=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            step_name = st.text_input("Step Name", placeholder="e.g., Load Data", key="new_step_name")
        with col2:
            step_type = st.selectbox("Step Type", ["Process", "Analyze", "Transform", "Output"], key="new_step_type")

        # Additional step details
        step_description = st.text_area("Step Description", placeholder="What does this step do?", height=80, key="new_step_desc")

        col3, col4 = st.columns(2)
        with col3:
            requires = st.text_input("Requires (comma-separated)", placeholder="e.g., raw_data, config", key="new_step_requires")
        with col4:
            produces = st.text_input("Produces (comma-separated)", placeholder="e.g., processed_data", key="new_step_produces")

        if st.button("Add Step"):
            if step_name:
                st.session_state.action_steps.append({
                    "step_name": step_name,
                    "step_type": step_type.lower(),
                    "description": step_description,
                    "requires": [r.strip() for r in requires.split(',')] if requires else [],
                    "produces": [p.strip() for p in produces.split(',')] if produces else [],
                    "position": len(st.session_state.action_steps)
                })
                st.success(f"Added step: {step_name}")
                st.rerun()

    # Display current steps
    if st.session_state.action_steps:
        st.markdown("**Current Action Steps:**")
        for i, step in enumerate(st.session_state.action_steps):
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.write(f"**{i+1}.**")
                with col2:
                    st.write(f"**{step['step_name']}** ({step['step_type']})")
                    if step.get('description'):
                        st.caption(step['description'])
                    if step.get('requires'):
                        st.caption(f"📥 Requires: {', '.join(step['requires'])}")
                    if step.get('produces'):
                        st.caption(f"📤 Produces: {', '.join(step['produces'])}")
                with col3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.action_steps.pop(i)
                        st.rerun()
                st.markdown("---")

    # Create workflow from action steps
    if st.button("🚀 Create Workflow from Action Steps", type="primary", use_container_width=True):
        if workflow_name and st.session_state.action_steps:
            try:
                # Import ActionStepsManager
                from domain.services.action_steps_manager import ActionStepsManager
                from pathlib import Path
                from datetime import datetime

                # Create workflow directory
                workflows_dir = Path("domain/workflows/projects") / workflow_name
                workflows_dir.mkdir(parents=True, exist_ok=True)

                # Create standard directories
                (workflows_dir / "criteria").mkdir(exist_ok=True)
                (workflows_dir / "templates").mkdir(exist_ok=True)
                (workflows_dir / "inputs").mkdir(exist_ok=True)
                (workflows_dir / "outputs").mkdir(exist_ok=True)
                (workflows_dir / "resources").mkdir(exist_ok=True)
                (workflows_dir / "action_steps").mkdir(exist_ok=True)

                # Initialize ActionStepsManager
                manager = ActionStepsManager(workflow_name, workflows_dir)

                # Save each action step
                for step in st.session_state.action_steps:
                    result = manager.save_action_step(step['step_name'], step)
                    if not result['success']:
                        st.error(f"Failed to save step {step['step_name']}: {result.get('error')}")

                # Create workflow config
                workflow_config = {
                    "workflow_id": workflow_name,
                    "workflow_name": workflow_name.replace('_', ' ').title(),
                    "workflow_type": "action_based",
                    "description": f"Action-based workflow with {len(st.session_state.action_steps)} steps",
                    "action_steps_count": len(st.session_state.action_steps),
                    "created_at": datetime.now().isoformat()
                }

                # Save workflow config
                config_file = workflows_dir / "project_config.json"
                import json
                with open(config_file, 'w') as f:
                    json.dump(workflow_config, f, indent=2)

                st.success(f"✅ Created workflow: {workflow_name}")
                st.success(f"📁 Saved {len(st.session_state.action_steps)} action steps")
                st.balloons()

                # Clear state
                st.session_state.action_steps = []
                del st.session_state.create_mode
                st.rerun()

            except Exception as e:
                st.error(f"Failed to create workflow: {e}")
        else:
            st.warning("Please enter a workflow name and add at least one action step")

def _render_prompts_flow(workflow_manager, registry):
    """Render prompts-based workflow creation."""
    st.markdown("### 💡 **Prompts Workflow**")
    st.info("Create workflows using natural language prompts and templates")

    # Initialize prompt steps in session state
    if 'prompt_steps' not in st.session_state:
        st.session_state.prompt_steps = []

    # Workflow name at the top
    workflow_name = st.text_input("Workflow Name", placeholder="my_prompt_workflow", key="prompt_workflow_name")

    # Add prompt interface
    with st.expander("➕ Add New Prompt Step", expanded=True):
        prompt_name = st.text_input("Prompt Name", placeholder="e.g., Extract Invoice Data", key="new_prompt_name")

        prompt_template = st.text_area(
            "Prompt Template",
            placeholder="Extract the following from {document_type}:\n- Invoice number\n- Date\n- Total amount\n- Line items\n\nFormat as JSON with fields: {output_format}",
            height=150,
            key="new_prompt_template"
        )

        # Variables section
        col1, col2 = st.columns(2)
        with col1:
            variables = st.text_input(
                "Variables (comma-separated)",
                placeholder="document_type, output_format",
                key="new_prompt_vars"
            )
        with col2:
            prompt_category = st.selectbox(
                "Category",
                ["extraction", "analysis", "generation", "validation", "custom"],
                key="new_prompt_category"
            )

        if st.button("Add Prompt Step"):
            if prompt_name and prompt_template:
                # Extract variables from template if not provided
                import re
                detected_vars = re.findall(r'\{([^}]+)\}', prompt_template)
                vars_list = [v.strip() for v in variables.split(',')] if variables else detected_vars

                st.session_state.prompt_steps.append({
                    "prompt_name": prompt_name,
                    "template": prompt_template,
                    "variables": vars_list,
                    "category": prompt_category,
                    "position": len(st.session_state.prompt_steps)
                })
                st.success(f"Added prompt: {prompt_name}")
                st.rerun()

    # Display current prompts
    if st.session_state.prompt_steps:
        st.markdown("**Current Prompt Steps:**")
        for i, prompt in enumerate(st.session_state.prompt_steps):
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                with col1:
                    st.write(f"**{i+1}.**")
                with col2:
                    st.write(f"**{prompt['prompt_name']}** ({prompt['category']})")
                    st.caption(f"Template preview: {prompt['template'][:100]}...")
                    if prompt.get('variables'):
                        st.caption(f"📌 Variables: {', '.join(prompt['variables'])}")
                with col3:
                    if st.button("🗑️", key=f"del_prompt_{i}"):
                        st.session_state.prompt_steps.pop(i)
                        st.rerun()
                st.markdown("---")

    # Example prompts section
    st.markdown("**📚 Example Prompt Templates:**")
    example_cols = st.columns(3)

    examples = [
        {
            "name": "Document Extraction",
            "template": "Extract structured data from {document_type}. Focus on {key_fields}. Output as {format}.",
            "icon": "📄"
        },
        {
            "name": "Data Analysis",
            "template": "Analyze {dataset} for {analysis_type}. Consider {factors}. Provide insights on {metrics}.",
            "icon": "📊"
        },
        {
            "name": "Compliance Check",
            "template": "Review {content} for compliance with {regulations}. Flag any violations of {rules}.",
            "icon": "🔍"
        }
    ]

    for i, example in enumerate(examples):
        with example_cols[i]:
            if st.button(f"{example['icon']} {example['name']}", key=f"ex_prompt_{i}", use_container_width=True):
                # Add example as a prompt step
                st.session_state.prompt_steps.append({
                    "prompt_name": example['name'],
                    "template": example['template'],
                    "variables": re.findall(r'\{([^}]+)\}', example['template']),
                    "category": "extraction" if "Extract" in example['name'] else "analysis",
                    "position": len(st.session_state.prompt_steps)
                })
                st.rerun()

    # Create workflow from prompts
    if st.button("🚀 Create Workflow from Prompts", type="primary", use_container_width=True):
        if workflow_name and st.session_state.prompt_steps:
            try:
                # Import PromptStepsManager
                from domain.services.prompt_steps_manager import PromptStepsManager
                from pathlib import Path
                from datetime import datetime

                # Create workflow directory
                workflows_dir = Path("domain/workflows/projects") / workflow_name
                workflows_dir.mkdir(parents=True, exist_ok=True)

                # Create standard directories including prompts
                for dir_name in ["criteria", "templates", "inputs", "outputs", "resources", "action_steps", "prompts"]:
                    (workflows_dir / dir_name).mkdir(exist_ok=True)

                # Initialize PromptStepsManager
                manager = PromptStepsManager(workflow_name, workflows_dir)

                # Save each prompt step
                for prompt in st.session_state.prompt_steps:
                    result = manager.save_prompt(prompt['prompt_name'].lower().replace(' ', '_'), prompt)
                    if not result['success']:
                        st.error(f"Failed to save prompt {prompt['prompt_name']}: {result.get('error')}")

                # Create workflow config
                workflow_config = {
                    "workflow_id": workflow_name,
                    "workflow_name": workflow_name.replace('_', ' ').title(),
                    "workflow_type": "prompt_based",
                    "description": f"Prompt-based workflow with {len(st.session_state.prompt_steps)} prompt templates",
                    "prompt_steps_count": len(st.session_state.prompt_steps),
                    "created_at": datetime.now().isoformat()
                }

                # Save workflow config
                config_file = workflows_dir / "project_config.json"
                import json
                with open(config_file, 'w') as f:
                    json.dump(workflow_config, f, indent=2)

                st.success(f"✅ Created workflow: {workflow_name}")
                st.success(f"💡 Saved {len(st.session_state.prompt_steps)} prompt templates")
                st.balloons()

                # Clear state
                st.session_state.prompt_steps = []
                del st.session_state.create_mode
                st.rerun()

            except Exception as e:
                st.error(f"Failed to create workflow: {e}")
        else:
            st.warning("Please enter a workflow name and add at least one prompt step")

def _render_ask_ai_flow(workflow_manager, registry):
    """Render AI assistant for workflow creation."""
    st.markdown("### 🤖 **Ask AI Assistant**")
    st.info("Get AI help to design your workflow")

    # Chat interface
    if 'ai_messages' not in st.session_state:
        st.session_state.ai_messages = [
            {"role": "assistant", "content": "Hi! I can help you create a workflow. What would you like to accomplish?"}
        ]

    # Display chat messages
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input
    if user_input := st.chat_input("Ask the AI assistant..."):
        st.session_state.ai_messages.append({"role": "user", "content": user_input})

        # AI response (mock for now)
        ai_response = f"I understand you want to: {user_input}. I suggest creating a workflow with these steps..."
        st.session_state.ai_messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Conversation"):
            st.success("Conversation saved")
    with col2:
        if st.button("🚀 Create Suggested Workflow"):
            st.success("Creating workflow based on AI suggestions...")
            del st.session_state.create_mode
            st.rerun()

def _render_basic_flow(workflow_manager, registry):
    """Render the basic flow creation - simplified version."""
    st.markdown("### 🟢 **Basic Flow Creation**")
    st.info("Quick and easy workflow setup with minimal configuration")

    # Simple form with just essentials
    workflow_name = st.text_input(
        "Workflow Name",
        placeholder="my_simple_workflow",
        help="Enter a simple name for your workflow (no spaces)"
    )

    workflow_purpose = st.selectbox(
        "What will this workflow do?",
        ["Process documents", "Analyze data", "Generate reports", "Extract information"],
        help="Choose the main purpose of your workflow"
    )

    # Create button
    if st.button("✅ **Create Basic Workflow**", type="primary", use_container_width=True):
        if workflow_name:
            # Create basic workflow structure
            workflow_data = {
                "workflow_id": workflow_name,
                "workflow_name": workflow_name.replace('_', ' ').title(),
                "workflow_type": "basic",
                "description": f"Basic workflow for {workflow_purpose.lower()}",
                "steps": [
                    {"step_name": "input", "step_type": "input", "template": ""},
                    {"step_name": "process", "step_type": workflow_purpose.lower().replace(' ', '_'), "template": ""},
                    {"step_name": "output", "step_type": "output", "template": ""}
                ],
                "created_date": datetime.now().isoformat()
            }

            # Save workflow
            try:
                workflows_dir = Path("tidyllm/workflows/projects") / workflow_name
                workflows_dir.mkdir(parents=True, exist_ok=True)

                # Create directory structure
                (workflows_dir / "criteria").mkdir(exist_ok=True)
                (workflows_dir / "templates").mkdir(exist_ok=True)
                (workflows_dir / "inputs").mkdir(exist_ok=True)
                (workflows_dir / "outputs").mkdir(exist_ok=True)
                (workflows_dir / "action_steps").mkdir(exist_ok=True)

                st.success(f"✅ **Created basic workflow**: {workflow_name}")
                st.balloons()

                # Clear state to go back to button selection
                del st.session_state.create_level
                st.rerun()

            except Exception as e:
                st.error(f"❌ **Creation failed**: {e}")
        else:
            st.warning("⚠️ Please enter a workflow name")

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

    # Creation controls - 3 CLEAR CHOICES
    st.markdown("---")
    st.markdown("### Choose your action:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 **Create Now**", type="primary", use_container_width=True):
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
                    (workflows_dir / "action_steps").mkdir(exist_ok=True)

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

    with col2:
        if st.button("💾 **Save Draft**", use_container_width=True):
            st.info("Draft saved (feature coming soon)")

    with col3:
        if st.button("👁️ **Preview**", use_container_width=True):
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