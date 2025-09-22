"""
Functional Tests for Manage Tab CRUD Operations
===============================================
Real tests that interact with the WorkflowManager and verify CRUD operations
"""

import sys
import os
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "portals" / "flow"))

# Import the enhanced manage tab
from t_manage_flows_enhanced import WorkflowManager


class TestWorkflowCRUD:
    """Test workflow CRUD operations"""

    def __init__(self):
        """Setup test environment with temporary directory"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_workflows_file = self.temp_dir / "portal_workflows.json"
        self.test_versions_dir = self.temp_dir / "versions"
        self.test_versions_dir.mkdir()

        # Create test data
        self.test_data = {
            "workflows": {
                "Test Workflow 1": {
                    "name": "Test Workflow 1",
                    "version": "1.0",
                    "created": "2025-01-14",
                    "description": "Test workflow for CRUD operations",
                    "cards": [
                        {"id": "extract_doc", "name": "📄 Extract Document", "category": "observe", "ai_level": "None"},
                        {"id": "analyze_content", "name": "💡 Analyze Content", "category": "orient", "ai_level": "Assist"}
                    ]
                },
                "Test Workflow 2": {
                    "name": "Test Workflow 2",
                    "version": "2.0",
                    "created": "2025-01-14",
                    "description": "Second test workflow",
                    "cards": [
                        {"id": "load_data", "name": "📊 Load Data", "category": "observe", "ai_level": "None"}
                    ]
                }
            }
        }

        # Write test data
        with open(self.test_workflows_file, 'w') as f:
            json.dump(self.test_data, f)

        # Create manager with test paths
        self.manager = WorkflowManager(project_name=None)  # Test global workflows
        self.manager.workflows_file = self.test_workflows_file
        self.manager.versions_dir = self.test_versions_dir

    def cleanup(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_workflow(self):
        """Test creating a new workflow"""
        print("\n[TEST] Create Workflow")
        print("-" * 40)

        # Load existing workflows
        workflows = self.manager.load_workflows()
        initial_count = len(workflows)
        print(f"Initial workflows: {initial_count}")

        # Create new workflow
        new_workflow = {
            "name": "Created Test Workflow",
            "version": "1.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "description": "Created via test",
            "cards": []
        }

        # Add to workflows
        workflows["Created Test Workflow"] = new_workflow

        # Save
        success = self.manager.save_workflows(workflows)
        assert success, "Failed to save workflow"
        print("[OK] Workflow saved")

        # Verify persistence
        loaded = self.manager.load_workflows()
        assert len(loaded) == initial_count + 1, "Workflow count incorrect"
        assert "Created Test Workflow" in loaded, "New workflow not found"
        print(f"[OK] Workflow persisted. Count: {len(loaded)}")

        # Verify content
        created = loaded["Created Test Workflow"]
        assert created["name"] == "Created Test Workflow"
        assert created["version"] == "1.0"
        assert created["description"] == "Created via test"
        assert len(created["cards"]) == 0
        print("[OK] Workflow content verified")

        return True

    def test_read_workflow(self):
        """Test reading existing workflows"""
        print("\n[TEST] Read Workflow")
        print("-" * 40)

        workflows = self.manager.load_workflows()

        # Test read existing
        assert "Test Workflow 1" in workflows, "Workflow 1 not found"
        workflow1 = workflows["Test Workflow 1"]

        print(f"Read workflow: {workflow1['name']}")
        assert workflow1["version"] == "1.0"
        assert len(workflow1["cards"]) == 2
        print(f"[OK] Version: {workflow1['version']}, Cards: {len(workflow1['cards'])}")

        # Test read all
        assert len(workflows) >= 2, "Not all workflows loaded"
        print(f"[OK] Loaded {len(workflows)} workflows")

        # Test non-existent
        assert "NonExistent" not in workflows
        print("[OK] Non-existent workflow returns None")

        return True

    def test_update_workflow(self):
        """Test updating workflow properties"""
        print("\n[TEST] Update Workflow")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        # Store original
        original_version = workflow["version"]
        original_desc = workflow.get("description", "")
        print(f"Original version: {original_version}")

        # Update metadata
        workflow["version"] = "1.1"
        workflow["description"] = "Updated description"
        workflow["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save
        success = self.manager.save_workflows(workflows)
        assert success, "Failed to save updates"
        print("[OK] Updates saved")

        # Verify persistence
        loaded = self.manager.load_workflows()
        updated = loaded["Test Workflow 1"]
        assert updated["version"] == "1.1", "Version not updated"
        assert updated["description"] == "Updated description", "Description not updated"
        assert "last_modified" in updated, "Timestamp not added"
        print(f"[OK] Updated to version {updated['version']}")

        return True

    def test_delete_workflow(self):
        """Test deleting a workflow"""
        print("\n[TEST] Delete Workflow")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        initial_count = len(workflows)
        print(f"Initial count: {initial_count}")

        # Verify workflow exists
        assert "Test Workflow 2" in workflows
        to_delete = workflows["Test Workflow 2"]

        # Create backup before delete (archive)
        self.manager.create_version_backup("DELETED_Test_Workflow_2", to_delete)

        # Check backup created
        backups = list(self.test_versions_dir.glob("DELETED_*.json"))
        assert len(backups) > 0, "Backup not created"
        print(f"[OK] Backup created: {backups[0].name}")

        # Delete
        del workflows["Test Workflow 2"]

        # Save
        success = self.manager.save_workflows(workflows)
        assert success, "Failed to save after delete"

        # Verify deleted
        loaded = self.manager.load_workflows()
        assert "Test Workflow 2" not in loaded, "Workflow not deleted"
        assert len(loaded) == initial_count - 1, "Count incorrect after delete"
        print(f"[OK] Workflow deleted. Remaining: {len(loaded)}")

        return True

    def test_validate_workflow_name(self):
        """Test workflow name validation"""
        print("\n[TEST] Validate Workflow Name")
        print("-" * 40)

        # Test empty name
        valid, error = self.manager.validate_workflow_name("")
        assert not valid, "Empty name should be invalid"
        assert "empty" in error.lower()
        print("[OK] Empty name rejected")

        # Test duplicate name
        valid, error = self.manager.validate_workflow_name("Test Workflow 1")
        assert not valid, "Duplicate name should be invalid"
        assert "exists" in error.lower()
        print("[OK] Duplicate name rejected")

        # Test valid new name
        valid, error = self.manager.validate_workflow_name("Valid New Name")
        assert valid, "Valid name should pass"
        assert error == ""
        print("[OK] Valid name accepted")

        # Test rename (same name allowed)
        valid, error = self.manager.validate_workflow_name("Test Workflow 1", "Test Workflow 1")
        assert valid, "Same name should be allowed when renaming"
        print("[OK] Same name allowed for current workflow")

        return True


class TestCardCRUD:
    """Test card CRUD operations within workflows"""

    def __init__(self, manager):
        self.manager = manager

    def test_add_card(self):
        """Test adding cards to workflow"""
        print("\n[TEST] Add Card")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        initial_count = len(workflow["cards"])
        print(f"Initial cards: {initial_count}")

        # Add new card
        new_card = {
            "id": "create_report",
            "name": "📝 Create Report",
            "category": "act",
            "ai_level": "Assist"
        }

        workflow["cards"].append(new_card)

        # Save
        self.manager.save_workflows(workflows)

        # Verify
        loaded = self.manager.load_workflows()
        updated = loaded["Test Workflow 1"]
        assert len(updated["cards"]) == initial_count + 1
        print(f"[OK] Card added. Total: {len(updated['cards'])}")

        # Verify card content
        last_card = updated["cards"][-1]
        assert last_card["id"] == "create_report"
        assert last_card["ai_level"] == "Assist"
        # Handle potential emoji in output
        card_name = last_card['name'].encode('utf-8', 'ignore').decode('ascii', 'ignore')
        print(f"[OK] Card details: {card_name}")

        return True

    def test_update_card(self):
        """Test updating card properties"""
        print("\n[TEST] Update Card")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        # Get first card
        card = workflow["cards"][0]
        original_ai = card["ai_level"]
        print(f"Original AI level: {original_ai}")

        # Update AI level
        card["ai_level"] = "Auto"
        card["parameters"] = {
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Save
        self.manager.save_workflows(workflows)

        # Verify
        loaded = self.manager.load_workflows()
        updated_card = loaded["Test Workflow 1"]["cards"][0]
        assert updated_card["ai_level"] == "Auto"
        assert "parameters" in updated_card
        assert updated_card["parameters"]["temperature"] == 0.7
        print(f"[OK] AI level updated to: {updated_card['ai_level']}")
        print(f"[OK] Parameters added: {updated_card['parameters']}")

        return True

    def test_reorder_cards(self):
        """Test reordering cards in workflow"""
        print("\n[TEST] Reorder Cards")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        # Get original order
        original_first = workflow["cards"][0]["id"]
        original_second = workflow["cards"][1]["id"]
        print(f"Original order: [{original_first}, {original_second}]")

        # Swap cards
        workflow["cards"][0], workflow["cards"][1] = workflow["cards"][1], workflow["cards"][0]

        # Save
        self.manager.save_workflows(workflows)

        # Verify
        loaded = self.manager.load_workflows()
        reordered = loaded["Test Workflow 1"]["cards"]
        assert reordered[0]["id"] == original_second
        assert reordered[1]["id"] == original_first
        print(f"[OK] New order: [{reordered[0]['id']}, {reordered[1]['id']}]")

        return True

    def test_delete_card(self):
        """Test removing cards from workflow"""
        print("\n[TEST] Delete Card")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        initial_count = len(workflow["cards"])
        print(f"Initial cards: {initial_count}")

        # Store card to delete
        to_delete = workflow["cards"][0]["name"]

        # Delete first card
        workflow["cards"].pop(0)

        # Save
        self.manager.save_workflows(workflows)

        # Verify
        loaded = self.manager.load_workflows()
        updated = loaded["Test Workflow 1"]
        assert len(updated["cards"]) == initial_count - 1
        print(f"[OK] Card deleted. Remaining: {len(updated['cards'])}")

        # Verify correct card deleted
        remaining_names = [c["name"] for c in updated["cards"]]
        assert to_delete not in remaining_names
        # Handle potential emoji in output
        deleted_name = to_delete.encode('utf-8', 'ignore').decode('ascii', 'ignore')
        print(f"[OK] Deleted: {deleted_name}")

        return True

    def test_get_available_cards(self):
        """Test getting available card templates"""
        print("\n[TEST] Get Available Cards")
        print("-" * 40)

        cards = self.manager.get_available_cards()

        # Verify structure
        assert "observe" in cards
        assert "orient" in cards
        assert "decide" in cards
        assert "act" in cards
        print("[OK] All categories present")

        # Count cards
        total = sum(len(cat_cards) for cat_cards in cards.values())
        print(f"[OK] Total available cards: {total}")

        # Verify card structure
        observe_cards = cards["observe"]
        assert len(observe_cards) > 0
        first_card = observe_cards[0]
        assert "id" in first_card
        assert "name" in first_card
        assert "ai_level" in first_card
        # Handle potential emoji in output
        card_name = first_card['name'].encode('utf-8', 'ignore').decode('ascii', 'ignore')
        print(f"[OK] Card structure valid: {card_name}")

        return True


class TestVersioning:
    """Test version backup functionality"""

    def __init__(self, manager):
        self.manager = manager

    def test_create_version_backup(self):
        """Test creating version backups"""
        print("\n[TEST] Create Version Backup")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        # Create backup
        self.manager.create_version_backup("Test Workflow 1", workflow)

        # Verify backup created (note: workflow name has spaces)
        backups = list(self.manager.versions_dir.glob("Test Workflow 1_*.json"))
        assert len(backups) > 0, "No backup created"
        print(f"[OK] Backup created: {backups[0].name}")

        # Verify backup content
        with open(backups[0], 'r') as f:
            backup_data = json.load(f)

        assert backup_data["name"] == workflow["name"]
        assert backup_data["version"] == workflow["version"]
        assert len(backup_data["cards"]) == len(workflow["cards"])
        print("[OK] Backup content verified")

        return True

    def test_multiple_versions(self):
        """Test creating multiple version backups"""
        print("\n[TEST] Multiple Version Backups")
        print("-" * 40)

        workflows = self.manager.load_workflows()
        workflow = workflows["Test Workflow 1"]

        # Create multiple backups
        for i in range(3):
            workflow["version"] = f"1.{i}"
            self.manager.create_version_backup("Test Workflow 1", workflow)

        # Verify all backups created (note: workflow name has spaces)
        backups = list(self.manager.versions_dir.glob("Test Workflow 1_*.json"))
        assert len(backups) >= 3, f"Expected 3+ backups, found {len(backups)}"
        print(f"[OK] Created {len(backups)} version backups")

        # Verify each has unique name
        backup_names = [b.name for b in backups]
        assert len(backup_names) == len(set(backup_names)), "Duplicate backup names"
        print("[OK] All backups have unique names")

        return True


def run_all_tests():
    """Run all CRUD functional tests"""
    print("=" * 60)
    print("MANAGE TAB CRUD FUNCTIONAL TESTS")
    print("=" * 60)

    test_runner = TestWorkflowCRUD()
    results = []

    try:
        # Workflow CRUD Tests
        print("\n### WORKFLOW CRUD TESTS ###")
        results.append(("Create Workflow", test_runner.test_create_workflow()))
        results.append(("Read Workflow", test_runner.test_read_workflow()))
        results.append(("Update Workflow", test_runner.test_update_workflow()))
        results.append(("Delete Workflow", test_runner.test_delete_workflow()))
        results.append(("Validate Name", test_runner.test_validate_workflow_name()))

        # Card CRUD Tests
        print("\n### CARD CRUD TESTS ###")
        card_tester = TestCardCRUD(test_runner.manager)
        results.append(("Add Card", card_tester.test_add_card()))
        results.append(("Update Card", card_tester.test_update_card()))
        results.append(("Reorder Cards", card_tester.test_reorder_cards()))
        results.append(("Delete Card", card_tester.test_delete_card()))
        results.append(("Get Available Cards", card_tester.test_get_available_cards()))

        # Versioning Tests
        print("\n### VERSIONING TESTS ###")
        version_tester = TestVersioning(test_runner.manager)
        results.append(("Create Backup", version_tester.test_create_version_backup()))
        results.append(("Multiple Versions", version_tester.test_multiple_versions()))

    finally:
        # Cleanup
        test_runner.cleanup()

    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("The Manage Tab CRUD operations are fully functional!")
    else:
        print(f"\n[WARNING] {total - passed} tests failed")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)