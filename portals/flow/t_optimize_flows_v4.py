"""
Optimize Flows Tab V4 - Simple Performance Metrics
==================================================
View performance and get AI suggestions for improvement
"""

import streamlit as st
import random
from typing import Dict, List

def render_optimize_tab():
    """Render the Optimize workflow tab - clear metrics and suggestions"""

    st.header("📈 Optimize Workflows")
    st.markdown("See how your workflows perform and get improvement suggestions")

    workflows = st.session_state.get('workflows', {})

    # Get current workflow from session state
    current_workflow = st.session_state.get('current_workflow')

    if workflows:
        # Use current workflow if set, otherwise use first available
        if current_workflow and current_workflow in workflows:
            selected = current_workflow
        elif workflows:
            selected = list(workflows.keys())[0]
        else:
            selected = None

        if selected:
            workflow = workflows[selected]

            # Performance Overview (simple metrics)
            st.markdown(f"### Performance: **{selected}**")

            # Key metrics in big cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                success_rate = random.randint(85, 99)  # Simulated
                st.metric(
                    "Success Rate",
                    f"{success_rate}%",
                    f"+{random.randint(1,5)}%",
                    help="Percentage of successful runs"
                )

            with col2:
                avg_time = round(random.uniform(2.5, 8.5), 1)  # Simulated
                st.metric(
                    "Avg Time",
                    f"{avg_time}s",
                    f"-{round(random.uniform(0.1, 0.5), 1)}s",
                    help="Average execution time"
                )

            with col3:
                rl_score = round(random.uniform(0.75, 0.95), 2)  # Simulated
                st.metric(
                    "RL Score",
                    f"{rl_score}",
                    f"+{round(random.uniform(0.01, 0.05), 2)}",
                    help="Reinforcement Learning optimization score"
                )

            with col4:
                cost_run = round(random.uniform(0.05, 0.25), 2)  # Simulated
                st.metric(
                    "Cost/Run",
                    f"${cost_run}",
                    f"-${round(random.uniform(0.01, 0.03), 2)}",
                    help="Average cost per execution"
                )

            st.markdown("---")

            # Step-by-step performance
            st.markdown("### 📊 Step Performance")

            steps = workflow.get('cards', [])
            for i, step in enumerate(steps):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

                with col1:
                    # Step name with AI indicator
                    ai_level = step.get('ai_level', 'Assist')
                    ai_emoji = {"None": "⚪", "Assist": "🔵", "Auto": "🟢"}
                    st.markdown(f"**{i+1}. {step['name']}** {ai_emoji[ai_level]}")

                with col2:
                    # Success rate per step
                    step_success = random.randint(80, 100)
                    color = "🟢" if step_success > 90 else "🟡" if step_success > 80 else "🔴"
                    st.caption(f"{color} {step_success}% success")

                with col3:
                    # Time per step
                    step_time = round(random.uniform(0.5, 3.0), 1)
                    st.caption(f"⏱️ {step_time}s")

                with col4:
                    # Cost per step (if AI)
                    if ai_level != "None":
                        step_cost = round(random.uniform(0.01, 0.08), 3)
                        st.caption(f"💰 ${step_cost}")
                    else:
                        st.caption("💰 Free")

            st.markdown("---")

            # AI Suggestions (simple, actionable)
            st.markdown("### 💡 AI Suggestions")

            suggestions = _generate_suggestions(workflow)

            for i, suggestion in enumerate(suggestions):
                with st.expander(f"**Suggestion {i+1}: {suggestion['title']}**"):
                    st.write(suggestion['description'])

                    # Impact metrics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"**Expected improvement:** {suggestion['impact']}")
                    with col2:
                        st.caption(f"**Difficulty:** {suggestion['difficulty']}")

                    # Apply button
                    if st.button(f"Apply this suggestion", key=f"apply_{i}"):
                        st.success("✅ Suggestion applied! Check the Create tab to see changes.")
                        _apply_suggestion(selected, suggestion)

            # Optimization actions
            st.markdown("---")
            st.markdown("### 🚀 Quick Actions")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("🧪 Run A/B Test", use_container_width=True):
                    st.info("A/B testing will compare two versions of your workflow")

            with col2:
                if st.button("🔄 Auto-Optimize", use_container_width=True):
                    with st.spinner("Optimizing with RL..."):
                        time.sleep(2)
                        st.success("✅ Workflow optimized! +5% performance expected")

            with col3:
                if st.button("📊 Export Report", use_container_width=True):
                    st.info("Performance report exported to reports/")

    else:
        # No workflows yet
        st.info("📝 No workflows to optimize yet. Create some workflows first!")

        # Tips for optimization
        st.markdown("### 🎯 Optimization Tips")

        tips = [
            {
                "title": "Use AI Wisely",
                "tip": "Set AI to 'Auto' only for complex reasoning steps. Use 'Assist' for guidance and 'None' for simple data operations."
            },
            {
                "title": "Order Matters",
                "tip": "Place data extraction steps before AI analysis to reduce token usage."
            },
            {
                "title": "Cache Results",
                "tip": "Enable caching for expensive operations that don't change often."
            },
            {
                "title": "Choose Right Models",
                "tip": "Use GPT-3.5 for simple tasks, GPT-4 only when needed for complex reasoning."
            }
        ]

        for tip in tips:
            with st.expander(tip['title']):
                st.write(tip['tip'])


