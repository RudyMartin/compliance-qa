"""
Workflow Domain Service
======================
Core business logic for workflow management following hexagonal architecture.
This service contains pure domain logic and uses ports to access infrastructure.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from ..ports.outbound.workflow_port import (
    WorkflowDependenciesPort,
    WorkflowSystemType,
    WorkflowStatus
)


class WorkflowService:
    """
    Domain service for workflow management.
    Contains pure business logic without infrastructure dependencies.
    """

    def __init__(self, dependencies: WorkflowDependenciesPort):
        """Initialize workflow service with dependency ports."""
        self.dependencies = dependencies
        self.logger = logging.getLogger(__name__)

    # ==================== WORKFLOW SYSTEM AVAILABILITY ====================

    def is_system_available(self, system_type: WorkflowSystemType) -> bool:
        """
        Check if a workflow system type is available.
        Business logic: system is available if template exists and RAG dependencies are met.
        """
        try:
            registry_service = self.dependencies.get_registry_service()
            template = registry_service.get_workflow_template(system_type)

            if not template:
                return False

            # Check RAG dependencies through port
            rag_service = self.dependencies.get_rag_integration_service()
            rag_requirements = template.get("rag_integration", [])

            for rag_type in rag_requirements:
                if not rag_service.is_rag_system_available(rag_type):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"System availability check failed for {system_type.value}: {e}")
            return False

    def get_available_systems(self) -> Dict[str, bool]:
        """Get availability status for all workflow systems."""
        availability = {}
        for system_type in WorkflowSystemType:
            availability[system_type.value] = self.is_system_available(system_type)
        return availability

    # ==================== WORKFLOW LIFECYCLE MANAGEMENT ====================

    def create_workflow(self, system_type: WorkflowSystemType, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow instance.
        Business logic: validate system availability, config, and create workflow.
        """
        try:
            # Validate system availability
            if not self.is_system_available(system_type):
                return {
                    "success": False,
                    "error": f"Workflow system {system_type.value} is not available"
                }

            # Validate configuration
            registry_service = self.dependencies.get_registry_service()
            validation_result = registry_service.validate_workflow_config(config)

            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "error": f"Invalid configuration: {validation_result.get('errors', [])}"
                }

            # Create workflow through execution port
            execution_service = self.dependencies.get_execution_service()
            result = execution_service.create_workflow(system_type, config)

            if result.get("success"):
                # Log creation event
                monitoring_service = self.dependencies.get_monitoring_service()
                monitoring_service.log_workflow_event(
                    workflow_id=result.get("workflow_id"),
                    event_type="workflow_created",
                    event_data={
                        "system_type": system_type.value,
                        "config": config,
                        "timestamp": datetime.now().isoformat()
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Workflow creation failed: {e}")
            return {
                "success": False,
                "error": f"Workflow creation failed: {str(e)}"
            }

    def deploy_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Deploy a workflow for execution.
        Business logic: validate workflow exists and is in deployable state.
        """
        try:
            # Check workflow exists
            storage_service = self.dependencies.get_storage_service()
            workflow_data = storage_service.load_workflow(workflow_id)

            if not workflow_data:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }

            # Check current status allows deployment
            execution_service = self.dependencies.get_execution_service()
            current_status = execution_service.get_workflow_status(workflow_id)

            if current_status not in [WorkflowStatus.CREATED]:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} cannot be deployed in status {current_status.value}"
                }

            # Deploy RAG systems if required
            rag_service = self.dependencies.get_rag_integration_service()
            rag_requirements = workflow_data.get("rag_integration", [])

            for rag_type in rag_requirements:
                rag_result = rag_service.deploy_rag_system(rag_type, workflow_data)
                if not rag_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Failed to deploy RAG system {rag_type}: {rag_result.get('error')}"
                    }

            # Deploy workflow
            result = execution_service.deploy_workflow(workflow_id)

            if result.get("success"):
                monitoring_service = self.dependencies.get_monitoring_service()
                monitoring_service.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="workflow_deployed",
                    event_data={"timestamp": datetime.now().isoformat()}
                )

            return result

        except Exception as e:
            self.logger.error(f"Workflow deployment failed: {e}")
            return {
                "success": False,
                "error": f"Workflow deployment failed: {str(e)}"
            }

    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a deployed workflow.
        Business logic: validate workflow is deployed and ready for execution.
        """
        try:
            # Check workflow status
            execution_service = self.dependencies.get_execution_service()
            current_status = execution_service.get_workflow_status(workflow_id)

            if current_status != WorkflowStatus.DEPLOYED:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} must be deployed before execution. Current status: {current_status.value}"
                }

            # Create session for execution
            session_service = self.dependencies.get_session_service()
            session_result = session_service.create_session(workflow_id)

            if not session_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to create execution session: {session_result.get('error')}"
                }

            # Execute workflow
            result = execution_service.execute_workflow(workflow_id, inputs or {})

            # Log execution event
            monitoring_service = self.dependencies.get_monitoring_service()
            monitoring_service.log_workflow_event(
                workflow_id=workflow_id,
                event_type="workflow_execution_started",
                event_data={
                    "inputs": inputs,
                    "session_id": session_result.get("session_id"),
                    "timestamp": datetime.now().isoformat()
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}"
            }

    # ==================== FLOW MACRO OPERATIONS ====================

    def execute_flow_macro(self, macro_command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a Flow Macro command.
        Business logic: parse command, validate syntax, and execute workflow chain.
        """
        try:
            flow_macro_service = self.dependencies.get_flow_macro_service()

            # Validate macro syntax
            validation_result = flow_macro_service.validate_macro_syntax(macro_command)
            if not validation_result.get("valid", False):
                return {
                    "success": False,
                    "error": f"Invalid Flow Macro syntax: {validation_result.get('errors', [])}"
                }

            # Parse macro command
            parsed_macro = flow_macro_service.parse_macro_command(macro_command)

            # Execute macro through port
            result = flow_macro_service.execute_flow_macro(macro_command, context or {})

            # Log Flow Macro execution
            monitoring_service = self.dependencies.get_monitoring_service()
            monitoring_service.log_workflow_event(
                workflow_id=result.get("workflow_id", "flow_macro"),
                event_type="flow_macro_executed",
                event_data={
                    "command": macro_command,
                    "parsed_macro": parsed_macro,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Flow Macro execution failed: {e}")
            return {
                "success": False,
                "error": f"Flow Macro execution failed: {str(e)}"
            }

    def get_available_flow_macros(self) -> List[Dict[str, Any]]:
        """Get list of available Flow Macros."""
        try:
            flow_macro_service = self.dependencies.get_flow_macro_service()
            return flow_macro_service.get_available_macros()
        except Exception as e:
            self.logger.error(f"Failed to get available Flow Macros: {e}")
            return []

    # ==================== WORKFLOW MANAGEMENT ====================

    def list_workflows(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List workflows with optional filters."""
        try:
            storage_service = self.dependencies.get_storage_service()
            return storage_service.list_workflows(filters)
        except Exception as e:
            self.logger.error(f"Failed to list workflows: {e}")
            return []

    def get_workflow_details(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed workflow information."""
        try:
            storage_service = self.dependencies.get_storage_service()
            workflow_data = storage_service.load_workflow(workflow_id)

            if not workflow_data:
                return None

            # Enrich with current status and metrics
            execution_service = self.dependencies.get_execution_service()
            monitoring_service = self.dependencies.get_monitoring_service()

            workflow_data["current_status"] = execution_service.get_workflow_status(workflow_id).value
            workflow_data["metrics"] = monitoring_service.get_workflow_metrics(workflow_id)

            return workflow_data

        except Exception as e:
            self.logger.error(f"Failed to get workflow details: {e}")
            return None

    def pause_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Pause a running workflow."""
        try:
            execution_service = self.dependencies.get_execution_service()
            result = execution_service.pause_workflow(workflow_id)

            if result.get("success"):
                monitoring_service = self.dependencies.get_monitoring_service()
                monitoring_service.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="workflow_paused",
                    event_data={"timestamp": datetime.now().isoformat()}
                )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Resume a paused workflow."""
        try:
            execution_service = self.dependencies.get_execution_service()
            result = execution_service.resume_workflow(workflow_id)

            if result.get("success"):
                monitoring_service = self.dependencies.get_monitoring_service()
                monitoring_service.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="workflow_resumed",
                    event_data={"timestamp": datetime.now().isoformat()}
                )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a workflow execution."""
        try:
            execution_service = self.dependencies.get_execution_service()
            result = execution_service.cancel_workflow(workflow_id)

            if result.get("success"):
                monitoring_service = self.dependencies.get_monitoring_service()
                monitoring_service.log_workflow_event(
                    workflow_id=workflow_id,
                    event_type="workflow_cancelled",
                    event_data={"timestamp": datetime.now().isoformat()}
                )

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== HEALTH AND MONITORING ====================

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            monitoring_service = self.dependencies.get_monitoring_service()
            return monitoring_service.health_check()
        except Exception as e:
            return {
                "overall_healthy": False,
                "error": str(e)
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get workflow system performance metrics."""
        try:
            monitoring_service = self.dependencies.get_monitoring_service()
            return monitoring_service.get_performance_metrics()
        except Exception as e:
            return {
                "error": str(e)
            }

    # ==================== BUSINESS SIGNATURE INTEGRATION ====================

    def create_business_signature_workflow(self, signature_id: str,
                                         business_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and execute a workflow based on a business signature.
        This integrates business signatures as executable workflow tools.
        """
        try:
            # Load business signature configuration
            storage_service = self.dependencies.get_storage_service()
            signature_data = storage_service.load_workflow(f"business_sig_{signature_id}")

            if not signature_data:
                return {
                    "success": False,
                    "error": f"Business signature {signature_id} not found"
                }

            # Create workflow configuration based on business signature
            workflow_config = {
                "workflow_type": "business_signature",
                "signature_id": signature_id,
                "business_name": signature_data.get("signature_name"),
                "business_inputs": business_inputs,
                "signature_template": signature_data.get("signature_template"),
                "validation_rules": signature_data.get("validation_rules", []),
                "business_context": signature_data.get("business_requirement", {}).get("business_context"),
                "created_from_signature": True
            }

            # Create workflow using existing workflow creation logic
            result = self.create_workflow(
                WorkflowSystemType.CUSTOM_WORKFLOW,
                workflow_config
            )

            if result.get("success"):
                # Auto-deploy business signature workflows
                workflow_id = result.get("workflow_id")
                deploy_result = self.deploy_workflow(workflow_id)

                if deploy_result.get("success"):
                    # Execute with business inputs
                    execution_result = self.execute_workflow(workflow_id, business_inputs)

                    # Enhance result with business context
                    execution_result["business_signature_id"] = signature_id
                    execution_result["business_name"] = signature_data.get("signature_name")
                    execution_result["business_context"] = signature_data.get("business_requirement", {}).get("business_context")

                    return execution_result
                else:
                    return deploy_result
            else:
                return result

        except Exception as e:
            self.logger.error(f"Business signature workflow creation failed: {e}")
            return {
                "success": False,
                "error": f"Business signature workflow failed: {str(e)}"
            }

    def execute_business_tool_macro(self, tool_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a business tool through Flow Macro syntax.
        Supports Flow Macro commands like [BUSINESS_TOOL:tool_id] input.pdf
        """
        try:
            # Extract signature ID from business tool ID
            if tool_id.startswith("business_tool_"):
                signature_id = tool_id.replace("business_tool_", "")
            else:
                signature_id = tool_id

            # Execute business signature workflow
            result = self.create_business_signature_workflow(signature_id, inputs)

            # Log Flow Macro execution
            monitoring_service = self.dependencies.get_monitoring_service()
            monitoring_service.log_workflow_event(
                workflow_id=result.get("workflow_id", f"business_tool_{tool_id}"),
                event_type="business_tool_macro_executed",
                event_data={
                    "tool_id": tool_id,
                    "signature_id": signature_id,
                    "inputs": inputs,
                    "execution_result": result.get("success", False),
                    "timestamp": datetime.now().isoformat()
                }
            )

            return result

        except Exception as e:
            self.logger.error(f"Business tool macro execution failed: {e}")
            return {
                "success": False,
                "error": f"Business tool macro failed: {str(e)}"
            }

    def list_business_signature_tools(self) -> List[Dict[str, Any]]:
        """List all available business signature tools for Flow Macros."""
        try:
            storage_service = self.dependencies.get_storage_service()

            # Get all business signatures
            business_tools = storage_service.list_workflows({
                "workflow_type": "business_signature"
            })

            # Format for Flow Macro integration
            formatted_tools = []
            for tool_data in business_tools:
                formatted_tools.append({
                    "tool_id": f"business_tool_{tool_data.get('signature_id', 'unknown')}",
                    "business_name": tool_data.get("signature_name", "Unknown Business Tool"),
                    "business_purpose": tool_data.get("business_purpose", ""),
                    "business_context": tool_data.get("business_context", ""),
                    "flow_macro_syntax": f"[BUSINESS_TOOL:{tool_data.get('signature_id', 'unknown')}]",
                    "input_schema": tool_data.get("domain_inputs", {}),
                    "output_schema": tool_data.get("domain_outputs", {}),
                    "validation_rules": tool_data.get("validation_rules", [])
                })

            return formatted_tools

        except Exception as e:
            self.logger.error(f"Failed to list business signature tools: {e}")
            return []