# MLflow Usage Examples

Complete examples showing how to use MLflow session tracking and activity monitoring in TidyLLM.

## Quick Reference

### Basic Session Tracking
```python
import tidyllm

# Simple chat with session tracking
response = tidyllm.chat(
    "What is machine learning?",
    chat_type='direct',
    user_id='example_user',
    audit_reason='learning_session'
)
```

### All Chat Modes with Tracking
```python
# Test all modes with session tracking
modes = ['direct', 'dspy', 'rag', 'hybrid']

for mode in modes:
    response = tidyllm.chat(
        f"Test {mode} mode with tracking",
        chat_type=mode,
        reasoning=True,
        user_id=f'test_user_{mode}',
        audit_reason=f'{mode}_mode_test'
    )
    print(f"{mode} mode: {'SUCCESS' if response else 'FAILED'}")
```

## User Session Management

### Single User Session
```python
import uuid
from datetime import datetime

# Create unique session for a user
user_id = "john_doe_123"
session_id = str(uuid.uuid4())
start_time = datetime.now()

print(f"Starting session {session_id} for user {user_id}")

# Multiple questions in same session
questions = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "Explain neural networks"
]

for i, question in enumerate(questions, 1):
    response = tidyllm.chat(
        question,
        chat_type='hybrid',
        user_id=user_id,
        session_id=session_id,
        audit_reason=f'learning_session_q{i}'
    )

    print(f"Question {i}: {len(response.get('content', ''))} chars response")

print(f"Session duration: {datetime.now() - start_time}")
```

### Multi-User Concurrent Sessions
```python
import threading
import time

def user_session(user_id, questions):
    """Simulate a user session with multiple questions."""
    session_id = str(uuid.uuid4())

    for i, question in enumerate(questions):
        response = tidyllm.chat(
            question,
            chat_type='direct',
            user_id=user_id,
            session_id=session_id,
            audit_reason=f'concurrent_session_{i+1}'
        )

        print(f"User {user_id}: Question {i+1} completed")
        time.sleep(1)  # Simulate user think time

# Simulate 3 concurrent users
users = [
    ("user_alice", ["Question about AI", "Follow-up on ML"]),
    ("user_bob", ["What is NLP?", "How does it work?"]),
    ("user_charlie", ["Explain deep learning", "Show me examples"])
]

threads = []
for user_id, questions in users:
    thread = threading.Thread(target=user_session, args=(user_id, questions))
    threads.append(thread)
    thread.start()

# Wait for all sessions to complete
for thread in threads:
    thread.join()

print("All concurrent sessions completed")
```

## Activity Monitoring Examples

### View Recent Activity
```python
from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records

# Generate some activity first
for i in range(3):
    tidyllm.chat(
        f"Activity monitoring test {i+1}",
        chat_type='direct',
        user_id=f'monitoring_user_{i+1}',
        audit_reason='activity_monitoring_demo'
    )

print("Checking recent MLflow activity...")
show_last_5_mlflow_records()
```

### Evidence Checking
```python
from tidyllm.infrastructure.tools.mlflow_evidence_checker import show_missing_evidence

# Check for missing evidence after activity
show_missing_evidence()
```

### Custom Activity Analysis
```python
from tidyllm.services import MLflowIntegrationService
import time

# Test MLflow service directly
mlflow_service = MLflowIntegrationService()

print("=== MLflow Service Status ===")
print(f"Available: {mlflow_service.is_available()}")
print(f"Connected: {mlflow_service.is_connected}")
print(f"Has logging method: {hasattr(mlflow_service, 'log_llm_request')}")

# Generate test activity with custom parameters
test_cases = [
    {
        'model': 'claude-3-sonnet',
        'user_id': 'analysis_user_1',
        'prompt': 'Test prompt for analysis',
        'response': 'Test response content',
        'processing_time': 1500.0,
        'tokens': {'input': 8, 'output': 15, 'total': 23}
    },
    {
        'model': 'claude-3-haiku',
        'user_id': 'analysis_user_2',
        'prompt': 'Another test prompt',
        'response': 'Another test response',
        'processing_time': 800.0,
        'tokens': {'input': 12, 'output': 25, 'total': 37}
    }
]

print("\n=== Logging Test Cases ===")
for i, case in enumerate(test_cases, 1):
    result = mlflow_service.log_llm_request(
        model=case['model'],
        prompt=case['prompt'],
        response=case['response'],
        processing_time=case['processing_time'],
        token_usage=case['tokens'],
        success=True,
        user_id=case['user_id'],
        audit_reason=f'custom_analysis_test_{i}'
    )
    print(f"Test case {i}: {'SUCCESS' if result else 'FAILED'}")
    time.sleep(0.5)
```

## Performance Testing

