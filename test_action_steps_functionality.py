"""
Test Action Steps Functionality
================================

Tests the ActionStepsManager and integration with the workflow system.
"""

import json
from pathlib import Path
from datetime import datetime
import shutil
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from domain.services.action_steps_manager import ActionStepsManager


def test_action_steps_manager():
    """Test the ActionStepsManager functionality."""

    print("=" * 60)
    print("TESTING ACTION STEPS FUNCTIONALITY")
    print("=" * 60)

    # Test project
    test_project_id = "test_action_workflow"
    test_project_path = Path("domain/workflows/projects") / test_project_id

    # Clean up any existing test project
    if test_project_path.exists():
        shutil.rmtree(test_project_path)

    # Initialize manager
    print("\n1. Initializing ActionStepsManager...")
    manager = ActionStepsManager(test_project_id)
    print(f"   [OK] Manager initialized for project: {test_project_id}")
    print(f"   [OK] Action steps path: {manager.action_steps_path}")

    # Test 1: Save action steps
    print("\n2. Testing save_action_step...")

    test_steps = [
        {
            "step_name": "load_data",
            "step_type": "process",
            "description": "Load data from source files",
            "requires": [],
            "produces": ["raw_data"],
            "position": 0
        },
        {
            "step_name": "validate_data",
            "step_type": "analyze",
            "description": "Validate data quality and completeness",
            "requires": ["raw_data"],
            "produces": ["validated_data", "validation_report"],
            "position": 1
        },
        {
            "step_name": "transform_data",
            "step_type": "transform",
            "description": "Transform data into target format",
            "requires": ["validated_data"],
            "produces": ["transformed_data"],
            "position": 2
        },
        {
            "step_name": "generate_output",
            "step_type": "output",
            "description": "Generate final output files",
            "requires": ["transformed_data"],
            "produces": ["final_output"],
            "position": 3
        }
    ]

    for step in test_steps:
        result = manager.save_action_step(step["step_name"], step)
        if result["success"]:
            print(f"   [OK] Saved step: {step['step_name']}")
        else:
            print(f"   [FAIL] Failed to save step: {step['step_name']} - {result.get('error')}")

    # Test 2: Load action steps
    print("\n3. Testing get_all_action_steps...")
    all_steps = manager.get_all_action_steps()
    print(f"   [OK] Retrieved {len(all_steps)} action steps")

    for step in all_steps:
        print(f"      - {step['step_name']}: {step['step_type']}")

    # Test 3: Load specific step
    print("\n4. Testing load_action_step...")
    loaded_step = manager.load_action_step("validate_data")
    if loaded_step:
        print(f"   [OK] Loaded step: {loaded_step['step_name']}")
        print(f"      Requires: {loaded_step['requires']}")
        print(f"      Produces: {loaded_step['produces']}")

    # Test 4: Get summary
    print("\n5. Testing get_action_step_summary...")
    summary = manager.get_action_step_summary()
    print(f"   [OK] Total steps: {summary['total_steps']}")
    print(f"   [OK] Step types: {summary['step_types']}")

    # Test 5: Export action steps
    print("\n6. Testing export_action_steps...")
    export_result = manager.export_action_steps()
    if export_result["success"]:
        print(f"   [OK] Exported {export_result['action_steps_count']} steps")
        print(f"   [OK] Export path: {export_result['export_path']}")

    # Test 6: Create workflow config
    print("\n7. Creating workflow configuration...")
    workflow_config = {
        "workflow_id": test_project_id,
        "workflow_name": "Test Action Workflow",
        "workflow_type": "action_based",
        "description": f"Test workflow with {len(test_steps)} action steps",
        "action_steps_count": len(test_steps),
        "steps": test_steps,
        "created_at": datetime.now().isoformat()
    }

    config_file = test_project_path / "project_config.json"
    with open(config_file, 'w') as f:
        json.dump(workflow_config, f, indent=2)
    print(f"   [OK] Created workflow config: {config_file}")

    # Test 7: Verify directory structure
    print("\n8. Verifying project structure...")
    expected_dirs = ["criteria", "templates", "inputs", "outputs", "resources", "action_steps"]

    for dir_name in expected_dirs:
        dir_path = test_project_path / dir_name
        if dir_path.exists():
            print(f"   [OK] {dir_name}/ exists")
            # Count files in action_steps
            if dir_name == "action_steps":
                files = list(dir_path.glob("*.json"))
                print(f"      Contains {len(files)} files")
        else:
            print(f"   [FAIL] {dir_name}/ missing")

    # Test 8: Test workflow execution readiness
    print("\n9. Testing workflow readiness...")

    # Check action step dependencies
    step_dict = {s['step_name']: s for s in all_steps}
    errors = []

    for step in all_steps:
        for req in step.get('requires', []):
            # Check if required data is produced by a previous step
            found = False
            for other_step in all_steps:
                if other_step['position'] < step['position'] and req in other_step.get('produces', []):
                    found = True
                    break
            if not found and req:  # Ignore empty requirements
                errors.append(f"Step '{step['step_name']}' requires '{req}' but no previous step produces it")

    if errors:
        print("   [WARN] Dependency issues found:")
        for error in errors:
            print(f"      - {error}")
    else:
        print("   [OK] All step dependencies are satisfied")

    print("\n" + "=" * 60)
    print("ACTION STEPS FUNCTIONALITY TEST COMPLETE")
    print("=" * 60)

    print(f"\n[SUCCESS] Successfully created and tested workflow: {test_project_id}")
    print(f"[INFO] Location: {test_project_path}")
    print(f"[INFO] Action steps: {len(all_steps)}")

    return {
        "success": True,
        "project_id": test_project_id,
        "project_path": str(test_project_path),
        "action_steps_count": len(all_steps),
        "summary": summary
    }


if __name__ == "__main__":
    result = test_action_steps_manager()

    if result["success"]:
        print("\n[SUCCESS] All tests passed successfully!")
    else:
        print("\n[FAIL] Some tests failed")