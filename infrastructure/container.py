"""
Dependency Injection Container
==============================
Central container for managing dependencies and wiring the application.
"""

from typing import Dict, Any, Type, Callable
import logging

logger = logging.getLogger(__name__)


class DIContainer:
    """
    Dependency Injection Container for hexagonal architecture.

    This container manages the creation and wiring of all components,
    ensuring proper dependency inversion and testability.
    """

    def __init__(self):
        self.services = {}
        self.factories = {}
        self.singletons = {}
        self.adapters = {
            "primary": {},
            "secondary": {}
        }

    def register_service(self, name: str, service_class: Type, *args, **kwargs) -> None:
        """Register a service class"""
        self.services[name] = {
            "class": service_class,
            "args": args,
            "kwargs": kwargs
        }
        logger.info(f"Registered service: {name}")

    def register_factory(self, name: str, factory: Callable) -> None:
        """Register a factory function"""
        self.factories[name] = factory
        logger.info(f"Registered factory: {name}")

    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance"""
        self.singletons[name] = instance
        logger.info(f"Registered singleton: {name}")

    def register_adapter(self, type: str, name: str, adapter_class: Type, *args, **kwargs) -> None:
        """Register an adapter (primary or secondary)"""
        if type not in ["primary", "secondary"]:
            raise ValueError(f"Adapter type must be 'primary' or 'secondary', got {type}")

        self.adapters[type][name] = {
            "class": adapter_class,
            "args": args,
            "kwargs": kwargs
        }
        logger.info(f"Registered {type} adapter: {name}")

    def get_service(self, name: str) -> Any:
        """Get a service instance"""
        # Check singletons first
        if name in self.singletons:
            return self.singletons[name]

        # Check factories
        if name in self.factories:
            instance = self.factories[name]()
            return instance

        # Check services
        if name in self.services:
            service_config = self.services[name]
            instance = service_config["class"](
                *service_config["args"],
                **service_config["kwargs"]
            )
            return instance

        raise ValueError(f"Service {name} not found")

    def get_adapter(self, type: str, name: str) -> Any:
        """Get an adapter instance"""
        if type not in ["primary", "secondary"]:
            raise ValueError(f"Adapter type must be 'primary' or 'secondary', got {type}")

        if name not in self.adapters[type]:
            raise ValueError(f"{type.capitalize()} adapter {name} not found")

        adapter_config = self.adapters[type][name]
        instance = adapter_config["class"](
            *adapter_config["args"],
            **adapter_config["kwargs"]
        )
        return instance

    def wire(self) -> Dict[str, Any]:
        """
        Wire all dependencies and return the application context.

        This method creates all necessary instances and wires them together
        according to the hexagonal architecture principles.
        """
        context = {}

        try:
            # Create infrastructure components first
            from infrastructure.yaml_loader import SettingsLoader
            from infrastructure.services.credential_carrier import get_credential_carrier
            from adapters.secondary.session.unified_session_adapter import UnifiedSessionAdapter

            # Create shared infrastructure services (Resource Carrier Pattern)
            settings_loader = SettingsLoader()
            credential_carrier = get_credential_carrier()

            # Ensure environment variables are set for legacy compatibility
            credential_carrier.set_environment_from_credentials()

            # Create session adapter with credential carrier
            session_adapter = UnifiedSessionAdapter(credential_carrier)

            self.register_singleton("settings_loader", settings_loader)
            self.register_singleton("credential_carrier", credential_carrier)
            self.register_singleton("session_adapter", session_adapter)

            # Create repository adapters (secondary)
            from adapters.secondary.yaml_config_repository import YamlConfigRepository
            from adapters.secondary.in_memory_portal_repository import InMemoryPortalRepository

            config_repo = YamlConfigRepository(settings_loader)
            portal_repo = InMemoryPortalRepository()

            self.register_singleton("config_repository", config_repo)
            self.register_singleton("portal_repository", portal_repo)

            # Create domain services (if any)
            # None for now - pure domain models don't need DI

            # Create application services
            from application.use_cases.setup_environment import SetupEnvironmentUseCase
            from application.services.portal_orchestrator import PortalOrchestrator

            # Mock dependencies for now - replace with real ones
            credential_validator = type('obj', (object,), {
                'validate_database': lambda self, x: {"valid": True},
                'validate_aws': lambda self, x: {"valid": True}
            })()

            package_installer = type('obj', (object,), {
                'install': lambda self, x: {"success": True, "message": "Installed"}
            })()

            portal_runner = type('obj', (object,), {
                'start': lambda self, x: {"success": True},
                'stop': lambda self, x: {"success": True},
                'get_status': lambda self, x: {"status": "running"}
            })()

            setup_use_case = SetupEnvironmentUseCase(
                config_repo,
                credential_validator,
                package_installer
            )

            portal_orchestrator = PortalOrchestrator(
                portal_repo,
                portal_runner
            )

            self.register_singleton("setup_use_case", setup_use_case)
            self.register_singleton("portal_orchestrator", portal_orchestrator)

            # Build context
            context = {
                "infrastructure": {
                    "settings_loader": settings_loader,
                    "session_adapter": session_adapter
                },
                "repositories": {
                    "config": config_repo,
                    "portal": portal_repo
                },
                "use_cases": {
                    "setup": setup_use_case,
                    "portal_management": portal_orchestrator
                },
                "adapters": {
                    "session": session_adapter
                }
            }

            logger.info("Dependency injection wiring completed successfully")
            return context

        except Exception as e:
            logger.error(f"Failed to wire dependencies: {e}")
            raise


# Global container instance
_container = None


def get_container() -> DIContainer:
    """Get the global DI container instance"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container() -> None:
    """Reset the global container (useful for testing)"""
    global _container
    _container = None