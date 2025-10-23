# Tensor Logic: Ecosystem Distribution Strategy

## 🎯 Core Question

**Where should each component of Tensor Logic live within the TidyLLM ecosystem?**

Given the existing packages:
1. **tlm** - Pure Python ML primitives (numpy replacement)
2. **tidyllm-sentence** - Educational sentence embeddings
3. **tidyllm** - Core business logic, gateways, workflows, infrastructure

---

## 📦 Current TidyLLM Ecosystem Overview

### **Package 1: `tlm` (Math Primitives)**
**Repository:** https://github.com/RudyMartin/tlm
**Purpose:** Pure Python ML algorithms, zero dependencies
**Philosophy:** Simplicity as strategy, ML infrastructure sovereignty

**Current Capabilities:**
```python
import tlm

# Linear algebra
matrix = tlm.array([[1,2],[3,4]])
result = tlm.dot(matrix, vector)
normalized = tlm.l2_normalize(embeddings)

# ML algorithms
w, b, history = tlm.logreg_fit(X, y)
predictions = tlm.logreg_predict(X, w, b)
centers, labels, inertia = tlm.kmeans_fit(X, k=3)
```

**Key Design:**
- List-based operations (no numpy)
- Functional API (`module_operation`)
- Zero vendor lock-in
- Complete transparency

---

### **Package 2: `tidyllm-sentence` (Text Embeddings)**
**Repository:** https://github.com/RudyMartin/tidyllm-sentence
**Purpose:** Educational sentence embeddings with complete transparency

**Current Capabilities:**
```python
import tidyllm_sentence as tls

# Embedding methods
embeddings, model = tls.tfidf_fit_transform(sentences)
embeddings, model = tls.lsa_fit_transform(sentences, n_components=50)
embeddings, model = tls.word_avg_fit_transform(sentences, embedding_dim=100)

# Utilities
similarity = tls.cosine_similarity(emb1, emb2)
results = tls.semantic_search(query_emb, corpus_embs, top_k=5)
tokens = tls.word_tokenize("Hello, world!")
```

**Key Design:**
- Pure Python (depends on `tlm`)
- 177x less memory than sentence-transformers
- 77.9% of industrial quality
- Zero external ML dependencies

---

### **Package 3: `tidyllm` (Business Logic & Infrastructure)**
**Repository:** https://github.com/RudyMartin/TidyLLM
**Purpose:** Core business logic, LLM gateways, workflows, infrastructure

**Current Modules:**
```
tidyllm/
├── infrastructure/      # Sessions, delegates, reliability
├── services/           # Business services
├── gateways/           # LLM gateways (OpenAI, Claude, etc.)
├── knowledge_systems/  # RAG, knowledge graphs
├── flow/               # Workflow orchestration
├── validators/         # Data validation
├── utils/              # Utilities
├── domain/             # Domain models
├── interfaces/         # API interfaces
├── presentation/       # UI/presentation layer
├── workflows/          # Business workflows
├── rag2dag/            # RAG to DAG conversion
└── web/                # Web interfaces
```

**Key Design:**
- Clean architecture
- Hexagonal/ports & adapters
- Session management
- MLflow integration
- LLM gateway abstraction

---

## 🧠 Tensor Logic Component Breakdown

### **Tensor Logic = Temperature-Controlled Reasoning Framework**

**Core Components:**
1. **Mathematical Primitives** (similarity, scoring, vector ops)
2. **Embedding Operations** (semantic similarity, LSA-based reasoning)
3. **Symbolic Reasoning** (rules, logic, pattern matching)
4. **YRSN Scoring** (trustworthiness, quality validation)
5. **Temperature Routing** (T=0.0 → symbolic, T≥0.5 → analogical)
6. **Inference Service** (orchestration, result composition)
7. **Ports & Adapters** (interfaces, implementations)

---

## 🎯 Distribution Strategy

### **Option 1: Distributed Across Ecosystem (Recommended)**

