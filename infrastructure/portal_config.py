"""
Portal Configuration Manager for compliance-qa

Centralized configuration management for all 7 portals.
Provides consistent configuration access and validation.

Designed with hexagonal architecture principles for clean separation.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import json

from .environment_manager import get_environment_manager

logger = logging.getLogger(__name__)


@dataclass
class PortalDefinition:
    """Definition of a portal configuration."""
    name: str
    port: int
    title: str
    description: str
    script_path: str
    category: str
    dependencies: List[str]
    health_check_url: Optional[str] = None
    enabled: bool = True


class PortalConfigManager:
    """
    Configuration manager for all compliance-qa portals.

    Manages the 7 confirmed portals with centralized configuration,
    health monitoring, and deployment coordination.
    """

    def __init__(self):
        self.env_manager = get_environment_manager()
        self._portal_registry = self._initialize_portal_registry()

    def _initialize_portal_registry(self) -> Dict[str, PortalDefinition]:
        """Initialize the registry of all 7 portals."""
        return {
            "setup": PortalDefinition(
                name="setup",
                port=8511,
                title="Setup Portal",
                description="System configuration & setup",
                script_path="portals/setup/setup_portal.py",
                category="infrastructure",
                dependencies=["database", "aws"],
                health_check_url="http://localhost:8511/health"
            ),
            "unified_rag": PortalDefinition(
                name="unified_rag",
                port=8506,
                title="Unified RAG Portal",
                description="Knowledge & document management",
                script_path="portals/rag/unified_rag_portal.py",
                category="application",
                dependencies=["database", "aws", "mlflow"],
                health_check_url="http://localhost:8506/health"
            ),
            "rag_creator": PortalDefinition(
                name="rag_creator",
                port=8525,
                title="RAG Creator V3",
                description="RAG system design & creation",
                script_path="portals/rag/rag_creator_v3.py",
                category="creator",
                dependencies=["database", "aws"],
                health_check_url="http://localhost:8525/health"
            ),
            "services": PortalDefinition(
                name="services",
                port=8505,
                title="Services Portal",
                description="Secondary services management",
                script_path="portals/services/services_portal.py",
                category="infrastructure",
                dependencies=["database"],
                health_check_url="http://localhost:8505/health"
            ),
            "dashboard": PortalDefinition(
                name="dashboard",
                port=8501,
                title="Main Dashboard",
                description="Primary system interface",
                script_path="portals/dashboard/main_dashboard.py",
                category="infrastructure",
                dependencies=[],
                health_check_url="http://localhost:8501/health"
            ),
            "simple_chat": PortalDefinition(
                name="simple_chat",
                port=8502,
                title="Simple Chat",
                description="Basic chat interface testing",
                script_path="portals/chat/simple_chat.py",
                category="application",
                dependencies=["aws"],
                health_check_url="http://localhost:8502/health"
            ),
            "flow_creator": PortalDefinition(
                name="flow_creator",
                port=8550,
                title="Flow Creator V3",
                description="Workflow design & management",
                script_path="portals/flow/flow_creator_v3.py",
                category="creator",
                dependencies=["database", "aws", "mlflow"],
                health_check_url="http://localhost:8550/health"
            )
        }

    def get_all_portals(self) -> Dict[str, PortalDefinition]:
        """Get all portal definitions."""
        return self._portal_registry.copy()

    def get_portal(self, portal_name: str) -> Optional[PortalDefinition]:
        """Get specific portal definition."""
        return self._portal_registry.get(portal_name)

    def get_portals_by_category(self, category: str) -> List[PortalDefinition]:
        """Get portals filtered by category."""
        return [
            portal for portal in self._portal_registry.values()
            if portal.category == category
        ]

    def get_enabled_portals(self) -> List[PortalDefinition]:
        """Get all enabled portals."""
        return [
            portal for portal in self._portal_registry.values()
            if portal.enabled
        ]

    def get_portal_config(self, portal_name: str) -> Dict[str, Any]:
        """
        Get complete configuration for a specific portal.

        Combines portal definition with environment-specific settings.
        """
        portal = self.get_portal(portal_name)
        if not portal:
            raise ValueError(f"Portal '{portal_name}' not found")

        # Get base portal config from environment manager
        base_config = self.env_manager.get_portal_config(portal_name)

        # Add portal-specific configuration
        portal_config = {
            **base_config,
            'portal_name': portal.name,
            'portal_title': portal.title,
            'portal_description': portal.description,
            'portal_port': portal.port,
            'portal_category': portal.category,
            'script_path': portal.script_path,
            'health_check_url': portal.health_check_url,
            'dependencies': portal.dependencies,
            'enabled': portal.enabled
        }

        # Add dependency configurations
        portal_config['dependency_configs'] = {}
        for dep in portal.dependencies:
            if dep == "database":
                portal_config['dependency_configs']['database'] = self.env_manager.get_database_config()
            elif dep == "aws":
                portal_config['dependency_configs']['aws'] = self.env_manager.get_aws_config()
            elif dep == "mlflow":
                portal_config['dependency_configs']['mlflow'] = self.env_manager.get_mlflow_config()

        return portal_config

    def get_portal_urls(self) -> Dict[str, str]:
        """Get URLs for all portals."""
        return {
            name: f"http://localhost:{portal.port}"
            for name, portal in self._portal_registry.items()
            if portal.enabled
        }

    def validate_portal_dependencies(self, portal_name: str) -> Dict[str, bool]:
        """
        Validate dependencies for a specific portal.

        Returns:
            Dict mapping dependency names to validation status
        """
        portal = self.get_portal(portal_name)
        if not portal:
            return {}

        validation_results = {}
        env_validation = self.env_manager.validate_configuration()

        for dependency in portal.dependencies:
            if dependency in env_validation:
                validation_results[dependency] = env_validation[dependency]
            else:
                validation_results[dependency] = False

        return validation_results

    def get_deployment_manifest(self) -> Dict[str, Any]:
        """
        Generate deployment manifest for all portals.

        Includes configuration, dependencies, and deployment instructions.
        """
        portals_config = {}
        for name, portal in self._portal_registry.items():
            if portal.enabled:
                portals_config[name] = {
                    'port': portal.port,
                    'script_path': portal.script_path,
                    'dependencies': portal.dependencies,
                    'category': portal.category,
                    'health_check_url': portal.health_check_url
                }

        return {
            'version': '1.0',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'portals': portals_config,
            'global_config': {
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true'
            },
            'deployment_instructions': {
                'startup_order': self._get_startup_order(),
                'health_check_interval': 30,
                'restart_policy': 'on-failure'
            }
        }

    def _get_startup_order(self) -> List[str]:
        """
        Determine optimal startup order based on dependencies.

        Returns portals in dependency order (least dependent first).
        """
        # Simple dependency-based ordering
        # Infrastructure portals first, then applications, then creators
        order = []

        # Infrastructure portals (no dependencies or minimal dependencies)
        infrastructure = self.get_portals_by_category("infrastructure")
        infrastructure.sort(key=lambda p: len(p.dependencies))
        order.extend([p.name for p in infrastructure])

        # Application portals
        applications = self.get_portals_by_category("application")
        order.extend([p.name for p in applications])

        # Creator portals (typically have most dependencies)
        creators = self.get_portals_by_category("creator")
        order.extend([p.name for p in creators])

        return order

    def update_portal_status(self, portal_name: str, enabled: bool):
        """Enable or disable a portal."""
        if portal_name in self._portal_registry:
            self._portal_registry[portal_name].enabled = enabled
            logger.info(f"Portal '{portal_name}' {'enabled' if enabled else 'disabled'}")
        else:
            raise ValueError(f"Portal '{portal_name}' not found")

    def get_portal_summary(self) -> Dict[str, Any]:
        """Get summary of all portals and their status."""
        total_portals = len(self._portal_registry)
        enabled_portals = len(self.get_enabled_portals())

        categories = {}
        for portal in self._portal_registry.values():
            if portal.category not in categories:
                categories[portal.category] = 0
            categories[portal.category] += 1

        return {
            'total_portals': total_portals,
            'enabled_portals': enabled_portals,
            'disabled_portals': total_portals - enabled_portals,
            'categories': categories,
            'portal_list': [
                {
                    'name': portal.name,
                    'title': portal.title,
                    'port': portal.port,
                    'category': portal.category,
                    'enabled': portal.enabled,
                    'url': f"http://localhost:{portal.port}" if portal.enabled else None
                }
                for portal in self._portal_registry.values()
            ]
        }

    def export_configuration(self, file_path: Optional[str] = None) -> str:
        """
        Export portal configuration to file.

        Args:
            file_path: Optional file path. If None, uses default location.

        Returns:
            Path to exported configuration file
        """
        if file_path is None:
            file_path = "portal_configuration.yaml"

        config_data = {
            'portals': {
                name: {
                    'port': portal.port,
                    'title': portal.title,
                    'description': portal.description,
                    'script_path': portal.script_path,
                    'category': portal.category,
                    'dependencies': portal.dependencies,
                    'health_check_url': portal.health_check_url,
                    'enabled': portal.enabled
                }
                for name, portal in self._portal_registry.items()
            },
            'metadata': {
                'export_timestamp': str(datetime.now()),
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'total_portals': len(self._portal_registry)
            }
        }

        with open(file_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        logger.info(f"Portal configuration exported to {file_path}")
        return file_path


# Global portal config manager instance
_portal_config_manager = None

def get_portal_config_manager() -> PortalConfigManager:
    """Get global portal configuration manager instance."""
    global _portal_config_manager
    if _portal_config_manager is None:
        _portal_config_manager = PortalConfigManager()
    return _portal_config_manager


# Convenience functions
def get_portal_config(portal_name: str) -> Dict[str, Any]:
    """Quick access to portal configuration."""
    return get_portal_config_manager().get_portal_config(portal_name)

def get_all_portal_urls() -> Dict[str, str]:
    """Quick access to all portal URLs."""
    return get_portal_config_manager().get_portal_urls()

def get_portal_summary() -> Dict[str, Any]:
    """Quick access to portal summary."""
    return get_portal_config_manager().get_portal_summary()


if __name__ == "__main__":
    # Test the portal configuration manager
    from datetime import datetime

    config_mgr = PortalConfigManager()

    print("Portal Summary:")
    summary = config_mgr.get_portal_summary()
    print(f"  Total Portals: {summary['total_portals']}")
    print(f"  Enabled Portals: {summary['enabled_portals']}")
    print(f"  Categories: {summary['categories']}")

    print("\nPortal URLs:")
    urls = config_mgr.get_portal_urls()
    for name, url in urls.items():
        print(f"  {name}: {url}")

    print("\nDeployment Manifest:")
    manifest = config_mgr.get_deployment_manifest()
    print(f"  Startup Order: {manifest['deployment_instructions']['startup_order']}")
    print(f"  Total Configured Portals: {len(manifest['portals'])}")