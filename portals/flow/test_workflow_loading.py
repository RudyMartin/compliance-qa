#!/usr/bin/env python3
"""Test the workflow loading from the portal directory."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Import the WorkflowRegistry class
from flow_creator_v3 import WorkflowRegistry

# Create registry and test
print("Creating WorkflowRegistry...")
registry = WorkflowRegistry()

print(f"\nWorkflows found: {len(registry.workflows)}")

for workflow_id, workflow_data in registry.workflows.items():
    print(f"\n{workflow_id}:")
    print(f"  - Name: {workflow_data.get('workflow_name', 'N/A')}")
    print(f"  - Type: {workflow_data.get('workflow_type', 'N/A')}")
    print(f"  - Has Flow Definition: {workflow_data.get('has_flow_definition', False)}")