**Distribute components to their natural homes:**

#### **1. Math Primitives → `tlm`**
**What goes here:**
- Cosine similarity
- Vector normalization
- Softmax/temperature scaling
- Matrix operations for similarity scoring

**Why:**
- These are foundational ML operations
- Already has `cosine_similarity`-like functions
- Pure Python, list-based
- No dependencies

**Example Addition to `tlm`:**
```python
# tlm/core/similarity.py
def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    dot_prod = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = (sum(x**2 for x in vec1)) ** 0.5
    mag2 = (sum(x**2 for x in vec2)) ** 0.5
    return dot_prod / (mag1 * mag2) if mag1 * mag2 > 0 else 0.0

def temperature_scaled_softmax(logits, temperature=1.0):
    """Softmax with temperature scaling.

    T=0.0 → argmax (deterministic)
    T=1.0 → standard softmax
    T>1.0 → more uniform (exploration)
    """
    if temperature <= 1e-8:
        # Deterministic: return one-hot of argmax
        max_idx = logits.index(max(logits))
        return [1.0 if i == max_idx else 0.0 for i in range(len(logits))]

    # Standard softmax with temperature
    scaled = [x / temperature for x in logits]
    exp_vals = [exp(x) for x in scaled]
    total = sum(exp_vals)
    return [e / total for e in exp_vals]
```

**API in `tlm/__init__.py`:**
```python
# Add to tlm/__init__.py
from .core.similarity import (
    cosine_similarity,
    temperature_scaled_softmax,
    pairwise_cosine,
    top_k_similar
)
```

---

#### **2. Embedding-Based Reasoning → `tidyllm-sentence`**
**What goes here:**
- Semantic similarity search
- LSA-based analogical reasoning
- Case-based reasoning via embeddings
- Sentence-level comparison utilities

**Why:**
- Already has embeddings infrastructure
- Has `semantic_search()`
- Natural extension of embedding capabilities
- Pure Python, depends on `tlm`

**Example Addition to `tidyllm-sentence`:**
```python
# tidyllm_sentence/reasoning.py
def analogical_reasoning(query, cases, embeddings, top_k=5, temperature=1.0):
    """Find similar cases via semantic similarity with temperature control.

    Args:
        query: Query text
        cases: List of case texts
        embeddings: Pre-computed case embeddings
        top_k: Number of similar cases to return
        temperature: Controls diversity (T=0 → exact match, T>0 → exploration)

    Returns:
        List of (case_idx, similarity_score, case_text) tuples
    """
    # Embed query
    query_emb, _ = tfidf_fit_transform([query])

    # Find similar cases
    results = semantic_search(query_emb[0], embeddings, top_k=top_k)

    # Apply temperature scaling to scores
    if temperature > 0:
        scores = [score for idx, score in results]
        # Softmax over scores (higher temp = more exploration)
        import tlm
        scaled_scores = tlm.temperature_scaled_softmax(scores, temperature)
        results = [(idx, scaled_scores[i], cases[idx])
                   for i, (idx, _) in enumerate(results)]
    else:
        # T=0: Return only exact matches (similarity = 1.0)
        results = [(idx, score, cases[idx])
                   for idx, score in results if score > 0.999]

    return results

def case_retrieval(query, case_base, method='lsa', n_components=50):
    """Retrieve relevant cases from case base.

    Returns: List of (case, similarity) tuples sorted by relevance
    """
    if method == 'lsa':
        embeddings, model = lsa_fit_transform(case_base, n_components)
        query_emb = lsa_transform([query], model)
    elif method == 'tfidf':
        embeddings, model = tfidf_fit_transform(case_base)
        query_emb = tfidf_transform([query], model)

    # Find most similar cases
    results = semantic_search(query_emb[0], embeddings, top_k=len(case_base))
    return [(case_base[idx], score) for idx, score in results]
```

