# Safety Wrapper Pattern Documentation

## What is a Safety Wrapper?

A **safety wrapper** is a protective design pattern that wraps potentially dangerous, slow, or unreliable operations to prevent system failures, hangs, or poor user experience.

Think of it as:
- **Circuit breaker** for code
- **Safety harness** for dangerous operations
- **Timeout guard** for network calls
- **Fallback provider** when things go wrong

## The Problem It Solves

### Real-World Scenario: Corporate Networks
In corporate environments with strict firewalls and proxies:

```python
# THIS CAN HANG FOR 5+ MINUTES:
import boto3
s3 = boto3.client('s3')
buckets = s3.list_buckets()  # 🔴 HANGS in corporate network!
```

**Why it hangs:**
- Corporate proxy blocks AWS endpoints
- No timeout configured
- Connection attempts retry forever
- Application freezes, user frustrated

## The Safety Wrapper Solution

### Pattern Structure
```python
class SafetyWrapper:
    def __init__(self):
        self.timeout = 15  # seconds
        self.mode = self.detect_environment()

    def dangerous_operation(self):
        if self.mode == 'safe':
            # Skip dangerous call entirely
            return self.mock_response()
        else:
            # Try with timeout protection
            return self.try_with_timeout()
```

## Implementation in Your Codebase

### 1. CorporateSafeUSM Wrapper
**Location**: `packages/tidyllm/utils/corporate/usm_wrapper.py`

```python
class CorporateSafeUSM:
    """Wraps UnifiedSessionManager to prevent corporate network hangs"""

    def initialize_safely(self):
        # Step 1: Detect if we're in corporate environment
        if self.is_corporate_environment():
            # Step 2: Skip dangerous AWS calls
            return self.initialize_fallback_usm()
        else:
            # Step 3: Safe to make real calls
            return self.initialize_standard_usm()
```

### 2. AWS Validator with Safety Mode
**Location**: `packages/tidyllm/validators/aws.py`

```python
class AWSValidator(BaseValidator):
    def validate_aws_connectivity(self):
        # Detect corporate environment first
        env_info = self.detect_corporate_environment()

        if self.corporate_mode:
            return self._validate_corporate_mode()  # SAFE: No hanging calls
        else:
            return self._validate_standard_mode()   # NORMAL: With timeouts

    def _validate_corporate_mode(self):
        """Corporate mode - creates clients but doesn't call them"""
        # SAFE: Just create client (fast)
        boto3.client('s3')

        # UNSAFE: Never do this in corporate mode!
        # client.list_buckets()  ❌ Would hang!

        return {'status': 'corporate_safe', 'message': 'Skipped hanging calls'}
```

## Where It's Used in Your Codebase

### 11 Files Using Safety Patterns:

1. **Validators** (7 files) - All inherit from `BaseValidator` with corporate safety:
   - `aws.py` - Validates AWS without hanging
   - `database.py` - Validates PostgreSQL safely
   - `gateway.py` - Validates LLM gateway safely
   - `mlflow.py` - Validates MLflow safely
   - `workflow.py` - Validates workflows safely
   - `base.py` - Base class with corporate detection
   - `detector.py` - Corporate environment detection

2. **Utilities** (2 files):
   - `usm_wrapper.py` - Main USM safety wrapper
   - `validator.py` - Corporate safety validator

3. **Services** (1 file):
   - `document_processors.py` - Safe document processing

4. **Portals** (1 file):
   - `dspy_configurator.py` - Safe DSPy configuration

## Real Examples of Usage

### Example 1: S3 Operations
```python
# UNSAFE - Can hang in corporate:
s3 = boto3.client('s3')
buckets = s3.list_buckets()  # ❌ Hangs!

# SAFE - Using validator with safety wrapper:
validator = AWSValidator()
result = validator.validate_aws_connectivity()
# Returns: {'s3': {'status': 'corporate_safe', 'message': 'Skipped to prevent hanging'}}
```

### Example 2: Bedrock Model Listing
```python
# UNSAFE - Can hang:
bedrock = boto3.client('bedrock')
models = bedrock.list_foundation_models()  # ❌ Hangs!

# SAFE - Using safety pattern:
if validator.corporate_mode:
    models = []  # Return empty list instead of hanging
else:
    models = bedrock.list_foundation_models()  # Safe to call
```

### Example 3: Database Connection
```python
# UNSAFE - Can hang on connect:
psycopg2.connect(host='internal-db', timeout=None)  # ❌ No timeout!

# SAFE - Using DatabaseValidator:
validator = DatabaseValidator()
result = validator.validate_postgres()
# Automatically uses timeout and fallback in corporate mode
```

## Key Safety Techniques

### 1. Environment Detection
```python
def detect_corporate_environment(self):
    indicators = {
        'proxy': os.environ.get('HTTP_PROXY'),
        'vpn': self.check_vpn_active(),
        'domain': 'CORP' in socket.getfqdn(),
        'aws_timeout': self.test_aws_with_timeout(1.0)
    }
    return 'corporate' if any(indicators.values()) else 'standard'
```

### 2. Timeout Protection
```python
def with_timeout(func, timeout_seconds=15):
    """Execute function with timeout"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("Operation timed out")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        result = func()
    finally:
        signal.alarm(0)  # Cancel alarm
    return result
```

### 3. Fallback Responses
```python
def corporate_safe_result(self, service, reason):
    """Return safe fallback result"""
    return {
        'status': 'corporate_safe',
        'service': service,
        'available': 'unknown',
        'message': reason,
        'client_creation': 'success',  # We can create, just not call
        'latency': 0
    }
```

## Benefits of Safety Wrappers

1. **Prevents Application Freezing**
   - No more 5-minute hangs
   - Responsive UI even in restricted networks

2. **Graceful Degradation**
   - App works with limited features vs not at all
   - Users get feedback instead of frozen screen

3. **Better User Experience**
   - Clear messages about why things are skipped
   - Fast fallbacks instead of timeouts

4. **Easier Debugging**
   - Logs show "corporate_mode" vs mysterious hangs
   - Clear indication of what was skipped and why

## When to Use Safety Wrappers

Use a safety wrapper when:
- ✅ Making network calls that might hang
- ✅ Accessing resources that might not exist
- ✅ Operating in restricted environments (corporate, cloud)
- ✅ Dealing with unreliable external services
- ✅ Needing fallback behavior for failures

Don't use when:
- ❌ Operations are always fast and reliable
- ❌ Failures should crash the program
- ❌ You need the real result (no fallback acceptable)

## Safety Wrapper vs Other Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Safety Wrapper** | Prevent hangs/failures | Skip S3 calls in corporate |
| **Delegate** | Layer separation | Access S3 without importing infrastructure |
| **Adapter** | Interface conversion | Convert port to implementation |
| **Proxy** | Control access | Add logging to all S3 calls |
| **Circuit Breaker** | Prevent cascading failures | Stop calling failed service |

## Conclusion

Safety wrappers are essential for robust applications that must work in various environments. In your codebase, they prevent AWS operations from hanging in corporate networks, ensuring the application remains responsive even when external services are blocked or slow.

The pattern is used extensively in validators (11 files) to ensure all service validations complete quickly with appropriate fallbacks, making the system resilient to network restrictions.