#!/usr/bin/env python3
"""
Debug credentials loading
"""

import logging
from infrastructure.services.credential_carrier import get_credential_carrier

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_credentials():
    """Debug credential loading step by step"""

    print("=== Credential Loading Debug ===")

    # Create a fresh credential carrier
    from infrastructure.services.credential_carrier import reset_credential_carrier
    reset_credential_carrier()

    credential_carrier = get_credential_carrier()

    print("\n1. Credential sources after loading:")
    print(f"   Sources: {credential_carrier._credential_sources}")

    print("\n2. Cached credentials after loading:")
    for service, creds in credential_carrier._cached_credentials.items():
        print(f"   {service}: {type(creds)} - {list(creds.keys()) if isinstance(creds, dict) else creds}")
        if isinstance(creds, dict):
            for k, v in creds.items():
                if 'password' in k.lower() or 'secret' in k.lower():
                    print(f"     {k}: [REDACTED]")
                else:
                    print(f"     {k}: {v}")

    print("\n3. Test getting specific credentials:")
    aws_creds = credential_carrier.get_aws_credentials()
    print(f"   AWS: {'Available' if aws_creds else 'None'}")

    db_creds = credential_carrier.get_database_credentials()
    print(f"   Database: {'Available' if db_creds else 'None'}")

    print("\n4. Credential status:")
    status = credential_carrier.get_credential_status()
    for service, info in status.items():
        print(f"   {service}: {info}")

    # Test settings loader directly
    print("\n5. Test settings loader directly:")
    try:
        from infrastructure.settings_loader import get_settings_loader
        settings_loader = get_settings_loader()
        config = settings_loader.load_config()

        print(f"   Config type: {type(config)}")
        print(f"   Has credentials: {hasattr(config, 'credentials')}")

        if hasattr(config, 'credentials'):
            print(f"   Credentials type: {type(config.credentials)}")
            print(f"   Credentials attrs: {dir(config.credentials)}")

            if hasattr(config.credentials, 'postgresql'):
                print(f"   PostgreSQL type: {type(config.credentials.postgresql)}")
                print(f"   PostgreSQL attrs: {dir(config.credentials.postgresql)}")
                postgres = config.credentials.postgresql
                if hasattr(postgres, 'host'):
                    print(f"   Host: {postgres.host}")
                if hasattr(postgres, 'database'):
                    print(f"   Database: {postgres.database}")
                if hasattr(postgres, 'username'):
                    print(f"   Username: {postgres.username}")
                if hasattr(postgres, 'password'):
                    print(f"   Password: [REDACTED - Length: {len(postgres.password)}]")

    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_credentials()