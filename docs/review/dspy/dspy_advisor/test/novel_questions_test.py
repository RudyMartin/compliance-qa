#!/usr/bin/env python3
"""
DSPyAdvisor Novel Questions Test Suite
====================================

Testing 20 well-thought-out questions exploring new ideas and capabilities.
"""

import time
import json
from datetime import datetime
from tidyllm.services.dspy_advisor import get_advisor

def test_novel_questions():
    """Test DSPyAdvisor with 20 innovative and diverse questions."""
    print("=== DSPyAdvisor Novel Questions Test Suite ===")

    # 20 Novel Questions - categorized by innovation area
    novel_questions = [
        # 1-4: Advanced Workflow Architecture
        {
            "category": "Advanced Architecture",
            "question": "How can I design a self-healing workflow that automatically detects and recovers from data quality issues using machine learning feedback loops?",
            "innovation": "ML-driven self-repair systems"
        },
        {
            "category": "Advanced Architecture",
            "question": "What's the optimal strategy for implementing a distributed workflow that spans multiple cloud providers while maintaining data sovereignty and compliance?",
            "innovation": "Multi-cloud orchestration"
        },
        {
            "category": "Advanced Architecture",
            "question": "How do I create a workflow that dynamically adjusts its processing strategy based on real-time cost optimization and performance metrics?",
            "innovation": "Adaptive resource management"
        },
        {
            "category": "Advanced Architecture",
            "question": "Design a workflow that can seamlessly transition between batch and streaming processing modes based on data velocity and business priorities.",
            "innovation": "Hybrid processing paradigms"
        },

        # 5-8: AI/ML Integration Innovation
        {
            "category": "AI/ML Integration",
            "question": "How can I integrate multiple LLM models in a workflow where each model specializes in different aspects of document analysis with consensus-based decision making?",
            "innovation": "Multi-LLM ensemble workflows"
        },
        {
            "category": "AI/ML Integration",
            "question": "What's the best approach for creating a workflow that learns from user feedback to continuously improve its document classification accuracy?",
            "innovation": "Human-in-the-loop learning"
        },
        {
            "category": "AI/ML Integration",
            "question": "How do I build a workflow that can automatically generate new validation rules based on patterns discovered in historical data anomalies?",
            "innovation": "Automated rule discovery"
        },
        {
            "category": "AI/ML Integration",
            "question": "Design a workflow that uses reinforcement learning to optimize the sequence of processing steps for maximum efficiency.",
            "innovation": "RL-optimized workflows"
        },

        # 9-12: Security & Privacy Innovation
        {
            "category": "Security & Privacy",
            "question": "How can I implement a zero-knowledge workflow where sensitive data is processed without exposing it to intermediate processing nodes?",
            "innovation": "Zero-knowledge processing"
        },
        {
            "category": "Security & Privacy",
            "question": "What's the strategy for building a workflow that provides differential privacy guarantees while maintaining analytical utility?",
            "innovation": "Privacy-preserving analytics"
        },
        {
            "category": "Security & Privacy",
            "question": "How do I create a workflow with homomorphic encryption that allows computation on encrypted data throughout the entire pipeline?",
            "innovation": "Encrypted computation workflows"
        },
        {
            "category": "Security & Privacy",
            "question": "Design a workflow that implements continuous security posture assessment and automatically adapts its security controls based on threat intelligence.",
            "innovation": "Adaptive security workflows"
        },

        # 13-16: Real-time & Edge Computing
        {
            "category": "Real-time & Edge",
            "question": "How can I build a workflow that operates across edge devices with intermittent connectivity while ensuring eventual consistency?",
            "innovation": "Edge-cloud hybrid processing"
        },
        {
            "category": "Real-time & Edge",
            "question": "What's the optimal design for a workflow that processes IoT sensor streams in real-time while predicting and preventing equipment failures?",
            "innovation": "Predictive maintenance workflows"
        },
        {
            "category": "Real-time & Edge",
            "question": "How do I create a workflow that can operate in degraded network conditions by intelligently caching and prefetching data?",
            "innovation": "Network-resilient workflows"
        },
        {
            "category": "Real-time & Edge",
            "question": "Design a workflow that dynamically partitions itself across edge and cloud based on data locality and processing requirements.",
            "innovation": "Dynamic workflow partitioning"
        },

        # 17-20: Emerging Technologies
        {
            "category": "Emerging Technologies",
            "question": "How can I integrate quantum computing components into my workflow for specific optimization problems while maintaining classical fallbacks?",
            "innovation": "Quantum-classical hybrid workflows"
        },
        {
            "category": "Emerging Technologies",
            "question": "What's the approach for building a workflow that leverages blockchain for immutable audit trails while maintaining high throughput?",
            "innovation": "Blockchain-integrated workflows"
        },
        {
            "category": "Emerging Technologies",
            "question": "How do I create a workflow that uses digital twins to simulate and optimize process improvements before implementing them?",
            "innovation": "Digital twin optimization"
        },
        {
            "category": "Emerging Technologies",
            "question": "Design a workflow that incorporates neuromorphic computing principles for ultra-low power edge AI processing.",
            "innovation": "Neuromorphic workflow computing"
        }
    ]

    results = []
    category_performance = {}

    for i, test_case in enumerate(novel_questions, 1):
        print(f"\n[{i}/20] Testing: {test_case['category']}")
        print(f"Innovation: {test_case['innovation']}")
        print(f"Question: {test_case['question'][:80]}...")

        start_time = time.time()

        try:
            advisor = get_advisor(model_name="claude-3-sonnet")

            result = advisor.get_workflow_advice(
                criteria={
                    "innovation_level": "advanced",
                    "complexity": "high",
                    "domain": test_case['category'].lower().replace(' ', '_')
                },
                template_fields={
                    "innovation_type": test_case['innovation'],
                    "category": test_case['category'],
                    "complexity_level": "advanced"
                },
                user_question=test_case['question'],
                use_cases=["innovation", "research", "advanced_workflows", test_case['category'].lower()]
            )

            elapsed_time = time.time() - start_time

            # Analyze response quality
            advice = result.get('advice', '')
            reasoning = result.get('reasoning', '')

            quality_metrics = {
                'response_length': len(advice),
                'reasoning_length': len(reasoning),
                'mentions_innovation': test_case['innovation'].lower() in advice.lower(),
                'technical_depth': len([word for word in advice.split() if len(word) > 8]),  # Complex terms
                'actionable_items': advice.count('1.') + advice.count('2.') + advice.count('3.'),  # Numbered items
                'future_looking': any(term in advice.lower() for term in ['future', 'emerging', 'next-generation', 'evolving'])
            }

            test_result = {
                'test_id': i,
                'category': test_case['category'],
                'innovation': test_case['innovation'],
                'question': test_case['question'],
                'success': result.get('success', False),
                'response_time': elapsed_time,
                'quality_metrics': quality_metrics,
                'advice_preview': advice[:200] + "..." if len(advice) > 200 else advice,
                'timestamp': datetime.now().isoformat()
            }

            results.append(test_result)

            # Track category performance
            if test_case['category'] not in category_performance:
                category_performance[test_case['category']] = []
            category_performance[test_case['category']].append({
                'time': elapsed_time,
                'success': result.get('success', False),
                'quality': quality_metrics
            })

            # Print quick feedback
            status = "✓" if result.get('success') else "✗"
            print(f"  {status} Success: {result.get('success')} | Time: {elapsed_time:.2f}s | Length: {len(advice)} chars")

            if quality_metrics['mentions_innovation']:
                print(f"  ✓ Addressed innovation concept")

            if quality_metrics['future_looking']:
                print(f"  ✓ Future-oriented response")

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append({
                'test_id': i,
                'category': test_case['category'],
                'innovation': test_case['innovation'],
                'question': test_case['question'],
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            })

        # Brief pause between tests
        time.sleep(0.5)

    # Analysis and summary
    print(f"\n=== Novel Questions Test Analysis ===")

    successful_tests = [r for r in results if r.get('success', False)]
    success_rate = len(successful_tests) / len(results)
    avg_response_time = sum(r['response_time'] for r in results) / len(results)

    print(f"Overall success rate: {success_rate:.1%} ({len(successful_tests)}/{len(results)})")
    print(f"Average response time: {avg_response_time:.2f}s")

    # Category analysis
    print(f"\n=== Category Performance ===")
    for category, tests in category_performance.items():
        cat_success_rate = sum(1 for t in tests if t['success']) / len(tests)
        cat_avg_time = sum(t['time'] for t in tests) / len(tests)
        avg_innovation_mentions = sum(1 for t in tests if t.get('quality', {}).get('mentions_innovation', False)) / len(tests)

        print(f"{category}:")
        print(f"  Success: {cat_success_rate:.1%} | Avg Time: {cat_avg_time:.2f}s | Innovation Depth: {avg_innovation_mentions:.1%}")

    # Innovation insights
    print(f"\n=== Innovation Insights ===")
    if successful_tests:
        high_quality = [r for r in successful_tests if r.get('quality_metrics', {}).get('technical_depth', 0) > 10]
        future_focused = [r for r in successful_tests if r.get('quality_metrics', {}).get('future_looking', False)]

        print(f"High technical depth responses: {len(high_quality)}/{len(successful_tests)}")
        print(f"Future-oriented responses: {len(future_focused)}/{len(successful_tests)}")

    return results, category_performance

if __name__ == "__main__":
    print("Starting comprehensive novel questions testing...")
    test_results, category_stats = test_novel_questions()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"novel_questions_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump({
            'test_results': test_results,
            'category_performance': category_stats,
            'summary': {
                'total_tests': len(test_results),
                'successful_tests': len([r for r in test_results if r.get('success', False)]),
                'timestamp': timestamp
            }
        }, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")
    print("Novel questions testing completed!")