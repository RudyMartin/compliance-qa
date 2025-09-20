#!/usr/bin/env python3
"""
Test script for QA Control Flows functionality
Tests the main QA workflow automation features
"""

import sys
import os

# Add absolute path to packages
sys.path.insert(0, r'C:\Users\marti\qa-shipping\packages\tidyllm')

from flow.qa_control_flows import QAControlFlowManager

def test_qa_control_flows():
    """Test the QA Control Flow system."""
    print("=" * 60)
    print("Testing QA Control Flows & Workflow Automation")
    print("=" * 60)

    # Initialize the QA flow manager
    qa_manager = QAControlFlowManager()

    # Test 1: Get available flows
    print("\n1. Available QA FLOW Commands:")
    available_flows = qa_manager.get_qa_flows()
    for flow in available_flows[:5]:  # Show first 5
        print(f"   - {flow}")
    print(f"   ... and {len(available_flows) - 5} more")

    # Test 2: Process MVR
    print("\n2. Testing MVR Processing:")
    result = qa_manager.execute_qa_flow(
        "[Process MVR]",
        context={"document_id": "TEST_MVR_001"}
    )
    if result['success']:
        print(f"   [OK] Status: {result['result']['status']}")
        print(f"   [OK] Documents processed: {result['result']['documents_processed']}")
        print(f"   [OK] Processing time: {result['result']['processing_time_ms']}ms")
        print(f"   [OK] Findings: {len(result['result']['findings'])}")
    else:
        print(f"   [FAIL] Failed: {result.get('error')}")

    # Test 3: Check MVS Compliance
    print("\n3. Testing MVS Compliance Check:")
    result = qa_manager.execute_qa_flow(
        "[Check MVS Compliance]",
        context={"document_path": "test_document.pdf"}
    )
    if result['success']:
        print(f"   [OK] Overall status: {result['result']['overall_status']}")
        print(f"   [OK] Requirements checked: {result['result']['requirements_checked']}")
        print(f"   [OK] Compliant: {result['result']['compliant_count']}")
        print(f"   [OK] Non-compliant: {result['result']['non_compliant_count']}")
    else:
        print(f"   [FAIL] Failed: {result.get('error')}")

    # Test 4: Classify Findings
    print("\n4. Testing Finding Classification:")
    result = qa_manager.execute_qa_flow(
        "[Classify Findings]",
        context={"findings": ["Finding 1", "Finding 2"]}
    )
    if result['success']:
        print(f"   [OK] Total findings: {result['result']['total_findings']}")
        print(f"   [OK] Critical: {result['result']['classification']['critical']}")
        print(f"   [OK] High: {result['result']['classification']['high']}")
        print(f"   [OK] Medium: {result['result']['classification']['medium']}")
        print(f"   [OK] Low: {result['result']['classification']['low']}")
    else:
        print(f"   [FAIL] Failed: {result.get('error')}")

    # Test 5: Run QA Checklist
    print("\n5. Testing QA Checklist:")
    result = qa_manager.execute_qa_flow("[Run QA Checklist]")
    if result['success']:
        print(f"   [OK] Checklist version: {result['result']['checklist_version']}")
        print(f"   [OK] Total items: {result['result']['total_items']}")
        print(f"   [OK] Passed: {result['result']['passed']}")
        print(f"   [OK] Failed: {result['result']['failed']}")
        print(f"   [OK] Overall status: {result['result']['overall_status']}")
    else:
        print(f"   [FAIL] Failed: {result.get('error')}")

    print("\n" + "=" * 60)
    print("QA Control Flows Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_qa_control_flows()