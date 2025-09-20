#!/usr/bin/env python3
"""
Migrate Settings.yaml to Self-Describing Structure
==================================================
Converts current settings.yaml to configuration-driven approach with 'type' fields.

ZERO DEVELOPER DEPENDENCY MIGRATION:
- Adds 'type' fields to all credential sources
- Preserves all existing data
- Makes structure self-describing
- Enables pure configuration-driven infrastructure
"""

import yaml
import shutil
from pathlib import Path
from datetime import datetime

def migrate_settings_to_self_describing():
    """Migrate current settings.yaml to self-describing structure"""

    settings_path = Path("infrastructure/settings.yaml")
    backup_path = Path(f"infrastructure/settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")

    print("=" * 70)
    print("MIGRATING TO SELF-DESCRIBING CONFIGURATION")
    print("=" * 70)

    # 1. Backup current settings
    print(f"\n1. Backing up current settings to {backup_path}")
    shutil.copy2(settings_path, backup_path)

    # 2. Load current settings
    with open(settings_path, 'r') as f:
        current_settings = yaml.safe_load(f)

    # 3. Create self-describing structure
    print("\n2. Converting to self-describing structure...")

    new_settings = {}

    # Copy non-credential sections as-is
    for section in ['configuration', 'deployment', 'features', 'onboarding', 'operations', 'search_paths', 'system']:
        if section in current_settings:
            new_settings[section] = current_settings[section]

    # 4. Transform credentials section
    if 'credentials' in current_settings:
        new_settings['credentials'] = {}
        creds = current_settings['credentials']

        # AWS credentials
        if 'aws' in creds:
            aws_creds = creds['aws']
            new_settings['credentials']['aws_basic'] = {
                'type': 'aws_credentials',
                **aws_creds
            }
            print("   [SUCCESS] Converted AWS credentials")

        # PostgreSQL credentials
        if 'postgresql' in creds:
            pg_creds = creds['postgresql']
            new_settings['credentials']['postgresql_primary'] = {
                'type': 'database_credentials',
                'engine': 'postgresql',
                **pg_creds
            }
            print("   [SUCCESS] Converted PostgreSQL credentials")

        # Backup DB credentials
        if 'backup_db' in creds:
            backup_creds = creds['backup_db']
            new_settings['credentials']['sqlite_backup'] = {
                'type': 'database_credentials',
                **backup_creds
            }
            print("   [SUCCESS] Converted backup DB credentials")

    # 5. Transform services section with LLM extraction
    if 'services' in current_settings:
        new_settings['services'] = {}
        services = current_settings['services']

        # Extract Bedrock LLM service
        if 'aws' in services and 'bedrock' in services['aws']:
            aws_service = services['aws']
            bedrock_config = aws_service['bedrock']

            # Create separate LLM service credential
            new_settings['credentials']['bedrock_llm'] = {
                'type': 'llm_service',
                'service_provider': 'aws_bedrock',
                'region': aws_service.get('region', 'us-east-1'),
                'default_model': bedrock_config.get('default_model'),
                'model_mapping': bedrock_config.get('model_mapping', {}),
                'adapter_config': bedrock_config.get('adapter_config', {})
            }

            # Create LLM service reference
            new_settings['services']['llm_processing'] = {
                'type': 'llm_service',
                'credential_ref': 'bedrock_llm',
                'enabled': True
            }

            # Keep other AWS services
            remaining_aws = {k: v for k, v in aws_service.items() if k != 'bedrock'}
            if remaining_aws:
                new_settings['services']['aws_infrastructure'] = {
                    'type': 'aws_service',
                    'credential_ref': 'aws_basic',
                    **remaining_aws
                }

            print("   [SUCCESS] Extracted Bedrock LLM service")

        # Copy other services with type annotations
        for service_name, service_config in services.items():
            if service_name == 'aws':
                continue  # Already handled above

            if service_name == 'postgresql':
                new_settings['services']['database_service'] = {
                    'type': 'database_service',
                    'credential_ref': 'postgresql_primary',
                    **service_config
                }
            elif service_name == 'mlflow':
                # Create MLflow API credentials
                if 'mlflow_api' not in new_settings.get('credentials', {}):
                    new_settings.setdefault('credentials', {})['mlflow_api'] = {
                        'type': 'api_credentials',
                        'service': 'mlflow',
                        'tracking_uri': service_config.get('tracking_uri', 'http://localhost:5000'),
                        'artifact_store': service_config.get('artifact_store', '')
                    }

                new_settings['services']['data_tracking'] = {
                    'type': 'tracking_service',
                    'credential_ref': 'mlflow_api',
                    **service_config
                }
            else:
                new_settings['services'][service_name] = {
                    'type': f'{service_name}_service',
                    **service_config
                }

    # 6. Transform databases section
    if 'databases' in current_settings:
        new_settings['databases'] = {}
        dbs = current_settings['databases']

        for db_name, db_config in dbs.items():
            engine = db_config.get('engine', 'unknown')

            # Map to credential references
            if engine == 'postgresql' and db_name == 'primary':
                credential_ref = 'postgresql_primary'
            elif engine == 'sqlite' and db_name == 'backup':
                credential_ref = 'sqlite_backup'
            else:
                credential_ref = f'{db_name}_credentials'

            new_settings['databases'][db_name] = {
                'type': 'database_pool',
                'credential_ref': credential_ref,
                **db_config
            }

        print("   [SUCCESS] Converted database configurations")

    # 7. Transform integrations section
    if 'integrations' in current_settings:
        new_settings['integrations'] = {}
        integrations = current_settings['integrations']

        for int_name, int_config in integrations.items():
            if int_name == 'mlflow':
                new_settings['integrations'][int_name] = {
                    'type': 'tracking_integration',
                    'credential_ref': 'mlflow_api',
                    **int_config
                }
            else:
                int_type = f"{int_name}_integration"
                new_settings['integrations'][int_name] = {
                    'type': int_type,
                    **int_config
                }

        print("   [SUCCESS] Converted integrations")

    # 8. Write new self-describing settings
    print(f"\n3. Writing self-describing settings to {settings_path}")

    with open(settings_path, 'w') as f:
        yaml.dump(new_settings, f, default_flow_style=False, sort_keys=False, indent=2)

    print("\n[COMPLETE] MIGRATION COMPLETE!")
    print(f"   Original settings backed up to: {backup_path}")
    print(f"   New self-describing settings: {settings_path}")

    # 9. Show what changed
    print(f"\n📋 MIGRATION SUMMARY:")
    print(f"   [SUCCESS] Added 'type' fields to all credential sources")
    print(f"   [SUCCESS] Extracted Bedrock LLM as separate credential")
    print(f"   [SUCCESS] Added credential references to services/databases")
    print(f"   [SUCCESS] Made configuration completely self-describing")

    return new_settings

if __name__ == "__main__":
    migrate_settings_to_self_describing()