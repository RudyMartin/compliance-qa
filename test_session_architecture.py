#!/usr/bin/env python3
"""
Session Architecture Test
=========================
Test the new session management using hexagonal architecture.
"""

import sys
from pathlib import Path
import asyncio

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the session components
from domain.ports.outbound.session_port import SessionPort, DatabaseSessionPort, AWSSessionPort, CredentialPort
from adapters.secondary.session.unified_session_adapter import UnifiedSessionAdapter
from infrastructure.container import get_container, reset_container


async def test_session_port_interface():
    """Test that session adapter implements all port interfaces"""
    print("\n[TEST] Session Port Interface")
    print("-" * 40)

    adapter = UnifiedSessionAdapter()

    # Check that adapter implements all ports
    implements_session = isinstance(adapter, SessionPort)
    implements_database = isinstance(adapter, DatabaseSessionPort)
    implements_aws = isinstance(adapter, AWSSessionPort)
    implements_credential = isinstance(adapter, CredentialPort)

    print(f"Implements SessionPort: {implements_session}")
    print(f"Implements DatabaseSessionPort: {implements_database}")
    print(f"Implements AWSSessionPort: {implements_aws}")
    print(f"Implements CredentialPort: {implements_credential}")

    all_implemented = all([implements_session, implements_database, implements_aws, implements_credential])
    print(f"All ports implemented: {all_implemented}")

    return all_implemented


async def test_session_functionality():
    """Test session functionality through ports"""
    print("\n[TEST] Session Functionality")
    print("-" * 40)

    adapter = UnifiedSessionAdapter()

    try:
        # Test connection status
        status = await adapter.get_connection_status()
        print(f"Connection status retrieved: {status.get('overall_health', 'unknown')}")

        # Test credential validation
        cred_status = await adapter.get_credential_status()
        print(f"Credential validation completed: {len(cred_status)} services checked")

        # Test individual service tests
        for service in ["aws", "database"]:
            try:
                result = await adapter.test_connection(service)
                print(f"  - {service}: {result.get('success', False)}")
            except Exception as e:
                print(f"  - {service}: Failed ({e})")

        return True

    except Exception as e:
        print(f"Session functionality test failed: {e}")
        return False


async def test_dependency_injection_with_session():
    """Test that DI container properly wires session adapter"""
    print("\n[TEST] DI Container with Session")
    print("-" * 40)

    try:
        # Reset and wire container
        reset_container()
        container = get_container()
        context = container.wire()

        # Check that session adapter is in context
        session_adapter = context.get("adapters", {}).get("session")
        has_session = session_adapter is not None

        print(f"Session adapter in context: {has_session}")

        if has_session:
            # Test that it implements the right interfaces
            is_session_port = isinstance(session_adapter, SessionPort)
            print(f"Session adapter implements SessionPort: {is_session_port}")

            # Test that we can use it
            status = await session_adapter.get_connection_status()
            print(f"Session adapter functional: {status.get('overall_health') != 'error'}")

        return has_session

    except Exception as e:
        print(f"DI container test failed: {e}")
        return False


async def test_session_isolation():
    """Test that session is properly isolated from domain"""
    print("\n[TEST] Session Isolation")
    print("-" * 40)

    # Check that domain models don't import session directly
    try:
        from domain.models import portal, configuration
        import inspect

        # Get all imports from domain modules
        portal_imports = [name for name, obj in inspect.getmembers(portal) if inspect.ismodule(obj)]
        config_imports = [name for name, obj in inspect.getmembers(configuration) if inspect.ismodule(obj)]

        # Check for session-related imports
        session_imports = [imp for imp in portal_imports + config_imports if 'session' in imp.lower()]

        print(f"Domain portal imports: {portal_imports}")
        print(f"Domain config imports: {config_imports}")
        print(f"Session-related imports in domain: {session_imports}")

        isolated = len(session_imports) == 0
        print(f"Domain properly isolated from session: {isolated}")

        return isolated

    except Exception as e:
        print(f"Session isolation test failed: {e}")
        return False


def show_architecture_improvement():
    """Show how the new architecture improves on the old"""
    print("\n[IMPROVEMENT] Session Architecture")
    print("-" * 40)

    print("BEFORE (Legacy):")
    print("  - UnifiedSessionManager imported everywhere")
    print("  - Direct coupling between business logic and infrastructure")
    print("  - Hard to test (requires real AWS/DB connections)")
    print("  - Violates dependency inversion principle")

    print("\nAFTER (Hexagonal):")
    print("  ✅ Domain defines session port interfaces")
    print("  ✅ Adapter implements all session ports")
    print("  ✅ DI container manages the wiring")
    print("  ✅ Easy to mock for testing")
    print("  ✅ Business logic doesn't know about infrastructure")

    print("\nKey Benefits:")
    print("  🎯 Testability: Can inject mock session for unit tests")
    print("  🔄 Flexibility: Can swap session implementations")
    print("  📦 Isolation: Domain layer has no infrastructure dependencies")
    print("  🔌 Standards: Follows port/adapter pattern consistently")


async def main():
    """Run all session architecture tests"""
    print("=" * 50)
    print("SESSION ARCHITECTURE TEST SUITE")
    print("=" * 50)

    tests = [
        ("Session Port Interface", test_session_port_interface),
        ("Session Functionality", test_session_functionality),
        ("DI Container with Session", test_dependency_injection_with_session),
        ("Session Isolation", test_session_isolation)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("SESSION TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    # Show improvement
    show_architecture_improvement()

    if passed == total:
        print("\n[SUCCESS] Session architecture properly implemented!")
        print("The legacy session management has been successfully")
        print("transformed into a proper hexagonal architecture!")
    else:
        print("\n[WARNING] Some session tests failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)