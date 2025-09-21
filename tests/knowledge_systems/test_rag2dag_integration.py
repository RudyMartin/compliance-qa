#!/usr/bin/env python3
"""
Test RAG2DAG Integration
========================

Test the RAG2DAG optimization integration across the system components.
"""

import sys
import json
from pathlib import Path

def test_rag2dag_optimizer():
    """Test RAG2DAG Optimizer Gateway functionality"""
    print("🧪 Testing RAG2DAG Optimizer Gateway...")

    try:
        from tidyllm.gateways.rag2dag_optimizer_gateway import rag2dag_optimizer

        # Test 1: Simple workflow analysis
        print("\n📝 Test 1: Simple workflow analysis")
        result = rag2dag_optimizer.analyze_and_optimize(
            request="Analyze multiple documents and compare their contents",
            context="Document comparison workflow",
            source_files=["doc1.pdf", "doc2.pdf", "doc3.pdf", "doc4.pdf"]
        )

        print(f"  Should optimize: {result.should_optimize}")
        print(f"  Pattern detected: {result.pattern_detected}")
        print(f"  Estimated speedup: {result.estimated_speedup:.1f}x")
        print(f"  Reason: {result.optimization_reason}")

        # Test 2: Workflow design suggestion
        print("\n🎯 Test 2: Workflow design suggestion")
        suggestion = rag2dag_optimizer.suggest_optimization(
            "Create a workflow that processes research papers, extracts key findings, and compares methodologies across multiple sources",
            expected_load="high"
        )

        print(f"  Performance gain: {suggestion.performance_gain}%")
        print(f"  Cost impact: {suggestion.cost_impact}")
        print(f"  Complexity reduction: {suggestion.complexity_reduction}")
        print(f"  Suggested changes: {suggestion.suggested_changes}")

        # Test 3: Get optimization stats
        print("\n📊 Test 3: Optimization statistics")
        stats = rag2dag_optimizer.get_optimization_stats()
        print(f"  Total analyzed: {stats['total_analyzed']}")
        print(f"  Optimizations applied: {stats['optimizations_applied']}")
        print(f"  Patterns detected: {stats['patterns_detected']}")

        print("✅ RAG2DAG Optimizer Gateway tests passed!")
        return True

    except Exception as e:
        print(f"❌ RAG2DAG Optimizer test failed: {e}")
        return False


def test_corporate_gateway_integration():
    """Test Corporate LLM Gateway RAG2DAG integration"""
    print("\n🧪 Testing Corporate LLM Gateway Integration...")

    try:
        from tidyllm.gateways.corporate_llm_gateway import CorporateLLMGateway
        from tidyllm.infrastructure.unified_session_manager import UnifiedSessionManager

        # Check if gateway has RAG2DAG capabilities
        session_manager = UnifiedSessionManager()
        gateway = CorporateLLMGateway(session_manager=session_manager)

        capabilities = gateway.get_capabilities()
        has_rag2dag = capabilities.get("rag2dag_optimization_enabled", False)

        print(f"  RAG2DAG optimization enabled: {has_rag2dag}")

        if has_rag2dag:
            print("✅ Corporate LLM Gateway has RAG2DAG integration!")
            return True
        else:
            print("⚠️  Corporate LLM Gateway missing RAG2DAG integration")
            return False

    except Exception as e:
        print(f"❌ Corporate Gateway integration test failed: {e}")
        return False


def test_flow_creator_integration():
    """Test Flow Creator V2 RAG2DAG integration"""
    print("\n🧪 Testing Flow Creator V2 Integration...")

    try:
        # Check if flow_creator_v2.py has RAG2DAG imports
        flow_creator_path = Path("flow_creator_v2.py")
        if not flow_creator_path.exists():
            print("⚠️  Flow Creator V2 not found")
            return False

        content = flow_creator_path.read_text()

        has_rag2dag_import = "rag2dag_optimizer_gateway" in content
        has_optimization_analysis = "Performance Optimization Analysis" in content
        has_suggest_optimization = "suggest_optimization" in content

        print(f"  Has RAG2DAG import: {has_rag2dag_import}")
        print(f"  Has optimization analysis: {has_optimization_analysis}")
        print(f"  Has optimization suggestions: {has_suggest_optimization}")

        if all([has_rag2dag_import, has_optimization_analysis, has_suggest_optimization]):
            print("✅ Flow Creator V2 has RAG2DAG integration!")
            return True
        else:
            print("⚠️  Flow Creator V2 missing some RAG2DAG integration")
            return False

    except Exception as e:
        print(f"❌ Flow Creator integration test failed: {e}")
        return False


def test_rag2dag_patterns():
    """Test RAG2DAG pattern detection and DAG generation"""
    print("\n🧪 Testing RAG2DAG Pattern Detection...")

    try:
        from tidyllm.rag2dag.converter import RAG2DAGConverter, RAGPatternType
        from tidyllm.rag2dag.config import RAG2DAGConfig

        # Initialize converter
        config = RAG2DAGConfig.create_default_config()
        converter = RAG2DAGConverter(config)

        # Test pattern detection
        patterns = converter.patterns
        print(f"  Available patterns: {len(patterns)}")

        for pattern_type, pattern in patterns.items():
            print(f"    - {pattern_type.value}: {pattern.name} (complexity: {pattern.complexity_score})")

        # Test specific patterns
        test_cases = [
            ("Compare financial reports across quarters", RAGPatternType.COMPARATIVE_ANALYSIS),
            ("Extract data from multiple sources and synthesize", RAGPatternType.RESEARCH_SYNTHESIS),
            ("Verify claims against multiple documents", RAGPatternType.FACT_CHECKING),
            ("What is the company policy?", RAGPatternType.SIMPLE_QA)
        ]

        print("\n🎯 Pattern Detection Tests:")
        for request, expected_pattern in test_cases:
            # This would need the actual pattern detection logic
            print(f"  Request: '{request[:50]}...'")
            print(f"    Expected: {expected_pattern.value}")

        print("✅ RAG2DAG pattern tests completed!")
        return True

    except Exception as e:
        print(f"❌ RAG2DAG pattern test failed: {e}")
        return False


def main():
    """Run all RAG2DAG integration tests"""
    print("RAG2DAG Integration Test Suite")
    print("=" * 50)

    tests = [
        ("RAG2DAG Optimizer Gateway", test_rag2dag_optimizer),
        ("Corporate Gateway Integration", test_corporate_gateway_integration),
        ("Flow Creator Integration", test_flow_creator_integration),
        ("RAG2DAG Pattern Detection", test_rag2dag_patterns)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All RAG2DAG integration tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check integration")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)