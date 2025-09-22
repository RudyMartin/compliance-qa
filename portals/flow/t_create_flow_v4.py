"""
Create Flow Tab V4 - Simple Card-Based Workflow Builder
========================================================
Easy drag-and-drop workflow creation with Business Builder cards
"""

import streamlit as st
from pathlib import Path
import json
from typing import Dict, List, Any

def render_create_tab():
    """Render the Create workflow tab - simple and clean"""

    st.header("📝 Create New Workflow")

    # Check if user selected "Create new workflow" from the selector
    if st.session_state.get('show_create_message', False):
        current_project = st.session_state.get('selected_project', 'global')
        st.success(f"🎯 Creating new workflow in project: **{current_project}**")
        # Clear the flag after showing
        st.session_state.show_create_message = False

    st.markdown("Build workflows by selecting cards. Each card does one specific task.")

    # Two columns: Card Library | Workflow Builder
    col1, col2 = st.columns([1, 2])

    # LEFT: Card Library
    with col1:
        st.subheader("Card Library")
        st.caption("Click cards to add them →")

        # Initialize selected cards in session
        if 'selected_cards' not in st.session_state:
            st.session_state.selected_cards = []

        # Card categories - simple and clear
        with st.expander("🔍 **OBSERVE** - Get Data", expanded=True):
            if st.button("📄 Extract Document", use_container_width=True):
                _add_card("extract_document", "📄 Extract Document", "observe")
            if st.button("🔎 RAG Search", use_container_width=True):
                _add_card("rag_search", "🔎 RAG Search", "observe")
            if st.button("📊 Load Data", use_container_width=True):
                _add_card("load_data", "📊 Load Data", "observe")

        with st.expander("🧠 **ORIENT** - Understand", expanded=False):
            if st.button("💡 Analyze Content", use_container_width=True):
                _add_card("analyze_content", "💡 Analyze Content", "orient")
            if st.button("🔄 Compare Documents", use_container_width=True):
                _add_card("compare_docs", "🔄 Compare Documents", "orient")
            if st.button("🤔 Ask Expert", use_container_width=True):
                _add_card("ask_expert", "🤔 Ask Expert", "orient")

        with st.expander("✅ **DECIDE** - Make Choices", expanded=False):
            if st.button("⚖️ Evaluate Options", use_container_width=True):
                _add_card("evaluate", "⚖️ Evaluate Options", "decide")
            if st.button("🎯 Generate Insights", use_container_width=True):
                _add_card("insights", "🎯 Generate Insights", "decide")

        with st.expander("⚡ **ACT** - Take Action", expanded=False):
            if st.button("📝 Create Report", use_container_width=True):
                _add_card("create_report", "📝 Create Report", "act")
            if st.button("📧 Send Results", use_container_width=True):
                _add_card("send_results", "📧 Send Results", "act")

    # RIGHT: Workflow Builder
    with col2:
        st.subheader("Your Workflow")

        # Workflow name - simple input
        workflow_name = st.text_input(
            "Workflow Name",
            placeholder="e.g., Document Analysis",
            help="Give your workflow a descriptive name"
        )

        # Show selected cards as workflow steps
        if st.session_state.selected_cards:
            st.markdown("### Workflow Steps")

            # Display each card with full attribute controls
            for i, card in enumerate(st.session_state.selected_cards):
                with st.expander(f"**{i+1}. {card['name']}** ({card.get('category', 'unknown')})", expanded=False):
                    # Position and basic controls
                    col1, col2, col3 = st.columns([1, 3, 2])

                    with col1:
                        st.markdown("**Position**")
                        if i > 0:
                            if st.button("⬆", key=f"up_{i}", help="Move up"):
                                st.session_state.selected_cards[i], st.session_state.selected_cards[i-1] = \
                                    st.session_state.selected_cards[i-1], st.session_state.selected_cards[i]
                                st.rerun()
                        if i < len(st.session_state.selected_cards) - 1:
                            if st.button("⬇", key=f"down_{i}", help="Move down"):
                                st.session_state.selected_cards[i], st.session_state.selected_cards[i+1] = \
                                    st.session_state.selected_cards[i+1], st.session_state.selected_cards[i]
                                st.rerun()

                    with col2:
                        # AI Level control
                        ai_level = st.select_slider(
                            "**AI Level**",
                            options=["None", "Assist", "Auto"],
                            value=card.get('ai_level', "Assist"),
                            key=f"ai_{i}",
                            help="None: Just data • Assist: AI helps • Auto: AI decides"
                        )
                        card['ai_level'] = ai_level

                    with col3:
                        # Step Type selector
                        step_types = ["process", "transform", "analyze", "output", "validation", "prompt"]
                        step_type = st.selectbox(
                            "**Step Type**",
                            step_types,
                            index=step_types.index(card.get('step_type', 'process')) if card.get('step_type', 'process') in step_types else 0,
                            key=f"step_type_{i}"
                        )
                        card['step_type'] = step_type

                    st.markdown("---")

                    # Core 8 Attributes
                    st.markdown("**📋 Configure Card Attributes**")

                    # Description
                    description = st.text_area(
                        "**Description**",
                        value=card.get('description', f"Processes {card['name']} for {card.get('category', 'workflow')}"),
                        key=f"desc_{i}",
                        help="Describe what this card does"
                    )
                    card['description'] = description

                    # Requirements and Outputs
                    col4, col5 = st.columns(2)
                    with col4:
                        requires = st.text_input(
                            "**Requires (comma-separated)**",
                            value=", ".join(card.get('requires', [])),
                            key=f"requires_{i}",
                            placeholder="e.g., document, user_query"
                        )
                        card['requires'] = [r.strip() for r in requires.split(',') if r.strip()]

                    with col5:
                        produces = st.text_input(
                            "**Produces (comma-separated)**",
                            value=", ".join(card.get('produces', [])),
                            key=f"produces_{i}",
                            placeholder="e.g., summary, entities"
                        )
                        card['produces'] = [p.strip() for p in produces.split(',') if p.strip()]

                    # Parameters
                    col6, col7 = st.columns(2)
                    with col6:
                        st.markdown("**Parameters (key=value pairs)**")
                        params_text = st.text_area(
                            "Parameters",
                            value="\n".join([f"{k}={v}" for k, v in card.get('params', {}).items()]),
                            key=f"params_{i}",
                            height=80,
                            label_visibility="collapsed",
                            placeholder="max_length=500\ntemperature=0.7"
                        )
                        # Parse parameters
                        params = {}
                        for line in params_text.split('\n'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                params[key.strip()] = value.strip()
                        card['params'] = params

                    with col7:
                        st.markdown("**Validation Rules (key=value pairs)**")
                        validation_text = st.text_area(
                            "Validation",
                            value="\n".join([f"{k}={v}" for k, v in card.get('validation_rules', {}).items()]),
                            key=f"validation_{i}",
                            height=80,
                            label_visibility="collapsed",
                            placeholder="min_length=10\nrequired_fields=title,body"
                        )
                        # Parse validation rules
                        validation = {}
                        for line in validation_text.split('\n'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                validation[key.strip()] = value.strip()
                        card['validation_rules'] = validation

                    # Kind selector for model routing
                    kind_options = ["Not set", "classify", "extract", "summarize", "report", "validate", "notify"]
                    kind = st.selectbox(
                        "**Kind (for model routing)**",
                        kind_options,
                        index=kind_options.index(card.get('kind', 'Not set')) if card.get('kind', 'Not set') in kind_options else 0,
                        key=f"kind_{i}"
                    )
                    if kind != "Not set":
                        card['kind'] = kind

                    # Delete button
                    if st.button(f"🗑️ Remove Card", key=f"del_{i}", type="secondary"):
                        st.session_state.selected_cards.pop(i)
                        st.rerun()

            # Action buttons
            col_save, col_test, col_clear = st.columns(3)

            with col_save:
                if st.button("💾 **Save Workflow**", type="primary", use_container_width=True):
                    if workflow_name:
                        _save_workflow(workflow_name)
                        st.success(f"✅ Saved '{workflow_name}'!")
                    else:
                        st.error("Please enter a workflow name")

            with col_test:
                if st.button("🧪 Test Workflow", use_container_width=True):
                    st.info("Testing will be available in the Run tab")

            with col_clear:
                if st.button("🔄 Clear All", use_container_width=True):
                    st.session_state.selected_cards = []
                    st.rerun()
        else:
            # Empty state - helpful message
            st.info("👈 Select cards from the library to build your workflow")

            # Quick templates for beginners
            st.markdown("### Quick Start Templates")

            template_cols = st.columns(3)
            with template_cols[0]:
                if st.button("📄 Document Analysis", use_container_width=True):
                    _load_template("document_analysis")

            with template_cols[1]:
                if st.button("🔍 RAG Q&A", use_container_width=True):
                    _load_template("rag_qa")

            with template_cols[2]:
                if st.button("📊 Data Processing", use_container_width=True):
                    _load_template("data_processing")


def _add_card(card_id: str, card_name: str, category: str):
    """Add a card to the workflow with full attributes"""

    # Define default attributes based on card type
    default_attrs = {
        "extract_document": {
            "description": "Extracts text and metadata from documents (PDF, Word, etc.)",
            "requires": ["document_path"],
            "produces": ["extracted_text", "metadata"],
            "params": {"format": "text", "include_metadata": "true"},
            "validation_rules": {"file_exists": "true", "max_size_mb": "10"},
            "step_type": "process",
            "kind": "extract"
        },
        "rag_search": {
            "description": "Performs semantic search using RAG (Retrieval Augmented Generation)",
            "requires": ["query", "knowledge_base"],
            "produces": ["search_results", "relevant_chunks"],
            "params": {"top_k": "5", "similarity_threshold": "0.7"},
            "validation_rules": {"query_min_length": "3"},
            "step_type": "process",
            "kind": "extract"
        },
        "load_data": {
            "description": "Loads data from various sources (CSV, JSON, database)",
            "requires": ["data_source"],
            "produces": ["dataframe", "data_summary"],
            "params": {"format": "auto", "encoding": "utf-8"},
            "validation_rules": {"source_exists": "true"},
            "step_type": "process",
            "kind": "extract"
        },
        "analyze_content": {
            "description": "Analyzes content using AI to extract insights and patterns",
            "requires": ["content"],
            "produces": ["analysis", "insights"],
            "params": {"depth": "detailed", "focus_areas": "all"},
            "validation_rules": {"content_min_length": "100"},
            "step_type": "analyze",
            "kind": "summarize"
        },
        "compare_docs": {
            "description": "Compares multiple documents to find similarities and differences",
            "requires": ["document_1", "document_2"],
            "produces": ["comparison_report", "diff_highlights"],
            "params": {"comparison_type": "semantic", "detail_level": "high"},
            "validation_rules": {"min_documents": "2"},
            "step_type": "analyze",
            "kind": "summarize"
        },
        "ask_expert": {
            "description": "Consults AI expert for domain-specific guidance",
            "requires": ["question", "context"],
            "produces": ["expert_answer", "references"],
            "params": {"expertise_level": "advanced", "include_sources": "true"},
            "validation_rules": {"question_min_length": "10"},
            "step_type": "prompt",
            "kind": "classify"
        },
        "evaluate": {
            "description": "Evaluates options against criteria to make decisions",
            "requires": ["options", "criteria"],
            "produces": ["evaluation_scores", "recommendation"],
            "params": {"scoring_method": "weighted", "normalize": "true"},
            "validation_rules": {"min_options": "2", "min_criteria": "1"},
            "step_type": "analyze",
            "kind": "classify"
        },
        "insights": {
            "description": "Generates actionable insights from analyzed data",
            "requires": ["analysis_results"],
            "produces": ["insights_report", "action_items"],
            "params": {"insight_depth": "comprehensive", "priority_ranking": "true"},
            "validation_rules": {"data_completeness": "80%"},
            "step_type": "transform",
            "kind": "summarize"
        },
        "create_report": {
            "description": "Creates formatted reports from processed data",
            "requires": ["report_data", "template"],
            "produces": ["report_document", "summary"],
            "params": {"format": "pdf", "include_visualizations": "true"},
            "validation_rules": {"required_sections": "summary,details,conclusion"},
            "step_type": "output",
            "kind": "report"
        },
        "send_results": {
            "description": "Sends results via email or other channels",
            "requires": ["results", "recipients"],
            "produces": ["delivery_status", "tracking_id"],
            "params": {"channel": "email", "priority": "normal"},
            "validation_rules": {"valid_recipients": "true"},
            "step_type": "output",
            "kind": "notify"
        }
    }

    # Get default attributes or create generic ones
    attrs = default_attrs.get(card_id, {
        "description": f"Processes {card_name} for {category} operations",
        "requires": [],
        "produces": [],
        "params": {},
        "validation_rules": {},
        "step_type": "process",
        "kind": "extract"
    })

    card = {
        "id": card_id,
        "name": card_name,
        "category": category,
        "ai_level": "Assist",  # Default AI assistance
        "position": len(st.session_state.selected_cards),
        **attrs  # Add all the default attributes
    }
    st.session_state.selected_cards.append(card)
    st.success(f"Added: {card_name}")


def _save_workflow(name: str):
    """Save the workflow to the selected project"""
    workflow = {
        "name": name,
        "cards": st.session_state.selected_cards,
        "version": "1.0",
        "created": "today",
        "description": f"Created workflow with {len(st.session_state.selected_cards)} steps"
    }

    # Get selected project from session state
    selected_project = st.session_state.get('selected_project', 'Global')

    if selected_project != 'Global':
        # Save to project-specific workflows
        project_dir = Path(__file__).parent.parent.parent / "domain" / "workflows" / "projects" / selected_project
        project_dir.mkdir(parents=True, exist_ok=True)
        workflow_file = project_dir / "workflows.json"

        # Load existing workflows
        if workflow_file.exists():
            with open(workflow_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                workflows = data.get('workflows', {})
        else:
            workflows = {}

        # Add new workflow
        workflows[name] = workflow

        # Save back
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump({"workflows": workflows}, f, indent=2)
    else:
        # Save to global workflows
        if 'workflows' not in st.session_state:
            st.session_state.workflows = {}
        st.session_state.workflows[name] = workflow

        # Also save to file
        workflow_file = Path(__file__).parent.parent.parent / "domain" / "workflows" / "portal_workflows.json"

        if workflow_file.exists():
            with open(workflow_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                workflows = data.get('workflows', {})
        else:
            workflows = {}

        workflows[name] = workflow

        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump({"workflows": workflows}, f, indent=2)

    st.session_state.current_workflow = name


def _load_template(template_type: str):
    """Load a pre-made template"""
    templates = {
        "document_analysis": [
            {"id": "extract_document", "name": "📄 Extract Document", "category": "observe"},
            {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient"},
            {"id": "insights", "name": "🎯 Generate Insights", "category": "decide"},
            {"id": "create_report", "name": "📝 Create Report", "category": "act"}
        ],
        "rag_qa": [
            {"id": "load_data", "name": "📊 Load Data", "category": "observe"},
            {"id": "rag_search", "name": "🔎 RAG Search", "category": "observe"},
            {"id": "ask_expert", "name": "🤔 Ask Expert", "category": "orient"},
            {"id": "send_results", "name": "📧 Send Results", "category": "act"}
        ],
        "data_processing": [
            {"id": "load_data", "name": "📊 Load Data", "category": "observe"},
            {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient"},
            {"id": "evaluate", "name": "⚖️ Evaluate Options", "category": "decide"},
            {"id": "create_report", "name": "📝 Create Report", "category": "act"}
        ]
    }

    if template_type in templates:
        st.session_state.selected_cards = templates[template_type]
        st.success(f"Loaded {template_type.replace('_', ' ').title()} template!")
        st.rerun()