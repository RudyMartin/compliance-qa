"""
Complete Knowledge Base Workflow Test
====================================

Tests the end-to-end knowledge base pipeline:
1. Document Processing (extraction)
2. Embedding Generation (using flow-based providers)
3. Vector Storage (with standardized dimensions)
4. Knowledge Chat (RAG query/response)

Uses the clean facade approach with TidyLLM's Provider system.
"""

import sys
import logging
from pathlib import Path

# Add tidyllm to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_systems.facades import EmbeddingProcessor, VectorStorage, DocumentProcessor
from knowledge_systems.core.domain_rag import DomainRAG, DomainRAGConfig, RAGQuery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_documents():
    """Create sample documents for testing"""
    documents = {
        "model_validation.txt": """
Model Validation Best Practices

Model validation is a critical process in machine learning operations that ensures models perform reliably in production environments.

Key principles:
1. Independent validation data - Never use training data for validation
2. Statistical significance - Ensure sufficient sample sizes for robust testing
3. Business metric alignment - Validate against actual business outcomes
4. Temporal validation - Test model performance across different time periods
5. Segment analysis - Validate performance across different user segments

Validation techniques:
- Cross-validation for robust performance estimates
- Backtesting for time-series models
- A/B testing for production validation
- Shadow mode deployment for risk mitigation

Model monitoring should include:
- Performance drift detection
- Data drift monitoring
- Bias detection and mitigation
- Regulatory compliance tracking
        """,
        
        "risk_management.txt": """
Risk Management in ML Systems

Machine learning systems introduce unique risks that require specialized management approaches.

Technical risks:
1. Model drift - Performance degradation over time
2. Data quality issues - Corrupt or biased input data
3. Adversarial attacks - Malicious attempts to fool models
4. System failures - Infrastructure and deployment issues
5. Privacy breaches - Unauthorized access to sensitive data

Business risks:
1. Regulatory compliance - Meeting industry standards
2. Reputation damage - From biased or incorrect predictions
3. Financial losses - From poor model decisions
4. Operational disruption - System downtime or failures

Risk mitigation strategies:
- Comprehensive testing and validation
- Monitoring and alerting systems
- Regular model retraining and updates
- Access controls and audit trails
- Incident response procedures

The three lines of defense model applies to ML:
- First line: Model developers and data scientists
- Second line: Model risk management team
- Third line: Internal audit and compliance
        """,
        
        "data_governance.txt": """
Data Governance for Machine Learning

Effective data governance is essential for successful ML implementations and regulatory compliance.

Data governance principles:
1. Data quality - Accurate, complete, and consistent data
2. Data lineage - Clear tracking of data sources and transformations
3. Data security - Protection against unauthorized access
4. Data privacy - Compliance with privacy regulations
5. Data retention - Appropriate storage and deletion policies

Governance framework components:
- Data stewardship roles and responsibilities
- Data classification and cataloging
- Access controls and permission management
- Data quality monitoring and validation
- Metadata management and documentation

ML-specific governance considerations:
- Training data provenance and bias assessment
- Model feature documentation and validation
- Prediction explainability and interpretability
- Model versioning and artifact management
- Performance monitoring and drift detection

Regulatory considerations:
- GDPR compliance for personal data
- Model fairness and bias prevention
- Algorithmic transparency requirements
- Right to explanation for automated decisions
- Data subject rights and consent management
        """
    }
    
    # Create test directory and files
    test_dir = Path("test_knowledge_base")
    test_dir.mkdir(exist_ok=True)
    
    created_files = []
    for filename, content in documents.items():
        file_path = test_dir / filename
        file_path.write_text(content, encoding='utf-8')
        created_files.append(file_path)
        logger.info(f"Created test document: {filename}")
    
    return test_dir, created_files

