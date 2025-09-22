#!/usr/bin/env python3
"""
Debug MLflow configuration to see why it's connecting to localhost
"""

from infrastructure.environment_manager import setup_environment_from_settings
setup_environment_from_settings()

print("=" * 60)
print("DEBUGGING MLFLOW CONFIGURATION")
print("=" * 60)

# Check environment variables
import os
print("Environment Variables:")
for key, value in os.environ.items():
    if 'MLFLOW' in key or 'DB' in key:
        print(f"  {key}: {value}")

print("\nMLflow Configuration:")
import mlflow
print(f"  Current tracking URI: {mlflow.get_tracking_uri()}")

print("\nCredential Carrier Test:")
try:
    from infrastructure.services.self_describing_credential_carrier import get_self_describing_credential_carrier

    carrier = get_self_describing_credential_carrier()

    # Test database credentials
    db_creds = carrier.get_credentials_by_type('database_credentials')
    print(f"  Database credentials found: {len(db_creds)}")

    for source_id, creds in db_creds.items():
        if 'postgresql' in source_id or 'primary' in source_id:
            print(f"    {source_id}: {creds.get('host', 'N/A')}:{creds.get('port', 'N/A')}")

    # Test api credentials
    api_creds = carrier.get_credentials_by_type('api_credentials')
    print(f"  API credentials found: {len(api_creds)}")

    for source_id, creds in api_creds.items():
        if 'mlflow' in source_id:
            print(f"    {source_id}: {creds.get('tracking_uri', 'N/A')}")

except Exception as e:
    print(f"  Error: {e}")

print("\nTesting manual MLflow URI setup:")
try:
    from infrastructure.services.self_describing_credential_carrier import get_self_describing_credential_carrier

    carrier = get_self_describing_credential_carrier()
    db_creds = carrier.get_credentials_by_type('database_credentials')

    # Find PostgreSQL credentials
    primary_db = None
    for source_id, creds in db_creds.items():
        if 'primary' in source_id or 'postgresql' in source_id:
            primary_db = creds
            break

    if primary_db:
        host = primary_db.get('host')
        port = primary_db.get('port', 5432)
        database = primary_db.get('database')
        username = primary_db.get('username')
        password = primary_db.get('password')

        tracking_uri = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        print(f"  Built URI: {tracking_uri[:50]}...")

        # #future_fix: Convert to use enhanced service infrastructure
        # Set tracking URI
        mlflow.set_tracking_uri(tracking_uri)
        print(f"  After setting: {mlflow.get_tracking_uri()[:50]}...")

    else:
        print("  No PostgreSQL credentials found")

except Exception as e:
    print(f"  Setup error: {e}")