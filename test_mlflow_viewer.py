#!/usr/bin/env python3
"""
Test the updated MLflow viewer service with standardized approach
"""

# Use existing environment management infrastructure
try:
    from infrastructure.environment_manager import setup_environment_from_settings
    setup_environment_from_settings()
except ImportError:
    pass

# Load test configuration
try:
    from infrastructure.settings_loader import get_settings_loader
    settings_loader = get_settings_loader()
    test_config = settings_loader._load_settings().get('testing', {}).get('standardized_config', {})
    MAX_RETRIES = test_config.get('max_retries', 3)
    DEFAULT_TIMEOUT = test_config.get('default_timeout', 30)
except ImportError:
    MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 30

print("=" * 60)
print("TESTING UPDATED MLFLOW VIEWER SERVICE")
print("=" * 60)

try:
    # Import the updated viewer
    from packages.tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records

    print("Testing MLflow viewer with standardized approach...")
    print("-" * 50)

    # Run the viewer
    show_last_5_mlflow_records()

    print("\n" + "=" * 60)
    print("MLFLOW VIEWER TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

except Exception as e:
    print(f"[ERROR] MLflow viewer test failed: {e}")
    print("This may be due to:")
    print("- Infrastructure services not available")
    print("- MLflow service not running")
    print("- Database connection issues")
    print("- Missing enhanced MLflow service")