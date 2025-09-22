#!/usr/bin/env python3
"""
RAG Portal - Hexagonal Architecture Compliant
==============================================

Fixed RAG management portal using delegate pattern.
No direct infrastructure imports - uses RAGDelegate.

Port: 8505
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import delegate (proper hexagonal architecture)
try:
    from packages.tidyllm.infrastructure.delegates.rag_delegate import get_rag_delegate
    from packages.tidyllm.infrastructure.rag_delegate import RAGSystemType  # Keep enum from old location
except ImportError as e:
    # Fallback if running from different location
    qa_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(qa_root))
    from packages.tidyllm.infrastructure.delegates.rag_delegate import get_rag_delegate
    from packages.tidyllm.infrastructure.rag_delegate import RAGSystemType

# Initialize delegate
rag_delegate = get_rag_delegate()

def set_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="RAG Portal - Management Interface",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_operation' not in st.session_state:
        st.session_state.current_operation = 'browse'
    if 'selected_system_type' not in st.session_state:
        st.session_state.selected_system_type = RAGSystemType.AI_POWERED
    if 'show_detailed_view' not in st.session_state:
        st.session_state.show_detailed_view = False
    if 'last_operation_result' not in st.session_state:
        st.session_state.last_operation_result = None

def render_header():
    """Render the portal header"""
    st.title("🧠 RAG Portal - Management Interface")
    st.markdown("**Manage RAG systems using hexagonal architecture delegate pattern**")

    # Quick status
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delegate_status = "Available" if rag_delegate.is_available() else "Unavailable"
        st.metric("Delegate Status", delegate_status)

    with col2:
        systems = rag_delegate.get_available_systems()
        st.metric("System Types", len(systems))

    with col3:
        instances = rag_delegate.list_systems()
        st.metric("Active Instances", len(instances))

    with col4:
        metrics = rag_delegate.get_metrics()
        success_rate = f"{metrics.get('overall_success_rate', 0)*100:.1f}%"
        st.metric("Success Rate", success_rate)

    st.markdown("---")

def render_navigation_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.title("🎛️ RAG Operations")

        # Operation selection
        st.subheader("📋 Operations")
        operations = {
            'browse': '📖 Browse Systems',
            'create': '➕ Create System',
            'update': '✏️ Update System',
            'delete': '🗑️ Delete System',
            'health': '🏥 Health Dashboard'
        }

        for op_key, op_label in operations.items():
            if st.button(op_label, use_container_width=True):
                st.session_state.current_operation = op_key
                st.rerun()

        # System type selection
        st.subheader("🤖 System Types")
        systems = rag_delegate.get_available_systems()
        system_options = list(systems.keys())

        st.session_state.selected_system_type = st.selectbox(
            "Select System Type:",
            system_options,
            index=system_options.index(st.session_state.selected_system_type) if st.session_state.selected_system_type in system_options else 0
        )

        # Options
        st.subheader("⚙️ Options")
        st.session_state.show_detailed_view = st.checkbox(
            "Detailed View",
            value=st.session_state.show_detailed_view
        )

        # Delegate status
        st.subheader("🔌 Delegate Status")
        if rag_delegate.is_available():
            st.success("✅ RAG Delegate Connected")
        else:
            st.error("❌ RAG Delegate Unavailable")

def render_browse_systems():
    """Render browse systems interface"""
    st.subheader("📖 Browse RAG Systems")

    # Available system types
    systems = rag_delegate.get_available_systems()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("**Available System Types:**")
        for system_type, info in systems.items():
            with st.expander(f"{info['icon']} {info['name']}"):
                st.write(f"**Description:** {info['description']}")
                st.write(f"**Capabilities:** {', '.join(info['capabilities'])}")
                st.write(f"**Use Cases:** {', '.join(info['use_cases'])}")

                # Check availability
                available = rag_delegate.check_system_availability(system_type)
                status = "🟢 Available" if available else "🔴 Unavailable"
                st.write(f"**Status:** {status}")

    with col2:
        st.write("**Active Instances:**")
        instances = rag_delegate.list_systems()

        if instances:
            for instance in instances:
                with st.container():
                    st.write(f"**{instance['name']}**")
                    st.write(f"Type: {instance['type']}")
                    st.write(f"Status: {instance['status']}")
                    st.write(f"Health: {instance['health_score']:.2f}")
                    st.write(f"Collections: {instance['collections_count']}")
                    st.write("---")
        else:
            st.info("No active instances found")

def render_create_system():
    """Render create system interface"""
    st.subheader("➕ Create RAG System")

    systems = rag_delegate.get_available_systems()
    selected_system = systems.get(st.session_state.selected_system_type, {})

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Creating: {selected_system.get('name', 'Unknown System')}**")
        st.write(f"Description: {selected_system.get('description', '')}")

        # Configuration form
        with st.form("create_system_form"):
            collection_name = st.text_input(
                "Collection Name:",
                value=f"rag_{st.session_state.selected_system_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            model_preference = st.selectbox(
                "Model Preference:",
                ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"]
            )

            temperature = st.slider(
                "Temperature:",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )

            context_window = st.number_input(
                "Context Window Size:",
                min_value=1000,
                max_value=32000,
                value=4000,
                step=1000
            )

            submit_create = st.form_submit_button("🚀 Create System")

            if submit_create:
                config = {
                    'collection_name': collection_name,
                    'model_preference': model_preference,
                    'temperature': temperature,
                    'context_window': context_window,
                    'system_type': st.session_state.selected_system_type
                }

                with st.spinner("Creating RAG system..."):
                    result = rag_delegate.create_system(st.session_state.selected_system_type, config)
                    st.session_state.last_operation_result = result

                if result.get('success'):
                    st.success(f"✅ {result.get('message')}")
                    st.write(f"System ID: {result.get('system_id')}")
                else:
                    st.error(f"❌ {result.get('error')}")

    with col2:
        st.write("**System Capabilities:**")
        for capability in selected_system.get('capabilities', []):
            st.write(f"• {capability}")

        st.write("**Recommended Use Cases:**")
        for use_case in selected_system.get('use_cases', []):
            st.write(f"• {use_case}")

def render_update_system():
    """Render update system interface"""
    st.subheader("✏️ Update RAG System")

    instances = rag_delegate.list_systems()

    if not instances:
        st.info("No systems available to update. Create a system first.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Select system to update
        system_options = {inst['system_id']: f"{inst['name']} ({inst['type']})" for inst in instances}
        selected_system_id = st.selectbox(
            "Select System to Update:",
            options=list(system_options.keys()),
            format_func=lambda x: system_options[x]
        )

        # Update form
        with st.form("update_system_form"):
            st.write(f"**Updating: {system_options[selected_system_id]}**")

            new_model = st.selectbox(
                "New Model Preference:",
                ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"]
            )

            new_temperature = st.slider(
                "New Temperature:",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )

            submit_update = st.form_submit_button("🔄 Update System")

            if submit_update:
                config = {
                    'model_preference': new_model,
                    'temperature': new_temperature
                }

                with st.spinner("Updating RAG system..."):
                    result = rag_delegate.update_system(selected_system_id, config)
                    st.session_state.last_operation_result = result

                if result.get('success'):
                    st.success(f"✅ {result.get('message')}")
                    st.write(f"Updated fields: {', '.join(result.get('updated_fields', []))}")
                else:
                    st.error(f"❌ {result.get('error')}")

    with col2:
        # Show current system details
        selected_instance = next((inst for inst in instances if inst['system_id'] == selected_system_id), None)
        if selected_instance:
            st.write("**Current System Details:**")
            st.json(selected_instance)

def render_delete_system():
    """Render delete system interface"""
    st.subheader("🗑️ Delete RAG System")

    instances = rag_delegate.list_systems()

    if not instances:
        st.info("No systems available to delete.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Select system to delete
        system_options = {inst['system_id']: f"{inst['name']} ({inst['type']})" for inst in instances}
        selected_system_id = st.selectbox(
            "Select System to Delete:",
            options=list(system_options.keys()),
            format_func=lambda x: system_options[x]
        )

        st.warning("⚠️ This action cannot be undone!")

        confirm_delete = st.text_input(
            "Type 'DELETE' to confirm:",
            placeholder="DELETE"
        )

        if st.button("🗑️ Delete System", type="primary"):
            if confirm_delete == "DELETE":
                with st.spinner("Deleting RAG system..."):
                    result = rag_delegate.delete_system(selected_system_id)
                    st.session_state.last_operation_result = result

                if result.get('success'):
                    st.success(f"✅ {result.get('message')}")
                else:
                    st.error(f"❌ {result.get('error')}")
            else:
                st.error("Please type 'DELETE' to confirm deletion")

    with col2:
        # Show system details
        selected_instance = next((inst for inst in instances if inst['system_id'] == selected_system_id), None)
        if selected_instance:
            st.write("**System to Delete:**")
            st.json(selected_instance)

def render_health_dashboard():
    """Render health monitoring dashboard"""
    st.subheader("🏥 Health Dashboard")

    if not rag_delegate.is_available():
        st.error("❌ RAG delegate unavailable - cannot show health data")
        return

    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)

    metrics = rag_delegate.get_metrics()

    with col1:
        avg_time = metrics.get('avg_response_time_ms', 0)
        st.metric("Avg Response Time", f"{avg_time}ms")

    with col2:
        success_rate = metrics.get('overall_success_rate', 0)
        st.metric("Success Rate", f"{success_rate*100:.1f}%")

    with col3:
        queries_today = metrics.get('queries_today', 0)
        st.metric("Queries Today", queries_today)

    with col4:
        instances = rag_delegate.list_systems()
        healthy_count = sum(1 for inst in instances if inst['status'] == 'healthy')
        st.metric("Healthy Systems", f"{healthy_count}/{len(instances)}")

    # System health details
    st.subheader("📊 System Health Details")

    systems = rag_delegate.get_available_systems()

    for system_type, system_info in systems.items():
        with st.expander(f"{system_info['icon']} {system_info['name']} Health"):
            health = rag_delegate.get_system_health(system_type)

            col1, col2 = st.columns(2)

            with col1:
                status = health.get('status', 'unknown')
                status_color = "🟢" if status == "healthy" else "🔴"
                st.write(f"**Status:** {status_color} {status}")
                st.write(f"**Response Time:** {health.get('response_time_ms', 0)}ms")
                st.write(f"**Success Rate:** {health.get('success_rate', 0)*100:.1f}%")

            with col2:
                st.write(f"**Last Checked:** {health.get('last_checked', 'Never')}")
                st.write(f"**Queries Processed:** {health.get('queries_processed', 0)}")
                if health.get('error'):
                    st.error(f"Error: {health['error']}")

    # Trend data
    st.subheader("📈 Performance Trends")

    trend_data = rag_delegate.get_trend_data()

    if trend_data.get('timestamps'):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Response Time Trend:**")
            st.line_chart({
                'Response Time (ms)': trend_data['response_times']
            })

        with col2:
            st.write("**Success Rate Trend:**")
            st.line_chart({
                'Success Rate': trend_data['success_rates']
            })

def render_operation_result():
    """Display last operation result"""
    if st.session_state.last_operation_result:
        result = st.session_state.last_operation_result

        if result.get('success'):
            st.success(f"✅ Operation completed: {result.get('message', 'Success')}")
        else:
            st.error(f"❌ Operation failed: {result.get('error', 'Unknown error')}")

        if st.button("Clear Result"):
            st.session_state.last_operation_result = None
            st.rerun()

def main():
    """Main application"""
    set_page_config()
    initialize_session_state()

    # Render navigation sidebar
    render_navigation_sidebar()

    # Main content area
    render_header()

    # Show operation result if any
    render_operation_result()

    # Render based on current operation
    if st.session_state.current_operation == 'browse':
        render_browse_systems()
    elif st.session_state.current_operation == 'create':
        render_create_system()
    elif st.session_state.current_operation == 'update':
        render_update_system()
    elif st.session_state.current_operation == 'delete':
        render_delete_system()
    elif st.session_state.current_operation == 'health':
        render_health_dashboard()

if __name__ == "__main__":
    main()