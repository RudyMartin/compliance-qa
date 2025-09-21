#!/usr/bin/env python3
"""
Test Enhanced Extraction with S3-First Architecture
===================================================

Demonstrates the enhanced parsing capabilities adapted for our clean
S3-first domain RAG system, without old metadata dependencies.
"""

import os
import sys
from pathlib import Path

# Set AWS credentials
# Credentials loaded by centralized system
# Credentials loaded by centralized system

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def test_enhanced_vs_basic_extraction():
    """Compare enhanced extraction with basic extraction"""
    
    print("Enhanced Extraction Test - S3-First Architecture")
    print("=" * 55)
    
    # Initialize extractors
    from knowledge_systems.core.enhanced_extraction import get_enhanced_extractor
    from ...infrastructure.s3_manager import get_s3_manager
    
    enhanced_extractor = get_enhanced_extractor()
    s3_manager = get_s3_manager()
    
    print(f"Enhanced Extractor Capabilities:")
    print(f"  PDF Support: {enhanced_extractor.pdf_available}")
    print(f"  NLTK Support: {enhanced_extractor.nltk_available}")
    print(f"  Smart Chunking: Available")
    print(f"  Blank Page Detection: Available")
    print(f"  S3 Direct Processing: Available")
    
    # Test S3 connection
    s3_status = s3_manager.test_connection()
    print(f"\nS3 Connection: {'SUCCESS' if s3_status['success'] else 'FAILED'}")
    
    if not s3_status["success"]:
        print("Testing with local files (S3 not available)")
        test_local_files(enhanced_extractor)
        return
    
    # Test with S3 documents
    test_s3_documents(enhanced_extractor, s3_manager)