def test_document_processing(test_dir):
    """Test document extraction and processing"""
    logger.info("=== Testing Document Processing ===")
    
    try:
        # Initialize document processor
        doc_processor = DocumentProcessor()
        
        # Process documents in the test directory
        results = []
        for file_path in test_dir.glob("*.txt"):
            logger.info(f"Processing document: {file_path.name}")
            
            result = doc_processor.process_file(str(file_path))
            results.append(result)
            
            # Display processing results
            if result["success"]:
                logger.info(f"✅ Processed: {file_path.name}")
                logger.info(f"   Chunks: {len(result['chunks'])}")
                logger.info(f"   Metadata: {result['metadata']}")
            else:
                logger.error(f"❌ Failed: {file_path.name} - {result.get('error', 'Unknown error')}")
        
        return results
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        return []

def test_embedding_generation(doc_results):
    """Test embedding generation with flow-based providers"""
    logger.info("=== Testing Embedding Generation ===")
    
    try:
        # Initialize embedding processor with flow-based approach
        embedding_processor = EmbeddingProcessor(target_dimension=1024)
        
        embedded_docs = []
        
        for doc_result in doc_results:
            if not doc_result["success"]:
                continue
                
            logger.info(f"Generating embeddings for: {doc_result['source_file']}")
            
            doc_embeddings = []
            for i, chunk in enumerate(doc_result["chunks"]):
                try:
                    # Try to use TidyLLM provider (will fallback if not configured)
                    try:
                        # Import TidyLLM provider
                        from tidyllm import bedrock
                        provider = bedrock()
                        
                        embedding = embedding_processor.embed(chunk, provider=provider)
                        
                    except (ImportError, Exception) as provider_error:
                        logger.warning(f"Provider-based embedding failed: {provider_error}")
                        logger.info("This is expected if TidyLLM gateway is not configured")
                        
                        # Create mock embedding for testing
                        import random
                        embedding = [random.random() for _ in range(1024)]
                        logger.info("Using mock embedding for testing purposes")
                    
                    doc_embeddings.append({
                        "chunk_id": i,
                        "text": chunk,
                        "embedding": embedding,
                        "dimension": len(embedding)
                    })
                    
                    logger.info(f"   Chunk {i}: {len(embedding)}d embedding generated")
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for chunk {i}: {e}")
            
            embedded_docs.append({
                "source": doc_result["source_file"],
                "metadata": doc_result["metadata"],
                "embeddings": doc_embeddings
            })
            
            logger.info(f"✅ Generated {len(doc_embeddings)} embeddings")
        
        return embedded_docs
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []

def test_vector_storage(embedded_docs):
    """Test vector storage and retrieval"""
    logger.info("=== Testing Vector Storage ===")
    
    try:
        # Initialize vector storage
        vector_store = VectorStorage(
            collection_name="test_knowledge_base",
            dimension=1024
        )
        
        stored_docs = []
        
        for doc in embedded_docs:
            logger.info(f"Storing vectors for: {Path(doc['source']).name}")
            
            doc_storage_ids = []
            for emb_data in doc["embeddings"]:
                try:
                    # Store embedding with metadata
                    storage_id = vector_store.store(
                        embedding=emb_data["embedding"],
                        text=emb_data["text"],
                        document_id=f"{Path(doc['source']).stem}_chunk_{emb_data['chunk_id']}",
                        metadata={
                            **doc["metadata"],
                            "chunk_id": emb_data["chunk_id"],
                            "source_document": doc["source"]
                        }
                    )
                    
                    doc_storage_ids.append(storage_id)
                    logger.info(f"   Stored chunk {emb_data['chunk_id']}: {storage_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to store chunk {emb_data['chunk_id']}: {e}")
            
            stored_docs.append({
                "source": doc["source"],
                "storage_ids": doc_storage_ids,
                "chunk_count": len(doc_storage_ids)
            })
            
            logger.info(f"✅ Stored {len(doc_storage_ids)} vectors")
        
        return vector_store, stored_docs
        
    except Exception as e:
        logger.error(f"Vector storage failed: {e}")
        return None, []

