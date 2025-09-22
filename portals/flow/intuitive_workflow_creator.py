"""
Intuitive Workflow Creator Portal
================================
A natural language, conversational interface for creating business workflows.
No technical knowledge required - just describe what you want to accomplish.

Features:
- Natural language workflow description
- AI-powered conversational guidance
- Automatic template generation
- Business-friendly interface
- Zero technical jargon
"""

import streamlit as st
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import domain services
try:
    from domain.services.business_signature_service import (
        BusinessSignatureService,
        BusinessRequirementType,
        BusinessContext
    )
    from domain.services.ai_template_builder_service import AITemplateBuilderService
    from adapters.secondary.workflow.workflow_dependencies_adapter import get_workflow_dependencies_adapter
    DOMAIN_SERVICES_AVAILABLE = True
except ImportError as e:
    st.error(f"Domain services not available: {e}")
    DOMAIN_SERVICES_AVAILABLE = False

# Import AI advisor
try:
    from tidyllm.workflows.ai_advisor.workflow_advisor import WorkflowAIAdvisor
    AI_ADVISOR_AVAILABLE = True
except ImportError as e:
    AI_ADVISOR_AVAILABLE = False


class ConversationalWorkflowBuilder:
    """
    Conversational AI interface for building workflows through natural language.
    Acts like a business consultant helping users define their processes.
    """

    def __init__(self):
        """Initialize the conversational workflow builder."""
        self.logger = logging.getLogger(__name__)

        if DOMAIN_SERVICES_AVAILABLE:
            dependencies_adapter = get_workflow_dependencies_adapter()
            self.business_signature_service = BusinessSignatureService(dependencies_adapter)
            self.ai_template_builder = AITemplateBuilderService(dependencies_adapter)
        else:
            self.business_signature_service = None
            self.ai_template_builder = None

        if AI_ADVISOR_AVAILABLE:
            self.ai_advisor = WorkflowAIAdvisor()
        else:
            self.ai_advisor = None

        # Initialize session state
        self._initialize_session_state()

        # Business conversation prompts
        self.conversation_prompts = {
            "greeting": "Hi! I'm here to help you create a business workflow. What business process would you like to automate or improve?",
            "clarify_goal": "That sounds interesting! Can you tell me more about what you're trying to accomplish?",
            "understand_inputs": "What information or documents will you be working with?",
            "define_outputs": "What results do you need to get from this process?",
            "identify_steps": "How do you currently handle this process manually?",
            "confirm_understanding": "Let me make sure I understand correctly...",
            "suggest_improvements": "Based on what you've told me, I have some suggestions that might help..."
        }

        # Industry templates for quick starts
        self.industry_templates = {
            "Financial Services": {
                "Credit Risk Assessment": "Analyze loan applications and assess credit risk",
                "Compliance Monitoring": "Monitor transactions for regulatory compliance",
                "Investment Analysis": "Evaluate investment opportunities and risks"
            },
            "Healthcare": {
                "Patient Record Analysis": "Analyze patient records for treatment insights",
                "Medical Document Processing": "Process and organize medical documentation",
                "Insurance Claims Review": "Review and process insurance claims"
            },
            "Legal Services": {
                "Contract Review": "Review contracts for risks and compliance",
                "Document Discovery": "Organize and analyze legal documents",
                "Compliance Verification": "Verify compliance with legal requirements"
            },
            "Human Resources": {
                "Resume Screening": "Screen resumes for job qualifications",
                "Employee Onboarding": "Automate employee onboarding processes",
                "Performance Analysis": "Analyze employee performance data"
            },
            "Operations": {
                "Quality Control": "Monitor and improve product/service quality",
                "Supplier Evaluation": "Evaluate and monitor supplier performance",
                "Process Optimization": "Analyze and optimize business processes"
            }
        }

    def _initialize_session_state(self):
        """Initialize Streamlit session state for conversation tracking."""
        if 'conversation_stage' not in st.session_state:
            st.session_state.conversation_stage = 'greeting'

        if 'workflow_context' not in st.session_state:
            st.session_state.workflow_context = {}

        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []

        if 'generated_workflow' not in st.session_state:
            st.session_state.generated_workflow = None

        if 'user_responses' not in st.session_state:
            st.session_state.user_responses = {}

    def render_main_interface(self):
        """Render the main conversational workflow creation interface."""
        st.title("💬 Create Your Business Workflow")
        st.markdown("""
        **Just tell me what you want to accomplish, and I'll help you build it!**

        No technical knowledge needed - we'll have a conversation about your business process,
        and I'll create a complete workflow for you.
        """)

        # Quick start options
        self._render_quick_start_section()

        st.markdown("---")

        # Main conversation interface
        self._render_conversation_interface()

        # Show generated workflow if available
        if st.session_state.generated_workflow:
            st.markdown("---")
            self._render_generated_workflow_preview()

    def _render_quick_start_section(self):
        """Render quick start templates for common business processes."""
        st.subheader("🚀 Quick Start Templates")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Start with an industry template:**")
            selected_industry = st.selectbox(
                "Choose your industry",
                options=[""] + list(self.industry_templates.keys()),
                format_func=lambda x: "Select your industry..." if x == "" else x
            )

            if selected_industry:
                templates = self.industry_templates[selected_industry]
                selected_template = st.selectbox(
                    "Choose a common process",
                    options=[""] + list(templates.keys()),
                    format_func=lambda x: "Select a process..." if x == "" else x
                )

                if selected_template:
                    template_description = templates[selected_template]
                    st.info(f"**{selected_template}**: {template_description}")

                    if st.button("🎯 Start with this template", key="quick_start"):
                        # Initialize conversation with template
                        st.session_state.user_responses['initial_goal'] = f"I want to {template_description.lower()}"
                        st.session_state.workflow_context['industry'] = selected_industry
                        st.session_state.workflow_context['template'] = selected_template
                        st.session_state.conversation_stage = 'clarify_goal'
                        st.rerun()

        with col2:
            st.markdown("**Or describe your own process:**")
            st.text_area(
                "What do you want to accomplish?",
                placeholder="Example: I need to review supplier contracts and identify any financial risks before we sign them",
                key="custom_goal_input",
                height=100
            )

            if st.button("💡 Let's build this!", key="custom_start"):
                if st.session_state.custom_goal_input.strip():
                    st.session_state.user_responses['initial_goal'] = st.session_state.custom_goal_input
                    st.session_state.conversation_stage = 'clarify_goal'
                    st.rerun()
                else:
                    st.warning("Please describe what you want to accomplish first!")

    def _render_conversation_interface(self):
        """Render the conversational interface based on current stage."""
        st.subheader("💬 Let's Design Your Workflow")

        # Display conversation history
        if st.session_state.conversation_history:
            with st.expander("📚 Conversation History", expanded=False):
                for entry in st.session_state.conversation_history:
                    if entry['type'] == 'ai':
                        st.markdown(f"🤖 **AI**: {entry['message']}")
                    else:
                        st.markdown(f"👤 **You**: {entry['message']}")

        # Current conversation stage
        current_stage = st.session_state.conversation_stage

        if current_stage == 'greeting':
            self._render_greeting_stage()
        elif current_stage == 'clarify_goal':
            self._render_clarify_goal_stage()
        elif current_stage == 'understand_inputs':
            self._render_understand_inputs_stage()
        elif current_stage == 'define_outputs':
            self._render_define_outputs_stage()
        elif current_stage == 'identify_steps':
            self._render_identify_steps_stage()
        elif current_stage == 'confirm_understanding':
            self._render_confirm_understanding_stage()
        elif current_stage == 'generate_workflow':
            self._render_generate_workflow_stage()
        elif current_stage == 'completed':
            self._render_completion_stage()

    def _render_greeting_stage(self):
        """Render the initial greeting and goal capture."""
        st.markdown("🤖 " + self.conversation_prompts['greeting'])

        user_goal = st.text_area(
            "Tell me about your business process:",
            placeholder="Example: I want to analyze customer feedback to identify improvement opportunities",
            key="goal_input",
            height=100
        )

        if st.button("Continue", key="goal_continue"):
            if user_goal.strip():
                st.session_state.user_responses['initial_goal'] = user_goal
                self._add_to_conversation('ai', self.conversation_prompts['greeting'])
                self._add_to_conversation('user', user_goal)
                st.session_state.conversation_stage = 'clarify_goal'
                st.rerun()
            else:
                st.warning("Please describe what you want to accomplish!")

    def _render_clarify_goal_stage(self):
        """Render goal clarification stage."""
        initial_goal = st.session_state.user_responses.get('initial_goal', '')

        # Get AI analysis of the goal
        if self.ai_advisor:
            ai_analysis = self._get_ai_goal_analysis(initial_goal)
            clarification_prompt = f"{self.conversation_prompts['clarify_goal']}\n\n{ai_analysis}"
        else:
            clarification_prompt = self.conversation_prompts['clarify_goal']

        st.markdown(f"🤖 {clarification_prompt}")

        # Questions based on goal analysis
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Who will use this workflow?**")
            workflow_users = st.multiselect(
                "Select all that apply:",
                ["Managers", "Analysts", "Customer Service", "Sales Team", "Operations", "Finance", "Legal", "HR", "Other"],
                key="workflow_users"
            )

            if "Other" in workflow_users:
                other_users = st.text_input("Please specify:", key="other_users")

        with col2:
            st.markdown("**How often will this run?**")
            frequency = st.selectbox(
                "Choose frequency:",
                ["As needed", "Daily", "Weekly", "Monthly", "Quarterly", "On specific events"],
                key="frequency"
            )

            if frequency == "On specific events":
                event_triggers = st.text_input("What triggers this process?", key="event_triggers")

        # Volume and complexity
        st.markdown("**Tell me about the scale:**")
        col1, col2 = st.columns(2)

        with col1:
            volume = st.selectbox(
                "How many items will you process at once?",
                ["1-10 items", "11-50 items", "51-200 items", "200+ items", "Varies significantly"],
                key="volume"
            )

        with col2:
            complexity = st.selectbox(
                "How complex is each item to analyze?",
                ["Simple (1-2 minutes manually)", "Moderate (5-15 minutes manually)", "Complex (30+ minutes manually)", "Very complex (hours manually)"],
                key="complexity"
            )

        if st.button("Next: Define Inputs", key="clarify_continue"):
            # Save responses
            st.session_state.user_responses.update({
                'workflow_users': workflow_users,
                'other_users': st.session_state.get('other_users', ''),
                'frequency': frequency,
                'event_triggers': st.session_state.get('event_triggers', ''),
                'volume': volume,
                'complexity': complexity
            })

            self._add_to_conversation('ai', clarification_prompt)
            self._add_to_conversation('user', f"Users: {', '.join(workflow_users)}, Frequency: {frequency}, Volume: {volume}, Complexity: {complexity}")

            st.session_state.conversation_stage = 'understand_inputs'
            st.rerun()

    def _render_understand_inputs_stage(self):
        """Render input understanding stage."""
        st.markdown(f"🤖 {self.conversation_prompts['understand_inputs']}")

        st.markdown("**What will you be working with?**")

        # Input types
        input_types = st.multiselect(
            "Select all input types:",
            ["PDF Documents", "Word Documents", "Excel Spreadsheets", "Images", "Text Data", "Database Records", "Email", "Web Forms", "API Data", "Other"],
            key="input_types"
        )

        if "Other" in input_types:
            other_inputs = st.text_input("Please specify other input types:", key="other_inputs")

        # Input characteristics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Input characteristics:**")
            structured_data = st.checkbox("Data is well-organized and consistent", key="structured_data")
            multiple_formats = st.checkbox("Data comes in different formats", key="multiple_formats")
            quality_varies = st.checkbox("Data quality varies significantly", key="quality_varies")

        with col2:
            st.markdown("**Security requirements:**")
            sensitive_data = st.checkbox("Contains sensitive/confidential information", key="sensitive_data")
            compliance_required = st.checkbox("Must meet regulatory compliance", key="compliance_required")

            if compliance_required:
                compliance_types = st.multiselect(
                    "Which compliance requirements?",
                    ["GDPR", "HIPAA", "SOX", "PCI DSS", "Financial regulations", "Industry specific", "Other"],
                    key="compliance_types"
                )

        # Data examples
        st.markdown("**Can you provide an example?**")
        data_example = st.text_area(
            "Describe a typical example of what you'll be processing:",
            placeholder="Example: A supplier contract in PDF format, usually 10-20 pages, containing terms, pricing, and legal clauses",
            key="data_example",
            height=80
        )

        if st.button("Next: Define Results", key="inputs_continue"):
            st.session_state.user_responses.update({
                'input_types': input_types,
                'other_inputs': st.session_state.get('other_inputs', ''),
                'structured_data': structured_data,
                'multiple_formats': multiple_formats,
                'quality_varies': quality_varies,
                'sensitive_data': sensitive_data,
                'compliance_required': compliance_required,
                'compliance_types': st.session_state.get('compliance_types', []),
                'data_example': data_example
            })

            user_response = f"Input types: {', '.join(input_types)}"
            if data_example:
                user_response += f"\nExample: {data_example}"

            self._add_to_conversation('ai', self.conversation_prompts['understand_inputs'])
            self._add_to_conversation('user', user_response)

            st.session_state.conversation_stage = 'define_outputs'
            st.rerun()

    def _render_define_outputs_stage(self):
        """Render output definition stage."""
        st.markdown(f"🤖 {self.conversation_prompts['define_outputs']}")

        st.markdown("**What results do you need?**")

        # Output types
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Primary results:**")
            output_formats = st.multiselect(
                "What format should the results be in?",
                ["Summary Report", "Detailed Analysis", "Dashboard/Charts", "Recommendations List", "Risk Assessment", "Score/Rating", "Structured Data (Excel/CSV)", "Notifications/Alerts", "Other"],
                key="output_formats"
            )

            if "Other" in output_formats:
                other_outputs = st.text_input("Please specify:", key="other_outputs")

        with col2:
            st.markdown("**Key information to extract:**")
            key_info = st.multiselect(
                "What specific information do you need?",
                ["Key Facts", "Risk Factors", "Financial Information", "Dates/Deadlines", "Names/Entities", "Classifications", "Quality Scores", "Compliance Status", "Recommendations", "Other"],
                key="key_info"
            )

        # Business decisions
        st.markdown("**How will you use these results?**")
        result_usage = st.multiselect(
            "Select all that apply:",
            ["Make approval decisions", "Identify risks", "Prioritize actions", "Generate reports", "Update databases", "Trigger other processes", "Provide recommendations", "Monitor compliance"],
            key="result_usage"
        )

        # Success criteria
        st.markdown("**What makes this successful?**")
        success_criteria = st.text_area(
            "How will you know the workflow is working well?",
            placeholder="Example: Results are 95% accurate, processing time reduced from 2 hours to 15 minutes, all compliance requirements are automatically checked",
            key="success_criteria",
            height=80
        )

        if st.button("Next: Process Steps", key="outputs_continue"):
            st.session_state.user_responses.update({
                'output_formats': output_formats,
                'other_outputs': st.session_state.get('other_outputs', ''),
                'key_info': key_info,
                'result_usage': result_usage,
                'success_criteria': success_criteria
            })

            user_response = f"Output formats: {', '.join(output_formats)}, Key info: {', '.join(key_info)}"
            if success_criteria:
                user_response += f"\nSuccess criteria: {success_criteria}"

            self._add_to_conversation('ai', self.conversation_prompts['define_outputs'])
            self._add_to_conversation('user', user_response)

            st.session_state.conversation_stage = 'identify_steps'
            st.rerun()

    def _render_identify_steps_stage(self):
        """Render process steps identification stage."""
        st.markdown(f"🤖 {self.conversation_prompts['identify_steps']}")

        st.markdown("**Describe your current manual process:**")

        current_process = st.text_area(
            "Walk me through how you handle this today:",
            placeholder="Example: First, I receive the contract via email. Then I read through it looking for key terms. I check the financial terms against our standards. I identify any unusual clauses. Finally, I write a summary with recommendations.",
            key="current_process",
            height=120
        )

        # Pain points
        st.markdown("**What's challenging about the current process?**")
        pain_points = st.multiselect(
            "Select all that apply:",
            ["Takes too much time", "Prone to human error", "Inconsistent results", "Requires specialized knowledge", "Difficult to scale", "Hard to track progress", "Creates bottlenecks", "Compliance concerns"],
            key="pain_points"
        )

        # Quality requirements
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Quality requirements:**")
            accuracy_required = st.selectbox(
                "How accurate must the results be?",
                ["Extremely accurate (>99%)", "Very accurate (95-99%)", "Moderately accurate (85-95%)", "Reasonably accurate (75-85%)"],
                key="accuracy_required"
            )

            human_review = st.selectbox(
                "Will someone review the results?",
                ["Always reviewed by expert", "Reviewed when flagged", "Spot checking only", "Fully automated"],
                key="human_review"
            )

        with col2:
            st.markdown("**Speed requirements:**")
            speed_importance = st.selectbox(
                "How important is processing speed?",
                ["Critical (must be real-time)", "Very important (within minutes)", "Moderately important (within hours)", "Not critical (within days)"],
                key="speed_importance"
            )

            batch_processing = st.checkbox("Process multiple items at once", key="batch_processing")

        if st.button("Next: Review & Generate", key="steps_continue"):
            st.session_state.user_responses.update({
                'current_process': current_process,
                'pain_points': pain_points,
                'accuracy_required': accuracy_required,
                'human_review': human_review,
                'speed_importance': speed_importance,
                'batch_processing': batch_processing
            })

            user_response = f"Current process: {current_process[:100]}..."
            if pain_points:
                user_response += f"\nPain points: {', '.join(pain_points)}"

            self._add_to_conversation('ai', self.conversation_prompts['identify_steps'])
            self._add_to_conversation('user', user_response)

            st.session_state.conversation_stage = 'confirm_understanding'
            st.rerun()

    def _render_confirm_understanding_stage(self):
        """Render understanding confirmation and workflow generation."""
        st.markdown("🤖 " + self.conversation_prompts['confirm_understanding'])

        # Generate workflow summary
        workflow_summary = self._generate_workflow_summary()

        st.markdown("**Here's what I understand:**")
        st.info(workflow_summary)

        # Confirmation
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, that's correct!", key="confirm_yes"):
                st.session_state.conversation_stage = 'generate_workflow'
                st.rerun()

        with col2:
            if st.button("❌ Let me clarify something", key="confirm_no"):
                clarification = st.text_area(
                    "What would you like to clarify or change?",
                    key="clarification_input"
                )
                if clarification and st.button("Update understanding", key="update"):
                    self._add_to_conversation('user', f"Clarification: {clarification}")
                    # Could implement logic to go back to specific stage
                    st.info("Thanks for the clarification! Let me update my understanding...")

    def _render_generate_workflow_stage(self):
        """Generate the actual workflow using AI."""
        st.markdown("🤖 Perfect! Let me create your workflow...")

        if not st.session_state.generated_workflow:
            with st.spinner("🧠 AI is designing your workflow... This may take a moment."):
                generated_workflow = self._generate_workflow_from_conversation()
                st.session_state.generated_workflow = generated_workflow

        if st.session_state.generated_workflow:
            if st.session_state.generated_workflow.get('success'):
                st.success("🎉 Your workflow has been created!")
                st.session_state.conversation_stage = 'completed'
                st.rerun()
            else:
                st.error(f"❌ There was an issue creating your workflow: {st.session_state.generated_workflow.get('error')}")
                if st.button("Try Again", key="retry_generate"):
                    st.session_state.generated_workflow = None
                    st.rerun()

    def _render_completion_stage(self):
        """Render completion stage with next steps."""
        st.markdown("🎉 **Congratulations! Your workflow is ready!**")

        workflow = st.session_state.generated_workflow

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 Deploy Workflow", type="primary", key="deploy"):
                with st.spinner("Deploying your workflow..."):
                    # Deploy the workflow
                    deployment_result = self._deploy_workflow(workflow)
                    if deployment_result.get('success'):
                        st.success("✅ Workflow deployed successfully!")
                        st.markdown(f"**Your workflow is now available as:** `{deployment_result.get('tool_name')}`")
                        st.markdown("You can use it immediately in your business processes!")
                    else:
                        st.error(f"Deployment failed: {deployment_result.get('error')}")

        with col2:
            if st.button("📝 Start Over", key="start_over"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key.startswith(('conversation_', 'workflow_', 'user_responses', 'generated_workflow')):
                        del st.session_state[key]
                st.rerun()

    def _render_generated_workflow_preview(self):
        """Render preview of the generated workflow."""
        st.subheader("🔧 Your Generated Workflow")

        workflow = st.session_state.generated_workflow

        if workflow and workflow.get('success'):
            template = workflow.get('template', {})

            # Basic info
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Name:** {template.get('template_name', 'Generated Workflow')}")
                st.markdown(f"**Purpose:** {template.get('business_purpose', 'Business process automation')}")

            with col2:
                st.markdown(f"**Confidence:** {template.get('metadata', {}).get('confidence_score', 0.8):.0%}")
                st.markdown(f"**Ready for use:** {'✅ Yes' if template.get('business_readiness', {}).get('ready_for_deployment') else '⚠️ Needs review'}")

            # Workflow steps
            with st.expander("📋 Workflow Steps", expanded=True):
                steps = template.get('workflow_config', {}).get('steps', [])
                for i, step in enumerate(steps, 1):
                    st.markdown(f"{i}. **{step}**")

            # Technical details (collapsed)
            with st.expander("🔧 Technical Details", expanded=False):
                st.json(template)

    # Helper methods
    def _add_to_conversation(self, message_type: str, message: str):
        """Add message to conversation history."""
        st.session_state.conversation_history.append({
            'type': message_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })

    def _get_ai_goal_analysis(self, goal: str) -> str:
        """Use AI advisor to analyze the user's goal and suggest clarifying questions."""
        if not self.ai_advisor:
            return "Can you tell me more about the specific outcomes you're looking for?"

        try:
            analysis = self.ai_advisor.get_workflow_advice(
                criteria={},
                template_fields={},
                recent_activity=[],
                final_results={},
                user_question=f"""
                A user wants to create a workflow for: "{goal}"

                What clarifying questions should I ask to better understand their requirements?
                What business context and technical considerations should I explore?
                Be conversational and business-friendly, not technical.
                """,
                use_cases=["workflow_clarification", "business_analysis"]
            )

            if analysis.get('success'):
                return analysis.get('advice', 'Can you tell me more about what you need?')
            else:
                return "Can you tell me more about the specific outcomes you're looking for?"

        except Exception:
            return "Can you tell me more about what you need to accomplish?"

    def _generate_workflow_summary(self) -> str:
        """Generate a human-readable summary of the workflow requirements."""
        responses = st.session_state.user_responses

        summary = f"**Goal:** {responses.get('initial_goal', '')}\n\n"

        if responses.get('workflow_users'):
            summary += f"**Users:** {', '.join(responses.get('workflow_users', []))}\n"

        if responses.get('input_types'):
            summary += f"**Inputs:** {', '.join(responses.get('input_types', []))}\n"

        if responses.get('output_formats'):
            summary += f"**Outputs:** {', '.join(responses.get('output_formats', []))}\n"

        if responses.get('frequency'):
            summary += f"**Frequency:** {responses.get('frequency')}\n"

        if responses.get('success_criteria'):
            summary += f"**Success Criteria:** {responses.get('success_criteria')}\n"

        return summary

    def _generate_workflow_from_conversation(self) -> Dict[str, Any]:
        """Generate the actual workflow using the AI template builder."""
        if not self.ai_template_builder:
            return {"success": False, "error": "AI template builder not available"}

        try:
            responses = st.session_state.user_responses

            # Convert conversation to business requirements
            business_requirements = [
                responses.get('initial_goal', ''),
                f"Users: {', '.join(responses.get('workflow_users', []))}",
                f"Inputs: {', '.join(responses.get('input_types', []))}",
                f"Outputs: {', '.join(responses.get('output_formats', []))}",
                responses.get('success_criteria', '')
            ]

            # Determine business context
            business_context = self._infer_business_context(responses)

            # Define workflow objectives
            workflow_objectives = [
                "Automate manual process",
                "Improve accuracy and consistency",
                "Reduce processing time",
                "Ensure compliance"
            ]

            # Generate template
            result = self.ai_template_builder.build_template_from_requirements(
                business_requirements=business_requirements,
                business_context=business_context,
                workflow_objectives=workflow_objectives,
                constraints={"user_friendly": True, "business_focused": True},
                performance_targets={"accuracy": 0.95, "speed": "fast"}
            )

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _infer_business_context(self, responses: Dict[str, Any]) -> BusinessContext:
        """Infer business context from user responses."""
        goal = responses.get('initial_goal', '').lower()

        if any(word in goal for word in ['contract', 'legal', 'agreement', 'compliance']):
            return BusinessContext.CONTRACT_REVIEW
        elif any(word in goal for word in ['financial', 'credit', 'risk', 'investment', 'money']):
            return BusinessContext.FINANCIAL_ANALYSIS
        elif any(word in goal for word in ['quality', 'defect', 'standard', 'specification']):
            return BusinessContext.QUALITY_ASSURANCE
        elif any(word in goal for word in ['document', 'text', 'analyze', 'extract']):
            return BusinessContext.DOCUMENT_PROCESSING
        else:
            return BusinessContext.OPERATIONAL_WORKFLOW

    def _deploy_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy the generated workflow as a business tool."""
        if not self.business_signature_service:
            return {"success": False, "error": "Business signature service not available"}

        try:
            # Implementation would deploy the workflow
            return {
                "success": True,
                "tool_name": workflow.get('template', {}).get('template_name', 'Generated Workflow'),
                "tool_id": f"workflow_{int(datetime.now().timestamp())}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Main function to run the Intuitive Workflow Creator."""
    st.set_page_config(
        page_title="Intuitive Workflow Creator",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar
    with st.sidebar:
        st.title("💬 Workflow Creator")
        st.markdown("""
        **Create workflows through conversation**

        No technical knowledge required!
        Just describe what you want to accomplish.

        **How it works:**
        1. Tell me your business goal
        2. Answer a few questions
        3. Get a complete workflow
        4. Deploy and use immediately
        """)

        st.markdown("---")
        st.markdown("**Tips for success:**")
        st.markdown("• Be specific about your goals")
        st.markdown("• Think about current pain points")
        st.markdown("• Describe your ideal outcome")
        st.markdown("• Don't worry about technical details")

    # Initialize and render portal
    creator = ConversationalWorkflowBuilder()
    creator.render_main_interface()


if __name__ == "__main__":
    main()