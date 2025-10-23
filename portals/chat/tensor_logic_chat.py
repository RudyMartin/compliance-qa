#!/usr/bin/env python3
"""
Tensor Logic Chat Portal
=========================
Interactive Streamlit chat interface for tensor logic compliance QA.

Features:
- Temperature slider for reasoning mode control
- Document upload (PDF, JSON, text)
- Real-time compliance checking
- Entity similarity search
- Training data management
- Result visualization
"""

import streamlit as st
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.factories.tensor_logic_factory import create_tensor_logic_service
from domain.services.tensor_logic import ReasoningMode


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Tensor Logic Compliance QA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session State
# ============================================================================

if 'service' not in st.session_state:
    st.session_state.service = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'training_data' not in st.session_state:
    st.session_state.training_data = []


# ============================================================================
# Initialization
# ============================================================================

def initialize_service():
    """Initialize tensor logic service."""
    if st.session_state.service is None:
        with st.spinner("Initializing Tensor Logic service..."):
            try:
                st.session_state.service = create_tensor_logic_service(mode='auto')
                st.success("✅ Service initialized!")
            except Exception as e:
                st.error(f"Failed to initialize service: {e}")
                st.session_state.service = create_tensor_logic_service(mode='mock')
                st.warning("⚠️ Using mock mode (Cleanlab API not available)")


# ============================================================================
# Sidebar
# ============================================================================

st.sidebar.title("🧠 Tensor Logic QA")
st.sidebar.markdown("---")

# Temperature Control
st.sidebar.header("🌡️ Reasoning Control")

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.1,
    step=0.1,
    help="""
    Controls reasoning mode:
    - 0.0: Pure symbolic (certifiable)
    - 0.1-0.4: Hybrid (rules + analogies)
    - 0.5+: Analogical (learn from similar)
    """
)

# Show reasoning mode
initialize_service()
service = st.session_state.service

if service:
    mode = service.get_reasoning_mode(temperature)
    mode_colors = {
        ReasoningMode.SYMBOLIC: "🟢",
        ReasoningMode.HYBRID: "🟡",
        ReasoningMode.ANALOGICAL: "🔵"
    }

    mode_icon = mode_colors.get(mode, "⚪")
    st.sidebar.info(f"{mode_icon} **{mode.value.upper()}** mode")

    description = service.get_reasoning_description(temperature)
    st.sidebar.caption(description)

st.sidebar.markdown("---")

# Compliance Standard
st.sidebar.header("📋 Compliance Standard")
compliance_standard = st.sidebar.selectbox(
    "Standard",
    ["MVS_5.4.3", "VST_3.0", "SR_11-7"],
    help="Select compliance standard to check against"
)

st.sidebar.markdown("---")

# Service Status
st.sidebar.header("📊 Service Status")
if service:
    stats = service.get_statistics()
    st.sidebar.metric("Training Entities", stats['entities_loaded'])
    st.sidebar.metric("Trustworthiness Mode", stats['trustworthiness_mode'])
    st.sidebar.metric("Embedding Method", stats['embedding_method'])

st.sidebar.markdown("---")

# Quick Actions
st.sidebar.header("⚡ Quick Actions")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

if st.sidebar.button("🔄 Reset Service"):
    st.session_state.service = None
    st.rerun()


# ============================================================================
# Main Content
# ============================================================================

st.title("🧠 Tensor Logic Compliance QA")
st.markdown(
    f"**Temperature-controlled reasoning** for regulatory compliance. "
    f"Currently at **T={temperature:.1f}** in **{mode.value}** mode."
)

# ============================================================================
# Tabs
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat",
    "📄 Document Check",
    "🔍 Entity Search",
    "📚 Training Data"
])

# ============================================================================
# Tab 1: Chat Interface
# ============================================================================

