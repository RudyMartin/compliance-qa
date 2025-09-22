"""
Test Registry Loading
=====================

Check if the WorkflowRegistry loads all workflows including test ones.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "portals" / "flow"))

# Import the registry
from flow_creator_v3_modular import WorkflowRegistry

def test_registry_loading():
    """Test that the registry loads all workflows."""

    print("=" * 70)
    print("TESTING WORKFLOW REGISTRY LOADING")
    print("=" * 70)

    # Create registry instance
    registry = WorkflowRegistry()

    print(f"\n[INFO] Registry path: {registry.workflows_base_path}")
    print(f"[INFO] Path exists: {registry.workflows_base_path.exists()}")

    # Get loaded workflows
    workflows = registry.workflows

    print(f"\n[INFO] Total workflows loaded: {len(workflows)}")
    print("-" * 70)

    # List all workflows
    for workflow_id, workflow_data in workflows.items():
        print(f"\n{workflow_id}:")
        print(f"  Name: {workflow_data.get('workflow_name', 'N/A')}")
        print(f"  Type: {workflow_data.get('workflow_type', 'N/A')}")
        print(f"  Description: {workflow_data.get('description', 'N/A')[:60]}...")

        # Check for action steps
        project_path = registry.workflows_base_path / workflow_id
        action_steps_path = project_path / "action_steps"
        if action_steps_path.exists():
            action_step_files = list(action_steps_path.glob("*.json"))
            # Exclude config file from count
            step_count = len([f for f in action_step_files if f.name != "action_steps_config.json"])
            print(f"  Action Steps: {step_count}")

    # Check specifically for our test workflows
    print("\n" + "=" * 70)
    print("CHECKING FOR TEST WORKFLOWS")
    print("-" * 70)

    test_workflows = [
        "document_compliance_checker",
        "test_action_workflow"
    ]

    for test_id in test_workflows:
        if test_id in workflows:
            print(f"[OK] Found: {test_id}")
        else:
            print(f"[MISSING] Not found: {test_id}")

    print("\n" + "=" * 70)
    print("REGISTRY LOADING TEST COMPLETE")
    print("=" * 70)

    return workflows

if __name__ == "__main__":
    workflows = test_registry_loading()

    if "document_compliance_checker" in workflows and "test_action_workflow" in workflows:
        print("\n[SUCCESS] Both test workflows appear in the registry!")
    else:
        print("\n[INFO] Test workflows not showing - check demo filter settings")