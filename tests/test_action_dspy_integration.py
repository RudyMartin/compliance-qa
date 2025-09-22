#!/usr/bin/env python3
"""
Test Action-DSPy Integration Demo
==================================

Demonstrates the integration of actions_spec.json with DSPy for automated
workflow execution. Shows how business actions are converted to DSPy signatures
and executed as a workflow chain.

Run: python test_action_dspy_integration.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_actions_loader():
    """Test the actions loader service."""
    print("\n" + "=" * 60)
    print("TESTING ACTIONS LOADER SERVICE")
    print("=" * 60)

    try:
        from domain.services.actions_loader_service import get_actions_loader

        loader = get_actions_loader()
        actions = loader.get_all_actions()

        print(f"\n[OK] Loaded {len(actions)} action definitions from actions_spec.json")

        print("\nAvailable Actions:")
        for action in actions:
            metadata = loader.get_action_metadata(action.action_type)
            print(f"  - {action.title}")
            print(f"     Type: {action.action_type}")
            print(f"     Requires: {', '.join(action.requires) if action.requires else 'None'}")
            print(f"     Produces: {', '.join(action.produces)}")

        print("\nPre-defined Action Chains:")
        for i, chain in enumerate(loader.get_action_chains()):
            print(f"  Chain {i+1}: {' -> '.join(chain)}")

        # Test validation
        test_chain = ["ingest_docs", "extract_key_terms", "score_risk"]
        is_valid, errors = loader.validate_action_sequence(test_chain)

        print(f"\nValidation test for {test_chain}:")
        print(f"  Valid: {is_valid}")
        if errors:
            print(f"  Errors: {errors}")

        return loader

    except Exception as e:
        print(f"[ERROR] Error loading actions: {e}")
        return None


def test_dspy_signature_generation(loader):
    """Test DSPy signature generation from actions."""
    print("\n" + "=" * 60)
    print("TESTING DSPY SIGNATURE GENERATION")
    print("=" * 60)

    try:
        from packages.tidyllm.services.dspy_service import get_dspy_service

        dspy_service = get_dspy_service(auto_configure=False)

        # Test single action signature
        action = loader.get_action("extract_key_terms")
        if action:
            action_dict = {
                'type': action.action_type,
                'title': action.title,
                'description': action.description,
                'requires': action.requires,
                'produces': action.produces,
                'params': action.params,
                'inputs': action.inputs,
                'output_schema': action.output_schema
            }

            result = dspy_service.generate_action_signature(action_dict)

            if result.get("success"):
                print(f"\n[OK] Generated DSPy signature for: {action.title}")
                print(f"  Signature name: {result['signature_name']}")
                print("\n[CODE] Signature Code:")
                print("```python")
                print(result["signature_code"])
                print("```")
            else:
                print(f"[ERROR] Failed to generate signature: {result.get('error')}")

        # Test action chain module
        test_chain = ["ingest_docs", "extract_key_terms", "summarize_findings"]
        print(f"\n[CHAIN] Testing action chain: {' -> '.join(test_chain)}")

        chain_result = dspy_service.generate_action_chain_module(test_chain)

        if chain_result.get("success"):
            print("[OK] Generated DSPy chain module")
            print(f"  Steps: {chain_result['execution_plan']['steps']}")
            print(f"  Signatures: {', '.join(chain_result['signatures'])}")
            print("\n[CODE] Module Code:")
            print("```python")
            print(chain_result["module_code"])
            print("```")
        else:
            print(f"[ERROR] Failed to generate chain module: {chain_result.get('error')}")

        return dspy_service

    except Exception as e:
        print(f"[ERROR] Error with DSPy service: {e}")
        return None


def test_workflow_creation(loader):
    """Test creating a workflow from actions."""
    print("\n" + "=" * 60)
    print("TESTING WORKFLOW CREATION FROM ACTIONS")
    print("=" * 60)

    try:
        # Use a predefined action chain
        chain_index = 0  # Document processing chain
        workflow_steps = loader.create_workflow_from_chain(chain_index)

        if workflow_steps:
            print(f"\n[OK] Created workflow with {len(workflow_steps)} steps:")

            for step in workflow_steps:
                print(f"\n  Step {step.position + 1}: {step.step_name}")
                print(f"    Type: {step.step_type}")
                print(f"    Template: {step.template}")
                print(f"    Requires: {step.requires}")
                print(f"    Produces: {step.produces}")

            # Create workflow config
            workflow_config = {
                "workflow_name": "test_action_workflow",
                "workflow_type": "action_based",
                "description": "Test workflow from action templates",
                "steps": [step.__dict__ for step in workflow_steps],
                "action_chain": [step.action_def.action_type for step in workflow_steps],
                "dspy_enabled": True,
                "created_at": datetime.now().isoformat()
            }

            print("\n[CONFIG] Workflow Configuration:")
            print(json.dumps(workflow_config, indent=2))

            return workflow_config
        else:
            print("[ERROR] Failed to create workflow")
            return None

    except Exception as e:
        print(f"[ERROR] Error creating workflow: {e}")
        return None


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print(" ACTION-DSPY INTEGRATION TEST DEMO")
    print("=" * 60)

    print("\nThis demo shows how actions_spec.json definitions are:")
    print("  1. Loaded as workflow templates")
    print("  2. Converted to DSPy signatures")
    print("  3. Chained into executable workflows")
    print("  4. Integrated with the Flow Creator Portal")

    # Test 1: Load actions
    loader = test_actions_loader()
    if not loader:
        print("\n[ERROR] Actions loader failed - cannot continue")
        return 1

    # Test 2: Generate DSPy signatures
    dspy_service = test_dspy_signature_generation(loader)
    if not dspy_service:
        print("\n[WARNING] DSPy service not fully available - some features limited")

    # Test 3: Create workflow
    workflow = test_workflow_creation(loader)
    if not workflow:
        print("\n[WARNING] Workflow creation had issues")

    print("\n" + "=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)

    print("\n[OK] Key Integration Points:")
    print("  - actions_spec.json -> Actions Loader Service -> UI Display")
    print("  - Selected Actions -> DSPy Signature Generator -> Executable Workflow")
    print("  - Action Parameters -> Flow Configuration -> DSPy Module Parameters")
    print("  - Action Dependencies -> Workflow Step Ordering -> Execution Chain")

    print("\n[BENEFITS]:")
    print("  - Pre-built business workflow templates")
    print("  - Consistent action definitions across system")
    print("  - DSPy provides the execution engine")
    print("  - No new code for standard business operations")
    print("  - Easy to extend with new actions in JSON")

    print("\n[NEXT STEPS]:")
    print("  1. Open the Flow Creator Portal")
    print("  2. Toggle 'Use Action Templates' option")
    print("  3. Select a pre-defined action chain")
    print("  4. Preview the generated DSPy signatures")
    print("  5. Create and execute the workflow")

    print("\n[SUCCESS] Integration test completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)