"""
Ask AI Tab V4 - Simple AI Assistant for Workflows
=================================================
Chat interface for workflow help and generation
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict
from utils.project_selector import render_universal_selector

def render_ask_ai_tab():
    """Render the Ask AI tab - simple chat interface"""

    st.header("🤖 Ask AI Assistant")
    st.markdown("Get help building, fixing, and optimizing workflows")

    # Show current context
    current_project = st.session_state.get('selected_project', 'Global')
    current_workflow = st.session_state.get('current_workflow')

    if current_project != 'Global' or current_workflow:
        context_msg = []
        if current_project != 'Global':
            context_msg.append(f"**Project:** {current_project}")
        if current_workflow:
            context_msg.append(f"**Workflow:** {current_workflow}")
        st.info(" | ".join(context_msg))

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hi! I can help you:\n• Build new workflows\n• Fix problems\n• Optimize performance\n• Explain how cards work\n\nWhat would you like help with?"
            }
        ]

    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("How do I start?", use_container_width=True):
            _add_user_message("How do I create my first workflow?")
            _add_ai_response(_get_starter_guide())

    with col2:
        if st.button("Fix my workflow", use_container_width=True):
            _add_user_message("My workflow is failing. How can I debug it?")
            _add_ai_response(_get_debug_guide())

    with col3:
        if st.button("Make it faster", use_container_width=True):
            _add_user_message("How can I make my workflow run faster?")
            _add_ai_response(_get_optimization_tips())

    with col4:
        if st.button("Explain RAG", use_container_width=True):
            _add_user_message("What is RAG and how do I use it?")
            _add_ai_response(_get_rag_explanation())

    st.markdown("---")

    # Chat interface
    st.markdown("### 💬 Chat")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")

    # Input area
    st.markdown("---")
    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Ask anything about workflows:",
            placeholder="e.g., How do I extract data from PDFs?",
            key="user_input"
        )

    with col2:
        send_button = st.button("Send →", use_container_width=True)

    if send_button and user_input:
        # Add user message
        _add_user_message(user_input)

        # Generate AI response
        response = _generate_ai_response(user_input)
        _add_ai_response(response)

        # Clear input
        st.rerun()

    # Context panel
    st.markdown("---")
    st.markdown("### 📋 Current Context")

    # Show current workflow context
    current_workflow = st.session_state.get('current_workflow')
    workflows = st.session_state.get('workflows', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Your Workflows:**")
        if workflows:
            for name in list(workflows.keys())[:3]:
                st.caption(f"• {name}")
        else:
            st.caption("No workflows yet")

    with col2:
        st.markdown("**Current Focus:**")
        if current_workflow:
            st.caption(f"Working on: {current_workflow}")
        else:
            st.caption("No workflow selected")

    # Help examples
    with st.expander("💡 Example Questions"):
        examples = [
            "How do I build a document analysis workflow?",
            "What's the difference between AI levels?",
            "How can I use multiple RAG systems?",
            "Why is my workflow slow?",
            "How do I add error handling?",
            "Can you create a workflow for financial reports?",
            "What cards work best together?",
            "How does RL optimization work?"
        ]

        for example in examples:
            st.caption(f"• {example}")


def _add_user_message(content: str):
    """Add user message to chat history"""
    st.session_state.chat_history.append({
        "role": "user",
        "content": content
    })


def _add_ai_response(content: str):
    """Add AI response to chat history"""
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": content
    })


def _generate_ai_response(user_input: str) -> str:
    """Generate AI response based on user input"""

    input_lower = user_input.lower()

    # Pattern matching for common questions
    if "create" in input_lower or "build" in input_lower or "start" in input_lower:
        return _get_starter_guide()

    elif "rag" in input_lower:
        return _get_rag_explanation()

    elif "slow" in input_lower or "fast" in input_lower or "optimize" in input_lower:
        return _get_optimization_tips()

    elif "error" in input_lower or "fail" in input_lower or "debug" in input_lower:
        return _get_debug_guide()

    elif "ai level" in input_lower or "assist" in input_lower or "auto" in input_lower:
        return _get_ai_levels_explanation()

    elif "card" in input_lower and "together" in input_lower:
        return _get_card_combination_advice()

    else:
        # Generic helpful response
        return """I can help with that! Here's what I understand:

**To work with workflows:**
1. Go to **Create** tab to build new workflows
2. Select cards from the library (Observe → Orient → Decide → Act)
3. Configure AI level for each card (None/Assist/Auto)
4. Save and test your workflow

**Key tips:**
• Start simple with 3-4 cards
• Use AI 'Assist' mode for most cards
• Test with small inputs first

Would you like me to explain any specific part in more detail?"""


def _get_starter_guide() -> str:
    return """Great! Here's how to create your first workflow:

**Step 1: Go to Create Tab**
Click on the **Create** tab at the top.

