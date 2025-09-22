"""
Run Flows Tab V4 - Simple Workflow Execution
============================================
Execute workflows with clear progress and control
"""

import streamlit as st
import time
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

def render_run_tab():
    """Render the Run workflow tab - simple execution interface"""

    st.header("▶️ Run Workflows")
    st.markdown("Execute and test your workflows")

    # Show current context
    selected_project = st.session_state.get('selected_project', 'global')
    current_workflow = st.session_state.get('current_workflow')

    if selected_project != 'global' or current_workflow:
        context_msg = []
        if selected_project != 'global':
            context_msg.append(f"**Project:** {selected_project}")
        if current_workflow:
            context_msg.append(f"**Workflow:** {current_workflow}")
        st.info(" | ".join(context_msg))

    # Use the global project selection from session state
    projects_dir = Path(__file__).parent.parent.parent / "domain" / "workflows" / "projects"

    # Get selected project from session state
    selected_project = st.session_state.get('selected_project', 'Global')
    project_name = None if selected_project == "Global" else selected_project

    if project_name:
        # Load project-specific workflows
        workflow_file = projects_dir / project_name / "workflows.json"
    else:
        # Load global workflows
        workflow_file = Path(__file__).parent.parent.parent / "domain" / "workflows" / "portal_workflows.json"

    # Load workflows from file
    workflows = {}
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            workflows = data.get('workflows', {})

    # Get current workflow
    current_workflow = st.session_state.get('current_workflow')

    # Use current workflow if set, otherwise use first available
    if current_workflow and current_workflow in workflows:
        selected = current_workflow
    elif workflows:
        selected = list(workflows.keys())[0]
        st.session_state.current_workflow = selected
    else:
        selected = "Select a workflow..."


    if selected != "Select a workflow...":
        workflow = workflows[selected]

        # Workflow overview
        st.markdown(f"### Running: **{selected}**")

        # Step count
        steps = workflow.get('cards', [])
        st.caption(f"This workflow has {len(steps)} steps")

        # Input section (simple)
        st.markdown("### 📥 Inputs")
        col1, col2 = st.columns(2)

        with col1:
            input_type = st.selectbox(
                "Input Type",
                ["Text", "File", "URL"],
                help="What kind of input do you have?"
            )

        with col2:
            if input_type == "Text":
                input_value = st.text_area("Enter text:", height=100)
            elif input_type == "File":
                input_value = st.file_uploader("Upload file:")
            else:
                input_value = st.text_input("Enter URL:")

        # Execution controls
        st.markdown("### ⚙️ Execution Settings")

        col1, col2, col3 = st.columns(3)

        with col1:
            execution_mode = st.radio(
                "Mode",
                ["Fast", "Careful", "Debug"],
                help="Fast: Quick run • Careful: With validation • Debug: Step by step"
            )

        with col2:
            ai_override = st.checkbox(
                "Override AI settings",
                help="Use workflow's default AI settings"
            )

            if ai_override:
                ai_model = st.selectbox(
                    "AI Model",
                    ["GPT-4", "GPT-3.5", "Claude", "Local"]
                )

        with col3:
            save_results = st.checkbox(
                "Save results",
                value=True,
                help="Save execution results for later"
            )

        # Big run button
        st.markdown("---")

        if st.button("🚀 **RUN WORKFLOW**", type="primary", use_container_width=True):
            if input_value:
                _execute_workflow(workflow, input_value, execution_mode)
            else:
                st.error("Please provide input first!")

        # Execution history (if exists)
        if 'execution_history' in st.session_state:
            st.markdown("---")
            st.markdown("### 📜 Recent Runs")

            history = st.session_state.execution_history
            for run in history[-3:]:  # Show last 3 runs
                with st.expander(f"{run['workflow']} - {run['time']}"):
                    st.write(f"**Status:** {run['status']}")
                    st.write(f"**Duration:** {run['duration']}s")
                    st.write(f"**Steps completed:** {run['steps_completed']}/{run['total_steps']}")

                    if run['status'] == "✅ Success":
                        st.success("Completed successfully!")
                        if st.button("View results", key=f"view_{run['id']}"):
                            _show_results(run['results'])
                    else:
                        st.error(f"Failed at step {run['steps_completed']}")

    else:
        # No workflow selected
        st.info("👆 Select a workflow to run, or go to **Manage** tab to see all workflows")

        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Go to Create", use_container_width=True):
                st.info("Switch to Create tab to build a workflow")

        with col2:
            if st.button("Go to Manage", use_container_width=True):
                st.info("Switch to Manage tab to select a workflow")


def _execute_workflow(workflow: Dict, input_value: Any, mode: str):
    """Execute the workflow with progress display"""

    steps = workflow.get('cards', [])
    total_steps = len(steps)

    # Progress container
    progress_container = st.container()
    status_container = st.container()

    with progress_container:
        st.markdown("### 🔄 Execution Progress")
        progress_bar = st.progress(0)
        progress_text = st.empty()

    # Execute each step
    results = []
    start_time = time.time()

    for i, step in enumerate(steps):
        # Update progress
        progress = (i / total_steps)
        progress_bar.progress(progress)
        progress_text.text(f"Step {i+1}/{total_steps}: {step['name']}")

        # Simulate execution
        with status_container:
            with st.spinner(f"Running: {step['name']}..."):
                # Simulate different execution times based on AI level
                ai_level = step.get('ai_level', 'Assist')
                if ai_level == 'Auto':
                    time.sleep(2)  # AI takes longer
                elif ai_level == 'Assist':
                    time.sleep(1)
                else:
                    time.sleep(0.5)  # No AI is faster

                # Simulate step result
                result = {
                    "step": step['name'],
                    "status": "success",
                    "output": f"Processed with {ai_level} AI assistance"
                }
                results.append(result)

                # Show step completion
                st.success(f"✅ {step['name']}")

        # Debug mode - pause between steps
        if mode == "Debug" and i < total_steps - 1:
            if st.button(f"Continue to next step", key=f"continue_{i}"):
                pass
            else:
                st.stop()

    # Complete
    progress_bar.progress(1.0)
    progress_text.text(f"✅ Workflow complete!")

    duration = round(time.time() - start_time, 1)

    # Save to history
    if 'execution_history' not in st.session_state:
        st.session_state.execution_history = []

    run_record = {
        "id": len(st.session_state.execution_history),
        "workflow": workflow['name'],
        "time": datetime.now().strftime("%H:%M:%S"),
        "status": "✅ Success",
        "duration": duration,
        "steps_completed": total_steps,
        "total_steps": total_steps,
        "results": results
    }

    st.session_state.execution_history.append(run_record)

    # Show summary
    st.markdown("---")
    st.markdown("### ✅ Execution Complete!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duration", f"{duration}s")
    with col2:
        st.metric("Steps", f"{total_steps}/{total_steps}")
    with col3:
        st.metric("Status", "Success")

    # Show results preview
    with st.expander("📊 View Results", expanded=True):
        for result in results:
            st.write(f"• **{result['step']}**: {result['output']}")


def _show_results(results: List[Dict]):
    """Display execution results"""
    for result in results:
        st.write(f"• **{result['step']}**: {result['output']}")