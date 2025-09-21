#!/usr/bin/env python3
"""
Test 9: Simple Load Test
Purpose: Test system with multiple sequential requests
Status: READY TO RUN
"""

import tidyllm
import time

def test_simple_load():
    """Test system performance with multiple sequential requests"""
    print("=== Simple Load Test ===")

    num_requests = 10
    test_message_base = "Load test message"

    print(f"Running {num_requests} sequential requests...")

    start_time = time.time()
    results = []

    for i in range(num_requests):
        request_start = time.time()
        test_message = f"{test_message_base} {i+1}"

        print(f"Request {i+1}/{num_requests}: {test_message}")

        try:
            response = tidyllm.chat(test_message, chat_type='direct')
            request_end = time.time()

            request_time = request_end - request_start
            response_length = len(str(response))

            result = {
                'request_id': i + 1,
                'message': test_message,
                'response_time': request_time,
                'response_length': response_length,
                'status': 'SUCCESS'
            }

            print(f"  SUCCESS: {request_time:.2f}s, {response_length} chars")

        except Exception as e:
            request_end = time.time()
            request_time = request_end - request_start

            result = {
                'request_id': i + 1,
                'message': test_message,
                'response_time': request_time,
                'error': str(e),
                'status': 'ERROR'
            }

            print(f"  ERROR: {e}")

        results.append(result)

    total_time = time.time() - start_time

    # Performance analysis
    print(f"\nLoad Test Results:")
    print(f"Total time: {total_time:.2f}s")

    successful_requests = [r for r in results if r['status'] == 'SUCCESS']
    failed_requests = [r for r in results if r['status'] == 'ERROR']

    success_count = len(successful_requests)
    failure_count = len(failed_requests)
    success_rate = success_count / num_requests

    print(f"Successful requests: {success_count}/{num_requests} ({success_rate:.1%})")
    print(f"Failed requests: {failure_count}")

    if successful_requests:
        # Response time analysis
        response_times = [r['response_time'] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)

        print(f"Response times:")
        print(f"  Average: {avg_response_time:.2f}s")
        print(f"  Minimum: {min_response_time:.2f}s")
        print(f"  Maximum: {max_response_time:.2f}s")

        # Throughput calculation
        throughput = success_count / total_time
        print(f"Throughput: {throughput:.2f} requests/second")

        # Response length analysis
        response_lengths = [r['response_length'] for r in successful_requests]
        avg_length = sum(response_lengths) / len(response_lengths)
        min_length = min(response_lengths)
        max_length = max(response_lengths)

        print(f"Response lengths:")
        print(f"  Average: {avg_length:.1f} chars")
        print(f"  Range: {min_length} - {max_length} chars")

        # Performance degradation check
        first_half = response_times[:len(response_times)//2]
        second_half = response_times[len(response_times)//2:]

        if len(first_half) > 0 and len(second_half) > 0:
            first_half_avg = sum(first_half) / len(first_half)
            second_half_avg = sum(second_half) / len(second_half)
            degradation = (second_half_avg - first_half_avg) / first_half_avg

            print(f"Performance degradation: {degradation:.1%}")
            if degradation > 0.2:
                print("  WARNING: Significant performance degradation detected")

    else:
        print("No successful requests for performance analysis")
        avg_response_time = None
        throughput = 0

    # Overall performance assessment
    if success_rate >= 0.9 and (avg_response_time is None or avg_response_time < 10):
        performance_rating = "EXCELLENT"
    elif success_rate >= 0.8 and (avg_response_time is None or avg_response_time < 20):
        performance_rating = "GOOD"
    elif success_rate >= 0.6:
        performance_rating = "FAIR"
    else:
        performance_rating = "POOR"

    print(f"Performance rating: {performance_rating}")

    # Error analysis
    if failed_requests:
        print(f"\nError Analysis:")
        error_types = {}
        for req in failed_requests:
            error_msg = req.get('error', 'Unknown error')
            error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
            error_types[error_type] = error_types.get(error_type, 0) + 1

        for error_type, count in error_types.items():
            print(f"  {error_type}: {count} occurrences")

    return {
        'test_name': 'simple_load',
        'num_requests': num_requests,
        'total_time': total_time,
        'successful_requests': success_count,
        'failed_requests': failure_count,
        'success_rate': success_rate,
        'avg_response_time': avg_response_time,
        'throughput': throughput,
        'performance_rating': performance_rating,
        'results': results,
        'status': 'COMPLETED'
    }

if __name__ == "__main__":
    result = test_simple_load()
    print(f"\nTest completed: {result['test_name']}")