#!/usr/bin/env python3
"""
Test script for AI-Powered A/B Testing functionality
Tests the model optimization and comparison features
Note: This is a simulation since actual AI calls require API credentials
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# PathManager import with fallback
try:
    from core.utilities.path_manager import get_path_manager
except ImportError:
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        def get_path_manager():
            class MockPathManager:
                @property
                def root_folder(self):
                    return os.getcwd()
            return MockPathManager()

# Add packages path using PathManager
path_manager = get_path_manager()
packages_path = Path(path_manager.root_folder) / "packages" / "tidyllm"
sys.path.insert(0, str(packages_path))

# Import the A/B testing module
from services.optimization.dual_ai_ab_testing import (
    DualAIABTesting,
    ABTestConfig,
    DualAIResult
)
from services.optimization.dual_ai_pipeline import (
    AIResponse,
    AIStage
)

def simulate_ab_testing():
    """Simulate A/B testing without actual AI calls."""
    print("=" * 60)
    print("Testing AI-Powered A/B Testing & Optimization")
    print("=" * 60)

    # Initialize A/B testing framework
    ab_tester = DualAIABTesting("test_project")

    # Test 1: Show available test configurations
    print("\n1. Available Test Configurations:")
    for test_id, config in ab_tester.test_configs.items():
        print(f"   Test {test_id}: {config.label}")
        print(f"      Models: {config.stage1_model} → {config.stage2_model}")
        print(f"      Focus: {config.description}")

    # Test 2: Simulate test results (without actual AI calls)
    print("\n2. Simulating A/B Test Results:")

    # Create simulated results for demonstration
    simulated_results = {
        "A": DualAIResult(
            initial_response=AIResponse(
                content="Initial analysis for speed focus test",
                confidence=0.75,
                processing_time_ms=500,
                stage=AIStage.INITIAL,
                model_used="claude-3-haiku",
                tokens_used=150,
                metadata={"test": "simulated"}
            ),
            enhanced_response=AIResponse(
                content="Enhanced analysis with improved details",
                confidence=0.85,
                processing_time_ms=800,
                stage=AIStage.ENHANCEMENT,
                model_used="claude-3-sonnet",
                tokens_used=250,
                metadata={"test": "simulated"}
            ),
            improvement_summary="Speed-focused processing with 10% confidence gain",
            total_processing_time_ms=1300,
            confidence_improvement=0.10,
            final_content="Enhanced analysis with improved details"
        ),
        "B": DualAIResult(
            initial_response=AIResponse(
                content="Initial quality-focused analysis",
                confidence=0.80,
                processing_time_ms=900,
                stage=AIStage.INITIAL,
                model_used="claude-3-sonnet",
                tokens_used=200,
                metadata={"test": "simulated"}
            ),
            enhanced_response=AIResponse(
                content="Premium enhanced analysis with comprehensive details",
                confidence=0.92,
                processing_time_ms=1200,
                stage=AIStage.ENHANCEMENT,
                model_used="claude-3-5-sonnet",
                tokens_used=350,
                metadata={"test": "simulated"}
            ),
            improvement_summary="Quality-focused processing with 12% confidence gain",
            total_processing_time_ms=2100,
            confidence_improvement=0.12,
            final_content="Premium enhanced analysis with comprehensive details"
        ),
        "C": DualAIResult(
            initial_response=AIResponse(
                content="Fast initial assessment",
                confidence=0.70,
                processing_time_ms=400,
                stage=AIStage.INITIAL,
                model_used="claude-3-haiku",
                tokens_used=120,
                metadata={"test": "simulated"}
            ),
            enhanced_response=AIResponse(
                content="Premium enhancement with superior quality",
                confidence=0.91,
                processing_time_ms=1100,
                stage=AIStage.ENHANCEMENT,
                model_used="claude-3-5-sonnet",
                tokens_used=320,
                metadata={"test": "simulated"}
            ),
            improvement_summary="Premium focus with maximum 21% confidence gain",
            total_processing_time_ms=1500,
            confidence_improvement=0.21,
            final_content="Premium enhancement with superior quality"
        )
    }

    # Display results for each test
    for test_id, result in simulated_results.items():
        config = ab_tester.test_configs[test_id]
        print(f"\n   Test {test_id} - {config.name}:")
        print(f"      Total time: {result.total_processing_time_ms}ms")
        print(f"      Confidence improvement: {result.confidence_improvement:.1%}")
        print(f"      Total tokens: {result.initial_response.tokens_used + result.enhanced_response.tokens_used}")
        print(f"      Summary: {result.improvement_summary}")

    # Test 3: Performance comparison
    print("\n3. Performance Comparison:")
    print("   " + "-" * 50)
    print("   | Test | Time (ms) | Confidence | Tokens | Efficiency |")
    print("   " + "-" * 50)

    for test_id, result in simulated_results.items():
        total_tokens = result.initial_response.tokens_used + result.enhanced_response.tokens_used
        efficiency = result.confidence_improvement / (result.total_processing_time_ms / 1000)  # confidence per second
        print(f"   |  {test_id}   | {result.total_processing_time_ms:9} | {result.confidence_improvement:10.1%} | {total_tokens:6} | {efficiency:10.2f} |")
    print("   " + "-" * 50)

    # Test 4: Identify best configurations
    print("\n4. Optimization Recommendations:")

    # Find best for different criteria
    best_speed = min(simulated_results.items(), key=lambda x: x[1].total_processing_time_ms)
    best_quality = max(simulated_results.items(), key=lambda x: x[1].confidence_improvement)
    best_efficiency = max(simulated_results.items(), key=lambda x: x[1].confidence_improvement / x[1].total_processing_time_ms)

    print(f"   [OK] Fastest: Test {best_speed[0]} ({best_speed[1].total_processing_time_ms}ms)")
    print(f"   [OK] Highest Quality: Test {best_quality[0]} ({best_quality[1].confidence_improvement:.1%} improvement)")
    print(f"   [OK] Most Efficient: Test {best_efficiency[0]} (best confidence/time ratio)")

    # Test 5: Summary report
    print("\n5. Test Summary:")
    ab_tester.results = simulated_results  # Set simulated results
    summary = ab_tester.get_test_summary()
    print(f"   [OK] Total tests: {summary['total_tests']}")
    print(f"   [OK] Project: {summary['project_name']}")
    print(f"   [OK] Tests completed: {len([t for t in summary['tests'].values()])}")

    print("\n" + "=" * 60)
    print("AI-Powered A/B Testing Test Complete!")
    print("(Note: Results are simulated for demonstration)")
    print("=" * 60)

if __name__ == "__main__":
    simulate_ab_testing()