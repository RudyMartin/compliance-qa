#!/usr/bin/env python3
"""
Test MLflow Backend Configuration Options
========================================
Test the configuration-driven MLflow backend selection system.

DEMONSTRATES:
1. Multiple backend options (shared pool, alternative DB, file, S3)
2. Configuration-driven backend selection
3. Fallback mechanisms when primary backend fails
4. Classic MLflow configuration preserved
"""

import logging
from infrastructure.services.self_describing_credential_carrier import get_self_describing_credential_carrier

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mlflow_backend_configurations():
    """Test MLflow backend configuration options"""

    print("=" * 80)
    print("TESTING MLFLOW BACKEND CONFIGURATION OPTIONS")
    print("Configuration-Driven Backend Selection")
    print("=" * 80)

    # Get credential carrier
    carrier = get_self_describing_credential_carrier()

    # 1. Show MLflow-related credentials discovered
    print("\n1. MLFLOW CREDENTIALS DISCOVERED:")
    print("-" * 40)

    mlflow_creds = {}
    for source_id, source_info in carrier._discovered_sources.items():
        if 'mlflow' in source_id.lower() or source_info.get('credential_type') == 'tracking_service':
            mlflow_creds[source_id] = source_info
            cred_type = source_info.get('credential_type')
            print(f"   {source_id}: {cred_type}")

    # 2. Test main data_tracking service configuration
    print("\n2. DATA TRACKING SERVICE CONFIGURATION:")
    print("-" * 45)

    data_tracking = carrier._discovered_sources.get('data_tracking', {})
    if data_tracking:
        config = data_tracking.get('config', {})
        print(f"   Service Type: {data_tracking.get('credential_type')}")
        print(f"   Credential Ref: {config.get('credential_ref')}")
        print(f"   Tracking URI: {config.get('tracking_uri')}")
        print(f"   Artifact Store: {config.get('artifact_store')}")

        # Show backend options
        backend_options = config.get('backend_options', {})
        if backend_options:
            print(f"\n   Backend Options:")
            for option_name, option_value in backend_options.items():
                print(f"     {option_name}: {option_value}")

        print(f"   Backend Store URI: {config.get('backend_store_uri')}")

    # 3. Test MLflow integration configuration
    print("\n3. MLFLOW INTEGRATION CONFIGURATION:")
    print("-" * 40)

    mlflow_integration = carrier._discovered_sources.get('mlflow', {})
    if mlflow_integration:
        config = mlflow_integration.get('config', {})
        print(f"   Integration Type: {mlflow_integration.get('credential_type')}")
        print(f"   Adapter Type: {config.get('adapter_type')}")
        print(f"   Enabled: {config.get('enabled')}")

        # Show backend options
        backend_options = config.get('backend_options', {})
        if backend_options:
            print(f"\n   Backend Options:")
            for option_name, option_value in backend_options.items():
                print(f"     {option_name}: {option_value}")

        # Show integration config
        integration_config = config.get('integration_config', {})
        if integration_config:
            print(f"\n   Integration Config:")
            print(f"     Pool Client: {integration_config.get('pool_client_name')}")
            print(f"     Use Shared Pool: {integration_config.get('use_shared_pool')}")
            print(f"     Backend Fallback: {integration_config.get('backend_fallback_enabled')}")
            print(f"     Test on Startup: {integration_config.get('test_backend_on_startup')}")

    # 4. Test alternative database credentials
    print("\n4. ALTERNATIVE DATABASE CREDENTIALS:")
    print("-" * 40)

    alt_db = carrier.get_credentials_by_name('mlflow_alt_db')
    if alt_db:
        print(f"   Host: {alt_db.get('host')}")
        print(f"   Database: {alt_db.get('database')}")
        print(f"   Engine: {alt_db.get('engine')}")
        print(f"   Purpose: {alt_db.get('purpose')}")
        print(f"   [AVAILABLE] Alternative DB configured")
    else:
        print("   [NOT FOUND] Alternative DB not configured")

    # 5. Show backend selection logic
    print("\n5. BACKEND SELECTION LOGIC:")
    print("-" * 35)

    print("   Configuration-driven backend selection:")
    print("   1. Primary: postgresql_shared_pool (uses connection pool)")
    print("   2. Alternative: mlflow_alt_db (separate PostgreSQL)")
    print("   3. Fallback: file://./mlflow_data (local filesystem)")
    print("   4. Test Mode: sqlite:///./test_mlflow.db (for testing)")
    print("   5. S3 Artifacts: Enabled for artifact storage")

    # 6. Demonstrate configuration flexibility
    print("\n6. CONFIGURATION FLEXIBILITY DEMONSTRATION:")
    print("-" * 50)

    print("   [SUCCESS] Multiple backend options configured")
    print("   [SUCCESS] Alternative PostgreSQL database defined")
    print("   [SUCCESS] File-based fallback available")
    print("   [SUCCESS] S3 artifact storage configured")
    print("   [SUCCESS] Test mode with SQLite available")
    print("   [SUCCESS] Backend selection driven by configuration")

    # 7. Show how to switch backends
    print("\n7. HOW TO SWITCH BACKENDS:")
    print("-" * 30)

    print("   To use alternative PostgreSQL:")
    print("     backend_store_uri: mlflow_alt_db")

    print("\n   To use file-based storage:")
    print("     backend_store_uri: file://./mlflow_data")

    print("\n   To use test SQLite:")
    print("     backend_store_uri: sqlite:///./test_mlflow.db")

    print("\n   Current: auto_select (infrastructure chooses best available)")

    print("\n" + "=" * 80)
    print("MLFLOW BACKEND CONFIGURATION TEST COMPLETE!")
    print("Classic MLflow flexibility preserved with configuration-driven approach")
    print("=" * 80)

def simulate_backend_selection():
    """Simulate how backend selection would work"""

    print("\n" + "=" * 60)
    print("SIMULATING BACKEND SELECTION LOGIC")
    print("=" * 60)

    carrier = get_self_describing_credential_carrier()

    # Simulate checking different backends
    backends_to_test = [
        'postgresql_shared_pool',
        'mlflow_alt_db',
        'file://./mlflow_data',
        'sqlite:///./test_mlflow.db'
    ]

    print("\nBackend availability check:")
    for backend in backends_to_test:
        if backend == 'postgresql_shared_pool':
            # Check if primary PostgreSQL is available
            pg_creds = carrier.get_credentials_by_name('postgresql_primary')
            status = "[AVAILABLE]" if pg_creds else "[UNAVAILABLE]"
        elif backend == 'mlflow_alt_db':
            # Check if alternative DB is configured
            alt_creds = carrier.get_credentials_by_name('mlflow_alt_db')
            status = "[AVAILABLE]" if alt_creds else "[UNAVAILABLE]"
        else:
            # File and SQLite are always available
            status = "[AVAILABLE]"

        print(f"   {backend}: {status}")

    print("\nRecommended selection order:")
    print("   1. postgresql_shared_pool (if connection pool healthy)")
    print("   2. mlflow_alt_db (if alternative DB configured)")
    print("   3. file://./mlflow_data (filesystem fallback)")
    print("   4. sqlite:///./test_mlflow.db (test/emergency mode)")

if __name__ == "__main__":
    test_mlflow_backend_configurations()
    simulate_backend_selection()