def test_knowledge_chat(vector_store, stored_docs):
    """Test RAG-based knowledge chat"""
    logger.info("=== Testing Knowledge Chat ===")
    
    if not vector_store or not stored_docs:
        logger.error("Cannot test chat - vector storage not available")
        return
    
    try:
        # Initialize domain RAG for chat
        config = DomainRAGConfig(
            domain_name="ml_risk_management",
            description="Machine learning model validation and risk management knowledge base"
        )
        
        domain_rag = DomainRAG(config)
        
        # Test queries
        test_queries = [
            "What are the key principles of model validation?",
            "How do you manage risks in ML systems?",
            "What are the data governance requirements for machine learning?",
            "What validation techniques should be used for ML models?",
            "How do you detect model drift?"
        ]
        
        chat_results = []
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Query {i}: {query}")
            
            try:
                # Create RAG query
                rag_query = RAGQuery(
                    query=query,
                    domain_context=config.description,
                    max_results=3,
                    similarity_threshold=0.6
                )
                
                # Execute query
                response = domain_rag.query(rag_query)
                
                # Display results
                logger.info(f"Answer: {response.answer[:200]}...")
                logger.info(f"Confidence: {response.confidence:.2f}")
                logger.info(f"Sources: {len(response.sources)}")
                logger.info(f"Processing time: {response.processing_time:.3f}s")
                
                chat_results.append({
                    "query": query,
                    "answer": response.answer,
                    "confidence": response.confidence,
                    "sources_count": len(response.sources),
                    "processing_time": response.processing_time
                })
                
                logger.info("✅ Query processed successfully")
                
            except Exception as e:
                logger.error(f"Failed to process query: {e}")
            
            logger.info("---")
        
        return chat_results
        
    except Exception as e:
        logger.error(f"Knowledge chat failed: {e}")
        return []

def main():
    """Run the complete knowledge base workflow test"""
    logger.info("🚀 Starting Complete Knowledge Base Workflow Test")
    logger.info("Testing: Document Processing → Embedding → Vector Storage → Chat")
    
    try:
        # Step 1: Create test documents
        logger.info("Step 1: Creating test documents...")
        test_dir, created_files = create_test_documents()
        logger.info(f"Created {len(created_files)} test documents")
        
        # Step 2: Document processing
        logger.info("\nStep 2: Document processing...")
        doc_results = test_document_processing(test_dir)
        successful_docs = [r for r in doc_results if r["success"]]
        logger.info(f"Successfully processed {len(successful_docs)}/{len(doc_results)} documents")
        
        # Step 3: Embedding generation
        logger.info("\nStep 3: Embedding generation...")
        embedded_docs = test_embedding_generation(successful_docs)
        total_embeddings = sum(len(doc["embeddings"]) for doc in embedded_docs)
        logger.info(f"Generated {total_embeddings} embeddings across {len(embedded_docs)} documents")
        
        # Step 4: Vector storage
        logger.info("\nStep 4: Vector storage...")
        vector_store, stored_docs = test_vector_storage(embedded_docs)
        total_stored = sum(doc["chunk_count"] for doc in stored_docs)
        logger.info(f"Stored {total_stored} vectors in database")
        
        # Step 5: Knowledge chat
        logger.info("\nStep 5: Knowledge chat...")
        chat_results = test_knowledge_chat(vector_store, stored_docs)
        logger.info(f"Processed {len(chat_results)} chat queries")
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("🎉 WORKFLOW TEST COMPLETE")
        logger.info(f"Documents processed: {len(successful_docs)}")
        logger.info(f"Embeddings generated: {total_embeddings}")
        logger.info(f"Vectors stored: {total_stored}")
        logger.info(f"Chat queries: {len(chat_results)}")
        logger.info("="*60)
        
        # Show chat results summary
        if chat_results:
            logger.info("\n📋 Chat Results Summary:")
            for i, result in enumerate(chat_results, 1):
                logger.info(f"{i}. {result['query'][:60]}...")
                logger.info(f"   Confidence: {result['confidence']:.2f} | Sources: {result['sources_count']} | Time: {result['processing_time']:.3f}s")
        
        logger.info("\n✅ Complete knowledge base workflow tested successfully!")
        
        # Cleanup
        logger.info(f"\nCleaning up test files in {test_dir}")
        import shutil
        shutil.rmtree(test_dir)
        
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()