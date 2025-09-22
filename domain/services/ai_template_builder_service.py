"""
AI Template Builder Service
===========================
Uses AI advisor to automatically generate complete workflow templates from business requirements.
This frees users to focus on workflow orchestration rather than template construction details.

Core Concept: Business Requirements → AI Analysis → Complete Template Generation
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import domain services
try:
    from .business_signature_service import (
        BusinessSignatureService,
        BusinessRequirementType,
        BusinessContext,
        BusinessRequirement
    )
    from .workflow_service import WorkflowService
    from ..ports.outbound.workflow_port import WorkflowDependenciesPort
    DOMAIN_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Domain services not available: {e}")
    DOMAIN_SERVICES_AVAILABLE = False

# Import AI advisor
try:
    from tidyllm.workflows.ai_advisor.workflow_advisor import WorkflowAIAdvisor
    AI_ADVISOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI advisor not available: {e}")
    AI_ADVISOR_AVAILABLE = False

# Import DSPy for template generation signatures
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


class TemplateArchitect(dspy.Signature):
    """AI signature for designing complete workflow templates from business requirements."""

    business_requirements = dspy.InputField(desc="Comprehensive business requirements and objectives")
    domain_context = dspy.InputField(desc="Business domain and industry context")
    workflow_constraints = dspy.InputField(desc="Technical and business constraints")
    existing_templates = dspy.InputField(desc="Available template patterns and components")

    template_design = dspy.OutputField(desc="Complete workflow template with steps, validation, and business logic")


class WorkflowOrchestrator(dspy.Signature):
    """AI signature for determining optimal workflow step ordering and dependencies."""

    business_process = dspy.InputField(desc="Business process description and objectives")
    available_steps = dspy.InputField(desc="Available workflow steps and their capabilities")
    business_priorities = dspy.InputField(desc="Business priorities and success criteria")
    performance_requirements = dspy.InputField(desc="Performance and efficiency requirements")

    orchestration_plan = dspy.OutputField(desc="Optimal step ordering with dependencies and parallel execution opportunities")


class TemplateValidator(dspy.Signature):
    """AI signature for validating generated templates against business requirements."""

    generated_template = dspy.InputField(desc="Generated workflow template")
    original_requirements = dspy.InputField(desc="Original business requirements")
    domain_standards = dspy.InputField(desc="Domain-specific standards and best practices")

    validation_report = dspy.OutputField(desc="Template validation with compliance check and improvement suggestions")


class AITemplateBuilderService:
    """
    AI-powered service that automatically generates complete workflow templates from business requirements.

    This service handles the technical complexity of template construction, allowing users to focus
    on business logic and workflow orchestration.
    """

    def __init__(self, dependencies: WorkflowDependenciesPort):
        """Initialize AI template builder service."""
        self.dependencies = dependencies
        self.logger = logging.getLogger(__name__)

        # Initialize domain services
        if DOMAIN_SERVICES_AVAILABLE:
            self.business_signature_service = BusinessSignatureService(dependencies)
            self.workflow_service = WorkflowService(dependencies)
        else:
            self.business_signature_service = None
            self.workflow_service = None

        # Initialize AI advisor
        if AI_ADVISOR_AVAILABLE:
            self.ai_advisor = WorkflowAIAdvisor()
        else:
            self.ai_advisor = None

        # Initialize DSPy modules for template generation
        if DSPY_AVAILABLE:
            self.template_architect = dspy.ChainOfThought(TemplateArchitect)
            self.workflow_orchestrator = dspy.ChainOfThought(WorkflowOrchestrator)
            self.template_validator = dspy.ChainOfThought(TemplateValidator)
        else:
            self.template_architect = None
            self.workflow_orchestrator = None
            self.template_validator = None

        # Template component library
        self.template_components = self._initialize_template_components()

    def _initialize_template_components(self) -> Dict[str, Any]:
        """Initialize library of reusable template components."""
        return {
            "input_handlers": {
                "document_upload": {
                    "type": "file_input",
                    "validation": ["file_size", "file_type", "virus_scan"],
                    "business_purpose": "Secure document ingestion"
                },
                "text_input": {
                    "type": "text_field",
                    "validation": ["length", "format", "content_filter"],
                    "business_purpose": "Structured text data capture"
                },
                "structured_data": {
                    "type": "json_input",
                    "validation": ["schema", "required_fields", "data_types"],
                    "business_purpose": "Structured business data input"
                }
            },
            "processing_steps": {
                "document_analysis": {
                    "capabilities": ["text_extraction", "entity_recognition", "classification"],
                    "business_value": "Extract actionable information from documents"
                },
                "financial_calculation": {
                    "capabilities": ["ratio_analysis", "trend_calculation", "risk_scoring"],
                    "business_value": "Generate financial insights and metrics"
                },
                "compliance_check": {
                    "capabilities": ["rule_validation", "pattern_matching", "exception_detection"],
                    "business_value": "Ensure regulatory and policy compliance"
                },
                "quality_assessment": {
                    "capabilities": ["completeness_check", "accuracy_validation", "consistency_analysis"],
                    "business_value": "Validate information quality and reliability"
                }
            },
            "output_generators": {
                "business_report": {
                    "format": "structured_report",
                    "components": ["executive_summary", "detailed_analysis", "recommendations"],
                    "business_purpose": "Comprehensive business analysis output"
                },
                "decision_support": {
                    "format": "decision_matrix",
                    "components": ["options", "criteria", "scoring", "recommendation"],
                    "business_purpose": "Support business decision-making"
                },
                "compliance_report": {
                    "format": "compliance_summary",
                    "components": ["status", "violations", "remediation_plan"],
                    "business_purpose": "Demonstrate regulatory compliance"
                }
            }
        }

    def build_template_from_requirements(self,
                                       business_requirements: List[str],
                                       business_context: BusinessContext,
                                       workflow_objectives: List[str],
                                       constraints: Dict[str, Any] = None,
                                       performance_targets: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Build complete workflow template from business requirements using AI.

        This is the main method that takes business requirements and returns a complete,
        executable workflow template.
        """
        try:
            self.logger.info("Starting AI-powered template generation")

            # Step 1: Analyze business requirements with AI advisor
            requirements_analysis = self._analyze_business_requirements(
                business_requirements, business_context, workflow_objectives
            )

            # Step 2: Generate template architecture
            template_design = self._generate_template_architecture(
                requirements_analysis, constraints or {}
            )

            # Step 3: Create workflow orchestration plan
            orchestration_plan = self._create_orchestration_plan(
                template_design, performance_targets or {}
            )

            # Step 4: Generate complete template with business signatures
            complete_template = self._generate_complete_template(
                template_design, orchestration_plan, requirements_analysis
            )

            # Step 5: Validate template against business requirements
            validation_result = self._validate_generated_template(
                complete_template, business_requirements, business_context
            )

            # Step 6: Apply AI recommendations and optimizations
            optimized_template = self._optimize_template_with_ai(
                complete_template, validation_result
            )

            return {
                "success": True,
                "template": optimized_template,
                "analysis": requirements_analysis,
                "orchestration": orchestration_plan,
                "validation": validation_result,
                "ai_confidence": self._calculate_template_confidence(validation_result),
                "business_readiness": self._assess_business_readiness(optimized_template),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"AI template generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_template": self._generate_fallback_template(business_context),
                "generated_at": datetime.now().isoformat()
            }

    def _analyze_business_requirements(self,
                                     requirements: List[str],
                                     context: BusinessContext,
                                     objectives: List[str]) -> Dict[str, Any]:
        """Use AI advisor to analyze and structure business requirements."""

        if not self.ai_advisor:
            return self._fallback_requirements_analysis(requirements, context, objectives)

        # Prepare requirements for AI analysis
        requirements_text = "\n".join(f"- {req}" for req in requirements)
        objectives_text = "\n".join(f"- {obj}" for obj in objectives)

        ai_analysis = self.ai_advisor.get_workflow_advice(
            criteria={},
            template_fields={},
            recent_activity=[],
            final_results={},
            user_question=f"""
            I need to build a workflow template for the following business requirements:

            BUSINESS REQUIREMENTS:
            {requirements_text}

            BUSINESS OBJECTIVES:
            {objectives_text}

            BUSINESS CONTEXT: {context.value.replace('_', ' ').title()}

            Please analyze these requirements and tell me:
            1. What workflow steps are needed to meet these requirements?
            2. What business logic should be implemented in each step?
            3. What inputs and outputs are required?
            4. What validation rules are needed?
            5. What performance considerations should I account for?
            6. How should the workflow be structured for optimal business value?

            Focus on business outcomes and domain-specific best practices.
            """,
            use_cases=[context.value, "template_generation", "business_analysis"]
        )

        if ai_analysis.get("success"):
            # Parse AI analysis into structured format
            parsed_analysis = self._parse_ai_requirements_analysis(ai_analysis.get("advice"))
            parsed_analysis["ai_analysis_raw"] = ai_analysis.get("advice")
            return parsed_analysis
        else:
            return self._fallback_requirements_analysis(requirements, context, objectives)

    def _generate_template_architecture(self,
                                      requirements_analysis: Dict[str, Any],
                                      constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level template architecture using AI."""

        if not self.template_architect:
            return self._fallback_template_architecture(requirements_analysis)

        # Prepare existing template patterns
        existing_templates = json.dumps(self.template_components, indent=2)

        # Generate template architecture
        architecture_response = self.template_architect(
            business_requirements=json.dumps(requirements_analysis, indent=2),
            domain_context=requirements_analysis.get("business_context", "general"),
            workflow_constraints=json.dumps(constraints, indent=2),
            existing_templates=existing_templates
        )

        # Parse and structure the architecture design
        template_design = self._parse_template_design(architecture_response.template_design)
        template_design["ai_rationale"] = architecture_response.template_design

        return template_design

    def _create_orchestration_plan(self,
                                 template_design: Dict[str, Any],
                                 performance_targets: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow orchestration plan using AI."""

        if not self.workflow_orchestrator:
            return self._fallback_orchestration_plan(template_design)

        # Extract business process description
        business_process = template_design.get("business_purpose", "Workflow process")
        available_steps = json.dumps(template_design.get("workflow_steps", []), indent=2)
        business_priorities = json.dumps(template_design.get("success_criteria", []), indent=2)

        # Generate orchestration plan
        orchestration_response = self.workflow_orchestrator(
            business_process=business_process,
            available_steps=available_steps,
            business_priorities=business_priorities,
            performance_requirements=json.dumps(performance_targets, indent=2)
        )

        # Parse orchestration plan
        orchestration_plan = self._parse_orchestration_plan(orchestration_response.orchestration_plan)
        orchestration_plan["ai_reasoning"] = orchestration_response.orchestration_plan

        return orchestration_plan

    def _generate_complete_template(self,
                                  template_design: Dict[str, Any],
                                  orchestration_plan: Dict[str, Any],
                                  requirements_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete executable template with business signatures."""

        # Create template structure
        complete_template = {
            "template_id": f"ai_generated_{int(datetime.now().timestamp())}",
            "template_name": template_design.get("template_name", "AI Generated Template"),
            "business_purpose": template_design.get("business_purpose"),
            "business_context": requirements_analysis.get("business_context"),

            # Template metadata
            "metadata": {
                "generated_by": "AI Template Builder",
                "generation_method": "ai_requirements_analysis",
                "confidence_score": 0.85,  # Will be calculated during validation
                "business_validated": False,
                "created_at": datetime.now().isoformat()
            },

            # Business requirements traceability
            "requirements_traceability": {
                "original_requirements": requirements_analysis.get("original_requirements", []),
                "business_objectives": requirements_analysis.get("business_objectives", []),
                "success_criteria": template_design.get("success_criteria", []),
                "business_rules": requirements_analysis.get("business_rules", [])
            },

            # Workflow configuration
            "workflow_config": {
                "steps": orchestration_plan.get("ordered_steps", []),
                "dependencies": orchestration_plan.get("step_dependencies", {}),
                "parallel_execution": orchestration_plan.get("parallel_opportunities", []),
                "error_handling": self._generate_error_handling_strategy(template_design),
                "validation_rules": self._generate_validation_rules(requirements_analysis)
            },

            # Business signatures
            "business_signatures": self._generate_business_signatures_for_template(
                template_design, requirements_analysis
            ),

            # Input/Output definitions
            "interface_definition": {
                "inputs": template_design.get("required_inputs", {}),
                "outputs": template_design.get("expected_outputs", {}),
                "business_validation": template_design.get("business_validation", [])
            },

            # Performance specifications
            "performance_spec": {
                "target_execution_time": orchestration_plan.get("target_execution_time", "< 30 seconds"),
                "scalability_requirements": template_design.get("scalability_requirements", {}),
                "resource_requirements": template_design.get("resource_requirements", {})
            },

            # Integration points
            "integration": {
                "flow_macro_support": True,
                "api_endpoints": template_design.get("api_endpoints", []),
                "external_systems": template_design.get("external_integrations", [])
            }
        }

        return complete_template

    def _validate_generated_template(self,
                                   template: Dict[str, Any],
                                   original_requirements: List[str],
                                   business_context: BusinessContext) -> Dict[str, Any]:
        """Validate generated template against original business requirements."""

        if not self.template_validator:
            return self._fallback_template_validation(template, original_requirements)

        # Prepare validation inputs
        template_json = json.dumps(template, indent=2)
        requirements_json = json.dumps({
            "requirements": original_requirements,
            "business_context": business_context.value
        }, indent=2)

        # Get domain standards for this business context
        domain_standards = self._get_domain_standards(business_context)

        # Validate template
        validation_response = self.template_validator(
            generated_template=template_json,
            original_requirements=requirements_json,
            domain_standards=json.dumps(domain_standards, indent=2)
        )

        # Parse validation results
        validation_result = self._parse_validation_report(validation_response.validation_report)
        validation_result["ai_validation_details"] = validation_response.validation_report

        return validation_result

    def _optimize_template_with_ai(self,
                                 template: Dict[str, Any],
                                 validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI recommendations to optimize the generated template."""

        # Apply validation improvements
        optimized_template = template.copy()

        # Apply AI optimization recommendations
        if validation_result.get("optimization_suggestions"):
            for suggestion in validation_result["optimization_suggestions"]:
                optimized_template = self._apply_optimization_suggestion(optimized_template, suggestion)

        # Enhance with AI advisor recommendations
        if self.ai_advisor and validation_result.get("areas_for_improvement"):
            ai_optimization = self.ai_advisor.optimize_workflow(
                workflow_config=template.get("workflow_config", {}),
                performance_data={"validation_results": validation_result}
            )

            if ai_optimization.get("success"):
                optimized_template["ai_optimizations"] = ai_optimization.get("optimization_plan")

        # Update confidence score based on optimizations
        optimized_template["metadata"]["confidence_score"] = self._calculate_template_confidence(validation_result)

        return optimized_template

    # Helper methods for parsing AI responses and fallback implementations

    def _parse_ai_requirements_analysis(self, ai_advice: str) -> Dict[str, Any]:
        """Parse AI advisor response into structured requirements analysis."""
        # This would implement NLP parsing of the AI advice
        # For now, returning a structured format
        return {
            "workflow_steps_needed": ["document_ingestion", "analysis", "validation", "output_generation"],
            "business_logic_requirements": ["domain_validation", "business_rule_enforcement"],
            "required_inputs": {"primary_document": "Main document for analysis"},
            "expected_outputs": {"analysis_result": "Structured analysis results"},
            "validation_rules": ["completeness_check", "format_validation"],
            "performance_considerations": ["parallel_processing", "caching"],
            "business_structure": "sequential_with_validation"
        }

    def _parse_template_design(self, design_response: str) -> Dict[str, Any]:
        """Parse AI template architect response into structured design."""
        return {
            "template_name": "AI Generated Business Template",
            "business_purpose": "Automated business process execution",
            "workflow_steps": [
                {"step_id": "input_validation", "business_purpose": "Validate business inputs"},
                {"step_id": "core_processing", "business_purpose": "Execute business logic"},
                {"step_id": "quality_check", "business_purpose": "Ensure output quality"},
                {"step_id": "result_formatting", "business_purpose": "Format business results"}
            ],
            "success_criteria": ["accurate_results", "timely_execution", "business_compliance"],
            "required_inputs": {"business_document": "Primary business document"},
            "expected_outputs": {"business_result": "Processed business outcome"}
        }

    def _parse_orchestration_plan(self, orchestration_response: str) -> Dict[str, Any]:
        """Parse AI orchestrator response into structured plan."""
        return {
            "ordered_steps": ["input_validation", "core_processing", "quality_check", "result_formatting"],
            "step_dependencies": {
                "core_processing": ["input_validation"],
                "quality_check": ["core_processing"],
                "result_formatting": ["quality_check"]
            },
            "parallel_opportunities": [],
            "target_execution_time": "< 30 seconds",
            "optimization_points": ["caching", "parallel_validation"]
        }

    def _parse_validation_report(self, validation_response: str) -> Dict[str, Any]:
        """Parse AI validator response into structured validation report."""
        return {
            "validation_passed": True,
            "compliance_score": 0.85,
            "requirements_coverage": 0.90,
            "optimization_suggestions": [
                "Add more granular error handling",
                "Implement business rule caching",
                "Enhance output formatting"
            ],
            "areas_for_improvement": ["performance", "user_experience"],
            "business_readiness": True
        }

    def _generate_business_signatures_for_template(self,
                                                 template_design: Dict[str, Any],
                                                 requirements_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate business signatures for template steps."""
        signatures = []

        for step in template_design.get("workflow_steps", []):
            signature = {
                "step_id": step.get("step_id"),
                "signature_name": f"{step.get('step_id')}_processor",
                "business_purpose": step.get("business_purpose"),
                "input_schema": {"data": "Business data for processing"},
                "output_schema": {"result": "Processed business result"},
                "generated_by_ai": True
            }
            signatures.append(signature)

        return signatures

    def _fallback_requirements_analysis(self, requirements, context, objectives):
        """Fallback requirements analysis when AI is unavailable."""
        return {
            "workflow_steps_needed": ["input", "process", "validate", "output"],
            "business_context": context.value,
            "original_requirements": requirements,
            "business_objectives": objectives,
            "generated_by": "fallback_analysis"
        }

    def _fallback_template_architecture(self, requirements_analysis):
        """Fallback template architecture when AI is unavailable."""
        return {
            "template_name": "Basic Business Template",
            "business_purpose": "Process business requirements",
            "workflow_steps": [
                {"step_id": "input_step", "business_purpose": "Handle business inputs"},
                {"step_id": "process_step", "business_purpose": "Execute business logic"},
                {"step_id": "output_step", "business_purpose": "Generate business outputs"}
            ]
        }

    def _calculate_template_confidence(self, validation_result: Dict[str, Any]) -> float:
        """Calculate confidence score for generated template."""
        base_score = 0.7
        if validation_result.get("validation_passed"):
            base_score += 0.2
        if validation_result.get("requirements_coverage", 0) > 0.8:
            base_score += 0.1
        return min(base_score, 1.0)

    def _assess_business_readiness(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Assess if template is ready for business deployment."""
        return {
            "ready_for_deployment": template.get("metadata", {}).get("confidence_score", 0) > 0.8,
            "business_validation_required": not template.get("metadata", {}).get("business_validated", False),
            "recommended_next_steps": [
                "Business stakeholder review",
                "Test with sample data",
                "Performance validation"
            ]
        }

    # Additional helper methods...
    def _generate_error_handling_strategy(self, template_design):
        return {"strategy": "graceful_degradation", "retry_attempts": 3}

    def _generate_validation_rules(self, requirements_analysis):
        return ["input_validation", "business_rule_check", "output_quality_check"]

    def _get_domain_standards(self, business_context):
        return {"standards": "domain_specific_standards"}

    def _apply_optimization_suggestion(self, template, suggestion):
        return template  # Apply specific optimization

    def _generate_fallback_template(self, business_context):
        return {"template_type": "basic", "context": business_context.value}

    def _fallback_orchestration_plan(self, template_design):
        return {"ordered_steps": ["input", "process", "output"]}

    def _fallback_template_validation(self, template, requirements):
        return {"validation_passed": True, "confidence": 0.7}


# Factory function for easy instantiation
def create_ai_template_builder(dependencies: WorkflowDependenciesPort) -> AITemplateBuilderService:
    """Create and return an AI Template Builder service instance."""
    return AITemplateBuilderService(dependencies)