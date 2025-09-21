#!/usr/bin/env python3
"""
Test 8: Different Question Types
Purpose: Test chat with various question types
Status: READY TO RUN
"""

import tidyllm

def test_question_types():
    """Test chat responses to different types of questions"""
    print("=== Question Types Test ===")

    question_types = [
        ("What is 2+2?", "math"),
        ("Explain photosynthesis briefly", "science"),
        ("Write a short haiku", "creative"),
        ("List 3 benefits of exercise", "factual_list"),
        ("How do you feel today?", "conversational"),
        ("What is the capital of France?", "factual_simple"),
        ("Compare cats and dogs", "comparative"),
        ("Why is teamwork important?", "explanatory"),
        ("Describe the color blue", "descriptive"),
        ("If I have 10 apples and eat 3, how many remain?", "word_problem")
    ]

    results = {}

    for question, question_type in question_types:
        print(f"\nTesting {question_type} question...")
        print(f"Question: {question}")

        try:
            response = tidyllm.chat(question, chat_type='direct')
            response_text = str(response)
            response_length = len(response_text)

            # Basic response analysis
            analysis = analyze_response_quality(question, response_text, question_type)

            results[question_type] = {
                'question': question,
                'response': response_text,
                'response_length': response_length,
                'analysis': analysis,
                'status': 'SUCCESS'
            }

            print(f"Response ({response_length} chars): {response_text[:150]}...")
            print(f"Quality: {analysis['quality_assessment']}")

        except Exception as e:
            print(f"ERROR: {e}")
            results[question_type] = {
                'question': question,
                'error': str(e),
                'status': 'ERROR'
            }

    # Overall analysis
    print(f"\nQuestion Types Analysis:")

    successful_types = [qtype for qtype, data in results.items()
                       if data['status'] == 'SUCCESS']
    failed_types = [qtype for qtype, data in results.items()
                   if data['status'] == 'ERROR']

    print(f"Successful question types: {len(successful_types)}/{len(question_types)}")
    if failed_types:
        print(f"Failed question types: {failed_types}")

    # Quality analysis
    if successful_types:
        quality_counts = {}
        for qtype in successful_types:
            quality = results[qtype]['analysis']['quality_assessment']
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        print("Response quality distribution:")
        for quality, count in quality_counts.items():
            print(f"  {quality}: {count}")

        # Response length analysis
        lengths = [results[qtype]['response_length'] for qtype in successful_types]
        avg_length = sum(lengths) / len(lengths)
        min_length = min(lengths)
        max_length = max(lengths)

        print(f"Response lengths: avg={avg_length:.1f}, min={min_length}, max={max_length}")

    # Overall assessment
    success_rate = len(successful_types) / len(question_types)
    if success_rate >= 0.9:
        overall_performance = "EXCELLENT"
    elif success_rate >= 0.7:
        overall_performance = "GOOD"
    elif success_rate >= 0.5:
        overall_performance = "FAIR"
    else:
        overall_performance = "POOR"

    print(f"Overall performance: {overall_performance} ({success_rate:.1%} success rate)")

    return {
        'test_name': 'question_types',
        'results': results,
        'successful_types': len(successful_types),
        'failed_types': len(failed_types),
        'total_types': len(question_types),
        'success_rate': success_rate,
        'overall_performance': overall_performance,
        'status': 'COMPLETED'
    }

def analyze_response_quality(question, response, question_type):
    """Analyze response quality based on question type"""

    response_lower = response.lower()
    analysis = {
        'relevant_keywords': [],
        'quality_indicators': [],
        'quality_assessment': 'UNKNOWN'
    }

    # Type-specific analysis
    if question_type == "math":
        if "4" in response or "four" in response_lower:
            analysis['relevant_keywords'].append("correct_answer")
        if any(word in response_lower for word in ["plus", "add", "sum", "equals"]):
            analysis['quality_indicators'].append("mathematical_language")

    elif question_type == "science":
        science_words = ["plant", "sunlight", "carbon", "dioxide", "oxygen", "glucose", "chlorophyll"]
        found_science_words = [word for word in science_words if word in response_lower]
        analysis['relevant_keywords'].extend(found_science_words)

    elif question_type == "creative":
        if len(response.split('\n')) >= 3:  # Haiku structure
            analysis['quality_indicators'].append("structured_format")
        if any(word in response_lower for word in ["nature", "season", "beauty"]):
            analysis['quality_indicators'].append("appropriate_theme")

    elif question_type == "factual_list":
        if response.count('1') > 0 or response.count('2') > 0 or response.count('3') > 0:
            analysis['quality_indicators'].append("numbered_list")
        exercise_words = ["health", "strength", "fitness", "energy", "heart"]
        found_exercise_words = [word for word in exercise_words if word in response_lower]
        analysis['relevant_keywords'].extend(found_exercise_words)

    elif question_type == "conversational":
        conversational_indicators = ["i", "feel", "today", "good", "fine", "well"]
        found_indicators = [word for word in conversational_indicators if word in response_lower]
        analysis['relevant_keywords'].extend(found_indicators)

    elif question_type == "factual_simple":
        if "paris" in response_lower:
            analysis['relevant_keywords'].append("correct_answer")

    elif question_type == "word_problem":
        if "7" in response or "seven" in response_lower:
            analysis['relevant_keywords'].append("correct_answer")

    # General quality assessment
    response_length = len(response)
    has_relevant_content = len(analysis['relevant_keywords']) > 0
    has_quality_indicators = len(analysis['quality_indicators']) > 0
    reasonable_length = 20 <= response_length <= 1000

    if has_relevant_content and reasonable_length:
        if has_quality_indicators:
            analysis['quality_assessment'] = "EXCELLENT"
        else:
            analysis['quality_assessment'] = "GOOD"
    elif reasonable_length:
        analysis['quality_assessment'] = "FAIR"
    else:
        analysis['quality_assessment'] = "POOR"

    return analysis

if __name__ == "__main__":
    result = test_question_types()
    print(f"\nTest completed: {result['test_name']}")