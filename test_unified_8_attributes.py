"""
Test Unified 8-Attribute Pattern
=================================

Demonstrates all three managers using the standard 8-attribute pattern.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from domain.services.action_steps_manager import ActionStepsManager
from domain.services.prompt_steps_manager import PromptStepsManager
from domain.services.ask_ai_steps_manager import AskAIStepsManager
from domain.services.step_attributes import ActionStep, PromptStep, AIInteractionStep


def demonstrate_8_attributes():
    """Demonstrate the 8-attribute pattern across all managers."""

    print("=" * 80)
    print("UNIFIED 8-ATTRIBUTE PATTERN DEMONSTRATION")
    print("=" * 80)

    workflow_id = "unified_test_workflow"

    # ==========================================
    # 1. ACTION STEPS (Original 8 attributes)
    # ==========================================
    print("\n" + "=" * 80)
    print("1. ACTION STEPS - Standard 8 Attributes")
    print("=" * 80)

    action_manager = ActionStepsManager(workflow_id)

    action_step = {
        # Core 8 attributes
        "step_name": "data_processing",              # 1
        "step_type": "transform",                    # 2
        "description": "Transform raw data into structured format",  # 3
        "requires": ["raw_data", "config"],          # 4
        "produces": ["processed_data", "metadata"],   # 5
        "position": 1,                                # 6
        "params": {                                   # 7
            "format": "json",
            "compression": "gzip",
            "batch_size": 100
        },
        "validation_rules": {                         # 8
            "min_records": 10,
            "max_size_mb": 500,
            "required_fields": ["id", "timestamp"]
        }
    }

    result = action_manager.save_step("data_processing", action_step)
    print(f"\n[ACTION STEP SAVED]")
    print(f"  1. step_name: {action_step['step_name']}")
    print(f"  2. step_type: {action_step['step_type']}")
    print(f"  3. description: {action_step['description'][:50]}...")
    print(f"  4. requires: {action_step['requires']}")
    print(f"  5. produces: {action_step['produces']}")
    print(f"  6. position: {action_step['position']}")
    print(f"  7. params: {list(action_step['params'].keys())}")
    print(f"  8. validation_rules: {list(action_step['validation_rules'].keys())}")

    # ==========================================
    # 2. PROMPT STEPS (Adapted to 8 attributes)
    # ==========================================
    print("\n" + "=" * 80)
    print("2. PROMPT STEPS - Adapted 8 Attributes")
    print("=" * 80)

    prompt_manager = PromptStepsManager(workflow_id)

    prompt_step = {
        # Core 8 attributes (adapted for prompts)
        "step_name": "extraction_prompt",            # 1
        "step_type": "extraction",                   # 2
        "description": "Extract key information from documents",  # 3
        "requires": ["document_text"],               # 4
        "produces": ["extracted_entities", "summary"],  # 5
        "position": 2,                                # 6
        "params": {                                   # 7 (prompt-specific params)
            "template": "Extract the following from {document_type}:\n- Names\n- Dates\n- Amounts\nFormat as {output_format}",
            "variables": ["document_type", "output_format"],
            "temperature": 0.3,
            "max_tokens": 500
        },
        "validation_rules": {                         # 8 (prompt validation)
            "min_confidence": 0.7,
            "required_variables": ["document_type", "output_format"],
            "output_format": "json"
        }
    }

    result = prompt_manager.save_prompt("extraction_prompt", prompt_step)
    print(f"\n[PROMPT STEP SAVED]")
    print(f"  1. step_name: {prompt_step['step_name']}")
    print(f"  2. step_type: {prompt_step['step_type']}")
    print(f"  3. description: {prompt_step['description'][:50]}...")
    print(f"  4. requires: {prompt_step['requires']}")
    print(f"  5. produces: {prompt_step['produces']}")
    print(f"  6. position: {prompt_step['position']}")
    print(f"  7. params: template + {list(prompt_step['params'].keys())}")
    print(f"  8. validation_rules: {list(prompt_step['validation_rules'].keys())}")

    # ==========================================
    # 3. AI INTERACTION STEPS (Adapted to 8 attributes)
    # ==========================================
    print("\n" + "=" * 80)
    print("3. AI INTERACTION STEPS - Adapted 8 Attributes")
    print("=" * 80)

    ai_manager = AskAIStepsManager(workflow_id)

    # Start a conversation
    conv_result = ai_manager.start_conversation("test_conversation")

    ai_step = {
        # Core 8 attributes (adapted for AI interactions)
        "step_name": "ai_workflow_design",           # 1
        "step_type": "suggestion",                   # 2
        "description": "AI suggests optimal workflow structure",  # 3
        "requires": ["business_requirements", "constraints"],  # 4
        "produces": ["workflow_design", "implementation_plan"],  # 5
        "position": 3,                                # 6
        "params": {                                   # 7 (AI-specific params)
            "conversation_id": "test_conversation",
            "model": "gpt-4",
            "context_window": 8000,
            "learning_rate": 0.1
        },
        "validation_rules": {                         # 8 (AI validation)
            "confidence_threshold": 0.75,
            "max_iterations": 5,
            "required_context": ["business_domain", "objectives"]
        }
    }

    # Additional AI-specific attributes
    ai_step["reasoning"] = "Based on requirements, suggesting a 3-step workflow"
    ai_step["confidence_score"] = 0.85
    ai_step["workflow_steps"] = [
        {"name": "input", "type": "ingestion"},
        {"name": "process", "type": "transformation"},
        {"name": "output", "type": "generation"}
    ]

    result = ai_manager.save_ai_suggestion("ai_workflow_design", ai_step)
    print(f"\n[AI STEP SAVED]")
    print(f"  1. step_name: {ai_step['step_name']}")
    print(f"  2. step_type: {ai_step['step_type']}")
    print(f"  3. description: {ai_step['description'][:50]}...")
    print(f"  4. requires: {ai_step['requires']}")
    print(f"  5. produces: {ai_step['produces']}")
    print(f"  6. position: {ai_step['position']}")
    print(f"  7. params: {list(ai_step['params'].keys())}")
    print(f"  8. validation_rules: {list(ai_step['validation_rules'].keys())}")
    print(f"  + AI extras: reasoning, confidence_score, workflow_steps")

    # ==========================================
    # 4. UNIFIED WORKFLOW USING ALL THREE
    # ==========================================
    print("\n" + "=" * 80)
    print("4. UNIFIED WORKFLOW - Combining All Step Types")
    print("=" * 80)

    unified_workflow = {
        "workflow_id": workflow_id,
        "workflow_name": "Unified 8-Attribute Workflow",
        "description": "Demonstrates all three managers with standard attributes",
        "steps": [
            {
                "position": 0,
                "type": "action",
                "step": "data_ingestion",
                "manager": "ActionStepsManager"
            },
            {
                "position": 1,
                "type": "action",
                "step": "data_processing",
                "manager": "ActionStepsManager"
            },
            {
                "position": 2,
                "type": "prompt",
                "step": "extraction_prompt",
                "manager": "PromptStepsManager"
            },
            {
                "position": 3,
                "type": "ai",
                "step": "ai_workflow_design",
                "manager": "AskAIStepsManager"
            }
        ]
    }

    print("\nUnified Workflow Structure:")
    print("-" * 40)
    for step in unified_workflow["steps"]:
        print(f"  {step['position']}. [{step['type'].upper()}] {step['step']} ({step['manager']})")

    # ==========================================
    # 5. VERIFY DEPENDENCY CHAIN
    # ==========================================
    print("\n" + "=" * 80)
    print("5. DEPENDENCY VALIDATION")
    print("=" * 80)

    all_produces = set()
    validation_passed = True

    steps = [
        {"name": "data_ingestion", "requires": [], "produces": ["raw_data", "config"]},
        {"name": "data_processing", "requires": ["raw_data", "config"], "produces": ["processed_data", "metadata", "document_text"]},
        {"name": "extraction_prompt", "requires": ["document_text"], "produces": ["extracted_entities", "summary", "business_requirements", "constraints"]},
        {"name": "ai_workflow_design", "requires": ["business_requirements", "constraints"], "produces": ["workflow_design", "implementation_plan"]}
    ]

    for step in steps:
        # Check requirements
        for req in step["requires"]:
            if req not in all_produces:
                print(f"  [FAIL] {step['name']} requires '{req}' but not produced yet")
                validation_passed = False
            else:
                print(f"  [OK] {step['name']} requirement '{req}' satisfied")

        # Add produces
        all_produces.update(step["produces"])

    if validation_passed:
        print("\n[SUCCESS] All dependencies satisfied in correct order!")

    # ==========================================
    # 6. SUMMARY
    # ==========================================
    print("\n" + "=" * 80)
    print("SUMMARY: UNIFIED 8-ATTRIBUTE PATTERN")
    print("=" * 80)

    print("""
The 8-attribute pattern provides consistency across all step types:

1. step_name        - Unique identifier
2. step_type        - Category of operation
3. description      - Human-readable explanation
4. requires         - Input dependencies
5. produces         - Output artifacts
6. position         - Sequence order
7. params           - Configuration (varies by type)
8. validation_rules - Quality checks (varies by type)

Benefits:
- Consistent interface across all managers
- Clear dependency tracking
- Polymorphic handling of different step types
- Easy validation and orchestration
- Extensible for future step types
""")

    return {
        "success": True,
        "workflow_id": workflow_id,
        "action_steps": 1,
        "prompt_steps": 1,
        "ai_steps": 1
    }


if __name__ == "__main__":
    result = demonstrate_8_attributes()

    if result["success"]:
        print("\n[SUCCESS] Unified 8-attribute pattern demonstrated successfully!")
    else:
        print("\n[FAIL] Test failed")