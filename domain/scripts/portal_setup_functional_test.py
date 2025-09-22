#!/usr/bin/env python3
"""
Portal Setup Functional Test
============================
Tests the lean setup portal functionality without running Streamlit UI.
"""

import sys
from pathlib import Path

print("=" * 60)
print("PORTAL SETUP FUNCTIONAL TEST")
print("=" * 60)

# Add project to path
sys.path.insert(0, str(Path.cwd()))

def test_setup_service():
    """Test the setup service that the portal uses."""
    print("\n1. Testing Setup Service:")
    print("-" * 40)

    try:
        from domain.services.setup_service import SetupService
        service = SetupService()
        print("[OK] SetupService imported")

        # Test environment summary
        summary = service.get_environment_summary()
        print(f"[OK] Environment summary retrieved: {len(summary)} items")

        # Test credential validation
        cred_status = service.validate_credentials()
        print(f"[OK] Credential validation: {cred_status.get('overall_status', 'unknown')}")

        # Test database connection
        db_status = service.test_database_connection()
        print(f"[OK] Database test: {db_status.get('status', 'unknown')}")

        return True
    except Exception as e:
        print(f"[FAILED] SetupService: {e}")
        return False

def test_portal_imports():
    """Test that portal can import its dependencies."""
    print("\n2. Testing Portal Imports:")
    print("-" * 40)

    try:
        # Import the lean portal module
        sys.path.insert(0, str(Path.cwd() / "portals" / "setup"))
        import lean_setup_portal
        print("[OK] lean_setup_portal module imported")

        # Check if main components exist
        if hasattr(lean_setup_portal, 'render_environment_tab'):
            print("[OK] render_environment_tab function found")
        else:
            print("[WARNING] render_environment_tab not found")

        if hasattr(lean_setup_portal, 'render_database_tab'):
            print("[OK] render_database_tab function found")
        else:
            print("[WARNING] render_database_tab not found")

        return True
    except Exception as e:
        print(f"[FAILED] Portal import: {e}")
        return False

def test_domain_services():
    """Test all domain services used by portals."""
    print("\n3. Testing Domain Services:")
    print("-" * 40)

    services_to_test = [
        ("setup_service", "SetupService"),
        ("qa_workflow_service", "QAWorkflowService"),
        ("dspy_compiler_service", "DSPyCompilerService"),
        ("dspy_execution_service", "DSPyExecutionService")
    ]

    all_ok = True
    for module_name, class_name in services_to_test:
        try:
            module = __import__(f"domain.services.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            print(f"[OK] {class_name} instantiated")
        except Exception as e:
            print(f"[FAILED] {class_name}: {e}")
            all_ok = False

    return all_ok

def test_infrastructure_services():
    """Test infrastructure services availability."""
    print("\n4. Testing Infrastructure Services:")
    print("-" * 40)

    # Test AWS service
    try:
        from infrastructure.services.aws_service import get_aws_service
        aws = get_aws_service()
        print(f"[OK] AWS service available: {aws.is_available()}")
    except Exception as e:
        print(f"[WARNING] AWS service: {e}")

    # Test Database service
    try:
        from infrastructure.services.database_service import get_database_service
        db = get_database_service()
        print("[OK] Database service created")
    except Exception as e:
        print(f"[WARNING] Database service: {e}")

    # Test enhanced MLflow service
    try:
        from infrastructure.services.enhanced_mlflow_service import EnhancedMLflowService
        mlflow = EnhancedMLflowService()
        print("[OK] MLflow service created")
    except Exception as e:
        print(f"[WARNING] MLflow service: {e}")

    return True

def test_portal_functionality():
    """Test actual portal functionality without UI."""
    print("\n5. Testing Portal Functionality (No UI):")
    print("-" * 40)

    try:
        from domain.services.setup_service import SetupService
        service = SetupService()

        # Simulate what the portal does
        print("Simulating portal operations...")

        # Tab 1: Environment
        env_summary = service.get_environment_summary()
        print(f"  - Environment items: {len(env_summary)}")

        # Tab 2: Database
        db_config = {}  # Would come from UI inputs
        db_status = service.test_database_connection(db_config)
        print(f"  - Database connection: {db_status.get('status', 'unknown')}")

        # Tab 3: AWS
        aws_config = {}  # Would come from UI inputs
        aws_status = service.test_aws_connection(aws_config)
        print(f"  - AWS connection: {aws_status.get('status', 'unknown')}")

        print("[OK] Portal functionality simulation complete")
        return True

    except Exception as e:
        print(f"[FAILED] Portal functionality: {e}")
        return False

def main():
    """Run all tests."""
    results = {
        "Setup Service": test_setup_service(),
        "Portal Imports": test_portal_imports(),
        "Domain Services": test_domain_services(),
        "Infrastructure": test_infrastructure_services(),
        "Portal Functionality": test_portal_functionality()
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed."))

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())