**Step 2: Choose Cards**
1. Start with an **Observe** card (like "Extract Document")
2. Add an **Orient** card (like "Analyze Content")
3. Finish with an **Act** card (like "Create Report")

**Step 3: Configure AI**
For each card, choose AI level:
• **None** = Just data processing
• **Assist** = AI helps (recommended)
• **Auto** = AI decides everything

**Step 4: Save**
Give it a name and click **Save Workflow**

**Quick Template:**
Try the "Document Analysis" template to start! It has everything set up for you.

Need help with a specific workflow type?"""


def _get_rag_explanation() -> str:
    return """**RAG (Retrieval-Augmented Generation)** makes AI smarter by giving it access to your documents!

**How it works:**
1. **Retrieval** - Searches your documents for relevant info
2. **Augmented** - Adds that info to the AI's context
3. **Generation** - AI creates better answers using your data

**In workflows:**
• Use "RAG Search" card to find relevant documents
• Follow with "Ask Expert" to get AI analysis
• The AI will use your documents to give accurate answers

**Example workflow:**
1. Load Data → 2. RAG Search → 3. Ask Expert → 4. Create Report

**Benefits:**
• More accurate answers
• Uses your specific knowledge
• No hallucinations

Want me to help you build a RAG workflow?"""


def _get_optimization_tips() -> str:
    return """Here's how to make your workflows faster:

**Quick Wins:**
1. **Reduce AI Usage**
   - Change 'Auto' to 'Assist' where possible
   - Use 'None' for simple data operations

2. **Order Matters**
   - Put data extraction first
   - AI analysis after data is ready
   - Reports/outputs last

3. **Choose Right Models**
   - GPT-3.5 for simple tasks (faster, cheaper)
   - GPT-4 only for complex reasoning

4. **Enable Caching**
   - Cache expensive operations
   - Reuse results when possible

**Check Performance:**
Go to **Optimize** tab to see:
• Which steps are slow
• Cost per run
• AI suggestions

**Biggest Impact:**
Usually changing all 'Auto' to 'Assist' gives 40% speed improvement!

Want me to review your specific workflow?"""


def _get_debug_guide() -> str:
    return """Let's fix your workflow! Here's how to debug:

**Step 1: Check the Run Tab**
Look at which step is failing and the error message.

**Common Issues & Fixes:**

**1. Timeout Errors**
• Problem: Step takes too long
• Fix: Reduce AI complexity or switch to faster model

**2. No Input**
• Problem: Card expects input that doesn't exist
• Fix: Make sure previous cards produce needed data

**3. AI Errors**
• Problem: AI can't understand request
• Fix: Simplify prompt or provide examples

**Debug Mode:**
In **Run** tab, select "Debug" mode to:
• Run step by step
• See outputs at each stage
• Modify inputs between steps

**Quick Fixes:**
• Change AI from 'Auto' to 'Assist'
• Add error handling cards
• Test with simpler input first

What specific error are you seeing?"""


def _get_ai_levels_explanation() -> str:
    return """**AI Levels** control how much AI helps with each card:

**⚪ None (No AI)**
• Pure data processing
• Fastest and free
• Use for: File operations, data loading, simple transforms

**🔵 Assist (AI Helps)**
• AI provides guidance and suggestions
• Balanced speed and intelligence
• Use for: Analysis, content understanding, summaries

**🟢 Auto (Full AI)**
• AI makes all decisions
• Slowest but smartest
• Use for: Complex reasoning, creative tasks, critical decisions

**Best Practices:**
• Start with 'Assist' for most cards
• Use 'None' for data operations
• Save 'Auto' for critical thinking steps

**Example Setup:**
1. Extract Document (None) - Just get the text
2. Analyze Content (Assist) - AI helps understand
3. Generate Insights (Auto) - AI creates new ideas
4. Save Results (None) - Just save the file

This balances performance and intelligence!"""


def _get_card_combination_advice() -> str:
    return """Here are powerful card combinations that work great together:

**📄 Document Processing Chain:**
Extract Document → Analyze Content → Generate Insights → Create Report

**🔍 RAG Question-Answering:**
Load Data → RAG Search → Ask Expert → Send Results

**📊 Data Analysis Pipeline:**
Load Data → Compare Documents → Evaluate Options → Create Report

**🎯 Decision Support System:**
Extract Document → RAG Search → Evaluate Options → Generate Insights

**Tips for Combining Cards:**
1. **Data Flow** - Make sure each card's output matches next card's input
2. **AI Progression** - Start with None/Assist, end with Auto
3. **OODA Loop** - Observe → Orient → Decide → Act

**Don't Mix:**
• Multiple extraction cards (redundant)
• Too many AI Auto cards (slow and expensive)

**Power Combo:**
RAG Search + Ask Expert = Super accurate answers using your data!

Want a specific combination for your use case?"""