### Response Time Analysis
```python
import time
from datetime import datetime

def test_mode_performance(mode, iterations=5):
    """Test performance of a specific chat mode with tracking."""
    times = []

    for i in range(iterations):
        start = time.time()

        response = tidyllm.chat(
            f"Performance test {i+1} for {mode} mode",
            chat_type=mode,
            user_id=f'perf_user_{mode}',
            audit_reason=f'performance_test_{mode}'
        )

        end = time.time()
        times.append(end - start)

        # Extract processing time from audit trail if available
        if isinstance(response, dict) and 'audit_trail' in response:
            internal_time = response['audit_trail'].get('processing_time_ms', 0)
            print(f"{mode} test {i+1}: {end-start:.2f}s total, {internal_time:.0f}ms internal")

    avg_time = sum(times) / len(times)
    print(f"{mode} mode average: {avg_time:.2f}s over {iterations} tests")
    return avg_time

# Test all modes
modes = ['direct', 'dspy', 'rag', 'hybrid']
results = {}

print("=== Performance Testing with MLflow Tracking ===")
for mode in modes:
    results[mode] = test_mode_performance(mode, 3)

print("\n=== Performance Summary ===")
for mode, avg_time in sorted(results.items(), key=lambda x: x[1]):
    print(f"{mode:8}: {avg_time:.2f}s average")
```

### Load Testing
```python
import concurrent.futures
import time

def load_test_chat(user_id, request_num):
    """Single chat request for load testing."""
    start_time = time.time()

    response = tidyllm.chat(
        f"Load test request {request_num}",
        chat_type='direct',
        user_id=user_id,
        audit_reason=f'load_test_req_{request_num}'
    )

    end_time = time.time()

    success = bool(response)
    tokens = 0
    if isinstance(response, dict) and 'token_usage' in response:
        tokens = response['token_usage'].get('total', 0)

    return {
        'user_id': user_id,
        'request_num': request_num,
        'success': success,
        'duration': end_time - start_time,
        'tokens': tokens
    }

def run_load_test(num_users=5, requests_per_user=3):
    """Run concurrent load test with MLflow tracking."""
    print(f"=== Load Test: {num_users} users, {requests_per_user} requests each ===")

    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = []

        for user_num in range(num_users):
            user_id = f'load_user_{user_num+1}'

            for req_num in range(requests_per_user):
                future = executor.submit(load_test_chat, user_id, req_num+1)
                futures.append(future)

        # Collect results
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"User {result['user_id']} req {result['request_num']}: "
                  f"{'SUCCESS' if result['success'] else 'FAILED'} "
                  f"({result['duration']:.2f}s, {result['tokens']} tokens)")

    end_time = time.time()

    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\n=== Load Test Results ===")
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {len(successful)/len(results)*100:.1f}%")
    print(f"Total time: {end_time-start_time:.2f}s")

    if successful:
        avg_duration = sum(r['duration'] for r in successful) / len(successful)
        total_tokens = sum(r['tokens'] for r in successful)
        print(f"Average response time: {avg_duration:.2f}s")
        print(f"Total tokens used: {total_tokens}")

# Run the load test
run_load_test(num_users=3, requests_per_user=2)
```

## Error Handling & Debugging

### Error Tracking Example
```python
def test_error_handling():
    """Test error cases with MLflow tracking."""

    test_cases = [
        # Valid case
        {
            'message': 'Valid test message',
            'chat_type': 'direct',
            'expected': 'success'
        },
        # Invalid mode
        {
            'message': 'Test with invalid mode',
            'chat_type': 'invalid_mode',
            'expected': 'error'
        },
        # None input
        {
            'message': None,
            'chat_type': 'direct',
            'expected': 'error'
        }
    ]

    print("=== Error Handling Test ===")

    for i, case in enumerate(test_cases, 1):
        try:
            response = tidyllm.chat(
                case['message'],
                chat_type=case['chat_type'],
                user_id=f'error_test_user_{i}',
                audit_reason=f'error_handling_test_{i}'
            )

            success = bool(response)
            print(f"Test {i}: {'SUCCESS' if success else 'FAILED'} "
                  f"(expected {case['expected']})")

            # Check if error was tracked in audit trail
            if isinstance(response, dict) and 'audit_trail' in response:
                error = response['audit_trail'].get('error')
                if error:
                    print(f"  Error tracked: {error}")

        except Exception as e:
            print(f"Test {i}: EXCEPTION - {e}")

test_error_handling()
```

### Service Diagnostics
```python
def run_mlflow_diagnostics():
    """Comprehensive MLflow service diagnostics."""
    print("=== MLflow Service Diagnostics ===")

    from tidyllm.services import MLflowIntegrationService

    # Test service initialization
    try:
        service = MLflowIntegrationService()
        print("✓ Service initialization: SUCCESS")
    except Exception as e:
        print(f"✗ Service initialization: FAILED - {e}")
        return

    # Test service status
    print(f"✓ Service available: {service.is_available()}")
    print(f"✓ Service connected: {service.is_connected}")
    print(f"✓ Has log method: {hasattr(service, 'log_llm_request')}")

    # Test logging capability
    try:
        result = service.log_llm_request(
            model='diagnostic-test',
            prompt='diagnostic prompt',
            response='diagnostic response',
            processing_time=100.0,
            success=True,
            user_id='diagnostic_user',
            audit_reason='service_diagnostic'
        )
        print(f"✓ Manual logging: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        print(f"✗ Manual logging: FAILED - {e}")

    # Test chat integration
    try:
        response = tidyllm.chat(
            "Diagnostic test message",
            chat_type='direct',
            user_id='diagnostic_user',
            audit_reason='chat_diagnostic'
        )

        has_audit = isinstance(response, dict) and 'audit_trail' in response
        has_tokens = isinstance(response, dict) and 'token_usage' in response

        print(f"✓ Chat integration: {'SUCCESS' if response else 'FAILED'}")
        print(f"✓ Audit trail present: {has_audit}")
        print(f"✓ Token usage present: {has_tokens}")

    except Exception as e:
        print(f"✗ Chat integration: FAILED - {e}")

run_mlflow_diagnostics()
```

