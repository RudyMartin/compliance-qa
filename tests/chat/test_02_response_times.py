#!/usr/bin/env python3
"""
Test 2: Response Time Check
Purpose: Measure response times across different chat modes
Status: READY TO RUN
"""

import tidyllm
import time

def test_response_times():
    """Test response times for all chat modes"""
    print("=== Response Time Test ===")

    modes = ['direct', 'dspy', 'hybrid', 'custom']
    test_message = "Test response time"
    results = {}

    for mode in modes:
        print(f"Testing {mode} mode...")

        try:
            start_time = time.time()
            response = tidyllm.chat(test_message, chat_type=mode)
            end_time = time.time()

            response_time = end_time - start_time
            response_len = len(str(response))

            results[mode] = {
                'time': response_time,
                'length': response_len,
                'status': 'SUCCESS'
            }

            print(f"  {mode}: {response_time:.2f}s, {response_len} chars - OK")

        except Exception as e:
            results[mode] = {
                'time': None,
                'length': 0,
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"  {mode}: ERROR - {e}")

    # Performance analysis
    print(f"\nPerformance Summary:")
    successful_modes = [mode for mode, data in results.items() if data['status'] == 'SUCCESS']

    if successful_modes:
        times = [results[mode]['time'] for mode in successful_modes]
        fastest = min(times)
        slowest = max(times)
        average = sum(times) / len(times)

        print(f"  Successful modes: {len(successful_modes)}/{len(modes)}")
        print(f"  Fastest: {fastest:.2f}s")
        print(f"  Slowest: {slowest:.2f}s")
        print(f"  Average: {average:.2f}s")

        # Performance assessment
        if average < 5.0:
            print("  Performance: EXCELLENT (avg < 5s)")
        elif average < 15.0:
            print("  Performance: GOOD (avg < 15s)")
        else:
            print("  Performance: SLOW (avg >= 15s)")
    else:
        print("  No successful responses")

    return {
        'test_name': 'response_times',
        'results': results,
        'successful_modes': len(successful_modes),
        'total_modes': len(modes),
        'status': 'COMPLETED'
    }

if __name__ == "__main__":
    result = test_response_times()
    print(f"\nTest completed: {result['test_name']}")