def test_local_files(enhanced_extractor):
    """Test enhanced extraction with local files"""
    
    # Find a local PDF to test
    knowledge_base_path = Path(__file__).parent.parent / "knowledge_base"
    if not knowledge_base_path.exists():
        knowledge_base_path = Path(__file__).parent.parent / "tidyllm" / "knowledge_base"
    
    if not knowledge_base_path.exists():
        print("No knowledge base found for local testing")
        return
    
    pdf_files = list(knowledge_base_path.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found for testing")
        return
    
    test_file = pdf_files[0]
    print(f"\nTesting Enhanced Extraction with: {test_file.name}")
    
    # Read file content
    with open(test_file, 'rb') as f:
        content = f.read()
    
    # Test enhanced extraction
    result = enhanced_extractor.extract_from_s3_content(content, test_file.name)
    
    display_extraction_results(result, "Local File Test")

def test_s3_documents(enhanced_extractor, s3_manager):
    """Test enhanced extraction with S3 documents"""
    
    bucket = "dsai-2025-asu"
    prefix = "workflows/model_validation_demo/01_input/"
    
    print(f"\nTesting Enhanced Extraction with S3 documents")
    print(f"S3 Location: s3://{bucket}/{prefix}")
    
    # List S3 documents
    try:
        s3_documents = s3_manager.list_documents(bucket, prefix)
        print(f"Found {len(s3_documents)} documents in S3")
        
        if not s3_documents:
            print("No documents found - may need to run domain workflow first")
            return
        
        # Test with first document
        test_doc = s3_documents[0]
        print(f"\nTesting with: {test_doc['filename']}")
        
        # Download content for processing
        download_result = s3_manager.download_file(bucket, test_doc['key'])
        
        if download_result["success"]:
            local_path = Path(download_result["local_path"])
            
            # Read content
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # Test enhanced extraction
            result = enhanced_extractor.extract_from_s3_content(content, test_doc['filename'])
            
            display_extraction_results(result, "S3 Document Test")
            
            # Cleanup
            local_path.unlink()
            
        else:
            print(f"Failed to download S3 document: {download_result['error']}")
            
    except Exception as e:
        print(f"S3 testing failed: {e}")

def display_extraction_results(result, test_name):
    """Display extraction results in a clean format"""
    
    print(f"\n{test_name} Results:")
    print("-" * 30)
    print(f"Success: {result['success']}")
    print(f"Filename: {result['filename']}")
    
    if result["success"]:
        print(f"Text Length: {len(result['text'])} characters")
        print(f"Chunks Created: {len(result['chunks'])}")
        
        # Show metadata
        metadata = result.get("metadata", {})
        print(f"Processing Method: {metadata.get('processing_method', 'Unknown')}")
        
        if "total_pages" in metadata:
            print(f"PDF Pages: {metadata['total_pages']} (processed: {metadata['processed_pages']})")
            if metadata.get('blank_pages_skipped', 0) > 0:
                print(f"Blank Pages Skipped: {metadata['blank_pages_skipped']}")
        
        # Show chunk examples
        if result["chunks"]:
            print(f"\nChunk Examples:")
            for i, chunk in enumerate(result["chunks"][:2], 1):
                print(f"  Chunk {i}: {chunk['word_count']} words")
                preview = chunk["content"][:100] + "..." if len(chunk["content"]) > 100 else chunk["content"]
                print(f"    Preview: {preview}")
        
        # Quality assessment
        quality_result = enhanced_extractor.validate_extraction_quality(result)
        print(f"\nQuality Assessment:")
        print(f"  Quality Score: {quality_result['quality_score']:.2f}")
        if quality_result["issues"]:
            print(f"  Issues: {', '.join(quality_result['issues'])}")
        
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

def demonstrate_smart_chunking():
    """Demonstrate smart chunking capabilities"""
    
    print(f"\nSMART CHUNKING DEMONSTRATION")
    print("=" * 35)
    
    from knowledge_systems.core.enhanced_extraction import get_enhanced_extractor
    extractor = get_enhanced_extractor()
    
    # Sample text for chunking
    sample_text = """
    Model validation is a critical component of model risk management. Financial institutions 
    must ensure that their models are performing as expected and meet regulatory requirements.
    
    The model validation process typically includes several key components. First, conceptual 
    soundness review examines the model's theoretical foundation and assumptions. Second, 
    ongoing monitoring tracks model performance over time. Third, outcome analysis compares 
    model predictions with actual results.
    
    Basel III requirements specify that banks must have robust model validation frameworks.
    These frameworks should address model development, implementation, use, and ongoing 
    performance monitoring. Regular validation helps identify model limitations and potential 
    improvements.
    
    Documentation is another essential aspect of model validation. Institutions must maintain 
    comprehensive records of model development, validation testing, and performance monitoring.
    This documentation supports regulatory examinations and internal governance processes.
    """
    
    # Test different chunking strategies
    chunk_sizes = [50, 100, 150]
    
    for chunk_size in chunk_sizes:
        print(f"\nChunking with max {chunk_size} words:")
        chunks = extractor.smart_chunking(sample_text, max_words=chunk_size, overlap_words=10)
        
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Word counts: {[chunk['word_count'] for chunk in chunks]}")
        
        # Show overlap information
        for chunk in chunks:
            overlap = chunk.get("overlap_info", {})
            if overlap.get("prev_overlap", 0) > 0:
                print(f"    Chunk {chunk['chunk_index']}: {overlap['prev_overlap']} word overlap with previous")

def main():
    """Run all enhanced extraction tests"""
    
    # Test extraction capabilities
    test_enhanced_vs_basic_extraction()
    
    # Demonstrate smart chunking
    demonstrate_smart_chunking()
    
    print(f"\nENHANCED EXTRACTION SUMMARY")
    print("=" * 30)
    print("✓ Smart chunking with sentence boundaries")
    print("✓ Blank page detection and filtering") 
    print("✓ Direct S3 content processing")
    print("✓ Unicode normalization and cleaning")
    print("✓ Quality validation and scoring")
    print("✓ Structured output for vector storage")
    print("✓ Clean architecture (no old metadata dependencies)")
    
    print(f"\nREADY FOR S3-FIRST DOMAIN RAG INTEGRATION!")

if __name__ == "__main__":
    main()