def _generate_suggestions(workflow: Dict) -> List[Dict]:
    """Generate optimization suggestions for workflow"""

    suggestions = []
    cards = workflow.get('cards', [])

    # Check for optimization opportunities
    has_all_ai = all(c.get('ai_level') == 'Auto' for c in cards)
    has_no_ai = all(c.get('ai_level') == 'None' for c in cards)

    if has_all_ai:
        suggestions.append({
            "title": "Reduce AI usage",
            "description": "Not all steps need full AI. Consider using 'Assist' or 'None' for simpler steps.",
            "impact": "+20% speed, -30% cost",
            "difficulty": "Easy",
            "action": "reduce_ai"
        })

    if has_no_ai:
        suggestions.append({
            "title": "Add AI assistance",
            "description": "Adding AI to analysis steps could improve quality of results.",
            "impact": "+15% accuracy",
            "difficulty": "Easy",
            "action": "add_ai"
        })

    if len(cards) > 5:
        suggestions.append({
            "title": "Combine similar steps",
            "description": "Some steps could be merged for better efficiency.",
            "impact": "+10% speed",
            "difficulty": "Medium",
            "action": "merge_steps"
        })

    # Always add a RAG suggestion
    suggestions.append({
        "title": "Use RAG for better context",
        "description": "Adding RAG search could improve accuracy by providing better context to AI steps.",
        "impact": "+25% accuracy",
        "difficulty": "Medium",
        "action": "add_rag"
    })

    return suggestions[:3]  # Return top 3 suggestions


def _apply_suggestion(workflow_name: str, suggestion: Dict):
    """Apply optimization suggestion to workflow"""

    if workflow_name in st.session_state.workflows:
        workflow = st.session_state.workflows[workflow_name]

        # Apply different optimizations
        if suggestion['action'] == 'reduce_ai':
            # Reduce some AI levels
            for card in workflow['cards']:
                if card.get('ai_level') == 'Auto':
                    card['ai_level'] = 'Assist'
                    break

        elif suggestion['action'] == 'add_ai':
            # Add AI to some steps
            for card in workflow['cards']:
                if card.get('ai_level') == 'None' and 'analyze' in card['name'].lower():
                    card['ai_level'] = 'Assist'
                    break

        # Update workflow
        st.session_state.workflows[workflow_name] = workflow


# Import for time simulation
import time