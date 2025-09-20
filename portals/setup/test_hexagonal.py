"""
Test Hexagonal Architecture in Setup Portal
===========================================
Demonstrates the new architecture in action.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from our hexagonal architecture
from infrastructure.container import get_container
from domain.models.portal import Portal, PortalStatus, PortalType
from domain.models.configuration import Configuration
from application.use_cases.setup_environment import SetupEnvironmentUseCase
from application.services.portal_orchestrator import PortalOrchestrator
from domain.ports.inbound.use_case_port import SetupRequest


def test_architecture():
    """Test the hexagonal architecture components"""
    st.title("🔷 Hexagonal Architecture Test")

    # Create tabs for different tests
    tabs = st.tabs([
        "🏗️ Architecture Overview",
        "📦 Domain Layer",
        "⚙️ Application Layer",
        "🔌 Adapters Layer",
        "💉 Dependency Injection",
        "🧪 Live Test"
    ])

    with tabs[0]:
        st.header("Architecture Overview")
        st.markdown("""
        ### Current Structure:
        ```
        qa-shipping/
        ├── domain/          # Core business logic
        │   ├── models/      # Portal, Configuration
        │   └── ports/       # Interfaces
        ├── application/     # Use cases & orchestration
        │   ├── use_cases/   # SetupEnvironmentUseCase
        │   └── services/    # PortalOrchestrator
        ├── adapters/        # External integrations
        │   ├── primary/     # Web, CLI (driving)
        │   └── secondary/   # Database, Files (driven)
        └── infrastructure/  # Framework & tools
            ├── container.py # Dependency injection
            └── factories/   # Configuration factory
        ```
        """)

        # Show layer dependencies
        st.subheader("✅ Dependency Rules")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("Domain → Nothing")
            st.caption("Pure business logic")

        with col2:
            st.info("Application → Domain")
            st.caption("Uses domain models")

        with col3:
            st.warning("Adapters → Application")
            st.caption("Implements ports")

    with tabs[1]:
        st.header("Domain Layer Test")

        # Test Portal model
        st.subheader("Portal Domain Model")

        test_portal = Portal(
            id="test",
            name="Test Portal",
            port=8080,
            type=PortalType.SETUP,
            status=PortalStatus.STOPPED,
            description="Test portal",
            module_path="test.module"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Portal Properties:**")
            st.json({
                "id": test_portal.id,
                "name": test_portal.name,
                "port": test_portal.port,
                "type": test_portal.type.value,
                "status": test_portal.status.value
            })

        with col2:
            st.write("**Business Logic:**")
            st.write(f"Is Active: {test_portal.is_active()}")
            st.write(f"Can Start: {test_portal.can_start()}")
            st.write(f"Is Valid: {test_portal.validate()}")

            # Test status changes
            if st.button("Toggle Status"):
                if test_portal.status == PortalStatus.STOPPED:
                    test_portal.status = PortalStatus.RUNNING
                else:
                    test_portal.status = PortalStatus.STOPPED
                st.rerun()

        st.info("✅ Domain model has business logic but no framework dependencies!")

    with tabs[2]:
        st.header("Application Layer Test")

        st.subheader("Use Case: Setup Environment")

        # Show the use case flow
        st.markdown("""
        ```python
        # SetupEnvironmentUseCase orchestrates:
        1. Load configuration (via repository port)
        2. Validate credentials (via validator service)
        3. Install packages (via installer service)
        4. Return results as DTO
        ```
        """)

        # Create a mock setup request
        setup_request = SetupRequest(
            environment="development",
            validate_credentials=st.checkbox("Validate Credentials", value=True),
            install_packages=st.checkbox("Install Packages", value=False)
        )

        st.write("**Request Configuration:**")
        st.json({
            "environment": setup_request.environment,
            "validate_credentials": setup_request.validate_credentials,
            "install_packages": setup_request.install_packages
        })

        st.info("✅ Application layer orchestrates without knowing implementation details!")

    with tabs[3]:
        st.header("Adapters Layer Test")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Primary Adapters")
            st.markdown("""
            **Current Portal (Web Adapter):**
            - Location: `/adapters/primary/web/setup/`
            - Implements: Web interface port
            - Drives: Application use cases
            """)

            st.markdown("""
            **CLI Scripts:**
            - Location: `/adapters/primary/cli/`
            - Implements: CLI interface port
            - Drives: Application use cases
            """)

        with col2:
            st.subheader("🔧 Secondary Adapters")
            st.markdown("""
            **YAML Config Repository:**
            - Location: `/adapters/secondary/yaml/`
            - Implements: ConfigurationRepositoryPort
            - Driven by: Application layer
            """)

            st.markdown("""
            **In-Memory Portal Repository:**
            - Location: `/adapters/secondary/memory/`
            - Implements: PortalRepositoryPort
            - Driven by: Application layer
            """)

        st.success("✅ Adapters are swappable - could replace YAML with database!")

    with tabs[4]:
        st.header("Dependency Injection Test")

        st.subheader("Container Configuration")

        # Get the container
        container = get_container()

        # Show registered services
        st.write("**Registered Services:**")
        services = {
            "Services": list(container.services.keys()) if container.services else [],
            "Singletons": list(container.singletons.keys()) if container.singletons else [],
            "Factories": list(container.factories.keys()) if container.factories else []
        }

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Services", len(services["Services"]))
        with col2:
            st.metric("Singletons", len(services["Singletons"]))
        with col3:
            st.metric("Factories", len(services["Factories"]))

        # Wire dependencies
        if st.button("Wire Dependencies"):
            try:
                context = container.wire()
                st.success("✅ Dependencies wired successfully!")

                # Show wired components
                st.write("**Application Context:**")
                st.json({
                    "infrastructure": list(context.get("infrastructure", {}).keys()),
                    "repositories": list(context.get("repositories", {}).keys()),
                    "use_cases": list(context.get("use_cases", {}).keys())
                })
            except Exception as e:
                st.error(f"Wiring failed: {e}")

        st.info("✅ DI Container manages all dependencies and wiring!")

    with tabs[5]:
        st.header("🧪 Live Architecture Test")

        st.subheader("End-to-End Test")

        if st.button("Run Complete Test", type="primary"):
            with st.spinner("Running architecture test..."):
                results = run_live_test()

                # Show results
                for result in results:
                    if result["success"]:
                        st.success(f"✅ {result['test']}: {result['message']}")
                    else:
                        st.error(f"❌ {result['test']}: {result['message']}")

        st.markdown("---")
        st.subheader("Architecture Benefits")

        benefits = {
            "🎯 Clean Separation": "Business logic isolated from frameworks",
            "🔄 Testability": "Can test domain without infrastructure",
            "🔌 Flexibility": "Easy to swap databases, UIs, etc.",
            "📦 Maintainability": "Clear boundaries between layers",
            "⚡ Scalability": "Can evolve each layer independently"
        }

        for benefit, description in benefits.items():
            st.write(f"**{benefit}:** {description}")


def run_live_test():
    """Run a live test of the architecture"""
    results = []

    # Test 1: Domain model creation
    try:
        portal = Portal(
            id="live-test",
            name="Live Test Portal",
            port=9999,
            type=PortalType.SETUP,
            status=PortalStatus.STOPPED,
            description="Live test",
            module_path="test.live"
        )
        results.append({
            "test": "Domain Model Creation",
            "success": portal.validate(),
            "message": "Portal model created and validated"
        })
    except Exception as e:
        results.append({
            "test": "Domain Model Creation",
            "success": False,
            "message": str(e)
        })

    # Test 2: Repository adapter
    try:
        from adapters.secondary.in_memory_portal_repository import InMemoryPortalRepository
        repo = InMemoryPortalRepository()

        # Run async operation
        async def test_repo():
            portals = await repo.find_all()
            return len(portals) > 0

        success = asyncio.run(test_repo())
        results.append({
            "test": "Repository Adapter",
            "success": success,
            "message": f"In-memory repository initialized with default portals"
        })
    except Exception as e:
        results.append({
            "test": "Repository Adapter",
            "success": False,
            "message": str(e)
        })

    # Test 3: Configuration factory
    try:
        from infrastructure.factories.config_factory import ConfigurationFactory
        config = ConfigurationFactory.create_default()
        results.append({
            "test": "Configuration Factory",
            "success": config.is_valid(),
            "message": f"Default configuration created with {config.architecture.pattern} pattern"
        })
    except Exception as e:
        results.append({
            "test": "Configuration Factory",
            "success": False,
            "message": str(e)
        })

    # Test 4: Dependency injection
    try:
        from infrastructure.container import get_container, reset_container
        reset_container()
        container = get_container()
        context = container.wire()
        results.append({
            "test": "Dependency Injection",
            "success": "use_cases" in context,
            "message": "DI container wired all components"
        })
    except Exception as e:
        results.append({
            "test": "Dependency Injection",
            "success": False,
            "message": str(e)
        })

    return results


if __name__ == "__main__":
    test_architecture()