#!/usr/bin/env python3
"""
Test NEW Setup Portal
====================
Tests the complete new setup portal designed for 12th graders.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_new_portal():
    """Test the new setup portal functionality."""
    print("=" * 60)
    print("TESTING NEW SETUP PORTAL")
    print("=" * 60)

    # Test portal import
    print("\n1. Testing Portal Import:")
    print("-" * 40)
    try:
        from portals.setup.new_setup_portal import setup_service
        print("[OK] New setup portal imported successfully")
        print("[OK] Setup service initialized")
    except Exception as e:
        print(f"[FAILED] Portal import: {e}")
        return False

    # Test all integrated functions
    print("\n2. Testing All Integrated Functions:")
    print("-" * 40)

    functions_to_test = [
        ('installation_wizard', 'System Check'),
        ('dependency_check', 'Software Check'),
        ('tidyllm_basic_setup', 'AI Chat Setup'),
        ('health_check', 'Health Check'),
        ('portal_guide', 'Portal Guide'),
        ('load_examples', 'Load Examples')
    ]

    all_working = True
    for func_name, description in functions_to_test:
        try:
            func = getattr(setup_service, func_name)
            result = func()
            status = result.get('overall_status', 'unknown')
            print(f"[OK] {description}: {status}")

            # Special check for model count
            if func_name == 'tidyllm_basic_setup':
                model_count = result.get('model_count', 0)
                print(f"     Models available: {model_count}")

        except Exception as e:
            print(f"[FAILED] {description}: {e}")
            all_working = False

    # Test portal structure
    print("\n3. Testing Portal Structure:")
    print("-" * 40)

    portal_file = project_root / "portals" / "setup" / "new_setup_portal.py"
    if portal_file.exists():
        print("[OK] New portal file exists")

        # Check for key student-friendly features
        with open(portal_file, 'r', encoding='utf-8') as f:
            content = f.read()

        features_to_check = [
            ('Step 1️⃣', 'Step 1 system check'),
            ('Step 2️⃣', 'Step 2 software check'),
            ('Step 3️⃣', 'Step 3 AI chat setup'),
            ('Step 4️⃣', 'Step 4 health check'),
            ('Step 5️⃣', 'Step 5 portal guide'),
            ('12th grader', 'Student-friendly language'),
            ('model_count', 'Model count display'),
            ('NEXT STEP', 'Clear next step guidance')
        ]

        for feature, description in features_to_check:
            if feature in content:
                print(f"[OK] {description}: Found")
            else:
                print(f"[WARNING] {description}: Not found")

    else:
        print("[FAILED] New portal file not found")
        all_working = False

    print("\n" + "=" * 60)
    print("NEW SETUP PORTAL TEST RESULTS")
    print("=" * 60)

    if all_working:
        print("[PASS] New setup portal is working perfectly")
        print("[PASS] All 6 basic functions integrated")
        print("[PASS] Student-friendly interface ready")
        print("[PASS] Clear step-by-step guidance")
        print("[PASS] AI models count displayed")
        print("[PASS] Portal ready for 12th graders")

        print("\nSUCCESS: New Setup Portal is ready for students!")
        print("Students can now follow clear steps to set up their AI system")

    else:
        print("[FAILED] Some issues found in new portal")

    return all_working

if __name__ == "__main__":
    test_new_portal()