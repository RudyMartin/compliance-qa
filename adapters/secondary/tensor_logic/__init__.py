"""
Tensor Logic Adapters
======================
Secondary adapters implementing tensor logic reasoning ports.

These adapters provide concrete implementations of the reasoning
interfaces defined in domain/ports/reasoning_ports.py.

Available Adapters:
-------------------

1. **ComplianceRulesAdapter** - Symbolic reasoning using MVS/VST/SR rules
   - Implements: SymbolicReasoningPort
   - Uses: domain/rules/mvs_rules.py
   - Certifiable: Yes (T=0.0)

2. **TidyLLMEmbeddingAdapter** - Embedding-based analogical reasoning
   - Implements: EmbeddingReasoningPort
   - Uses: packages/tidyllm-sentence/ (LSA, TF-IDF, etc.)
   - Certifiable: No (T>0.0)

3. **TidyLLMTrustworthinessAdapter** - YRSN-based trustworthiness scoring
   - Implements: TrustworthinessPort
   - Uses: YOUR tlm + tidyllm-sentence packages (NO external APIs)
   - Framework: YRSN (Yes/Relevant/Specific/No-fluff)

4. **MockTrustworthinessAdapter** - Mock trustworthiness for testing
   - Implements: TrustworthinessPort
   - Uses: Simple heuristics (no external dependencies)

5. **SmartHybridAdapter** - Hybrid reasoning
   - Implements: HybridReasoningPort
   - Combines: Symbolic + Embedding engines

Usage Example:
--------------

```python
from adapters.secondary.tensor_logic import (
    ComplianceRulesAdapter,
    TidyLLMEmbeddingAdapter,
    TidyLLMTrustworthinessAdapter
)
from domain.services.tensor_logic import TensorLogicService

# Initialize adapters (all using YOUR packages - NO external APIs!)
symbolic_adapter = ComplianceRulesAdapter()
embedding_adapter = TidyLLMEmbeddingAdapter(embedding_method='lsa')
scorer_adapter = TidyLLMTrustworthinessAdapter()  # YRSN framework

# Create service with adapters
service = TensorLogicService(
    symbolic_engine=symbolic_adapter,
    embedding_engine=embedding_adapter,
    trustworthiness_scorer=scorer_adapter
)

# Perform inference
result = service.infer(
    query="Is this document MVS compliant?",
    context={'document': document_data},
    temperature=0.0
)
```

Integration Notes:
------------------

### With Existing MVS Rules
The ComplianceRulesAdapter wraps your existing MVS rules:

```python
from domain.rules.mvs_rules import MVSRules

adapter = ComplianceRulesAdapter()
# Uses MVSRules internally for symbolic reasoning
```

### With tidyllm-sentence Package
The TidyLLMEmbeddingAdapter uses YOUR embedding package:

```python
adapter = TidyLLMEmbeddingAdapter(
    embedding_method='lsa',  # or 'tfidf', 'transformer'
    min_similarity=0.3
)

# Add entities with outcomes
adapter.add_entity(
    entity_id='entity_123',
    entity_data={'name': 'Example Corp', 'industry': 'Finance'},
    outcome='compliant'
)
```

### With TidyLLM Trustworthiness (YRSN Framework)
The TidyLLMTrustworthinessAdapter uses YOUR packages (NO external APIs):

```python
from adapters.secondary.tensor_logic import TidyLLMTrustworthinessAdapter

# Initialize (uses YOUR tlm + tidyllm-sentence)
adapter = TidyLLMTrustworthinessAdapter()

# Score trustworthiness using YRSN framework
result = adapter.score(
    query="Is document compliant?",
    response="Yes, the document is compliant with all required standards."
)
print(result['score'])  # 0.0-1.0
print(result['reliable'])  # True/False
print(result['yrsn_validation'])  # PASS/FAIL
print(result['explanation'])  # Detailed YRSN breakdown
```

### Mock Adapters for Testing
Use mock adapters when external dependencies unavailable:

```python
from adapters.secondary.tensor_logic import MockTrustworthinessAdapter

# Always returns fixed score (good for testing)
mock_adapter = MockTrustworthinessAdapter(default_score=0.8)
```

Architecture:
-------------

```
Domain Layer (Interfaces)
    ↓
domain/ports/reasoning_ports.py
    - SymbolicReasoningPort
    - EmbeddingReasoningPort
    - TrustworthinessPort
    - HybridReasoningPort
    ↑ implemented by
Adapter Layer (Implementations)
    ↓
adapters/secondary/tensor_logic/
    - ComplianceRulesAdapter (→ MVS rules)
    - TidyLLMEmbeddingAdapter (→ tidyllm-sentence)
    - TidyLLMTrustworthinessAdapter (→ YRSN + YOUR tlm/tidyllm-sentence)
    - SmartHybridAdapter (→ combines above)
```

Dependencies (All YOUR packages - NO external APIs!):
------------------------------------------------------
- **Required**: domain/rules/mvs_rules.py (for symbolic)
- **Required**: packages/tidyllm-sentence/ (for embedding)
- **Required**: packages/tlm/ (for ML-based scoring)
- **Reference**: code_samples/yrsn/ (YRSN patterns)
"""

from .symbolic_reasoning_adapter import ComplianceRulesAdapter
from .embedding_reasoning_adapter import TidyLLMEmbeddingAdapter
from .tidyllm_trustworthiness_adapter import TidyLLMTrustworthinessAdapter
from .trustworthiness_adapter import MockTrustworthinessAdapter
from .hybrid_reasoning_adapter import SmartHybridAdapter

__all__ = [
    # Symbolic reasoning
    'ComplianceRulesAdapter',

    # Embedding reasoning
    'TidyLLMEmbeddingAdapter',

    # Trustworthiness scoring (YRSN-based, NO external APIs)
    'TidyLLMTrustworthinessAdapter',
    'MockTrustworthinessAdapter',

    # Hybrid reasoning
    'SmartHybridAdapter',
]

__version__ = '0.1.0'
