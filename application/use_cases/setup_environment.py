"""
Setup Environment Use Case
==========================
Business logic for environment setup.
"""

from typing import Dict, Any, List
from domain.ports.inbound.use_case_port import SetupUseCasePort, SetupRequest, SetupResponse
from domain.ports.outbound.repository_port import ConfigurationRepositoryPort
from domain.models.configuration import Configuration


class SetupEnvironmentUseCase(SetupUseCasePort):
    """
    Use case for setting up the environment.

    This contains the business logic for environment setup,
    independent of any framework or infrastructure concerns.
    """

    def __init__(self,
                 config_repo: ConfigurationRepositoryPort,
                 credential_validator,
                 package_installer):
        self.config_repo = config_repo
        self.credential_validator = credential_validator
        self.package_installer = package_installer

    async def setup_environment(self, request: SetupRequest) -> SetupResponse:
        """
        Setup the environment based on the request.

        Business rules:
        1. Configuration must be valid
        2. Credentials must be validated if requested
        3. Packages must be installed if requested
        """
        try:
            # Load configuration
            config = await self.config_repo.load()

            if not config.is_valid():
                return SetupResponse(
                    success=False,
                    message="Invalid configuration",
                    details={"error": "Configuration validation failed"}
                )

            details = {"environment": request.environment}

            # Validate credentials if requested
            if request.validate_credentials:
                validation_results = await self._validate_all_credentials(config)
                details["credentials"] = validation_results

                if not all(v.get("valid", False) for v in validation_results.values()):
                    return SetupResponse(
                        success=False,
                        message="Credential validation failed",
                        details=details
                    )

            # Install packages if requested
            if request.install_packages:
                install_results = await self._install_core_packages()
                details["packages"] = install_results

                if not all(r.get("success", False) for r in install_results):
                    return SetupResponse(
                        success=False,
                        message="Package installation failed",
                        details=details
                    )

            return SetupResponse(
                success=True,
                message="Environment setup completed successfully",
                details=details
            )

        except Exception as e:
            return SetupResponse(
                success=False,
                message=f"Setup failed: {str(e)}",
                details={"error": str(e)}
            )

    async def validate_configuration(self) -> SetupResponse:
        """Validate the current configuration"""
        try:
            config = await self.config_repo.load()

            validation_results = {
                "has_database": config.has_database(),
                "has_aws": config.has_aws(),
                "is_valid": config.is_valid(),
                "architecture": config.architecture.pattern if config.architecture else None
            }

            if config.is_valid():
                return SetupResponse(
                    success=True,
                    message="Configuration is valid",
                    details=validation_results
                )
            else:
                return SetupResponse(
                    success=False,
                    message="Configuration is invalid",
                    details=validation_results
                )

        except Exception as e:
            return SetupResponse(
                success=False,
                message=f"Validation failed: {str(e)}",
                details={"error": str(e)}
            )

    async def install_packages(self, package_names: List[str]) -> SetupResponse:
        """Install specified packages"""
        try:
            results = []
            for package_name in package_names:
                result = await self.package_installer.install(package_name)
                results.append({
                    "package": package_name,
                    "success": result.get("success", False),
                    "message": result.get("message", "")
                })

            all_success = all(r["success"] for r in results)

            return SetupResponse(
                success=all_success,
                message="All packages installed" if all_success else "Some packages failed",
                details={"packages": results}
            )

        except Exception as e:
            return SetupResponse(
                success=False,
                message=f"Installation failed: {str(e)}",
                details={"error": str(e)}
            )

    async def _validate_all_credentials(self, config: Configuration) -> Dict[str, Any]:
        """Validate all configured credentials"""
        results = {}

        if config.has_database():
            results["database"] = await self.credential_validator.validate_database(config.database)

        if config.has_aws():
            results["aws"] = await self.credential_validator.validate_aws(config.aws)

        return results

    async def _install_core_packages(self) -> List[Dict[str, Any]]:
        """Install core packages"""
        core_packages = ["tidyllm", "tlm", "tidyllm-sentence"]
        results = []

        for package in core_packages:
            result = await self.package_installer.install(package)
            results.append({
                "package": package,
                "success": result.get("success", False)
            })

        return results