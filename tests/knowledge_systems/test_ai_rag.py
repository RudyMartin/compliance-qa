#!/usr/bin/env python3
"""
Test AI-Powered RAG Adapter
"""

import asyncio
import sys

# Set UTF-8 encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

async def test_ai_rag():
    print("Testing AI-Powered RAG...")

    try:
        from rag_adapters.ai_powered_rag_adapter import AIPoweredRAGAdapter, RAGQuery

        adapter = AIPoweredRAGAdapter()
        print("✅ AI-Powered RAG Adapter initialized")

        # Test with a real query about your documents
        query = RAGQuery(
            query="What are the validation requirements?",
            domain="credit_risk_test",
            authority_tier=2
        )

        print(f"🔍 Testing query: '{query.query}'")
        response = adapter.query_unified_rag(query)

        print(f"\n📋 Response:")
        print(f"Content: {response.response}")
        print(f"Confidence: {response.confidence}")
        print(f"AI Analysis: {response.ai_analysis}")
        print(f"Sources found: {len(response.sources)}")

        if response.sources:
            print(f"\n📄 First source: {response.sources[0]['filename']}")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_rag())
    print(f"\n{'🎉 Test PASSED' if success else '💥 Test FAILED'}")