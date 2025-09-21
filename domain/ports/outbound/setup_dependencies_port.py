"""
Setup Dependencies Port
=======================
Port interface for setup service dependencies.
This allows the domain setup service to access infrastructure services
without directly importing from infrastructure (hexagonal architecture).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class ConfigurationPort(ABC):
    """Port for configuration management."""

    @abstractmethod
    def load_config(self) -> Any:
        """Load configuration."""
        pass

    @abstractmethod
    def get_bedrock_config(self) -> Dict[str, Any]:
        """Get Bedrock configuration."""
        pass

    @abstractmethod
    def get_mlflow_config(self) -> Dict[str, Any]:
        """Get MLflow configuration."""
        pass

    @abstractmethod
    def setup_environment_from_settings(self) -> Dict[str, str]:
        """Setup environment variables from settings."""
        pass


class EnvironmentPort(ABC):
    """Port for environment management."""

    @abstractmethod
    def get_variables(self) -> Dict[str, str]:
        """Get environment variables."""
        pass

    @abstractmethod
    def set_variable(self, key: str, value: str) -> None:
        """Set environment variable."""
        pass

    @abstractmethod
    def validate_environment(self) -> Dict[str, Any]:
        """Validate environment setup."""
        pass


class CredentialPort(ABC):
    """Port for credential management."""

    @abstractmethod
    def validate_all_credentials(self) -> Dict[str, Any]:
        """Validate all configured credentials."""
        pass

    @abstractmethod
    def quick_health_check(self) -> Dict[str, bool]:
        """Perform quick health check on credentials."""
        pass

    @abstractmethod
    def sync_active_credential_state(self, status: str) -> None:
        """Sync active credential state."""
        pass


class PortalConfigPort(ABC):
    """Port for portal configuration."""

    @abstractmethod
    def get_portal_summary(self) -> Dict[str, Any]:
        """Get portal configuration summary."""
        pass


class PackageInstallerPort(ABC):
    """Port for package installation."""

    @abstractmethod
    def check_local_packages(self) -> List[Dict[str, Any]]:
        """Check status of local packages."""
        pass

    @abstractmethod
    def install_local_packages(self) -> Dict[str, Any]:
        """Install local packages."""
        pass

    @abstractmethod
    def run_tests(self, package_name: str, test_type: str = 'unit') -> Dict[str, Any]:
        """Run tests for a package."""
        pass


class ScriptGeneratorPort(ABC):
    """Port for script generation."""

    @abstractmethod
    def generate_startup_script(self, **kwargs) -> Path:
        """Generate startup script."""
        pass

    @abstractmethod
    def generate_service_script(self, service: str, **kwargs) -> Path:
        """Generate service-specific script."""
        pass


class AWSServicePort(ABC):
    """Port for AWS service access."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if AWS service is available."""
        pass

    @abstractmethod
    def get_bedrock_client(self) -> Any:
        """Get Bedrock client."""
        pass

    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test AWS connection."""
        pass


class SetupDependenciesPort(ABC):
    """Combined port for all setup service dependencies."""

    @abstractmethod
    def get_configuration_service(self) -> ConfigurationPort:
        """Get configuration service."""
        pass

    @abstractmethod
    def get_environment_service(self) -> EnvironmentPort:
        """Get environment service."""
        pass

    @abstractmethod
    def get_credential_service(self) -> CredentialPort:
        """Get credential service."""
        pass

    @abstractmethod
    def get_portal_config_service(self) -> PortalConfigPort:
        """Get portal configuration service."""
        pass

    @abstractmethod
    def get_package_installer_service(self) -> PackageInstallerPort:
        """Get package installer service."""
        pass

    @abstractmethod
    def get_script_generator_service(self) -> ScriptGeneratorPort:
        """Get script generator service."""
        pass

    @abstractmethod
    def get_aws_service(self) -> AWSServicePort:
        """Get AWS service."""
        pass