"""
Enhanced Manage Flows Tab - Complete CRUD with Detailed UI
===========================================================
Full workflow and card management with testing capabilities
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import copy

class WorkflowManager:
    """Handles all workflow CRUD operations"""

    def __init__(self, project_name: str = None):
        self.domain_path = Path(__file__).parent.parent.parent / "domain" / "workflows"
        self.project_name = project_name

        if project_name:
            # Project-specific storage
            self.project_dir = self.domain_path / "projects" / project_name
            self.project_dir.mkdir(parents=True, exist_ok=True)
            self.workflows_file = self.project_dir / "workflows.json"
            self.versions_dir = self.project_dir / "versions"
        else:
            # Global workflows
            self.workflows_file = self.domain_path / "portal_workflows.json"
            self.versions_dir = self.domain_path / "versions"

        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def load_workflows(self) -> Dict:
        """Load workflows from domain file"""
        if self.workflows_file.exists():
            with open(self.workflows_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('workflows', {})
        return {}

    def save_workflows(self, workflows: Dict) -> bool:
        """Save workflows to domain file"""
        try:
            data = {"workflows": workflows}
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Save failed: {e}")
            return False

    def create_version_backup(self, workflow_name: str, workflow_data: Dict):
        """Create versioned backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = workflow_data.get('version', '1.0')
        backup_file = self.versions_dir / f"{workflow_name}_v{version}_{timestamp}.json"

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)

    def validate_workflow_name(self, name: str, current_name: str = None) -> tuple[bool, str]:
        """Validate workflow name is unique"""
        workflows = self.load_workflows()

        if not name or len(name.strip()) == 0:
            return False, "Name cannot be empty"

        if name != current_name and name in workflows:
            return False, f"Workflow '{name}' already exists"

        return True, ""

    def get_available_cards(self) -> Dict:
        """Get all available card templates with full attributes"""
        return {
            "observe": [
                {
                    "id": "extract_document",
                    "name": "📄 Extract Document",
                    "ai_level": "None",
                    "step_type": "process",
                    "kind": "extract",
                    "description": "Extracts text and metadata from documents (PDF, Word, etc.)",
                    "requires": ["document_path"],
                    "produces": ["extracted_text", "metadata"],
                    "params": {"format": "text", "include_metadata": "true", "ocr_enabled": "false"},
                    "validation_rules": {"file_exists": "true", "max_size_mb": "10"}
                },
                {
                    "id": "load_data",
                    "name": "📊 Load Data",
                    "ai_level": "None",
                    "step_type": "process",
                    "kind": "extract",
                    "description": "Loads data from various sources (CSV, JSON, database)",
                    "requires": ["data_source"],
                    "produces": ["dataframe", "data_summary"],
                    "params": {"format": "auto", "encoding": "utf-8"},
                    "validation_rules": {"source_exists": "true"}
                },
                {
                    "id": "rag_search",
                    "name": "🔎 RAG Search",
                    "ai_level": "None",
                    "step_type": "process",
                    "kind": "extract",
                    "description": "Performs semantic search using RAG (Retrieval Augmented Generation)",
                    "requires": ["query", "knowledge_base"],
                    "produces": ["search_results", "relevant_chunks"],
                    "params": {"top_k": "5", "similarity_threshold": "0.7"},
                    "validation_rules": {"query_min_length": "3"}
                },
                {
                    "id": "extract_metadata",
                    "name": "📊 Extract Metadata",
                    "ai_level": "None",
                    "step_type": "process",
                    "kind": "extract",
                    "description": "Extracts structured metadata from documents and files",
                    "requires": ["file_path"],
                    "produces": ["metadata_json", "file_properties"],
                    "params": {"include_system": "true", "parse_headers": "true"},
                    "validation_rules": {"file_readable": "true"}
                }
            ],
            "orient": [
                {
                    "id": "analyze_content",
                    "name": "💡 Analyze Content",
                    "ai_level": "Assist",
                    "step_type": "analyze",
                    "kind": "summarize",
                    "description": "Analyzes content using AI to extract insights and patterns",
                    "requires": ["content"],
                    "produces": ["analysis", "insights"],
                    "params": {"depth": "detailed", "focus_areas": "all"},
                    "validation_rules": {"content_min_length": "100"}
                },
                {
                    "id": "compare_docs",
                    "name": "🔄 Compare Documents",
                    "ai_level": "Assist",
                    "step_type": "analyze",
                    "kind": "summarize",
                    "description": "Compares multiple documents to find similarities and differences",
                    "requires": ["document_1", "document_2"],
                    "produces": ["comparison_report", "diff_highlights"],
                    "params": {"comparison_type": "semantic", "detail_level": "high"},
                    "validation_rules": {"min_documents": "2"}
                },
                {
                    "id": "ask_expert",
                    "name": "🤔 Ask Expert",
                    "ai_level": "Auto",
                    "step_type": "prompt",
                    "kind": "classify",
                    "description": "Consults AI expert for domain-specific guidance",
                    "requires": ["question", "context"],
                    "produces": ["expert_answer", "references"],
                    "params": {"expertise_level": "advanced", "include_sources": "true"},
                    "validation_rules": {"question_min_length": "10"}
                },
                {
                    "id": "extract_entities",
                    "name": "🔍 Extract Entities",
                    "ai_level": "Assist",
                    "step_type": "analyze",
                    "kind": "extract",
                    "description": "Identifies and extracts named entities (people, places, organizations)",
                    "requires": ["text_content"],
                    "produces": ["entities_list", "entity_relationships"],
                    "params": {"entity_types": "all", "confidence_threshold": "0.8"},
                    "validation_rules": {"text_min_length": "50"}
                }
            ],
            "decide": [
                {
                    "id": "evaluate_options",
                    "name": "⚖️ Evaluate Options",
                    "ai_level": "Auto",
                    "step_type": "analyze",
                    "kind": "classify",
                    "description": "Evaluates multiple options against defined criteria",
                    "requires": ["options", "criteria"],
                    "produces": ["evaluation_scores", "recommendation"],
                    "params": {"scoring_method": "weighted", "normalize": "true"},
                    "validation_rules": {"min_options": "2", "min_criteria": "1"}
                },
                {
                    "id": "generate_insights",
                    "name": "🎯 Generate Insights",
                    "ai_level": "Auto",
                    "step_type": "transform",
                    "kind": "summarize",
                    "description": "Generates actionable insights from analyzed data",
                    "requires": ["analysis_results"],
                    "produces": ["insights_report", "action_items"],
                    "params": {"insight_depth": "comprehensive", "priority_ranking": "true"},
                    "validation_rules": {"data_completeness": "80%"}
                },
                {
                    "id": "risk_assessment",
                    "name": "⚠️ Risk Assessment",
                    "ai_level": "Auto",
                    "step_type": "analyze",
                    "kind": "classify",
                    "description": "Evaluates potential risks and provides mitigation strategies",
                    "requires": ["scenario", "risk_factors"],
                    "produces": ["risk_score", "mitigation_plan"],
                    "params": {"risk_model": "comprehensive", "include_probability": "true"},
                    "validation_rules": {"factors_min": "3"}
                }
            ],
            "act": [
                {
                    "id": "create_report",
                    "name": "📝 Create Report",
                    "ai_level": "Assist",
                    "step_type": "output",
                    "kind": "report",
                    "description": "Creates formatted reports from processed data",
                    "requires": ["report_data", "template"],
                    "produces": ["report_document", "summary"],
                    "params": {"format": "pdf", "include_visualizations": "true"},
                    "validation_rules": {"required_sections": "summary,details,conclusion"}
                },
                {
                    "id": "send_results",
                    "name": "📧 Send Results",
                    "ai_level": "None",
                    "step_type": "output",
                    "kind": "notify",
                    "description": "Sends results via email or other channels",
                    "requires": ["results", "recipients"],
                    "produces": ["delivery_status", "tracking_id"],
                    "params": {"channel": "email", "priority": "normal"},
                    "validation_rules": {"valid_recipients": "true"}
                },
                {
                    "id": "save_outputs",
                    "name": "💾 Save Outputs",
                    "ai_level": "None",
                    "step_type": "output",
                    "kind": "report",
                    "description": "Saves processed outputs to specified storage location",
                    "requires": ["output_data", "destination"],
                    "produces": ["saved_path", "checksum"],
                    "params": {"format": "json", "compression": "none"},
                    "validation_rules": {"destination_writable": "true"}
                }
            ]
        }


