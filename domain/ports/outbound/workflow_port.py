"""
Workflow Domain Ports
====================
Port interfaces for workflow domain services.
This allows the domain workflow service to access infrastructure services
without directly importing from infrastructure (hexagonal architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime


class WorkflowSystemType(Enum):
    """Enumeration of supported workflow system types."""
    MVR_ANALYSIS = "mvr_analysis"
    DOMAIN_RAG = "domain_rag"
    FINANCIAL_ANALYSIS = "financial_analysis"
    CONTRACT_REVIEW = "contract_review"
    COMPLIANCE_CHECK = "compliance_check"
    QUALITY_CHECK = "quality_check"
    PEER_REVIEW = "peer_review"
    DATA_EXTRACTION = "data_extraction"
    HYBRID_ANALYSIS = "hybrid_analysis"
    CODE_REVIEW = "code_review"
    RESEARCH_SYNTHESIS = "research_synthesis"
    CLASSIFICATION = "classification"
    CUSTOM_WORKFLOW = "custom_workflow"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    CREATED = "created"
    DEPLOYED = "deployed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class WorkflowRegistryPort(ABC):
    """Port for workflow registry management."""

    @abstractmethod
    def load_workflow_registry(self) -> Dict[str, Any]:
        """Load the comprehensive workflow registry."""
        pass

    @abstractmethod
    def get_workflow_template(self, workflow_type: WorkflowSystemType) -> Optional[Dict[str, Any]]:
        """Get workflow template by type."""
        pass

    @abstractmethod
    def validate_workflow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow configuration."""
        pass

    @abstractmethod
    def save_workflow_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Save workflow template."""
        pass


class WorkflowExecutionPort(ABC):
    """Port for workflow execution operations."""

    @abstractmethod
    def create_workflow(self, system_type: WorkflowSystemType, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow instance."""
        pass

    @abstractmethod
    def deploy_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deploy a workflow for execution."""
        pass

    @abstractmethod
    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a deployed workflow."""
        pass

    @abstractmethod
    def get_workflow_status(self, workflow_id: str) -> WorkflowStatus:
        """Get current workflow execution status."""
        pass

    @abstractmethod
    def pause_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Pause a running workflow."""
        pass

    @abstractmethod
    def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Resume a paused workflow."""
        pass

    @abstractmethod
    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a workflow execution."""
        pass


class WorkflowStoragePort(ABC):
    """Port for workflow persistence operations."""

    @abstractmethod
    def save_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save workflow data."""
        pass

    @abstractmethod
    def load_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow data by ID."""
        pass

    @abstractmethod
    def list_workflows(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List workflows with optional filters."""
        pass

    @abstractmethod
    def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete workflow data."""
        pass

    @abstractmethod
    def archive_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Archive a completed workflow."""
        pass


class SessionManagementPort(ABC):
    """Port for session management operations."""

    @abstractmethod
    def create_session(self, workflow_id: str) -> Dict[str, Any]:
        """Create a new session for workflow execution."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        pass

    @abstractmethod
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close an active session."""
        pass

    @abstractmethod
    def is_session_healthy(self, session_id: str) -> bool:
        """Check if session is healthy and available."""
        pass


class RAGIntegrationPort(ABC):
    """Port for RAG system integration."""

    @abstractmethod
    def get_rag_manager(self) -> Any:
        """Get RAG manager instance."""
        pass

    @abstractmethod
    def is_rag_system_available(self, rag_type: str) -> bool:
        """Check if RAG system type is available."""
        pass

    @abstractmethod
    def deploy_rag_system(self, rag_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy RAG system for workflow."""
        pass

    @abstractmethod
    def query_rag_system(self, rag_id: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query deployed RAG system."""
        pass


class FlowMacroPort(ABC):
    """Port for Flow Macro operations."""

    @abstractmethod
    def execute_flow_macro(self, macro_command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Flow Macro command like [MVR_ANALYSIS] document.pdf."""
        pass

    @abstractmethod
    def parse_macro_command(self, command: str) -> Dict[str, Any]:
        """Parse Flow Macro command into structured format."""
        pass

    @abstractmethod
    def validate_macro_syntax(self, command: str) -> Dict[str, Any]:
        """Validate Flow Macro command syntax."""
        pass

    @abstractmethod
    def get_available_macros(self) -> List[Dict[str, Any]]:
        """Get list of available Flow Macros."""
        pass


class WorkflowMonitoringPort(ABC):
    """Port for workflow monitoring and health checks."""

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        pass

    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get workflow system performance metrics."""
        pass

    @abstractmethod
    def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """Get metrics for specific workflow."""
        pass

    @abstractmethod
    def log_workflow_event(self, workflow_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Log workflow execution event."""
        pass


class WorkflowDependenciesPort(ABC):
    """Combined port for all workflow service dependencies."""

    @abstractmethod
    def get_registry_service(self) -> WorkflowRegistryPort:
        """Get workflow registry service."""
        pass

    @abstractmethod
    def get_execution_service(self) -> WorkflowExecutionPort:
        """Get workflow execution service."""
        pass

    @abstractmethod
    def get_storage_service(self) -> WorkflowStoragePort:
        """Get workflow storage service."""
        pass

    @abstractmethod
    def get_session_service(self) -> SessionManagementPort:
        """Get session management service."""
        pass

    @abstractmethod
    def get_rag_integration_service(self) -> RAGIntegrationPort:
        """Get RAG integration service."""
        pass

    @abstractmethod
    def get_flow_macro_service(self) -> FlowMacroPort:
        """Get Flow Macro service."""
        pass

    @abstractmethod
    def get_monitoring_service(self) -> WorkflowMonitoringPort:
        """Get workflow monitoring service."""
        pass