#!/usr/bin/env python3
"""
Analyze the current settings.yaml structure to understand dynamic requirements
"""

import yaml
from pathlib import Path

def analyze_settings_structure():
    """Analyze what's actually in settings.yaml"""

    settings_path = Path("infrastructure/settings.yaml")

    with open(settings_path, 'r') as f:
        settings = yaml.safe_load(f)

    print("=== SETTINGS.YAML STRUCTURE ANALYSIS ===")
    print()

    # Analyze credentials section
    print("[CREDS] CREDENTIALS SECTION:")
    if 'credentials' in settings:
        creds = settings['credentials']
        for service, config in creds.items():
            print(f"  [KEY] {service}:")
            if isinstance(config, dict):
                for key, value in config.items():
                    if isinstance(value, dict):
                        print(f"    [NESTED] {key}: {list(value.keys())}")
                    else:
                        print(f"    [VALUE] {key}: {type(value).__name__}")

    # Analyze databases section
    print("\n[DB] DATABASES SECTION:")
    if 'databases' in settings:
        dbs = settings['databases']
        for db_name, config in dbs.items():
            print(f"  [DB] {db_name}: {config.get('type', 'unknown')} ({config.get('engine', 'unknown')})")

    # Analyze services section
    print("\n[SVC] SERVICES SECTION:")
    if 'services' in settings:
        services = settings['services']
        for service_name, config in services.items():
            print(f"  [SVC] {service_name}: {list(config.keys()) if isinstance(config, dict) else type(config).__name__}")

    # Analyze integrations section
    print("\n[INT] INTEGRATIONS SECTION:")
    if 'integrations' in settings:
        integrations = settings['integrations']
        for integration_name, config in integrations.items():
            enabled = config.get('enabled', False) if isinstance(config, dict) else False
            print(f"  [INT] {integration_name}: {'[ENABLED]' if enabled else '[DISABLED]'}")

    # Show the architectural challenge
    print("\n" + "="*60)
    print("[ALERT] ARCHITECTURAL CHALLENGE:")
    print("="*60)
    print("Current credential carrier only handles:")
    print("  - 'aws' credentials")
    print("  - 'database' credentials (mapped to postgresql)")
    print()
    print("But settings.yaml actually contains:")
    print("  - Multiple credential sources")
    print("  - Multiple database configurations")
    print("  - Multiple service configurations")
    print("  - Dynamic integration settings")
    print()
    print("❌ This is NOT dynamic - it's hardcoded!")

if __name__ == "__main__":
    analyze_settings_structure()