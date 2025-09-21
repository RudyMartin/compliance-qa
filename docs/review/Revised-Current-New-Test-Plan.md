# Revised Current New Test Plan - Chat Focus
**Date:** 2025-09-17
**Purpose:** Simplified test plan focused on chat functionality based on current working patterns
**Status:** 🎯 PRACTICAL IMPLEMENTATION - Matching existing test approach

## 🎯 Overview

This test plan builds directly on our **existing working chat tests** and expands them systematically. We focus on what's already working and add practical improvements that match the current testing style.

**Based on Current Working Tests:**
- ✅ Direct Mode: `tidyllm.chat("Hello!", chat_type="direct", reasoning=True)`
- ✅ DSPy Mode: `tidyllm.chat("Solve step by step", chat_type="dspy", reasoning=True)`
- ✅ Hybrid Mode: `tidyllm.chat("Explain reasoning step by step", chat_type="hybrid")`
- ⚠️ RAG Mode: Error with UnifiedRAGManager query method
- ✅ Custom Mode: Placeholder working

---

## 📋 Current Chat Tests (What We Have)

### Test 1: Direct Mode Validation
```python
# Current working test
python -c "import tidyllm; response = tidyllm.chat('Hello!', chat_type='direct', reasoning=True); print(response)"
```

**Results:** ✅ Working with full audit trails, token usage, 1989ms response time

### Test 2: DSPy Chain of Thought
```python
# Current working test
python -c "import tidyllm; response = tidyllm.chat('Solve step by step', chat_type='dspy', reasoning=True); print(response)"
```

**Results:** ✅ Working with reasoning chains, 250ms response time

### Test 3: Hybrid Intelligence
```python
# Current working test
python -c "import tidyllm; response = tidyllm.chat('Explain reasoning step by step', chat_type='hybrid'); print(response)"
```

**Results:** ✅ Working intelligent routing

### Test 4: RAG Mode Issue
```python
# Current failing test
python -c "import tidyllm; response = tidyllm.chat('What is machine learning?', reasoning=True); print(response)"
```

**Results:** ⚠️ Error: `'UnifiedRAGManager' object has no attribute 'query'`

---

## 🔧 New Chat Tests (Simple Additions)

### New Test 1: Chat Consistency Check
**Purpose:** Ensure same input gives consistent responses

```bash
# Run same test 3 times
cd tidyllm && python -c "
import tidyllm
print('=== Consistency Test ===')
for i in range(3):
    response = tidyllm.chat('Hello', chat_type='direct')
    print(f'Test {i+1}: {len(str(response))} chars')
"
```

**Expected:** Similar response lengths, no errors

### New Test 2: Response Time Check
**Purpose:** Measure response times across modes

```bash
# Time different modes
cd tidyllm && python -c "
import tidyllm, time
modes = ['direct', 'dspy', 'hybrid', 'custom']
for mode in modes:
    start = time.time()
    try:
        response = tidyllm.chat('Test', chat_type=mode)
        elapsed = time.time() - start
        print(f'{mode}: {elapsed:.2f}s - OK')
    except Exception as e:
        print(f'{mode}: ERROR - {e}')
"
```

**Expected:** Performance baseline for each mode

### New Test 3: Reasoning Quality Check
**Purpose:** Validate reasoning=True provides good explanations

```bash
# Test reasoning across modes
cd tidyllm && python -c "
import tidyllm
modes = ['direct', 'dspy', 'hybrid']
for mode in modes:
    try:
        response = tidyllm.chat('Why is the sky blue?', chat_type=mode, reasoning=True)
        if isinstance(response, dict) and 'reasoning' in response:
            reasoning_length = len(response['reasoning'])
            print(f'{mode}: reasoning={reasoning_length} chars')
        else:
            print(f'{mode}: no reasoning field')
    except Exception as e:
        print(f'{mode}: error - {e}')
"
```

**Expected:** Substantial reasoning text (>50 chars) for each mode

### New Test 4: Audit Trail Validation
**Purpose:** Ensure all responses have proper audit trails

