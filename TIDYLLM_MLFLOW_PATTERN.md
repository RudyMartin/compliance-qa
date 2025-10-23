# TidyLLM MLflow Wrapping Pattern - Analysis

## 🎯 **The Big Picture: How TidyLLM Wraps MLflow**

You have **THREE layers of MLflow wrapping** with different purposes:

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: SAFE WRAPPER (packages/tidyllm/)                   │
│ - Circuit breaker pattern                                   │
│ - NEVER blocks core functionality                           │
│ - Graceful degradation                                      │
│ - Async logging queue                                       │
│ mlflow_safe_wrapper.py                                      │
└──────────────────────────────────────────────────────────────┘
                          ↓ wraps
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: ENHANCED SERVICE (infrastructure/)                 │
│ - Backend isolation (separate PostgreSQL database)          │
│ - Timeout protections                                       │
│ - Multiple backend fallbacks                                │
│ - Self-describing configuration                             │
│ enhanced_mlflow_service.py                                  │
└──────────────────────────────────────────────────────────────┘
                          ↓ wraps
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: INTEGRATION SERVICE (packages/tidyllm/)            │
│ - MLflow Gateway client connection                          │
│ - Unified session management                                │
│ - Health monitoring                                         │
│ - Request/response transformation                           │
│ mlflow_integration_service.py                               │
└──────────────────────────────────────────────────────────────┘
                          ↓ uses
┌──────────────────────────────────────────────────────────────┐
│ MLFLOW (Standard Library)                                   │
│ - MlflowClient                                              │
│ - Tracking API                                              │
│ - Model Registry                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 **Layer 1: Integration Service (packages/tidyllm/)**

**File**: `packages/tidyllm/services/mlflow_integration_service.py`

### **Purpose**
Basic MLflow client management with unified session integration.

### **Key Features**

1. **Unified Session Management**
   ```python
   def _load_config_from_unified_sessions(self):
       """Load MLflow config from unified sessions system."""
       session_manager = get_global_session_manager()
       mlflow_config = session_manager.get_mlflow_config()

       self.config = MLflowConfig(
           gateway_uri=mlflow_config.get('tracking_uri'),
           timeout=30,
           retry_count=3
       )
   ```

2. **Graceful Import**
   ```python
   try:
       import mlflow
       from mlflow.tracking import MlflowClient
       MLFLOW_AVAILABLE = True
   except ImportError:
       MLFLOW_AVAILABLE = False
       logger.info("MLflow not installed - service will operate in offline mode")
   ```

3. **Gateway Registry Integration**
   ```python
   # First try to get session manager from GatewayRegistry (injected)
   from tidyllm.gateways.gateway_registry import get_global_registry
   registry = get_global_registry()
   if hasattr(registry, 'session_manager'):
       session_manager = registry.session_manager
   ```

4. **Health Monitoring**
   ```python
   def health_check(self) -> Dict[str, Any]:
       connection_ok = self._test_connection()
       return {
           "service": "mlflow_integration",
           "healthy": connection_ok,
           "mlflow_available": MLFLOW_AVAILABLE,
           "connected": self.is_connected,
           "gateway_uri": self.config.gateway_uri
       }
   ```

5. **LLM Request Logging** (Simplified)
   ```python
   def log_llm_request(self, model, prompt, response, processing_time, ...):
       """Log LLM request/response for tracking."""
       if not self.is_available():
           return False

       # Basic logging (would need experiment/run management)
       logger.info(f"Logged LLM request: {model} ({processing_time:.1f}ms)")
       return True
   ```

### **Usage Pattern**
```python
from tidyllm.services.mlflow_integration_service import MLflowIntegrationService

service = MLflowIntegrationService()

# Log LLM requests
service.log_llm_request(
    model="gpt-4",
    prompt="Analyze compliance",
    response="Document is compliant",
    processing_time=1234.5
)

# Health check
status = service.health_check()
```

