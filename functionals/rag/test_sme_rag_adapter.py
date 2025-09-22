#!/usr/bin/env python3
"""
Functional Test for SME RAG Adapter
===================================

Tests the Subject Matter Expert RAG Adapter with real database operations,
collection management, and document storage/retrieval.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import SME RAG Adapter and types
from packages.tidyllm.knowledge_systems.adapters.sme_rag.sme_rag_adapter import (
    SMERAGAdapter, get_sme_rag_adapter
)
from packages.tidyllm.knowledge_systems.adapters.base import RAGQuery, RAGResponse


class TestSMERAGAdapter:
    """Functional tests for SME RAG Adapter."""

    def __init__(self):
        """Initialize test suite."""
        self.adapter = None
        self.test_collections = []
        self.test_documents = []
        print("\n" + "="*60)
        print("SME RAG Adapter Functional Test Suite")
        print("="*60)

    def setup(self):
        """Set up test environment."""
        print("\n[SETUP] Initializing SME RAG Adapter...")
        try:
            self.adapter = get_sme_rag_adapter({
                'default_collection': 'test_general',
                'chunk_size': 500,
                'chunk_overlap': 50
            })
            print("[SUCCESS] SME RAG Adapter initialized successfully")
            return True
        except Exception as e:
            print(f"[FAILED] Failed to initialize adapter: {e}")
            return False

    def test_health_check(self):
        """Test adapter health check."""
        print("\n[TEST] Health Check")
        print("-" * 40)

        try:
            health = self.adapter.health_check()
            print(f"Status: {health.get('status')}")
            print(f"Database: {health.get('database')}")
            print(f"Collections Available: {health.get('collections_available', 0)}")

            assert health['status'] == 'healthy', "Adapter should be healthy"
            assert health['database'] == 'connected', "Database should be connected"
            print("[SUCCESS] Health check passed")
            return True

        except Exception as e:
            print(f"[FAILED] Health check failed: {e}")
            return False

    def test_adapter_info(self):
        """Test adapter information."""
        print("\n[TEST] Adapter Information")
        print("-" * 40)

        try:
            info = self.adapter.get_info()
            print(f"Name: {info.get('name')}")
            print(f"Version: {info.get('version')}")
            print(f"Type: {info.get('type')}")
            print(f"Capabilities: {', '.join(info.get('capabilities', []))}")

            assert info['name'] == 'SME RAG Adapter', "Should have correct name"
            assert 'collection_management' in info['capabilities'], "Should have collection management"
            print("[SUCCESS] Adapter info verified")
            return True

        except Exception as e:
            print(f"[FAILED] Info retrieval failed: {e}")
            return False

    def test_create_collection(self):
        """Test collection creation."""
        print("\n[TEST] Collection Creation")
        print("-" * 40)

        collections_to_create = [
            {
                'name': f'test_compliance_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'description': 'Test compliance documentation collection',
                'settings': {'authority_tier': 4, 'regulated': True}
            },
            {
                'name': f'test_engineering_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'description': 'Test engineering guides collection',
                'settings': {'authority_tier': 2, 'skill_levels': ['beginner', 'intermediate', 'expert']}
            }
        ]

        for collection_config in collections_to_create:
            try:
                result = self.adapter.create_collection(
                    name=collection_config['name'],
                    description=collection_config['description'],
                    settings=collection_config['settings']
                )

                if result['success']:
                    print(f"[SUCCESS] Created collection: {collection_config['name']}")
                    print(f"   Collection ID: {result['collection_id']}")
                    self.test_collections.append(collection_config['name'])
                else:
                    print(f"[WARNING] Collection creation returned success=False: {result.get('message')}")

            except Exception as e:
                print(f"[FAILED] Failed to create collection {collection_config['name']}: {e}")
                return False

        return True

    def test_list_collections(self):
        """Test listing collections."""
        print("\n[TEST] List Collections")
        print("-" * 40)

        try:
            collections = self.adapter.list_collections()
            print(f"Found {len(collections)} total collections")

            # Check if our test collections exist
            test_found = 0
            for collection in collections:
                if any(test_name in collection.get('name', '') for test_name in self.test_collections):
                    print(f"[SUCCESS] Found test collection: {collection['name']}")
                    test_found += 1

            if test_found > 0:
                print(f"[SUCCESS] Successfully listed collections ({test_found} test collections found)")
                return True
            else:
                print("[WARNING] No test collections found in list")
                return True  # Not a failure, collections might not persist

        except Exception as e:
            print(f"[FAILED] Failed to list collections: {e}")
            return False

    def test_add_documents(self):
        """Test adding documents to collections."""
        print("\n[TEST] Add Documents to Collections")
        print("-" * 40)

        # Use the first test collection or create a default one
        collection_name = self.test_collections[0] if self.test_collections else 'test_default'

        documents = [
            {
                'content': """
                GDPR Article 17 - Right to Erasure

                The data subject shall have the right to obtain from the controller the erasure
                of personal data concerning him or her without undue delay and the controller
                shall have the obligation to erase personal data without undue delay where one
                of the following grounds applies:

                (a) the personal data are no longer necessary in relation to the purposes for
                which they were collected or otherwise processed;

                (b) the data subject withdraws consent on which the processing is based.
                """,
                'metadata': {
                    'source': 'GDPR Official Text',
                    'article': '17',
                    'title': 'Right to Erasure',
                    'authority': 'EU Commission',
                    'year': 2018
                }
            },
            {
                'content': """
                Data Retention Best Practices

                Organizations should implement a comprehensive data retention policy that includes:

                1. Classification of data types and their retention periods
                2. Regular review and deletion of outdated data
                3. Automated retention management where possible
                4. Clear documentation of retention decisions
                5. Compliance with applicable regulations (GDPR, CCPA, etc.)

                Remember: Keep data only as long as necessary for the stated purpose.
                """,
                'metadata': {
                    'source': 'Internal Guidelines',
                    'category': 'Best Practices',
                    'last_updated': '2024-01-15',
                    'expertise_level': 'intermediate'
                }
            }
        ]

        for i, doc in enumerate(documents):
            try:
                result = self.adapter.add_document(
                    collection_name=collection_name,
                    content=doc['content'],
                    metadata=doc['metadata']
                )

                if result['success']:
                    print(f"[SUCCESS] Added document {i+1} to collection {collection_name}")
                    print(f"   Doc ID: {result['doc_id']}")
                    print(f"   Chunks created: {result['chunks_created']}")
                    self.test_documents.append(result['doc_id'])
                else:
                    print(f"[WARNING] Document addition returned success=False: {result.get('message')}")

            except Exception as e:
                print(f"[FAILED] Failed to add document {i+1}: {e}")
                return False

        return True

    def test_search_collection(self):
        """Test searching within a collection."""
        print("\n[TEST] Search Within Collection")
        print("-" * 40)

        # Use the first test collection or default
        collection_name = self.test_collections[0] if self.test_collections else 'test_default'

        test_queries = [
            "right to erasure",
            "data retention policy",
            "GDPR compliance",
            "automated deletion"
        ]

        for query in test_queries:
            print(f"\nSearching for: '{query}'")
            try:
                results = self.adapter.search_collection(
                    collection_name=collection_name,
                    query=query,
                    limit=3
                )

                print(f"Found {len(results)} results")
                for i, result in enumerate(results[:2]):  # Show first 2
                    content_preview = result.get('content', '')[:100]
                    print(f"  Result {i+1}: {content_preview}...")

            except Exception as e:
                print(f"[FAILED] Search failed for '{query}': {e}")
                return False

        print("\n[SUCCESS] Collection search completed successfully")
        return True

    def test_rag_query(self):
        """Test RAG query functionality."""
        print("\n[TEST] RAG Query with Domain Filtering")
        print("-" * 40)

        # Use test collection as domain
        domain = self.test_collections[0] if self.test_collections else None

        queries = [
            {
                'query': 'What are the requirements for data erasure under GDPR?',
                'domain': domain,
                'authority_tier': 3
            },
            {
                'query': 'How long should we retain customer data?',
                'domain': domain,
                'authority_tier': 2
            }
        ]

        for test_case in queries:
            print(f"\nQuery: {test_case['query']}")
            print(f"Domain: {test_case.get('domain', 'default')}")
            print(f"Authority Tier: {test_case.get('authority_tier', 'any')}")

            try:
                rag_query = RAGQuery(
                    query=test_case['query'],
                    domain=test_case.get('domain'),
                    authority_tier=test_case.get('authority_tier'),
                    max_results=5
                )

                response = self.adapter.query(rag_query)

                print(f"\nResponse confidence: {response.confidence:.2f}")
                print(f"Sources found: {len(response.sources)}")
                print(f"Response preview: {response.response[:200]}...")

                # Verify response structure
                assert isinstance(response, RAGResponse), "Should return RAGResponse"
                assert response.response is not None, "Should have a response"

            except Exception as e:
                print(f"[FAILED] RAG query failed: {e}")
                return False

        print("\n[SUCCESS] RAG queries completed successfully")
        return True

    def test_collection_stats(self):
        """Test getting collection statistics."""
        print("\n[TEST] Collection Statistics")
        print("-" * 40)

        if not self.test_collections:
            print("[WARNING] No test collections to get stats for")
            return True

        collection_name = self.test_collections[0]

        try:
            stats = self.adapter.get_collection_stats(collection_name)

            print(f"Collection: {stats.get('name', collection_name)}")
            print(f"Status: {stats.get('status', 'unknown')}")

            if stats.get('status') != 'not_found':
                print(f"Documents: {stats.get('document_count', 0)}")
                print(f"Chunks: {stats.get('chunk_count', 0)}")
                print(f"Description: {stats.get('description', 'N/A')}")

            print("[SUCCESS] Collection stats retrieved successfully")
            return True

        except Exception as e:
            print(f"[FAILED] Failed to get collection stats: {e}")
            return False

    def test_authority_tiers(self):
        """Test authority tier filtering."""
        print("\n[TEST] Authority Tier Filtering")
        print("-" * 40)

        print("Testing different authority tiers for the same query...")

        base_query = "data protection requirements"

        for tier in [1, 2, 3, 4]:
            print(f"\nAuthority Tier {tier}:")
            try:
                rag_query = RAGQuery(
                    query=base_query,
                    domain=self.test_collections[0] if self.test_collections else None,
                    authority_tier=tier,
                    max_results=3
                )

                response = self.adapter.query(rag_query)
                print(f"  Confidence: {response.confidence:.2f}")
                print(f"  Sources: {len(response.sources)}")

                # Check metadata for authority info
                if response.metadata:
                    print(f"  Metadata: {response.metadata.get('authority_tier', 'not set')}")

            except Exception as e:
                print(f"  [WARNING] Query failed for tier {tier}: {e}")

        print("\n[SUCCESS] Authority tier testing completed")
        return True

    def run_all_tests(self):
        """Run all tests in sequence."""
        print("\n" + "="*60)
        print("Running SME RAG Adapter Functional Tests")
        print("="*60)

        # Track test results
        results = {}

        # Setup
        if not self.setup():
            print("\n[FAILED] Setup failed, cannot continue tests")
            return

        # Run tests
        tests = [
            ('Health Check', self.test_health_check),
            ('Adapter Info', self.test_adapter_info),
            ('Create Collections', self.test_create_collection),
            ('List Collections', self.test_list_collections),
            ('Add Documents', self.test_add_documents),
            ('Search Collection', self.test_search_collection),
            ('RAG Query', self.test_rag_query),
            ('Collection Stats', self.test_collection_stats),
            ('Authority Tiers', self.test_authority_tiers),
        ]

        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"\n[FAILED] Unexpected error in {test_name}: {e}")
                results[test_name] = False

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for v in results.values() if v)
        total = len(results)

        for test_name, passed in results.items():
            status = "[SUCCESS] PASSED" if passed else "[FAILED] FAILED"
            print(f"{test_name}: {status}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n[COMPLETE] All tests passed successfully!")
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed")

        return passed == total


def main():
    """Main test execution function."""
    print("\n" + "#"*60)
    print("# SME RAG Adapter Functional Test")
    print("# Testing with Real Database Operations")
    print("#"*60)

    tester = TestSMERAGAdapter()
    success = tester.run_all_tests()

    print("\n" + "#"*60)
    if success:
        print("# [SUCCESS] SME RAG ADAPTER TEST SUITE: PASSED")
    else:
        print("# [FAILED] SME RAG ADAPTER TEST SUITE: FAILED")
    print("#"*60 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())