**API in `tidyllm_sentence/__init__.py`:**
```python
# Add to tidyllm_sentence/__init__.py
from .reasoning import (
    analogical_reasoning,
    case_retrieval,
    similarity_based_inference
)
```

---

#### **3. Symbolic Reasoning, YRSN, Temperature Routing → `tidyllm`**
**What goes here:**
- Symbolic reasoning engine (rules, pattern matching)
- YRSN trustworthiness scoring
- Temperature routing logic
- `TensorLogicService` orchestration
- Ports & adapters for reasoning
- Integration with LLM gateways

**Why:**
- `tidyllm` is for business logic and infrastructure
- Already has services, gateways, workflows
- Needs orchestration capabilities
- Can depend on both `tlm` and `tidyllm-sentence`

**Example Addition to `tidyllm`:**
```python
# tidyllm/reasoning/
├── __init__.py
├── symbolic/
│   ├── __init__.py
│   ├── engine.py          # Symbolic reasoning engine
│   ├── rules.py           # Rule definitions
│   └── matcher.py         # Pattern matching
├── analogical/
│   ├── __init__.py
│   └── engine.py          # Analogical reasoning (uses tidyllm-sentence)
├── yrsn/
│   ├── __init__.py
│   ├── quality.py         # YRSN quality scoring
│   ├── evidence.py        # Evidence validation
│   └── consistency.py     # Consistency analysis
├── temperature/
│   ├── __init__.py
│   ├── router.py          # Temperature-based routing
│   └── scheduler.py       # Temperature scheduling
└── service.py             # TensorLogicService orchestration
```

**TensorLogicService in `tidyllm/reasoning/service.py`:**
```python
import tlm
import tidyllm_sentence as tls
from .symbolic.engine import SymbolicReasoner
from .analogical.engine import AnalogicalReasoner
from .yrsn.quality import YRSNScorer
from .temperature.router import TemperatureRouter

class TensorLogicService:
    """Temperature-controlled reasoning service.

    Orchestrates symbolic and analogical reasoning based on temperature:
    - T=0.0: Pure symbolic (certifiable)
    - T=0.1-0.4: Hybrid (symbolic + analogical)
    - T≥0.5: Pure analogical (case-based)
    """

    def __init__(self, rules=None, case_base=None, embedding_method='lsa'):
        self.symbolic = SymbolicReasoner(rules)
        self.analogical = AnalogicalReasoner(case_base, method=embedding_method)
        self.yrsn = YRSNScorer()
        self.router = TemperatureRouter()

    def infer(self, query, context=None, temperature=0.0, score_trustworthiness=True):
        """Run inference with temperature-controlled reasoning."""

        # Route based on temperature
        mode = self.router.get_mode(temperature)

        if mode == 'symbolic':
            result = self.symbolic.infer(query, context)
            certifiable = True
        elif mode == 'analogical':
            result = self.analogical.infer(query, context, temperature)
            certifiable = False
        else:  # hybrid
            sym_result = self.symbolic.infer(query, context)
            ana_result = self.analogical.infer(query, context, temperature)
            result = self._merge_results(sym_result, ana_result, temperature)
            certifiable = False

        # Score trustworthiness
        if score_trustworthiness:
            trust_score = self.yrsn.score(query, result['answer'])
        else:
            trust_score = None

        return {
            'answer': result['answer'],
            'confidence': result['confidence'],
            'reasoning_mode': mode,
            'certifiable': certifiable,
            'trustworthiness': trust_score,
            'evidence': result.get('evidence', [])
        }
```

---

### **Option 2: New Package `tidyllm-tensor` (Alternative)**

**Create standalone package that depends on ecosystem:**

```python
# tidyllm-tensor depends on:
# - tlm (math primitives)
# - tidyllm-sentence (embeddings)
# - tidyllm (optional, for integration)

import tlm
import tidyllm_sentence as tls
from tidyllm_tensor import TensorLogicService

service = TensorLogicService()
result = service.infer(query, context, temperature=0.0)
```

