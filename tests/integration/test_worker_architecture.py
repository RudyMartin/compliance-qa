#!/usr/bin/env python3
"""
Test Worker Architecture - Comprehensive Testing Script
=======================================================

Tests the new agent worker architecture integrated with existing TidyLLM
processing flows. Demonstrates:

1. Individual worker functionality (Extraction, Embedding, Indexing)
2. Coordinated workflow processing 
3. Gateway integration compatibility
4. MCP server worker delegation
5. Performance and scalability testing

Usage:
    python scripts/test_worker_architecture.py
"""

import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_worker_architecture")

# Add project root to path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tidyllm.infrastructure.workers import (
        ExtractionWorker,
        EmbeddingWorker, 
        IndexingWorker,
        ProcessingWorker,
        WorkerStatus,
        TaskPriority
    )
    from tidyllm.infrastructure.workers.worker_integration import (
        WorkerPool,
        WorkerPoolConfig,
        GatewayWorkerIntegration,
        MCPWorkerIntegration,
        initialize_worker_integrations
    )
    WORKERS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Worker modules not available: {e}")
    WORKERS_AVAILABLE = False


class WorkerArchitectureTestSuite:
    """Comprehensive test suite for worker architecture."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = {
            "individual_workers": {},
            "workflow_coordination": {},
            "integration_tests": {},
            "performance_tests": {},
            "errors": []
        }
        
        # Test document content
        self.sample_document = """
        TidyLLM Worker Architecture Test Document
        ========================================
        
        This is a sample document for testing the worker architecture.
        It contains multiple paragraphs to test chunking and extraction.
        
        Section 1: Introduction
        The worker architecture provides scalable agent-based processing
        for document extraction, embedding generation, and indexing operations.
        
        Section 2: Components  
        - ExtractionWorker: Handles document content extraction
        - EmbeddingWorker: Generates vector embeddings
        - IndexingWorker: Manages document indexing and search
        - ProcessingWorker: Orchestrates multi-step workflows
        
        Section 3: Integration
        Workers integrate with existing gateways and MCP server infrastructure
        to provide enhanced processing capabilities without disrupting existing APIs.
        """
        
        logger.info("Test suite initialized")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        logger.info("Starting comprehensive worker architecture tests...")
        
        if not WORKERS_AVAILABLE:
            self.test_results["errors"].append("Worker modules not available for testing")
            return self.test_results
        
        try:
            # Test individual workers
            await self._test_individual_workers()
            
            # Test workflow coordination
            await self._test_workflow_coordination()
            
            # Test integration layers
            await self._test_integration_layers()
            
            # Test performance and scalability
            await self._test_performance_scalability()
            
            logger.info("All tests completed successfully")
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.test_results["errors"].append(str(e))
        
        return self.test_results
    
    async def _test_individual_workers(self) -> None:
        """Test individual worker functionality."""
        logger.info("Testing individual worker functionality...")
        
        # Test ExtractionWorker
        await self._test_extraction_worker()
        
        # Test EmbeddingWorker
        await self._test_embedding_worker()
        
        # Test IndexingWorker
        await self._test_indexing_worker()
    
    async def _test_extraction_worker(self) -> None:
        """Test ExtractionWorker functionality."""
        logger.info("Testing ExtractionWorker...")
        
        try:
            # Initialize worker
            worker = ExtractionWorker(worker_name="test_extraction")
            await worker.initialize()
            await worker.start()
            
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(self.sample_document)
                temp_file_path = f.name
            
            try:
                # Test document extraction
                task_id = await worker.extract_document(
                    document_id="test_doc_001",
                    content_source=temp_file_path,
                    document_type="txt",
                    priority=TaskPriority.HIGH
                )
                
                # Wait for completion
                result = await self._wait_for_task_completion(worker, task_id)
                
                # Validate results
                success = (
                    result and
                    result.document_id == "test_doc_001" and
                    len(result.extracted_text) > 0 and
                    len(result.chunks) > 0
                )
                
                self.test_results["individual_workers"]["extraction"] = {
                    "success": success,
                    "extracted_text_length": len(result.extracted_text) if result else 0,
                    "chunks_created": len(result.chunks) if result else 0,
                    "processing_time": result.extraction_time if result else None,
                    "task_id": task_id
                }
                
                logger.info(f"ExtractionWorker test: {'SUCCESS' if success else 'FAILED'}")
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
                await worker.stop()
                
        except Exception as e:
            logger.error(f"ExtractionWorker test failed: {e}")
            self.test_results["individual_workers"]["extraction"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_embedding_worker(self) -> None:
        """Test EmbeddingWorker functionality."""
        logger.info("Testing EmbeddingWorker...")
        
        try:
            # Initialize worker
            worker = EmbeddingWorker(worker_name="test_embedding")
            await worker.initialize()
            await worker.start()
            
            # Test single embedding
            task_id = await worker.generate_embedding(
                text_id="test_text_001",
                text_content="This is a test text for embedding generation.",
                model_provider="default",
                target_dimension=1024,
                priority=TaskPriority.HIGH
            )
            
            # Wait for completion
            result = await self._wait_for_task_completion(worker, task_id)
            
            # Validate results
            single_success = (
                result and
                result.text_id == "test_text_001" and
                result.embedding and
                len(result.embedding) == 1024
            )
            
            # Test batch embedding
            batch_texts = [
                {"id": "batch_text_1", "content": "First test text for batch processing."},
                {"id": "batch_text_2", "content": "Second test text for batch processing."},
                {"id": "batch_text_3", "content": "Third test text for batch processing."}
            ]
            
            batch_task_id = await worker.generate_batch_embeddings(
                batch_id="test_batch_001",
                texts=batch_texts,
                model_provider="default",
                target_dimension=1024,
                priority=TaskPriority.HIGH
            )
            
            # Wait for batch completion
            batch_result = await self._wait_for_task_completion(worker, batch_task_id)
            
            batch_success = (
                batch_result and
                batch_result.batch_id == "test_batch_001" and
                batch_result.successful_embeddings == 3 and
                len(batch_result.embeddings) == 3
            )
            
            overall_success = single_success and batch_success
            
            self.test_results["individual_workers"]["embedding"] = {
                "success": overall_success,
                "single_embedding": {
                    "success": single_success,
                    "embedding_dimension": len(result.embedding) if result and result.embedding else 0,
                    "processing_time": result.processing_time if result else None
                },
                "batch_embedding": {
                    "success": batch_success,
                    "successful_embeddings": batch_result.successful_embeddings if batch_result else 0,
                    "total_processing_time": batch_result.total_processing_time if batch_result else None
                }
            }
            
            logger.info(f"EmbeddingWorker test: {'SUCCESS' if overall_success else 'FAILED'}")
            
            await worker.stop()
            
        except Exception as e:
            logger.error(f"EmbeddingWorker test failed: {e}")
            self.test_results["individual_workers"]["embedding"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_indexing_worker(self) -> None:
        """Test IndexingWorker functionality."""
        logger.info("Testing IndexingWorker...")
        
        try:
            # Initialize worker
            worker = IndexingWorker(worker_name="test_indexing")
            await worker.initialize()
            await worker.start()
            
            # Prepare test chunks with mock embeddings
            test_chunks = [
                {
                    "chunk_id": "test_doc_002_chunk_0",
                    "text": "This is the first chunk of the test document.",
                    "start_offset": 0,
                    "end_offset": 50,
                    "embedding": [0.1] * 1024,  # Mock embedding
                    "metadata": {"chunk_index": 0}
                },
                {
                    "chunk_id": "test_doc_002_chunk_1", 
                    "text": "This is the second chunk of the test document.",
                    "start_offset": 51,
                    "end_offset": 100,
                    "embedding": [0.2] * 1024,  # Mock embedding
                    "metadata": {"chunk_index": 1}
                }
            ]
            
            # Test document indexing
            task_id = await worker.index_document(
                document_id="test_doc_002",
                title="Test Document for Indexing",
                content="Complete test document content for indexing tests.",
                chunks=test_chunks,
                source="test_suite",
                doc_type="text",
                metadata={"test": True},
                priority=TaskPriority.HIGH
            )
            
            # Wait for completion
            result = await self._wait_for_task_completion(worker, task_id)
            
            # Validate indexing results
            indexing_success = (
                result and
                result.document_id == "test_doc_002" and
                result.indexed_chunks > 0 and
                result.index_status in ["success", "partial"]
            )
            
            # Test vector search (if indexing succeeded)
            search_success = False
            if indexing_success:
                try:
                    search_task_id = await worker.search_vectors(
                        query_id="test_search_001", 
                        query_embedding=[0.15] * 1024,  # Similar to indexed embeddings
                        max_results=5,
                        similarity_threshold=0.5,
                        priority=TaskPriority.HIGH
                    )
                    
                    search_result = await self._wait_for_task_completion(worker, search_task_id)
                    search_success = (
                        search_result and
                        search_result.query_id == "test_search_001" and
                        len(search_result.results) > 0
                    )
                    
                except Exception as e:
                    logger.warning(f"Vector search test failed: {e}")
            
            overall_success = indexing_success
            
            self.test_results["individual_workers"]["indexing"] = {
                "success": overall_success,
                "document_indexing": {
                    "success": indexing_success,
                    "indexed_chunks": result.indexed_chunks if result else 0,
                    "total_chunks": result.total_chunks if result else 0,
                    "index_status": result.index_status if result else "unknown",
                    "processing_time": result.index_time if result else None
                },
                "vector_search": {
                    "success": search_success,
                    "results_found": len(search_result.results) if search_success and 'search_result' in locals() else 0
                }
            }
            
            logger.info(f"IndexingWorker test: {'SUCCESS' if overall_success else 'FAILED'}")
            
            await worker.stop()
            
        except Exception as e:
            logger.error(f"IndexingWorker test failed: {e}")
            self.test_results["individual_workers"]["indexing"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_workflow_coordination(self) -> None:
        """Test ProcessingWorker workflow coordination."""
        logger.info("Testing workflow coordination with ProcessingWorker...")
        
        try:
            # Initialize processing worker
            worker = ProcessingWorker(worker_name="test_processing")
            await worker.initialize()
            await worker.start()
            
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(self.sample_document)
                temp_file_path = f.name
            
            try:
                # Test complete document processing pipeline
                task_id = await worker.process_document_pipeline(
                    pipeline_id="test_pipeline_001",
                    document_id="test_doc_003",
                    document_source=temp_file_path,
                    document_type="txt",
                    title="Test Document Pipeline",
                    source="test_suite",
                    metadata={"pipeline_test": True},
                    priority=TaskPriority.NORMAL
                )
                
                # Wait for completion (may take longer)
                result = await self._wait_for_task_completion(worker, task_id, timeout=600.0)
                
                # Validate pipeline results
                success = (
                    result and
                    result.pipeline_id == "test_pipeline_001" and
                    result.document_id == "test_doc_003" and
                    result.overall_status in ["success", "partial"] and
                    len(result.processing_stages) > 0
                )
                
                self.test_results["workflow_coordination"]["processing_pipeline"] = {
                    "success": success,
                    "pipeline_id": result.pipeline_id if result else None,
                    "overall_status": result.overall_status if result else "unknown",
                    "processing_stages": list(result.processing_stages.keys()) if result else [],
                    "extracted_text_length": result.extracted_text_length if result else 0,
                    "chunks_created": result.chunks_created if result else 0,
                    "embeddings_generated": result.embeddings_generated if result else 0,
                    "chunks_indexed": result.chunks_indexed if result else 0,
                    "total_processing_time": result.total_processing_time if result else None,
                    "warnings": len(result.warnings) if result else 0,
                    "errors": len(result.errors) if result else 0
                }
                
                logger.info(f"ProcessingWorker pipeline test: {'SUCCESS' if success else 'FAILED'}")
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
                await worker.stop()
                
        except Exception as e:
            logger.error(f"ProcessingWorker test failed: {e}")
            self.test_results["workflow_coordination"]["processing_pipeline"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_integration_layers(self) -> None:
        """Test worker integration with gateways and MCP server."""
        logger.info("Testing integration layers...")
        
        try:
            # Initialize worker integration components
            integration_components = await initialize_worker_integrations()
            worker_pool = integration_components["worker_pool"]
            gateway_integration = integration_components["gateway_integration"]
            mcp_integration = integration_components["mcp_integration"]
            
            # Test gateway integration
            await self._test_gateway_integration(gateway_integration)
            
            # Test MCP integration
            await self._test_mcp_integration(mcp_integration)
            
            # Clean up
            await worker_pool.shutdown()
            
        except Exception as e:
            logger.error(f"Integration layer tests failed: {e}")
            self.test_results["integration_tests"]["error"] = str(e)
    
    async def _test_gateway_integration(self, gateway_integration: GatewayWorkerIntegration) -> None:
        """Test gateway worker integration."""
        logger.info("Testing gateway integration...")
        
        try:
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Gateway integration test document content.")
                temp_file_path = f.name
            
            try:
                # Test gateway document extraction
                extraction_result = await gateway_integration.extract_document_content(
                    document_id="gateway_test_001",
                    content_source=temp_file_path,
                    document_type="txt"
                )
                
                extraction_success = (
                    extraction_result and
                    extraction_result["document_id"] == "gateway_test_001" and
                    len(extraction_result["extracted_text"]) > 0
                )
                
                # Test gateway embedding generation
                embedding_result = await gateway_integration.generate_embeddings(
                    text_data="Gateway integration test text for embedding.",
                    model_provider="default"
                )
                
                embedding_success = (
                    embedding_result and
                    isinstance(embedding_result, list) and
                    len(embedding_result) > 0
                )
                
                self.test_results["integration_tests"]["gateway"] = {
                    "success": extraction_success and embedding_success,
                    "extraction": {
                        "success": extraction_success,
                        "text_length": len(extraction_result["extracted_text"]) if extraction_success else 0
                    },
                    "embedding": {
                        "success": embedding_success,
                        "embedding_dimension": len(embedding_result) if embedding_success else 0
                    }
                }
                
                logger.info(f"Gateway integration test: {'SUCCESS' if extraction_success and embedding_success else 'FAILED'}")
                
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Gateway integration test failed: {e}")
            self.test_results["integration_tests"]["gateway"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_mcp_integration(self, mcp_integration: MCPWorkerIntegration) -> None:
        """Test MCP worker integration."""
        logger.info("Testing MCP integration...")
        
        try:
            # Test MCP capabilities
            capabilities = mcp_integration.get_worker_enhanced_capabilities()
            
            capabilities_success = (
                capabilities and
                "tools" in capabilities and
                len(capabilities["tools"]) > 0 and
                "worker_pool" in capabilities
            )
            
            # Test MCP worker pool status tool
            status_result = await mcp_integration.handle_worker_tool_call(
                tool_name="get_worker_pool_status",
                parameters={}
            )
            
            status_success = (
                status_result and
                status_result.get("success") and
                "pool_status" in status_result
            )
            
            self.test_results["integration_tests"]["mcp"] = {
                "success": capabilities_success and status_success,
                "capabilities": {
                    "success": capabilities_success,
                    "tool_count": len(capabilities.get("tools", [])) if capabilities_success else 0
                },
                "worker_status": {
                    "success": status_success,
                    "pool_initialized": status_result.get("pool_status", {}).get("pool_initialized", False) if status_success else False
                }
            }
            
            logger.info(f"MCP integration test: {'SUCCESS' if capabilities_success and status_success else 'FAILED'}")
            
        except Exception as e:
            logger.error(f"MCP integration test failed: {e}")
            self.test_results["integration_tests"]["mcp"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _test_performance_scalability(self) -> None:
        """Test worker performance and scalability."""
        logger.info("Testing performance and scalability...")
        
        try:
            # Initialize worker pool with multiple workers
            config = WorkerPoolConfig(
                max_extraction_workers=2,
                max_embedding_workers=2,
                max_indexing_workers=2,
                max_processing_workers=1
            )
            
            worker_pool = WorkerPool(config)
            await worker_pool.initialize()
            
            # Test concurrent processing
            start_time = time.time()
            
            # Submit multiple extraction tasks concurrently
            extraction_tasks = []
            for i in range(5):
                # Create temporary files
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(f"Performance test document {i}\n" + self.sample_document)
                    temp_file_path = f.name
                
                worker = worker_pool.get_extraction_worker()
                if worker:
                    task_id = await worker.extract_document(
                        document_id=f"perf_test_{i}",
                        content_source=temp_file_path,
                        document_type="txt",
                        priority=TaskPriority.NORMAL
                    )
                    extraction_tasks.append((worker, task_id, temp_file_path))
            
            # Wait for all tasks to complete
            successful_tasks = 0
            total_processing_time = 0
            
            for worker, task_id, temp_file_path in extraction_tasks:
                try:
                    result = await self._wait_for_task_completion(worker, task_id, timeout=120.0)
                    if result and result.extraction_time:
                        successful_tasks += 1
                        total_processing_time += result.extraction_time
                except Exception as e:
                    logger.warning(f"Performance task failed: {e}")
                finally:
                    os.unlink(temp_file_path)
            
            total_time = time.time() - start_time
            average_task_time = total_processing_time / successful_tasks if successful_tasks > 0 else 0
            
            # Get pool status
            pool_status = worker_pool.get_pool_status()
            
            self.test_results["performance_tests"] = {
                "concurrent_processing": {
                    "total_tasks": len(extraction_tasks),
                    "successful_tasks": successful_tasks,
                    "total_wall_time": total_time,
                    "average_task_time": average_task_time,
                    "throughput": successful_tasks / total_time if total_time > 0 else 0
                },
                "worker_pool_status": pool_status
            }
            
            logger.info(f"Performance test completed: {successful_tasks}/{len(extraction_tasks)} tasks in {total_time:.2f}s")
            
            await worker_pool.shutdown()
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            self.test_results["performance_tests"] = {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_task_completion(self, worker, task_id: str, timeout: float = 60.0) -> Any:
        """Wait for worker task completion."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task_status = worker.get_task_status(task_id)
            
            if task_status and task_status.get("completed_at"):
                # Find completed task
                for completed_task in worker.completed_tasks:
                    if completed_task.task_id == task_id:
                        if completed_task.error_message:
                            raise RuntimeError(f"Task failed: {completed_task.error_message}")
                        return completed_task.result
                
                raise RuntimeError("Task completed but result not found")
            
            await asyncio.sleep(0.1)
        
        raise asyncio.TimeoutError(f"Task {task_id} timed out")
    
    def print_test_summary(self) -> None:
        """Print comprehensive test results summary."""
        print("\n" + "="*70)
        print("TIDYLLM WORKER ARCHITECTURE TEST RESULTS")
        print("="*70)
        
        # Individual worker tests
        print("\n1. INDIVIDUAL WORKER TESTS:")
        for worker_type, result in self.test_results["individual_workers"].items():
            status = "PASS" if result.get("success") else "FAIL"
            print(f"   {worker_type.upper()}: {status}")
            if not result.get("success") and "error" in result:
                print(f"      Error: {result['error']}")
        
        # Workflow coordination tests
        print("\n2. WORKFLOW COORDINATION TESTS:")
        workflow_result = self.test_results["workflow_coordination"]
        if workflow_result:
            for test_name, result in workflow_result.items():
                status = "PASS" if result.get("success") else "FAIL"
                print(f"   {test_name.upper()}: {status}")
                if result.get("success") and isinstance(result, dict):
                    print(f"      Stages: {result.get('processing_stages', [])}")
                    print(f"      Processing Time: {result.get('total_processing_time', 'N/A')}s")
        
        # Integration tests
        print("\n3. INTEGRATION TESTS:")
        integration_result = self.test_results["integration_tests"]
        if integration_result:
            for integration_type, result in integration_result.items():
                if integration_type != "error":
                    status = "PASS" if result.get("success") else "FAIL"
                    print(f"   {integration_type.upper()}: {status}")
        
        # Performance tests
        print("\n4. PERFORMANCE TESTS:")
        perf_result = self.test_results["performance_tests"]
        if perf_result and "concurrent_processing" in perf_result:
            cp = perf_result["concurrent_processing"]
            print(f"   Concurrent Tasks: {cp['successful_tasks']}/{cp['total_tasks']}")
            print(f"   Total Time: {cp['total_wall_time']:.2f}s")
            print(f"   Throughput: {cp['throughput']:.2f} tasks/sec")
        
        # Errors
        if self.test_results["errors"]:
            print("\n5. ERRORS:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")
        
        print("\n" + "="*70)
        print("TESTING COMPLETE")
        print("="*70 + "\n")


async def main():
    """Main test execution function."""
    print("TidyLLM Worker Architecture Test Suite")
    print("=====================================\n")
    
    # Initialize test suite
    test_suite = WorkerArchitectureTestSuite()
    
    # Run all tests
    results = await test_suite.run_all_tests()
    
    # Print summary
    test_suite.print_test_summary()
    
    # Save detailed results
    results_file = project_root / "test_results_worker_architecture.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Detailed results saved to: {results_file}")
    
    # Return overall success status
    individual_success = all(
        result.get("success", False) 
        for result in results.get("individual_workers", {}).values()
    )
    
    workflow_success = all(
        result.get("success", False)
        for result in results.get("workflow_coordination", {}).values()
    )
    
    integration_success = all(
        result.get("success", False)
        for result in results.get("integration_tests", {}).values()
        if isinstance(result, dict)
    )
    
    overall_success = individual_success and workflow_success and integration_success
    
    print(f"Overall Test Result: {'PASS' if overall_success else 'FAIL'}")
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)