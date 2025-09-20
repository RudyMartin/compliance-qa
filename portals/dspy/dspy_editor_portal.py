#!/usr/bin/env python3
"""
DSPy Markdown Editor Portal
===========================
Allows business users to define AI workflows using markdown syntax
that gets compiled to DSPy programs for execution.

Similar to workflow editor but for AI behavior customization.
"""

import streamlit as st
import yaml
from pathlib import Path
import sys

# Add parent paths
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

from domain.services.dspy_compiler_service import DSPyCompilerService
from domain.services.dspy_execution_service import DSPyExecutionService

# Initialize services
compiler_service = DSPyCompilerService()
execution_service = DSPyExecutionService()

def set_page_config():
    """Configure Streamlit page."""
    st.set_page_config(
        page_title="DSPy Editor - AI Customization",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render portal header."""
    st.title("🤖 DSPy AI Customization Portal")
    st.markdown("**Define AI behavior using business-friendly markdown**")
    st.markdown("---")

def render_template_selector():
    """Show pre-built templates for common use cases."""
    st.subheader("📚 Start with a Template")

    templates = {
        "Document QA": """
# Document Question Answering

## Objective
Answer questions about uploaded documents accurately.

## Steps
1. **Load Document**
   - Input: PDF or Word document
   - Process: Extract text content

2. **Understand Question**
   - Input: User question
   - Process: Identify key terms and intent

3. **Find Relevant Sections**
   - Search: Look for paragraphs mentioning [key terms]
   - Rank: Score by relevance to question

4. **Generate Answer**
   - Context: Use top 3 relevant sections
   - Style: Professional and concise
   - Include: Source references

## Constraints
- Maximum 500 words per answer
- Always cite document sections
- Admit when information not found
""",

        "Compliance Check": """
# Compliance Validation

## Objective
Check documents against regulatory requirements.

## Requirements
- MVS 5.4.3: Model documentation complete
- VST Section 3: Validation procedures documented
- SR11-7: Risk assessment included

## Process
1. **Extract Compliance Sections**
   - Look for: Risk, Validation, Model sections

2. **Check Each Requirement**
   - For each requirement:
     - Find relevant content
     - Assess completeness
     - Note any gaps

3. **Generate Report**
   - Summary: COMPLIANT or NON-COMPLIANT
   - Details: List specific findings
   - Recommendations: How to address gaps

## Output Format
- Overall Status: [PASS/FAIL]
- Requirement Checklist: [✓/✗]
- Action Items: [List]
""",

        "Data Analysis": """
# Intelligent Data Analysis

## Objective
Analyze data and provide insights.

## Input
- Data: CSV, Excel, or JSON
- Question: What to analyze

## Analysis Steps
1. **Data Overview**
   - Shape: rows × columns
   - Types: numeric, categorical, dates
   - Quality: missing values, outliers

2. **Statistical Summary**
   - Central tendency: mean, median
   - Spread: std dev, ranges
   - Correlations: key relationships

3. **Answer Question**
   - Specific analysis for user query
   - Visualizations if helpful
   - Statistical significance

## Deliverables
- Executive summary (3 sentences)
- Key findings (bullet points)
- Recommendations (actionable items)
"""
    }

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_template = st.selectbox(
            "Choose Template",
            ["Custom"] + list(templates.keys())
        )

        if selected_template != "Custom":
            if st.button("Load Template"):
                st.session_state['dspy_markdown'] = templates[selected_template]
                st.rerun()

    with col2:
        if selected_template != "Custom" and selected_template in templates:
            st.info(f"**{selected_template}**: {templates[selected_template].split('##')[1].split('\\n')[1]}")

def render_markdown_editor():
    """Main markdown editor for DSPy definitions."""
    st.subheader("✏️ Define AI Behavior")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**📝 Markdown Definition**")

        # Initialize with template or empty
        default_text = st.session_state.get('dspy_markdown', """# My AI Workflow

## Objective
What should the AI accomplish?

## Input
What information does it need?

## Process
1. First step
2. Second step
3. Third step

## Output
What should it produce?

## Constraints
- Any limitations
- Quality requirements
- Performance needs
""")

        markdown_text = st.text_area(
            "Write your AI behavior in markdown:",
            value=default_text,
            height=500,
            key="dspy_editor"
        )

        # Parse button
        if st.button("🔄 Parse & Validate", type="primary"):
            result = compiler_service.parse_markdown(markdown_text)
            st.session_state['parsed_dspy'] = result

            if result['valid']:
                st.success("✅ Valid DSPy definition!")
            else:
                st.error(f"❌ Invalid: {result.get('error')}")

    with col2:
        st.write("**🤖 Compiled DSPy Program**")

        if 'parsed_dspy' in st.session_state:
            result = st.session_state['parsed_dspy']

            if result['valid']:
                # Show compiled DSPy
                st.code(result['dspy_program'], language='python')

                # Show signatures
                st.write("**Extracted Signatures:**")
                for sig in result.get('signatures', []):
                    st.write(f"- {sig}")

                # Show modules
                st.write("**DSPy Modules:**")
                for module in result.get('modules', []):
                    st.write(f"- {module}")
        else:
            st.info("👈 Write markdown and click Parse to see DSPy program")

def render_execution_panel():
    """Panel for testing the DSPy program."""
    st.subheader("🚀 Test Execution")

    if 'parsed_dspy' not in st.session_state:
        st.warning("⚠️ Parse your markdown first")
        return

    if not st.session_state['parsed_dspy']['valid']:
        st.error("❌ Fix validation errors first")
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("**Test Input**")

        # Dynamic input fields based on parsed requirements
        parsed = st.session_state['parsed_dspy']
        inputs = {}

        for input_field in parsed.get('inputs', ['text']):
            if input_field == 'document':
                uploaded = st.file_uploader(f"Upload {input_field}", type=['pdf', 'txt', 'docx'])
                if uploaded:
                    inputs[input_field] = uploaded
            else:
                inputs[input_field] = st.text_area(f"Enter {input_field}:", height=100)

        if st.button("▶️ Execute DSPy Program"):
            with st.spinner("Running DSPy program..."):
                result = execution_service.execute(
                    parsed['dspy_program'],
                    inputs
                )
                st.session_state['execution_result'] = result

    with col2:
        st.write("**Execution Result**")

        if 'execution_result' in st.session_state:
            result = st.session_state['execution_result']

            if result['success']:
                st.success("✅ Execution successful!")

                # Show output
                st.write("**Output:**")
                st.write(result['output'])

                # Show metrics
                if result.get('metrics'):
                    st.write("**Metrics:**")
                    for key, value in result['metrics'].items():
                        st.metric(key, value)

                # Show trace
                with st.expander("🔍 Execution Trace"):
                    st.json(result.get('trace', {}))
            else:
                st.error(f"❌ Execution failed: {result.get('error')}")

def render_library_manager():
    """Manage saved DSPy programs."""
    st.subheader("📚 DSPy Program Library")

    saved_programs = compiler_service.list_saved_programs()

    if not saved_programs:
        st.info("No saved programs yet. Create and save your first one!")
        return

    col1, col2, col3 = st.columns([2, 1, 1])

    for program in saved_programs:
        with col1:
            st.write(f"**{program['name']}**")
            st.write(f"_{program['description']}_")

        with col2:
            if st.button(f"Load", key=f"load_{program['id']}"):
                st.session_state['dspy_markdown'] = program['markdown']
                st.rerun()

        with col3:
            if st.button(f"Delete", key=f"delete_{program['id']}"):
                compiler_service.delete_program(program['id'])
                st.rerun()

def render_save_dialog():
    """Dialog to save current DSPy program."""
    if 'parsed_dspy' in st.session_state and st.session_state['parsed_dspy']['valid']:
        with st.expander("💾 Save Program"):
            name = st.text_input("Program Name")
            description = st.text_area("Description", height=60)

            if st.button("Save to Library"):
                if name:
                    compiler_service.save_program(
                        name=name,
                        description=description,
                        markdown=st.session_state.get('dspy_markdown', ''),
                        dspy_program=st.session_state['parsed_dspy']['dspy_program']
                    )
                    st.success(f"✅ Saved '{name}' to library!")
                else:
                    st.error("Please enter a name")

def render_integration_options():
    """Options for integrating with other systems."""
    st.subheader("🔌 Integration Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Export Options**")
        if st.button("📄 Export as Python"):
            if 'parsed_dspy' in st.session_state:
                st.download_button(
                    "Download .py file",
                    st.session_state['parsed_dspy']['dspy_program'],
                    "dspy_program.py",
                    "text/plain"
                )

    with col2:
        st.write("**API Endpoint**")
        if st.button("🌐 Generate API"):
            st.code("""
# POST /api/dspy/execute
{
    "program_id": "your_program_id",
    "inputs": {
        "text": "input text",
        "document": "base64_encoded"
    }
}
            """, language='json')

    with col3:
        st.write("**Workflow Integration**")
        if st.button("🔄 Add to Workflow"):
            st.info("DSPy program can be used as a workflow step")

def main():
    """Main application."""
    set_page_config()
    render_header()

    # Sidebar navigation
    with st.sidebar:
        st.title("🤖 DSPy Editor")

        page = st.selectbox(
            "Section",
            ["Templates", "Editor", "Test", "Library", "Integration"]
        )

        st.markdown("---")

        st.write("**What is DSPy?**")
        st.info(
            "DSPy lets you define AI behavior declaratively. "
            "Write what you want in markdown, and it becomes "
            "an optimized AI program!"
        )

        st.write("**Benefits:**")
        st.write("✅ No coding required")
        st.write("✅ Business-friendly syntax")
        st.write("✅ Automatic optimization")
        st.write("✅ Reusable programs")

    # Render selected page
    if page == "Templates":
        render_template_selector()
        render_markdown_editor()
    elif page == "Editor":
        render_markdown_editor()
        render_save_dialog()
    elif page == "Test":
        render_execution_panel()
    elif page == "Library":
        render_library_manager()
    elif page == "Integration":
        render_integration_options()

if __name__ == "__main__":
    main()