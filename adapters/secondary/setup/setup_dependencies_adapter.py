"""
Setup Dependencies Adapter
==========================
Adapter implementation that connects the domain setup service
to infrastructure services through the port interface.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from domain.ports.outbound.setup_dependencies_port import (
    SetupDependenciesPort,
    ConfigurationPort,
    EnvironmentPort,
    CredentialPort,
    PortalConfigPort,
    PackageInstallerPort,
    ScriptGeneratorPort,
    AWSServicePort
)

logger = logging.getLogger(__name__)


class ConfigurationAdapter(ConfigurationPort):
    """Adapter for configuration management."""

    def __init__(self):
        """Initialize configuration adapter."""
        self._loader = None

    def _get_loader(self):
        """Lazy load the settings loader."""
        if self._loader is None:
            from infrastructure.yaml_loader import get_settings_loader
            self._loader = get_settings_loader()
        return self._loader

    def load_config(self) -> Any:
        """Load configuration."""
        return self._get_loader().load_config()

    def get_bedrock_config(self) -> Dict[str, Any]:
        """Get Bedrock configuration."""
        return self._get_loader().get_bedrock_config()

    def get_mlflow_config(self) -> Dict[str, Any]:
        """Get MLflow configuration."""
        return self._get_loader().get_mlflow_config()

    def setup_environment_from_settings(self) -> Dict[str, str]:
        """Setup environment variables from settings."""
        from infrastructure.yaml_loader import setup_environment_from_settings
        return setup_environment_from_settings()


class EnvironmentAdapter(EnvironmentPort):
    """Adapter for environment management."""

    def __init__(self):
        """Initialize environment adapter."""
        self._manager = None

    def _get_manager(self):
        """Lazy load the environment manager."""
        if self._manager is None:
            from infrastructure.environment_manager import get_environment_manager
            self._manager = get_environment_manager()
        return self._manager

    def get_variables(self) -> Dict[str, str]:
        """Get environment variables."""
        return self._get_manager().get_variables()

    def set_variable(self, key: str, value: str) -> None:
        """Set environment variable."""
        self._get_manager().set_variable(key, value)

    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup."""
        return self._get_manager().validate_environment()


class CredentialAdapter(CredentialPort):
    """Adapter for credential management."""

    def validate_all_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials."""
        from infrastructure.credential_validator import validate_all_credentials
        return validate_all_credentials()

    def quick_health_check(self) -> Dict[str, bool]:
        """Perform quick health check on credentials."""
        from infrastructure.credential_validator import quick_health_check
        return quick_health_check()

    def sync_active_credential_state(self, status: str) -> None:
        """Sync active credential state."""
        from infrastructure.services.credential_carrier import sync_active_credential_state
        sync_active_credential_state(status)


class PortalConfigAdapter(PortalConfigPort):
    """Adapter for portal configuration."""

    def get_portal_summary(self) -> Dict[str, Any]:
        """Get portal configuration summary."""
        from infrastructure.portal_config import get_portal_summary
        return get_portal_summary()


class PackageInstallerAdapter(PackageInstallerPort):
    """Adapter for package installation."""

    def __init__(self):
        """Initialize package installer adapter."""
        self._installer = None

    def _get_installer(self):
        """Lazy load the package installer."""
        if self._installer is None:
            from infrastructure.install_packages import PackageInstaller
            self._installer = PackageInstaller()
        return self._installer

    def check_local_packages(self) -> List[Dict[str, Any]]:
        """Check status of local packages."""
        return self._get_installer().check_local_packages()

    def install_local_packages(self) -> Dict[str, Any]:
        """Install local packages."""
        return self._get_installer().install_local_packages()

    def run_tests(self, package_name: str, test_type: str = 'unit') -> Dict[str, Any]:
        """Run tests for a package."""
        return self._get_installer().run_tests(package_name, test_type)


class ScriptGeneratorAdapter(ScriptGeneratorPort):
    """Adapter for script generation."""

    def __init__(self):
        """Initialize script generator adapter."""
        self._generator = None

    def _get_generator(self):
        """Lazy load the script generator."""
        if self._generator is None:
            from infrastructure.script_generator import get_script_generator
            self._generator = get_script_generator()
        return self._generator

    def generate_startup_script(self, **kwargs) -> Path:
        """Generate startup script."""
        return self._get_generator().generate_startup_script(**kwargs)

    def generate_service_script(self, service: str, **kwargs) -> Path:
        """Generate service-specific script."""
        return self._get_generator().generate_service_script(service, **kwargs)


class AWSServiceAdapter(AWSServicePort):
    """Adapter for AWS service access."""

    def __init__(self):
        """Initialize AWS service adapter."""
        self._service = None

    def _get_service(self):
        """Lazy load the AWS service."""
        if self._service is None:
            from infrastructure.services.aws_service import get_aws_service
            self._service = get_aws_service()
        return self._service

    def is_available(self) -> bool:
        """Check if AWS service is available."""
        return self._get_service().is_available()

    def get_bedrock_client(self) -> Any:
        """Get Bedrock client."""
        return self._get_service().get_bedrock_client()

    def test_connection(self) -> Dict[str, Any]:
        """Test AWS connection."""
        return {
            'connected': self.is_available(),
            'has_bedrock': self.get_bedrock_client() is not None
        }


class SetupDependenciesAdapter(SetupDependenciesPort):
    """Main adapter that provides all setup dependencies."""

    def __init__(self):
        """Initialize all service adapters."""
        self._config_service = None
        self._env_service = None
        self._cred_service = None
        self._portal_service = None
        self._package_service = None
        self._script_service = None
        self._aws_service = None

    def get_configuration_service(self) -> ConfigurationPort:
        """Get configuration service."""
        if self._config_service is None:
            self._config_service = ConfigurationAdapter()
        return self._config_service

    def get_environment_service(self) -> EnvironmentPort:
        """Get environment service."""
        if self._env_service is None:
            self._env_service = EnvironmentAdapter()
        return self._env_service

    def get_credential_service(self) -> CredentialPort:
        """Get credential service."""
        if self._cred_service is None:
            self._cred_service = CredentialAdapter()
        return self._cred_service

    def get_portal_config_service(self) -> PortalConfigPort:
        """Get portal configuration service."""
        if self._portal_service is None:
            self._portal_service = PortalConfigAdapter()
        return self._portal_service

    def get_package_installer_service(self) -> PackageInstallerPort:
        """Get package installer service."""
        if self._package_service is None:
            self._package_service = PackageInstallerAdapter()
        return self._package_service

    def get_script_generator_service(self) -> ScriptGeneratorPort:
        """Get script generator service."""
        if self._script_service is None:
            self._script_service = ScriptGeneratorAdapter()
        return self._script_service

    def get_aws_service(self) -> AWSServicePort:
        """Get AWS service."""
        if self._aws_service is None:
            self._aws_service = AWSServiceAdapter()
        return self._aws_service


# Singleton instance
_adapter = None

def get_setup_dependencies_adapter() -> SetupDependenciesAdapter:
    """Get singleton adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = SetupDependenciesAdapter()
    return _adapter