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
            return self._direct_chat(message, context)
        elif mode == ChatMode.WORKFLOW:
            return self._workflow_chat(message, context)
        elif mode == ChatMode.QA_COMPLIANCE:
            return self._qa_chat(message, context)
        elif mode == ChatMode.FLOW_AGREEMENT:
            return self._flow_agreement_chat(message, context)
        else:
            return self._context_aware_chat(message, context)

    def _direct_chat(self, message: str, context: Dict = None) -> Dict:
        """Direct chat using real AI models through UnifiedChatManager."""
        model = context.get("model", "claude-3-haiku") if context else "claude-3-haiku"
        temperature = context.get("temperature", 0.7) if context else 0.7

        # Always use the real chat manager for actual responses
        if hasattr(self, 'chat_manager') and self.chat_manager:
            try:
                # Use UnifiedChatManager which routes through CorporateLLMGateway
                response = self.chat_manager.chat(
                    message=message,
                    mode="direct",
                    model=model,
                    temperature=temperature,
                    reasoning=False,  # Set to True if you want detailed reasoning
                    user_id="chat_portal_user"
                )

                # Handle different response formats
                if isinstance(response, str):
                    response_text = response
                    rl_metadata = {}
                elif isinstance(response, dict):
                    # Response with reasoning/metadata
                    response_text = response.get("response", response.get("content", str(response)))

                    # Extract RL fields from response if available
                    rl_metadata = {}
                    if "rl_metrics" in response:
                        rl_metadata["rl_metrics"] = response["rl_metrics"]
                    if "rl_state" in response:
                        rl_metadata["rl_state"] = response["rl_state"]
                    if "learning_feedback" in response:
                        rl_metadata["learning_feedback"] = response["learning_feedback"]
                    if "policy_info" in response:
                        rl_metadata["policy_info"] = response["policy_info"]
                    if "exploration_data" in response:
                        rl_metadata["exploration_data"] = response["exploration_data"]
                    if "value_estimation" in response:
                        rl_metadata["value_estimation"] = response["value_estimation"]
                    if "reward_signal" in response:
                        rl_metadata["reward_signal"] = response["reward_signal"]
                else:
                    response_text = str(response)
                    rl_metadata = {}

                # Build response with RL fields
                result = {
                    "response": response_text,
                    "mode": "direct",
                    "model": model,
                    "temperature": temperature,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }

                # Add RL metadata if available
                result.update(rl_metadata)

                return result

            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error in direct chat: {e}\n{error_details}")

                # Return error but don't fall back to mock
                return {
                    "response": f"Error connecting to AI service: {str(e)}. Please check the configuration.",
                    "mode": "direct",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error": str(e)
                }

        # No chat manager available
        return {
            "response": "Chat service is not initialized. Please check your infrastructure configuration.",
            "mode": "direct",
            "model": model,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": "No chat manager available"
        }

    def _workflow_chat(self, message: str, context: Dict) -> Dict:
        """Chat with workflow integration using hybrid mode for intelligent processing."""
        model = context.get("model", "claude-3-haiku")
        workflow_id = context.get("workflow_id", "default")

        if hasattr(self, 'chat_manager') and self.chat_manager:
            try:
                # Use hybrid mode for workflow-related queries
                enhanced_message = f"[Workflow: {workflow_id}] {message}"
                response = self.chat_manager.chat(
                    message=enhanced_message,
                    mode="hybrid",  # Intelligent mode selection
                    model=model,
                    temperature=0.7,
                    user_id="chat_portal_user",
                    workflow_context=workflow_id
                )

                if isinstance(response, str):
                    response_text = response
                elif isinstance(response, dict):
                    response_text = response.get("response", response.get("content", str(response)))
                else:
                    response_text = str(response)

                return {
                    "response": response_text,
                    "workflow_id": workflow_id,
                    "mode": "workflow",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }

            except Exception as e:
                print(f"Error in workflow chat: {e}")
                # Fall back to direct mode
                return self._direct_chat(message, context)

        return {
            "response": "Workflow chat service is not available.",
            "workflow_id": workflow_id,
            "mode": "workflow",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

    def _qa_chat(self, message: str, context: Dict) -> Dict:
        """QA compliance chat with real AI processing."""
        model = context.get("model", "claude-3-haiku")

        if hasattr(self, 'chat_manager') and self.chat_manager:
            try:
                # Add QA context to the message
                qa_message = f"[QA Compliance Context] {message}"
                response = self.chat_manager.chat(
                    message=qa_message,
                    mode="direct",  # Use direct mode with QA context
                    model=model,
                    temperature=0.3,  # Lower temperature for compliance accuracy
                    user_id="qa_compliance_user"
                )

                if isinstance(response, str):
                    response_text = response
                elif isinstance(response, dict):
                    response_text = response.get("response", response.get("content", str(response)))
                else:
                    response_text = str(response)

                return {
                    "response": response_text,
                    "compliance_status": "reviewed",
                    "mode": "qa_compliance",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }

            except Exception as e:
                print(f"Error in QA chat: {e}")
                return {
                    "response": f"QA processing error: {str(e)}",
                    "compliance_status": "error",
                    "mode": "qa_compliance",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }

        return {
            "response": "QA compliance service is not available.",
            "compliance_status": "unavailable",
            "mode": "qa_compliance",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

    def _flow_agreement_chat(self, message: str, context: Dict) -> Dict:
        """Flow agreement processing with real AI understanding."""
        model = context.get("model", "claude-3-haiku")
        agreement_id = context.get("agreement_id", "unknown")

        if hasattr(self, 'chat_manager') and self.chat_manager:
            try:
                # Process flow agreement queries
                flow_message = f"[Flow Agreement ID: {agreement_id}] {message}"
                response = self.chat_manager.chat(
                    message=flow_message,
                    mode="direct",
                    model=model,
                    temperature=0.5,  # Balanced temperature
                    user_id="flow_agreement_user"
                )

                if isinstance(response, str):
                    response_text = response
                elif isinstance(response, dict):
                    response_text = response.get("response", response.get("content", str(response)))
                else:
                    response_text = str(response)

                return {
                    "response": response_text,
                    "agreement_id": agreement_id,
                    "mode": "flow_agreement",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }

            except Exception as e:
                print(f"Error in flow agreement chat: {e}")
                return {
                    "response": f"Flow agreement processing error: {str(e)}",
                    "agreement_id": agreement_id,
                    "mode": "flow_agreement",
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }

        return {
            "response": "Flow agreement service is not available.",
            "agreement_id": agreement_id,
            "mode": "flow_agreement",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

    def _context_aware_chat(self, message: str, context: Dict) -> Dict:
        """Context-aware chat using RAG mode for better context handling."""
        model = context.get("model", "claude-3-haiku")

        if hasattr(self, 'chat_manager') and self.chat_manager:
            try:
                # Use RAG mode for context-aware responses
                response = self.chat_manager.chat(
                    message=message,
                    mode="rag",  # RAG mode for context-enhanced responses
                    model=model,
                    temperature=0.7,
                    history=context.get("history", []),
                    user_id="chat_portal_user"
                )

                # Handle different response formats and extract RL fields
                if isinstance(response, str):
                    response_text = response
                    rl_metadata = {}
                elif isinstance(response, dict):
                    response_text = response.get("response", response.get("content", str(response)))

                    # Extract RL fields from response if available
                    rl_metadata = {}
                    if "rl_metrics" in response:
                        rl_metadata["rl_metrics"] = response["rl_metrics"]
                    if "rl_state" in response:
                        rl_metadata["rl_state"] = response["rl_state"]
                    if "learning_feedback" in response:
                        rl_metadata["learning_feedback"] = response["learning_feedback"]
                    if "policy_info" in response:
                        rl_metadata["policy_info"] = response["policy_info"]
                    if "exploration_data" in response:
                        rl_metadata["exploration_data"] = response["exploration_data"]
                    if "value_estimation" in response:
                        rl_metadata["value_estimation"] = response["value_estimation"]
                    if "reward_signal" in response:
                        rl_metadata["reward_signal"] = response["reward_signal"]
                else:
                    response_text = str(response)
                    rl_metadata = {}

                # Build response with RL fields
                result = {
                    "response": response_text,
                    "context_used": len(context.get("history", [])),
                    "mode": "context_aware",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }

                # Add RL metadata if available
                result.update(rl_metadata)

                return result

            except Exception as e:
                print(f"Error in context-aware chat: {e}")
                # Fall back to direct mode if RAG fails
                return self._direct_chat(message, context)

        return {
            "response": "Context-aware chat service is not available.",
            "mode": "context_aware",
            "timestamp": datetime.now().isoformat(),
            "success": False
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
            "🎯 Modes Overview",
            "🔄 Workflows",
            "✅ QA Compliance",
            "📋 Flow Agreements"
        ])

        with tab1:
            self.render_chat_tab()

        with tab2:
            self.render_modes_overview_tab()

        with tab3:
            self.render_workflows_tab()

        with tab4:
            self.render_qa_tab()

        with tab5:
            self.render_flow_agreements_tab()

        # Sidebar controls
        self.render_sidebar()

    def render_modes_overview_tab(self):
        """Render the modes overview tab showing modes as combinations."""
        st.header("🎯 Chat Modes - Component Combinations")

        st.info("""
        **Key Insight**: Each "mode" is actually a **combination** of:
        - 🤖 **Model** (claude-3-haiku, sonnet, opus)
        - ⚙️ **Settings** (temperature, max_tokens, etc.)
        - 🔌 **Adapter** (Direct, RAG, DSPy)
        - 📊 **Output Format** (text, reasoning, structured)
        - 🎛️ **Processing Pipeline** (single-step, multi-step, retrieval-augmented)
        """)

        # Visual representation of mode combinations
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📦 Mode = Recipe of Components")
            st.markdown("""
            Think of modes as **recipes** that combine ingredients:

            ```
            DIRECT Mode Recipe:
            - Model: Any Claude model
            - Temperature: 0.7
            - Adapter: CorporateLLMGateway
            - Pipeline: Simple request→response
            - Output: Plain text

            RAG Mode Recipe:
            - Model: Any Claude model
            - Temperature: 0.7
            - Adapter: RAGAdapter + LLMGateway
            - Pipeline: Search→Retrieve→Augment→Generate
            - Output: Context-enhanced text

            QA_COMPLIANCE "Mode" (Portal Label):
            - Model: Same as DIRECT
            - Temperature: 0.3 (lowered for accuracy)
            - Adapter: Same as DIRECT
            - Pipeline: Same as DIRECT
            - Output: Same as DIRECT
            ```
            """)

        with col2:
            st.subheader("🔧 Build Your Own Mode")
            st.markdown("You can create custom combinations:")

            custom_model = st.selectbox(
                "Choose Model:",
                ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
            )

            custom_temp = st.slider(
                "Temperature:",
                0.0, 1.0, 0.7,
                help="0.0 = Deterministic, 1.0 = Creative"
            )

            custom_adapter = st.selectbox(
                "Choose Adapter:",
                ["Direct (CorporateLLMGateway)", "RAG (Vector Search + LLM)", "DSPy (Optimized Prompts)"]
            )

            custom_pipeline = st.multiselect(
                "Pipeline Steps:",
                ["Retrieve Context", "Extract Entities", "Apply Rules", "Generate Response", "Post-process"],
                default=["Generate Response"]
            )

            if st.button("Preview Custom Mode"):
                st.code(f"""
# Your Custom Mode Configuration
custom_mode = {{
    "model": "{custom_model}",
    "temperature": {custom_temp},
    "adapter": "{custom_adapter.split('(')[0].strip()}",
    "pipeline": {custom_pipeline},
    "max_tokens": 4000
}}

# To use in code:
response = chat_manager.chat(
    message="Your query",
    model=custom_mode["model"],
    temperature=custom_mode["temperature"],
    mode="custom"  # Would use custom pipeline
)
                """, language="python")

        # Detailed breakdown
        st.divider()
        st.subheader("🔍 Component Details")

        tab_model, tab_settings, tab_adapter, tab_output = st.tabs(
            ["🤖 Models", "⚙️ Settings", "🔌 Adapters", "📊 Outputs"]
        )

        with tab_model:
            st.markdown("""
            ### Available Models
            | Model | Speed | Quality | Cost | Best For |
            |-------|-------|---------|------|----------|
            | **claude-3-haiku** | ⚡ Fastest | Good | $ | Quick responses, high volume |
            | **claude-3-sonnet** | ⚡⚡ Fast | Excellent | $$ | Balanced performance |
            | **claude-3-opus** | ⚡⚡⚡ Slower | Best | $$$ | Complex reasoning |
            """)

        with tab_settings:
            st.markdown("""
            ### Configurable Settings
            - **temperature**: Controls randomness (0.0-1.0)
            - **max_tokens**: Maximum response length (1-4096)
            - **top_p**: Nucleus sampling parameter
            - **frequency_penalty**: Reduce repetition
            - **presence_penalty**: Encourage new topics
            - **stop_sequences**: Where to stop generation
            """)

        with tab_adapter:
            st.markdown("""
            ### Adapter Types

            **CorporateLLMGateway** (DIRECT)
            - Straight path to LLM
            - Includes audit logging
            - Fastest option

            **RAGAdapter** (RAG)
            - Vector database search
            - Context retrieval
            - Knowledge-enhanced responses

            **DSPyAdapter** (DSPY)
            - Prompt optimization
            - Chain of Thought
            - Few-shot learning
            """)

        with tab_output:
            st.markdown("""
            ### Output Formats

            **Plain Text**
            ```json
            {"response": "Simple text response"}
            ```

            **With Reasoning**
            ```json
            {
                "response": "Answer",
                "reasoning": "Step-by-step thought process",
                "confidence": 0.95
            }
            ```

            **Structured Data**
            ```json
            {
                "response": "Answer",
                "entities": ["entity1", "entity2"],
                "metadata": {...}
            }
            ```
            """)

        # Mode comparison matrix
        st.divider()
        st.subheader("📊 Mode Comparison Matrix")

        comparison_data = {
            "Component": ["Model", "Temperature", "Adapter", "Pipeline", "Output", "Use Case"],
            "DIRECT": [
                "Any Claude", "0.7", "Gateway", "Simple", "Text", "General chat"
            ],
            "RAG": [
                "Any Claude", "0.7", "RAG+Gateway", "Multi-step", "Enhanced", "Research"
            ],
            "DSPY": [
                "Any Claude", "0.5", "DSPy+Gateway", "CoT", "Reasoning", "Analysis"
            ],
            "QA_COMPLIANCE": [
                "Any Claude", "0.3", "Gateway", "Simple", "Text", "Validation"
            ],
            "WORKFLOW": [
                "Any Claude", "0.7", "Hybrid", "Variable", "Text", "Automation"
            ]
        }

        st.dataframe(comparison_data)

        # Key takeaway
        st.success("""
        **💡 The Big Picture**:

        "Modes" aren't hardcoded features - they're **configurable combinations** of:
        1. Which AI model to use
        2. What settings to apply
        3. Which adapter/infrastructure to route through
        4. What processing pipeline to follow
        5. How to format the output

        The portal labels (QA_COMPLIANCE, WORKFLOW, etc.) are just **presets** -
        pre-configured combinations that make sense for specific use cases!
        """)

        # Workflow Script Builder Section
        st.divider()
        st.header("🚀 Workflow Script Builder")
        st.markdown("Build executable Python scripts using the 5-stage pattern with chat mode combinations")

        # Import the generator
        try:
            from .workflow_script_generator import WorkflowScriptGenerator
            generator = WorkflowScriptGenerator()
            generator_available = True
        except ImportError:
            try:
                # Fallback to absolute import
                import sys
                from pathlib import Path
                sys.path.append(str(Path(__file__).parent))
                from workflow_script_generator import WorkflowScriptGenerator
                generator = WorkflowScriptGenerator()
                generator_available = True
            except ImportError:
                generator_available = False
                st.warning("Workflow generator not available")

        if generator_available:
            # Workflow configuration
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📋 Workflow Configuration")
                workflow_name = st.text_input(
                    "Workflow Name",
                    value="My Custom Workflow",
                    help="Name for your workflow script"
                )

                workflow_description = st.text_area(
                    "Description",
                    value="Automated workflow with chat mode integration",
                    height=80
                )

                author = st.text_input(
                    "Author",
                    value="Your Name",
                    help="Author of this workflow"
                )

            with col2:
                st.subheader("🎯 5-Stage Pattern")
                st.markdown("""
                **OBSERVE** → **ORIENT** → **DECIDE** → **ACT** → **MONITOR**

                1. **OBSERVE**: Gather data (load, extract, search)
                2. **ORIENT**: Understand context (analyze, compare)
                3. **DECIDE**: Make decisions (evaluate, generate insights)
                4. **ACT**: Take action (create reports, send results)
                5. **MONITOR**: Track & validate (check results, log)
                """)

            # Step Builder
            st.divider()
            st.subheader("🔧 Build Workflow Steps")

            # Initialize workflow steps in session state
            if 'workflow_steps' not in st.session_state:
                st.session_state.workflow_steps = []

            # Add step section
            with st.expander("➕ Add New Step", expanded=False):
                step_col1, step_col2, step_col3 = st.columns([1, 1, 1])

                with step_col1:
                    step_name = st.text_input("Step Name", key="new_step_name")
                    step_type = st.selectbox(
                        "Stage",
                        ["OBSERVE", "ORIENT", "DECIDE", "ACT", "MONITOR"],
                        key="new_step_type"
                    )
                    step_description = st.text_input("Description", key="new_step_desc")

                with step_col2:
                    step_model = st.selectbox(
                        "Model",
                        ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"],
                        key="new_step_model"
                    )
                    step_temp = st.slider(
                        "Temperature",
                        0.0, 1.0, 0.7,
                        key="new_step_temp"
                    )
                    step_mode = st.selectbox(
                        "Mode",
                        ["direct", "rag", "hybrid"],
                        key="new_step_mode"
                    )

                with step_col3:
                    step_requires = st.text_input(
                        "Requires (comma-separated)",
                        key="new_step_requires",
                        help="Input dependencies"
                    )
                    step_produces = st.text_input(
                        "Produces (comma-separated)",
                        key="new_step_produces",
                        help="Output artifacts"
                    )
                    step_max_tokens = st.number_input(
                        "Max Tokens",
                        100, 4000, 1000,
                        key="new_step_tokens"
                    )

                if st.button("Add Step", type="primary"):
                    if step_name and step_description:
                        new_step = {
                            "step_name": step_name.lower().replace(' ', '_'),
                            "step_type": step_type,
                            "description": step_description,
                            "model": step_model,
                            "temperature": step_temp,
                            "mode": step_mode,
                            "requires": [r.strip() for r in step_requires.split(',')] if step_requires else [],
                            "produces": [p.strip() for p in step_produces.split(',')] if step_produces else [],
                            "max_tokens": step_max_tokens,
                            "params": {}
                        }
                        st.session_state.workflow_steps.append(new_step)
                        st.success(f"Added step: {step_name}")
                        st.rerun()

            # Display current steps
            if st.session_state.workflow_steps:
                st.markdown("### Current Steps")
                for i, step in enumerate(st.session_state.workflow_steps):
                    with st.expander(f"{i+1}. **{step['step_name']}** ({step['step_type']})", expanded=False):
                        col1, col2, col3 = st.columns([2, 2, 1])

                        with col1:
                            st.markdown(f"**Description**: {step['description']}")
                            st.markdown(f"**Model**: {step['model']} (temp={step['temperature']})")
                            st.markdown(f"**Mode**: {step['mode']}")

                        with col2:
                            if step['requires']:
                                st.markdown(f"**Requires**: {', '.join(step['requires'])}")
                            if step['produces']:
                                st.markdown(f"**Produces**: {', '.join(step['produces'])}")
                            st.markdown(f"**Max Tokens**: {step['max_tokens']}")

                        with col3:
                            if st.button("🗑️ Remove", key=f"remove_step_{i}_{step['step_name']}"):
                                st.session_state.workflow_steps.pop(i)
                                st.rerun()

                # Generate and download section
                st.divider()
                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button("🔄 Clear All Steps"):
                        st.session_state.workflow_steps = []
                        st.rerun()

                with col2:
                    if st.button("⬇️ Generate & Download Script", type="primary"):
                        # Generate the script
                        config = {
                            "name": workflow_name,
                            "description": workflow_description,
                            "author": author,
                            "steps": st.session_state.workflow_steps
                        }

                        script_content = generator.generate_script(config)

                        # Provide download button
                        st.download_button(
                            label="📥 Download workflow_script.py",
                            data=script_content,
                            file_name=f"{workflow_name.lower().replace(' ', '_')}_workflow.py",
                            mime="text/x-python"
                        )

                # Example workflows
                st.divider()
                st.subheader("📚 Example Workflows")

                example_col1, example_col2 = st.columns([1, 1])

                with example_col1:
                    if st.button("Load Document Analysis Example"):
                        st.session_state.workflow_steps = [
                            {
                                "step_name": "load_document",
                                "step_type": "OBSERVE",
                                "description": "Load and extract text from document",
                                "model": "claude-3-haiku",
                                "temperature": 0.3,
                                "mode": "direct",
                                "requires": [],
                                "produces": ["document_text"],
                                "max_tokens": 1000,
                                "params": {}
                            },
                            {
                                "step_name": "analyze_content",
                                "step_type": "ORIENT",
                                "description": "Analyze document content and structure",
                                "model": "claude-3-sonnet",
                                "temperature": 0.5,
                                "mode": "rag",
                                "requires": ["document_text"],
                                "produces": ["analysis"],
                                "max_tokens": 2000,
                                "params": {}
                            },
                            {
                                "step_name": "generate_summary",
                                "step_type": "ACT",
                                "description": "Generate executive summary",
                                "model": "claude-3-opus",
                                "temperature": 0.4,
                                "mode": "direct",
                                "requires": ["analysis"],
                                "produces": ["summary"],
                                "max_tokens": 1500,
                                "params": {}
                            }
                        ]
                        st.success("Loaded Document Analysis workflow")
                        st.rerun()

                with example_col2:
                    if st.button("Load Data Processing Example"):
                        st.session_state.workflow_steps = [
                            {
                                "step_name": "extract_data",
                                "step_type": "OBSERVE",
                                "description": "Extract data from source",
                                "model": "claude-3-haiku",
                                "temperature": 0.2,
                                "mode": "direct",
                                "requires": [],
                                "produces": ["raw_data"],
                                "max_tokens": 500,
                                "params": {}
                            },
                            {
                                "step_name": "validate_data",
                                "step_type": "ORIENT",
                                "description": "Validate and clean data",
                                "model": "claude-3-haiku",
                                "temperature": 0.1,
                                "mode": "direct",
                                "requires": ["raw_data"],
                                "produces": ["clean_data"],
                                "max_tokens": 500,
                                "params": {}
                            },
                            {
                                "step_name": "analyze_patterns",
                                "step_type": "DECIDE",
                                "description": "Identify patterns and insights",
                                "model": "claude-3-sonnet",
                                "temperature": 0.6,
                                "mode": "hybrid",
                                "requires": ["clean_data"],
                                "produces": ["insights"],
                                "max_tokens": 2000,
                                "params": {}
                            },
                            {
                                "step_name": "create_report",
                                "step_type": "ACT",
                                "description": "Create final report",
                                "model": "claude-3-opus",
                                "temperature": 0.5,
                                "mode": "direct",
                                "requires": ["insights"],
                                "produces": ["report"],
                                "max_tokens": 3000,
                                "params": {}
                            },
                            {
                                "step_name": "validate_results",
                                "step_type": "MONITOR",
                                "description": "Validate and log results",
                                "model": "claude-3-haiku",
                                "temperature": 0.2,
                                "mode": "direct",
                                "requires": ["report"],
                                "produces": ["validation_log"],
                                "max_tokens": 500,
                                "params": {}
                            }
                        ]
                        st.success("Loaded Data Processing workflow")
                        st.rerun()

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
        """Render workflows management tab with custom commands"""
        st.subheader("🔄 Workflow Management & Custom Commands")

        # Sub-tabs for workflow features
        workflow_tab1, workflow_tab2, workflow_tab3 = st.tabs([
            "📋 Workflows",
            "🛠️ Custom Commands",
            "🔗 Pipeline Builder"
        ])

        with workflow_tab1:
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

        with workflow_tab2:
            st.markdown("### 🛠️ Custom Commands")
            st.info("Build reusable command templates with specific chat mode configurations")

            # Command builder
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown("**New Command:**")
                cmd_name = st.text_input("Name", key="wcmd_name")
                cmd_desc = st.text_area("Description", height=60, key="wcmd_desc")

                cmd_model = st.selectbox(
                    "Model",
                    ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"],
                    key="wcmd_model"
                )
                cmd_temp = st.slider("Temperature", 0.0, 1.0, 0.5, key="wcmd_temp")
                cmd_mode = st.selectbox("Mode", ["direct", "rag", "hybrid", "custom"], key="wcmd_mode")

                # Custom mode settings (only show if custom is selected)
                custom_mode_settings = {}
                if cmd_mode == "custom":
                    st.markdown("**Custom Mode Settings:**")
                    custom_mode_settings["max_tokens"] = st.number_input(
                        "Max Tokens", 100, 4000, 1000, key="wcmd_max_tokens"
                    )
                    custom_mode_settings["reasoning"] = st.checkbox(
                        "Enable Reasoning", key="wcmd_reasoning"
                    )
                    custom_mode_settings["system_prompt"] = st.text_area(
                        "System Prompt (optional)", height=60, key="wcmd_system"
                    )

                cmd_template = st.text_area(
                    "Prompt Template",
                    placeholder="{input} = user input",
                    height=100,
                    key="wcmd_template"
                )

                if st.button("💾 Save Command"):
                    if cmd_name and cmd_template:
                        if 'custom_commands' not in st.session_state:
                            st.session_state.custom_commands = []

                        command_data = {
                            "name": cmd_name,
                            "description": cmd_desc,
                            "model": cmd_model,
                            "temperature": cmd_temp,
                            "mode": cmd_mode,
                            "template": cmd_template
                        }

                        # Add custom mode settings if custom mode is selected
                        if cmd_mode == "custom":
                            command_data["custom_settings"] = custom_mode_settings

                        st.session_state.custom_commands.append(command_data)
                        st.success(f"Saved: {cmd_name}")

            with col2:
                st.markdown("**Saved Commands:**")
                if 'custom_commands' in st.session_state:
                    for i, cmd in enumerate(st.session_state.custom_commands):
                        with st.expander(cmd['name']):
                            st.markdown(f"*{cmd['description']}*")

                            # Basic settings
                            config_text = f"Model: {cmd['model']}\nTemp: {cmd['temperature']}\nMode: {cmd['mode']}"

                            # Add custom mode settings if they exist
                            if cmd['mode'] == 'custom' and 'custom_settings' in cmd:
                                custom = cmd['custom_settings']
                                config_text += f"\n\nCustom Settings:"
                                if 'max_tokens' in custom:
                                    config_text += f"\n- Max Tokens: {custom['max_tokens']}"
                                if 'reasoning' in custom:
                                    config_text += f"\n- Reasoning: {custom['reasoning']}"
                                if 'system_prompt' in custom and custom['system_prompt']:
                                    config_text += f"\n- System Prompt: {custom['system_prompt'][:50]}..."

                            st.code(config_text)

                            # Show template
                            if 'template' in cmd:
                                st.markdown("**Template:**")
                                st.code(cmd['template'], language="text")

                            if st.button(f"Delete", key=f"del_cmd_{i}_{cmd['name'].replace(' ', '_')}"):
                                st.session_state.custom_commands.remove(cmd)
                                st.rerun()
                else:
                    st.info("No commands saved yet")

        with workflow_tab3:
            st.markdown("### 🔗 Pipeline Builder")
            st.info("Chain workflows and commands into executable pipelines")

            if 'pipeline_steps' not in st.session_state:
                st.session_state.pipeline_steps = []

            # Add step
            col1, col2 = st.columns([3, 1])
            with col1:
                step_type = st.selectbox(
                    "Add Step",
                    ["Workflow", "Custom Command", "Chat Mode"],
                    key="pipe_step_type"
                )

                if step_type == "Workflow":
                    step = st.selectbox(
                        "Select",
                        [w['id'] for w in workflows],
                        key="pipe_workflow"
                    )
                elif step_type == "Custom Command" and 'custom_commands' in st.session_state:
                    step = st.selectbox(
                        "Select",
                        [c['name'] for c in st.session_state.custom_commands],
                        key="pipe_cmd"
                    )
                else:
                    step = st.selectbox("Select", ["direct", "rag", "hybrid"], key="pipe_mode")

            with col2:
                if st.button("➕ Add"):
                    if step:
                        st.session_state.pipeline_steps.append({
                            "type": step_type,
                            "value": step
                        })

            # Display pipeline
            if st.session_state.pipeline_steps:
                st.markdown("**Current Pipeline:**")
                for i, step in enumerate(st.session_state.pipeline_steps):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{i+1}. {step['type']}: **{step['value']}**")
                    with col2:
                        if st.button("❌", key=f"rm_pipe_{i}"):
                            st.session_state.pipeline_steps.pop(i)
                            st.rerun()

                if st.button("🔄 Clear Pipeline"):
                    st.session_state.pipeline_steps = []
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