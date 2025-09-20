#!/usr/bin/env python3
"""
Example: QA Control Flows
=========================
Demonstrates the QA workflow automation capabilities.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.workflows.qa_control_flows import QAControlFlowManager

def main():
    """Demonstrate QA Control Flows functionality."""
    print("=" * 60)
    print("QA Control Flows Example")
    print("=" * 60)

    # Initialize the QA flow manager
    qa_manager = QAControlFlowManager()

    # 1. Show available flows
    print("\nAvailable QA Workflows:")
    for flow in qa_manager.get_qa_flows()[:5]:
        print(f"  - {flow}")

    # 2. Process an MVR document
    print("\n" + "-" * 40)
    print("Processing MVR Document...")
    result = qa_manager.execute_qa_flow(
        "[Process MVR]",
        context={"document_id": "MVR_2025_EXAMPLE"}
    )
    if result['success']:
        mvr_result = result['result']
        print(f"  Status: {mvr_result['status']}")
        print(f"  Processing time: {mvr_result['processing_time_ms']}ms")
        print(f"  Findings: {len(mvr_result['findings'])}")
        for finding in mvr_result['findings']:
            print(f"    - [{finding['severity']}] {finding['description']}")

    # 3. Check compliance
    print("\n" + "-" * 40)
    print("Checking MVS Compliance...")
    result = qa_manager.execute_qa_flow(
        "[Check MVS Compliance]",
        context={"document_path": "example_document.pdf"}
    )
    if result['success']:
        compliance = result['result']
        print(f"  Overall status: {compliance['overall_status']}")
        print(f"  Compliant items: {compliance['compliant_count']}/{compliance['requirements_checked']}")

    # 4. Classify findings
    print("\n" + "-" * 40)
    print("Classifying Findings...")
    result = qa_manager.execute_qa_flow("[Classify Findings]")
    if result['success']:
        classification = result['result']
        print(f"  Total findings: {classification['total_findings']}")
        print(f"  By severity:")
        for level, count in classification['classification'].items():
            if count > 0:
                print(f"    - {level.capitalize()}: {count}")

    # 5. Run QA checklist
    print("\n" + "-" * 40)
    print("Running QA Checklist...")
    result = qa_manager.execute_qa_flow("[Run QA Checklist]")
    if result['success']:
        checklist = result['result']
        print(f"  Version: {checklist['checklist_version']}")
        print(f"  Results: {checklist['passed']}/{checklist['total_items']} passed")
        print(f"  Status: {checklist['overall_status']}")
        print(f"  Next action: {checklist['next_action']}")

    print("\n" + "=" * 60)
    print("Example Complete!")

if __name__ == "__main__":
    main()