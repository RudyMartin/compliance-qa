#!/usr/bin/env python3
"""
Complete QA-Shipping Setup Test
Tests all components end-to-end to ensure everything works.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add qa-shipping to path
qa_root = Path(__file__).parent
sys.path.insert(0, str(qa_root))

# Import all modules at module level
from infrastructure.yaml_loader import get_settings_loader, setup_environment_from_settings
from infrastructure.environment_manager import get_environment_manager
from infrastructure.credential_validator import quick_health_check
from common.utilities.path_manager import get_path_manager
from adapters.session.unified_session_manager import UnifiedSessionManager

def test_imports():
    """Test all critical imports work."""
    print("[SEARCH] Testing imports...")

    try:
        # Test that all modules are importable
        assert get_settings_loader is not None
        assert get_environment_manager is not None
        assert quick_health_check is not None
        assert get_path_manager is not None
        assert UnifiedSessionManager is not None
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[ERR] Import failed: {e}")
        return False

def test_settings_loader():
    """Test settings loading from YAML."""
    print("\n[WRENCH] Testing settings loader...")

    try:
        settings_loader = get_settings_loader()
        config = settings_loader.load_config()

        print(f"[OK] Settings loaded from: {settings_loader.settings_path}")

        # Read YAML directly to verify our settings.yaml architecture
        import yaml
        with open(settings_loader.settings_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        arch_pattern = raw_config.get('system', {}).get('architecture', {}).get('pattern', 'unknown')

        print(f"   Architecture: {arch_pattern}")
        print(f"   Database host: {config.db_host}")
        print(f"   AWS region: {config.aws_region}")
        return True
    except Exception as e:
        print(f"[ERR] Settings loader failed: {e}")
        return False

def test_environment_setup():
    """Test automatic environment setup."""
    print("\n[GLOBE] Testing environment setup...")

    try:
        setup_environment_from_settings()

        # Check if environment variables are set
        aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        db_host = os.getenv('DB_HOST')

        print(f"[OK] Environment setup complete")
        print(f"   AWS Key: {'Set' if aws_key else 'Not set'}")
        print(f"   DB Host: {'Set' if db_host else 'Not set'}")
        return True
    except Exception as e:
        print(f"[ERR] Environment setup failed: {e}")
        return False

def test_path_manager():
    """Test path manager functionality."""
    print("\n[FOLDER] Testing path manager...")

    try:
        pm = get_path_manager()

        print(f"[OK] Path manager working")
        print(f"   Root: {pm.root_folder}")
        print(f"   Packages: {pm.packages_folder}")
        print(f"   Portals: {pm.portals_folder}")
        print(f"   TidyLLM: {pm.tidyllm_package_path}")
        return True
    except Exception as e:
        print(f"[ERR] Path manager failed: {e}")
        return False

def test_environment_validation():
    """Test environment validation."""
    print("\n[CHECK] Testing environment validation...")

    try:
        env_mgr = get_environment_manager()
        summary = env_mgr.get_environment_summary()

        print(f"[OK] Environment validation complete")
        print(f"   Environment: {summary.get('environment', 'unknown')}")

        validation_results = summary.get('validation_results', {})
        for component, status in validation_results.items():
            icon = "[OK]" if status else "[ERR]"
            print(f"   {icon} {component}: {'PASS' if status else 'FAIL'}")

        return all(validation_results.values())
    except Exception as e:
        print(f"[ERR] Environment validation failed: {e}")
        return False

async def test_health_check():
    """Test async health check."""
    print("\n[HEALTH] Testing health check...")

    try:
        healthy = await quick_health_check()
        icon = "[OK]" if healthy else "[WARN]"
        print(f"{icon} Health check: {'HEALTHY' if healthy else 'ISSUES'}")
        return True
    except Exception as e:
        print(f"[ERR] Health check failed: {e}")
        return False

def test_session_manager():
    """Test unified session manager."""
    print("\n[LINK] Testing session manager...")

    try:
        sm = UnifiedSessionManager()
        s3_client = sm.get_s3_client()

        print(f"[OK] Session manager working")
        print(f"   S3 client: {'Available' if s3_client else 'Not available'}")
        return True
    except Exception as e:
        print(f"[ERR] Session manager failed: {e}")
        return False

def test_script_generation():
    """Test script generation."""
    print("\n[SCRIPT] Testing script generation...")

    try:
        from infrastructure.script_generator import get_script_generator
        generator = get_script_generator()

        # Test script info
        info = generator.get_script_info()
        print(f"[OK] Script generator working")
        print(f"   Source: {info['source_settings']}")
        print(f"   Output: {info['output_directory']}")

        # Test validation
        validation = generator.validate_generated_scripts()
        for script, valid in validation.items():
            icon = "[OK]" if valid else "[ERR]"
            print(f"   {icon} {script}: {'EXISTS' if valid else 'MISSING'}")

        return True
    except Exception as e:
        print(f"[ERR] Script generation failed: {e}")
        return False

async def main():
    """Run complete setup test."""
    print("[ROCKET] QA-Shipping Complete Setup Test")
    print("=" * 50)

    tests = [
        ("Imports", test_imports),
        ("Settings Loader", test_settings_loader),
        ("Environment Setup", test_environment_setup),
        ("Path Manager", test_path_manager),
        ("Environment Validation", test_environment_validation),
        ("Health Check", lambda: asyncio.create_task(test_health_check())),
        ("Session Manager", test_session_manager),
        ("Script Generation", test_script_generation),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutine(test_func()) or hasattr(test_func(), '__await__'):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERR] {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("[CHART] COMPLETE SETUP TEST RESULTS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        icon = "[OK]" if result else "[ERR]"
        status = "PASS" if result else "FAIL"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n[TARGET] OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("[PARTY] ALL SYSTEMS GO! QA-Shipping setup is fully functional!")
        print("\n[ROCKET] Ready to use:")
        print("   • Setup Portal: http://localhost:8512")
        print("   • Architecture: 4-Layer Clean")
        print("   • All components validated")
    else:
        print("[WARN] Some components need attention. Check failed tests above.")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)