**Pros:**
- ✅ Clean separation
- ✅ Can be installed independently
- ✅ Easy to version/release separately
- ✅ Clear ownership

**Cons:**
- ❌ Another package to maintain
- ❌ Adds dependency management complexity
- ❌ Harder to discover (users need to know about it)
- ❌ Duplicates infrastructure already in `tidyllm`

---

## 🏆 Recommendation: Distributed Approach (Option 1)

### **Why Distribute Across Ecosystem:**

1. **Natural Fit**
   - Math primitives belong in `tlm`
   - Embedding reasoning belongs in `tidyllm-sentence`
   - Business logic belongs in `tidyllm`

2. **Discoverability**
   - Users of `tlm` automatically get similarity functions
   - Users of `tidyllm-sentence` automatically get reasoning capabilities
   - Users of `tidyllm` get complete orchestration

3. **Maintenance**
   - Each package maintains what it does best
   - No additional package to version/release
   - Leverages existing infrastructure

4. **Philosophy Alignment**
   - **`tlm`**: Pure primitives, no dependencies
   - **`tidyllm-sentence`**: Text understanding, depends on `tlm`
   - **`tidyllm`**: Orchestration, depends on both

---

## 📋 Implementation Plan

### **Phase 1: Enhance `tlm` with Similarity/Temperature Functions**

#### **Files to Add:**
```
tlm/core/similarity.py      # Cosine similarity, pairwise operations
tlm/core/temperature.py     # Temperature-scaled softmax
```

#### **Changes:**
```python
# tlm/__init__.py
from .core.similarity import (
    cosine_similarity,
    pairwise_cosine,
    top_k_similar
)
from .core.temperature import (
    temperature_scaled_softmax,
    temperature_argmax
)
```

#### **Tests:**
```
tlm/tests/test_similarity.py
tlm/tests/test_temperature.py
```

---

### **Phase 2: Enhance `tidyllm-sentence` with Reasoning Functions**

#### **Files to Add:**
```
tidyllm_sentence/reasoning.py     # Analogical reasoning, case retrieval
tidyllm_sentence/similarity.py    # Advanced similarity operations
```

#### **Changes:**
```python
# tidyllm_sentence/__init__.py
from .reasoning import (
    analogical_reasoning,
    case_retrieval,
    similarity_based_inference
)
```

#### **Tests:**
```
tidyllm_sentence/tests/test_reasoning.py
```

---

### **Phase 3: Add Tensor Logic to `tidyllm`**

#### **Directory Structure:**
```
tidyllm/reasoning/
├── __init__.py
├── symbolic/
│   ├── __init__.py
│   ├── engine.py          # SymbolicReasoner
│   ├── rules.py           # Rule definitions
│   └── patterns.py        # Pattern matching
├── analogical/
│   ├── __init__.py
│   └── engine.py          # AnalogicalReasoner (uses tidyllm-sentence)
├── yrsn/
│   ├── __init__.py
│   ├── quality.py         # YRSN quality scoring
│   ├── evidence.py        # Evidence validation
│   └── consistency.py     # Consistency analysis
├── temperature/
│   ├── __init__.py
│   ├── router.py          # TemperatureRouter
│   └── modes.py           # ReasoningMode enum
├── service.py             # TensorLogicService
└── factory.py             # Convenience factory
```

#### **Changes:**
```python
# tidyllm/__init__.py
from .reasoning import (
    TensorLogicService,
    SymbolicReasoner,
    AnalogicalReasoner,
    YRSNScorer,
    create_reasoner  # Factory function
)
```

#### **Tests:**
```
tidyllm/tests/reasoning/
├── test_symbolic.py
├── test_analogical.py
├── test_yrsn.py
├── test_temperature.py
└── test_service.py
```

---

## 🎨 User Experience