def render_manage_tab():
    """Enhanced Manage tab with full CRUD capabilities"""

    st.header("📚 Manage Workflows")
    st.markdown("Organize and configure your workflows")

    # Use the global project selection from session state
    projects_dir = Path(__file__).parent.parent.parent / "domain" / "workflows" / "projects"

    # Get selected project from session state
    selected_project = st.session_state.get('selected_project', 'global')
    project_name = None if selected_project == "global" else selected_project

    # Show current context
    current_workflow = st.session_state.get('current_workflow')
    if selected_project != 'global' or current_workflow:
        context_msg = []
        if selected_project != 'global':
            context_msg.append(f"**Project:** {selected_project}")
        if current_workflow:
            context_msg.append(f"**Workflow:** {current_workflow}")
        st.info(" | ".join(context_msg))

    # Initialize manager with project
    manager = WorkflowManager(project_name=project_name)

    # Always reload workflows for the current project
    st.session_state.workflows = manager.load_workflows()

    # Initialize session state
    if 'selected_workflow' not in st.session_state:
        st.session_state.selected_workflow = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # REMOVED workflow selector - using the main page selector instead
    # The workflow selector was causing confusion with multiple dropdowns
    # Now the main page handles project/action selection consistently

    # Quick actions for workflows
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ New Workflow", use_container_width=True):
            _create_new_workflow()
    with col2:
        if st.button("📥 Import", use_container_width=True):
            st.info("Import feature coming soon")
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.workflows = manager.load_workflows()
            st.rerun()

    # Add sub-navigation tabs for project resources
    st.markdown("---")

    if project_name:
        # Show tabs for project resources
        workflows_tab, criteria_tab, templates_tab, inputs_tab = st.tabs([
            "🔄 Workflows",
            "📋 Criteria",
            "📝 Templates/Prompts",
            "📂 Inputs/Uploads"
        ])

        with workflows_tab:
            render_workflows_section(manager, project_name, projects_dir)

        with criteria_tab:
            render_criteria_section(project_name, projects_dir)

        with templates_tab:
            render_templates_section(project_name, projects_dir)

        with inputs_tab:
            render_inputs_section(project_name, projects_dir)
    else:
        # For global, only show workflows
        render_workflows_section(manager, project_name, projects_dir)