## Integration Testing

### End-to-End Session Test
```python
def test_complete_session_flow():
    """Test complete session flow from start to finish."""
    import uuid
    from datetime import datetime

    # Session setup
    user_id = "integration_test_user"
    session_id = str(uuid.uuid4())
    start_time = datetime.now()

    print(f"=== Complete Session Flow Test ===")
    print(f"User: {user_id}")
    print(f"Session: {session_id}")
    print(f"Started: {start_time}")

    # Step 1: Multiple chat interactions
    interactions = [
        ("direct", "Hello, start my session"),
        ("dspy", "Think step by step about AI"),
        ("rag", "What information do you have?"),
        ("hybrid", "Final question for this session")
    ]

    results = []
    for mode, message in interactions:
        print(f"\nStep: {mode} mode")

        response = tidyllm.chat(
            message,
            chat_type=mode,
            user_id=user_id,
            session_id=session_id,
            audit_reason=f'integration_test_{mode}'
        )

        result = {
            'mode': mode,
            'success': bool(response),
            'has_audit': isinstance(response, dict) and 'audit_trail' in response,
            'has_tokens': isinstance(response, dict) and 'token_usage' in response
        }

        if result['has_audit']:
            audit = response['audit_trail']
            result['user_id_tracked'] = audit.get('user_id') == user_id
            result['processing_time'] = audit.get('processing_time_ms', 0)

        if result['has_tokens']:
            tokens = response['token_usage']
            result['total_tokens'] = tokens.get('total', 0)

        results.append(result)
        print(f"  Success: {result['success']}")
        print(f"  Audit trail: {result['has_audit']}")
        print(f"  Token usage: {result['has_tokens']}")

    # Step 2: Analyze session results
    end_time = datetime.now()
    session_duration = end_time - start_time

    successful_interactions = sum(1 for r in results if r['success'])
    total_tokens = sum(r.get('total_tokens', 0) for r in results)
    avg_processing_time = sum(r.get('processing_time', 0) for r in results) / len(results)

    print(f"\n=== Session Summary ===")
    print(f"Duration: {session_duration}")
    print(f"Successful interactions: {successful_interactions}/{len(interactions)}")
    print(f"Total tokens used: {total_tokens}")
    print(f"Average processing time: {avg_processing_time:.0f}ms")

    # Step 3: Check MLflow tracking
    print(f"\n=== Checking MLflow Records ===")
    try:
        from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records
        show_last_5_mlflow_records()
        print("✓ MLflow records retrieved successfully")
    except Exception as e:
        print(f"✗ MLflow records failed: {e}")

    return {
        'session_id': session_id,
        'user_id': user_id,
        'duration': session_duration,
        'results': results,
        'summary': {
            'successful_interactions': successful_interactions,
            'total_interactions': len(interactions),
            'total_tokens': total_tokens,
            'avg_processing_time': avg_processing_time
        }
    }

# Run the complete test
session_results = test_complete_session_flow()
```

## Command Line Examples

### Direct MLflow Viewer Usage
```bash
# Navigate to tidyllm directory
cd /path/to/tidyllm

# View recent MLflow activity
python infrastructure/tools/mlflow_viewer.py

# Check for missing evidence
python infrastructure/tools/mlflow_evidence_checker.py

# Run session tracking tests
cd tests/mlflow
python test_session_tracking.py

# Run activity viewer tests
python test_activity_viewer.py
```

### Batch Processing Example
```bash
# Create a batch processing script
cat > batch_test.py << 'EOF'
import tidyllm
import time

users = ['batch_user_1', 'batch_user_2', 'batch_user_3']
questions = [
    'What is artificial intelligence?',
    'How does machine learning work?',
    'Explain deep learning'
]

for user in users:
    for i, question in enumerate(questions):
        response = tidyllm.chat(
            question,
            chat_type='direct',
            user_id=user,
            audit_reason=f'batch_processing_q{i+1}'
        )
        print(f"{user}: Question {i+1} completed")
        time.sleep(1)

print("Batch processing complete")
EOF

# Run the batch test
python batch_test.py

# Check results in MLflow
python infrastructure/tools/mlflow_viewer.py
```

These examples demonstrate the complete MLflow session tracking capabilities in TidyLLM, from basic usage to advanced enterprise scenarios.