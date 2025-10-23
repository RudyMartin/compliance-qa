# Tensor Logic Domain Service

Temperature-based reasoning service implementing Pedro Domingos's tensor logic approach for compliance QA.

## Overview

The Tensor Logic service provides **temperature-controlled reasoning** that seamlessly blends symbolic (rule-based) and analogical (embedding-based) inference:

- **T = 0.0**: Pure symbolic reasoning (certifiable, deterministic)
- **0.0 < T < 0.5**: Hybrid reasoning (combines rules + embeddings)
- **T ≥ 0.5**: Analogical reasoning (learns from similar cases)

## Architecture

This service follows the **hexagonal (ports & adapters) architecture**:

```
┌─────────────────────────────────────────┐
│  TensorLogicService (Domain Service)    │
│  ├── Temperature Router                 │
│  ├── Symbolic Reasoning (T=0)           │
│  ├── Hybrid Reasoning (0<T<0.5)         │
│  └── Analogical Reasoning (T≥0.5)       │
└─────────────────────────────────────────┘
           ↓ depends on ↓
┌─────────────────────────────────────────┐
│  Reasoning Ports (Interfaces)           │
│  ├── SymbolicReasoningPort              │
│  ├── EmbeddingReasoningPort             │
│  ├── TrustworthinessPort                │
│  └── HybridReasoningPort                │
└─────────────────────────────────────────┘
           ↑ implemented by ↑
┌─────────────────────────────────────────┐
│  Adapters (Infrastructure Layer)        │
│  ├── ComplianceRulesAdapter (MVS, VST)  │
│  ├── TidyLLMEmbeddingAdapter            │
│  └── CleanlabTLMAdapter                 │
└─────────────────────────────────────────┘
```

## Components

### 1. TensorLogicService
**Main domain service** that orchestrates temperature-based reasoning.

```python
from domain.services.tensor_logic import TensorLogicService
from domain.ports.reasoning_ports import (
    SymbolicReasoningPort,
    EmbeddingReasoningPort
)

# Initialize with adapters (implemented in infrastructure layer)
service = TensorLogicService(
    symbolic_engine=symbolic_adapter,
    embedding_engine=embedding_adapter,
    trustworthiness_scorer=scorer_adapter
)

# Perform inference
result = service.infer(
    query="Is this document MVS 5.4.3 compliant?",
    context={'document': document, 'entity_id': 'ent_123'},
    temperature=0.0,  # Pure symbolic
    compliance_standard='MVS_5.4.3'
)

print(f"Answer: {result.answer}")
print(f"Certifiable: {result.certifiable}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Trustworthiness: {result.trustworthiness_score:.2%}")
```

### 2. TemperatureRouter
**Routes inference requests** based on temperature value.

```python
from domain.services.tensor_logic import TemperatureRouter, ReasoningMode

router = TemperatureRouter()

# Determine reasoning mode
mode = router.route(temperature=0.0)  # -> ReasoningMode.SYMBOLIC
mode = router.route(temperature=0.3)  # -> ReasoningMode.HYBRID
mode = router.route(temperature=0.7)  # -> ReasoningMode.ANALOGICAL

# Get reasoning weights for hybrid mode
weights = router.get_reasoning_weights(0.25)
# -> {'symbolic': 0.75, 'analogical': 0.25}

# Get similarity threshold for embeddings
threshold = router.get_similarity_threshold(0.5)
# -> 0.5 (higher T = lower threshold = more analogies)

# Suggest temperature for use case
temp = router.suggest_temperature('compliance_check')  # -> 0.0
temp = router.suggest_temperature('risk_analysis')     # -> 0.3
temp = router.suggest_temperature('exploratory_research')  # -> 0.7
```

### 3. InferenceResult
**Comprehensive result dataclass** with complete reasoning trace.

```python
from domain.services.tensor_logic import InferenceResult, ReasoningMode

result = InferenceResult(
    answer="COMPLIANT",
    confidence=0.95,
    reasoning_mode=ReasoningMode.HYBRID,
    temperature=0.2,
    provenance=ProvenanceType.HYBRID,
    certifiable=True,
    trustworthiness_score=0.88,
    rules_applied=[...],  # List of RuleEvidence
    similar_entities=[...],  # List of AnalogicalEvidence
    explanation="Document satisfies all MVS 5.4.3 requirements...",
    reasoning_trace={...}  # Full trace for audit
)

# Check reliability
if result.is_reliable(threshold=0.7):
    print("Result is reliable!")

# Get summary
print(result.get_summary())

# Convert to dict for serialization
result_dict = result.to_dict()
```

### 4. Reasoning Ports (Interfaces)
**Port definitions** that adapters must implement.

```python
from domain.ports.reasoning_ports import (
    SymbolicReasoningPort,
    EmbeddingReasoningPort,
    TrustworthinessPort
)

# Adapters implement these interfaces
class MySymbolicAdapter(SymbolicReasoningPort):
    def execute(self, query, context, rules):
        # Implement symbolic reasoning
        return {
            'answer': True,
            'rules_used': ['MVS_5.4.3', 'MVS_5.4.3.1'],
            'violations': [],
            'explanation': 'All rules satisfied'
        }

class MyEmbeddingAdapter(EmbeddingReasoningPort):
    def execute(self, query, context, temperature):
        # Implement embedding-based reasoning
        return {
            'answer': 'COMPLIANT',
            'confidence': 0.85,
            'similar_entities': [...],
            'explanation': 'Similar to 3 compliant entities'
        }
```

## Usage Examples

