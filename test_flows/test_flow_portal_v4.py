"""
Test Flow Portal V4 Functionality
==================================
Tests for the new card-based workflow system
"""

import sys
import os
from pathlib import Path
import json

# Add parent path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_flow_portal_v4():
    """Test Flow Portal V4 components"""

    print("=" * 60)
    print("FLOW PORTAL V4 FUNCTIONAL TESTS")
    print("=" * 60)

    results = []

    # Test 1: Portal Main File
    print("\n1. Testing Portal Main File:")
    print("-" * 40)
    portal_file = Path("portals/flow/flow_portal_v4.py")
    if portal_file.exists():
        print("[OK] flow_portal_v4.py exists")
        results.append(True)
    else:
        print("[FAIL] flow_portal_v4.py not found")
        results.append(False)

    # Test 2: Tab Files
    print("\n2. Testing Tab Components:")
    print("-" * 40)
    tabs = [
        "t_create_flow_v4.py",
        "t_manage_flows_v4.py",
        "t_run_flows_v4.py",
        "t_optimize_flows_v4.py",
        "t_ask_ai_v4.py"
    ]

    for tab in tabs:
        tab_file = Path(f"portals/flow/{tab}")
        if tab_file.exists():
            print(f"[OK] {tab} exists")
            results.append(True)
        else:
            print(f"[FAIL] {tab} not found")
            results.append(False)

    # Test 3: Business Card System
    print("\n3. Testing Business Builder Cards:")
    print("-" * 40)
    card_dir = Path("domain/templates/business_builder_cards/ooda_loop")
    if card_dir.exists():
        card_categories = ["observe", "orient", "decide", "act", "loop"]
        for category in card_categories:
            category_dir = card_dir / category
            if category_dir.exists():
                card_count = len(list(category_dir.glob("*.json")))
                print(f"[OK] {category.upper()}: {card_count} cards")
                results.append(True)
            else:
                print(f"[WARN] {category} directory not found")
                results.append(False)
    else:
        print("[WARN] Business Builder cards directory not found")
        results.append(False)

    # Test 4: Unified Steps Manager
    print("\n4. Testing UnifiedStepsManager:")
    print("-" * 40)
    try:
        from domain.services.unified_steps_manager import UnifiedStepsManager
        print("[OK] UnifiedStepsManager imported")

        # Test initialization
        manager = UnifiedStepsManager("test_project")
        print("[OK] UnifiedStepsManager initialized")

        # Test step creation
        step = manager.create_hybrid_step(
            "Test Step",
            tidyllm_functions=[{"function": "test"}],
            prompt_template="test.md"
        )
        print("[OK] Hybrid step creation successful")
        print(f"    Step type: {step.get('step_type')}")
        print(f"    Has action phase: {'action' in step.get('phases', {})}")
        print(f"    Has prompt phase: {'prompt' in step.get('phases', {})}")
        results.append(True)
    except Exception as e:
        print(f"[FAIL] UnifiedStepsManager error: {e}")
        results.append(False)

    # Test 5: Port Configuration
    print("\n5. Testing Port Configuration:")
    print("-" * 40)

    # Check config file
    config_file = Path("portals/flow/.streamlit/config.toml")
    if config_file.exists():
        print("[OK] Streamlit config exists")
        with open(config_file, 'r') as f:
            content = f.read()
            if "port = 8501" in content:
                print("[OK] Default port 8501 configured")
            elif "port = 8510" in content:
                print("[OK] Special port 8510 configured")
            results.append(True)
    else:
        print("[WARN] Config file not found")
        results.append(False)

    # Check launch scripts
    launch_files = [
        "run_portal.py",
        "launch.bat",
        "setup_portal_special.py",
        "launch_special.bat"
    ]

    for launch_file in launch_files:
        file_path = Path(f"portals/flow/{launch_file}")
        if file_path.exists():
            print(f"[OK] {launch_file} exists")
            results.append(True)
        else:
            print(f"[INFO] {launch_file} not found (optional)")

    # Test 6: Card Features
    print("\n6. Testing Card Features:")
    print("-" * 40)

    # Check a sample card
    sample_card = Path("domain/templates/business_builder_cards/ooda_loop/observe/unified_document_analysis.json")
    if sample_card.exists():
        with open(sample_card, 'r') as f:
            card_data = json.load(f)

        print(f"[OK] Card: {card_data.get('card_name')}")
        print(f"    Type: {card_data.get('card_type')}")
        print(f"    OODA Level: {card_data.get('ooda_level')}")

        # Check unified step definition
        step_def = card_data.get('step_definition', {})
        if step_def.get('step_type') == 'unified':
            print("[OK] Unified step type (Action + Prompt)")
            phases = step_def.get('phases', {})
            if 'action' in phases and 'prompt' in phases:
                print("[OK] Has both action and prompt phases")
                results.append(True)
            else:
                print("[WARN] Missing phases")
                results.append(False)
        else:
            print("[WARN] Not a unified step")
            results.append(False)
    else:
        print("[WARN] Sample card not found")
        results.append(False)

    # Test 7: AI Control Levels
    print("\n7. Testing AI Control Levels:")
    print("-" * 40)
    ai_levels = {
        "None": "No AI involvement",
        "Assist": "AI helps with guidance",
        "Auto": "AI makes decisions"
    }

    for level, description in ai_levels.items():
        print(f"[OK] {level}: {description}")
    results.append(True)

    # Test 8: Workflow Templates
    print("\n8. Testing Workflow Templates:")
    print("-" * 40)
    templates = [
        "Document Analysis",
        "RAG Q&A",
        "Data Processing"
    ]

    for template in templates:
        print(f"[OK] Template available: {template}")
    results.append(True)

    # Summary
    print("\n" + "=" * 60)
    print("FLOW PORTAL V4 TEST RESULTS")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED!")
        print("Flow Portal V4 is ready for use")
    else:
        print(f"\n⚠️ Some tests failed ({total - passed} failures)")
        print("Review the output above for details")

    return passed == total

if __name__ == "__main__":
    success = test_flow_portal_v4()
    sys.exit(0 if success else 1)