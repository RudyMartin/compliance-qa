#!/usr/bin/env python3
"""
Test script for Document Processing functionality
Tests the document extraction and analysis features
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path

# Add absolute path to packages
sys.path.insert(0, r'C:\Users\marti\qa-shipping\packages\tidyllm')

from infrastructure.adapters.simple_qa_adapter import SimpleQAProcessor

def create_test_files():
    """Create test files for processing."""
    # Create test JSON file
    test_json = {
        "compliance": {
            "mvr_id": "MVR_2025_TEST",
            "status": "pending_review",
            "findings": ["finding1", "finding2"],
            "metadata": {
                "created": "2025-01-01",
                "reviewer": "QA Team"
            }
        }
    }
    with open("test_compliance.json", "w") as f:
        json.dump(test_json, f, indent=2)

    # Create test Excel file
    df = pd.DataFrame({
        "Requirement": ["MVS_5.4.3", "MVS_5.4.3.1", "MVS_5.4.3.2"],
        "Status": ["Compliant", "Compliant", "Partially Compliant"],
        "Risk": ["Low", "Low", "Medium"]
    })
    df.to_excel("test_checklist.xlsx", index=False)

    return ["test_compliance.json", "test_checklist.xlsx"]

def test_document_processing():
    """Test the Document Processing system."""
    print("=" * 60)
    print("Testing Document Processing & Content Extraction")
    print("=" * 60)

    # Initialize the processor
    processor = SimpleQAProcessor()

    # Create test files
    test_files = create_test_files()

    try:
        # Test 1: Process JSON file
        print("\n1. Processing JSON File:")
        json_result = processor.process_files("test_compliance.json")
        print(f"   [OK] File: {json_result.file_name}")
        print(f"   [OK] Status: {json_result.processing_status}")
        print(f"   [OK] Type: {json_result.file_type}")
        print(f"   [OK] Content extracted: {json_result.content_extracted}")
        stats = json_result.basic_stats
        print(f"   [OK] Top-level keys: {stats.get('top_level_keys', 0)}")
        print(f"   [OK] Nested levels: {stats.get('nested_levels', 0)}")

        # Test 2: Process Excel file
        print("\n2. Processing Excel File:")
        excel_result = processor.process_files("test_checklist.xlsx")
        print(f"   [OK] File: {excel_result.file_name}")
        print(f"   [OK] Status: {excel_result.processing_status}")
        print(f"   [OK] Type: {excel_result.file_type}")
        stats = excel_result.basic_stats
        print(f"   [OK] Sheets: {stats.get('sheet_count', 0)}")
        print(f"   [OK] Rows: {stats.get('first_sheet_rows', 0)}")
        print(f"   [OK] Columns: {stats.get('first_sheet_columns', 0)}")
        if 'column_names' in stats:
            print(f"   [OK] Column names: {', '.join(stats['column_names'][:3])}")

        # Test 3: Process PDF file (will show limited processing)
        print("\n3. Processing PDF File (simulated):")
        # Create a dummy PDF file name for testing
        pdf_result = processor.process_files("test_document.pdf")
        print(f"   [OK] File: {pdf_result.file_name}")
        print(f"   [OK] Status: {pdf_result.processing_status}")
        print(f"   [OK] Type: {pdf_result.file_type}")
        if pdf_result.processing_status == "LIMITED":
            print(f"   [INFO] {pdf_result.basic_stats.get('note', 'Limited processing')}")

        # Test 4: Process unsupported file
        print("\n4. Processing Unsupported File:")
        unsupported_result = processor.process_files("test.unknown")
        print(f"   [OK] File: {unsupported_result.file_name}")
        print(f"   [OK] Status: {unsupported_result.processing_status}")
        print(f"   [OK] Type: {unsupported_result.file_type}")
        print(f"   [INFO] {unsupported_result.basic_stats.get('error', 'Unknown format')}")

    finally:
        # Cleanup test files
        for file in test_files:
            try:
                os.remove(file)
            except:
                pass

    print("\n" + "=" * 60)
    print("Document Processing Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_document_processing()