```bash
# Check audit trails
cd tidyllm && python -c "
import tidyllm
response = tidyllm.chat('Audit test', chat_type='direct', reasoning=True)
if isinstance(response, dict):
    audit = response.get('audit_trail', {})
    required_fields = ['timestamp', 'user_id', 'model_id', 'success']
    missing = [f for f in required_fields if f not in audit]
    if missing:
        print(f'Missing audit fields: {missing}')
    else:
        print('Audit trail complete')
        print(f'Timestamp: {audit[\"timestamp\"]}')
        print(f'Model: {audit[\"model_id\"]}')
        print(f'Success: {audit[\"success\"]}')
else:
    print('No audit trail found')
"
```

**Expected:** All required audit fields present

### New Test 5: Token Usage Tracking
**Purpose:** Validate cost tracking works

```bash
# Check token usage
cd tidyllm && python -c "
import tidyllm
response = tidyllm.chat('Count my tokens', chat_type='direct', reasoning=True)
if isinstance(response, dict) and 'token_usage' in response:
    tokens = response['token_usage']
    print(f'Input tokens: {tokens.get(\"input\", \"missing\")}')
    print(f'Output tokens: {tokens.get(\"output\", \"missing\")}')
    print(f'Total tokens: {tokens.get(\"total\", \"missing\")}')

    # Validate math
    if all(k in tokens for k in ['input', 'output', 'total']):
        calculated_total = tokens['input'] + tokens['output']
        if calculated_total == tokens['total']:
            print('Token math correct')
        else:
            print(f'Token math error: {calculated_total} != {tokens[\"total\"]}')
else:
    print('No token usage found')
"
```

**Expected:** Token counts present and math correct

### New Test 6: Error Handling Check
**Purpose:** Test graceful error handling

```bash
# Test error scenarios
cd tidyllm && python -c "
import tidyllm

# Test empty input
try:
    response = tidyllm.chat('', chat_type='direct')
    print(f'Empty input: {type(response)} - {len(str(response))} chars')
except Exception as e:
    print(f'Empty input error: {e}')

# Test very long input
long_text = 'test ' * 1000
try:
    response = tidyllm.chat(long_text, chat_type='direct')
    print(f'Long input: {type(response)} - OK')
except Exception as e:
    print(f'Long input error: {e}')

# Test invalid mode
try:
    response = tidyllm.chat('test', chat_type='invalid_mode')
    print(f'Invalid mode: {type(response)}')
except Exception as e:
    print(f'Invalid mode error: {e}')
"
```

**Expected:** Graceful error handling, no crashes

### New Test 7: Multi-Message Conversation
**Purpose:** Test conversation context handling

```bash
# Test conversation flow
cd tidyllm && python -c "
import tidyllm

print('=== Conversation Test ===')
# Message 1: Establish context
response1 = tidyllm.chat('My name is Alice', chat_type='direct')
print(f'Message 1: Set name to Alice')

# Message 2: Reference context
response2 = tidyllm.chat('What is my name?', chat_type='direct')
print(f'Message 2: {response2}')

# Check if name was remembered (basic test)
if 'Alice' in str(response2):
    print('Context: Name remembered!')
else:
    print('Context: Name not found in response')
"
```

**Expected:** Basic context handling (may not work without conversation memory)

### New Test 8: Different Question Types
**Purpose:** Test chat with various question types

```bash
# Test different question types
cd tidyllm && python -c "
import tidyllm

question_types = [
    ('What is 2+2?', 'math'),
    ('Explain photosynthesis', 'science'),
    ('Write a haiku', 'creative'),
    ('List 3 benefits of exercise', 'factual'),
    ('How do you feel today?', 'conversational')
]

for question, qtype in question_types:
    try:
        response = tidyllm.chat(question, chat_type='direct')
        response_len = len(str(response))
        print(f'{qtype}: {response_len} chars - OK')
    except Exception as e:
        print(f'{qtype}: ERROR - {e}')
"
```

**Expected:** Reasonable responses to different question types

### New Test 9: Performance Under Load
**Purpose:** Simple load test with multiple requests

