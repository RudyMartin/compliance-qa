#!/usr/bin/env python3
"""
Run Fast Chat Tests
Purpose: Execute key tests quickly with timeouts and retries
Status: READY TO RUN
"""

import os
import sys
import importlib.util
import json
import time
from datetime import datetime

# Fast test configuration
MAX_RETRIES = 3
TEST_TIMEOUT = 30  # 30 seconds per test
FAST_TESTS = [
    'test_01_consistency.py',
    'test_02_response_times.py',
    'test_04_audit_trails.py',
    'test_05_token_usage.py',
    'test_10_rag_investigation.py'
]

def run_fast_tests():
    """Run selected tests quickly with timeouts"""
    print("=== TidyLLM Fast Chat Tests ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Timeout: {TEST_TIMEOUT}s per test, {MAX_RETRIES} retries")
    print()

    # Get test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Find available fast tests
    available_tests = [f for f in FAST_TESTS if os.path.exists(os.path.join(test_dir, f))]

    print(f"Running {len(available_tests)} fast tests:")
    for test_file in available_tests:
        print(f"  - {test_file}")
    print()

    # Results collection
    results = {
        'start_time': datetime.now().isoformat(),
        'test_results': {},
        'summary': {}
    }

    successful_tests = 0
    failed_tests = 0

    # Run each test
    for i, test_file in enumerate(available_tests):
        test_name = test_file[:-3]  # Remove .py extension
        print(f"[{i+1}/{len(available_tests)}] Running {test_name}...")
        print("-" * 40)

        test_result = None
        final_duration = 0

        # Retry logic
        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                print(f"  Retry {attempt}...")

            start_time = time.time()

            try:
                # Import test module
                spec = importlib.util.spec_from_file_location(
                    test_name,
                    os.path.join(test_dir, test_file)
                )
                test_module = importlib.util.module_from_spec(spec)

                # Add tidyllm to path
                tidyllm_path = os.path.abspath(os.path.join(test_dir, '..', '..', '..'))
                if tidyllm_path not in sys.path:
                    sys.path.insert(0, tidyllm_path)

                spec.loader.exec_module(test_module)

                # Find test function
                test_function_name = f"test_{test_name.split('_', 2)[-1]}"
                if hasattr(test_module, test_function_name):
                    test_func = getattr(test_module, test_function_name)
                else:
                    # Fallback
                    for attr_name in dir(test_module):
                        if attr_name.startswith('test_') and callable(getattr(test_module, attr_name)):
                            test_func = getattr(test_module, attr_name)
                            break
                    else:
                        raise Exception("No test function found")

                # Run with timeout monitoring
                test_result = test_func()
                elapsed = time.time() - start_time
                final_duration = elapsed

                # Check timeout
                if elapsed > TEST_TIMEOUT:
                    print(f"  WARNING: Test took {elapsed:.1f}s (>{TEST_TIMEOUT}s)")
                    if test_result and test_result.get('status') == 'COMPLETED':
                        print(f"  But test completed successfully, accepting result")
                        break
                    elif attempt < MAX_RETRIES - 1:
                        print(f"  Retrying due to timeout...")
                        continue
                    else:
                        test_result = {
                            'test_name': test_name,
                            'status': 'TIMEOUT',
                            'error': f'Exceeded {TEST_TIMEOUT}s timeout'
                        }
                else:
                    print(f"  Completed in {elapsed:.1f}s")
                    break

            except Exception as e:
                final_duration = time.time() - start_time
                print(f"  Attempt {attempt + 1} failed: {str(e)[:100]}...")

                if attempt < MAX_RETRIES - 1:
                    print(f"  Retrying in 1 second...")
                    time.sleep(1)
                else:
                    test_result = {
                        'test_name': test_name,
                        'status': 'ERROR',
                        'error': str(e)
                    }

        # Store result
        if test_result and test_result.get('status') in ['COMPLETED', 'SUCCESS']:
            successful_tests += 1
            print(f"  RESULT: PASS ({final_duration:.1f}s)")
            results['test_results'][test_name] = {
                'status': 'PASS',
                'duration': final_duration,
                'result': test_result
            }
        else:
            failed_tests += 1
            status = test_result.get('status', 'UNKNOWN') if test_result else 'NO_RESULT'
            print(f"  RESULT: FAIL - {status} ({final_duration:.1f}s)")
            results['test_results'][test_name] = {
                'status': 'FAIL',
                'duration': final_duration,
                'result': test_result
            }

        print()

    # Summary
    total_duration = sum(r.get('duration', 0) for r in results['test_results'].values())
    success_rate = successful_tests / len(available_tests) if available_tests else 0

    results['summary'] = {
        'total_tests': len(available_tests),
        'successful': successful_tests,
        'failed': failed_tests,
        'success_rate': success_rate,
        'total_duration': total_duration
    }

    print("=" * 50)
    print("FAST TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {len(available_tests)}")
    print(f"Passed: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {success_rate:.1%}")
    print(f"Total time: {total_duration:.1f}s")
    print()

    # Individual results
    print("Individual Results:")
    for test_name, result in results['test_results'].items():
        status = result['status']
        duration = result['duration']
        print(f"  {test_name:25} {status:8} ({duration:5.1f}s)")

    # Save results
    results_file = os.path.join(test_dir, f"fast_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved: {results_file}")
    except Exception as e:
        print(f"\nFailed to save results: {e}")

    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results

if __name__ == "__main__":
    results = run_fast_tests()