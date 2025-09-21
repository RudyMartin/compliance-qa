"""
TidyLLM Workflows Package
========================

Comprehensive workflow management system with registry, CLI, and execution capabilities.

Components:
- registry: Core workflow registry system and management
- cli: Command-line interface for workflow operations
- generator: README and documentation generation
- definitions: Workflow definitions, templates, and criteria
- types: Individual workflow implementations

Features:
- Workflow registration and discovery
- Template-based workflow creation
- Criteria-based validation and scoring
- CLI and programmatic interfaces
- Documentation generation
"""

from .registry import WorkflowRegistrySystem, WorkflowCriteria, WorkflowTemplate, RegisteredWorkflow
from .cli import WorkflowCLI

__all__ = [
    'WorkflowRegistrySystem',
    'WorkflowCriteria',
    'WorkflowTemplate',
    'RegisteredWorkflow',
    'WorkflowCLI'
]