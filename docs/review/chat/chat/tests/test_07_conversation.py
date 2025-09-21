#!/usr/bin/env python3
"""
Test 7: Multi-Message Conversation
Purpose: Test conversation context handling
Status: READY TO RUN
"""

import tidyllm
import time

def test_conversation():
    """Test basic conversation context handling"""
    print("=== Conversation Test ===")

    conversation_turns = [
        ("My name is Alice", "name_establishment"),
        ("What is my name?", "name_recall"),
        ("I work at TechCorp", "work_establishment"),
        ("Where do I work?", "work_recall"),
        ("What do you know about me?", "comprehensive_recall")
    ]

    conversation_id = f"test_conv_{int(time.time())}"
    results = {}
    context_history = []

    print(f"Starting conversation: {conversation_id}")

    for turn_num, (message, purpose) in enumerate(conversation_turns):
        print(f"\nTurn {turn_num + 1}: {purpose}")
        print(f"Input: {message}")

        try:
            # Build context from previous turns (simple approach)
            if context_history:
                context_string = " | ".join(context_history)
                # Note: This may not work if tidyllm doesn't support context parameter
                # We'll try both with and without context
                try:
                    response = tidyllm.chat(message, chat_type='direct', context=context_string)
                except TypeError:
                    # If context parameter not supported, try without it
                    response = tidyllm.chat(message, chat_type='direct')
            else:
                response = tidyllm.chat(message, chat_type='direct')

            response_text = str(response)
            response_length = len(response_text)

            print(f"Output: {response_text[:200]}...")
            print(f"Length: {response_length} chars")

            # Analyze context awareness
            context_analysis = analyze_context_awareness(message, response_text, turn_num, context_history)

            results[f"turn_{turn_num + 1}"] = {
                'purpose': purpose,
                'message': message,
                'response': response_text,
                'response_length': response_length,
                'context_analysis': context_analysis,
                'status': 'SUCCESS'
            }

            # Add to context history
            context_history.append(f"{message} -> {response_text[:100]}")

        except Exception as e:
            print(f"Error: {e}")
            results[f"turn_{turn_num + 1}"] = {
                'purpose': purpose,
                'message': message,
                'error': str(e),
                'status': 'ERROR'
            }

    # Conversation analysis
    print(f"\nConversation Analysis:")

    successful_turns = [turn for turn, data in results.items()
                       if data['status'] == 'SUCCESS']
    failed_turns = [turn for turn, data in results.items()
                   if data['status'] == 'ERROR']

    print(f"Successful turns: {len(successful_turns)}/{len(conversation_turns)}")
    if failed_turns:
        print(f"Failed turns: {failed_turns}")

    # Check for context awareness
    context_aware_turns = []
    for turn, data in results.items():
        if data['status'] == 'SUCCESS':
            context_analysis = data.get('context_analysis', {})
            if context_analysis.get('likely_context_aware', False):
                context_aware_turns.append(turn)

    print(f"Likely context-aware turns: {len(context_aware_turns)}")

    # Overall conversation assessment
    if len(successful_turns) == len(conversation_turns):
        if len(context_aware_turns) >= 2:
            conversation_quality = "EXCELLENT"
        elif len(context_aware_turns) >= 1:
            conversation_quality = "GOOD"
        else:
            conversation_quality = "BASIC"
    else:
        conversation_quality = "POOR"

    print(f"Conversation quality: {conversation_quality}")

    return {
        'test_name': 'conversation',
        'conversation_id': conversation_id,
        'results': results,
        'successful_turns': len(successful_turns),
        'failed_turns': len(failed_turns),
        'context_aware_turns': len(context_aware_turns),
        'conversation_quality': conversation_quality,
        'status': 'COMPLETED'
    }

def analyze_context_awareness(message, response, turn_num, context_history):
    """Analyze if response shows context awareness"""

    # Simple heuristics for context awareness
    likely_context_aware = False
    analysis_notes = []

    # Check for name recall
    if "name" in message.lower() and turn_num > 0:
        if "alice" in response.lower():
            likely_context_aware = True
            analysis_notes.append("Name recalled correctly")
        else:
            analysis_notes.append("Name not found in response")

    # Check for work recall
    if "work" in message.lower() and turn_num > 2:
        if "techcorp" in response.lower():
            likely_context_aware = True
            analysis_notes.append("Work location recalled correctly")
        else:
            analysis_notes.append("Work location not found in response")

    # Check for comprehensive recall
    if "know about me" in message.lower():
        alice_mentioned = "alice" in response.lower()
        techcorp_mentioned = "techcorp" in response.lower()
        if alice_mentioned and techcorp_mentioned:
            likely_context_aware = True
            analysis_notes.append("Both name and work mentioned")
        elif alice_mentioned or techcorp_mentioned:
            analysis_notes.append("Partial context recalled")
        else:
            analysis_notes.append("No context recalled")

    return {
        'likely_context_aware': likely_context_aware,
        'analysis_notes': analysis_notes
    }

if __name__ == "__main__":
    result = test_conversation()
    print(f"\nTest completed: {result['test_name']}")