def render_workflows_section(manager, project_name, projects_dir):
    """Render the workflows management section"""

    # Initialize other session state
    if 'original_workflow' not in st.session_state:
        st.session_state.original_workflow = None
    if 'has_changes' not in st.session_state:
        st.session_state.has_changes = False

    # Main Content Area
    if st.session_state.selected_workflow:
        workflow = st.session_state.workflows[st.session_state.selected_workflow]

        if not st.session_state.edit_mode:
            # READ MODE
            _render_read_mode(workflow, manager)
        else:
            # EDIT MODE
            _render_edit_mode(workflow, manager)

    elif not st.session_state.workflows:
        # No workflows exist - show in the workflows tab content area
        st.info("No workflows found. Click '➕ New' above to create your first workflow!")

        # Quick start templates
        st.markdown("### Quick Start Templates")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Document Analyzer", key="template_doc_analyzer", use_container_width=True):
                _create_template_workflow("Document Analyzer", manager)

        with col2:
            if st.button("🔍 RAG Pipeline", key="template_rag_pipeline", use_container_width=True):
                _create_template_workflow("RAG Pipeline", manager)

        with col3:
            if st.button("📊 Data Processing", key="template_data_processing", use_container_width=True):
                _create_template_workflow("Data Processing", manager)


def _render_read_mode(workflow: Dict, manager: WorkflowManager):
    """Render workflow in read-only mode"""

    # Workflow Header
    st.markdown(f"### {workflow['name']}")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Version:** {workflow.get('version', '1.0')}")
        st.write(f"**Created:** {workflow.get('created', 'Unknown')}")

    with col2:
        st.write(f"**Cards:** {len(workflow.get('cards', []))}")
        ai_count = sum(1 for c in workflow.get('cards', []) if c.get('ai_level') != 'None')
        st.write(f"**AI Cards:** {ai_count}")

    with col3:
        st.write(f"**Status:** Active")
        st.write(f"**Runs:** {workflow.get('run_count', 0)}")

    if desc := workflow.get('description'):
        st.info(desc)

    # Cards Display with Full Attributes
    st.markdown("### Workflow Cards")

    cards = workflow.get('cards', [])
    if cards:
        for i, card in enumerate(cards):
            with st.expander(f"**{i+1}. {card['name']}** ({card.get('category', 'unknown')})", expanded=False):
                # Basic Info Row
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Card ID:** {card.get('id', 'unknown')}")
                    ai_badges = {"None": "⚪", "Assist": "🔵", "Auto": "🟢"}
                    ai_level = card.get('ai_level', 'None')
                    st.write(f"**AI Level:** {ai_badges.get(ai_level, '')} {ai_level}")

                with col2:
                    st.write(f"**Category:** {card.get('category', 'unknown')}")
                    st.write(f"**Step Type:** {card.get('step_type', 'process')}")

                with col3:
                    st.write(f"**Position:** #{i + 1}")
                    st.write(f"**Kind:** {card.get('kind', 'Not set')}")

                st.markdown("---")

                # Core 8 Attributes - NOW EDITABLE IN VIEW MODE
                st.markdown("**📋 Core Attributes** *(Click to edit)*")

                # Description - Editable
                desc = card.get('description', '')
                if not desc:
                    desc = f"Processes {card.get('name', 'data')} using {card.get('category', 'method')}"

                new_desc = st.text_area(
                    "**Description**",
                    value=desc,
                    key=f"view_desc_{i}",
                    help="Edit the description directly"
                )
                if new_desc != desc:
                    card['description'] = new_desc
                    st.session_state.has_changes = True
                    manager.save_workflows(st.session_state.workflows)
                    st.success("✅ Description updated!", icon="✅")

                # Requirements and Outputs - Editable
                col4, col5 = st.columns(2)
                with col4:
                    requires = card.get('requires', [])
                    requires_str = ", ".join(requires)
                    new_requires = st.text_input(
                        "**🔗 Requires (inputs)**",
                        value=requires_str,
                        key=f"view_requires_{i}",
                        placeholder="e.g., document, user_query",
                        help="Comma-separated list of inputs"
                    )
                    if new_requires != requires_str:
                        card['requires'] = [r.strip() for r in new_requires.split(',') if r.strip()]
                        st.session_state.has_changes = True
                        manager.save_workflows(st.session_state.workflows)

                with col5:
                    produces = card.get('produces', [])
                    produces_str = ", ".join(produces)
                    new_produces = st.text_input(
                        "**📤 Produces (outputs)**",
                        value=produces_str,
                        key=f"view_produces_{i}",
                        placeholder="e.g., summary, entities",
                        help="Comma-separated list of outputs"
                    )
                    if new_produces != produces_str:
                        card['produces'] = [p.strip() for p in new_produces.split(',') if p.strip()]
                        st.session_state.has_changes = True
                        manager.save_workflows(st.session_state.workflows)

                # Parameters and Validation - Editable
                col6, col7 = st.columns(2)
                with col6:
                    st.markdown("**⚙️ Parameters** *(key=value pairs)*")
                    params = card.get('params', {})
                    params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
                    new_params = st.text_area(
                        "",
                        value=params_str,
                        key=f"view_params_{i}",
                        placeholder="e.g., format=pdf, max_length=500",
                        help="Enter as key=value pairs, comma-separated",
                        height=80
                    )
                    if new_params != params_str:
                        # Parse key=value pairs
                        new_params_dict = {}
                        if new_params:
                            for pair in new_params.split(','):
                                if '=' in pair:
                                    k, v = pair.strip().split('=', 1)
                                    new_params_dict[k.strip()] = v.strip()
                        card['params'] = new_params_dict
                        st.session_state.has_changes = True
                        manager.save_workflows(st.session_state.workflows)

                with col7:
                    st.markdown("**✅ Validation Rules** *(key=value pairs)*")
                    validation = card.get('validation_rules', {})
                    validation_str = ", ".join([f"{k}={v}" for k, v in validation.items()])
                    new_validation = st.text_area(
                        "",
                        value=validation_str,
                        key=f"view_validation_{i}",
                        placeholder="e.g., min_length=100, required=true",
                        help="Enter as key=value pairs, comma-separated",
                        height=80
                    )
                    if new_validation != validation_str:
                        # Parse key=value pairs
                        new_validation_dict = {}
                        if new_validation:
                            for pair in new_validation.split(','):
                                if '=' in pair:
                                    k, v = pair.strip().split('=', 1)
                                    new_validation_dict[k.strip()] = v.strip()
                        card['validation_rules'] = new_validation_dict
                        st.session_state.has_changes = True
                        manager.save_workflows(st.session_state.workflows)
    else:
        st.warning("No cards in this workflow")

    # Action Buttons
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("▶️ Run", key="run_workflow_btn", use_container_width=True):
            st.session_state.current_workflow = workflow['name']
            st.success("Go to Run tab to execute")

    with col2:
        if st.button("✏️ Edit", key="edit_workflow_btn", use_container_width=True):
            st.session_state.edit_mode = True
            st.session_state.original_workflow = copy.deepcopy(workflow)
            st.session_state.has_changes = False
            st.rerun()

    with col3:
        if st.button("📋 Clone", key="clone_workflow_btn", use_container_width=True):
            _clone_workflow(workflow['name'], manager)

    with col4:
        if st.button("📤 Export", key="export_workflow_btn", use_container_width=True):
            _export_workflow(workflow)

    with col5:
        if st.button("🗑️ Delete", key="delete_workflow_btn", type="secondary", use_container_width=True):
            _delete_workflow(workflow['name'], manager)