### **Scenario 1: Using Just Math Primitives**
```python
import tlm

# Temperature-scaled softmax
logits = [2.0, 1.0, 0.5]
probs_cold = tlm.temperature_scaled_softmax(logits, temperature=0.01)  # [0.99, 0.01, 0.00]
probs_hot = tlm.temperature_scaled_softmax(logits, temperature=2.0)    # [0.42, 0.32, 0.26]

# Cosine similarity
vec1 = [1.0, 2.0, 3.0]
vec2 = [2.0, 3.0, 4.0]
similarity = tlm.cosine_similarity(vec1, vec2)  # 0.974
```

**Use Case:** Data scientists who just need core operations

---

### **Scenario 2: Using Embedding-Based Reasoning**
```python
import tidyllm_sentence as tls

# Analogical reasoning via case retrieval
query = "How should I validate data?"
cases = [
    "Validation requires checking data types",
    "Data validation includes range checks",
    "Ensure data meets schema requirements"
]

# Embed cases
embeddings, model = tls.lsa_fit_transform(cases, n_components=10)

# Find similar cases with temperature control
results = tls.analogical_reasoning(
    query=query,
    cases=cases,
    embeddings=embeddings,
    top_k=3,
    temperature=0.5  # Moderate exploration
)

for case_idx, score, case_text in results:
    print(f"Score {score:.3f}: {case_text}")
```

**Use Case:** NLP engineers working with embeddings

---

### **Scenario 3: Using Full Tensor Logic Service**
```python
from tidyllm.reasoning import TensorLogicService

# Create service with rules and cases
service = TensorLogicService(
    rules=[
        {'pattern': 'MVS 5.4.3', 'action': 'check_data_validation'},
        {'pattern': 'compliance', 'action': 'verify_standards'}
    ],
    case_base=[
        "Previous compliance check required data validation...",
        "Last MVS audit needed schema validation..."
    ],
    embedding_method='lsa'
)

# Symbolic reasoning (T=0.0 - certifiable)
result_symbolic = service.infer(
    query="Is MVS 5.4.3 data validation required?",
    context={'document': document_data},
    temperature=0.0
)
print(f"Certifiable: {result_symbolic['certifiable']}")  # True
print(f"Answer: {result_symbolic['answer']}")

# Analogical reasoning (T=0.7 - case-based)
result_analogical = service.infer(
    query="What validation approach was used before?",
    temperature=0.7
)
print(f"Certifiable: {result_analogical['certifiable']}")  # False
print(f"Answer: {result_analogical['answer']}")

# Hybrid reasoning (T=0.3 - both)
result_hybrid = service.infer(
    query="How should I validate this data?",
    temperature=0.3
)
print(f"Mode: {result_hybrid['reasoning_mode']}")  # 'hybrid'
print(f"Trustworthiness: {result_hybrid['trustworthiness']}")
```

**Use Case:** Application developers building compliance systems

---

## 🔄 Migration from `compliance-qa`

### **Current State:**
```
compliance-qa/
├── domain/services/tensor_logic/
│   ├── tensor_logic_service.py
│   └── temperature_router.py
└── adapters/secondary/tensor_logic/
    ├── tidyllm_embedding_adapter.py
    ├── tidyllm_trustworthiness_adapter.py
    └── compliance_rules_adapter.py
```

### **After Distribution:**

**1. Move to `tlm`:**
```
tlm/core/similarity.py       ← Extract similarity functions
tlm/core/temperature.py      ← Extract temperature scaling
```

**2. Move to `tidyllm-sentence`:**
```
tidyllm_sentence/reasoning.py  ← Extract analogical reasoning
                                  (from tidyllm_embedding_adapter)
```

**3. Move to `tidyllm`:**
```
tidyllm/reasoning/
├── symbolic/engine.py           ← compliance_rules_adapter.py
├── yrsn/quality.py              ← tidyllm_trustworthiness_adapter.py
├── temperature/router.py        ← temperature_router.py
└── service.py                   ← tensor_logic_service.py
```

