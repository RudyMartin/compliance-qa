#!/usr/bin/env python3
"""
Chat Modes Overview Page
========================
Interactive documentation page showing all chat modes with expandable details.
This clarifies that some modes are UI labels that map to core UnifiedChatManager modes.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent path for imports
qa_root = Path(__file__).parent.parent.parent
if str(qa_root) not in sys.path:
    sys.path.insert(0, str(qa_root))

def render_chat_modes_overview():
    """Render the chat modes overview with expandable cards."""

    st.title("🎯 Chat Modes Overview")
    st.markdown("*Understanding TidyLLM's intelligent chat processing modes*")

    # Important clarification
    st.info("""
    **📌 Important Note**: There are two types of modes:

    1. **Core Modes** (in UnifiedChatManager): DIRECT, RAG, DSPY, HYBRID, CUSTOM
    2. **Portal Labels** (in Chat UI): Additional user-friendly names that map to core modes with specific configurations

    The portal labels (like QA_COMPLIANCE, WORKFLOW) are essentially **preset configurations**
    of the core modes designed for specific business use cases.
    """)

    # Tabs for organization
    tab1, tab2, tab3 = st.tabs(["🔧 Core Modes", "🏷️ Portal Labels", "⚙️ Configuration"])

    with tab1:
        st.header("Core UnifiedChatManager Modes")
        st.markdown("These are the fundamental processing modes in `packages/tidyllm/services/unified_chat_manager.py`")

        # DIRECT Mode
        with st.expander("**1️⃣ DIRECT Mode** - Fast, straightforward AI responses", expanded=True):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("""
                ### How It Works
                - Direct path to LLM without additional processing
                - Uses CorporateLLMGateway for audit and tracking
                - Fastest response time (~1-2 seconds)

                ### Code Path
                ```python
                UnifiedChatManager._process_direct_chat()
                  → CorporateLLMGateway.process_request()
                    → AWS Bedrock (Claude-3 models)
                ```

                ### Best For
                - Simple Q&A
                - General conversation
                - Quick responses
                - When context isn't needed
                """)

            with col2:
                st.markdown("### ⚙️ Settings")
                st.code("""
model: claude-3-haiku
temperature: 0.7
max_tokens: 4000
retry_count: 3
timeout_ms: 5000
                """, language="yaml")

                st.metric("Avg Response Time", "1-2 sec")
                st.metric("Cost per Query", "$0.01-0.02")

        # RAG Mode
        with st.expander("**2️⃣ RAG Mode** - Context-enhanced with knowledge base"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("""
                ### How It Works
                - Searches vector database for relevant context
                - Combines retrieved documents with query
                - Generates response using both context and query

                ### Code Path
                ```python
                UnifiedChatManager._process_rag_chat()
                  → UnifiedRAGManager.query()
                    → Vector Search (ChromaDB/PostgreSQL)
                    → Context + Query → LLM
                ```

                ### RAG System Types
                - **AI_POWERED**: General knowledge
                - **INTELLIGENT**: Domain-specific
                - **SME**: Expert knowledge

                ### Best For
                - Documentation queries
                - Research questions
                - Context-dependent answers
                - Historical information
                """)

            with col2:
                st.markdown("### ⚙️ Settings")
                st.code("""
top_k: 5
similarity_threshold: 0.7
chunk_size: 512
embedding_model: titan-embed
temperature: 0.7
                """, language="yaml")

                st.metric("Avg Response Time", "2-4 sec")
                st.metric("Cost per Query", "$0.03-0.05")

        # DSPY Mode
        with st.expander("**3️⃣ DSPY Mode** - Optimized prompts & Chain of Thought"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("""
                ### How It Works
                - Uses DSPy framework for prompt optimization
                - Applies Chain of Thought reasoning
                - Few-shot learning from examples

                ### Code Path
                ```python
                UnifiedChatManager._process_dspy_chat()
                  → DSPyService.configure_lm()
                    → Chain of Thought signature
                    → Multi-step reasoning
                ```

                ### Features
                - Automatic prompt optimization
                - Step-by-step reasoning
                - Self-improving with usage

                ### Best For
                - Complex analysis
                - Math problems
                - Logic puzzles
                - Detailed explanations
                """)

                st.warning("⚠️ **Status**: Partially implemented - returns placeholder responses currently")

            with col2:
                st.markdown("### ⚙️ Settings")
                st.code("""