def _render_edit_mode(workflow: Dict, manager: WorkflowManager):
    """Render workflow in edit mode"""

    st.markdown("### 📝 Edit Mode")

    if st.session_state.has_changes:
        st.warning("⚠️ You have unsaved changes")

    # Metadata Editing
    with st.form("workflow_metadata"):
        st.markdown("#### Workflow Details")

        # Name
        new_name = st.text_input(
            "Name:",
            value=workflow['name'],
            key="edit_name"
        )

        # Version
        col1, col2 = st.columns(2)
        with col1:
            current_version = workflow.get('version', '1.0')
            st.text_input("Current Version:", value=current_version, disabled=True)

        with col2:
            # Suggest next version
            parts = current_version.split('.')
            suggested = f"{parts[0]}.{int(parts[1]) + 1}" if len(parts) > 1 else "1.1"
            new_version = st.text_input("New Version:", value=suggested)

        # Description
        new_description = st.text_area(
            "Description:",
            value=workflow.get('description', ''),
            height=100
        )

        # Update button
        if st.form_submit_button("Update Details"):
            valid, error = manager.validate_workflow_name(new_name, workflow['name'])
            if valid:
                workflow['name'] = new_name
                workflow['version'] = new_version
                workflow['description'] = new_description
                st.session_state.has_changes = True
                st.success("Details updated")
                st.rerun()
            else:
                st.error(error)

    # Cards Editing
    st.markdown("#### Workflow Cards")

    cards = workflow.get('cards', [])

    # Display cards with full attribute editing
    for i, card in enumerate(cards):
        with st.expander(f"**{i+1}. {card['name']}** ({card.get('category', 'unknown')})", expanded=False):
            # Position controls
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                st.markdown("**Position**")
                if i > 0:
                    if st.button("⬆ Move Up", key=f"up_{i}"):
                        cards[i], cards[i-1] = cards[i-1], cards[i]
                        card['position'] = i - 1
                        cards[i]['position'] = i
                        st.session_state.has_changes = True
                        st.rerun()
                if i < len(cards) - 1:
                    if st.button("⬇ Move Down", key=f"down_{i}"):
                        cards[i], cards[i+1] = cards[i+1], cards[i]
                        card['position'] = i + 1
                        cards[i]['position'] = i
                        st.session_state.has_changes = True
                        st.rerun()

            with col2:
                # AI Level selector
                ai_options = ["None", "Assist", "Auto"]
                current_ai = card.get('ai_level', 'None')
                new_ai = st.selectbox(
                    "**AI Level**",
                    ai_options,
                    index=ai_options.index(current_ai),
                    key=f"ai_{i}"
                )
                if new_ai != current_ai:
                    card['ai_level'] = new_ai
                    st.session_state.has_changes = True

            with col3:
                # Step Type selector
                step_types = ["process", "transform", "analyze", "output", "validation", "prompt"]
                current_type = card.get('step_type', 'process')
                new_type = st.selectbox(
                    "**Step Type**",
                    step_types,
                    index=step_types.index(current_type) if current_type in step_types else 0,
                    key=f"step_type_{i}"
                )
                if new_type != current_type:
                    card['step_type'] = new_type
                    st.session_state.has_changes = True

            st.markdown("---")

            # 8 Core Attributes Editing
            st.markdown("**📋 Edit Core Attributes**")

            # Description
            current_desc = card.get('description', '')
            if not current_desc:
                current_desc = f"Processes {card.get('name', 'data')} using {card.get('category', 'method')}"

            new_desc = st.text_area(
                "**Description**",
                value=current_desc,
                key=f"desc_{i}",
                help="Describe what this card does"
            )
            if new_desc != current_desc:
                card['description'] = new_desc
                st.session_state.has_changes = True

            # Requirements and Outputs
            col4, col5 = st.columns(2)
            with col4:
                requires_str = ", ".join(card.get('requires', []))
                new_requires = st.text_input(
                    "**Requires (comma-separated)**",
                    value=requires_str,
                    key=f"requires_{i}",
                    help="Input dependencies, e.g., 'document, user_query'"
                )
                if new_requires != requires_str:
                    card['requires'] = [r.strip() for r in new_requires.split(',') if r.strip()]
                    st.session_state.has_changes = True

            with col5:
                produces_str = ", ".join(card.get('produces', []))
                new_produces = st.text_input(
                    "**Produces (comma-separated)**",
                    value=produces_str,
                    key=f"produces_{i}",
                    help="Output artifacts, e.g., 'summary, entities'"
                )
                if new_produces != produces_str:
                    card['produces'] = [p.strip() for p in new_produces.split(',') if p.strip()]
                    st.session_state.has_changes = True

            # Parameters (JSON)
            st.markdown("**Parameters (JSON format)**")
            params = card.get('params', {})
            params_str = json.dumps(params, indent=2) if params else "{}"
            new_params_str = st.text_area(
                "Edit Parameters",
                value=params_str,
                key=f"params_{i}",
                height=100,
                label_visibility="collapsed"
            )
            try:
                new_params = json.loads(new_params_str)
                if new_params != params:
                    card['params'] = new_params
                    st.session_state.has_changes = True
            except json.JSONDecodeError:
                st.error("Invalid JSON format for parameters")

            # Validation Rules (JSON)
            st.markdown("**Validation Rules (JSON format)**")
            validation = card.get('validation_rules', {})
            validation_str = json.dumps(validation, indent=2) if validation else "{}"
            new_validation_str = st.text_area(
                "Edit Validation Rules",
                value=validation_str,
                key=f"validation_{i}",
                height=100,
                label_visibility="collapsed"
            )
            try:
                new_validation = json.loads(new_validation_str)
                if new_validation != validation:
                    card['validation_rules'] = new_validation
                    st.session_state.has_changes = True
            except json.JSONDecodeError:
                st.error("Invalid JSON format for validation rules")

            # Kind selector
            kind_options = ["classify", "extract", "summarize", "report", "validate", "notify", "Not set"]
            current_kind = card.get('kind', 'Not set')
            new_kind = st.selectbox(
                "**Kind (for model routing)**",
                kind_options,
                index=kind_options.index(current_kind) if current_kind in kind_options else len(kind_options)-1,
                key=f"kind_{i}"
            )
            if new_kind != current_kind and new_kind != "Not set":
                card['kind'] = new_kind
                st.session_state.has_changes = True

            # Delete button
            if st.button(f"🗑️ Delete Card", key=f"del_{i}", type="secondary"):
                cards.pop(i)
                st.session_state.has_changes = True
                st.rerun()

            st.divider()

    # Add Card Section
    with st.expander("➕ Add New Card"):
        available_cards = manager.get_available_cards()

        tabs = st.tabs(["🔍 Observe", "🧠 Orient", "✅ Decide", "⚡ Act"])

        for tab_idx, (category, category_cards) in enumerate(available_cards.items()):
            with tabs[tab_idx]:
                for card_template in category_cards:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{card_template['name']}")
                    with col2:
                        if st.button("Add", key=f"add_{card_template['id']}"):
                            new_card = {
                                **card_template,
                                "category": category,
                                "position": len(cards)  # Set position based on current list length
                            }
                            cards.append(new_card)
                            st.session_state.has_changes = True
                            st.success(f"Added {card_template['name']}")
                            st.rerun()

    # Save/Cancel Buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("💾 Save", key="save_changes_btn", type="primary", use_container_width=True):
            # Create backup before saving
            manager.create_version_backup(workflow['name'], st.session_state.original_workflow)

            # Update workflow
            workflow['cards'] = cards
            st.session_state.workflows[workflow['name']] = workflow

            # Save to domain
            if manager.save_workflows(st.session_state.workflows):
                st.session_state.edit_mode = False
                st.session_state.has_changes = False
                st.success("✅ Workflow saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save workflow")

    with col2:
        if st.button("❌ Cancel", key="cancel_changes_btn", use_container_width=True):
            if st.session_state.has_changes:
                st.warning("You have unsaved changes. Click again to confirm cancel.")
                if st.button("Confirm Cancel", key="confirm_cancel_btn", type="secondary"):
                    # Restore original
                    st.session_state.workflows[workflow['name']] = st.session_state.original_workflow
                    st.session_state.edit_mode = False
                    st.session_state.has_changes = False
                    st.rerun()
            else:
                st.session_state.edit_mode = False
                st.rerun()


