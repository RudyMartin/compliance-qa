#!/usr/bin/env python3
"""
DSPyAdvisor Speed & Performance Testing
=====================================

Test script to evaluate response times, MLflow integration, and performance characteristics.
"""

import time
import json
from datetime import datetime
from tidyllm.services.dspy_advisor import get_advisor

def time_advisor_call(question, context_data=None):
    """Time a single advisor call and return metrics."""
    start_time = time.time()

    advisor = get_advisor(model_name="claude-3-sonnet")

    config_time = time.time()

    result = advisor.get_workflow_advice(
        criteria=context_data.get('criteria', {}) if context_data else {},
        template_fields=context_data.get('template_fields', {}) if context_data else {},
        recent_activity=context_data.get('recent_activity', []) if context_data else [],
        final_results=context_data.get('final_results', {}) if context_data else {},
        user_question=question,
        use_cases=context_data.get('use_cases', ['general workflow']) if context_data else ['general workflow']
    )

    end_time = time.time()

    return {
        'question': question,
        'config_time': config_time - start_time,
        'total_time': end_time - start_time,
        'inference_time': end_time - config_time,
        'success': result.get('success', False),
        'advice_length': len(result.get('advice', '')),
        'reasoning_length': len(result.get('reasoning', '')),
        'timestamp': datetime.now().isoformat()
    }

def run_speed_tests():
    """Run comprehensive speed testing."""
    print("=== DSPyAdvisor Speed & Performance Tests ===")

    # Test questions of varying complexity
    test_questions = [
        "What is a workflow?",  # Simple
        "How can I optimize my template field validation rules?",  # Medium
        "Design a comprehensive quality assurance workflow with multiple RAG systems, complex validation criteria, and real-time monitoring for a document processing pipeline handling sensitive financial data with strict compliance requirements.",  # Complex
        "Help me troubleshoot performance issues",  # Medium
        "Best practices for RAG integration"  # Medium
    ]

    # Context data variations
    minimal_context = {
        'criteria': {},
        'template_fields': {},
        'recent_activity': [],
        'final_results': {},
        'use_cases': ['general']
    }

    rich_context = {
        'criteria': {
            'validation_rules': ['required', 'format_check', 'business_logic'],
            'quality_standards': 'ISO9001',
            'compliance_requirements': ['GDPR', 'SOX', 'PCI-DSS']
        },
        'template_fields': {
            f'field_{i}': {'type': 'text', 'required': True, 'validation': f'pattern_{i}'}
            for i in range(1, 11)  # 10 fields
        },
        'recent_activity': [
            {'execution_id': f'exec_{i}', 'status': 'success', 'duration': i*10}
            for i in range(1, 6)  # 5 executions
        ],
        'final_results': {
            'summary': 'Complex workflow execution completed',
            'metrics': {'accuracy': 0.95, 'throughput': 1000, 'error_rate': 0.05},
            'recommendations': ['optimize field validation', 'enhance error handling']
        },
        'use_cases': ['document processing', 'quality assurance', 'compliance monitoring', 'data validation']
    }

    results = []

    # Test each question with different context complexity
    for question in test_questions:
        print(f"\nTesting: '{question[:50]}...'")

        # Minimal context test
        print("  - Minimal context...")
        metrics = time_advisor_call(question, minimal_context)
        metrics['context_type'] = 'minimal'
        results.append(metrics)
        print(f"    Time: {metrics['total_time']:.2f}s | Success: {metrics['success']}")

        # Rich context test
        print("  - Rich context...")
        metrics = time_advisor_call(question, rich_context)
        metrics['context_type'] = 'rich'
        results.append(metrics)
        print(f"    Time: {metrics['total_time']:.2f}s | Success: {metrics['success']}")

        # Cool-down to avoid rate limiting
        time.sleep(1)

    # Analysis
    print(f"\n=== Performance Analysis ===")

    avg_total_time = sum(r['total_time'] for r in results) / len(results)
    avg_inference_time = sum(r['inference_time'] for r in results) / len(results)
    success_rate = sum(1 for r in results if r['success']) / len(results)

    minimal_times = [r['total_time'] for r in results if r['context_type'] == 'minimal']
    rich_times = [r['total_time'] for r in results if r['context_type'] == 'rich']

    print(f"Average total time: {avg_total_time:.2f}s")
    print(f"Average inference time: {avg_inference_time:.2f}s")
    print(f"Success rate: {success_rate:.1%}")
    print(f"Minimal context avg: {sum(minimal_times)/len(minimal_times):.2f}s")
    print(f"Rich context avg: {sum(rich_times)/len(rich_times):.2f}s")

    # Identify performance patterns
    slow_queries = [r for r in results if r['total_time'] > avg_total_time * 1.5]
    fast_queries = [r for r in results if r['total_time'] < avg_total_time * 0.7]

    if slow_queries:
        print(f"\nSlow queries ({len(slow_queries)}):")
        for query in slow_queries:
            print(f"  - {query['question'][:40]}... ({query['total_time']:.2f}s)")

    if fast_queries:
        print(f"\nFast queries ({len(fast_queries)}):")
        for query in fast_queries:
            print(f"  - {query['question'][:40]}... ({query['total_time']:.2f}s)")

    return results

if __name__ == "__main__":
    test_results = run_speed_tests()

    # Save results for analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"speed_test_results_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2)

    print(f"\nResults saved to: {filename}")