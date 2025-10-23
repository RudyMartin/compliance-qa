# How Tensor Logic Components Work Together

## 🎯 **The Big Picture**

You have **THREE separate but interconnected systems** working together:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. COMPLIANCE-QA SYSTEM (Your Main Application)                │
│    - Business logic, workflows, portals, APIs                  │
│    - Document processing, compliance checking                  │
│    - MLflow tracking, database storage                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────────┐
│ 2. TENSOR LOGIC (NEW - Pedro Domingos's Approach)              │
│    - Temperature-based reasoning (symbolic ↔ analogical)       │
│    - Hexagonal architecture (domain → adapters)                │
│    - YRSN trustworthiness scoring                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────────┐
│ 3. TIDYLLM ECOSYSTEM (Your ML Infrastructure)                  │
│    - packages/tlm/ (Pure-Python ML)                            │
│    - packages/tidyllm-sentence/ (Embeddings)                   │
│    - packages/tidyllm/ (LLM gateways, workflows)               │
│    - code_samples/yrsn/ (Compliance patterns)                  │
└─────────────────────────────────────────────────────────────────┘
```

Let me explain each layer and how they connect...

---

## 📚 **Layer 1: TidyLLM Ecosystem (Foundation)**

### **What It Is**
Your **proprietary ML infrastructure** - the "engine room" that powers everything.

### **Components**

#### **A. `packages/tlm/` - Pure-Python ML**
- **What**: NumPy replacement + ML algorithms
- **Examples**: `mean()`, `std()`, `cosine_similarity()`, `dot()`, PCA, clustering
- **Philosophy**: Zero dependencies, complete transparency
- **Used By**: YRSN trustworthiness scoring (coherence calculations)

```python
# From packages/tlm/
from tlm import mean, std, cosine_similarity

# Calculate average coherence
coherence_scores = [0.85, 0.78, 0.92]
avg_coherence = mean(coherence_scores)  # Uses YOUR code, not numpy!
```

#### **B. `packages/tidyllm-sentence/` - Text Embeddings**
- **What**: Text → vector embeddings (LSA, TF-IDF, transformers)
- **Examples**: `lsa_fit_transform()`, `cosine_similarity()`
- **Philosophy**: Lightweight, no sentence-transformers dependency
- **Used By**: Query-response consistency, coherence scoring

```python
# From packages/tidyllm-sentence/
from tidyllm_sentence import lsa_fit_transform, cosine_similarity

texts = ["Is document compliant?", "Yes, document is compliant"]
embeddings = lsa_fit_transform(texts)
similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
# Tells you if response matches query semantically
```

#### **C. `packages/tidyllm/` - LLM Infrastructure**
- **What**: Corporate LLM gateways, workflows, RAG systems
- **Examples**: `CorporateLLMGateway`, `QAWorkflow`, RAG with authority tiers
- **Philosophy**: Unified sessions, connection pooling
- **Used By**: Compliance-QA main application (NOT Tensor Logic directly)

```python
# From packages/tidyllm/
from tidyllm.gateways import CorporateLLMGateway

gateway = CorporateLLMGateway()
response = gateway.query("Analyze document compliance")
# This is how Compliance-QA talks to LLMs (Azure OpenAI, Claude, etc.)
```

#### **D. `code_samples/yrsn/` - Compliance Patterns**
- **What**: Reference implementations for compliance validation
- **Examples**: YRSN analyzer, evidence validator, consistency checker
- **Philosophy**: Production-tested patterns from real compliance work
- **Used By**: YRSN trustworthiness adapter (patterns extracted/hardcoded)

```python
# Patterns INSPIRED Tensor Logic trustworthiness adapter
# Not directly imported, but logic was copied/adapted

# YRSN Pattern (from code_samples/yrsn/yrsn_analyzer.py):
actionable_indicators = ['required', 'must use', 'compliant']
noise_indicators = ['may be', 'unclear', 'possibly']

# Used in adapters/secondary/tensor_logic/tidyllm_trustworthiness_adapter.py
# to score response quality
```

### **Key Point**:
**TidyLLM Ecosystem is INDEPENDENT** - you can use it in ANY project, not just Tensor Logic or Compliance-QA.

---

## 🧠 **Layer 2: Tensor Logic (The "Brain")**

### **What It Is**
A **reasoning framework** based on Pedro Domingos's work that blends:
- **Symbolic reasoning** (rules, logic) ← T=0.0
- **Analogical reasoning** (similarity, cases) ← T≥0.5
- **Hybrid** (both) ← T=0.1-0.4

### **Architecture: Hexagonal (Ports & Adapters)**

```
┌─────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                        │
│         (Business logic, NO external dependencies)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  domain/services/tensor_logic/                          │
│  ├── tensor_logic_service.py     ← Core service        │
│  ├── temperature_router.py       ← Routes by T value   │
│  ├── inference_result.py         ← Result dataclass    │
│                                                         │
│  domain/ports/reasoning_ports.py  ← Interface contracts│
│  ├── SymbolicReasoningPort                             │
│  ├── EmbeddingReasoningPort                            │
│  ├── TrustworthinessPort                               │
│  ├── HybridReasoningPort                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↑ implemented by
┌─────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER                        │
│         (Concrete implementations using YOUR tools)     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  adapters/secondary/tensor_logic/                       │
│  ├── symbolic_reasoning_adapter.py                      │
│  │   └── Wraps MVS rules (symbolic T=0.0)              │
│  │                                                      │
│  ├── embedding_reasoning_adapter.py                     │
│  │   └── Uses tidyllm-sentence (analogical T≥0.5)      │
│  │                                                      │
│  ├── tidyllm_trustworthiness_adapter.py ← YRSN!        │
│  │   └── Uses tlm + tidyllm-sentence + YRSN patterns   │
│  │                                                      │
│  └── hybrid_reasoning_adapter.py                        │
│      └── Combines symbolic + embedding                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↑ orchestrated by
┌─────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                       │
│              (Use cases, workflows)                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  application/services/                                  │
│  └── tensor_logic_application_service.py               │
│      ├── check_compliance()                            │
│      ├── assess_risk()                                 │
│      ├── find_similar_entities()                       │
│      └── batch_check_compliance()                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↑ created by
┌─────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                       │
│         (Dependency injection, factories)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  infrastructure/factories/                              │
│  └── tensor_logic_factory.py                           │
│      ├── create_with_tidyllm()    ← Recommended!       │
│      ├── create_with_mock_trustworthiness()            │
│      └── create_default()                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **How Temperature Works**

```python
from infrastructure.factories.tensor_logic_factory import create_tensor_logic_service

service = create_tensor_logic_service(mode='tidyllm')

# T=0.0 → SYMBOLIC (rules-based, certifiable)
result = service.check_compliance(
    document={'data_quality': 'documented'},
    temperature=0.0  # Pure rules, deterministic
)
# Uses: ComplianceRulesAdapter → MVS rules
# Certifiable: YES
# Trustworthiness: YRSN scoring

# T=0.3 → HYBRID (rules + past cases)
result = service.assess_risk(
    entity_data={'name': 'Bank A'},
    temperature=0.3  # Mix of rules + similar entities
)
# Uses: ComplianceRulesAdapter + TidyLLMEmbeddingAdapter
# Certifiable: NO
# Trustworthiness: YRSN scoring

# T=0.7 → ANALOGICAL (similarity search)
result = service.find_similar_entities(
    entity_data={'name': 'Fintech Startup'},
    temperature=0.7  # Pure similarity
)
# Uses: TidyLLMEmbeddingAdapter only
# Certifiable: NO
# Trustworthiness: YRSN scoring
```

### **YRSN Trustworthiness Flow**

```python
# Every result gets scored for trustworthiness
result = service.check_compliance(document, temperature=0.0)

# Behind the scenes:
# 1. Tensor Logic generates answer
# 2. TidyLLMTrustworthinessAdapter scores it:
#    a. YRSN quality (actionable vs noise)
#    b. Evidence authenticity (timestamps, sources)
#    c. Logical consistency (query ↔ response match)
#    d. Coherence (sentence flow)
#    e. Context alignment

# Result contains:
result.trustworthiness_score  # 0.85 (weighted average)
result.components  # {'yrsn_quality': 0.82, 'evidence': 0.75, ...}
result.yrsn_validation  # 'PASS' or 'FAIL'
```

### **Key Point**:
**Tensor Logic is PLUGGABLE** - it uses YOUR TidyLLM packages through ports/adapters pattern. You can swap adapters without changing domain logic.

---

## 🏢 **Layer 3: Compliance-QA System (The "Application")**

### **What It Is**
Your **main business application** - document processing, compliance workflows, user interfaces.

### **Components**

#### **A. Domain Services (Business Logic)**
```
domain/services/
├── compliance_service.py           ← Core compliance checking
├── document_processor.py           ← PDF/document handling
├── dspy_execution_service.py       ← DSPy workflow execution
├── cumulative_learning_pipeline.py ← Learning from feedback
└── tensor_logic/ ← NEW!            ← Tensor Logic integration
```

#### **B. Infrastructure (External Services)**
```
infrastructure/
├── services/
│   └── enhanced_mlflow_service.py  ← MLflow tracking (PostgreSQL + S3)
├── factories/
│   └── tensor_logic_factory.py     ← Creates Tensor Logic services
└── settings.yaml                   ← Configuration
```

#### **C. Portals (User Interfaces)**
```
portals/
├── chat/tensor_logic_chat.py       ← Streamlit UI for Tensor Logic
└── setup/first_time_setup_app.py   ← System configuration
```

#### **D. API Layer**
```
api/
└── (FastAPI endpoints for compliance checking)
```

### **How Compliance-QA Uses Tensor Logic**

#### **Option 1: Direct Integration (Simple)**
```python
# In any domain service
from infrastructure.factories.tensor_logic_factory import create_tensor_logic_service

class ComplianceService:
    def __init__(self):
        # Create Tensor Logic service
        self.tensor_logic = create_tensor_logic_service(mode='tidyllm')

    def check_mvs_compliance(self, document):
        # Use Tensor Logic for compliance checking
        result = self.tensor_logic.check_compliance(
            document=document,
            compliance_standard='MVS_5.4.3',
            temperature=0.0  # Certifiable
        )

        # Log to MLflow
        self.mlflow_service.log_metrics({
            'confidence': result.confidence,
            'trustworthiness': result.trustworthiness_score,
            'yrsn_quality': result.components['yrsn_quality']
        })

        return result
```

#### **Option 2: MLflow Model (Advanced)**
```python
# Once packaged with MLflow wrapper
import mlflow
from compliance_qa.mlflow import TensorLogicModel

# Train/log model
with mlflow.start_run():
    model = TensorLogicModel(temperature=0.0)
    mlflow.pyfunc.log_model("tensor_logic", python_model=model)

# Use in production
class ComplianceService:
    def __init__(self):
        # Load from MLflow Model Registry
        self.tensor_logic = mlflow.pyfunc.load_model(
            "models:/TensorLogicCompliance/Production"
        )

    def check_mvs_compliance(self, document):
        result = self.tensor_logic.predict({
            "document": document,
            "query": "Check MVS 5.4.3 compliance",
            "temperature": 0.0
        })
        return result
```

### **MLflow Integration Architecture**

```
┌─────────────────────────────────────────────────────────┐
│ Compliance-QA System                                    │
│                                                         │
│  domain/services/compliance_service.py                  │
│         ↓ uses                                          │
│  Tensor Logic (via factory or MLflow)                   │
│         ↓ logs to                                       │
│  infrastructure/services/enhanced_mlflow_service.py     │
│         ↓ stores                                        │
│  ┌─────────────────┐     ┌──────────────────┐          │
│  │ PostgreSQL      │     │ S3 (Artifacts)   │          │
│  │ (Tracking DB)   │     │ (Models, Logs)   │          │
│  └─────────────────┘     └──────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

### **Key Point**:
**Compliance-QA ORCHESTRATES** - it coordinates Tensor Logic, MLflow, databases, and user interfaces into a cohesive system.

---

## 🔄 **Complete Data Flow Example**

Let's trace a **compliance check request** through all layers:

### **Scenario**: User asks "Is this document MVS compliant?" via Streamlit UI

```
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: User Interaction                                    │
└──────────────────────────────────────────────────────────────┘
   User → Streamlit UI (portals/chat/tensor_logic_chat.py)
   ↓
   Clicks "Check Compliance"
   Temperature slider at 0.0 (symbolic mode)
   Uploads document JSON

┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Portal → Application Service                        │
└──────────────────────────────────────────────────────────────┘
   Portal calls:
   service = create_tensor_logic_service(mode='tidyllm')
   result = service.check_compliance(
       document={'data_quality': 'documented', ...},
       compliance_standard='MVS_5.4.3',
       temperature=0.0
   )

┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Application Service → Domain Service                │
└──────────────────────────────────────────────────────────────┘
   application/services/tensor_logic_application_service.py
   ↓
   Calls: self.tensor_logic_service.infer(
       query="Check MVS 5.4.3 compliance",
       context={'document': document},
       temperature=0.0,
       score_trustworthiness=True
   )

┌──────────────────────────────────────────────────────────────┐
│ STEP 4: Domain Service (Temperature Routing)                │
└──────────────────────────────────────────────────────────────┘
   domain/services/tensor_logic/tensor_logic_service.py
   ↓
   TemperatureRouter checks: temperature=0.0 → SYMBOLIC mode
   ↓
   Calls: self._symbolic_reasoning(query, context, rules=['MVS_5.4.3'])

┌──────────────────────────────────────────────────────────────┐
│ STEP 5: Symbolic Adapter (MVS Rules)                        │
└──────────────────────────────────────────────────────────────┘
   adapters/secondary/tensor_logic/symbolic_reasoning_adapter.py
   ↓
   ComplianceRulesAdapter.execute(query, context, rules)
   ↓
   Loads: domain/rules/mvs_rules.py
   ↓
   Checks document against MVS 5.4.3 requirements:
   - data_quality: ✅ documented
   - methodology: ❓ missing
   - monitoring: ❓ missing
   ↓
   Returns: {
       'answer': False,  # Not compliant
       'confidence': 1.0,  # Symbolic is certain
       'rules_applied': ['MVS_5.4.3'],
       'evidence': ['data_quality documented', 'methodology missing']
   }

┌──────────────────────────────────────────────────────────────┐
│ STEP 6: Trustworthiness Scoring (YRSN)                      │
└──────────────────────────────────────────────────────────────┘
   adapters/secondary/tensor_logic/tidyllm_trustworthiness_adapter.py
   ↓
   TidyLLMTrustworthinessAdapter.score(
       query="Check MVS 5.4.3 compliance",
       response=False,
       context={'document': document}
   )
   ↓
   Calculates 5 component scores:

   1. YRSN Quality (30%):
      - Response text: "False" (too short)
      - Actionable indicators: 0
      - Noise indicators: 0
      - Score: 0.3 (low - not enough content)

   2. Evidence Authenticity (20%):
      Uses packages/tlm/ (if needed for calculations)
      - No timestamps/versions in response
      - Score: 0.2

   3. Logical Consistency (25%):
      Uses packages/tidyllm-sentence/:
      query_emb = lsa_fit_transform(["Check MVS 5.4.3 compliance"])
      response_emb = lsa_fit_transform(["False"])
      similarity = cosine_similarity(query_emb, response_emb)
      - Score: 0.6 (moderate match)

   4. Coherence (15%):
      Uses packages/tidyllm-sentence/ + packages/tlm/:
      - Single word response, trivially coherent
      - Score: 0.8

   5. Context Alignment (10%):
      - Checks overlap with document context
      - Score: 0.5

   ↓
   Weighted average:
   trust_score = 0.3*0.3 + 0.2*0.2 + 0.25*0.6 + 0.15*0.8 + 0.1*0.5
              = 0.09 + 0.04 + 0.15 + 0.12 + 0.05
              = 0.45
   ↓
   Returns: {
       'score': 0.45,
       'reliable': False,  # < 0.7 threshold
       'yrsn_validation': 'FAIL',
       'components': {...},
       'explanation': 'Low trustworthiness (0.45): ...'
   }

┌──────────────────────────────────────────────────────────────┐
│ STEP 7: Domain Service Combines Results                     │
└──────────────────────────────────────────────────────────────┘
   domain/services/tensor_logic/tensor_logic_service.py
   ↓
   Creates InferenceResult:
   InferenceResult(
       answer=False,
       confidence=1.0,  # Symbolic confidence
       reasoning_mode=ReasoningMode.SYMBOLIC,
       temperature=0.0,
       certifiable=True,  # T=0.0 is certifiable
       trustworthiness_score=0.45,  # YRSN score
       rules_applied=[...],
       similar_entities=[],  # None for symbolic
       explanation="Document fails MVS 5.4.3: missing methodology, monitoring"
   )

┌──────────────────────────────────────────────────────────────┐
│ STEP 8: Application Service Returns to Portal               │
└──────────────────────────────────────────────────────────────┘
   application/services/tensor_logic_application_service.py
   ↓
   Returns InferenceResult to portal

┌──────────────────────────────────────────────────────────────┐
│ STEP 9: Portal Displays Results                             │
└──────────────────────────────────────────────────────────────┘
   portals/chat/tensor_logic_chat.py
   ↓
   Streamlit displays:
   ┌─────────────────────────────────────────┐
   │ Answer: No (Not Compliant)              │
   │                                         │
   │ Confidence: 100%                        │
   │ Trustworthiness: 45% ⚠️                 │
   │ Certifiable: ✅ Yes                     │
   │ YRSN Validation: ❌ FAIL                │
   │                                         │
   │ Reasoning: SYMBOLIC (T=0.0)             │
   │                                         │
   │ Explanation:                            │
   │ Document fails MVS 5.4.3 compliance:    │
   │ - ✅ data_quality: documented           │
   │ - ❌ methodology: missing               │
   │ - ❌ monitoring: missing                │
   │                                         │
   │ Trustworthiness Issues:                 │
   │ - Low YRSN quality (0.30)               │
   │ - Insufficient evidence (0.20)          │
   └─────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ STEP 10: (Optional) Log to MLflow                           │
└──────────────────────────────────────────────────────────────┘
   If MLflow logging enabled:
   infrastructure/services/enhanced_mlflow_service.py
   ↓
   mlflow.log_metrics({
       'confidence': 1.0,
       'trustworthiness': 0.45,
       'yrsn_quality': 0.30,
       'evidence_authenticity': 0.20,
       'logical_consistency': 0.60,
       'coherence': 0.80,
       'context_alignment': 0.50
   })
   ↓
   mlflow.log_params({
       'temperature': 0.0,
       'reasoning_mode': 'SYMBOLIC',
       'compliance_standard': 'MVS_5.4.3'
   })
   ↓
   Stored in:
   - PostgreSQL (tracking DB)
   - S3 (artifacts)
```

---

## 🎨 **Visual: How Everything Fits**

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
│  Streamlit Portal → FastAPI → CLI                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   COMPLIANCE-QA APPLICATION                     │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Domain Services  │  │ Infrastructure   │  │ Adapters     │ │
│  │ - Compliance     │  │ - MLflow Service │  │ - Database   │ │
│  │ - Documents      │  │ - Factories      │  │ - S3         │ │
│  │ - DSPy Workflows │  │ - Settings       │  │ - External   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                              ↓                                  │
│                    ┌──────────────────┐                         │
│                    │ TENSOR LOGIC     │ ← NEW!                  │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────────┐
│                      TENSOR LOGIC LAYER                         │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Domain (Ports & Services)                              │    │
│  │ - TensorLogicService                                   │    │
│  │ - TemperatureRouter                                    │    │
│  │ - InferenceResult                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Adapters (Implementations)                             │    │
│  │ - ComplianceRulesAdapter (symbolic)                    │    │
│  │ - TidyLLMEmbeddingAdapter (analogical)                 │    │
│  │ - TidyLLMTrustworthinessAdapter (YRSN) ← Uses TidyLLM! │    │
│  │ - SmartHybridAdapter                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Application Services                                   │    │
│  │ - TensorLogicApplicationService                        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ uses
┌─────────────────────────────────────────────────────────────────┐
│                     TIDYLLM ECOSYSTEM                           │
│                                                                 │
│  ┌──────────────┐  ┌────────────────────┐  ┌──────────────┐   │
│  │ packages/tlm │  │ packages/tidyllm-  │  │ packages/    │   │
│  │              │  │       sentence     │  │  tidyllm     │   │
│  │ Pure-Python  │  │                    │  │              │   │
│  │ ML algos     │  │ Text embeddings    │  │ LLM gateways │   │
│  │ - mean()     │  │ - lsa_fit_transform│  │ - Corporate  │   │
│  │ - std()      │  │ - cosine_similarity│  │ - RAG        │   │
│  │ - cosine()   │  │ - TF-IDF           │  │ - Workflows  │   │
│  └──────────────┘  └────────────────────┘  └──────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ code_samples/yrsn/                                     │    │
│  │ Reference compliance patterns (YRSN framework)         │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ stores/logs to
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ PostgreSQL   │  │ S3 Artifacts │  │ MLflow Tracking  │     │
│  │ (Pooled)     │  │              │  │ Server           │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 **Key Takeaways**

### **1. Separation of Concerns**
- **TidyLLM** = Reusable ML primitives (tlm, tidyllm-sentence, tidyllm)
- **Tensor Logic** = Reasoning framework (temperature, ports/adapters)
- **Compliance-QA** = Business application (workflows, UI, persistence)

### **2. Dependency Direction** (Bottom → Top)
```
Compliance-QA depends on Tensor Logic
        ↓
Tensor Logic depends on TidyLLM
        ↓
TidyLLM depends on NOTHING (pure Python, zero deps)
```

### **3. YRSN Trustworthiness**
- Lives in **Tensor Logic layer** (adapters/secondary/)
- Uses **TidyLLM layer** (tlm + tidyllm-sentence)
- Inspired by **code_samples/yrsn/** patterns
- Scores EVERY inference result automatically

### **4. Temperature Control**
```
T=0.0  → Symbolic → ComplianceRulesAdapter → MVS rules
T=0.3  → Hybrid   → Symbolic + EmbeddingAdapter → Rules + cases
T=0.7  → Analogical → EmbeddingAdapter → Pure similarity
```

### **5. MLflow Integration** (Proposed)
- **Current**: Manual logging in Compliance-QA
- **Future**: Tensor Logic as MLflow PyFunc model
- **Benefits**: Versioning, deployment, model registry

### **6. No External APIs**
```
✅ packages/tlm              → Pure Python (zero deps)
✅ packages/tidyllm-sentence → Lightweight embeddings
✅ YRSN trustworthiness      → YOUR code, no APIs
❌ Cleanlab TLM              → REMOVED!
```

---

## 🚀 **Why This Architecture Matters**

### **Portability**
- TidyLLM packages work ANYWHERE (other projects, other companies)
- Tensor Logic can be extracted and used standalone
- No vendor lock-in (MLflow optional, not required)

### **Testability**
- Each layer tests independently
- Mock adapters for Tensor Logic
- Pure functions in TidyLLM (deterministic)

### **Transparency**
- Every algorithm step visible
- No "black box" ML models
- Audit trail from query → result → storage

### **Compliance-Ready**
- Certifiable results (T=0.0)
- YRSN quality validation
- Evidence tracking
- MLflow lineage

---

## ❓ **Common Questions**

### **Q: Why are packages inside compliance-qa?**
A: Historical development. Ideally, they'd be separate repos/packages. For now, they're bundled for convenience. MLflow packaging will need to handle this.

### **Q: Does Tensor Logic require MLflow?**
A: NO! Tensor Logic works standalone. MLflow is for **tracking/deployment** (optional enhancement).

### **Q: Can I use Tensor Logic without Compliance-QA?**
A: YES! Extract these directories:
- `domain/services/tensor_logic/`
- `adapters/secondary/tensor_logic/`
- `application/services/tensor_logic_application_service.py`
- `infrastructure/factories/tensor_logic_factory.py`
- `packages/tlm/`, `packages/tidyllm-sentence/`

### **Q: What happens if I change temperature mid-workflow?**
A: Each `infer()` call is independent - different T values, different reasoning modes. Temperature is per-request, not per-service.

### **Q: Where does DSPy fit in?**
A: DSPy is in Compliance-QA layer (`domain/services/dspy_execution_service.py`). It's SEPARATE from Tensor Logic. You could combine them (use Tensor Logic inside DSPy prompts), but currently they're independent.

---

## 🎯 **Next Steps Understanding**

Now that you see how it all fits together, the **MLflow packaging question** becomes clearer:

**Challenge**: How do we package Tensor Logic for MLflow when:
1. It depends on `packages/tlm`, `packages/tidyllm-sentence` (inside compliance-qa)
2. It uses existing domain/adapters/application/infrastructure code
3. MLflow deployments need self-contained environments

**Options**:
1. **Package compliance-qa itself** (what I proposed) - makes everything installable
2. **Extract Tensor Logic as separate package** - cleaner but more work
3. **Use MLflow's artifact bundling** - include packages/ in model artifacts

Which approach makes most sense for YOUR workflow? 🤔
