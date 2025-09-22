#!/usr/bin/env python3
"""
Environment Validation Script for compliance-qa Portal System

Validates all system prerequisites before portal startup.
Part of Phase 1: Security & Configuration Cleanup.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.credential_validator import validate_all_credentials, quick_health_check
from config.environment_manager import get_environment_manager, validate_environment
from config.portal_config import get_portal_config_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("COMPLIANCE-QA PORTAL SYSTEM - Environment Validation")
    print("=" * 60)
    print("Phase 1: Security & Configuration Cleanup")
    print("Validating system prerequisites...")
    print()


def print_section(title: str):
    """Print section header."""
    print(f"\n{'-' * 20} {title} {'-' * 20}")


async def validate_system_environment():
    """Validate system environment configuration."""
    print_section("SYSTEM ENVIRONMENT")

    env_mgr = get_environment_manager()
    summary = env_mgr.get_environment_summary()

    print(f"Environment: {summary['environment']}")
    print(f"Config Sources:")
    for component, source in summary['config_sources'].items():
        print(f"  {component}: {source}")

    print(f"\nValidation Results:")
    all_valid = True
    for component, valid in summary['validation_results'].items():
        status = "[PASS]" if valid else "[FAIL]"
        print(f"  {component}: {status}")
        if not valid:
            all_valid = False

    return all_valid


async def validate_credentials():
    """Validate all system credentials."""
    print_section("CREDENTIAL VALIDATION")

    report = await validate_all_credentials()

    print(f"Overall Status: {report['overall_status'].upper()}")
    print(f"Summary: {report['summary']['successful']}/{report['summary']['total_checks']} checks passed")

    if report['summary']['warnings'] > 0:
        print(f"Warnings: {report['summary']['warnings']}")

    if report['summary']['errors'] > 0:
        print(f"Errors: {report['summary']['errors']}")

    print("\nDetailed Results:")
    for result in report['results']:
        status_icon = {"success": "[OK]", "warning": "[WARN]", "error": "[FAIL]"}[result['status']]
        print(f"  {status_icon} {result['component']}: {result['message']}")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

    return report['overall_status'] in ['healthy', 'degraded']


def validate_portal_configuration():
    """Validate portal configuration."""
    print_section("PORTAL CONFIGURATION")

    config_mgr = get_portal_config_manager()
    summary = config_mgr.get_portal_summary()

    print(f"Total Portals: {summary['total_portals']}")
    print(f"Enabled Portals: {summary['enabled_portals']}")
    print(f"Disabled Portals: {summary['disabled_portals']}")

    print(f"\nPortal Categories:")
    for category, count in summary['categories'].items():
        print(f"  {category}: {count} portals")

    print(f"\nPortal Registry:")
    for portal in summary['portal_list']:
        status = "[ON]" if portal['enabled'] else "[OFF]"
        print(f"  {status} {portal['name']} ({portal['title']}) - Port {portal['port']}")

    return summary['enabled_portals'] > 0


async def perform_quick_health_check():
    """Perform quick health check on essential services."""
    print_section("QUICK HEALTH CHECK")

    print("Checking essential services...")
    healthy = await quick_health_check()

    if healthy:
        print("[OK] All essential services are healthy")
    else:
        print("[FAIL] Some essential services are not available")
        print("   Check database connectivity and credentials")

    return healthy


def check_environment_variables():
    """Check for required environment variables."""
    print_section("ENVIRONMENT VARIABLES")

    # Critical environment variables
    critical_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD'
    ]

    # Optional but recommended variables
    optional_vars = [
        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION',
        'MLFLOW_TRACKING_URI', 'ENVIRONMENT', 'LOG_LEVEL'
    ]

    all_critical_set = True

    print("Critical Variables:")
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            print(f"  [OK] {var}: Set")
        else:
            print(f"  [FAIL] {var}: Not set")
            all_critical_set = False

    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  [OK] {var}: Set")
        else:
            print(f"  [WARN] {var}: Not set (using default)")

    return all_critical_set


async def main():
    """Main validation routine."""
    print_banner()

    validation_results = []

    # 1. Check environment variables
    env_vars_ok = check_environment_variables()
    validation_results.append(("Environment Variables", env_vars_ok))

    # 2. Validate system environment
    env_ok = await validate_system_environment()
    validation_results.append(("System Environment", env_ok))

    # 3. Validate credentials
    creds_ok = await validate_credentials()
    validation_results.append(("Credentials", creds_ok))

    # 4. Validate portal configuration
    portal_ok = validate_portal_configuration()
    validation_results.append(("Portal Configuration", portal_ok))

    # 5. Quick health check
    health_ok = await perform_quick_health_check()
    validation_results.append(("Health Check", health_ok))

    # Summary
    print_section("VALIDATION SUMMARY")

    all_passed = True
    for component, passed in validation_results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {component}: {status}")
        if not passed:
            all_passed = False

    print(f"\nOverall Status: {'[SYSTEM READY]' if all_passed else '[SYSTEM NOT READY]'}")

    if not all_passed:
        print("\nRequired Actions:")
        print("  1. Set missing environment variables")
        print("  2. Fix credential configuration issues")
        print("  3. Ensure database connectivity")
        print("  4. Run validation again before starting portals")

        return 1  # Exit code 1 for failure

    print("\nSystem is ready for portal startup!")
    return 0  # Exit code 0 for success


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        print(f"\n[FAIL] Validation failed: {e}")
        sys.exit(1)