def _create_new_workflow():
    """Create a new workflow"""
    with st.form("new_workflow"):
        st.subheader("Create New Workflow")

        name = st.text_input("Workflow Name:")
        description = st.text_area("Description:", height=100)

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Create", type="primary"):
                if name:
                    manager = WorkflowManager()
                    valid, error = manager.validate_workflow_name(name)

                    if valid:
                        new_workflow = {
                            "name": name,
                            "version": "1.0",
                            "created": datetime.now().strftime("%Y-%m-%d"),
                            "description": description,
                            "cards": []
                        }

                        st.session_state.workflows[name] = new_workflow
                        manager.save_workflows(st.session_state.workflows)

                        st.session_state.selected_workflow = name
                        st.session_state.edit_mode = True
                        st.success(f"Created '{name}'! Add cards to build your workflow.")
                        st.rerun()
                    else:
                        st.error(error)
                else:
                    st.error("Please enter a workflow name")

        with col2:
            if st.form_submit_button("Cancel"):
                st.rerun()


def _clone_workflow(name: str, manager: WorkflowManager):
    """Clone an existing workflow"""
    workflow = st.session_state.workflows[name]

    # Generate unique name
    new_name = f"{name} (copy)"
    counter = 1
    while new_name in st.session_state.workflows:
        counter += 1
        new_name = f"{name} (copy {counter})"

    # Create clone
    cloned = copy.deepcopy(workflow)
    cloned['name'] = new_name
    cloned['created'] = datetime.now().strftime("%Y-%m-%d")
    cloned['version'] = "1.0"

    # Save
    st.session_state.workflows[new_name] = cloned
    manager.save_workflows(st.session_state.workflows)

    st.session_state.selected_workflow = new_name
    st.success(f"Created '{new_name}'")
    st.rerun()


