# Tensor Logic Library - Naming & Structure

## 🎯 **The Goal**

Make Tensor Logic a **standalone, reusable library** that fits into the TidyLLM ecosystem.

---

## 📦 **What Is This Library?**

A **temperature-based reasoning framework** that blends:
- Symbolic reasoning (rules, logic) at T=0.0
- Analogical reasoning (similarity, cases) at T≥0.5
- Hybrid reasoning (both) at T=0.1-0.4
- YRSN trustworthiness scoring (quality validation)

**Key Value Prop**: Certifiable compliance decisions with adjustable reasoning mode.

---

## 🤔 **Naming Considerations**

### **Context: TidyLLM Ecosystem**
Your existing packages follow these patterns:
- `tlm` - Pure-Python ML primitives (short, technical)
- `tidyllm` - Corporate LLM workflows (brand prefix)
- `tidyllm-sentence` - Embeddings (brand + domain)

### **Tensor Logic Specifics**
- Based on **Pedro Domingos's** work (academic credibility)
- Uses **temperature control** (key differentiator)
- Provides **certifiable reasoning** (compliance focus)
- Includes **YRSN framework** (quality validation)

---

## 💡 **Naming Options**

### **Option 1: `tidyllm-tensor` (Recommended)**
```python
from tidyllm_tensor import TemperatureRouter, TensorLogicService
```

**Pros:**
- ✅ Fits TidyLLM naming pattern (`tidyllm-*`)
- ✅ Short, memorable
- ✅ Clear it's part of TidyLLM family
- ✅ "Tensor" references Domingos's work
- ✅ Good for PyPI: `pip install tidyllm-tensor`

