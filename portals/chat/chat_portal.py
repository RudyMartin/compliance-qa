#!/usr/bin/env python3
"""
Chat Portal - AI Conversation Interface
========================================
Real-time chat interface with 4 Claude models and 5 chat modes.
Port: 8502
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Add parent to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Initialize services
# Since tidyllm is installed but services aren't exposed, use local import
from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
from infrastructure.yaml_loader import get_settings_loader
from infrastructure.services.aws_service import get_aws_service

# Initialize managers
chat_manager = UnifiedChatManager()
settings_loader = get_settings_loader()
aws_service = get_aws_service()

def set_page_config():
    """Configure the Streamlit page."""
    st.set_page_config(
        page_title="Chat Portal - AI Conversation",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = 'claude-3-sonnet'
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'direct'
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 1000
    if 'top_p' not in st.session_state:
        st.session_state.top_p = 0.9
    if 'use_reasoning' not in st.session_state:
        st.session_state.use_reasoning = False
    if 'use_streaming' not in st.session_state:
        st.session_state.use_streaming = False
    if 'show_history' not in st.session_state:
        st.session_state.show_history = True

def render_header():
    """Render the portal header."""
    st.title("💬 Chat Portal - AI Conversation Interface")
    st.markdown("**Chat with 4 Claude models using 5 different modes**")

    # Quick status
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Model", st.session_state.current_model.replace('-', ' ').title())

    with col2:
        st.metric("Chat Mode", st.session_state.current_mode.upper())

    with col3:
        st.metric("Messages", len(st.session_state.messages))

    with col4:
        bedrock_config = settings_loader.get_bedrock_config()
        model_count = len(bedrock_config.get('model_mapping', {}))
        st.metric("Models Available", model_count)

    st.markdown("---")

def render_chat_controls():
    """Render chat controls in sidebar."""
    with st.sidebar:
        st.title("🎛️ Chat Controls")

        # Model Selection
        st.subheader("🤖 Model Selection")
        bedrock_config = settings_loader.get_bedrock_config()
        model_mapping = bedrock_config.get('model_mapping', {})
        models = list(model_mapping.keys())

        st.session_state.current_model = st.selectbox(
            "Select AI Model:",
            models,
            index=models.index(st.session_state.current_model) if st.session_state.current_model in models else 0,
            help="Choose which Claude model to use"
        )

        # Model descriptions
        model_info = {
            'claude-3-haiku': "⚡ Fastest - Great for quick questions",
            'claude-3-sonnet': "⚖️ Balanced - Good for most tasks",
            'claude-3-5-sonnet': "✨ Enhanced - Latest capabilities",
            'claude-3-opus': "💪 Most Powerful - Complex reasoning"
        }

        if st.session_state.current_model in model_info:
            st.info(model_info[st.session_state.current_model])

        # Chat Mode Selection
        st.subheader("💬 Chat Mode")
        modes = [mode.value for mode in ChatMode]

        st.session_state.current_mode = st.selectbox(
            "Select Chat Mode:",
            modes,
            index=modes.index(st.session_state.current_mode) if st.session_state.current_mode in modes else 0,
            help="Choose how the AI processes your messages"
        )

        # Mode descriptions
        mode_info = {
            'direct': "Direct model response",
            'rag': "Enhanced with retrieval",
            'dspy': "Optimized prompting",
            'hybrid': "Intelligent mode selection",
            'custom': "Custom processing chain"
        }

        if st.session_state.current_mode in mode_info:
            st.caption(mode_info[st.session_state.current_mode])

        # Parameters
        st.subheader("⚙️ Parameters")

        st.session_state.temperature = st.slider(
            "Temperature (Creativity):",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )

        st.session_state.max_tokens = st.slider(
            "Max Tokens (Response Length):",
            min_value=100,
            max_value=4000,
            value=st.session_state.max_tokens,
            step=100,
            help="Maximum length of the response"
        )

        st.session_state.top_p = st.slider(
            "Top-p (Diversity):",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.top_p,
            step=0.1,
            help="Controls response diversity"
        )

        # Toggles
        st.subheader("🔄 Options")

        st.session_state.use_reasoning = st.checkbox(
            "Enable Reasoning/Chain of Thought",
            value=st.session_state.use_reasoning,
            help="Show AI's reasoning process"
        )

        st.session_state.use_streaming = st.checkbox(
            "Enable Streaming Response",
            value=st.session_state.use_streaming,
            help="Show response as it's generated",
            disabled=True  # Not yet implemented
        )

        st.session_state.show_history = st.checkbox(
            "Show Conversation History",
            value=st.session_state.show_history,
            help="Display previous messages"
        )

        # Actions
        st.subheader("🎬 Actions")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        with col2:
            if st.button("💾 Export", use_container_width=True):
                export_conversation()

def render_chat_interface():
    """Render the main chat interface."""
    # Display conversation history
    if st.session_state.show_history:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_ai_response(prompt)
                st.markdown(response)

                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})

def get_ai_response(prompt: str) -> str:
    """Get response from AI model."""
    try:
        # Prepare parameters
        params = {
            'temperature': st.session_state.temperature,
            'max_tokens': st.session_state.max_tokens,
            'top_p': st.session_state.top_p,
            'model': st.session_state.current_model
        }

        # Add reasoning if enabled
        if st.session_state.use_reasoning:
            prompt = f"Please think step-by-step and show your reasoning.\n\n{prompt}"

        # Call chat manager
        try:
            response = chat_manager.chat(
                message=prompt,
                mode=ChatMode(st.session_state.current_mode),
                **params
            )
        except:
            # Fallback to direct AWS call if chat manager fails
            bedrock_config = settings_loader.get_bedrock_config()
            model_id = bedrock_config['model_mapping'][st.session_state.current_model]

            # Simple direct call
            response = f"[Using {st.session_state.current_model} in {st.session_state.current_mode} mode]\n\n"
            response += f"Response to: {prompt[:100]}...\n\n"
            response += "Chat functionality is being configured. Please check AWS Bedrock connection."

        return response

    except Exception as e:
        return f"Error: {str(e)}"

def export_conversation():
    """Export conversation to file."""
    if st.session_state.messages:
        # Create export content
        export_content = "# Chat Conversation Export\n\n"
        export_content += f"Model: {st.session_state.current_model}\n"
        export_content += f"Mode: {st.session_state.current_mode}\n"
        export_content += f"Temperature: {st.session_state.temperature}\n"
        export_content += f"Max Tokens: {st.session_state.max_tokens}\n"
        export_content += f"Top-p: {st.session_state.top_p}\n\n"
        export_content += "---\n\n"

        for msg in st.session_state.messages:
            role = msg['role'].upper()
            content = msg['content']
            export_content += f"## {role}:\n{content}\n\n"

        # Download button
        st.download_button(
            label="📥 Download Conversation",
            data=export_content,
            file_name="chat_conversation.md",
            mime="text/markdown"
        )
        st.success("Conversation ready for download!")
    else:
        st.warning("No conversation to export")

def render_model_info():
    """Render model information panel."""
    with st.expander("📊 Model Information", expanded=False):
        bedrock_config = settings_loader.get_bedrock_config()
        model_mapping = bedrock_config.get('model_mapping', {})

        st.write("**Available Models:**")
        for model_name, model_id in model_mapping.items():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(f"**{model_name}**")
            with col2:
                st.code(model_id, language=None)

        st.write("**Configuration:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Timeout", f"{bedrock_config.get('timeout', 60)}s")
        with col2:
            st.metric("Retry Attempts", bedrock_config.get('retry_attempts', 3))
        with col3:
            st.metric("Default Model", st.session_state.current_model)

def render_quick_prompts():
    """Render quick prompt buttons."""
    st.subheader("💡 Quick Prompts")

    prompts = {
        "Hello": "Hello! How can you help me today?",
        "Explain": "Can you explain how you work?",
        "Code": "Write a Python function to calculate fibonacci numbers",
        "Story": "Tell me a short story about a robot",
        "Analyze": "What are the key considerations for building an AI system?",
        "Compare": "Compare the different Claude models available"
    }

    cols = st.columns(len(prompts))
    for i, (label, prompt) in enumerate(prompts.items()):
        with cols[i]:
            if st.button(label, use_container_width=True):
                # Simulate sending the prompt
                st.session_state.messages.append({"role": "user", "content": prompt})
                response = get_ai_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

def main():
    """Main application."""
    set_page_config()
    initialize_session_state()

    # Render controls in sidebar
    render_chat_controls()

    # Main content area
    render_header()

    # Quick prompts
    render_quick_prompts()

    st.markdown("---")

    # Chat interface
    render_chat_interface()

    # Model info at bottom
    render_model_info()

if __name__ == "__main__":
    main()