def _delete_workflow(name: str, manager: WorkflowManager):
    """Delete a workflow with confirmation"""
    if st.checkbox(f"⚠️ Confirm delete '{name}'?", key="confirm_delete"):
        if st.button("Delete Forever", key="confirm_delete_btn", type="secondary"):
            # Archive first
            workflow = st.session_state.workflows[name]
            manager.create_version_backup(f"DELETED_{name}", workflow)

            # Delete
            del st.session_state.workflows[name]
            manager.save_workflows(st.session_state.workflows)

            st.session_state.selected_workflow = None
            st.success(f"Deleted '{name}'")
            st.rerun()


def _export_workflow(workflow: Dict):
    """Export workflow as JSON"""
    json_str = json.dumps(workflow, indent=2)

    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"{workflow['name']}_export.json",
        mime="application/json"
    )


def render_criteria_section(project_name: str, projects_dir: Path):
    """Render the criteria files management section"""
    st.markdown("### 📋 JSON Criteria Files")

    project_path = projects_dir / project_name
    criteria_path = project_path / "criteria"

    if criteria_path.exists():
        json_files = list(criteria_path.glob("*.json"))

        if json_files:
            for json_file in json_files:
                with st.expander(f"📄 {json_file.name}", expanded=False):
                    col_preview, col_actions = st.columns([3, 1])

                    with col_preview:
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                content = json.load(f)
                            st.json(content)
                        except Exception as e:
                            st.error(f"Error reading file: {e}")

                    with col_actions:
                        if st.button("🗑️ Delete", key=f"del_criteria_{json_file.name}"):
                            json_file.unlink()
                            st.success(f"Deleted {json_file.name}")
                            st.rerun()

                        with open(json_file, 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f.read(),
                                file_name=json_file.name,
                                mime="application/json",
                                key=f"download_criteria_{json_file.name}"
                            )
        else:
            st.info("📋 No criteria files found")
    else:
        st.warning("📂 Criteria folder not found")

    # Upload criteria files
    st.markdown("---")
    st.markdown("**⬆️ Upload JSON Criteria Files**")
    uploaded_criteria = st.file_uploader(
        "Choose JSON criteria files",
        type=['json'],
        accept_multiple_files=True,
        key=f"criteria_upload_{project_name}",
        help="Upload JSON files to the criteria folder"
    )

    if uploaded_criteria:
        criteria_path.mkdir(parents=True, exist_ok=True)
        for uploaded_file in uploaded_criteria:
            file_path = criteria_path / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Uploaded {uploaded_file.name} to criteria/")
        st.rerun()


