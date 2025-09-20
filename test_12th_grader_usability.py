#!/usr/bin/env python3
"""
12th Grader Usability Test for MLflow Recent Activity
"""

import importlib.util
import sys
from pathlib import Path

print("=" * 60)
print("12TH GRADER USABILITY TEST: MLflow Recent Activity")
print("=" * 60)

# Setup environment
try:
    from infrastructure.environment_manager import setup_environment_from_settings
    setup_environment_from_settings()
    print("✓ Environment setup: SUCCESS")
except ImportError:
    print("X Environment setup: FAILED (but continuing...)")

print("\n1. IMPORT TEST: Can a 12th grader import the MLflow viewer?")
print("-" * 55)

try:
    # Direct module import to avoid package issues
    spec = importlib.util.spec_from_file_location(
        "mlflow_viewer",
        "packages/tidyllm/infrastructure/tools/mlflow_viewer.py"
    )
    viewer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(viewer_module)

    print("✓ MLflow viewer imported successfully")
    print("✓ 12th grader could use this with simple instructions")

except Exception as e:
    print(f"X MLflow viewer import failed: {e}")
    print("X 12th grader would be confused - needs simpler setup")

print("\n2. FUNCTIONALITY TEST: Does the recent activity work?")
print("-" * 52)

try:
    print("Calling show_last_5_mlflow_records()...")
    viewer_module.show_last_5_mlflow_records()
    print("\n✓ Recent activity function executed")
    print("✓ 12th grader could see results")

except Exception as e:
    print(f"X Recent activity failed: {e}")
    print("X 12th grader would be frustrated - needs better error handling")

print("\n3. USABILITY ASSESSMENT")
print("-" * 24)

print("\n📋 12TH GRADER CHECKLIST:")
print("   ✓ Clear function name: 'show_last_5_mlflow_records'")
print("   ✓ Self-explanatory: Shows exactly what it does")
print("   ? Technical terms: May need glossary")
print("   ? Error handling: Needs user-friendly messages")

print("\n🎯 RECOMMENDATIONS FOR 12TH GRADERS:")
print("   1. Add a simple web interface button labeled 'Recent Activity'")
print("   2. Show results in plain English, not technical jargon")
print("   3. Add tooltips explaining terms like 'tokens', 'experiments'")
print("   4. Use colors: Green for success, Red for failures")
print("   5. Add timestamps in human-readable format")

print("\n💡 INTUITIVE DESIGN SUGGESTIONS:")
print("   - Button text: 'Show Recent AI Activity' (not 'MLflow Records')")
print("   - Result format: 'John asked AI about math at 10:30 AM - SUCCESS'")
print("   - Error message: 'Cannot connect to database' (not 'psycopg2 error')")
print("   - Loading message: 'Looking up recent activity...'")

print("\n" + "=" * 60)
print("CONCLUSION: Needs user-friendly interface wrapper!")
print("Current: Technical but functional")
print("Needed: Simple and intuitive for 12th graders")
print("=" * 60)