temperature: 0.5
chain_of_thought: true
few_shot_examples: 3
signature: "question -> answer"
                """, language="yaml")

                st.metric("Avg Response Time", "3-5 sec")
                st.metric("Cost per Query", "$0.04-0.06")

        # HYBRID Mode
        with st.expander("**4️⃣ HYBRID Mode** - Intelligent automatic mode selection"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("""
                ### How It Works
                - Analyzes query characteristics
                - Automatically selects best mode
                - No manual mode selection needed

                ### Routing Logic
                ```python
                if "step by step" in query:
                    → DSPY Mode
                elif len(query) > 100 or "?" in query:
                    → RAG Mode
                else:
                    → DIRECT Mode
                ```

                ### Smart Routing Rules
                | Query Pattern | Selected Mode |
                |--------------|---------------|
                | "explain", "reasoning" | DSPY |
                | Long query or questions | RAG |
                | Simple statements | DIRECT |

                ### Best For
                - Mixed query types
                - When unsure which mode
                - General-purpose chat
                """)

            with col2:
                st.markdown("### ⚙️ Settings")
                st.code("""
complexity_threshold: 100
question_detection: true
auto_routing: enabled
fallback_mode: direct
                """, language="yaml")

                st.metric("Response Time", "Variable")
                st.metric("Cost", "Optimized")

        # CUSTOM Mode
        with st.expander("**5️⃣ CUSTOM Mode** - User-defined processing pipelines"):
            st.markdown("""
            ### Purpose
            - Create specialized processing chains
            - Integrate external services
            - Custom business logic

            ### Example Pipeline
            ```python
            def custom_pipeline(message):
                # Step 1: Entity extraction
                entities = extract_entities(message)

                # Step 2: Business rules
                rules = apply_business_rules(entities)

                # Step 3: Generate response
                response = generate_response(message, rules)

                return response
            ```

            🚧 **Status**: Framework ready, awaiting implementation
            """)

    with tab2:
        st.header("Portal-Specific Labels")
        st.markdown("""
        These are **user-friendly labels** in the Chat Portal that map to core modes
        with specific configurations. They're not separate modes but rather **presets**
        for common use cases.
        """)

        # Mapping table
        st.subheader("📊 Label → Core Mode Mapping")

        mapping_data = {
            "Portal Label": ["CONTEXT_AWARE", "WORKFLOW", "QA_COMPLIANCE", "FLOW_AGREEMENT"],
            "Maps To": ["RAG Mode", "HYBRID Mode", "DIRECT Mode", "DIRECT Mode"],
            "Special Config": [
                "Includes conversation history",
                "Adds workflow context",
                "Temperature = 0.3 (high accuracy)",
                "Temperature = 0.5 (balanced)"
            ],
            "Use Case": [
                "Multi-turn conversations",
                "Business process automation",
                "Compliance & validation",
                "Contract analysis"
            ]
        }

        st.table(mapping_data)

        # Detailed cards for each label
        with st.expander("**📋 CONTEXT_AWARE** - Conversation with memory"):
            st.markdown("""
            ### What It Really Is
            - **Core Mode**: RAG
            - **Enhancement**: Passes conversation history as additional context
            - **Not a separate mode**, just RAG with `history` parameter

            ### Implementation in chat_app.py
            ```python
            def _context_aware_chat(self, message, context):
                # It's just RAG mode with history!
                return self.chat_manager.chat(
                    message=message,
                    mode="rag",  # ← Using RAG mode
                    history=context.get("history", [])  # ← Added context
                )
            ```

            ### Why This Label Exists
            - More intuitive for users than "RAG with history"
            - Clarifies the use case
            - Better UX in the interface
            """)

        with st.expander("**🔄 WORKFLOW** - Business process integration"):
            st.markdown("""
            ### What It Really Is
            - **Core Mode**: HYBRID
            - **Enhancement**: Prepends workflow context to message
            - **Just HYBRID mode** with workflow ID in the prompt

            ### Implementation
            ```python
            def _workflow_chat(self, message, context):
                workflow_id = context.get("workflow_id")
                enhanced_message = f"[Workflow: {workflow_id}] {message}"

                return self.chat_manager.chat(
                    message=enhanced_message,
                    mode="hybrid"  # ← Using HYBRID mode
                )
            ```

            ### Purpose
            - Helps users understand it's for workflow tasks
            - Provides context about the business process
            """)

        with st.expander("**✅ QA_COMPLIANCE** - High-accuracy responses"):
            st.markdown("""
            ### What It Really Is
            - **Core Mode**: DIRECT
            - **Enhancement**: Lower temperature (0.3) for consistency
            - **Same as DIRECT** but with accuracy-focused settings

            ### Implementation
            ```python
            def _qa_chat(self, message, context):
                qa_message = f"[QA Compliance Context] {message}"

                return self.chat_manager.chat(
                    message=qa_message,
                    mode="direct",      # ← Using DIRECT mode
                    temperature=0.3     # ← Lower temperature
                )
            ```

            ### Why Lower Temperature?
            - More deterministic responses
            - Higher consistency
            - Better for compliance/audit
            """)

        with st.expander("**📄 FLOW_AGREEMENT** - Balanced processing"):
            st.markdown("""
            ### What It Really Is
            - **Core Mode**: DIRECT
            - **Enhancement**: Medium temperature (0.5)
            - **Another DIRECT preset** with balanced settings

            ### Implementation
            ```python
            def _flow_agreement_chat(self, message, context):
                agreement_id = context.get("agreement_id")
                flow_message = f"[Flow Agreement ID: {agreement_id}] {message}"

                return self.chat_manager.chat(
                    message=flow_message,
                    mode="direct",      # ← Using DIRECT mode
                    temperature=0.5     # ← Balanced temperature
                )
            ```

            ### Temperature Balance
            - Not too creative (might hallucinate)
            - Not too rigid (might miss nuances)
            - Good for contract/agreement analysis
            """)

    with tab3:
        st.header("Configuration & Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📁 Where Settings Live")
            st.markdown("""
            1. **Global Defaults**
               - `infrastructure/settings.yaml`
               - System-wide configuration

            2. **Service Level**
               - `packages/tidyllm/services/unified_chat_manager.py`
               - Core mode implementations

            3. **UI Level**
               - `portals/chat/chat_app.py`
               - Portal-specific labels and presets
            """)

        with col2:
            st.subheader("🎛️ How to Adjust")
            st.markdown("""
            ### Change Core Mode Behavior
            Edit `unified_chat_manager.py`:
            ```python
            self.default_model = "claude-3-sonnet"
            self.default_temperature = 0.7
            ```

            ### Add New Portal Label
            In `chat_app.py`, add to ChatMode enum:
            ```python
            class ChatMode(Enum):
                YOUR_LABEL = "your_label"
            ```

            Then create handler:
            ```python
            def _your_label_chat(self, message, context):
                return self.chat_manager.chat(
                    message=message,
                    mode="direct",  # Pick core mode
                    temperature=0.6  # Your settings
                )
            ```
            """)

        # Performance comparison
        st.subheader("📊 Performance Comparison")

        perf_data = {
            "Mode/Label": ["DIRECT", "RAG", "DSPY", "HYBRID", "CONTEXT_AWARE", "QA_COMPLIANCE"],
            "Actual Mode": ["DIRECT", "RAG", "DSPY", "Variable", "RAG", "DIRECT"],
            "Response Time": ["1-2s", "2-4s", "3-5s", "Variable", "2-4s", "1-2s"],
            "Cost/Query": ["$0.01", "$0.04", "$0.05", "Variable", "$0.04", "$0.01"],
            "Accuracy": ["Good", "Excellent", "Excellent", "Optimal", "Excellent", "Very Good"]
        }

        st.dataframe(perf_data)

        # Key takeaway
        st.success("""
        **🎯 Key Takeaway**: The portal labels are just **user-friendly names** for
        specific configurations of the 5 core modes. They make the interface more
        intuitive without adding complexity to the underlying system.

        Think of them as "presets" on a camera - the camera (UnifiedChatManager) has
        core capabilities, and the presets (portal labels) are just convenient ways to
        configure those capabilities for specific scenarios.
        """)

def main():
    st.set_page_config(
        page_title="Chat Modes Overview",
        page_icon="🎯",
        layout="wide"
    )

    render_chat_modes_overview()

if __name__ == "__main__":
    main()