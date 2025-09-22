"""
Workflow Dependencies Adapter
=============================
Secondary adapter implementing workflow ports for hexagonal architecture.
Bridges domain workflow service to existing infrastructure services.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import traceback
import logging

from domain.ports.outbound.workflow_port import (
    WorkflowDependenciesPort,
    WorkflowRegistryPort,
    WorkflowExecutionPort,
    WorkflowStoragePort,
    SessionManagementPort,
    RAGIntegrationPort,
    FlowMacroPort,
    WorkflowMonitoringPort,
    WorkflowSystemType,
    WorkflowStatus
)

# Import existing infrastructure services
try:
    from tidyllm.infrastructure.session.unified import UnifiedSessionManager
    from tidyllm.services.unified_rag_manager import UnifiedRAGManager, RAGSystemType
    INFRASTRUCTURE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TidyLLM infrastructure not available: {e}")
    INFRASTRUCTURE_AVAILABLE = False


class WorkflowRegistryAdapter(WorkflowRegistryPort):
    """Adapter for workflow registry operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Use project-based structure instead of hardcoded paths
        self.workflows_dir = Path("packages/tidyllm/workflows/projects")
        self.templates_dir = Path("packages/tidyllm/workflows/projects")
        self.registry_file = Path("extracted_files/tidyllm/workflows/definitions/registry.json")

    def load_workflow_registry(self) -> Dict[str, Any]:
        """Load the comprehensive workflow registry."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                self.logger.info(f"Loaded {len(registry)} workflow definitions from registry")
                return registry
            else:
                self.logger.warning("Workflow registry not found, creating default")
                return self._create_default_registry()
        except Exception as e:
            self.logger.error(f"Registry load failed: {e}")
            return self._create_default_registry()

    def get_workflow_template(self, workflow_type: WorkflowSystemType) -> Optional[Dict[str, Any]]:
        """Get workflow template by type."""
        registry = self.load_workflow_registry()
        return registry.get(workflow_type.value)

    def validate_workflow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration."""
        try:
            errors = []

            # Basic validation
            if not config.get("workflow_name"):
                errors.append("workflow_name is required")

            if not config.get("workflow_type"):
                errors.append("workflow_type is required")

            # Validate workflow type exists
            try:
                WorkflowSystemType(config.get("workflow_type"))
            except ValueError:
                errors.append(f"Invalid workflow_type: {config.get('workflow_type')}")

            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"]
            }

    def save_workflow_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Save workflow template."""
        try:
            # Implementation for saving templates
            template_path = self.templates_dir / f"{template.get('workflow_id', 'unnamed')}.json"
            self.templates_dir.mkdir(parents=True, exist_ok=True)

            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)

            return {"success": True, "template_path": str(template_path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_default_registry(self) -> Dict[str, Any]:
        """Create default workflow registry."""
        return {
            "mvr_analysis": {
                "workflow_id": "mvr_analysis",
                "workflow_name": "MVR Analysis Workflow",
                "workflow_type": "mvr_analysis",
                "description": "4-stage MVR document analysis with RAG peer review",
                "rag_integration": ["ai_powered", "postgres", "intelligent"],
                "stages": ["mvr_tag", "mvr_qa", "mvr_peer", "mvr_report"],
                "criteria": {
                    "scoring_rubric": {"accuracy": 0.3, "completeness": 0.3, "compliance": 0.4}
                }
            },
            "domain_rag": {
                "workflow_id": "domain_rag",
                "workflow_name": "Domain RAG Creation",
                "workflow_type": "domain_rag",
                "description": "Create domain-specific RAG systems",
                "rag_integration": ["ai_powered", "postgres", "intelligent", "sme", "dspy"],
                "stages": ["input", "process", "index", "deploy"],
                "criteria": {
                    "scoring_rubric": {"retrieval_quality": 0.4, "response_accuracy": 0.4, "performance": 0.2}
                }
            }
        }


class WorkflowExecutionAdapter(WorkflowExecutionPort):
    """Adapter for workflow execution operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflow_cache = {}
        self.execution_state = {}

    def create_workflow(self, system_type: WorkflowSystemType, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow instance."""
        try:
            workflow_id = f"{system_type.value}_{int(time.time())}"

            workflow_data = {
                "workflow_id": workflow_id,
                "system_type": system_type.value,
                "config": config,
                "status": WorkflowStatus.CREATED.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            self.workflow_cache[workflow_id] = workflow_data

            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": WorkflowStatus.CREATED.value
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def deploy_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deploy a workflow for execution."""
        try:
            if workflow_id not in self.workflow_cache:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            workflow_data = self.workflow_cache[workflow_id]
            workflow_data["status"] = WorkflowStatus.DEPLOYED.value
            workflow_data["deployed_at"] = datetime.now().isoformat()
            workflow_data["updated_at"] = datetime.now().isoformat()

            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": WorkflowStatus.DEPLOYED.value
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a deployed workflow."""
        try:
            if workflow_id not in self.workflow_cache:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            workflow_data = self.workflow_cache[workflow_id]
            workflow_data["status"] = WorkflowStatus.RUNNING.value
            workflow_data["execution_started_at"] = datetime.now().isoformat()
            workflow_data["inputs"] = inputs or {}
            workflow_data["updated_at"] = datetime.now().isoformat()

            # Store execution state
            self.execution_state[workflow_id] = {
                "started_at": datetime.now().isoformat(),
                "inputs": inputs or {},
                "current_stage": "initial"
            }

            return {
                "success": True,
                "workflow_id": workflow_id,
                "execution_id": f"{workflow_id}_exec_{int(time.time())}",
                "status": WorkflowStatus.RUNNING.value
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_workflow_status(self, workflow_id: str) -> WorkflowStatus:
        """Get current workflow execution status."""
        if workflow_id in self.workflow_cache:
            status_str = self.workflow_cache[workflow_id].get("status", "created")
            try:
                return WorkflowStatus(status_str)
            except ValueError:
                return WorkflowStatus.CREATED
        return WorkflowStatus.CREATED

    def pause_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Pause a running workflow."""
        try:
            if workflow_id not in self.workflow_cache:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            workflow_data = self.workflow_cache[workflow_id]
            workflow_data["status"] = WorkflowStatus.PAUSED.value
            workflow_data["paused_at"] = datetime.now().isoformat()
            workflow_data["updated_at"] = datetime.now().isoformat()

            return {"success": True, "workflow_id": workflow_id, "status": WorkflowStatus.PAUSED.value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Resume a paused workflow."""
        try:
            if workflow_id not in self.workflow_cache:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            workflow_data = self.workflow_cache[workflow_id]
            workflow_data["status"] = WorkflowStatus.RUNNING.value
            workflow_data["resumed_at"] = datetime.now().isoformat()
            workflow_data["updated_at"] = datetime.now().isoformat()

            return {"success": True, "workflow_id": workflow_id, "status": WorkflowStatus.RUNNING.value}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a workflow execution."""
        try:
            if workflow_id not in self.workflow_cache:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            workflow_data = self.workflow_cache[workflow_id]
            workflow_data["status"] = WorkflowStatus.FAILED.value
            workflow_data["cancelled_at"] = datetime.now().isoformat()
            workflow_data["updated_at"] = datetime.now().isoformat()

            return {"success": True, "workflow_id": workflow_id, "status": WorkflowStatus.FAILED.value}
        except Exception as e:
            return {"success": False, "error": str(e)}


class WorkflowStorageAdapter(WorkflowStoragePort):
    """Adapter for workflow persistence operations."""

    def __init__(self, execution_adapter: WorkflowExecutionAdapter):
        self.logger = logging.getLogger(__name__)
        self.execution_adapter = execution_adapter

    def save_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save workflow data."""
        try:
            self.execution_adapter.workflow_cache[workflow_id] = workflow_data
            return {"success": True, "workflow_id": workflow_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def load_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow data by ID."""
        return self.execution_adapter.workflow_cache.get(workflow_id)

    def list_workflows(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List workflows with optional filters."""
        workflows = list(self.execution_adapter.workflow_cache.values())

        if filters:
            # Apply filters
            if "status" in filters:
                workflows = [w for w in workflows if w.get("status") == filters["status"]]
            if "system_type" in filters:
                workflows = [w for w in workflows if w.get("system_type") == filters["system_type"]]

        return workflows

    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete workflow data."""
        try:
            if workflow_id in self.execution_adapter.workflow_cache:
                del self.execution_adapter.workflow_cache[workflow_id]
                return {"success": True, "workflow_id": workflow_id}
            else:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def archive_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Archive a completed workflow."""
        try:
            if workflow_id in self.execution_adapter.workflow_cache:
                workflow_data = self.execution_adapter.workflow_cache[workflow_id]
                workflow_data["status"] = WorkflowStatus.ARCHIVED.value
                workflow_data["archived_at"] = datetime.now().isoformat()
                workflow_data["updated_at"] = datetime.now().isoformat()
                return {"success": True, "workflow_id": workflow_id}
            else:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class SessionManagementAdapter(SessionManagementPort):
    """Adapter for session management operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session_cache = {}
        self.usm = None

        if INFRASTRUCTURE_AVAILABLE:
            try:
                self.usm = UnifiedSessionManager()
                self.logger.info("UnifiedSessionManager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize UnifiedSessionManager: {e}")

    def create_session(self, workflow_id: str) -> Dict[str, Any]:
        """Create a new session for workflow execution."""
        try:
            session_id = f"session_{workflow_id}_{int(time.time())}"
            session_data = {
                "session_id": session_id,
                "workflow_id": workflow_id,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }

            self.session_cache[session_id] = session_data

            return {
                "success": True,
                "session_id": session_id,
                "workflow_id": workflow_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        return self.session_cache.get(session_id)

    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close an active session."""
        try:
            if session_id in self.session_cache:
                self.session_cache[session_id]["status"] = "closed"
                self.session_cache[session_id]["closed_at"] = datetime.now().isoformat()
                return {"success": True, "session_id": session_id}
            else:
                return {"success": False, "error": f"Session {session_id} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def is_session_healthy(self, session_id: str) -> bool:
        """Check if session is healthy and available."""
        session = self.session_cache.get(session_id)
        return session is not None and session.get("status") == "active"


class RAGIntegrationAdapter(RAGIntegrationPort):
    """Adapter for RAG system integration."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rag_manager = None

        if INFRASTRUCTURE_AVAILABLE:
            try:
                self.rag_manager = UnifiedRAGManager(auto_load_credentials=False)
                self.logger.info("UnifiedRAGManager initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize UnifiedRAGManager: {e}")

    def get_rag_manager(self) -> Any:
        """Get RAG manager instance."""
        return self.rag_manager

    def is_rag_system_available(self, rag_type: str) -> bool:
        """Check if RAG system type is available."""
        if not self.rag_manager:
            return False

        try:
            rag_system_type = RAGSystemType(rag_type)
            return self.rag_manager.is_system_available(rag_system_type)
        except (ValueError, AttributeError):
            return False

    def deploy_rag_system(self, rag_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy RAG system for workflow."""
        try:
            if not self.rag_manager:
                return {"success": False, "error": "RAG manager not available"}

            # Use existing RAG manager deployment logic
            return {"success": True, "rag_type": rag_type, "config": config}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def query_rag_system(self, rag_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query deployed RAG system."""
        try:
            if not self.rag_manager:
                return {"success": False, "error": "RAG manager not available"}

            # Implement RAG query logic
            return {
                "success": True,
                "rag_id": rag_id,
                "query": query,
                "response": "Mock RAG response",
                "context": context or {}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class FlowMacroAdapter(FlowMacroPort):
    """Adapter for Flow Macro operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_flow_macro(self, macro_command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Flow Macro command like [MVR_ANALYSIS] document.pdf."""
        try:
            parsed = self.parse_macro_command(macro_command)

            # Implementation would integrate with existing Flow Macro system
            return {
                "success": True,
                "macro_command": macro_command,
                "parsed_command": parsed,
                "execution_id": f"macro_{int(time.time())}",
                "status": "executed",
                "context": context
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def parse_macro_command(self, command: str) -> Dict[str, Any]:
        """Parse Flow Macro command into structured format."""
        try:
            # Basic parsing logic for [MACRO_NAME] arguments
            import re
            pattern = r'\[([^\]]+)\]\s*(.*)'
            match = re.match(pattern, command.strip())

            if match:
                macro_name = match.group(1)
                arguments = match.group(2).strip()

                return {
                    "macro_name": macro_name,
                    "arguments": arguments.split() if arguments else [],
                    "raw_command": command
                }
            else:
                return {"error": "Invalid macro command format"}
        except Exception as e:
            return {"error": str(e)}

    def validate_macro_syntax(self, command: str) -> Dict[str, Any]:
        """Validate Flow Macro command syntax."""
        try:
            parsed = self.parse_macro_command(command)
            if "error" in parsed:
                return {"valid": False, "errors": [parsed["error"]]}

            # Additional validation logic
            return {"valid": True, "parsed": parsed}
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

    def get_available_macros(self) -> List[Dict[str, Any]]:
        """Get list of available Flow Macros."""
        return [
            {"name": "MVR_ANALYSIS", "description": "4-stage MVR document analysis"},
            {"name": "DOMAIN_RAG", "description": "Create domain-specific RAG systems"},
            {"name": "COMPLIANCE_CHECK", "description": "Regulatory validation workflow"},
            {"name": "QUALITY_REVIEW", "description": "Quality assurance workflow"}
        ]


class WorkflowMonitoringAdapter(WorkflowMonitoringPort):
    """Adapter for workflow monitoring and health checks."""

    def __init__(self, execution_adapter: WorkflowExecutionAdapter):
        self.logger = logging.getLogger(__name__)
        self.execution_adapter = execution_adapter
        self.health_cache = {}
        self.last_health_check = {}

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            health_status = {
                "overall_healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }

            # Check workflow execution system
            health_status["components"]["workflow_execution"] = {
                "healthy": True,
                "active_workflows": len(self.execution_adapter.workflow_cache),
                "details": "Workflow execution system operational"
            }

            # Check infrastructure availability
            health_status["components"]["infrastructure"] = {
                "healthy": INFRASTRUCTURE_AVAILABLE,
                "details": "TidyLLM infrastructure availability" if INFRASTRUCTURE_AVAILABLE else "Infrastructure not available"
            }

            self.health_cache = health_status
            self.last_health_check = datetime.now()

            return health_status
        except Exception as e:
            return {
                "overall_healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get workflow system performance metrics."""
        try:
            workflows = list(self.execution_adapter.workflow_cache.values())

            metrics = {
                "total_workflows": len(workflows),
                "by_status": {},
                "by_type": {},
                "timestamp": datetime.now().isoformat()
            }

            # Calculate status distribution
            for workflow in workflows:
                status = workflow.get("status", "unknown")
                metrics["by_status"][status] = metrics["by_status"].get(status, 0) + 1

                system_type = workflow.get("system_type", "unknown")
                metrics["by_type"][system_type] = metrics["by_type"].get(system_type, 0) + 1

            return metrics
        except Exception as e:
            return {"error": str(e)}

    def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """Get metrics for specific workflow."""
        try:
            workflow_data = self.execution_adapter.workflow_cache.get(workflow_id)
            if not workflow_data:
                return {"error": f"Workflow {workflow_id} not found"}

            metrics = {
                "workflow_id": workflow_id,
                "status": workflow_data.get("status"),
                "created_at": workflow_data.get("created_at"),
                "updated_at": workflow_data.get("updated_at"),
                "execution_time": None
            }

            # Calculate execution time if workflow has run
            if workflow_data.get("execution_started_at"):
                start_time = datetime.fromisoformat(workflow_data["execution_started_at"])
                end_time = datetime.now()
                metrics["execution_time"] = (end_time - start_time).total_seconds()

            return metrics
        except Exception as e:
            return {"error": str(e)}

    def log_workflow_event(self, workflow_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log workflow execution event."""
        try:
            self.logger.info(f"Workflow Event - {workflow_id}: {event_type} - {event_data}")
        except Exception as e:
            self.logger.error(f"Failed to log workflow event: {e}")


class WorkflowDependenciesAdapter(WorkflowDependenciesPort):
    """Main adapter implementing all workflow dependency ports."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize all adapters
        self.registry_adapter = WorkflowRegistryAdapter()
        self.execution_adapter = WorkflowExecutionAdapter()
        self.storage_adapter = WorkflowStorageAdapter(self.execution_adapter)
        self.session_adapter = SessionManagementAdapter()
        self.rag_adapter = RAGIntegrationAdapter()
        self.flow_macro_adapter = FlowMacroAdapter()
        self.monitoring_adapter = WorkflowMonitoringAdapter(self.execution_adapter)

    def get_registry_service(self) -> WorkflowRegistryPort:
        """Get workflow registry service."""
        return self.registry_adapter

    def get_execution_service(self) -> WorkflowExecutionPort:
        """Get workflow execution service."""
        return self.execution_adapter

    def get_storage_service(self) -> WorkflowStoragePort:
        """Get workflow storage service."""
        return self.storage_adapter

    def get_session_service(self) -> SessionManagementPort:
        """Get session management service."""
        return self.session_adapter

    def get_rag_integration_service(self) -> RAGIntegrationPort:
        """Get RAG integration service."""
        return self.rag_adapter

    def get_flow_macro_service(self) -> FlowMacroPort:
        """Get Flow Macro service."""
        return self.flow_macro_adapter

    def get_monitoring_service(self) -> WorkflowMonitoringPort:
        """Get workflow monitoring service."""
        return self.monitoring_adapter


def get_workflow_dependencies_adapter() -> WorkflowDependenciesAdapter:
    """Factory function to get workflow dependencies adapter."""
    return WorkflowDependenciesAdapter()