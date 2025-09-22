"""
Manage Flows Tab V4 - Simple Workflow Library
==============================================
View, organize, and manage your workflows
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any

def render_manage_tab():
    """Render the Manage workflows tab - clean library view"""

    st.header("📚 Manage Workflows")
    st.markdown("All your workflows in one place")

    # Get workflows from session
    workflows = st.session_state.get('workflows', {})

    if workflows:
        # Search bar
        search = st.text_input("🔍 Search workflows", placeholder="Type to filter...")

        # Filter workflows
        filtered = {k: v for k, v in workflows.items()
                   if not search or search.lower() in k.lower()}

        # Display workflows as cards
        for name, workflow in filtered.items():
            with st.expander(f"**{name}**", expanded=False):
                # Workflow info in simple format
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown("**Steps:**")
                    for i, card in enumerate(workflow.get('cards', [])):
                        ai_badge = {"None": "⚪", "Assist": "🔵", "Auto": "🟢"}
                        ai_level = card.get('ai_level', 'Assist')
                        st.write(f"{i+1}. {card['name']} {ai_badge[ai_level]}")

                with col2:
                    st.markdown("**Info:**")
                    st.caption(f"Version: {workflow.get('version', '1.0')}")
                    st.caption(f"Cards: {len(workflow.get('cards', []))}")
                    st.caption(f"Created: {workflow.get('created', 'today')}")

                with col3:
                    st.markdown("**Actions:**")

                    # Action buttons
                    if st.button("▶️ Run", key=f"run_{name}", use_container_width=True):
                        st.session_state.current_workflow = name
                        st.info(f"Go to Run tab to execute '{name}'")

                    if st.button("📝 Edit", key=f"edit_{name}", use_container_width=True):
                        _load_for_editing(name, workflow)
                        st.info("Go to Create tab to edit")

                    if st.button("📋 Clone", key=f"clone_{name}", use_container_width=True):
                        _clone_workflow(name, workflow)

                    if st.button("🗑️ Delete", key=f"del_{name}", use_container_width=True):
                        if st.checkbox(f"Confirm delete '{name}'?", key=f"confirm_{name}"):
                            del st.session_state.workflows[name]
                            st.success(f"Deleted '{name}'")
                            st.rerun()

        # Summary stats
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        cols = st.columns(4)

        with cols[0]:
            st.metric("Total Workflows", len(workflows))

        with cols[1]:
            total_cards = sum(len(w.get('cards', [])) for w in workflows.values())
            st.metric("Total Cards", total_cards)

        with cols[2]:
            ai_cards = sum(1 for w in workflows.values()
                          for c in w.get('cards', [])
                          if c.get('ai_level') != 'None')
            st.metric("AI-Enhanced Cards", ai_cards)

        with cols[3]:
            categories = set(c['category'] for w in workflows.values()
                           for c in w.get('cards', []))
            st.metric("Categories Used", len(categories))

    else:
        # Empty state
        st.info("📝 No workflows yet. Go to **Create** tab to build your first workflow!")

        # Sample workflows to get started
        st.markdown("### 🚀 Get Started with Templates")

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container():
                st.markdown("**📄 Document Analyzer**")
                st.caption("Extract → Analyze → Report")
                if st.button("Create from template", key="t1"):
                    _create_sample_workflow("Document Analyzer")

        with col2:
            with st.container():
                st.markdown("**🔍 RAG Assistant**")
                st.caption("Load → Search → Answer")
                if st.button("Create from template", key="t2"):
                    _create_sample_workflow("RAG Assistant")

        with col3:
            with st.container():
                st.markdown("**📊 Data Pipeline**")
                st.caption("Extract → Process → Store")
                if st.button("Create from template", key="t3"):
                    _create_sample_workflow("Data Pipeline")


def _load_for_editing(name: str, workflow: Dict):
    """Load workflow for editing in Create tab"""
    st.session_state.selected_cards = workflow.get('cards', [])
    st.session_state.editing_workflow = name


def _clone_workflow(name: str, workflow: Dict):
    """Clone a workflow with new name"""
    new_name = f"{name} (copy)"
    counter = 1

    # Find unique name
    while new_name in st.session_state.workflows:
        counter += 1
        new_name = f"{name} (copy {counter})"

    # Clone it
    st.session_state.workflows[new_name] = {
        **workflow,
        "name": new_name,
        "created": "today"
    }
    st.success(f"Created '{new_name}'")
    st.rerun()


def _create_sample_workflow(template_name: str):
    """Create a sample workflow from template"""
    templates = {
        "Document Analyzer": {
            "cards": [
                {"id": "extract", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                {"id": "analyze", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Auto"},
                {"id": "report", "name": "📝 Create Report", "category": "act", "ai_level": "Assist"}
            ]
        },
        "RAG Assistant": {
            "cards": [
                {"id": "load", "name": "📊 Load Data", "category": "observe", "ai_level": "None"},
                {"id": "search", "name": "🔎 RAG Search", "category": "observe", "ai_level": "Assist"},
                {"id": "answer", "name": "🤔 Ask Expert", "category": "orient", "ai_level": "Auto"}
            ]
        },
        "Data Pipeline": {
            "cards": [
                {"id": "extract", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                {"id": "process", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"},
                {"id": "store", "name": "💾 Store Results", "category": "act", "ai_level": "None"}
            ]
        }
    }

    if template_name in templates:
        if 'workflows' not in st.session_state:
            st.session_state.workflows = {}

        st.session_state.workflows[template_name] = {
            "name": template_name,
            "version": "1.0",
            "created": "today",
            **templates[template_name]
        }
        st.success(f"Created '{template_name}' workflow!")
        st.rerun()