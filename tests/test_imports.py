#!/usr/bin/env python3
"""
Test Import Script
==================
Tests all the import paths to identify what's broken.
"""

import sys
from pathlib import Path

print("=" * 60)
print("IMPORT TEST DIAGNOSTIC")
print("=" * 60)

# Test 1: Basic path setup
print("\n1. Path Information:")
print(f"Current working directory: {Path.cwd()}")
print(f"Python executable: {sys.executable}")
print(f"Python path entries:")
for p in sys.path[:5]:
    print(f"  - {p}")

# Test 2: Infrastructure imports
print("\n2. Testing Infrastructure Imports:")

try:
    from infrastructure.environment_manager import EnvironmentManager
    print("[OK] infrastructure.environment_manager")
except ImportError as e:
    print(f"[FAILED] infrastructure.environment_manager: {e}")

try:
    from infrastructure.environment_manager import get_environment_manager
    print("[OK] get_environment_manager")
except ImportError as e:
    print(f"[FAILED] get_environment_manager: {e}")

try:
    from infrastructure.credential_validator import CredentialValidator
    print("[OK] infrastructure.credential_validator")
except ImportError as e:
    print(f"[FAILED] infrastructure.credential_validator: {e}")

try:
    from infrastructure.yaml_loader import get_settings_loader
    print("[OK] infrastructure.yaml_loader")
except ImportError as e:
    print(f"[FAILED] infrastructure.yaml_loader: {e}")

try:
    from infrastructure.portal_config import get_portal_config_manager
    print("[OK] infrastructure.portal_config")
except ImportError as e:
    print(f"[FAILED] infrastructure.portal_config: {e}")

# Test 3: Domain imports
print("\n3. Testing Domain Imports:")

try:
    from domain.services.setup_service import SetupService
    print("[OK] domain.services.setup_service")
except ImportError as e:
    print(f"[FAILED] domain.services.setup_service: {e}")

try:
    from domain.services.qa_workflow_service import QAWorkflowService
    print("[OK] domain.services.qa_workflow_service")
except ImportError as e:
    print(f"[FAILED] domain.services.qa_workflow_service: {e}")

# Test 4: Check if files exist
print("\n4. Checking File Existence:")

files_to_check = [
    "infrastructure/environment_manager.py",
    "infrastructure/credential_validator.py",
    "infrastructure/yaml_loader.py",
    "infrastructure/portal_config.py",
    "domain/services/setup_service.py",
    "domain/services/qa_workflow_service.py"
]

for file_path in files_to_check:
    full_path = Path(file_path)
    if full_path.exists():
        print(f"[OK] {file_path} - EXISTS")
    else:
        print(f"[FAILED] {file_path} - NOT FOUND")

# Test 5: Check __init__ files
print("\n5. Checking __init__.py Files:")

init_files = [
    "infrastructure/__init__.py",
    "domain/__init__.py",
    "domain/services/__init__.py"
]

for init_file in init_files:
    init_path = Path(init_file)
    if init_path.exists():
        print(f"[OK] {init_file} - EXISTS")
    else:
        print(f"[MISSING] {init_file} - May need to create")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)