**4. Update `compliance-qa`:**
```python
# compliance-qa now imports from tidyllm ecosystem
from tidyllm.reasoning import TensorLogicService

class ComplianceApplicationService:
    def __init__(self):
        self.tensor_logic = TensorLogicService(...)

    def check_compliance(self, document):
        return self.tensor_logic.infer(...)
```

---

## 📊 Dependency Graph

```
┌─────────────────────────────────────────┐
│           compliance-qa                 │
│     (Application-Specific Logic)        │
│                                          │
│  Uses: tidyllm.reasoning                 │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│            tidyllm                       │
│    (Business Logic & Infrastructure)    │
│                                          │
│  - reasoning/service.py (orchestration)  │
│  - reasoning/symbolic/ (rules)           │
│  - reasoning/yrsn/ (trustworthiness)     │
│  - reasoning/temperature/ (routing)      │
│                                          │
│  Depends on: tidyllm-sentence, tlm       │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      ↓             ↓
┌────────────┐  ┌──────────────────────┐
│    tlm     │  │  tidyllm-sentence    │
│  (Math)    │  │   (Embeddings)       │
│            │  │                      │
│ similarity │  │ reasoning.py         │
│ temperature│  │ (analogical)         │
│            │←─│                      │
│ Depends: ø │  │ Depends on: tlm      │
└────────────┘  └──────────────────────┘
```

---

## ✅ Benefits of Distribution

### **1. Composability**
```python
# Use only what you need
import tlm  # Just math
import tidyllm_sentence as tls  # Math + embeddings
from tidyllm.reasoning import TensorLogicService  # Full stack
```

### **2. Progressive Enhancement**
- Start with `tlm` for basics
- Add `tidyllm-sentence` for text understanding
- Use `tidyllm` for complete orchestration

### **3. Clear Responsibilities**
- **`tlm`**: Mathematical primitives (no dependencies)
- **`tidyllm-sentence`**: Text embeddings (depends on `tlm`)
- **`tidyllm`**: Business logic (depends on both)

### **4. Easy Testing**
- Each package tests its own components
- Integration tests in `tidyllm`
- Application tests in `compliance-qa`

### **5. Independent Evolution**
- `tlm` evolves math primitives
- `tidyllm-sentence` evolves embedding methods
- `tidyllm` evolves business logic
- All versioned independently

---

## 🎯 Final Recommendation

### **Distribute Tensor Logic Across TidyLLM Ecosystem:**

1. **`tlm`** ← Mathematical primitives
   - `cosine_similarity()`
   - `temperature_scaled_softmax()`
   - `pairwise_cosine()`

2. **`tidyllm-sentence`** ← Embedding-based reasoning
   - `analogical_reasoning()`
   - `case_retrieval()`
   - `similarity_based_inference()`

3. **`tidyllm`** ← Orchestration & business logic
   - `TensorLogicService`
   - `SymbolicReasoner`
   - `YRSNScorer`
   - `TemperatureRouter`

### **Why This Works:**
- ✅ Each component lives where it naturally belongs
- ✅ Users discover functionality organically
- ✅ No additional packages to maintain
- ✅ Leverages existing infrastructure
- ✅ Clear dependency graph
- ✅ Philosophy-aligned (tidyllm verse principles)

---

## 🚀 Next Steps

1. **Confirm distribution strategy** with you
2. **Phase 1:** Enhance `tlm` with similarity/temperature (1-2 hours)
3. **Phase 2:** Enhance `tidyllm-sentence` with reasoning (2-3 hours)
4. **Phase 3:** Add Tensor Logic to `tidyllm` (4-6 hours)
5. **Phase 4:** Update `compliance-qa` to use ecosystem (1-2 hours)
6. **Phase 5:** Documentation & examples (2-3 hours)

**Total Estimated Time:** 10-16 hours of focused work

---

**Ready to proceed with distributed approach?** 🤔
