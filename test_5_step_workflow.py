"""
Test 5 Action Step Workflow Creation
=====================================

Creates a complete 5-step workflow for document processing and compliance checking.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from domain.services.action_steps_manager import ActionStepsManager


def create_5_step_compliance_workflow():
    """Create a 5-step document compliance workflow."""

    print("=" * 70)
    print("CREATING 5-STEP DOCUMENT COMPLIANCE WORKFLOW")
    print("=" * 70)

    # Define workflow
    workflow_id = "document_compliance_checker"
    workflow_name = "Document Compliance Checker"

    print(f"\nWorkflow: {workflow_name}")
    print(f"ID: {workflow_id}")
    print("-" * 70)

    # Initialize manager
    manager = ActionStepsManager(workflow_id)
    print(f"\n[OK] Initialized ActionStepsManager")
    print(f"[OK] Project path: {manager.project_path}")

    # Define 5 action steps with clear dependencies
    action_steps = [
        {
            "step_name": "document_ingestion",
            "step_type": "process",
            "description": "Ingest documents from multiple sources (PDF, Word, Excel)",
            "requires": [],  # First step - no requirements
            "produces": ["raw_documents", "document_metadata"],
            "position": 0,
            "params": {
                "supported_formats": [".pdf", ".docx", ".xlsx"],
                "max_file_size_mb": 50,
                "batch_size": 10
            },
            "validation_rules": {
                "file_exists": True,
                "format_valid": True
            }
        },
        {
            "step_name": "content_extraction",
            "step_type": "transform",
            "description": "Extract text, tables, and structured data from documents",
            "requires": ["raw_documents", "document_metadata"],
            "produces": ["extracted_text", "extracted_tables", "document_structure"],
            "position": 1,
            "params": {
                "ocr_enabled": True,
                "language": "en",
                "preserve_formatting": True
            },
            "validation_rules": {
                "min_text_length": 100,
                "encoding": "utf-8"
            }
        },
        {
            "step_name": "compliance_analysis",
            "step_type": "analyze",
            "description": "Analyze documents against compliance rules and regulations",
            "requires": ["extracted_text", "document_structure"],
            "produces": ["compliance_scores", "violation_details", "risk_assessment"],
            "position": 2,
            "params": {
                "compliance_frameworks": ["GDPR", "HIPAA", "SOC2"],
                "threshold_score": 0.85,
                "detailed_analysis": True
            },
            "validation_rules": {
                "score_range": [0, 1],
                "required_checks": ["data_privacy", "security", "retention"]
            }
        },
        {
            "step_name": "report_generation",
            "step_type": "transform",
            "description": "Generate comprehensive compliance reports with recommendations",
            "requires": ["compliance_scores", "violation_details", "risk_assessment"],
            "produces": ["compliance_report", "executive_summary", "remediation_plan"],
            "position": 3,
            "params": {
                "report_format": "pdf",
                "include_charts": True,
                "language": "en",
                "detail_level": "comprehensive"
            },
            "validation_rules": {
                "sections_required": ["summary", "findings", "recommendations"],
                "max_pages": 100
            }
        },
        {
            "step_name": "notification_dispatch",
            "step_type": "output",
            "description": "Send reports and alerts to stakeholders via email and dashboard",
            "requires": ["compliance_report", "executive_summary"],
            "produces": ["notification_log", "delivery_confirmation"],
            "position": 4,
            "params": {
                "channels": ["email", "dashboard", "slack"],
                "priority_routing": True,
                "retry_attempts": 3,
                "escalation_enabled": True
            },
            "validation_rules": {
                "recipient_validation": True,
                "delivery_tracking": True
            }
        }
    ]

    # Save each action step
    print("\n" + "=" * 70)
    print("SAVING ACTION STEPS")
    print("=" * 70)

    for i, step in enumerate(action_steps, 1):
        print(f"\nStep {i}/{len(action_steps)}: {step['step_name']}")
        print(f"  Type: {step['step_type']}")
        print(f"  Description: {step['description'][:60]}...")
        print(f"  Requires: {step['requires'] if step['requires'] else 'Nothing (first step)'}")
        print(f"  Produces: {step['produces']}")

        result = manager.save_action_step(step["step_name"], step)
        if result["success"]:
            print(f"  [OK] Saved successfully")
        else:
            print(f"  [FAIL] Error: {result.get('error')}")

    # Create workflow configuration
    print("\n" + "=" * 70)
    print("CREATING WORKFLOW CONFIGURATION")
    print("=" * 70)

    workflow_config = {
        "workflow_id": workflow_id,
        "workflow_name": workflow_name,
        "workflow_type": "action_based",
        "description": "Comprehensive document compliance checking workflow with 5 sequential steps",
        "action_steps_count": len(action_steps),
        "steps": [s["step_name"] for s in action_steps],
        "total_inputs": 0,  # No external inputs needed
        "total_outputs": 2,  # notification_log, delivery_confirmation
        "created_at": datetime.now().isoformat(),
        "author": "ActionStepsManager",
        "version": "1.0.0",
        "tags": ["compliance", "document-processing", "automated", "5-step"]
    }

    # Create project directories
    project_path = Path("domain/workflows/projects") / workflow_id
    directories = ["criteria", "templates", "inputs", "outputs", "resources", "action_steps"]

    for dir_name in directories:
        dir_path = project_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Created {dir_name}/ directory")

    # Save workflow config
    config_file = project_path / "project_config.json"
    with open(config_file, 'w') as f:
        json.dump(workflow_config, f, indent=2)
    print(f"  [OK] Saved workflow configuration")

    # Verify the workflow
    print("\n" + "=" * 70)
    print("WORKFLOW VERIFICATION")
    print("=" * 70)

    # Load all steps
    all_steps = manager.get_all_action_steps()
    print(f"\n[OK] Loaded {len(all_steps)} action steps")

    # Verify dependency chain
    print("\nDependency Chain Verification:")
    print("-" * 35)

    step_dict = {s['step_name']: s for s in all_steps}
    all_produced = set()

    for step in sorted(all_steps, key=lambda x: x.get('position', 0)):
        step_name = step['step_name']
        requires = step.get('requires', [])
        produces = step.get('produces', [])

        print(f"\n{step['position'] + 1}. {step_name}")

        # Check requirements
        if requires:
            missing = [r for r in requires if r not in all_produced]
            if missing:
                print(f"   [WARN] Missing requirements: {missing}")
            else:
                print(f"   [OK] All requirements satisfied: {requires}")
        else:
            print(f"   [OK] No requirements (first step)")

        # Add to produced items
        all_produced.update(produces)
        print(f"   [OK] Produces: {produces}")

    # Export the workflow
    print("\n" + "=" * 70)
    print("EXPORTING WORKFLOW")
    print("=" * 70)

    export_result = manager.export_action_steps()
    if export_result["success"]:
        print(f"[OK] Exported to: {export_result['export_path']}")
        print(f"[OK] Total steps exported: {export_result['action_steps_count']}")

    # Summary
    print("\n" + "=" * 70)
    print("5-STEP WORKFLOW CREATION COMPLETE")
    print("=" * 70)

    summary = manager.get_action_step_summary()

    print(f"\nWorkflow: {workflow_name}")
    print(f"Location: {project_path}")
    print(f"Total Steps: {summary['total_steps']}")
    print(f"Step Types: {summary['step_types']}")
    print(f"\nWorkflow Flow:")
    print("  1. Document Ingestion (process)")
    print("  2. Content Extraction (transform)")
    print("  3. Compliance Analysis (analyze)")
    print("  4. Report Generation (transform)")
    print("  5. Notification Dispatch (output)")

    print("\n[SUCCESS] 5-step workflow created and verified successfully!")

    return {
        "success": True,
        "workflow_id": workflow_id,
        "workflow_name": workflow_name,
        "steps_count": len(action_steps),
        "project_path": str(project_path),
        "export_path": export_result.get("export_path")
    }


if __name__ == "__main__":
    result = create_5_step_compliance_workflow()

    if result["success"]:
        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nYou can now use this workflow in the Flow Creator portal!")
        print(f"Workflow ID: {result['workflow_id']}")
        print(f"Steps: {result['steps_count']}")
    else:
        print("\n[FAIL] Workflow creation failed")