### Example 1: Compliance Check (T=0.0)
```python
# Certifiable compliance checking using symbolic rules
result = service.infer(
    query="Does this model documentation satisfy MVS 5.4.3?",
    context={'document': model_doc},
    temperature=0.0,  # Pure symbolic - certifiable
    compliance_standard='MVS_5.4.3'
)

assert result.certifiable == True
assert result.reasoning_mode == ReasoningMode.SYMBOLIC
print(f"Rules applied: {len(result.rules_applied)}")
```

### Example 2: Risk Analysis (T=0.3)
```python
# Hybrid reasoning for risk assessment
result = service.infer(
    query="What is the risk level for this entity?",
    context={'entity_id': 'bank_xyz', 'document': risk_report},
    temperature=0.3,  # Hybrid - combines rules + similar cases
    compliance_standard='SR_11-7'
)

assert result.reasoning_mode == ReasoningMode.HYBRID
print(f"Symbolic weight: {result.reasoning_trace['weights']['symbolic']}")
print(f"Similar entities: {len(result.similar_entities)}")
```

### Example 3: Exploratory Research (T=0.7)
```python
# Analogical reasoning for broad research
result = service.infer(
    query="Find entities similar to this financial institution",
    context={'entity_id': 'bank_abc'},
    temperature=0.7  # Analogical - learns from similar cases
)

assert result.reasoning_mode == ReasoningMode.ANALOGICAL
assert result.certifiable == False  # Not certifiable
print(f"Found {len(result.similar_entities)} similar entities")
```

### Example 4: Batch Processing
```python
# Process multiple queries in batch
queries = [
    "Is document A compliant?",
    "Is document B compliant?",
    "Is document C compliant?"
]
contexts = [
    {'document': doc_a},
    {'document': doc_b},
    {'document': doc_c}
]

batch_result = service.batch_infer(
    queries=queries,
    contexts=contexts,
    temperature=0.0,
    compliance_standard='MVS_5.4.3'
)

print(f"Success rate: {batch_result.success_count}/{len(queries)}")
print(f"Average confidence: {batch_result.get_average_confidence():.2%}")
print(f"Certifiable count: {batch_result.get_certifiable_count()}")
```

## Temperature Guidelines

| Use Case | Suggested T | Reasoning Mode | Certifiable |
|----------|-------------|----------------|-------------|
| Regulatory compliance | 0.0 | Symbolic | ✅ Yes |
| Document review | 0.1 | Hybrid (90% rules) | ✅ Yes |
| Risk screening | 0.2 | Hybrid (80% rules) | ⚠️ Maybe |
| Risk analysis | 0.3 | Hybrid (70% rules) | ❌ No |
| Entity classification | 0.4 | Hybrid (60% rules) | ❌ No |
| Similarity search | 0.6 | Analogical | ❌ No |
| Exploratory research | 0.8 | Analogical | ❌ No |

## Integration with Existing Services

The Tensor Logic service integrates seamlessly with existing compliance-qa services:

### With MVS Rules
```python
# Your existing MVS rules become the symbolic layer
from domain.rules.mvs_rules import MVSRules

mvs = MVSRules()
rules = mvs.requirements

# Symbolic adapter uses these rules
result = service.infer(
    query="Check MVS compliance",
    context={'document': doc, 'rules': list(rules.values())},
    temperature=0.0
)
```

### With Model Risk Analysis
```python
from domain.services.model_risk_analysis import ModelRiskAnalyzer

analyzer = ModelRiskAnalyzer()
risk_factors = analyzer.analyze(document)

# Use tensor logic for hybrid risk assessment
result = service.infer(
    query="Assess overall risk level",
    context={
        'document': document,
        'risk_factors': risk_factors
    },
    temperature=0.3  # Hybrid mode
)
```

### With Workflow Service
```python
from domain.services.workflow_service import WorkflowService

workflow = WorkflowService()

# Add tensor logic step to workflow
workflow.add_step('tensor_logic_check', lambda ctx: service.infer(
    query=ctx['query'],
    context=ctx,
    temperature=ctx.get('temperature', 0.1)
))
```

## Next Steps

To complete the integration, implement the adapters:

1. **Symbolic Adapter**: `adapters/secondary/tensor_logic/symbolic_reasoning_adapter.py`
   - Uses your existing MVS/VST/SR compliance rules

2. **Embedding Adapter**: `adapters/secondary/tensor_logic/embedding_reasoning_adapter.py`
   - Uses `packages/tidyllm-sentence/` for embeddings

3. **Trustworthiness Adapter**: `adapters/secondary/tensor_logic/trustworthiness_adapter.py`
   - Uses Cleanlab TLM for scoring

4. **Application Service**: `application/services/tensor_logic_application_service.py`
   - Orchestrates use cases

5. **Chat Portal**: `portals/chat/tensor_logic_chat.py`
   - Streamlit UI with temperature slider

## Testing

```python
# Unit test example
def test_symbolic_reasoning():
    service = TensorLogicService(
        symbolic_engine=mock_symbolic,
        embedding_engine=mock_embedding
    )

    result = service.infer(
        query="Test query",
        context={'test': True},
        temperature=0.0
    )

    assert result.reasoning_mode == ReasoningMode.SYMBOLIC
    assert result.certifiable == True
    assert result.confidence == 1.0
```

## References

- Pedro Domingos: "Every Model Learned by Gradient Descent Is a Tensor Program"
- Cleanlab TLM: https://cleanlab.ai/blog/trustworthy-language-model/
- Hexagonal Architecture: https://alistair.cockburn.us/hexagonal-architecture/

---

**Status**: ✅ Core domain service implemented
**Next**: Implement adapters (Phase 2)
**Version**: 0.1.0
