#!/usr/bin/env python3
"""
CLI Test for Hexagonal Architecture
===================================
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our hexagonal components
from domain.models.portal import Portal, PortalStatus, PortalType
from domain.models.configuration import Configuration, ArchitectureConfig
from adapters.secondary.in_memory_portal_repository import InMemoryPortalRepository
from adapters.secondary.yaml_config_repository import YamlConfigRepository
from infrastructure.container import get_container, reset_container
from infrastructure.factories.config_factory import ConfigurationFactory


def test_domain_layer():
    """Test domain models work without dependencies"""
    print("\n[TEST] Domain Layer")
    print("-" * 40)

    # Create portal model
    portal = Portal(
        id="test",
        name="Test Portal",
        port=8080,
        type=PortalType.SETUP,
        status=PortalStatus.STOPPED,
        description="Test portal",
        module_path="test.module"
    )

    print(f"Created portal: {portal.name}")
    print(f"  - Is active: {portal.is_active()}")
    print(f"  - Can start: {portal.can_start()}")
    print(f"  - Is valid: {portal.validate()}")

    # Test business logic
    portal.status = PortalStatus.RUNNING
    print(f"  - After starting: is_active={portal.is_active()}, can_start={portal.can_start()}")

    return True


def test_repository_adapter():
    """Test repository adapters"""
    print("\n[TEST] Repository Adapters")
    print("-" * 40)

    async def run_test():
        # Test in-memory repository
        repo = InMemoryPortalRepository()
        portals = await repo.find_all()
        print(f"In-memory repo has {len(portals)} default portals")

        # Test finding by port
        portal_8512 = await repo.find_by_port(8512)
        if portal_8512:
            print(f"Found portal on port 8512: {portal_8512.name}")

        return len(portals) > 0

    result = asyncio.run(run_test())
    return result


def test_configuration_factory():
    """Test configuration factory"""
    print("\n[TEST] Configuration Factory")
    print("-" * 40)

    # Create default configuration
    config = ConfigurationFactory.create_default()
    print(f"Created default configuration")
    print(f"  - Architecture: {config.architecture.pattern}")
    print(f"  - Layers: {', '.join(config.architecture.layers)}")
    print(f"  - Is valid: {config.is_valid()}")

    # Create from environment
    env_config = ConfigurationFactory.create_from_env()
    print(f"Created configuration from environment")
    print(f"  - Has database: {env_config.has_database()}")
    print(f"  - Has AWS: {env_config.has_aws()}")

    return config.is_valid()


def test_dependency_injection():
    """Test dependency injection container"""
    print("\n[TEST] Dependency Injection")
    print("-" * 40)

    try:
        # Reset and get container
        reset_container()
        container = get_container()

        # Wire dependencies
        context = container.wire()

        print("DI Container wired successfully!")
        print(f"  - Infrastructure components: {list(context['infrastructure'].keys())}")
        print(f"  - Repositories: {list(context['repositories'].keys())}")
        print(f"  - Use cases: {list(context['use_cases'].keys())}")

        return True
    except Exception as e:
        print(f"DI Container failed: {e}")
        return False


def test_hexagonal_principles():
    """Verify hexagonal architecture principles"""
    print("\n[TEST] Hexagonal Architecture Principles")
    print("-" * 40)

    # Check domain has no external dependencies
    import inspect
    from domain.models import portal

    portal_imports = [name for name, _ in inspect.getmembers(portal, inspect.ismodule)]
    external_deps = [imp for imp in portal_imports if not imp.startswith('_')]

    print(f"Domain portal model imports: {external_deps}")
    if any('domain' not in imp and imp not in ['dataclasses', 'typing', 'enum'] for imp in external_deps):
        print("  [FAIL] Domain has external dependencies!")
        return False
    else:
        print("  [OK] Domain has no external dependencies")

    # Check adapters implement ports
    from adapters.secondary.in_memory_portal_repository import InMemoryPortalRepository
    from domain.ports.outbound.repository_port import PortalRepositoryPort

    if issubclass(InMemoryPortalRepository, PortalRepositoryPort):
        print("  [OK] Repository adapter implements port interface")
    else:
        print("  [FAIL] Repository adapter doesn't implement port!")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 50)
    print("HEXAGONAL ARCHITECTURE TEST SUITE")
    print("=" * 50)

    tests = [
        ("Domain Layer", test_domain_layer),
        ("Repository Adapters", test_repository_adapter),
        ("Configuration Factory", test_configuration_factory),
        ("Dependency Injection", test_dependency_injection),
        ("Hexagonal Principles", test_hexagonal_principles)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All hexagonal architecture tests passed!")
    else:
        print("\n[WARNING] Some tests failed - check implementation")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)