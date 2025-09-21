#!/usr/bin/env python3
"""
Test 3: Reasoning Quality Check
Purpose: Validate reasoning=True provides good explanations
Status: READY TO RUN
"""

import tidyllm

def test_reasoning_quality():
    """Test reasoning quality across chat modes"""
    print("=== Reasoning Quality Test ===")

    modes = ['direct', 'dspy', 'hybrid']
    test_question = "Why is the sky blue?"
    results = {}

    for mode in modes:
        print(f"Testing {mode} mode reasoning...")

        try:
            response = tidyllm.chat(test_question, chat_type=mode, reasoning=True)

            if isinstance(response, dict):
                reasoning_text = response.get('reasoning', '')
                response_text = response.get('response', str(response))

                reasoning_length = len(reasoning_text)
                has_reasoning_field = 'reasoning' in response
                reasoning_quality = "GOOD" if reasoning_length > 50 else "SHORT"

                results[mode] = {
                    'has_reasoning_field': has_reasoning_field,
                    'reasoning_length': reasoning_length,
                    'reasoning_quality': reasoning_quality,
                    'response_length': len(response_text),
                    'status': 'SUCCESS'
                }

                print(f"  {mode}: reasoning={reasoning_length} chars - {reasoning_quality}")
                if reasoning_length > 0:
                    print(f"    Sample: {reasoning_text[:100]}...")

            else:
                # String response - no reasoning field
                response_length = len(str(response))
                results[mode] = {
                    'has_reasoning_field': False,
                    'reasoning_length': 0,
                    'reasoning_quality': 'NONE',
                    'response_length': response_length,
                    'status': 'NO_REASONING_FIELD'
                }
                print(f"  {mode}: no reasoning field, response={response_length} chars")

        except Exception as e:
            results[mode] = {
                'has_reasoning_field': False,
                'reasoning_length': 0,
                'reasoning_quality': 'ERROR',
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"  {mode}: ERROR - {e}")

    # Reasoning analysis
    print(f"\nReasoning Analysis:")
    modes_with_reasoning = [mode for mode, data in results.items()
                           if data.get('has_reasoning_field', False)]

    good_reasoning = [mode for mode, data in results.items()
                     if data.get('reasoning_quality') == 'GOOD']

    print(f"  Modes with reasoning field: {len(modes_with_reasoning)}/{len(modes)}")
    print(f"  Modes with good reasoning: {len(good_reasoning)}/{len(modes)}")

    if modes_with_reasoning:
        avg_reasoning_length = sum(results[mode]['reasoning_length']
                                 for mode in modes_with_reasoning) / len(modes_with_reasoning)
        print(f"  Average reasoning length: {avg_reasoning_length:.1f} chars")

    return {
        'test_name': 'reasoning_quality',
        'results': results,
        'modes_with_reasoning': len(modes_with_reasoning),
        'good_reasoning_count': len(good_reasoning),
        'status': 'COMPLETED'
    }

if __name__ == "__main__":
    result = test_reasoning_quality()
    print(f"\nTest completed: {result['test_name']}")