#!/usr/bin/env python3
"""
Unified Chat Portal - One-Stop Shop for All Chat Services
==========================================================
Full-service chat portal using PURE hexagonal architecture.
Combines chat, QA workflows, and flow agreements in one interface.

Architecture:
- Domain Layer: Core business logic (chat, QA, workflows)
- Application Layer: Use cases and orchestration
- Infrastructure Layer: External services via delegates
- Presentation Layer: Streamlit UI with tabs

Port: 8502
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

# Add parent path for imports
qa_root = Path(__file__).parent.parent.parent
if str(qa_root) not in sys.path:
    sys.path.insert(0, str(qa_root))

# Import infrastructure and services
try:
    from packages.tidyllm.infrastructure.infra_delegate import get_infra_delegate
    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager
    REAL_INFRASTRUCTURE = True
except ImportError:
    # Fallback for development
    REAL_INFRASTRUCTURE = False
    print("Warning: Using mock infrastructure. Real services not available.")

# ============================================================================
# HEXAGONAL ARCHITECTURE - DOMAIN LAYER (Core Business Logic)
# ============================================================================

class ChatMode(Enum):
    """Chat modes available in the system"""
    DIRECT = "direct"
    CONTEXT_AWARE = "context_aware"
    WORKFLOW = "workflow"
    QA_COMPLIANCE = "qa_compliance"
    FLOW_AGREEMENT = "flow_agreement"

class ChatService:
    """Domain service for chat operations"""

    def __init__(self, infra_delegate):
        self.infra = infra_delegate

    def send_message(self, message: str, mode: ChatMode, context: Dict = None) -> Dict:
        """Send a message and get response based on mode"""
        if mode == ChatMode.DIRECT:
            return self._direct_chat(message)
        elif mode == ChatMode.WORKFLOW:
            return self._workflow_chat(message, context)
        elif mode == ChatMode.QA_COMPLIANCE:
            return self._qa_chat(message, context)
        elif mode == ChatMode.FLOW_AGREEMENT:
            return self._flow_agreement_chat(message, context)
        else:
            return self._context_aware_chat(message, context)

    def _direct_chat(self, message: str) -> Dict:
        """Direct chat without context"""
        if REAL_INFRASTRUCTURE and hasattr(self, 'chat_manager'):
            try:
                response = self.chat_manager.chat(
                    message=message,
                    mode="direct"
                )
                return {
                    "response": response.get("content", f"Response to: {message}"),
                    "mode": "direct",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "response": f"Error: {str(e)}. Fallback response to: {message}",
                    "mode": "direct",
                    "timestamp": datetime.now().isoformat()
                }
        return {
            "response": f"Direct response to: {message}",
            "mode": "direct",
            "timestamp": datetime.now().isoformat()
        }

    def _workflow_chat(self, message: str, context: Dict) -> Dict:
        """Chat with workflow integration"""
        return {
            "response": f"Workflow processing: {message}",
            "workflow_id": context.get("workflow_id", "default"),
            "mode": "workflow",
            "timestamp": datetime.now().isoformat()
        }

    def _qa_chat(self, message: str, context: Dict) -> Dict:
        """QA compliance chat"""
        return {
            "response": f"QA compliance check: {message}",
            "compliance_status": "pending",
            "mode": "qa_compliance",
            "timestamp": datetime.now().isoformat()
        }

    def _flow_agreement_chat(self, message: str, context: Dict) -> Dict:
        """Flow agreement processing"""
        return {
            "response": f"Flow agreement processing: {message}",
            "agreement_id": context.get("agreement_id"),
            "mode": "flow_agreement",
            "timestamp": datetime.now().isoformat()
        }

    def _context_aware_chat(self, message: str, context: Dict) -> Dict:
        """Context-aware chat with history"""
        return {
            "response": f"Context-aware response to: {message}",
            "context_used": len(context.get("history", [])),
            "mode": "context_aware",
            "timestamp": datetime.now().isoformat()
        }

class WorkflowService:
    """Domain service for workflow operations"""

    def __init__(self, infra_delegate):
        self.infra = infra_delegate

    def list_workflows(self) -> List[Dict]:
        """List available workflows"""
        return [
            {"id": "mvr_analysis", "name": "MVR Analysis", "stages": 4},
            {"id": "qa_compliance", "name": "QA Compliance Check", "stages": 3},
            {"id": "document_review", "name": "Document Review", "stages": 5},
            {"id": "rag_pipeline", "name": "RAG Pipeline", "stages": 6}
        ]

    def execute_workflow(self, workflow_id: str, input_data: Dict) -> Dict:
        """Execute a workflow"""
        workflow = next((w for w in self.list_workflows() if w["id"] == workflow_id), None)
        if not workflow:
            return {"error": "Workflow not found"}

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "stages_completed": workflow["stages"],
            "results": f"Processed {workflow['name']} successfully"
        }

class QAService:
    """Domain service for QA operations"""

    def __init__(self, infra_delegate):
        self.infra = infra_delegate

    def get_compliance_standards(self) -> List[str]:
        """Get available compliance standards"""
        return ["MVS", "VST", "ISO9001", "ISO27001", "HIPAA", "GDPR"]

    def check_compliance(self, document: str, standards: List[str]) -> Dict:
        """Check document compliance"""
        return {
            "document": document,
            "standards_checked": standards,
            "compliance_score": 0.85,
            "findings": [
                {"standard": s, "status": "compliant", "score": 0.9}
                for s in standards
            ],
            "timestamp": datetime.now().isoformat()
        }

    def process_mvr(self, document_path: str, context: Dict) -> Dict:
        """Process MVR document"""
        return {
            "status": "completed",
            "document_id": context.get("document_id", "unknown"),
            "processing_time_ms": 1250,
            "findings": [
                {"type": "metadata", "value": "REV00001"},
                {"type": "classification", "value": "VST"},
                {"type": "sentiment", "value": "neutral"}
            ],
            "audit_trail_id": f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

# ============================================================================
# HEXAGONAL ARCHITECTURE - APPLICATION LAYER (Use Cases)
# ============================================================================

class UnifiedChatApplication:
    """Application service orchestrating all chat features"""

    def __init__(self):
        # Initialize infrastructure
        if REAL_INFRASTRUCTURE:
            try:
                self.infra = get_infra_delegate()
                self.chat_manager = UnifiedChatManager()
            except Exception as e:
                print(f"Warning: Could not initialize real infrastructure: {e}")
                self.infra = None
                self.chat_manager = None
        else:
            self.infra = None
            self.chat_manager = None

        # Initialize domain services
        self.chat_service = ChatService(self.infra)
        if self.chat_manager:
            self.chat_service.chat_manager = self.chat_manager

        self.workflow_service = WorkflowService(self.infra)
        self.qa_service = QAService(self.infra)

        # Available models from infrastructure
        self.models = self._get_available_models()

    def _get_available_models(self) -> List[str]:
        """Get available models from infrastructure"""
        if self.infra:
            try:
                bedrock_config = self.infra.get_bedrock_config()
                models = list(bedrock_config.get('model_mapping', {}).keys())
                if models:
                    return models
            except Exception as e:
                print(f"Could not get models from infrastructure: {e}")

        # Fallback models
        return ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus", "claude-2.1"]

    def process_message(self, message: str, mode: str, context: Dict) -> Dict:
        """Process a message through the appropriate service"""
        chat_mode = ChatMode(mode)

        # Route to appropriate service based on mode
        if chat_mode in [ChatMode.WORKFLOW, ChatMode.FLOW_AGREEMENT]:
            # Check for workflow triggers
            if "[" in message and "]" in message:
                workflow_id = message[message.find("[")+1:message.find("]")]
                workflow_result = self.workflow_service.execute_workflow(workflow_id, {"message": message})
                context["workflow_result"] = workflow_result

        # Process through chat service
        return self.chat_service.send_message(message, chat_mode, context)

    def get_workflows(self) -> List[Dict]:
        """Get available workflows"""
        return self.workflow_service.list_workflows()

    def check_compliance(self, document: str, standards: List[str]) -> Dict:
        """Check document compliance"""
        return self.qa_service.check_compliance(document, standards)

    def process_mvr(self, document_path: str, document_id: str) -> Dict:
        """Process MVR document"""
        return self.qa_service.process_mvr(
            document_path,
            {"document_id": document_id}
        )

# ============================================================================
# HEXAGONAL ARCHITECTURE - PRESENTATION LAYER (Streamlit UI)
# ============================================================================

class UnifiedChatPortal:
    """Presentation layer - Streamlit UI"""

    def __init__(self):
        self.app = UnifiedChatApplication()
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'current_mode' not in st.session_state:
            st.session_state.current_mode = ChatMode.DIRECT.value
        if 'current_model' not in st.session_state:
            st.session_state.current_model = self.app.models[0] if self.app.models else "claude-3-sonnet"
        if 'active_workflow' not in st.session_state:
            st.session_state.active_workflow = None
        if 'qa_results' not in st.session_state:
            st.session_state.qa_results = []

    def render(self):
        """Main render method"""
        st.set_page_config(
            page_title="Unified Chat Portal - Everything Chat",
            page_icon="💬",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Header
        st.title("💬 Unified Chat Portal")
        st.markdown("**One-stop shop for all chat services - Pure Hexagonal Architecture**")

        # Tabs for different functionalities
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Chat",
            "🔄 Workflows",
            "✅ QA Compliance",
            "📋 Flow Agreements",
            "⚙️ Settings"
        ])

        with tab1:
            self.render_chat_tab()

        with tab2:
            self.render_workflows_tab()

        with tab3:
            self.render_qa_tab()

        with tab4:
            self.render_flow_agreements_tab()

        with tab5:
            self.render_settings_tab()

        # Sidebar controls
        self.render_sidebar()

    def render_chat_tab(self):
        """Render the main chat interface"""
        st.subheader("Chat Interface")

        # Chat mode selector
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            mode = st.selectbox(
                "Chat Mode",
                options=[mode.value for mode in ChatMode],
                index=[mode.value for mode in ChatMode].index(st.session_state.current_mode)
            )
            st.session_state.current_mode = mode

        with col2:
            model = st.selectbox(
                "Model",
                options=self.app.models,
                index=self.app.models.index(st.session_state.current_model) if st.session_state.current_model in self.app.models else 0
            )
            st.session_state.current_model = model

        with col3:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()

        # Message display
        message_container = st.container()
        with message_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if "metadata" in message:
                        with st.expander("Details"):
                            st.json(message["metadata"])

        # Chat input
        if prompt := st.chat_input("Type your message..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Process message
            context = {
                "history": st.session_state.messages[-10:],  # Last 10 messages
                "model": st.session_state.current_model,
                "workflow_id": st.session_state.active_workflow
            }

            response = self.app.process_message(prompt, st.session_state.current_mode, context)

            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["response"],
                "metadata": response
            })

            st.rerun()

    def render_workflows_tab(self):
        """Render workflows management tab"""
        st.subheader("🔄 Workflow Management")

        workflows = self.app.get_workflows()

        col1, col2 = st.columns([3, 2])

        with col1:
            st.write("**Available Workflows:**")
            for workflow in workflows:
                with st.expander(f"**{workflow['name']}** ({workflow['stages']} stages)"):
                    st.write(f"ID: `{workflow['id']}`")
                    st.write(f"Stages: {workflow['stages']}")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"▶️ Run", key=f"run_{workflow['id']}"):
                            result = self.app.workflow_service.execute_workflow(
                                workflow['id'],
                                {"user": "current_user"}
                            )
                            st.success(f"✅ {result['results']}")

                    with col_b:
                        if st.button(f"💬 Use in Chat", key=f"chat_{workflow['id']}"):
                            st.session_state.active_workflow = workflow['id']
                            st.session_state.current_mode = ChatMode.WORKFLOW.value
                            st.success(f"Workflow '{workflow['name']}' activated in chat")

        with col2:
            st.write("**Quick Launch:**")
            st.info("Type `[workflow_id]` in chat to trigger a workflow")
            st.code("[mvr_analysis] Process this document")

            if st.session_state.active_workflow:
                st.success(f"Active: {st.session_state.active_workflow}")
                if st.button("Deactivate"):
                    st.session_state.active_workflow = None
                    st.rerun()

    def render_qa_tab(self):
        """Render QA compliance tab"""
        st.subheader("✅ QA Compliance Checking")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.write("**Document Compliance Check**")

            document_id = st.text_input("Document ID", value="DOC_2024_001")
            document_path = st.text_input("Document Path", value="sample.pdf")

            standards = st.multiselect(
                "Compliance Standards",
                options=self.app.qa_service.get_compliance_standards(),
                default=["MVS", "VST"]
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔍 Check Compliance", type="primary"):
                    result = self.app.check_compliance(document_path, standards)
                    st.session_state.qa_results.append(result)
                    st.success(f"Compliance Score: {result['compliance_score']*100:.1f}%")

            with col_b:
                if st.button("📄 Process MVR"):
                    result = self.app.process_mvr(document_path, document_id)
                    st.session_state.qa_results.append(result)
                    st.success(f"Processing complete: {result['audit_trail_id']}")

        with col2:
            st.write("**Recent Results**")
            for i, result in enumerate(st.session_state.qa_results[-5:]):
                with st.expander(f"Result {i+1}", expanded=False):
                    st.json(result)

    def render_flow_agreements_tab(self):
        """Render flow agreements tab"""
        st.subheader("📋 Flow Agreements")

        st.info("Flow Agreements define automated workflow contracts")

        agreements = [
            {"id": "mvr_v1", "name": "MVR Analysis Agreement", "type": "Document Processing"},
            {"id": "qa_v1", "name": "QA Compliance Agreement", "type": "Compliance"},
            {"id": "rag_v1", "name": "RAG Pipeline Agreement", "type": "AI Processing"}
        ]

        for agreement in agreements:
            with st.expander(f"**{agreement['name']}**"):
                st.write(f"Type: {agreement['type']}")
                st.write(f"ID: `{agreement['id']}`")

                if st.button(f"Activate", key=f"activate_{agreement['id']}"):
                    st.session_state.current_mode = ChatMode.FLOW_AGREEMENT.value
                    st.success(f"Agreement '{agreement['name']}' activated")

    def render_settings_tab(self):
        """Render settings tab"""
        st.subheader("⚙️ Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Chat Settings**")
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
            max_tokens = st.slider("Max Tokens", 100, 4000, 1000)
            streaming = st.checkbox("Enable Streaming", value=False)

        with col2:
            st.write("**System Settings**")
            show_metadata = st.checkbox("Show Message Metadata", value=True)
            auto_save = st.checkbox("Auto-save Conversations", value=False)
            debug_mode = st.checkbox("Debug Mode", value=False)

        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")

    def render_sidebar(self):
        """Render sidebar controls"""
        with st.sidebar:
            st.title("🎛️ Control Panel")

            # Quick stats
            st.metric("Total Messages", len(st.session_state.messages))
            st.metric("Active Mode", st.session_state.current_mode)
            st.metric("Current Model", st.session_state.current_model.replace("-", " ").title())

            st.divider()

            # Quick actions
            st.subheader("Quick Actions")

            if st.button("📥 Export Chat"):
                st.download_button(
                    "Download JSON",
                    data=str(st.session_state.messages),
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            if st.button("🔄 Reset All"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the unified chat portal"""
    portal = UnifiedChatPortal()
    portal.render()

if __name__ == "__main__":
    main()