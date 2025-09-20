#!/usr/bin/env python3
"""
Example: Document Processing with VectorQA Integration
=======================================================
Demonstrates compliance document processing using TidyLLM's VectorQA capabilities.

This example shows:
- Basic document processing (JSON, Excel, PDF)
- Integration with TidyLLM's VectorQA when available
- Compliance-specific metadata extraction
"""

import sys
import json
import pandas as pd
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from domain.services.document_processor import DocumentProcessor

def create_sample_files():
    """Create sample files for demonstration."""
    # Sample JSON compliance data
    compliance_data = {
        "document_id": "COMP_2025_001",
        "type": "compliance_report",
        "status": "under_review",
        "sections": {
            "executive_summary": "Quarterly compliance review",
            "findings": [
                {"id": "F001", "severity": "medium", "description": "Documentation gap"},
                {"id": "F002", "severity": "low", "description": "Minor process improvement"}
            ],
            "recommendations": ["Update procedures", "Staff training"]
        }
    }

    with open("sample_compliance.json", "w") as f:
        json.dump(compliance_data, f, indent=2)

    # Sample Excel checklist
    checklist_data = {
        "Check ID": ["CHK001", "CHK002", "CHK003", "CHK004"],
        "Description": ["Data validation", "Access controls", "Audit logging", "Backup procedures"],
        "Status": ["Pass", "Pass", "Fail", "Pass"],
        "Priority": ["High", "Critical", "Medium", "High"]
    }

    df = pd.DataFrame(checklist_data)
    df.to_excel("sample_checklist.xlsx", index=False)

    return ["sample_compliance.json", "sample_checklist.xlsx"]

def main():
    """Demonstrate document processing functionality."""
    print("=" * 60)
    print("Document Processing Example with VectorQA")
    print("=" * 60)

    # Initialize the processor with VectorQA if available
    processor = DocumentProcessor(use_vectorqa=True)
    print(f"VectorQA enabled: {processor.use_vectorqa}")

    # Create sample files
    sample_files = create_sample_files()

    try:
        # Process JSON compliance report
        print("\n1. Processing JSON Compliance Report:")
        print("-" * 40)
        result = processor.process_files("sample_compliance.json")
        print(f"  File: {result.file_name}")
        print(f"  Status: {result.processing_status}")
        print(f"  Type: {result.file_type}")

        if result.processing_status == "SUCCESS":
            stats = result.basic_stats
            print(f"  Statistics:")
            print(f"    - Top-level keys: {stats.get('top_level_keys', 0)}")
            print(f"    - Content size: {stats.get('content_size_chars', 0)} characters")
            print(f"    - Nested levels: {stats.get('nested_levels', 0)}")
            if 'sample_keys' in stats:
                print(f"    - Keys found: {', '.join(stats['sample_keys'])}")

            # Show compliance metadata
            if result.compliance_metadata:
                print(f"  Compliance Metadata:")
                for key, value in result.compliance_metadata.items():
                    print(f"    - {key}: {value}")

        # Process Excel checklist
        print("\n2. Processing Excel Checklist:")
        print("-" * 40)
        result = processor.process_files("sample_checklist.xlsx")
        print(f"  File: {result.file_name}")
        print(f"  Status: {result.processing_status}")
        print(f"  Type: {result.file_type}")

        if result.processing_status == "SUCCESS":
            stats = result.basic_stats
            print(f"  Statistics:")
            print(f"    - Sheets: {stats.get('sheet_count', 0)}")
            print(f"    - Rows: {stats.get('first_sheet_rows', 0)}")
            print(f"    - Columns: {stats.get('first_sheet_columns', 0)}")
            if 'column_names' in stats:
                print(f"    - Columns: {', '.join(stats['column_names'])}")

            # Show compliance metadata
            if result.compliance_metadata:
                print(f"  Compliance Indicators:")
                for key, value in result.compliance_metadata.items():
                    print(f"    - {key}: {value}")

        # Try processing a PDF (will show limited processing)
        print("\n3. Processing PDF Document:")
        print("-" * 40)
        result = processor.process_files("sample_document.pdf")
        print(f"  File: {result.file_name}")
        print(f"  Status: {result.processing_status}")
        print(f"  Type: {result.file_type}")
        if result.processing_status == "LIMITED":
            print(f"  Note: {result.basic_stats.get('note', 'Limited processing available')}")

        # Process unsupported file type
        print("\n4. Handling Unsupported File:")
        print("-" * 40)
        result = processor.process_files("unknown_file.xyz")
        print(f"  File: {result.file_name}")
        print(f"  Status: {result.processing_status}")
        print(f"  Type: {result.file_type}")
        if result.processing_status == "SKIPPED":
            print(f"  Reason: {result.basic_stats.get('error', 'Unsupported format')}")

    finally:
        # Clean up sample files
        for file in sample_files:
            try:
                Path(file).unlink()
            except:
                pass

    print("\n" + "=" * 60)
    print("Example Complete!")
    print("\nNote: To enable full VectorQA processing, ensure:")
    print("  1. TidyLLM package is properly installed")
    print("  2. Infrastructure services are configured")
    print("  3. AWS credentials are available for Bedrock")

if __name__ == "__main__":
    main()