#!/usr/bin/env python3
"""
Chat Test App - Real Chat Interface with UnifiedChatManager
===========================================================

Testing different chat modes with actual Bedrock/AI integration.
Port: 8520 (test port)
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any
import sys
from pathlib import Path
import logging

# Set up paths using PathManager FIRST
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Import PathManager and set up paths properly
from common.utilities.path_manager import PathManager
path_mgr = PathManager()
# Add all necessary paths for imports
for path in path_mgr.get_python_paths():
    if path not in sys.path:
        sys.path.insert(0, path)

# Set up logging
logger = logging.getLogger(__name__)

# Try to import UnifiedChatManager from tidyllm package
try:
    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
    CHAT_SERVICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Chat service not available: {e}")
    CHAT_SERVICE_AVAILABLE = False
    # Fallback ChatMode
    from enum import Enum
    class ChatMode(Enum):
        DIRECT = "direct"
        RAG = "rag"
        DSPY = "dspy"
        HYBRID = "hybrid"
        CUSTOM = "custom"


class EnhancedChatManager:
    """Enhanced chat manager - UI layer component"""

    def __init__(self):
        self.models = ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus", "titan-text-express"]

        # UI should only talk to domain service, never infrastructure
        self.chat_manager = None

        if CHAT_SERVICE_AVAILABLE:
            try:
                # Initialize domain service (UnifiedChatManager)
                # Domain uses adapters/delegates internally - we don't care how
                self.chat_manager = UnifiedChatManager()
                st.success("✅ Connected to Chat Domain Service")
            except Exception as e:
                st.warning(f"⚠️ Could not initialize domain service: {e}")

    def process_message(self, message: str, mode: str, context: Dict) -> Dict:
        """Process a chat message through domain service"""
        # UI talks to domain service only
        if self.chat_manager:
            try:
                model = context.get("model", "claude-3-haiku")
                temperature = context.get("temperature", 0.7)

                # Call domain service method
                # The domain handles all business logic and uses adapters for infrastructure
                response = self.chat_manager.chat(
                    message=message,
                    mode=mode,
                    model=model,
                    temperature=temperature,
                    reasoning=False,
                    history=context.get("history", [])
                )

                # Format response for UI
                if isinstance(response, dict):
                    return response
                elif isinstance(response, str):
                    return {
                        "response": response,
                        "mode": mode,
                        "model": model,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "response": str(response),
                        "mode": mode,
                        "model": model,
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                # Domain service error - fallback
                logger.error(f"Domain service error: {e}")

        # Fallback simple response logic
        if mode == "direct" or mode == ChatMode.DIRECT.value:
            return self._direct_response(message)
        elif mode == "rag" or mode == ChatMode.RAG.value:
            return self._rag_response(message, context)
        elif mode == "dspy" or mode == ChatMode.DSPY.value:
            return self._dspy_response(message)
        elif mode == "hybrid" or mode == ChatMode.HYBRID.value:
            return self._hybrid_response(message, context)
        else:
            return {"response": f"Processing in {mode} mode: {message}", "mode": mode}

    def _direct_response(self, message: str) -> Dict:
        """Fallback when domain service not available"""
        return {
            "response": f"[DOMAIN SERVICE NOT AVAILABLE] {message}",
            "mode": "direct",
            "timestamp": datetime.now().isoformat()
        }

    def _rag_response(self, message: str, context: Dict) -> Dict:
        """RAG-enhanced response"""
        return {
            "response": f"[RAG MODE - NOT CONNECTED] {message}",
            "mode": "rag",
            "timestamp": datetime.now().isoformat()
        }

    def _dspy_response(self, message: str) -> Dict:
        """DSPy optimized response"""
        return {
            "response": f"[DSPY MODE - NOT CONNECTED] {message}",
            "mode": "dspy",
            "timestamp": datetime.now().isoformat()
        }

    def _hybrid_response(self, message: str, context: Dict) -> Dict:
        """Hybrid intelligent mode selection"""
        return {
            "response": f"[HYBRID MODE - NOT CONNECTED] {message}",
            "mode": "hybrid",
            "timestamp": datetime.now().isoformat()
        }


def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = ChatMode.DIRECT.value
    if 'current_model' not in st.session_state:
        st.session_state.current_model = "claude-3-haiku"
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = EnhancedChatManager()
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7


def render_chat_interface():
    """Render the main chat interface"""
    st.subheader("💬 Chat Interface")

    # Chat controls
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        mode = st.selectbox(
            "Chat Mode",
            options=[mode.value for mode in ChatMode],
            index=[mode.value for mode in ChatMode].index(st.session_state.current_mode),
            help="Select how the chat should process messages"
        )
        st.session_state.current_mode = mode

    with col2:
        model = st.selectbox(
            "Model",
            options=st.session_state.chat_manager.models,
            index=st.session_state.chat_manager.models.index(st.session_state.current_model),
            help="Select the AI model to use"
        )
        st.session_state.current_model = model

    with col3:
        if st.button("🗑️ Clear", help="Clear chat history"):
            st.session_state.messages = []
            st.rerun()

    # Temperature slider
    st.session_state.temperature = st.slider(
        "Temperature (creativity)",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )

    # Display mode info
    mode_info = {
        ChatMode.DIRECT.value: "💡 Direct: Simple Q&A without additional context",
        ChatMode.RAG.value: "📚 RAG: Retrieval-Augmented Generation with context",
        ChatMode.DSPY.value: "🎯 DSPy: Optimized prompts for better responses",
        ChatMode.HYBRID.value: "🔀 Hybrid: Intelligent mode selection",
        ChatMode.CUSTOM.value: "⚙️ Custom: Custom processing chain"
    }

    st.info(mode_info.get(st.session_state.current_mode, "Select a chat mode"))

    # Chat messages display
    message_container = st.container()
    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "metadata" in message and st.checkbox("Show details", key=f"details_{id(message)}"):
                    st.json(message["metadata"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Build context
        context = {
            "history": st.session_state.messages[-10:],  # Last 10 messages
            "model": st.session_state.current_model,
            "temperature": st.session_state.temperature,
        }

        # Process message
        response = st.session_state.chat_manager.process_message(
            prompt,
            st.session_state.current_mode,
            context
        )

        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["response"],
            "metadata": response
        })

        st.rerun()


def render_sidebar():
    """Render sidebar with stats and info"""
    with st.sidebar:
        st.title("📊 Chat Statistics")

        # Message count
        st.metric("Total Messages", len(st.session_state.messages))

        # Current settings
        st.write("**Current Settings:**")
        st.write(f"• Mode: {st.session_state.current_mode}")
        st.write(f"• Model: {st.session_state.current_model}")

        # Quick actions
        st.write("**Quick Actions:**")
        if st.button("Export Chat"):
            st.download_button(
                label="Download as JSON",
                data=str(st.session_state.messages),
                file_name="chat_export.json",
                mime="application/json"
            )

        # Mode-specific test queries
        st.write("**Test Queries for Current Mode:**")

        mode_queries = {
            ChatMode.DIRECT.value: [
                "Where is San Francisco?",
                "What is machine learning?",
                "Explain quantum computing"
            ],
            ChatMode.RAG.value: [
                "Tell me about our company policies",
                "What are the best practices for coding?",
                "Search for information about AWS"
            ],
            ChatMode.DSPY.value: [
                "Generate a creative story",
                "Solve this logic puzzle",
                "Write a poem about AI"
            ],
            ChatMode.HYBRID.value: [
                "Analyze this complex problem",
                "Help me understand this concept",
                "Research and explain blockchain"
            ],
            ChatMode.CUSTOM.value: [
                "Process this custom request",
                "Execute workflow for data analysis",
                "Run specialized task"
            ]
        }

        test_queries = mode_queries.get(st.session_state.current_mode, ["Hello", "Test message"])

        for query in test_queries:
            if st.button(f"Try: {query[:20]}...", key=f"test_{query}"):
                st.session_state.messages.append({"role": "user", "content": query})
                context = {
                    "history": st.session_state.messages[-10:],
                    "model": st.session_state.current_model,
                }
                response = st.session_state.chat_manager.process_message(
                    query,
                    st.session_state.current_mode,
                    context
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "metadata": response
                })
                st.rerun()


def main():
    """Main application"""
    st.set_page_config(
        page_title="Chat Test App",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Header
    st.title("💬 Chat Test Application")
    st.markdown("**A simplified chat interface for testing chat functionality**")

    # Initialize session state
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main chat interface
    render_chat_interface()

    # Footer
    st.markdown("---")
    st.caption("Chat Test App • Port 8520 • Testing simplified chat functionality")


if __name__ == "__main__":
    main()
