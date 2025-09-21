#!/usr/bin/env python3
"""
DSPyAdvisor Robustness & Stress Testing
======================================

Testing edge cases, error handling, and system resilience.
"""

import time
import json
from datetime import datetime
from tidyllm.services.dspy_advisor import get_advisor

def test_robustness():
    """Test DSPyAdvisor robustness with challenging inputs."""
    print("=== DSPyAdvisor Robustness & Stress Tests ===")

    # Edge case test scenarios
    edge_cases = [
        # Input Variations
        {
            "name": "Empty Question",
            "question": "",
            "expected": "Should handle gracefully"
        },
        {
            "name": "Single Character",
            "question": "?",
            "expected": "Minimal input handling"
        },
        {
            "name": "Extremely Long Question",
            "question": "How can I " + "optimize workflow performance " * 100 + "?",
            "expected": "Long input processing"
        },
        {
            "name": "Special Characters",
            "question": "How to handle workflows with ñáéíóú, 中文, العربية, and 🚀📊💡 symbols?",
            "expected": "Unicode handling"
        },
        {
            "name": "Code Injection Attempt",
            "question": "'; DROP TABLE workflows; SELECT * FROM sensitive_data; --",
            "expected": "Security resilience"
        },

        # Context Edge Cases
        {
            "name": "Massive Context Data",
            "question": "Optimize this workflow",
            "criteria": {f"rule_{i}": f"validation_{i}" for i in range(1000)},  # Large dict
            "expected": "Large context handling"
        },
        {
            "name": "Malformed JSON Context",
            "question": "Help with workflow design",
            "criteria": "not_a_dict",
            "expected": "Type error handling"
        },
        {
            "name": "Circular References",
            "question": "Design workflow",
            "setup": "circular_ref",
            "expected": "Circular reference handling"
        },

        # Domain-Specific Stress Tests
        {
            "name": "Highly Technical Jargon",
            "question": "Implement Byzantine fault-tolerant consensus with PBFT algorithms in a sharded blockchain-based workflow orchestration system using zero-knowledge proofs for privacy-preserving computation.",
            "expected": "Technical complexity handling"
        },
        {
            "name": "Contradictory Requirements",
            "question": "Design a workflow that is both completely stateless and maintains full historical state, processes data instantly while ensuring careful validation, and is both highly secure and completely open.",
            "expected": "Contradiction resolution"
        },

        # Language and Format Tests
        {
            "name": "Multiple Languages Mixed",
            "question": "¿Cómo puedo optimize my workflow for 最大 performance und minimale latency?",
            "expected": "Multilingual handling"
        },
        {
            "name": "Markdown Injection",
            "question": "# Header\n## Subheader\n```python\nmalicious_code()\n```\n**Bold** and *italic* text.",
            "expected": "Markdown safety"
        },

        # Performance Stress
        {
            "name": "Rapid Fire Requests",
            "question": "Quick workflow advice",
            "rapid_fire": 5,  # 5 rapid requests
            "expected": "Rate limiting handling"
        },

        # Philosophical/Abstract Questions
        {
            "name": "Abstract Philosophy",
            "question": "What is the essence of a perfect workflow in the context of universal entropy and the meaning of existence?",
            "expected": "Abstract concept handling"
        },

        # Nonsensical Input
        {
            "name": "Gibberish Input",
            "question": "Flibberty jabberwocky xyzqua workflow optimization banana telephone purple elephant?",
            "expected": "Nonsense handling"
        }
    ]

    results = []

    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n[{i}/{len(edge_cases)}] Testing: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")

        try:
            start_time = time.time()

            # Handle special test setups
            if test_case.get('setup') == 'circular_ref':
                # Create circular reference in criteria
                criteria = {'parent': {}}
                criteria['parent']['child'] = criteria  # Circular reference
            else:
                criteria = test_case.get('criteria', {})

            # Handle rapid fire tests
            if test_case.get('rapid_fire'):
                print(f"  Executing {test_case['rapid_fire']} rapid requests...")
                rapid_results = []
                for j in range(test_case['rapid_fire']):
                    rapid_start = time.time()
                    advisor = get_advisor()
                    result = advisor.get_workflow_advice(
                        criteria=criteria,
                        user_question=f"{test_case['question']} (request {j+1})",
                        use_cases=['stress_test']
                    )
                    rapid_time = time.time() - rapid_start
                    rapid_results.append({
                        'request_id': j+1,
                        'time': rapid_time,
                        'success': result.get('success', False)
                    })

                total_time = time.time() - start_time
                test_result = {
                    'test_name': test_case['name'],
                    'test_type': 'rapid_fire',
                    'rapid_results': rapid_results,
                    'total_time': total_time,
                    'avg_time_per_request': total_time / test_case['rapid_fire'],
                    'all_successful': all(r['success'] for r in rapid_results)
                }

            else:
                # Regular single request test
                advisor = get_advisor()
                result = advisor.get_workflow_advice(
                    criteria=criteria,
                    template_fields=test_case.get('template_fields', {}),
                    user_question=test_case['question'],
                    use_cases=['robustness_test']
                )

                elapsed_time = time.time() - start_time

                # Analyze response characteristics
                advice = result.get('advice', '')
                error_msg = result.get('error', '')

                test_result = {
                    'test_name': test_case['name'],
                    'test_type': 'single_request',
                    'question': test_case['question'],
                    'success': result.get('success', False),
                    'response_time': elapsed_time,
                    'advice_length': len(advice),
                    'has_error': bool(error_msg),
                    'error_message': error_msg,
                    'fallback_used': result.get('fallback', False),
                    'graceful_degradation': bool(advice) or bool(error_msg),  # Did it respond somehow?
                    'expected_behavior': test_case['expected']
                }

            results.append(test_result)

            # Quick status feedback
            if test_result.get('all_successful') is not None:
                status = "✓" if test_result['all_successful'] else "✗"
                print(f"  {status} Rapid fire: {test_result['all_successful']} | Avg time: {test_result['avg_time_per_request']:.2f}s")
            else:
                status = "✓" if test_result['success'] else "✗"
                graceful = "✓" if test_result['graceful_degradation'] else "✗"
                print(f"  {status} Success: {test_result['success']} | {graceful} Graceful: {test_result['graceful_degradation']}")
                print(f"  Time: {test_result['response_time']:.2f}s | Response length: {test_result['advice_length']}")

        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"  ✗ EXCEPTION: {e}")
            results.append({
                'test_name': test_case['name'],
                'test_type': 'exception',
                'question': test_case['question'],
                'success': False,
                'exception': str(e),
                'response_time': elapsed_time,
                'expected_behavior': test_case['expected']
            })

        # Brief pause between tests
        time.sleep(0.3)

    # Analysis
    print(f"\n=== Robustness Test Analysis ===")

    total_tests = len(results)
    successful_tests = len([r for r in results if r.get('success', False)])
    graceful_failures = len([r for r in results if not r.get('success', False) and r.get('graceful_degradation', False)])
    hard_failures = len([r for r in results if r.get('test_type') == 'exception'])

    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests} ({successful_tests/total_tests:.1%})")
    print(f"Graceful failures: {graceful_failures} ({graceful_failures/total_tests:.1%})")
    print(f"Hard failures: {hard_failures} ({hard_failures/total_tests:.1%})")

    # Robustness score
    robustness_score = (successful_tests + graceful_failures) / total_tests
    print(f"Robustness score: {robustness_score:.2f} (successful + graceful failures)")

    # Identify concerning patterns
    print(f"\n=== Issue Analysis ===")

    long_response_tests = [r for r in results if r.get('response_time', 0) > 10]
    if long_response_tests:
        print(f"Slow responses (>10s): {len(long_response_tests)}")
        for test in long_response_tests:
            print(f"  - {test['test_name']}: {test['response_time']:.1f}s")

    exception_tests = [r for r in results if r.get('test_type') == 'exception']
    if exception_tests:
        print(f"Exceptions thrown: {len(exception_tests)}")
        for test in exception_tests:
            print(f"  - {test['test_name']}: {test['exception']}")

    # Security concerns
    security_tests = [r for r in results if 'injection' in r['test_name'].lower() or 'security' in r.get('expected_behavior', '').lower()]
    if security_tests:
        print(f"Security-related tests: {len(security_tests)}")
        for test in security_tests:
            secure = test.get('success', False) and not any(dangerous in test.get('advice', '').lower()
                                                          for dangerous in ['drop table', 'delete', 'script'])
            status = "✓ SECURE" if secure else "⚠ REVIEW"
            print(f"  - {test['test_name']}: {status}")

    return results

if __name__ == "__main__":
    print("Starting robustness and stress testing...")
    test_results = test_robustness()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"robustness_test_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump({
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'successful_tests': len([r for r in test_results if r.get('success', False)]),
                'robustness_score': (len([r for r in test_results if r.get('success', False)]) +
                                   len([r for r in test_results if not r.get('success', False) and r.get('graceful_degradation', False)])) / len(test_results),
                'timestamp': timestamp
            }
        }, f, indent=2)

    print(f"\nRobustness test results saved to: {results_file}")
    print("Robustness testing completed!")