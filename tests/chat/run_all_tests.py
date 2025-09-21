#!/usr/bin/env python3
"""
Run All Chat Tests
Purpose: Execute all 10 chat tests and collect results
Status: READY TO RUN
"""

import os
import sys
import importlib.util
import json
import time
import signal
from datetime import datetime

# Test configuration
MAX_RETRIES = 3
TEST_TIMEOUT = 60  # seconds per test
GLOBAL_TIMEOUT = 1200  # 20 minutes total

def run_all_tests():
    """Run all chat tests and collect results"""
    print("=== TidyLLM Chat Test Suite ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get test directory
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Find all test files
    test_files = [f for f in os.listdir(test_dir)
                  if f.startswith('test_') and f.endswith('.py') and f != 'run_all_tests.py']
    test_files.sort()

    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    print()

    # Results collection
    all_results = {
        'start_time': datetime.now().isoformat(),
        'test_results': {},
        'summary': {}
    }

    successful_tests = 0
    failed_tests = 0

    # Run each test with retries and timeout
    for i, test_file in enumerate(test_files):
        test_name = test_file[:-3]  # Remove .py extension
        print(f"[{i+1}/{len(test_files)}] Running {test_name}...")
        print("=" * 50)

        test_result = None
        test_duration = 0

        # Retry logic
        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                print(f"  Retry {attempt}/{MAX_RETRIES-1}...")

            test_start_time = time.time()

            try:
                # Import and run the test with timeout
                spec = importlib.util.spec_from_file_location(
                    test_name,
                    os.path.join(test_dir, test_file)
                )
                test_module = importlib.util.module_from_spec(spec)

                # Add tidyllm parent directory to path if needed
                tidyllm_path = os.path.abspath(os.path.join(test_dir, '..', '..', '..'))
                if tidyllm_path not in sys.path:
                    sys.path.insert(0, tidyllm_path)

                spec.loader.exec_module(test_module)

                # Find and execute the main test function with timeout
                test_function_name = f"test_{test_name.split('_', 2)[-1]}"  # Extract test name part

                def run_test_with_timeout():
                    if hasattr(test_module, test_function_name):
                        return getattr(test_module, test_function_name)()
                    else:
                        # Fallback: look for any function that returns a result dict
                        for attr_name in dir(test_module):
                            if attr_name.startswith('test_') and callable(getattr(test_module, attr_name)):
                                return getattr(test_module, attr_name)()
                        return {
                            'test_name': test_name,
                            'status': 'ERROR',
                            'error': 'No test function found'
                        }

                # Execute with timeout check
                start_time = time.time()
                test_result = run_test_with_timeout()

                # Check if we exceeded timeout
                elapsed = time.time() - start_time
                if elapsed > TEST_TIMEOUT:
                    print(f"  Test exceeded timeout ({elapsed:.1f}s > {TEST_TIMEOUT}s)")
                    if attempt < MAX_RETRIES - 1:
                        continue  # Retry
                    else:
                        test_result = {
                            'test_name': test_name,
                            'status': 'TIMEOUT',
                            'error': f'Test exceeded {TEST_TIMEOUT}s timeout'
                        }

                # Success - break out of retry loop
                test_duration = time.time() - test_start_time
                break

            except Exception as e:
                test_duration = time.time() - test_start_time
                print(f"  Attempt {attempt + 1} failed: {e}")

                if attempt < MAX_RETRIES - 1:
                    print(f"  Retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    # Final attempt failed
                    test_result = {
                        'test_name': test_name,
                        'status': 'ERROR',
                        'error': str(e),
                        'attempts': MAX_RETRIES
                    }

        # Store final result
        if test_result:
            all_results['test_results'][test_name] = {
                'result': test_result,
                'duration': test_duration,
                'execution_status': 'SUCCESS' if test_result.get('status') in ['COMPLETED', 'SUCCESS'] else 'FAILED'
            }

            if test_result.get('status') in ['COMPLETED', 'SUCCESS']:
                successful_tests += 1
                print(f"[PASS] {test_name} COMPLETED ({test_duration:.1f}s)")
            else:
                failed_tests += 1
                status = test_result.get('status', 'UNKNOWN')
                print(f"[FAIL] {test_name} {status} ({test_duration:.1f}s)")
        else:
            # No result obtained
            all_results['test_results'][test_name] = {
                'execution_status': 'NO_RESULT',
                'error': 'No result after retries',
                'duration': test_duration
            }
            failed_tests += 1
            print(f"[ERROR] {test_name} NO_RESULT ({test_duration:.1f}s)")

        print()

    # Calculate total time
    total_duration = sum(result.get('duration', 0)
                        for result in all_results['test_results'].values())

    # Generate summary
    all_results['end_time'] = datetime.now().isoformat()
    all_results['summary'] = {
        'total_tests': len(test_files),
        'successful_tests': successful_tests,
        'failed_tests': failed_tests,
        'success_rate': successful_tests / len(test_files) if test_files else 0,
        'total_duration': total_duration
    }

    # Print summary
    print("=" * 60)
    print("TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(test_files)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {all_results['summary']['success_rate']:.1%}")
    print(f"Total duration: {total_duration:.1f}s")
    print()

    # Detailed results
    print("DETAILED RESULTS:")
    print("-" * 40)
    for test_name, test_data in all_results['test_results'].items():
        duration = test_data.get('duration', 0)
        if test_data.get('execution_status') == 'SUCCESS':
            result = test_data['result']
            status = result.get('status', 'UNKNOWN')
            print(f"{test_name:25} {status:12} ({duration:5.1f}s)")
        else:
            print(f"{test_name:25} {'EXCEPTION':12} ({duration:5.1f}s)")

    # Save results to file
    results_file = os.path.join(test_dir, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    try:
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nResults saved to: {results_file}")
    except Exception as e:
        print(f"\nFailed to save results: {e}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return all_results

if __name__ == "__main__":
    results = run_all_tests()