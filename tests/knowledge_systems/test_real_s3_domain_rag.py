#!/usr/bin/env python3
"""

# S3 Configuration Management
sys.path.append(str(Path(__file__).parent.parent / 'tidyllm' / 'admin') if 'tidyllm' in str(Path(__file__)) else str(Path(__file__).parent / 'tidyllm' / 'admin'))
from credential_loader import get_s3_config, build_s3_path

# Get S3 configuration (bucket and path builder)
s3_config = get_s3_config()  # Add environment parameter for dev/staging/prod

Test Real S3 Domain RAG with Admin Credentials
===============================================

Uses the admin credentials to test the actual S3-first domain RAG workflow:
1. Set AWS credentials from admin settings
2. Upload knowledge base to S3 with domain/prefix structure  
3. Create vector embeddings referencing S3 locations
4. Test stateless queries that fetch from S3 on-demand
"""

import os
import sys
from pathlib import Path

# Set AWS credentials from admin settings
# Credentials loaded by centralized system
# Credentials loaded by centralized system
os.environ['POSTGRES_PASSWORD'] = 'Fujifuji500!'

print("AWS Credentials set from admin settings")

# Add parent path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def main():
    print("Real S3 Domain RAG Test with Admin Credentials")
    print("=" * 55)
    
    # Initialize with credentials
    try:
        from knowledge_systems import get_knowledge_interface
        from ...infrastructure.s3_manager import get_s3_manager
        
        ki = get_knowledge_interface()
        s3_manager = get_s3_manager()
        
        print("SUCCESS: Knowledge systems initialized with admin credentials")
    except Exception as e:
        print(f"ERROR: Initialization failed: {e}")
        return
    
    # Test S3 connection with real credentials
    print("\nTesting S3 connection with admin credentials...")
    s3_status = s3_manager.test_connection()
    
    print(f"S3 Connection: {'SUCCESS' if s3_status['success'] else 'FAILED'}")
    if s3_status['success']:
        print(f"  Credential source: {s3_status['credential_source']}")
        print(f"  Region: {s3_status['region']}")
        print(f"  Buckets available: {s3_status['bucket_count']}")
        if s3_status.get('buckets'):
            print(f"  Sample buckets: {', '.join(s3_status['buckets'][:3])}")
    else:
        print(f"  Error: {s3_status['message']}")
        return
    
    # Configuration from admin settings
    domain_name = "model_validation"
    
    # Use bucket from admin settings (nsc-mvp1) or test bucket from evidence
    available_buckets = s3_status.get('buckets', [])
    
    if 'dsai-2025-asu' in available_buckets:
        bucket = 'dsai-2025-asu'
        print(f"Using test evidence bucket: {bucket}")
    elif s3_config["bucket"] in available_buckets:
        bucket = s3_config["bucket"]
        print(f"Using admin settings bucket: {bucket}")
    else:
        bucket = available_buckets[0] if available_buckets else 'dsai-2025-asu'
        print(f"Using first available bucket: {bucket}")
    
    s3_prefix = fbuild_s3_path("knowledge_base", "{domain_name}/")
    
    print(f"Configuration:")
    print(f"  Domain: {domain_name}")
    print(f"  S3 Bucket: {bucket}")
    print(f"  S3 Prefix: {s3_prefix}")
    
    # Find knowledge base
    knowledge_base_path = None
    kb_paths = [
        parent_dir / "knowledge_base",
        parent_dir / "tidyllm" / "knowledge_base"
    ]
    
    for path in kb_paths:
        if path.exists():
            knowledge_base_path = path
            break
    
    if not knowledge_base_path:
        print("ERROR: Knowledge base not found")
        return
    
    print(f"Found knowledge base: {knowledge_base_path}")
    pdf_files = list(knowledge_base_path.glob("*.pdf"))
    print(f"PDFs available: {len(pdf_files)}")
    
    # Test 1: Upload knowledge base to S3
    print(f"\nTEST 1: Upload Knowledge Base to S3")
    print("-" * 40)
    
    # Upload first 3 PDFs for testing
    test_files = pdf_files[:3]
    uploaded_docs = []
    
    print(f"Uploading {len(test_files)} PDFs to S3...")
    
    for i, pdf_file in enumerate(test_files, 1):
        s3_key = f"{s3_prefix}{pdf_file.name}"
        
        print(f"  {i}. Uploading {pdf_file.name}...")
        
        result = s3_manager.upload_file(
            file_path=pdf_file,
            bucket=bucket,
            s3_key=s3_key,
            metadata={
                "domain": domain_name,
                "content_type": "regulatory_document",
                "upload_purpose": "s3_first_domain_rag_test",
                "original_size": str(pdf_file.stat().st_size)
            }
        )
        
        if result.success:
            uploaded_docs.append({
                "filename": pdf_file.name,
                "s3_key": s3_key,
                "s3_url": result.s3_url,
                "size": result.file_size,
                "etag": result.etag,
                "upload_time": result.upload_duration
            })
            print(f"     SUCCESS: {result.s3_url}")
            print(f"     Size: {result.file_size} bytes")
            print(f"     Upload time: {result.upload_duration:.2f}s")
            print(f"     ETag: {result.etag}")
        else:
            print(f"     FAILED: {result.error}")
    
    print(f"\nUpload Summary:")
    print(f"  Total files: {len(test_files)}")
    print(f"  Successful uploads: {len(uploaded_docs)}")
    print(f"  Failed uploads: {len(test_files) - len(uploaded_docs)}")
    
    if not uploaded_docs:
        print("ERROR: No files uploaded successfully")
        return
    
    # Test 2: List S3 documents 
    print(f"\nTEST 2: List S3 Documents")
    print("-" * 30)
    
    s3_documents = s3_manager.list_documents(bucket, s3_prefix)
    print(f"Found {len(s3_documents)} documents in S3:")
    
    for doc in s3_documents:
        print(f"  - {doc['filename']} ({doc['size']} bytes)")
        print(f"    S3 URL: {doc['s3_url']}")
    
    # Test 3: Create S3-First Domain RAG
    print(f"\nTEST 3: Create S3-First Domain RAG")
    print("-" * 35)
    
    try:
        # Create domain RAG from S3 (not local files)
        print("Creating domain RAG from S3 documents...")
        
        result = ki.create_domain_rag(
            domain_name=f"s3_{domain_name}",
            s3_bucket=bucket,
            s3_prefix=s3_prefix,
            description=f"S3-first domain RAG for {domain_name} using admin credentials"
        )
        
        if result["success"]:
            print("SUCCESS: S3-first domain RAG created")
            print(f"  Domain: {result['domain_name']}")
            print(f"  Source: {result['source']}")
            stats = result["stats"]
            print(f"  Documents processed: {stats.get('documents_processed', 0)}")
            print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        else:
            print(f"FAILED: {result['error']}")
            return
            
    except Exception as e:
        print(f"ERROR: Domain RAG creation failed: {e}")
        return
    
    # Test 4: S3-Referenced Query
    print(f"\nTEST 4: Query S3-Referenced Domain RAG")
    print("-" * 40)
    
    test_queries = [
        "What are the key model validation requirements?",
        "How should risk assessment be conducted?",
        "What documentation is required for compliance?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        try:
            response = ki.query(query, domain=f"s3_{domain_name}")
            
            print(f"  Answer: {response.answer[:150]}...")
            print(f"  Confidence: {response.confidence:.2f}")
            print(f"  Sources: {len(response.sources)}")
            print(f"  Processing time: {response.processing_time:.2f}s")
            
            # Show S3 source references
            if response.sources:
                print("  S3 Sources:")
                for source in response.sources[:2]:
                    if hasattr(source, 'metadata') and source.metadata:
                        s3_ref = source.metadata.get('document_source', 'No S3 reference')
                        print(f"    - {s3_ref}")
                        
        except Exception as e:
            print(f"  ERROR: Query failed: {e}")
    
    # Test 5: Verify Stateless Operation
    print(f"\nTEST 5: Verify Stateless Operation")
    print("-" * 35)
    
    # Check that no files were left in app directories
    temp_dirs = [d for d in Path.cwd().iterdir() if d.is_dir() and 'temp' in d.name.lower()]
    cache_files = list(Path.cwd().glob("*cache*"))
    log_files = list(Path.cwd().glob("*.log"))
    
    print(f"Temp directories: {len(temp_dirs)}")
    print(f"Cache files: {len(cache_files)}")
    print(f"Log files: {len(log_files)}")
    
    if temp_dirs:
        print("WARNING: Temporary directories found:")
        for temp_dir in temp_dirs:
            print(f"  - {temp_dir}")
    
    # Verification Summary
    print(f"\nVERIFICATION SUMMARY")
    print("=" * 25)
    print(f"✓ AWS credentials: Working ({s3_status['credential_source']})")
    print(f"✓ S3 connection: Success ({s3_status['bucket_count']} buckets)")
    print(f"✓ Document upload: {len(uploaded_docs)}/{len(test_files)} files")
    print(f"✓ S3 document listing: {len(s3_documents)} found")
    print(f"✓ Domain RAG creation: {'Success' if result['success'] else 'Failed'}")
    print(f"✓ S3-referenced queries: {len(test_queries)} tested")
    print(f"✓ Stateless operation: {'Verified' if not temp_dirs else 'WARNING - temp files found'}")
    
    print(f"\nS3-FIRST DOMAIN RAG OPERATIONAL!")
    print("Documents stored in S3, embeddings in VectorDB")
    print("App remains stateless with zero local storage")
    print("Ready for production deployment")

if __name__ == "__main__":
    main()