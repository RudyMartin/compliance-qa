#!/usr/bin/env python3
"""Test dependency check to see what's actually failing."""

from pathlib import Path
from domain.services.setup_service import SetupService
import json

# Initialize service
setup_service = SetupService(str(Path.cwd()))

# Run dependency check
result = setup_service.dependency_check()

print("=" * 60)
print("DEPENDENCY CHECK RESULTS")
print("=" * 60)

# Print overall status
print(f"\nOverall Status: {result['overall_status']}")
print(f"Summary: {result['summary']}")

# Print each check result
print("\nDetailed Results:")
print("-" * 40)

for check, passed in result['results'].items():
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} - {check}: {passed}")

# Check specifics for AWS
print("\n" + "=" * 60)
print("AWS CREDENTIAL SOURCES CHECK")
print("=" * 60)

import os
from infrastructure.yaml_loader import get_settings_loader
from infrastructure.services.aws_service import get_aws_service

settings_loader = get_settings_loader()
bedrock_config = settings_loader.get_bedrock_config()

print(f"1. Bedrock config has access_key_id: {bool(bedrock_config.get('access_key_id'))}")
print(f"2. AWS_ACCESS_KEY_ID in environment: {bool(os.getenv('AWS_ACCESS_KEY_ID'))}")
print(f"3. AWS credentials file exists: {(Path.home() / '.aws' / 'credentials').exists()}")

aws_service = get_aws_service()
print(f"4. AWS Service is_available(): {aws_service.is_available()}")

print("\nBedrock config keys:", list(bedrock_config.keys()) if bedrock_config else "Empty")

print("\nFull result JSON:")
print(json.dumps(result, indent=2))