```bash
# Simple load test
cd tidyllm && python -c "
import tidyllm, time

print('=== Load Test ===')
start_time = time.time()
successful = 0
failed = 0

for i in range(10):  # 10 requests
    try:
        response = tidyllm.chat(f'Test {i}', chat_type='direct')
        successful += 1
        print(f'Request {i}: OK')
    except Exception as e:
        failed += 1
        print(f'Request {i}: FAILED - {e}')

total_time = time.time() - start_time
print(f'Results: {successful} successful, {failed} failed')
print(f'Total time: {total_time:.2f}s')
print(f'Average per request: {total_time/10:.2f}s')
"
```

**Expected:** Most requests successful, reasonable average time

### New Test 10: RAG Mode Fix Validation
**Purpose:** Test if RAG mode issues can be resolved

```bash
# Test RAG mode with different approaches
cd tidyllm && python -c "
import tidyllm

print('=== RAG Mode Investigation ===')

# Try default mode (should use RAG)
try:
    response1 = tidyllm.chat('What is artificial intelligence?')
    print(f'Default mode: {type(response1)}')
    if isinstance(response1, dict) and 'error' in response1:
        print(f'Default error: {response1[\"error\"]}')
except Exception as e:
    print(f'Default exception: {e}')

# Try explicit RAG mode (if supported)
try:
    response2 = tidyllm.chat('What is machine learning?', chat_type='rag')
    print(f'Explicit RAG: {type(response2)}')
except Exception as e:
    print(f'Explicit RAG exception: {e}')

# Try hybrid mode with knowledge question
try:
    response3 = tidyllm.chat('Explain deep learning', chat_type='hybrid')
    print(f'Hybrid knowledge: {len(str(response3))} chars')
except Exception as e:
    print(f'Hybrid exception: {e}')
"
```

**Expected:** Better understanding of RAG mode issues

---

## 📊 Simple Test Execution

### Morning Tests (Current Validation)
```bash
# Run existing tests to ensure they still work
cd tidyllm
python -c "import tidyllm; print('Direct:', tidyllm.chat('Hello', chat_type='direct')[:50])"
python -c "import tidyllm; print('DSPy:', tidyllm.chat('Step by step', chat_type='dspy')[:50])"
python -c "import tidyllm; print('Hybrid:', tidyllm.chat('Explain this', chat_type='hybrid')[:50])"
```

### Afternoon Tests (New Validation)
```bash
# Run new tests 1-5
# Copy each test command from above sections
```

### Evening Tests (Performance & Issues)
```bash
# Run tests 6-10
# Focus on error handling and RAG investigation
```

---

## 🎯 Expected Results

### What Should Work
- **Direct Mode:** Full responses with audit trails and token tracking
- **DSPy Mode:** Step-by-step reasoning responses
- **Hybrid Mode:** Intelligent routing to appropriate processing
- **Custom Mode:** Placeholder responses

### What Needs Investigation
- **RAG Mode:** UnifiedRAGManager query method issue
- **Performance:** Response time consistency
- **Context:** Conversation memory capabilities
- **Load Handling:** Multiple concurrent requests

### Success Criteria
- **90%+ tests pass** without errors
- **Response times** under 10 seconds average
- **Audit trails** present in all responses
- **Token tracking** accurate in all responses
- **Error handling** graceful for invalid inputs

---

## 📋 Test Results Template

```
Test Results - Chat Focus
========================

Current Tests (Baseline):
□ Direct Mode: ✅/❌ - Response time: ___s
□ DSPy Mode: ✅/❌ - Response time: ___s
□ Hybrid Mode: ✅/❌ - Response time: ___s
□ RAG Mode: ✅/❌ - Error: ___
□ Custom Mode: ✅/❌ - Response time: ___s

New Tests (Validation):
□ Consistency: ✅/❌ - Variance: ___
□ Timing: ✅/❌ - Average: ___s
□ Reasoning: ✅/❌ - Quality: ___
□ Audit Trails: ✅/❌ - Complete: ___
□ Token Usage: ✅/❌ - Accurate: ___
□ Error Handling: ✅/❌ - Graceful: ___
□ Conversation: ✅/❌ - Context: ___
□ Question Types: ✅/❌ - Variety: ___
□ Load Test: ✅/❌ - Success rate: ___%
□ RAG Investigation: ✅/❌ - Issue: ___

Overall Status: ___
Next Steps: ___
```

This simplified plan focuses on **practical chat testing** that builds directly on what we already know works!