**Cons:**
- ⚠️ "Tensor" might imply TensorFlow connection (it doesn't use it)

**Package Structure:**
```
tidyllm-tensor/
├── tidyllm_tensor/
│   ├── __init__.py
│   ├── reasoning/          # Core reasoning modes
│   ├── scoring/            # YRSN trustworthiness
│   ├── temperature.py      # Temperature routing
│   └── service.py          # Main service
```

---

### **Option 2: `tidyllm-reason` or `tidyllm-reasoning`**
```python
from tidyllm_reason import CertifiableReasoner
```

**Pros:**
- ✅ Clear purpose (reasoning framework)
- ✅ Fits TidyLLM pattern
- ✅ No confusion with TensorFlow
- ✅ Domain-focused name

**Cons:**
- ⚠️ Doesn't reference Domingos/temperature
- ⚠️ Generic (many reasoning libraries exist)

---

### **Option 3: `tidyllm-certifiable`**
```python
from tidyllm_certifiable import CertifiableCompliance
```

**Pros:**
- ✅ Emphasizes key differentiator (certifiable results)
- ✅ Compliance-focused
- ✅ Unique positioning

**Cons:**
- ⚠️ Long name
- ⚠️ Doesn't capture temperature/analogical aspects
- ⚠️ Too narrow (library does more than just certifiable reasoning)

---

### **Option 4: `tidyllm-domingos`**
```python
from tidyllm_domingos import TemperatureReasoner
```

**Pros:**
- ✅ Credits academic source
- ✅ Unique, searchable
- ✅ Academic credibility

**Cons:**
- ⚠️ Obscure to those unfamiliar with Domingos
- ⚠️ Hard to spell/remember
- ⚠️ Might seem like a "wrapper" of someone else's work

---

### **Option 5: `tidyllm-compliance` (Already taken?)**
```python
from tidyllm_compliance import ComplianceReasoner
```

**Pros:**
- ✅ Domain-specific
- ✅ Clear use case

**Cons:**
- ❌ Name clash with `code_samples/yrsn/tidyllm-compliance/`
- ❌ Too narrow (framework useful beyond compliance)
- ❌ Confusing with existing YRSN code

---

### **Option 6: `tidyllm-yrsn`**
```python
from tidyllm_yrsn import YRSNReasoner
```

**Pros:**
- ✅ Emphasizes YRSN framework
- ✅ Unique acronym
- ✅ Fits TidyLLM pattern

**Cons:**
- ⚠️ YRSN is just ONE component (trustworthiness scoring)
- ⚠️ Doesn't capture temperature/reasoning aspects
- ⚠️ Obscure acronym for new users

---

### **Option 7: `tensor-logic` (Standalone)**
```python
from tensor_logic import TemperatureReasoner
```

**Pros:**
- ✅ Direct reference to Domingos
- ✅ Standalone brand (not tied to TidyLLM)
- ✅ Short, memorable

**Cons:**
- ❌ Breaks TidyLLM naming convention
- ❌ Loses ecosystem association
- ❌ Harder to market as part of TidyLLM suite

---

## 🎯 **Recommended Option: `tidyllm-tensor`**

### **Why This Name?**

1. **Fits TidyLLM Ecosystem**
   ```
   tlm                    → ML primitives
   tidyllm                → LLM workflows
   tidyllm-sentence       → Embeddings
   tidyllm-tensor    ← NEW → Temperature reasoning
   ```

2. **References Academic Source**
   - "Tensor Logic" = Pedro Domingos's framework
   - Gives academic credibility
   - Searchable/citable

3. **Short & Memorable**
   - Easy to type: `pip install tidyllm-tensor`
   - Easy to import: `from tidyllm_tensor import ...`

4. **Unique Positioning**
   - Not generic like "reasoning"
   - Not too narrow like "certifiable"
   - Captures the essence (tensor = mathematical structure for reasoning)

---

## 📐 **Proposed Library Structure**

### **Package Name:** `tidyllm-tensor`

### **Directory Structure:**
```
tidyllm-tensor/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── requirements.txt
│
├── tidyllm_tensor/                    # Main package
│   ├── __init__.py                    # Public API
│   ├── version.py
│   │
│   ├── core/                          # Core reasoning engine
│   │   ├── __init__.py
│   │   ├── service.py                 # TensorLogicService
│   │   ├── temperature.py             # TemperatureRouter
│   │   ├── inference.py               # InferenceResult
│   │   └── modes.py                   # ReasoningMode enum
│   │
│   ├── ports/                         # Port interfaces (hexagonal)
│   │   ├── __init__.py
│   │   ├── symbolic.py                # SymbolicReasoningPort
│   │   ├── embedding.py               # EmbeddingReasoningPort
│   │   ├── trustworthiness.py         # TrustworthinessPort
│   │   └── hybrid.py                  # HybridReasoningPort
│   │
│   ├── adapters/                      # Adapter implementations
│   │   ├── __init__.py
│   │   ├── symbolic_rules.py          # Rules-based symbolic
│   │   ├── embedding_similarity.py    # Similarity-based analogical
│   │   ├── yrsn_scorer.py            # YRSN trustworthiness
│   │   └── hybrid_reasoner.py        # Hybrid adapter
│   │
│   ├── yrsn/                          # YRSN framework
│   │   ├── __init__.py
│   │   ├── quality.py                 # Quality scoring
│   │   ├── evidence.py                # Evidence validation
│   │   ├── consistency.py             # Consistency analysis
│   │   └── patterns.py                # YRSN patterns/indicators
│   │
│   └── factory.py                     # Factory for easy creation
│
├── examples/                          # Usage examples
│   ├── basic_usage.py
│   ├── temperature_sweep.py
│   ├── compliance_checking.py
│   └── yrsn_scoring.py
│
├── tests/                             # Test suite
│   ├── test_core/
│   ├── test_adapters/
│   └── test_yrsn/
│
└── docs/                              # Documentation
    ├── quickstart.md
    ├── temperature_guide.md
    ├── yrsn_framework.md
    └── api_reference.md
```

---

## 🔌 **Public API Design**

### **Simple Usage:**
```python
from tidyllm_tensor import create_reasoner

# Create reasoner with defaults
reasoner = create_reasoner()

# Symbolic reasoning (T=0.0 - certifiable)
result = reasoner.infer(
    query="Is document MVS compliant?",
    context={'document': document_data},
    temperature=0.0
)

print(f"Answer: {result.answer}")
print(f"Certifiable: {result.certifiable}")  # True
print(f"Trustworthiness: {result.trustworthiness_score}")
```

### **Advanced Usage:**
```python
from tidyllm_tensor import TensorLogicService, TemperatureRouter
from tidyllm_tensor.adapters import (
    SymbolicRulesAdapter,
    EmbeddingSimilarityAdapter,
    YRSNTrustworthinessAdapter
)

# Custom configuration
symbolic = SymbolicRulesAdapter(rules=my_rules)
embedding = EmbeddingSimilarityAdapter(method='lsa')
trustworthiness = YRSNTrustworthinessAdapter()

service = TensorLogicService(
    symbolic_engine=symbolic,
    embedding_engine=embedding,
    trustworthiness_scorer=trustworthiness
)

# Use with custom temperature routing
router = TemperatureRouter(
    symbolic_threshold=0.05,  # T ≤ 0.05 = symbolic
    hybrid_threshold=0.4      # T < 0.4 = hybrid
)

result = service.infer(query, context, temperature=0.3)
```

### **YRSN Scoring Only:**
```python
from tidyllm_tensor.yrsn import YRSNQualityScorer

scorer = YRSNQualityScorer()

quality = scorer.score(
    query="Is data validation required?",
    response="Yes, data validation is required per MVS 5.4.3"
)

print(f"YRSN Quality: {quality.score}")           # 0.85
print(f"Actionable Content: {quality.actionable_ratio}")
print(f"Noise Level: {quality.noise_percentage}%")
print(f"Validation: {quality.validation_status}")  # PASS/FAIL
```

---

## 🏷️ **Alternative Names (If You Don't Like `tidyllm-tensor`)**

### **Ranked by Preference:**

1. **`tidyllm-tensor`** ⭐ (Recommended)
   - Fits ecosystem, references Domingos

2. **`tidyllm-reason`**
   - Clear purpose, shorter

3. **`tidyllm-certify`**
   - Emphasizes certifiability

4. **`tidyllm-temperature`**
   - Direct feature reference

5. **`tidyllm-adaptive`**
   - Describes adjustable reasoning

6. **`tidyllm-logic`**
   - Simple, clear (but generic)

---

## 🎨 **Branding & Taglines**

### **For `tidyllm-tensor`:**

**Tagline Options:**
- "Temperature-Controlled Reasoning for Compliance"
- "Certifiable AI Decisions with Adjustable Logic"
- "From Symbolic Rules to Analogical Learning"
- "YRSN-Validated Reasoning Framework"
- "Pedro Domingos's Tensor Logic for Python"

**PyPI Description:**
```
tidyllm-tensor: Temperature-based reasoning framework combining symbolic
logic (T=0.0 - certifiable), hybrid reasoning (T=0.1-0.4), and analogical
inference (T≥0.5) with YRSN trustworthiness validation. Part of the
TidyLLM ecosystem for transparent, dependency-free ML.
```

**README Hero:**
```markdown
# 🧠 tidyllm-tensor

**Temperature-Controlled Reasoning for Certifiable Compliance**

Based on Pedro Domingos's Tensor Logic, `tidyllm-tensor` provides
adjustable reasoning modes from pure symbolic logic (certifiable)
to analogical learning (adaptive), with YRSN trustworthiness scoring.

Part of the TidyLLM ecosystem - transparent, dependency-free AI.
```

---

## 📊 **Decision Matrix**

| Name | Ecosystem Fit | Uniqueness | Clarity | Searchability | Score |
|------|--------------|------------|---------|---------------|-------|
| `tidyllm-tensor` | ✅ Perfect | ⭐ High | ✅ Good | ⭐ Excellent | **9/10** |
| `tidyllm-reason` | ✅ Perfect | ⚠️ Medium | ✅ Excellent | ⚠️ Generic | 7/10 |
| `tidyllm-certifiable` | ✅ Perfect | ⭐ High | ⚠️ Narrow | ✅ Good | 7/10 |
| `tidyllm-temperature` | ✅ Perfect | ⚠️ Medium | ✅ Good | ⚠️ Generic | 6/10 |
| `tensor-logic` | ❌ Standalone | ⭐ High | ✅ Good | ⭐ Excellent | 7/10 |

---

## ❓ **Questions for You**

1. **Do you like `tidyllm-tensor`?**
   - If yes → Let's design the full library structure
   - If no → Which alternative do you prefer?

2. **Should it be part of TidyLLM family or standalone?**
   - TidyLLM family → Use `tidyllm-*` prefix
   - Standalone → Use `tensor-logic` or similar

3. **What's the primary audience?**
   - Compliance professionals → Emphasize "certifiable"
   - Data scientists → Emphasize "temperature reasoning"
   - Both → Balanced approach

4. **Will this be open source (PyPI) or internal?**
   - PyPI → Focus on uniqueness/searchability
   - Internal → Focus on ecosystem fit

---

## 🎯 **My Recommendation**

**Name:** `tidyllm-tensor`

**Why:**
- ✅ Fits TidyLLM ecosystem perfectly
- ✅ References academic source (Domingos)
- ✅ Unique and searchable
- ✅ Short and memorable
- ✅ Works well on PyPI

**Next Steps:**
1. Confirm name
2. Design library structure (already outlined above)
3. Extract code from compliance-qa
4. Create setup.py and packaging
5. Write documentation
6. Publish to PyPI (optional)

---

**What do you think? Do you like `tidyllm-tensor`, or would you prefer a different name?** 🤔
