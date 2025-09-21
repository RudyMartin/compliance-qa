#!/usr/bin/env python3
"""
Test 1: Chat Consistency Check
Purpose: Ensure same input gives consistent responses
Status: READY TO RUN
"""

import tidyllm
import time

def test_consistency():
    """Test consistency of responses for same input"""
    print("=== Chat Consistency Test ===")

    test_message = "Hello"
    responses = []
    response_lengths = []

    for i in range(3):
        print(f"Running test {i+1}/3...")
        try:
            start_time = time.time()
            response = tidyllm.chat(test_message, chat_type='direct')
            end_time = time.time()

            responses.append(response)
            response_len = len(str(response))
            response_lengths.append(response_len)
            response_time = end_time - start_time

            print(f"  Test {i+1}: {response_len} chars, {response_time:.2f}s")

        except Exception as e:
            print(f"  Test {i+1}: ERROR - {e}")
            responses.append(None)
            response_lengths.append(0)

    # Analyze consistency
    valid_responses = [r for r in responses if r is not None]
    valid_lengths = [l for l in response_lengths if l > 0]

    if len(valid_responses) >= 2:
        min_len = min(valid_lengths)
        max_len = max(valid_lengths)
        avg_len = sum(valid_lengths) / len(valid_lengths)
        variance = max_len - min_len

        print(f"\nResults:")
        print(f"  Valid responses: {len(valid_responses)}/3")
        print(f"  Length range: {min_len} - {max_len} chars")
        print(f"  Average length: {avg_len:.1f} chars")
        print(f"  Variance: {variance} chars")

        # Consistency criteria
        if variance < avg_len * 0.5:  # Variance less than 50% of average
            print(f"  Consistency: GOOD (variance {variance} < {avg_len*0.5:.1f})")
        else:
            print(f"  Consistency: VARIABLE (variance {variance} >= {avg_len*0.5:.1f})")
    else:
        print("\nResults: FAILED - Insufficient valid responses")

    return {
        'test_name': 'consistency',
        'valid_responses': len(valid_responses),
        'total_attempts': 3,
        'response_lengths': response_lengths,
        'status': 'COMPLETED'
    }

if __name__ == "__main__":
    result = test_consistency()
    print(f"\nTest completed: {result}")