#!/usr/bin/env python3
"""
Test Dynamic Credential Carrier - TRUE dynamic loading
"""

import logging
from infrastructure.services.dynamic_credential_carrier import get_dynamic_credential_carrier

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dynamic_credential_discovery():
    """Test the dynamic credential discovery system"""

    print("=== DYNAMIC CREDENTIAL CARRIER TEST ===")
    print()

    # Get the dynamic credential carrier
    carrier = get_dynamic_credential_carrier()

    # 1. Show all discovered sources
    print("1. ALL DISCOVERED CREDENTIAL SOURCES:")
    print("-" * 50)

    discovered = carrier.get_all_discovered_sources()
    for source_id, source_info in discovered.items():
        print(f"  [{source_info['type'].upper()}] {source_id}")
        print(f"    Category: {source_info['category']}")
        print(f"    Source: {source_info['source']}")
        print(f"    Name: {source_info['name']}")
        print()

    # 2. Show loaded credentials by type
    print("2. CREDENTIALS BY TYPE:")
    print("-" * 30)

    for cred_type in ['aws', 'database', 'api', 'llm_service', 'generic']:
        creds = carrier.get_credentials_by_type(cred_type)
        print(f"  {cred_type.upper()} Credentials: {len(creds)} found")
        for source_id in creds:
            print(f"    - {source_id}")
    print()

    # 3. Show specific credential examples
    print("3. SPECIFIC CREDENTIAL EXAMPLES:")
    print("-" * 35)

    # AWS credentials
    aws_creds = carrier.get_credentials_by_type('aws')
    if aws_creds:
        first_aws = list(aws_creds.keys())[0]
        creds = aws_creds[first_aws]
        print(f"  AWS Example ({first_aws}):")
        print(f"    Access Key: {creds.get('access_key_id', 'N/A')}")
        print(f"    Region: {creds.get('region', 'N/A')}")
        print()

    # Database credentials
    db_creds = carrier.get_credentials_by_type('database')
    if db_creds:
        for db_id, creds in db_creds.items():
            print(f"  Database ({db_id}):")
            print(f"    Host: {creds.get('host', 'N/A')}")
            print(f"    Database: {creds.get('database', 'N/A')}")
            print(f"    Engine: {creds.get('engine', 'N/A')}")
            print()

    # 4. Show credential status
    print("4. CREDENTIAL STATUS:")
    print("-" * 20)

    status = carrier.get_credential_status()
    for source_id, info in status.items():
        available = "[AVAILABLE]" if info['available'] else "[MISSING]"
        valid = "[VALID]" if info['valid'] else "[INVALID]"
        print(f"  {source_id}: {available} {valid}")
        print(f"    Type: {info['type']} | Category: {info['category']}")
        print(f"    Source: {info['source']}")
        print()

    # 5. Test dynamic access
    print("5. DYNAMIC ACCESS TESTS:")
    print("-" * 25)

    # Try to get credentials by name
    postgresql_creds = carrier.get_credentials_by_name('postgresql')
    if postgresql_creds:
        print("  [SUCCESS] Found PostgreSQL credentials dynamically")
        print(f"    Host: {postgresql_creds.get('host', 'N/A')}")
    else:
        print("  [INFO] No PostgreSQL credentials found")

    backup_db_creds = carrier.get_credentials_by_name('backup_db')
    if backup_db_creds:
        print("  [SUCCESS] Found backup_db credentials dynamically")
        print(f"    Engine: {backup_db_creds.get('engine', 'N/A')}")
    else:
        print("  [INFO] No backup_db credentials found")

    print()

    # 6. LLM Configuration Tests
    print("6. LLM CONFIGURATION TESTS:")
    print("-" * 30)

    bedrock_config = carrier.get_bedrock_configuration()
    if bedrock_config:
        print("  [SUCCESS] Found Bedrock configuration")
        print(f"    Default Model: {bedrock_config.get('default_model', 'N/A')}")
        print(f"    Region: {bedrock_config.get('region', 'N/A')}")
        print(f"    Available Models: {len(bedrock_config.get('model_mapping', {}))}")

        models = carrier.get_available_models()
        for model_name, model_id in models.items():
            print(f"      - {model_name}: {model_id}")

        adapter_config = carrier.get_llm_adapter_config()
        if adapter_config:
            print(f"    Adapter Config: {list(adapter_config.keys())}")
    else:
        print("  [INFO] No Bedrock configuration found")

    print()
    print("=" * 60)
    print("[RESULT] DYNAMIC CREDENTIAL DISCOVERY COMPLETE!")
    print(f"Total sources discovered: {len(discovered)}")
    print(f"Total credentials loaded: {len([s for s in status.values() if s['available']])}")

    # Count LLM services specifically
    llm_count = len(carrier.get_credentials_by_type('llm_service'))
    if llm_count > 0:
        print(f"LLM services discovered: {llm_count} [CRITICAL FOR AI PROCESSING!]")

    print("=" * 60)

if __name__ == "__main__":
    test_dynamic_credential_discovery()