#!/usr/bin/env python3
"""
Test 10: RAG Mode Investigation
Purpose: Diagnose and document RAG mode issues
Status: READY TO RUN
"""

import tidyllm

def test_rag_investigation():
    """Investigate RAG mode issues and document findings"""
    print("=== RAG Mode Investigation ===")

    investigation_results = {}

    # Test 1: Default mode (should use RAG)
    print("1. Testing default mode (should attempt RAG)...")
    try:
        response = tidyllm.chat("What is artificial intelligence?")
        investigation_results['default_mode'] = {
            'status': 'SUCCESS',
            'response_type': type(response).__name__,
            'response_length': len(str(response)),
            'response_preview': str(response)[:200]
        }
        print(f"   Default mode: SUCCESS - {type(response)} ({len(str(response))} chars)")

        # Check if it's an error response
        if isinstance(response, dict) and 'error' in response:
            investigation_results['default_mode']['has_error'] = True
            investigation_results['default_mode']['error_message'] = response['error']
            print(f"   Error in response: {response['error']}")
        else:
            investigation_results['default_mode']['has_error'] = False

    except Exception as e:
        investigation_results['default_mode'] = {
            'status': 'EXCEPTION',
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
        print(f"   Default mode: EXCEPTION - {e}")

    # Test 2: Explicit RAG mode (if supported)
    print("\n2. Testing explicit RAG mode...")
    try:
        response = tidyllm.chat("What is machine learning?", chat_type="rag")
        investigation_results['explicit_rag'] = {
            'status': 'SUCCESS',
            'response_type': type(response).__name__,
            'response_length': len(str(response)),
            'response_preview': str(response)[:200]
        }
        print(f"   Explicit RAG: SUCCESS - {type(response)} ({len(str(response))} chars)")

    except Exception as e:
        investigation_results['explicit_rag'] = {
            'status': 'EXCEPTION',
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
        print(f"   Explicit RAG: EXCEPTION - {e}")

    # Test 3: Hybrid mode with knowledge question
    print("\n3. Testing hybrid mode with knowledge question...")
    try:
        response = tidyllm.chat("Explain deep learning", chat_type="hybrid")
        investigation_results['hybrid_knowledge'] = {
            'status': 'SUCCESS',
            'response_type': type(response).__name__,
            'response_length': len(str(response)),
            'response_preview': str(response)[:200]
        }
        print(f"   Hybrid knowledge: SUCCESS - {type(response)} ({len(str(response))} chars)")

    except Exception as e:
        investigation_results['hybrid_knowledge'] = {
            'status': 'EXCEPTION',
            'error_type': type(e).__name__,
            'error_message': str(e)
        }
        print(f"   Hybrid knowledge: EXCEPTION - {e}")

    # Test 4: Different RAG-style questions
    print("\n4. Testing various knowledge questions...")
    knowledge_questions = [
        "What is neural network?",
        "Explain supervised learning",
        "Define natural language processing",
        "What are the types of machine learning?"
    ]

    knowledge_results = {}
    for i, question in enumerate(knowledge_questions):
        print(f"   Question {i+1}: {question}")
        try:
            response = tidyllm.chat(question, reasoning=True)
            knowledge_results[f"question_{i+1}"] = {
                'question': question,
                'status': 'SUCCESS',
                'response_type': type(response).__name__,
                'response_length': len(str(response))
            }

            # Check for error patterns
            if isinstance(response, dict):
                if 'error' in response:
                    knowledge_results[f"question_{i+1}"]["has_error"] = True
                    knowledge_results[f"question_{i+1}"]["error_message"] = response['error']
                    print(f"     ERROR: {response['error']}")
                else:
                    knowledge_results[f"question_{i+1}"]["has_error"] = False
                    print(f"     SUCCESS: {len(str(response))} chars")
            else:
                knowledge_results[f"question_{i+1}"]["has_error"] = False
                print(f"     SUCCESS: {len(str(response))} chars")

        except Exception as e:
            knowledge_results[f"question_{i+1}"] = {
                'question': question,
                'status': 'EXCEPTION',
                'error_type': type(e).__name__,
                'error_message': str(e)
            }
            print(f"     EXCEPTION: {e}")

    investigation_results['knowledge_questions'] = knowledge_results

    # Analysis
    print(f"\nRAG Investigation Analysis:")

    # Check for consistent error patterns
    error_messages = []
    for test_name, result in investigation_results.items():
        if test_name == 'knowledge_questions':
            for q_result in result.values():
                if q_result.get('has_error'):
                    error_messages.append(q_result.get('error_message', ''))
        else:
            if result.get('has_error'):
                error_messages.append(result.get('error_message', ''))
            elif result.get('status') == 'EXCEPTION':
                error_messages.append(result.get('error_message', ''))

    print(f"Error messages collected: {len(error_messages)}")

    # Identify common error patterns
    if error_messages:
        print("Common error patterns:")
        error_patterns = {}
        for error_msg in error_messages:
            if "UnifiedRAGManager" in error_msg:
                error_patterns["UnifiedRAGManager"] = error_patterns.get("UnifiedRAGManager", 0) + 1
            if "query" in error_msg:
                error_patterns["query_method"] = error_patterns.get("query_method", 0) + 1
            if "attribute" in error_msg:
                error_patterns["missing_attribute"] = error_patterns.get("missing_attribute", 0) + 1

        for pattern, count in error_patterns.items():
            print(f"  {pattern}: {count} occurrences")

        # Primary issue identification
        if error_patterns.get("UnifiedRAGManager", 0) > 0 and error_patterns.get("query_method", 0) > 0:
            primary_issue = "UnifiedRAGManager missing query method"
        elif error_patterns.get("missing_attribute", 0) > 0:
            primary_issue = "Missing method/attribute in RAG system"
        else:
            primary_issue = "Unknown RAG system issue"

    else:
        primary_issue = "No consistent errors found"

    print(f"Primary issue identified: {primary_issue}")

    # Success analysis
    successful_tests = []
    for test_name, result in investigation_results.items():
        if test_name == 'knowledge_questions':
            for q_name, q_result in result.items():
                if q_result['status'] == 'SUCCESS' and not q_result.get('has_error', False):
                    successful_tests.append(f"{test_name}.{q_name}")
        else:
            if result['status'] == 'SUCCESS' and not result.get('has_error', False):
                successful_tests.append(test_name)

    print(f"Successful RAG-related tests: {len(successful_tests)}")
    if successful_tests:
        print(f"  Working: {successful_tests}")

    # Overall RAG status assessment
    total_tests = len(investigation_results) + len(knowledge_questions) - 1  # -1 because knowledge_questions is nested
    if len(successful_tests) == 0:
        rag_status = "COMPLETELY_BROKEN"
    elif len(successful_tests) < total_tests * 0.3:
        rag_status = "MOSTLY_BROKEN"
    elif len(successful_tests) < total_tests * 0.7:
        rag_status = "PARTIALLY_WORKING"
    else:
        rag_status = "MOSTLY_WORKING"

    print(f"Overall RAG status: {rag_status}")

    return {
        'test_name': 'rag_investigation',
        'investigation_results': investigation_results,
        'primary_issue': primary_issue,
        'successful_tests': len(successful_tests),
        'total_tests': total_tests,
        'rag_status': rag_status,
        'error_patterns': error_patterns if error_messages else {},
        'status': 'COMPLETED'
    }

if __name__ == "__main__":
    result = test_rag_investigation()
    print(f"\nTest completed: {result['test_name']}")