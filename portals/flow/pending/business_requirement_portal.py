"""
Business Requirement Capture Portal
===================================
Portal for capturing business requirements and converting them to DSPy signatures.
This addresses the question: "Is it the business requirements or the process?"

Focus: DOMAIN-DRIVEN business requirement capture, not technical implementation.
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
        BusinessContext,
        BusinessRequirement
    )
    from domain.services.workflow_service import WorkflowService
    from adapters.secondary.workflow.workflow_dependencies_adapter import get_workflow_dependencies_adapter
    DOMAIN_SERVICES_AVAILABLE = True
except ImportError as e:
    st.error(f"Domain services not available: {e}")
    DOMAIN_SERVICES_AVAILABLE = False


class BusinessRequirementPortal:
    """Portal for capturing and managing business requirements."""

    def __init__(self):
        """Initialize the business requirement portal."""
        self.logger = logging.getLogger(__name__)

        if DOMAIN_SERVICES_AVAILABLE:
            # Initialize domain services
            dependencies_adapter = get_workflow_dependencies_adapter()
            self.workflow_service = WorkflowService(dependencies_adapter)
            self.business_signature_service = BusinessSignatureService(dependencies_adapter)
        else:
            self.workflow_service = None
            self.business_signature_service = None

        # Initialize session state
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'current_requirement' not in st.session_state:
            st.session_state.current_requirement = None

        if 'captured_requirements' not in st.session_state:
            st.session_state.captured_requirements = []

        if 'generated_signatures' not in st.session_state:
            st.session_state.generated_signatures = []

    def render_main_interface(self):
        """Render the main business requirement capture interface."""
        st.title("🏢 Business Requirement Capture")
        st.markdown("""
        **Transform business questions into executable DSPy signatures**

        Focus on **WHAT** your business needs, not **HOW** it should be implemented.
        """)

        if not DOMAIN_SERVICES_AVAILABLE:
            st.error("⚠️ Domain services are not available. Please check your configuration.")
            return

        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Capture Requirements",
            "🔧 Generate Signatures",
            "📊 Review & Deploy",
            "🗂️ Manage Business Tools"
        ])

        with tab1:
            self._render_requirement_capture()

        with tab2:
            self._render_signature_generation()

        with tab3:
            self._render_review_and_deploy()

        with tab4:
            self._render_business_tools_management()

    def _render_requirement_capture(self):
        """Render the business requirement capture form."""
        st.header("📋 Capture Business Requirements")

        st.markdown("""
        **Start with your business question or need. Focus on domain concepts and business outcomes.**
        """)

        # Business Question Input
        st.subheader("1. What is your core business question?")
        business_question = st.text_area(
            "Describe what you need to accomplish from a business perspective",
            placeholder="Example: How do I determine if a contract poses financial risk to our organization?",
            height=100,
            help="Focus on the business outcome you want to achieve, not the technical process"
        )

        # Business Context Selection
        st.subheader("2. What is your business domain?")
        col1, col2 = st.columns(2)

        with col1:
            business_context = st.selectbox(
                "Select your business context",
                options=[context.value for context in BusinessContext],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Choose the business area that best describes your need"
            )

        with col2:
            requirement_type = st.selectbox(
                "What type of business requirement is this?",
                options=[req_type.value for req_type in BusinessRequirementType],
                format_func=lambda x: x.replace("_", " ").title(),
                help="Select the type of business process you need"
            )

        # Business Stakeholder Input
        st.subheader("3. Business Requirements Details")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Success Criteria**")
            success_criteria = st.text_area(
                "How will you measure business success?",
                placeholder="Example:\n• Identify risks with 90% accuracy\n• Provide actionable recommendations\n• Complete analysis within 2 minutes",
                height=120,
                help="Define what successful business outcomes look like"
            )

            st.markdown("**Business Rules & Constraints**")
            business_rules = st.text_area(
                "What business rules must be followed?",
                placeholder="Example:\n• Must comply with SOX regulations\n• Requires CFO approval for high-risk items\n• All decisions must be auditable",
                height=120,
                help="List any business rules, regulations, or constraints"
            )

        with col2:
            st.markdown("**Stakeholder Requirements**")
            stakeholder_requirements = st.text_area(
                "Who will use this and what do they need?",
                placeholder="Example:\n• Legal team needs risk assessment\n• Finance team needs cost impact\n• Management needs executive summary",
                height=120,
                help="Describe who will use this and their specific needs"
            )

            st.markdown("**Business Inputs Available**")
            business_inputs = st.text_area(
                "What business information do you have?",
                placeholder="Example:\n• Contract documents (PDF)\n• Company financial data\n• Historical risk assessments\n• Industry benchmarks",
                height=120,
                help="List the business information and data you can provide"
            )

        # Expected Business Outcomes
        st.subheader("4. Expected Business Outcomes")
        business_outcomes = st.text_area(
            "What specific business outputs do you need?",
            placeholder="Example:\n• Risk score (High/Medium/Low)\n• List of identified risk factors\n• Recommended contract modifications\n• Estimated financial impact",
            height=100,
            help="Describe exactly what business results you expect"
        )

        # Compliance Requirements
        st.subheader("5. Compliance & Regulatory Requirements")
        compliance_requirements = st.text_area(
            "Are there any compliance or regulatory requirements?",
            placeholder="Example:\n• GDPR compliance for data handling\n• SOX compliance for financial assessments\n• Industry-specific regulations",
            height=80,
            help="List any compliance requirements that must be met"
        )

        # Capture Button
        st.markdown("---")

        if st.button("📥 Capture Business Requirement", type="primary", use_container_width=True):
            if not business_question.strip():
                st.error("Please provide a business question.")
                return

            try:
                # Parse the business inputs
                stakeholder_input = {
                    "success_metrics": [line.strip("• -") for line in success_criteria.split("\n") if line.strip()],
                    "business_rules": [{"description": line.strip("• -"), "enforcement": "required"}
                                     for line in business_rules.split("\n") if line.strip()],
                    "stakeholder_requirements": [line.strip("• -") for line in stakeholder_requirements.split("\n") if line.strip()],
                    "required_inputs": self._parse_business_inputs(business_inputs),
                    "expected_outputs": self._parse_business_outputs(business_outcomes),
                    "compliance_requirements": [line.strip("• -") for line in compliance_requirements.split("\n") if line.strip()]
                }

                # Capture the business requirement
                requirement = self.business_signature_service.capture_business_requirement(
                    business_question=business_question.strip(),
                    requirement_type=BusinessRequirementType(requirement_type),
                    business_context=BusinessContext(business_context),
                    stakeholder_input=stakeholder_input
                )

                # Store in session state
                st.session_state.current_requirement = requirement
                st.session_state.captured_requirements.append(requirement)

                st.success(f"✅ Business requirement captured successfully!")
                st.info(f"**Requirement ID:** {requirement.requirement_id}")

                # Show captured requirement summary
                with st.expander("📋 View Captured Requirement", expanded=True):
                    self._display_requirement_summary(requirement)

            except Exception as e:
                st.error(f"❌ Failed to capture business requirement: {str(e)}")
                self.logger.error(f"Requirement capture failed: {e}")

    def _parse_business_inputs(self, inputs_text: str) -> Dict[str, str]:
        """Parse business inputs from text into structured format."""
        inputs = {}
        for line in inputs_text.split("\n"):
            line = line.strip("• -").strip()
            if line:
                # Simple parsing - could be enhanced with NLP
                if "(" in line and ")" in line:
                    name = line.split("(")[0].strip()
                    description = line
                else:
                    name = line.lower().replace(" ", "_")
                    description = line
                inputs[name] = description
        return inputs

    def _parse_business_outputs(self, outputs_text: str) -> Dict[str, str]:
        """Parse business outputs from text into structured format."""
        outputs = {}
        for line in outputs_text.split("\n"):
            line = line.strip("• -").strip()
            if line:
                if "(" in line and ")" in line:
                    name = line.split("(")[0].strip()
                    description = line
                else:
                    name = line.lower().replace(" ", "_")
                    description = line
                outputs[name] = description
        return outputs

    def _display_requirement_summary(self, requirement: BusinessRequirement):
        """Display a summary of the captured business requirement."""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Business Question:** {requirement.business_question}")
            st.markdown(f"**Domain:** {requirement.business_context.value.replace('_', ' ').title()}")
            st.markdown(f"**Type:** {requirement.requirement_type.value.replace('_', ' ').title()}")

        with col2:
            st.markdown(f"**Requirement ID:** {requirement.requirement_id}")
            st.markdown(f"**Created:** {requirement.created_at.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Success Criteria:** {len(requirement.success_criteria)} items")

        if requirement.business_rules:
            st.markdown("**Business Rules:**")
            for rule in requirement.business_rules:
                st.markdown(f"• {rule.get('description', 'Business rule')}")

    def _render_signature_generation(self):
        """Render the DSPy signature generation interface."""
        st.header("🔧 Generate Business Signatures")

        if not st.session_state.captured_requirements:
            st.info("📝 Please capture a business requirement first in the 'Capture Requirements' tab.")
            return

        st.markdown("**Convert your business requirements into executable DSPy signatures.**")

        # Select requirement to generate signature for
        requirement_options = {
            f"{req.requirement_id}: {req.business_question[:50]}...": req
            for req in st.session_state.captured_requirements
        }

        selected_req_key = st.selectbox(
            "Select a business requirement to generate signature for:",
            options=list(requirement_options.keys()),
            help="Choose which business requirement you want to convert to a DSPy signature"
        )

        if selected_req_key:
            selected_requirement = requirement_options[selected_req_key]

            # Display requirement details
            with st.expander("📋 Business Requirement Details", expanded=False):
                self._display_requirement_summary(selected_requirement)

            st.markdown("---")

            # Generation options
            st.subheader("🎯 Signature Generation Options")

            col1, col2 = st.columns(2)

            with col1:
                include_validation = st.checkbox(
                    "Include business validation rules",
                    value=True,
                    help="Include validation logic based on business rules"
                )

                include_testing = st.checkbox(
                    "Generate business test scenarios",
                    value=True,
                    help="Create test scenarios based on business requirements"
                )

            with col2:
                optimize_for_domain = st.checkbox(
                    "Optimize for domain vocabulary",
                    value=True,
                    help="Use domain-specific terminology and concepts"
                )

                include_compliance = st.checkbox(
                    "Include compliance checks",
                    value=True,
                    help="Add compliance validation based on requirements"
                )

            # Generate signature button
            if st.button("🚀 Generate Business Signature", type="primary", use_container_width=True):
                try:
                    with st.spinner("🔄 Generating business signature from domain requirements..."):
                        # Generate the business signature
                        business_signature = self.business_signature_service.generate_business_signature(
                            selected_requirement
                        )

                        # Store in session state
                        st.session_state.generated_signatures.append(business_signature)

                        st.success("✅ Business signature generated successfully!")

                        # Display the generated signature
                        self._display_generated_signature(business_signature)

                except Exception as e:
                    st.error(f"❌ Failed to generate business signature: {str(e)}")
                    self.logger.error(f"Signature generation failed: {e}")

        # Display previously generated signatures
        if st.session_state.generated_signatures:
            st.markdown("---")
            st.subheader("📚 Previously Generated Signatures")

            for i, signature in enumerate(st.session_state.generated_signatures):
                with st.expander(f"🔧 {signature.signature_name}", expanded=False):
                    self._display_generated_signature(signature, show_code=False)

    def _display_generated_signature(self, signature, show_code: bool = True):
        """Display details of a generated business signature."""
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Signature Name:** {signature.signature_name}")
            st.markdown(f"**Signature ID:** {signature.signature_id}")
            st.markdown(f"**Created:** {signature.created_at.strftime('%Y-%m-%d %H:%M')}")

        with col2:
            st.markdown(f"**Business Context:** {signature.business_requirement.business_context.value.replace('_', ' ').title()}")
            st.markdown(f"**Requirement Type:** {signature.business_requirement.requirement_type.value.replace('_', ' ').title()}")

        # Business purpose
        st.markdown("**Business Purpose:**")
        st.text_area("", value=signature.business_purpose, height=100, disabled=True, key=f"purpose_{signature.signature_id}")

        # Inputs and Outputs
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Business Inputs:**")
            for input_name, input_desc in signature.domain_inputs.items():
                st.markdown(f"• **{input_name}**: {input_desc}")

        with col2:
            st.markdown("**Business Outputs:**")
            for output_name, output_desc in signature.domain_outputs.items():
                st.markdown(f"• **{output_name}**: {output_desc}")

        # Business logic description
        st.markdown("**Business Logic:**")
        st.text_area("", value=signature.business_logic_description, height=120, disabled=True, key=f"logic_{signature.signature_id}")

        # Validation rules
        if signature.validation_rules:
            st.markdown("**Validation Rules:**")
            for rule in signature.validation_rules:
                st.markdown(f"• {rule}")

        # Generated DSPy code
        if show_code:
            st.markdown("**Generated DSPy Signature Code:**")
            st.code(signature.signature_template, language="python")

    def _render_review_and_deploy(self):
        """Render the signature review and deployment interface."""
        st.header("📊 Review & Deploy Business Signatures")

        if not st.session_state.generated_signatures:
            st.info("🔧 Please generate a business signature first in the 'Generate Signatures' tab.")
            return

        st.markdown("**Review generated signatures and deploy them as business tools.**")

        # Select signature to review
        signature_options = {
            f"{sig.signature_name} ({sig.signature_id})": sig
            for sig in st.session_state.generated_signatures
        }

        selected_sig_key = st.selectbox(
            "Select a signature to review and deploy:",
            options=list(signature_options.keys()),
            help="Choose which signature you want to review and deploy"
        )

        if selected_sig_key:
            selected_signature = signature_options[selected_sig_key]

            # Display signature details
            st.subheader("📋 Signature Review")
            self._display_generated_signature(selected_signature)

            st.markdown("---")

            # Business validation
            st.subheader("✅ Business Validation")

            col1, col2 = st.columns(2)

            with col1:
                business_approved = st.checkbox(
                    "Business stakeholders approve this signature",
                    help="Confirm that business stakeholders have reviewed and approved"
                )

                domain_validated = st.checkbox(
                    "Domain experts have validated the business logic",
                    help="Confirm that domain experts have reviewed the business logic"
                )

            with col2:
                compliance_checked = st.checkbox(
                    "Compliance requirements are met",
                    help="Confirm that all compliance requirements are satisfied"
                )

                testing_completed = st.checkbox(
                    "Business testing scenarios have been validated",
                    help="Confirm that test scenarios accurately reflect business needs"
                )

            # Deployment options
            st.subheader("🚀 Deployment Configuration")

            deployment_name = st.text_input(
                "Business Tool Name",
                value=selected_signature.signature_name,
                help="Name that will appear in business workflows"
            )

            deployment_description = st.text_area(
                "Business Tool Description",
                value=f"Business tool for {selected_signature.business_requirement.business_question}",
                help="Description that business users will see"
            )

            # Deploy button
            all_validations = business_approved and domain_validated and compliance_checked and testing_completed

            if st.button(
                "🌟 Deploy as Business Tool",
                type="primary",
                disabled=not all_validations,
                use_container_width=True
            ):
                if not all_validations:
                    st.error("❌ Please complete all business validations before deployment.")
                    return

                try:
                    with st.spinner("🚀 Deploying business signature as workflow tool..."):
                        # Deploy the signature as a business tool
                        deployment_result = self.business_signature_service.deploy_business_signature_as_tool(
                            selected_signature.signature_id
                        )

                        if deployment_result.get("success"):
                            st.success(f"✅ Successfully deployed '{deployment_name}' as a business tool!")
                            st.info(f"**Tool ID:** {deployment_result.get('tool_id')}")

                            # Show integration instructions
                            with st.expander("📖 Business Integration Instructions", expanded=True):
                                st.markdown(f"""
                                **Your business tool is now available in workflows!**

                                **Tool Name:** {deployment_name}
                                **Tool ID:** {deployment_result.get('tool_id')}

                                **How to use in Flow Macros:**
                                ```
                                [BUSINESS_TOOL:{deployment_result.get('tool_id')}] input_document.pdf
                                ```

                                **Business stakeholders can now:**
                                • Use this tool in their workflow processes
                                • Access it through the Flow Creator interface
                                • Include it in automated business workflows
                                • Monitor its performance through business metrics
                                """)
                        else:
                            st.error(f"❌ Deployment failed: {deployment_result.get('error')}")

                except Exception as e:
                    st.error(f"❌ Deployment failed: {str(e)}")
                    self.logger.error(f"Deployment failed: {e}")

            if not all_validations:
                st.warning("⚠️ Complete all business validations to enable deployment.")

    def _render_business_tools_management(self):
        """Render the business tools management interface."""
        st.header("🗂️ Manage Business Tools")

        st.markdown("**View and manage deployed business tools and signatures.**")

        try:
            # Get list of business signatures
            business_signatures = self.business_signature_service.list_business_signatures()

            if business_signatures:
                st.subheader("📚 Business Signature Library")

                for sig_data in business_signatures:
                    with st.expander(f"🔧 {sig_data.get('signature_name', 'Unnamed Signature')}", expanded=False):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"**Signature ID:** {sig_data.get('signature_id', 'N/A')}")
                            st.markdown(f"**Business Context:** {sig_data.get('business_context', 'N/A')}")
                            st.markdown(f"**Created:** {sig_data.get('created_at', 'N/A')}")

                        with col2:
                            st.markdown(f"**Status:** {sig_data.get('status', 'Available')}")
                            st.markdown(f"**Usage Count:** {sig_data.get('usage_count', 0)}")

                            if st.button(f"🔍 View Details", key=f"view_{sig_data.get('signature_id')}"):
                                # Load and display full signature details
                                pass
            else:
                st.info("📝 No business signatures found. Create some in the previous tabs!")

        except Exception as e:
            st.error(f"❌ Failed to load business tools: {str(e)}")
            self.logger.error(f"Business tools loading failed: {e}")

        # Business metrics section
        st.markdown("---")
        st.subheader("📈 Business Tool Performance")

        # Placeholder for metrics - would be populated from monitoring service
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Business Tools", "0", delta="0")

        with col2:
            st.metric("Active Deployments", "0", delta="0")

        with col3:
            st.metric("Business Success Rate", "0%", delta="0%")

        with col4:
            st.metric("Stakeholder Satisfaction", "0%", delta="0%")


def main():
    """Main function to run the Business Requirement Portal."""
    st.set_page_config(
        page_title="Business Requirement Capture",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar
    with st.sidebar:
        st.title("🏢 Business Focus")
        st.markdown("""
        **Domain-Driven Signature Creation**

        This portal focuses on:
        • Business requirements over technical implementation
        • Domain vocabulary and concepts
        • Stakeholder needs and outcomes
        • Business value and compliance

        **Question:** "Is it the business requirements or the process?"
        **Answer:** Focus on business requirements first, then generate the process.
        """)

        st.markdown("---")
        st.markdown("**Quick Help:**")
        st.markdown("• Start with your business question")
        st.markdown("• Use business language, not technical jargon")
        st.markdown("• Focus on outcomes, not implementation")
        st.markdown("• Include stakeholder perspectives")

    # Initialize and render portal
    portal = BusinessRequirementPortal()
    portal.render_main_interface()


if __name__ == "__main__":
    main()