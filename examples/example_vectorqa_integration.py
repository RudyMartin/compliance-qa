#!/usr/bin/env python3
"""
Example: VectorQA Integration
=============================
Demonstrates direct integration with TidyLLM's VectorQA capabilities
for compliance document analysis.

This example shows how compliance-qa uses TidyLLM's core business logic
while maintaining infrastructure in the qa-compliance layer.
"""

import sys
from pathlib import Path
import json

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'packages' / 'tidyllm'))

# Import from compliance-qa infrastructure
from infrastructure.environment_manager import EnvironmentManager
from infrastructure.session.session_manager import SessionManager

# Import compliance domain services
from domain.services.document_processor import DocumentProcessor

# Try to import TidyLLM's VectorQA capabilities
try:
    from services.unified_rag_manager import UnifiedRAGManager
    TIDYLLM_AVAILABLE = True
except ImportError:
    print("Warning: TidyLLM not available - using fallback processing")
    TIDYLLM_AVAILABLE = False

def demonstrate_vectorqa():
    """Demonstrate VectorQA capabilities for compliance documents."""
    print("=" * 60)
    print("VectorQA Integration Example")
    print("=" * 60)

    if not TIDYLLM_AVAILABLE:
        print("\n[ERROR] TidyLLM package not available")
        print("To enable VectorQA:")
        print("  1. Install tidyllm package: pip install ./packages/tidyllm")
        print("  2. Ensure all dependencies are installed")
        return

    # Initialize infrastructure (stays in qa-compliance)
    print("\n1. Initializing Infrastructure (qa-compliance layer):")
    print("-" * 40)

    try:
        env_manager = EnvironmentManager()
        session_manager = SessionManager()
        print("  - Environment Manager: OK")
        print("  - Session Manager: OK")
    except Exception as e:
        print(f"  - Infrastructure Error: {e}")
        print("  - Using mock infrastructure for demo")

    # Initialize VectorQA from TidyLLM (business logic)
    print("\n2. Initializing VectorQA (TidyLLM business logic):")
    print("-" * 40)

    try:
        rag_manager = UnifiedRAGManager(
            chunk_size=1000,
            chunk_overlap=200,
            embedding_model="text-embedding-ada-002"
        )
        print("  - RAG Manager initialized")
        print("  - Chunk size: 1000")
        print("  - Overlap: 200")
        print("  - Embedding model: text-embedding-ada-002")
    except Exception as e:
        print(f"  - VectorQA initialization error: {e}")
        print("  - Note: This requires AWS Bedrock credentials")
        rag_manager = None

    # Create sample compliance document
    print("\n3. Processing Sample Compliance Document:")
    print("-" * 40)

    sample_mvr = {
        "document_type": "MVR",
        "id": "MVR_2025_Q1_001",
        "model_name": "Credit Risk Model v3.2",
        "validation_sections": {
            "data_quality": {
                "status": "PASS",
                "findings": ["Minor data gaps in 2023 Q4"]
            },
            "model_performance": {
                "status": "PARTIAL",
                "findings": ["ROC-AUC degradation detected", "Recalibration recommended"]
            },
            "compliance": {
                "mvs_543": "COMPLIANT",
                "vst_section_3": "COMPLIANT",
                "sr11_7": "NEEDS_REVIEW"
            }
        }
    }

    # Save sample document
    with open("sample_mvr.json", "w") as f:
        json.dump(sample_mvr, f, indent=2)

    print("  Created sample MVR document")

    # Process with compliance-specific logic
    processor = DocumentProcessor(use_vectorqa=True)
    result = processor.process_files("sample_mvr.json")

    print(f"  Processing Status: {result.processing_status}")

    if result.compliance_metadata:
        print("\n  Compliance Analysis:")
        print(f"    - Document Type: {result.compliance_metadata.get('document_type')}")
        print(f"    - Requires MVR Check: {result.compliance_metadata.get('requires_mvr_check')}")
        print(f"    - Requires VST Check: {result.compliance_metadata.get('requires_vst_check')}")

    if result.vectorqa_chunks:
        print(f"\n  VectorQA Processing:")
        print(f"    - Chunks extracted: {result.basic_stats.get('vectorqa_chunks_total', 0)}")
        print(f"    - Preview available: Yes")

    # Demonstrate query capability (if VectorQA is available)
    if rag_manager and TIDYLLM_AVAILABLE:
        print("\n4. VectorQA Query Demonstration:")
        print("-" * 40)

        try:
            # This would normally query the vector store
            query = "What are the compliance findings?"
            print(f"  Query: '{query}'")
            print("  Response: [Would retrieve relevant chunks from vector store]")
            print("  Note: Full query requires vector store initialization")
        except Exception as e:
            print(f"  Query error: {e}")

    # Clean up
    try:
        Path("sample_mvr.json").unlink()
    except:
        pass

    print("\n" + "=" * 60)
    print("VectorQA Integration Complete!")
    print("\nKey Architecture Points:")
    print("  - Infrastructure (MLflow, DB) stays in qa-compliance")
    print("  - Business logic (VectorQA, RAG) comes from TidyLLM")
    print("  - Compliance rules remain in qa-compliance domain layer")

if __name__ == "__main__":
    demonstrate_vectorqa()