with tab1:
    st.header("💬 Interactive Chat")

    # Display chat history
    for msg in st.session_state.chat_history:
        role = msg['role']
        content = msg['content']

        with st.chat_message(role):
            st.markdown(content)

            if role == 'assistant' and 'result' in msg:
                result = msg['result']

                # Show metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Confidence", f"{result.confidence:.1%}")

                with col2:
                    st.metric("Trustworthiness", f"{result.trustworthiness_score:.1%}")

                with col3:
                    cert_icon = "✅" if result.certifiable else "⚠️"
                    st.metric("Certifiable", cert_icon)

                with col4:
                    st.metric("Mode", result.reasoning_mode.value)

                # Show explanation
                with st.expander("📖 Explanation"):
                    st.markdown(result.explanation)

                # Show evidence
                if result.rules_applied:
                    with st.expander(f"⚖️ Rules Applied ({len(result.rules_applied)})"):
                        for rule in result.rules_applied[:5]:
                            st.write(f"- {rule.rule_name}")

                if result.similar_entities:
                    with st.expander(f"🔗 Similar Entities ({len(result.similar_entities)})"):
                        for entity in result.similar_entities[:3]:
                            st.write(
                                f"- {entity.entity_id}: "
                                f"{entity.similarity_score:.1%} similar, "
                                f"outcome: {entity.outcome}"
                            )

    # Chat input
    user_query = st.chat_input(
        "Ask a compliance question...",
        key="chat_input"
    )

    if user_query and service:
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })

        # Process query
        with st.spinner("Reasoning..."):
            try:
                result = service.tensor_logic_service.infer(
                    query=user_query,
                    context={'document': {}},
                    temperature=temperature,
                    compliance_standard=compliance_standard,
                    score_trustworthiness=True
                )

                # Add assistant response
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': f"**Answer**: {result.answer}",
                    'result': result
                })

                st.rerun()

            except Exception as e:
                st.error(f"Error processing query: {e}")


# ============================================================================
# Tab 2: Document Compliance Check
# ============================================================================

with tab2:
    st.header("📄 Document Compliance Check")

    st.info(
        f"Upload a document to check against **{compliance_standard}** "
        f"using **T={temperature:.1f}** reasoning."
    )

    # File upload
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=['json', 'txt', 'pdf'],
        help="Upload JSON, text, or PDF document"
    )

    # Or paste JSON
    st.markdown("**Or paste JSON document:**")
    json_input = st.text_area(
        "Document (JSON)",
        height=200,
        placeholder='{"executive_summary": "...", "methodology": "..."}'
    )

    if st.button("🔍 Check Compliance", type="primary"):
        document_data = {}

        # Parse document
        if uploaded_file:
            try:
                if uploaded_file.type == 'application/json':
                    document_data = json.load(uploaded_file)
                else:
                    content = uploaded_file.read().decode('utf-8')
                    document_data = {'content': content}
            except Exception as e:
                st.error(f"Error reading file: {e}")

        elif json_input:
            try:
                document_data = json.loads(json_input)
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

        if document_data and service:
            with st.spinner("Checking compliance..."):
                result = service.check_compliance(
                    document=document_data,
                    compliance_standard=compliance_standard,
                    temperature=temperature
                )

                # Display result
                st.markdown("---")
                st.subheader("📊 Compliance Result")

                # Metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    answer_color = "🟢" if result.answer else "🔴"
                    st.metric("Compliance Status", f"{answer_color} {result.answer}")

                with col2:
                    st.metric("Confidence", f"{result.confidence:.1%}")

                with col3:
                    cert = "✅ Yes" if result.certifiable else "⚠️ No"
                    st.metric("Certifiable", cert)

                # Explanation
                st.markdown("### 📖 Explanation")
                st.markdown(result.explanation)

                # Remediation plan
                if not result.answer or result.answer != 'COMPLIANT':
                    st.markdown("### 🔧 Remediation Plan")
                    remediation = service.get_remediation_plan(
                        document=document_data,
                        compliance_standard=compliance_standard
                    )

                    if remediation:
                        for item in remediation:
                            with st.expander(f"📌 {item['requirement_id']} - {item['priority']}"):
                                st.write(f"**Requirement**: {item['requirement']}")
                                st.write(f"**Status**: {item['current_status']}")

                                if item['failed_criteria']:
                                    st.write("**Failed Criteria**:")
                                    for criterion in item['failed_criteria']:
                                        st.write(f"- {criterion}")

                                st.write("**Recommended Actions**:")
                                for action in item['actions']:
                                    st.write(f"- {action}")