### **Limitations**
- ❌ No timeout protection (can hang)
- ❌ No circuit breaker (repeated failures not handled)
- ❌ No backend isolation (uses default MLflow backend)
- ❌ No async logging (blocks on writes)
- ⚠️ Gateway query functionality commented out (tracking server doesn't support it)

---

## 📋 **Layer 2: Enhanced Service (infrastructure/)**

**File**: `infrastructure/services/enhanced_mlflow_service.py`

### **Purpose**
Production-grade MLflow service with backend isolation and timeout protection.

### **Key Features**

1. **Timeout Protection on Import**
   ```python
   # Set MLflow environment variables early to prevent network timeouts
   os.environ['DISABLE_MLFLOW_TELEMETRY'] = '1'
   os.environ['MLFLOW_TRACKING_TIMEOUT'] = '5'
   os.environ['MLFLOW_HTTP_TIMEOUT'] = '10'

   # Try to import with signal timeout (Unix)
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(10)  # 10 second timeout
   import mlflow
   signal.alarm(0)  # Cancel timeout
   ```

2. **Backend Isolation with Auto-Selection**
   ```python
   @dataclass
   class MLflowBackendConfig:
       primary: str = "postgresql_shared_pool"      # Use shared pool
       alternative: str = "mlflow_alt_db"           # Separate MLflow DB
       fallback: str = "file://./mlflow_data"       # File-based
       test_mode: str = "sqlite:///./test_mlflow.db"
       auto_select: bool = True
   ```

3. **Multiple Backend Fallback**
   ```python
   def _initialize_with_backend_selection(self):
       backends_to_try = [
           ('primary', self.backend_config.primary),
           ('alternative', self.backend_config.alternative),
           ('fallback', self.backend_config.fallback),
           ('test_mode', self.backend_config.test_mode)
       ]

       for backend_name, backend_id in backends_to_try:
           backend_uri = self._resolve_backend_uri(backend_id)
           if self._test_backend_connection(backend_uri):
               self._initialize_client_with_backend(backend_uri)
               logger.info(f"✅ MLflow initialized with {backend_name}")
               break
   ```

4. **Backend Resolution from Credential Carrier**
   ```python
   def _resolve_backend_uri(self, backend_id: str) -> Optional[str]:
       if backend_id == 'postgresql_shared_pool':
           pg_creds = self.credential_carrier.get_credentials_by_name('postgresql_primary')
           return f"postgresql://{username}:{password}@{host}:{port}/{database}"

       elif backend_id == 'mlflow_alt_db':
           alt_creds = self.credential_carrier.get_credentials_by_name('mlflow_alt_db')
           return f"postgresql://{username}:{password}@{host}:{port}/{database}"
   ```

5. **Full MLflow Logging with Experiment Management**
   ```python
   def log_llm_request(self, model, prompt, response, processing_time, ...):
       # Create experiment if needed
       experiment = self.client.get_experiment_by_name(experiment_name)
       if not experiment:
           experiment_id = self.client.create_experiment(experiment_name)

       # Start run and log
       with mlflow.start_run(experiment_id=experiment_id):
           mlflow.log_param("model", model)
           mlflow.log_metric("processing_time_ms", processing_time)
           mlflow.log_metric("input_tokens", token_usage.get("input", 0))
           # ... more logging
   ```

6. **Backend Switching**
   ```python
   def switch_backend(self, backend_id: str) -> bool:
       """Switch to a different backend on the fly."""
       backend_uri = self._resolve_backend_uri(backend_id)
       if self._test_backend_connection(backend_uri):
           self._initialize_client_with_backend(backend_uri)
           return True
   ```

7. **Backend Status Monitoring**
   ```python
   def get_backend_status(self) -> Dict[str, Any]:
       """Get status of all configured backends."""
       status = {}
       for name, backend_id in backends.items():
           backend_uri = self._resolve_backend_uri(backend_id)
           is_available = self._test_backend_connection(backend_uri)
           status[name] = {
               'available': is_available,
               'current': (name == self.current_backend)
           }
       return status
   ```

### **Usage Pattern**
```python
from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service

service = get_enhanced_mlflow_service()

# Check backend status
status = service.get_backend_status()
# {
#   'primary': {'available': True, 'current': True},
#   'alternative': {'available': True, 'current': False},
#   'fallback': {'available': True, 'current': False}
# }

# Switch backends if needed
service.switch_backend('alternative')

# Log with full MLflow support
service.log_llm_request(
    model="gpt-4",
    prompt="Check compliance",
    response="Compliant",
    processing_time=1500,
    token_usage={"input": 100, "output": 50},
    experiment_name="compliance_checks"
)
```

### **Advantages Over Layer 1**
- ✅ Timeout protection on import
- ✅ Backend isolation (separate DB for MLflow)
- ✅ Multiple backend fallbacks
- ✅ Self-describing configuration integration
- ✅ Full experiment management
- ✅ Connection pooling via credential carrier
- ✅ Backend switching capability

### **Limitations**
- ❌ Still blocks on logging (synchronous)
- ❌ No circuit breaker pattern
- ❌ No async queue for high throughput
- ❌ No graceful degradation under load

---

## 📋 **Layer 3: Safe Wrapper (packages/tidyllm/)**

**File**: `packages/tidyllm/infrastructure/reliability/mlflow_safe_wrapper.py`

### **Purpose**
**NEVER BLOCK CORE FUNCTIONALITY** - Circuit breaker pattern with async logging.

### **Design Philosophy**

> "MLflow is OPTIONAL. Core requests must NEVER fail due to MLflow."

### **Key Features**

1. **Circuit Breaker States**
   ```python
   class MLflowState(Enum):
       HEALTHY = "healthy"          # Working normally
       DEGRADED = "degraded"        # Working but slow
       DISABLED = "disabled"        # Too many failures
       UNAVAILABLE = "unavailable"  # Never worked
   ```

2. **Health Tracking**
   ```python
   @dataclass
   class MLflowHealth:
       state: MLflowState = MLflowState.UNAVAILABLE
       consecutive_failures: int = 0
       last_success: Optional[float] = None
       total_requests: int = 0
       total_successes: int = 0
       avg_response_time: float = 0.0
   ```

3. **Async Logging Queue**
   ```python
   def __init__(self, timeout_ms=500, max_failures=3):
       # Async logging queue (1000 entry buffer)
       self._log_queue = queue.Queue(maxsize=1000)
       self._executor = ThreadPoolExecutor(max_workers=1)
       self._logging_enabled = True
   ```

4. **Never-Block Guarantee**
   ```python
   def log_request(self, data: Dict[str, Any]):
       """Log request - NEVER blocks, NEVER throws."""
       try:
           # Quick queue check
           if self.health.state == MLflowState.DISABLED:
               return  # Skip immediately

           # Non-blocking queue put with timeout
           self._log_queue.put_nowait(data)

           # Async background logging
           self._executor.submit(self._process_queue)

       except queue.Full:
           # Queue full - circuit breaker may need to open
           logger.warning("MLflow queue full - may be degraded")

       except Exception as e:
           # Never propagate exceptions
           logger.debug(f"MLflow logging failed: {e}")
   ```

5. **Timeout Protection**
   ```python
   def _process_queue(self):
       """Process logging queue with timeout."""
       while not self._log_queue.empty():
           try:
               data = self._log_queue.get(timeout=0.1)

               # Execute with timeout
               future = self._executor.submit(self._log_to_mlflow, data)
               future.result(timeout=self.timeout_ms / 1000.0)  # 500ms default

               self._record_success()

           except TimeoutError:
               self._record_failure()
               logger.warning("MLflow logging timeout")

           except Exception as e:
               self._record_failure()
               logger.debug(f"MLflow logging error: {e}")
   ```

6. **Circuit Breaker Logic**
   ```python
   def _record_failure(self):
       """Record failure and potentially open circuit breaker."""
       with self._lock:
           self.health.consecutive_failures += 1
           self.health.last_failure = time.time()

           # Open circuit breaker after max_failures
           if self.health.consecutive_failures >= self.max_failures:
               self.health.state = MLflowState.DISABLED
               logger.warning(f"MLflow circuit breaker OPEN - disabled after {self.max_failures} failures")

   def _record_success(self):
       """Record success and reset circuit breaker."""
       with self._lock:
           self.health.consecutive_failures = 0
           self.health.last_success = time.time()
           self.health.total_successes += 1

           if self.health.state == MLflowState.DISABLED:
               self.health.state = MLflowState.HEALTHY
               logger.info("MLflow circuit breaker CLOSED - recovered")
   ```

7. **Auto-Recovery**
   ```python
   def _should_attempt_recovery(self) -> bool:
       """Check if enough time has passed to attempt recovery."""
       if self.health.state != MLflowState.DISABLED:
           return False

       if self.health.last_failure is None:
           return True

       time_since_failure = time.time() - self.health.last_failure
       return time_since_failure >= self.recovery_interval  # 300s default
   ```

8. **Traffic Capture Guarantee**
   ```python
   # When HEALTHY: Captures 100% of traffic (expands queue if needed)
   # When DEGRADED: Best effort capture (may drop some entries)
   # When DISABLED: No capture (circuit breaker open)
   # When UNAVAILABLE: No capture (MLflow not installed)
   ```

### **Usage Pattern**
```python
from tidyllm.infrastructure.reliability.mlflow_safe_wrapper import MLflowSafeWrapper

wrapper = MLflowSafeWrapper(
    timeout_ms=500,        # Max 500ms for logging
    max_failures=3,        # Disable after 3 failures
    recovery_interval=300  # Retry after 5 minutes
)

# Log requests - NEVER blocks, NEVER throws
for i in range(10000):
    wrapper.log_request({
        'model': 'gpt-4',
        'prompt_length': 100,
        'response_length': 500,
        'processing_time': 1234.5
    })
    # Core functionality continues regardless of MLflow state

# Check health
health = wrapper.health
print(f"State: {health.state}")
print(f"Success rate: {health.total_successes / health.total_requests}")
```

### **Advantages Over Layers 1 & 2**
- ✅ **NEVER blocks** - async queue processing
- ✅ **Circuit breaker** - auto-disable on failures
- ✅ **Auto-recovery** - retries after interval
- ✅ **Timeout protection** - max 500ms per log
- ✅ **Graceful degradation** - queue management
- ✅ **Zero impact** on core functionality
- ✅ **100% traffic capture** when healthy
- ✅ **Health metrics** for monitoring

---

## 🔄 **How They Work Together**

### **Typical Usage in Compliance-QA**

```python
# Option 1: Use Enhanced Service (Layer 2) directly
from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service

mlflow_service = get_enhanced_mlflow_service()

# Full-featured logging with backend isolation
mlflow_service.log_llm_request(
    model="gpt-4",
    prompt="Check compliance",
    response="Compliant",
    processing_time=1500,
    experiment_name="compliance_checks"
)

# Option 2: Wrap Enhanced Service with Safe Wrapper (Layer 3)
from tidyllm.infrastructure.reliability.mlflow_safe_wrapper import MLflowSafeWrapper

safe_wrapper = MLflowSafeWrapper()

# Never blocks, never fails
safe_wrapper.log_request({
    'model': 'gpt-4',
    'processing_time': 1500
})

# Option 3: Use Integration Service (Layer 1) in TidyLLM packages
from tidyllm.services.mlflow_integration_service import MLflowIntegrationService

integration_service = MLflowIntegrationService()

# Basic logging with unified session management
integration_service.log_llm_request(
    model="gpt-4",
    prompt="Query",
    response="Answer",
    processing_time=1000
)
```

### **Layering Strategy**

```
Application Code (Compliance-QA)
        ↓
Layer 3: MLflowSafeWrapper (if high-throughput critical path)
        ↓
Layer 2: EnhancedMLflowService (backend isolation, experiment mgmt)
        ↓
Layer 1: MLflowIntegrationService (basic client, session mgmt)
        ↓
MLflow Library
```

---

## 🎨 **Which Layer to Use When?**

### **Use Layer 1 (Integration Service)** when:
- ✅ Working inside TidyLLM packages
- ✅ Need unified session management
- ✅ Simple use cases
- ✅ Low throughput
- ❌ NOT for critical path code

### **Use Layer 2 (Enhanced Service)** when:
- ✅ Production compliance-qa application
- ✅ Need backend isolation (separate MLflow DB)
- ✅ Multiple backend fallbacks required
- ✅ Full experiment management needed
- ✅ Medium throughput (< 100 req/sec)
- ❌ NOT for ultra high-throughput

### **Use Layer 3 (Safe Wrapper)** when:
- ✅ **Critical path code** (must never block)
- ✅ High throughput (1000+ req/sec)
- ✅ MLflow failures can't impact service
- ✅ Need circuit breaker protection
- ✅ Async logging required
- ⚠️ Less features (no experiments, basic logging)

---

## 🚀 **Applying This to Tensor Logic MLflow Packaging**

### **Key Insight:**
Your **existing MLflow infrastructure** already has sophisticated wrapping!

### **What This Means for Tensor Logic:**

```python
# Option A: Use Existing Enhanced Service (Recommended)
from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service

class TensorLogicMLflowModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.service = create_tensor_logic_service(mode='tidyllm')
        self.mlflow_service = get_enhanced_mlflow_service()  # Use existing!

    def predict(self, context, model_input):
        result = self.service.infer(...)

        # Log metrics using existing infrastructure
        self.mlflow_service.log_llm_request(
            model="TensorLogic",
            prompt=model_input['query'],
            response=result.answer,
            processing_time=result.processing_time_ms,
            experiment_name="tensor_logic_inference"
        )

        return result

# Option B: Wrap with Safe Wrapper for Critical Path
from tidyllm.infrastructure.reliability.mlflow_safe_wrapper import MLflowSafeWrapper

class TensorLogicMLflowModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.service = create_tensor_logic_service(mode='tidyllm')
        self.safe_wrapper = MLflowSafeWrapper()  # Never blocks!

    def predict(self, context, model_input):
        result = self.service.infer(...)

        # Async logging - never blocks prediction
        self.safe_wrapper.log_request({
            'model': 'TensorLogic',
            'temperature': model_input.get('temperature', 0.0),
            'confidence': result.confidence,
            'trustworthiness': result.trustworthiness_score,
            'yrsn_quality': result.components.get('yrsn_quality'),
            'reasoning_mode': result.reasoning_mode.value,
            'certifiable': result.certifiable
        })

        return result
```

### **Recommendation:**

**Use Layer 2 (EnhancedMLflowService)** for Tensor Logic packaging because:

1. ✅ Already integrated with compliance-qa infrastructure
2. ✅ Backend isolation (won't overwhelm shared PostgreSQL)
3. ✅ Multiple fallbacks (file-based if DB fails)
4. ✅ Full experiment management (track temperature sweeps)
5. ✅ Credential carrier integration (proper AWS S3 access)
6. ✅ Self-describing configuration (yaml-driven)

### **Architecture:**

```
Tensor Logic Inference
        ↓
TensorLogicMLflowModel (PyFunc wrapper)
        ↓
EnhancedMLflowService (backend isolation, experiments)
        ↓
MLflow Tracking
        ↓
├── PostgreSQL (alternative DB - isolated from main pool)
└── S3 Artifacts (models, logs, results)
```

---

## 📝 **Updated Packaging Plan**

Given the existing MLflow infrastructure, the packaging should:

1. **Leverage Enhanced MLflow Service** (already exists!)
   - Don't reinvent the wheel
   - Use existing backend isolation
   - Use existing credential management

2. **Create Simple PyFunc Wrapper**
   ```python
   # compliance_qa/mlflow/tensor_logic_model.py

   from infrastructure.services.enhanced_mlflow_service import get_enhanced_mlflow_service
   from infrastructure.factories.tensor_logic_factory import create_tensor_logic_service

   class TensorLogicModel(mlflow.pyfunc.PythonModel):
       def __init__(self, temperature=0.0):
           self.temperature = temperature
           self.service = None
           self.mlflow_service = None

       def load_context(self, context):
           # Create Tensor Logic service
           self.service = create_tensor_logic_service(mode='tidyllm')

           # Use EXISTING MLflow infrastructure
           self.mlflow_service = get_enhanced_mlflow_service()

       def predict(self, context, model_input):
           result = self.service.infer(
               query=model_input['query'],
               context=model_input.get('context'),
               temperature=model_input.get('temperature', self.temperature)
           )

           # Log to existing MLflow backend
           self.mlflow_service.log_llm_request(
               model="TensorLogic",
               prompt=model_input['query'],
               response=str(result.answer),
               processing_time=getattr(result, 'processing_time_ms', 0),
               experiment_name="tensor_logic",
               confidence=result.confidence,
               trustworthiness=result.trustworthiness_score,
               yrsn_validation=getattr(result, 'yrsn_validation', 'UNKNOWN'),
               reasoning_mode=result.reasoning_mode.value,
               certifiable=result.certifiable,
               temperature=result.temperature
           )

           return {
               'answer': result.answer,
               'confidence': result.confidence,
               'trustworthiness_score': result.trustworthiness_score,
               'reasoning_mode': result.reasoning_mode.value,
               'certifiable': result.certifiable,
               'components': result.components
           }
   ```

3. **Simpler setup.py** - Less complexity needed
   - Enhanced MLflow Service handles backends
   - Credential carrier handles AWS/PostgreSQL
   - Just need to make compliance_qa importable

---

## 🎯 **Key Takeaways**

1. **You already have production-grade MLflow infrastructure!**
   - 3 layers of wrapping for different needs
   - Backend isolation
   - Circuit breakers
   - Async logging

2. **Tensor Logic should USE existing infrastructure**
   - Don't create new MLflow wrappers
   - Leverage EnhancedMLflowService
   - Simpler packaging needed

3. **Packaging focus shifts to:**
   - ✅ Make compliance_qa installable (`pip install -e .`)
   - ✅ Handle packages/ subdirectories (tlm, tidyllm, tidyllm-sentence)
   - ✅ Create simple PyFunc wrapper using EXISTING mlflow service
   - ✅ Document how to use existing MLflow backends

4. **No need to reinvent MLflow logging** - it's already solved! 🎉

---

**This changes the packaging plan significantly - want me to revise the implementation plan based on this understanding?**