def render_templates_section(project_name: str, projects_dir: Path):
    """Render the templates/prompts management section"""
    st.markdown("### 📝 Template & Prompt Files")

    project_path = projects_dir / project_name
    templates_path = project_path / "templates"
    prompts_path = project_path / "prompts"

    # Show templates
    if templates_path.exists():
        md_files = list(templates_path.glob("*.md"))
        txt_files = list(templates_path.glob("*.txt"))
        all_template_files = md_files + txt_files

        if all_template_files:
            st.markdown("**Templates:**")
            for template_file in all_template_files:
                with st.expander(f"📄 {template_file.name}", expanded=False):
                    col_preview, col_actions = st.columns([3, 1])

                    with col_preview:
                        try:
                            with open(template_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            if template_file.suffix == '.md':
                                st.markdown(content)
                            else:
                                st.text(content)
                        except Exception as e:
                            st.error(f"Error reading file: {e}")

                    with col_actions:
                        if st.button("🗑️ Delete", key=f"del_template_{template_file.name}"):
                            template_file.unlink()
                            st.success(f"Deleted {template_file.name}")
                            st.rerun()

                        with open(template_file, 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f.read(),
                                file_name=template_file.name,
                                mime="text/plain",
                                key=f"download_template_{template_file.name}"
                            )
        else:
            st.info("📝 No template files found")
    else:
        st.info("📂 Templates folder not found")

    # Show prompts
    if prompts_path.exists():
        prompt_files = list(prompts_path.glob("*.txt")) + list(prompts_path.glob("*.md"))
        if prompt_files:
            st.markdown("**Prompts:**")
            for prompt_file in prompt_files:
                with st.expander(f"💬 {prompt_file.name}", expanded=False):
                    col_preview, col_actions = st.columns([3, 1])

                    with col_preview:
                        try:
                            with open(prompt_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            st.text(content)
                        except Exception as e:
                            st.error(f"Error reading file: {e}")

                    with col_actions:
                        if st.button("🗑️ Delete", key=f"del_prompt_{prompt_file.name}"):
                            prompt_file.unlink()
                            st.success(f"Deleted {prompt_file.name}")
                            st.rerun()

                        with open(prompt_file, 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f.read(),
                                file_name=prompt_file.name,
                                mime="text/plain",
                                key=f"download_prompt_{prompt_file.name}"
                            )

    # Upload template/prompt files
    st.markdown("---")
    st.markdown("**⬆️ Upload Template/Prompt Files**")
    uploaded_templates = st.file_uploader(
        "Choose template or prompt files",
        type=['md', 'txt'],
        accept_multiple_files=True,
        key=f"templates_upload_{project_name}",
        help="Upload markdown or text files to templates/prompts folders"
    )

    if uploaded_templates:
        templates_path.mkdir(parents=True, exist_ok=True)
        for uploaded_file in uploaded_templates:
            file_path = templates_path / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"✅ Uploaded {uploaded_file.name} to templates/")
        st.rerun()


def render_inputs_section(project_name: str, projects_dir: Path):
    """Render the inputs/uploads management section"""
    st.markdown("### 📂 Input Files & Uploads")

    project_path = projects_dir / project_name
    inputs_path = project_path / "inputs"
    uploads_path = project_path / "uploads"

    # Show existing input files
    for folder_name, folder_path in [("inputs", inputs_path), ("uploads", uploads_path)]:
        st.markdown(f"**{folder_name.capitalize()} Folder:**")

        if folder_path.exists():
            input_files = list(folder_path.glob("*"))

            if input_files:
                for input_file in input_files:
                    if input_file.is_file():
                        file_size = input_file.stat().st_size
                        file_ext = input_file.suffix.lower()

                        # File type icon
                        if file_ext in ['.pdf']:
                            icon = "📄"
                        elif file_ext in ['.docx', '.doc']:
                            icon = "📝"
                        elif file_ext in ['.xlsx', '.xls', '.csv']:
                            icon = "📊"
                        elif file_ext in ['.txt', '.md']:
                            icon = "📋"
                        else:
                            icon = "📁"

                        with st.expander(f"{icon} {input_file.name} ({file_size:,} bytes)", expanded=False):
                            col_a, col_b = st.columns([3, 1])

                            with col_a:
                                st.markdown(f"**File:** {input_file.name}")
                                st.markdown(f"**Size:** {file_size:,} bytes")
                                st.markdown(f"**Type:** {file_ext.upper() if file_ext else 'Unknown'}")

                                mod_time = datetime.fromtimestamp(input_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                                st.markdown(f"**Modified:** {mod_time}")

                            with col_b:
                                # Download file
                                with open(input_file, 'rb') as f:
                                    st.download_button(
                                        "⬇️ Download",
                                        data=f.read(),
                                        file_name=input_file.name,
                                        key=f"download_{folder_name}_{input_file.name}"
                                    )

                                # Delete file
                                if st.button("🗑️ Delete", key=f"delete_{folder_name}_{input_file.name}"):
                                    input_file.unlink()
                                    st.success(f"✅ Deleted {input_file.name}")
                                    st.rerun()
            else:
                st.info(f"📂 No files in {folder_name} folder")
        else:
            st.info(f"📂 {folder_name.capitalize()} folder not found")

        st.markdown("---")

    # Upload new input files
    st.markdown("**⬆️ Upload New Input Files**")
    new_input_files = st.file_uploader(
        "Upload files for workflow processing",
        type=['pdf', 'docx', 'txt', 'md', 'csv', 'json', 'xlsx'],
        accept_multiple_files=True,
        key=f"upload_new_inputs_{project_name}",
        help="Upload documents to be processed by the workflow"
    )

    if new_input_files:
        inputs_path.mkdir(parents=True, exist_ok=True)

        for uploaded_file in new_input_files:
            try:
                # Save uploaded file
                file_path = inputs_path / uploaded_file.name
                content = uploaded_file.read()

                with open(file_path, 'wb') as f:
                    f.write(content)

                st.success(f"✅ Uploaded: {uploaded_file.name} to inputs/")

            except Exception as e:
                st.error(f"❌ Upload error: {e}")

        st.rerun()


def _create_template_workflow(template_name: str, manager: WorkflowManager):
    """Create workflow from template"""
    templates = {
        "Document Analyzer": {
            "description": "Analyze documents with AI assistance",
            "cards": [
                {"id": "extract_document", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"},
                {"id": "generate_insights", "name": "🎯 Generate Insights", "category": "decide", "ai_level": "Auto"},
                {"id": "create_report", "name": "📝 Create Report", "category": "act", "ai_level": "Assist"}
            ]
        },
        "RAG Pipeline": {
            "description": "RAG-based question answering system",
            "cards": [
                {"id": "load_data", "name": "📊 Load Data", "category": "observe", "ai_level": "None"},
                {"id": "rag_search", "name": "🔎 RAG Search", "category": "observe", "ai_level": "None"},
                {"id": "ask_expert", "name": "🤔 Ask Expert", "category": "orient", "ai_level": "Auto"},
                {"id": "create_report", "name": "📝 Create Report", "category": "act", "ai_level": "Assist"}
            ]
        },
        "Data Processing": {
            "description": "Process and analyze data files",
            "cards": [
                {"id": "load_data", "name": "📊 Load Data", "category": "observe", "ai_level": "None"},
                {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"},
                {"id": "save_outputs", "name": "💾 Save Outputs", "category": "act", "ai_level": "None"}
            ]
        }
    }

    if template_name in templates:
        template = templates[template_name]

        workflow = {
            "name": template_name,
            "version": "1.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "description": template['description'],
            "cards": template['cards']
        }

        st.session_state.workflows[template_name] = workflow
        manager.save_workflows(st.session_state.workflows)

        st.session_state.selected_workflow = template_name
        st.success(f"Created '{template_name}' from template")
        st.rerun()


# Make it available for import
if __name__ == "__main__":
    render_manage_tab()