# ============================================================================
# Tab 3: Entity Similarity Search
# ============================================================================

with tab3:
    st.header("🔍 Entity Similarity Search")

    st.info("Find entities similar to a query entity using embedding-based reasoning.")

    col1, col2 = st.columns(2)

    with col1:
        entity_id = st.text_input("Entity ID", placeholder="entity_123")

    with col2:
        top_k = st.number_input("Number of Results", min_value=1, max_value=20, value=5)

    entity_json = st.text_area(
        "Entity Data (JSON)",
        height=150,
        placeholder='{"name": "Example Bank", "type": "Financial", "assets": "10B"}'
    )

    if st.button("🔎 Find Similar", type="primary"):
        if entity_id and entity_json and service:
            try:
                entity_data = json.loads(entity_json)

                with st.spinner("Finding similar entities..."):
                    result = service.find_similar_entities(
                        entity_id=entity_id,
                        entity_data=entity_data,
                        temperature=temperature,
                        top_k=top_k
                    )

                    st.markdown("---")
                    st.subheader("🔗 Similar Entities")

                    if result.similar_entities:
                        for i, entity in enumerate(result.similar_entities, 1):
                            with st.expander(f"{i}. {entity.entity_id} ({entity.similarity_score:.1%} similar)"):
                                st.write(f"**Similarity**: {entity.similarity_score:.1%}")
                                st.write(f"**Outcome**: {entity.outcome}")
                                st.write(f"**Weight**: {entity.weight:.3f}")

                                if entity.attributes:
                                    st.json(entity.attributes)
                    else:
                        st.warning("No similar entities found. Try increasing temperature or adding more training data.")

            except json.JSONDecodeError:
                st.error("Invalid JSON in entity data")
            except Exception as e:
                st.error(f"Error: {e}")


# ============================================================================
# Tab 4: Training Data Management
# ============================================================================

with tab4:
    st.header("📚 Training Data Management")

    st.info("Add training entities with known outcomes for analogical reasoning.")

    # Add single entity
    st.subheader("➕ Add Training Entity")

    col1, col2 = st.columns(2)

    with col1:
        train_entity_id = st.text_input("Entity ID", key="train_id", placeholder="entity_001")

    with col2:
        train_outcome = st.selectbox(
            "Outcome",
            ["COMPLIANT", "NON_COMPLIANT", "PARTIALLY_COMPLIANT", "HIGH_RISK", "LOW_RISK"],
            key="train_outcome"
        )

    train_entity_json = st.text_area(
        "Entity Data (JSON)",
        key="train_data",
        height=100,
        placeholder='{"name": "Entity Name", "type": "Type"}'
    )

    if st.button("➕ Add Entity"):
        if train_entity_id and train_entity_json and service:
            try:
                entity_data = json.loads(train_entity_json)

                service.add_training_entity(
                    entity_id=train_entity_id,
                    entity_data=entity_data,
                    outcome=train_outcome
                )

                st.session_state.training_data.append({
                    'entity_id': train_entity_id,
                    'outcome': train_outcome,
                    'data': entity_data
                })

                st.success(f"✅ Added {train_entity_id} with outcome: {train_outcome}")

            except json.JSONDecodeError:
                st.error("Invalid JSON")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    # Show loaded entities
    st.subheader("📊 Loaded Training Entities")

    if service:
        entity_count = service.get_entity_count()
        st.metric("Total Entities", entity_count)

        if st.session_state.training_data:
            st.dataframe(
                [
                    {
                        'Entity ID': item['entity_id'],
                        'Outcome': item['outcome']
                    }
                    for item in st.session_state.training_data
                ],
                use_container_width=True
            )

    # Clear training data
    if st.button("🗑️ Clear All Training Data", type="secondary"):
        if service:
            service.clear_training_data()
            st.session_state.training_data = []
            st.success("✅ Training data cleared")
            st.rerun()


# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.caption(
    "🧠 **Tensor Logic Compliance QA** | "
    "Temperature-controlled reasoning for regulatory compliance | "
    f"Service: {service.__class__.__name__ if service else 'Not initialized'}"
)
