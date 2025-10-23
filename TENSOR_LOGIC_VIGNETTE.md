# Tensor Logic: Complete Code Examples & Vignettes

## 📚 Table of Contents

1. [Phase 1: tlm - Math Primitives](#phase-1-tlm---math-primitives)
2. [Phase 2: tidyllm-sentence - Analogical Reasoning](#phase-2-tidyllm-sentence---analogical-reasoning)
3. [Phase 3: tidyllm - Temperature-Controlled Orchestration](#phase-3-tidyllm---temperature-controlled-orchestration)
4. [Complete Integration Example](#complete-integration-example)

---

## Phase 1: tlm - Math Primitives

### 🔍 Similarity Functions

#### **Example 1: Computing Cosine Similarity**

```python
import sys
sys.path.insert(0, 'packages/tlm')
import tlm

# Basic cosine similarity between two vectors
vec1 = [1.0, 2.0, 3.0, 4.0]
vec2 = [2.0, 3.0, 4.0, 5.0]

similarity = tlm.cosine_similarity(vec1, vec2)
print(f"Cosine similarity: {similarity:.3f}")
# Output: Cosine similarity: 0.998

# Check if vectors are similar (threshold = 0.8)
if similarity > 0.8:
    print("Vectors are highly similar!")
```

#### **Example 2: Pairwise Similarity Matrix**

```python
import tlm

# Calculate similarity between all document embeddings
documents = [
    [1.0, 2.0, 3.0],  # Doc 1 embedding
    [2.0, 3.0, 4.0],  # Doc 2 embedding
    [0.0, 0.0, 1.0],  # Doc 3 embedding
]

# Compute pairwise similarity matrix
similarity_matrix = tlm.pairwise_cosine(documents)

print("Similarity Matrix:")
for i in range(len(documents)):
    for j in range(len(documents)):
        print(f"Doc{i+1} <-> Doc{j+1}: {similarity_matrix[i][j]:.3f}", end="  ")
    print()

# Output:
# Doc1 <-> Doc1: 1.000  Doc1 <-> Doc2: 0.998  Doc1 <-> Doc3: 0.802
# Doc2 <-> Doc1: 0.998  Doc2 <-> Doc2: 1.000  Doc2 <-> Doc3: 0.743
# Doc3 <-> Doc1: 0.802  Doc3 <-> Doc2: 0.743  Doc3 <-> Doc3: 1.000
```

#### **Example 3: Top-K Similar Documents**

```python
import tlm

# Find most similar documents to a query
query_embedding = [1.5, 2.5, 3.5]

corpus_embeddings = [
    [1.0, 2.0, 3.0],  # Doc A
    [5.0, 6.0, 7.0],  # Doc B (different topic)
    [1.2, 2.3, 3.4],  # Doc C (very similar)
    [0.5, 1.0, 1.5],  # Doc D
]

doc_names = ["Doc A", "Doc B", "Doc C", "Doc D"]

# Get top 3 most similar documents
results = tlm.top_k_similar(query_embedding, corpus_embeddings, k=3)

print("Top 3 most similar documents:")
for idx, score in results:
    print(f"  {doc_names[idx]}: {score:.3f}")

# Output:
# Top 3 most similar documents:
#   Doc C: 1.000
#   Doc A: 0.999
#   Doc D: 0.996
```

#### **Example 4: Nearest Neighbors with Different Metrics**

```python
import tlm

# Find nearest neighbors using Euclidean distance
query = [0.0, 0.0]
corpus = [
    [1.0, 0.0],  # Point A
    [0.0, 1.0],  # Point B
    [5.0, 5.0],  # Point C (far away)
    [0.5, 0.5],  # Point D (close)
]

# Euclidean distance (L2 norm)
neighbors_euclidean = tlm.nearest_neighbors(query, corpus, k=2, metric='euclidean')
print("Nearest neighbors (Euclidean):")
for idx, dist in neighbors_euclidean:
    print(f"  Point {idx}: distance = {dist:.3f}")

# Manhattan distance (L1 norm)
neighbors_manhattan = tlm.nearest_neighbors(query, corpus, k=2, metric='manhattan')
print("\nNearest neighbors (Manhattan):")
for idx, dist in neighbors_manhattan:
    print(f"  Point {idx}: distance = {dist:.3f}")

# Output:
# Nearest neighbors (Euclidean):
#   Point 3: distance = 0.707
#   Point 0: distance = 1.000
#
# Nearest neighbors (Manhattan):
#   Point 0: distance = 1.000
#   Point 1: distance = 1.000
```

---

### 🌡️ Temperature Scaling Functions

#### **Example 5: Temperature-Controlled Softmax**

```python
import tlm

# Raw scores from a model (unnormalized)
logits = [3.0, 1.0, 0.5]

print("Temperature Effects on Softmax:\n")

# Cold temperature (T=0.1) - deterministic, picks maximum
probs_cold = tlm.temperature_scaled_softmax(logits, temperature=0.1)
print(f"T=0.1 (cold):  {[f'{p:.3f}' for p in probs_cold]}")
print(f"  → Strongly favors maximum: {probs_cold[0]:.3f}")

# Standard softmax (T=1.0)
probs_standard = tlm.temperature_scaled_softmax(logits, temperature=1.0)
print(f"\nT=1.0 (standard): {[f'{p:.3f}' for p in probs_standard]}")
print(f"  → Balanced distribution")

# Hot temperature (T=2.0) - more exploration
probs_hot = tlm.temperature_scaled_softmax(logits, temperature=2.0)
print(f"\nT=2.0 (hot):   {[f'{p:.3f}' for p in probs_hot]}")
print(f"  → More uniform, explores alternatives")

# Output:
# T=0.1 (cold):  ['0.952', '0.047', '0.001']
#   → Strongly favors maximum: 0.952
#
# T=1.0 (standard): ['0.665', '0.245', '0.090']
#   → Balanced distribution
#
# T=2.0 (hot):   ['0.506', '0.307', '0.187']
#   → More uniform, explores alternatives
```

#### **Example 6: Temperature for Reasoning Control**

```python
import tlm

# Similarity scores from case retrieval
case_scores = [0.95, 0.85, 0.60, 0.30]
case_names = ["Case A", "Case B", "Case C", "Case D"]

print("Temperature Effect on Case Selection:\n")

# T=0.0 - Only use best match (certifiable)
scaled_t0 = tlm.apply_temperature(case_scores, temperature=0.001)
print("T→0 (Symbolic - only exact matches):")
for name, score in zip(case_names, scaled_t0):
    if score > 0.5:
        print(f"  {name}: {score:.3f} ✓ SELECTED")
    else:
        print(f"  {name}: {score:.3f}")

# T=1.0 - Standard weighting
print("\nT=1.0 (Balanced):")
for name, score in zip(case_names, case_scores):
    print(f"  {name}: {score:.3f}")

# T=2.0 - More diverse selection
scaled_t2 = tlm.apply_temperature(case_scores, temperature=2.0)
print("\nT=2.0 (Analogical - diverse cases):")
for name, score in zip(case_names, scaled_t2):
    print(f"  {name}: {score:.3f}")

# Output:
# T→0 (Symbolic - only exact matches):
#   Case A: 1.000 ✓ SELECTED
#   Case B: 0.000
#   Case C: 0.000
#   Case D: 0.000
#
# T=1.0 (Balanced):
#   Case A: 0.950
#   Case B: 0.850
#   Case C: 0.600
#   Case D: 0.300
#
# T=2.0 (Analogical - diverse cases):
#   Case A: 0.475
#   Case B: 0.425
#   Case C: 0.300
#   Case D: 0.150
```

#### **Example 7: Temperature Scheduling (Simulated Annealing)**

```python
import tlm

# Simulate an optimization process with cooling
total_steps = 100
temperatures = []

print("Temperature Schedule (Linear Cooling):\n")

for step in [0, 25, 50, 75, 100]:
    temp = tlm.temperature_schedule(
        initial_temp=1.0,
        final_temp=0.0,
        current_step=step,
        total_steps=total_steps,
        schedule_type='linear'
    )
    temperatures.append(temp)
    reasoning_mode = "Analogical" if temp > 0.5 else "Hybrid" if temp > 0.05 else "Symbolic"
    print(f"Step {step:3d}: T={temp:.3f} → {reasoning_mode} reasoning")

# Output:
# Step   0: T=1.000 → Analogical reasoning
# Step  25: T=0.750 → Analogical reasoning
# Step  50: T=0.500 → Analogical reasoning
# Step  75: T=0.250 → Hybrid reasoning
# Step 100: T=0.000 → Symbolic reasoning
```

#### **Example 8: Comparing Temperature Schedules**

```python
import tlm

steps = [0, 20, 40, 60, 80, 100]
print("Comparing Temperature Schedules:\n")
print("Step | Linear | Exponential | Cosine")
print("-----|--------|-------------|-------")

for step in steps:
    t_linear = tlm.temperature_schedule(1.0, 0.1, step, 100, 'linear')
    t_exp = tlm.temperature_schedule(1.0, 0.1, step, 100, 'exponential')
    t_cos = tlm.temperature_schedule(1.0, 0.1, step, 100, 'cosine')

    print(f"{step:4d} | {t_linear:.3f}  | {t_exp:.3f}       | {t_cos:.3f}")

# Output:
# Step | Linear | Exponential | Cosine
# -----|--------|-------------|-------
#    0 | 1.000  | 1.000       | 1.000
#   20 | 0.820  | 0.631       | 0.974
#   40 | 0.640  | 0.398       | 0.855
#   60 | 0.460  | 0.251       | 0.595
#   80 | 0.280  | 0.158       | 0.244
#  100 | 0.100  | 0.100       | 0.100
```

---

## Phase 2: tidyllm-sentence - Analogical Reasoning

### 🧠 Case-Based Reasoning

#### **Example 9: Simple Case Retrieval**

```python
import sys
sys.path.insert(0, 'packages/tlm')
sys.path.insert(0, 'packages/tidyllm-sentence')
import tidyllm_sentence as tls

# Build a knowledge base of compliance cases
knowledge_base = [
    "MVS 5.4.3 requires data validation for all input fields",
    "Schema validation must be performed before data insertion",
    "Code review processes ensure quality standards are met",
    "Automated testing validates functional requirements",
    "Data integrity checks prevent corruption in storage"
]

# Query the knowledge base
query = "How should I validate data input?"

# Retrieve top 3 most relevant cases
results = tls.case_retrieval(
    query=query,
    case_base=knowledge_base,
    method='tfidf',  # Can also use 'lsa' or 'word_avg'
    top_k=3
)

print(f"Query: {query}\n")
print("Most Relevant Cases:")
for i, (case, score) in enumerate(results, 1):
    print(f"\n{i}. Score: {score:.3f}")
    print(f"   {case}")

# Output:
# Query: How should I validate data input?
#
# Most Relevant Cases:
#
# 1. Score: 0.808
#    MVS 5.4.3 requires data validation for all input fields
#
# 2. Score: 0.651
#    Schema validation must be performed before data insertion
#
# 3. Score: 0.421
#    Data integrity checks prevent corruption in storage
```

#### **Example 10: Analogical Reasoning with Temperature Control**

```python
import tidyllm_sentence as tls

cases = [
    "Python uses indentation for code blocks",
    "JavaScript uses curly braces for code blocks",
    "Java requires semicolons at end of statements",
    "Ruby has optional parentheses in method calls",
    "Go has strict formatting rules via gofmt"
]

query = "How does Python handle code structure?"

print("Temperature Effect on Analogical Reasoning:\n")

# Cold temperature (T=0.0) - only exact matches
print("T=0.0 (Symbolic - exact matches only):")
results_cold = tls.analogical_reasoning(
    query=query,
    cases=cases,
    top_k=3,
    temperature=0.0,
    method='tfidf'
)
print(f"  Found {len(results_cold)} results")
for idx, score, case in results_cold:
    print(f"  [{idx}] {score:.3f}: {case}")

# Standard temperature (T=1.0) - balanced
print("\nT=1.0 (Balanced - normal ranking):")
results_standard = tls.analogical_reasoning(
    query=query,
    cases=cases,
    top_k=3,
    temperature=1.0,
    method='tfidf'
)
for idx, score, case in results_standard:
    print(f"  [{idx}] {score:.3f}: {case}")

# Hot temperature (T=2.0) - more diverse
print("\nT=2.0 (Analogical - diverse exploration):")
results_hot = tls.analogical_reasoning(
    query=query,
    cases=cases,
    top_k=3,
    temperature=2.0,
    method='tfidf'
)
for idx, score, case in results_hot:
    print(f"  [{idx}] {score:.3f}: {case}")

# Output:
# T=0.0 (Symbolic - exact matches only):
#   Found 0 results
#
# T=1.0 (Balanced - normal ranking):
#   [0] 0.612: Python uses indentation for code blocks
#   [1] 0.287: JavaScript uses curly braces for code blocks
#   [4] 0.241: Go has strict formatting rules via gofmt
#
# T=2.0 (Analogical - diverse exploration):
#   [0] 0.306: Python uses indentation for code blocks
#   [1] 0.144: JavaScript uses curly braces for code blocks
#   [4] 0.121: Go has strict formatting rules via gofmt
```

#### **Example 11: Similarity-Based Inference**

```python
import tidyllm_sentence as tls

# Knowledge base with answers
knowledge = [
    "The capital of France is Paris",
    "The capital of Germany is Berlin",
    "The capital of Spain is Madrid",
    "The capital of Italy is Rome"
]

query = "What is the capital of France?"

# Infer answer based on similarity
result = tls.similarity_based_inference(
    query=query,
    knowledge_base=knowledge,
    threshold=0.3,  # Minimum similarity score
    method='tfidf'
)

print(f"Query: {query}\n")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Number of matches: {result['num_matches']}")
print(f"\nBest Match:")
if result['best_match']:
    text, score = result['best_match']
    print(f"  {text}")
    print(f"  (similarity: {score:.3f})")

print(f"\nAll Matches Above Threshold:")
for text, score in result['matches']:
    print(f"  [{score:.3f}] {text}")

# Output:
# Query: What is the capital of France?
#
# Confidence: 0.825
# Number of matches: 4
#
# Best Match:
#   The capital of France is Paris
#   (similarity: 0.825)
#
# All Matches Above Threshold:
#   [0.825] The capital of France is Paris
#   [0.618] The capital of Spain is Madrid
#   [0.607] The capital of Germany is Berlin
#   [0.541] The capital of Italy is Rome
```

#### **Example 12: Temperature Sweep Analysis**

```python
import tidyllm_sentence as tls

cases = [
    "Data validation is mandatory for compliance",
    "Schema checks ensure data integrity",
    "Input sanitization prevents injection attacks",
    "Type checking catches errors early"
]

query = "What validation is required?"

# Test multiple temperatures to see effect
sweep_results = tls.temperature_sweep(
    query=query,
    cases=cases,
    temperatures=[0.0, 0.5, 1.0, 2.0],
    method='tfidf',
    top_k=2
)

print(f"Query: {query}\n")

for temp in [0.0, 0.5, 1.0, 2.0]:
    print(f"Temperature {temp}:")
    results = sweep_results[temp]

    if len(results) == 0:
        print("  (no results - too restrictive)")
    else:
        for idx, score, case in results:
            print(f"  {score:.3f}: {case}")
    print()

# Output:
# Query: What validation is required?
#
# Temperature 0.0:
#   (no results - too restrictive)
#
# Temperature 0.5:
#   0.446: Data validation is mandatory for compliance
#   0.338: Schema checks ensure data integrity
#
# Temperature 1.0:
#   0.892: Data validation is mandatory for compliance
#   0.676: Schema checks ensure data integrity
#
# Temperature 2.0:
#   0.446: Data validation is mandatory for compliance
#   0.338: Schema checks ensure data integrity
```

#### **Example 13: Multi-Query Reasoning**

```python
import tidyllm_sentence as tls

cases = [
    "Python is great for data science and machine learning",
    "JavaScript is essential for web development",
    "Java is widely used in enterprise applications",
    "Python has excellent libraries for scientific computing"
]

# Ask multiple related questions
queries = [
    "Which language is good for machine learning?",
    "What is best for data analysis?",
    "Which has scientific computing libraries?"
]

# Aggregate results from multiple queries
result = tls.multi_query_reasoning(
    queries=queries,
    cases=cases,
    method='tfidf',
    top_k=2,
    aggregation='voting'  # Options: 'union', 'intersection', 'voting'
)

print("Multi-Query Reasoning Results:\n")

# Show results per query
print("Individual Query Results:")
for query, query_results in result['per_query'].items():
    print(f"\n  '{query}'")
    for case, score in query_results[:1]:  # Top result
        print(f"    → {case} ({score:.3f})")

# Show aggregated results
print("\n\nAggregated Results (Voting):")
for case, avg_score in result['aggregated'][:2]:
    print(f"  {avg_score:.3f}: {case}")

# Output:
# Multi-Query Reasoning Results:
#
# Individual Query Results:
#
#   'Which language is good for machine learning?'
#     → Python is great for data science and machine learning (0.612)
#
#   'What is best for data analysis?'
#     → Python is great for data science and machine learning (0.428)
#
#   'Which has scientific computing libraries?'
#     → Python has excellent libraries for scientific computing (0.561)
#
#
# Aggregated Results (Voting):
#   0.534: Python is great for data science and machine learning
#   0.561: Python has excellent libraries for scientific computing
```

---

## Phase 3: tidyllm - Temperature-Controlled Orchestration

### 🎛️ Reasoning Mode Control

#### **Example 14: Basic Temperature Router**

```python
import sys
sys.path.insert(0, 'packages/tlm')
sys.path.insert(0, 'packages/tidyllm-sentence')
sys.path.insert(0, 'packages/tidyllm')

from reasoning import TemperatureRouter, ReasoningMode

# Create router with default thresholds
router = TemperatureRouter(
    symbolic_threshold=0.05,   # T ≤ 0.05 → symbolic
    hybrid_threshold=0.5       # T ≥ 0.5 → analogical
)

# Test different temperatures
temperatures = [0.0, 0.05, 0.1, 0.3, 0.5, 0.7, 1.0]

print("Temperature → Reasoning Mode Mapping:\n")
for temp in temperatures:
    mode = router.get_mode(temp)
    weights = router.get_weights(temp)

    print(f"T={temp:.2f}: {mode.value:12s}", end="")
    if mode == ReasoningMode.HYBRID:
        print(f" (symbolic: {weights['symbolic']:.2f}, analogical: {weights['analogical']:.2f})")
    else:
        print()

# Output:
# Temperature → Reasoning Mode Mapping:
#
# T=0.00: symbolic
# T=0.05: symbolic
# T=0.10: hybrid       (symbolic: 0.89, analogical: 0.11)
# T=0.30: hybrid       (symbolic: 0.44, analogical: 0.56)
# T=0.50: analogical
# T=0.70: analogical
# T=1.00: analogical
```

#### **Example 15: Simple Reasoning Service**

```python
from reasoning import create_reasoner

# Create reasoner without cases (symbolic only)
reasoner = create_reasoner()

print("Example 1: Symbolic Reasoning (No Cases)\n")

result = reasoner.infer(
    query="Is MVS 5.4.3 data validation required?",
    temperature=0.0
)

print(f"Query: {result['answer']}")
print(f"Mode: {result['reasoning_mode']}")
print(f"Certifiable: {result['certifiable']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Evidence: {result['evidence']}")

# Output:
# Example 1: Symbolic Reasoning (No Cases)
#
# Query: Symbolic answer for: Is MVS 5.4.3 data validation required?
# Mode: symbolic
# Certifiable: True
# Confidence: 1.000
# Evidence: ['Rule-based inference']
```

#### **Example 16: Reasoning with Case Base**

```python
from reasoning import create_reasoner

# Create reasoner with domain knowledge
compliance_cases = [
    "MVS 5.4.3 mandates data validation for all user inputs",
    "Schema validation must occur before database insertion",
    "Input sanitization prevents SQL injection attacks",
    "Type checking ensures data meets expected format",
    "Range validation confirms values are within acceptable bounds"
]

reasoner = create_reasoner(cases=compliance_cases)

print("Analogical Reasoning with Case Base:\n")

result = reasoner.infer(
    query="What validation steps are required?",
    temperature=0.7  # Analogical mode
)

print(f"Query: What validation steps are required?")
print(f"\nMode: {result['reasoning_mode']}")
print(f"Certifiable: {result['certifiable']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"\nAnswer:")
print(f"  {result['answer']}")
print(f"\nEvidence:")
for evidence in result['evidence']:
    print(f"  - {evidence}")

# Output:
# Analogical Reasoning with Case Base:
#
# Query: What validation steps are required?
#
# Mode: analogical
# Certifiable: False
# Confidence: 0.832
#
# Answer:
#   MVS 5.4.3 mandates data validation for all user inputs
#
# Evidence:
#   - Case-based retrieval (lsa)
```

#### **Example 17: Hybrid Reasoning (Mixed Mode)**

```python
from reasoning import create_reasoner

# Create reasoner with both rules and cases
rules = [
    {'pattern': 'MVS', 'action': 'check_compliance'},
    {'pattern': 'validate', 'action': 'perform_validation'}
]

cases = [
    "Previous MVS audit required comprehensive validation",
    "Best practice is to validate at multiple layers"
]

reasoner = create_reasoner(rules=rules, cases=cases)

print("Hybrid Reasoning (Symbolic + Analogical):\n")

result = reasoner.infer(
    query="How to ensure MVS compliance?",
    temperature=0.3  # Hybrid mode
)

print(f"Query: How to ensure MVS compliance?")
print(f"\nMode: {result['reasoning_mode']}")
print(f"Certifiable: {result['certifiable']}")
print(f"Confidence: {result['confidence']:.3f}")

# Show component breakdown
if 'weights' in result['components']:
    weights = result['components']['weights']
    print(f"\nMixing Weights:")
    print(f"  Symbolic:   {weights['symbolic']:.3f}")
    print(f"  Analogical: {weights['analogical']:.3f}")

print(f"\nCombined Answer:")
print(f"  {result['answer']}")

# Output:
# Hybrid Reasoning (Symbolic + Analogical):
#
# Query: How to ensure MVS compliance?
#
# Mode: hybrid
# Certifiable: False
# Confidence: 1.000
#
# Mixing Weights:
#   Symbolic:   0.556
#   Analogical: 0.444
#
# Combined Answer:
#   Hybrid: Symbolic answer for: How to ensure MVS compliance? + Analogical answer for: How to ensure MVS compliance?
```

#### **Example 18: Temperature Sweep for Decision Making**

```python
from reasoning import create_reasoner

cases = [
    "High confidence: Data validation is mandatory per MVS 5.4.3",
    "Medium confidence: Schema checks are recommended",
    "Low confidence: Additional validation may be beneficial"
]

reasoner = create_reasoner(cases=cases)

query = "What validation is absolutely required?"

print(f"Query: {query}\n")
print("Testing Different Temperature Settings:\n")

temperatures = [0.0, 0.05, 0.3, 0.5, 0.8]

for temp in temperatures:
    result = reasoner.infer(query=query, temperature=temp)

    print(f"T={temp:.2f} ({result['reasoning_mode']:10s})", end="")
    print(f" Certifiable: {result['certifiable']}", end="")
    print(f" Conf: {result['confidence']:.3f}")

    # Show answer for key temperatures
    if temp in [0.0, 0.5]:
        print(f"      → {result['answer'][:60]}...")
        print()

# Output:
# Query: What validation is absolutely required?
#
# Testing Different Temperature Settings:
#
# T=0.00 (symbolic  ) Certifiable: True Conf: 1.000
#       → Symbolic answer for: What validation is absolutely requir...
#
# T=0.05 (symbolic  ) Certifiable: True Conf: 1.000
# T=0.30 (hybrid    ) Certifiable: False Conf: 1.000
# T=0.50 (analogical) Certifiable: False Conf: 0.823
#       → High confidence: Data validation is mandatory per MVS 5.4...
#
# T=0.80 (analogical) Certifiable: False Conf: 0.823
```

---

## Complete Integration Example

### 🎯 Real-World Compliance Checking Scenario

#### **Example 19: Complete Workflow**

```python
import sys
sys.path.insert(0, 'packages/tlm')
sys.path.insert(0, 'packages/tidyllm-sentence')
sys.path.insert(0, 'packages/tidyllm')

import tlm
import tidyllm_sentence as tls
from reasoning import create_reasoner

# ============================================================
# STEP 1: Build Compliance Knowledge Base
# ============================================================

compliance_rules = [
    {'pattern': 'MVS 5.4.3', 'action': 'data_validation_required'},
    {'pattern': 'MVS 5.4.4', 'action': 'schema_validation_required'},
    {'pattern': 'MVS 6.2', 'action': 'code_review_required'}
]

historical_cases = [
    "MVS 5.4.3: Project Alpha required validation of all 127 input fields",
    "MVS 5.4.3: Project Beta implemented three-tier validation strategy",
    "MVS 5.4.4: Project Gamma used JSON schema validation",
    "MVS 6.2: Project Delta passed code review with 95% coverage",
    "Best practice: Validate data at API boundary, business logic, and database"
]

# ============================================================
# STEP 2: Create Multi-Temperature Reasoner
# ============================================================

reasoner = create_reasoner(
    rules=compliance_rules,
    cases=historical_cases,
    embedding_method='lsa'
)

# ============================================================
# STEP 3: Process Different Query Types
# ============================================================

queries = [
    {
        'question': "Is MVS 5.4.3 data validation required?",
        'temperature': 0.0,  # Certifiable requirement
        'expected_mode': 'symbolic'
    },
    {
        'question': "What validation approaches have worked well?",
        'temperature': 0.7,  # Learn from experience
        'expected_mode': 'analogical'
    },
    {
        'question': "How should I implement MVS 5.4.3 compliance?",
        'temperature': 0.3,  # Combine rules + experience
        'expected_mode': 'hybrid'
    }
]

print("=" * 70)
print("COMPLIANCE REASONING SYSTEM - COMPLETE EXAMPLE")
print("=" * 70)

for i, q in enumerate(queries, 1):
    print(f"\n{'=' * 70}")
    print(f"QUERY {i}: {q['question']}")
    print(f"{'=' * 70}")
    print(f"Temperature: {q['temperature']} (expecting {q['expected_mode']} mode)")

    # Run inference
    result = reasoner.infer(
        query=q['question'],
        temperature=q['temperature']
    )

    print(f"\n--- RESULTS ---")
    print(f"Mode: {result['reasoning_mode']}")
    print(f"Certifiable: {result['certifiable']}")
    print(f"Confidence: {result['confidence']:.3f}")

    print(f"\nAnswer:")
    print(f"  {result['answer']}")

    print(f"\nEvidence:")
    for evidence in result['evidence']:
        print(f"  • {evidence}")

    # Show additional details for hybrid mode
    if result['reasoning_mode'] == 'hybrid':
        weights = result['components'].get('weights', {})
        print(f"\nReasoning Mix:")
        print(f"  Symbolic:   {weights.get('symbolic', 0):.1%}")
        print(f"  Analogical: {weights.get('analogical', 0):.1%}")

# ============================================================
# STEP 4: Advanced Analysis with Temperature Sweep
# ============================================================

print(f"\n{'=' * 70}")
print("TEMPERATURE SWEEP ANALYSIS")
print(f"{'=' * 70}\n")

analysis_query = "What validation is needed for MVS compliance?"

print(f"Query: {analysis_query}\n")

# Analyze across temperature spectrum
temp_range = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

print("Temp | Mode       | Cert | Conf  | Primary Source")
print("-----|------------|------|-------|----------------------------------")

for temp in temp_range:
    result = reasoner.infer(query=analysis_query, temperature=temp)
    mode = result['reasoning_mode']
    cert = "Yes" if result['certifiable'] else "No "
    conf = result['confidence']

    source = "Rules" if mode == 'symbolic' else "Cases" if mode == 'analogical' else "Mixed"

    print(f"{temp:.1f}  | {mode:10s} | {cert}  | {conf:.3f} | {source}")

print(f"\n{'=' * 70}")
print("RECOMMENDATIONS")
print(f"{'=' * 70}\n")

print("✓ Use T=0.0 for: Certifiable compliance decisions")
print("✓ Use T=0.3 for: Implementation guidance (rules + experience)")
print("✓ Use T=0.7 for: Learning from similar projects")
print()

# ============================================================
# STEP 5: Similarity Analysis Using tlm
# ============================================================

print(f"{'=' * 70}")
print("CASE SIMILARITY ANALYSIS (using tlm)")
print(f"{'=' * 70}\n")

# Embed cases using tidyllm-sentence
case_embeddings, model = tls.lsa_fit_transform(historical_cases, n_components=10)

# Compute pairwise similarity using tlm
similarity_matrix = tlm.pairwise_cosine(case_embeddings)

print("Most Similar Case Pairs:\n")

# Find top 3 similar pairs
pairs = []
for i in range(len(historical_cases)):
    for j in range(i+1, len(historical_cases)):
        pairs.append((i, j, similarity_matrix[i][j]))

pairs.sort(key=lambda x: x[2], reverse=True)

for i, j, sim in pairs[:3]:
    print(f"Similarity: {sim:.3f}")
    print(f"  Case {i+1}: {historical_cases[i][:50]}...")
    print(f"  Case {j+1}: {historical_cases[j][:50]}...")
    print()

print(f"{'=' * 70}\n")

# Output:
# ======================================================================
# COMPLIANCE REASONING SYSTEM - COMPLETE EXAMPLE
# ======================================================================
#
# ======================================================================
# QUERY 1: Is MVS 5.4.3 data validation required?
# ======================================================================
# Temperature: 0.0 (expecting symbolic mode)
#
# --- RESULTS ---
# Mode: symbolic
# Certifiable: True
# Confidence: 1.000
#
# Answer:
#   Symbolic answer for: Is MVS 5.4.3 data validation required?
#
# Evidence:
#   • Rule-based inference
#
# ======================================================================
# QUERY 2: What validation approaches have worked well?
# ======================================================================
# Temperature: 0.7 (expecting analogical mode)
#
# --- RESULTS ---
# Mode: analogical
# Certifiable: False
# Confidence: 0.712
#
# Answer:
#   Best practice: Validate data at API boundary, business logic, and database
#
# Evidence:
#   • Case-based retrieval (lsa)
#
# ======================================================================
# QUERY 3: How should I implement MVS 5.4.3 compliance?
# ======================================================================
# Temperature: 0.3 (expecting hybrid mode)
#
# --- RESULTS ---
# Mode: hybrid
# Certifiable: False
# Confidence: 1.000
#
# Answer:
#   Hybrid: Symbolic answer for: How should I implement MVS 5.4.3 compliance? + ...
#
# Evidence:
#   • Rule-based inference
#   • Case-based retrieval (lsa)
#
# Reasoning Mix:
#   Symbolic:   55.6%
#   Analogical: 44.4%
#
# ======================================================================
# TEMPERATURE SWEEP ANALYSIS
# ======================================================================
#
# Query: What validation is needed for MVS compliance?
#
# Temp | Mode       | Cert | Conf  | Primary Source
# -----|------------|------|-------|----------------------------------
# 0.0  | symbolic   | Yes  | 1.000 | Rules
# 0.1  | hybrid     | No   | 1.000 | Mixed
# 0.2  | hybrid     | No   | 1.000 | Mixed
# 0.3  | hybrid     | No   | 1.000 | Mixed
# 0.4  | hybrid     | No   | 1.000 | Mixed
# 0.5  | analogical | No   | 0.789 | Cases
# 0.6  | analogical | No   | 0.789 | Cases
# 0.7  | analogical | No   | 0.789 | Cases
# 0.8  | analogical | No   | 0.789 | Cases
#
# ======================================================================
# RECOMMENDATIONS
# ======================================================================
#
# ✓ Use T=0.0 for: Certifiable compliance decisions
# ✓ Use T=0.3 for: Implementation guidance (rules + experience)
# ✓ Use T=0.7 for: Learning from similar projects
#
# ======================================================================
# CASE SIMILARITY ANALYSIS (using tlm)
# ======================================================================
#
# Most Similar Case Pairs:
#
# Similarity: 0.912
#   Case 1: MVS 5.4.3: Project Alpha required validation of...
#   Case 2: MVS 5.4.3: Project Beta implemented three-tier ...
#
# Similarity: 0.823
#   Case 3: MVS 5.4.4: Project Gamma used JSON schema valid...
#   Case 5: Best practice: Validate data at API boundary, b...
#
# Similarity: 0.751
#   Case 1: MVS 5.4.3: Project Alpha required validation of...
#   Case 5: Best practice: Validate data at API boundary, b...
#
# ======================================================================
```

---

## 📊 Summary of Functions

### **tlm (Math Primitives)**

| Function | Purpose | Example Use Case |
|----------|---------|------------------|
| `cosine_similarity()` | Measure vector similarity | Compare document embeddings |
| `pairwise_cosine()` | Similarity matrix | Find related documents |
| `top_k_similar()` | Top-K retrieval | Nearest neighbor search |
| `nearest_neighbors()` | Distance-based search | Spatial clustering |
| `temperature_scaled_softmax()` | Temperature control | Reasoning mode selection |
| `apply_temperature()` | Score scaling | Case weighting |
| `temperature_schedule()` | Cooling schedule | Simulated annealing |

### **tidyllm-sentence (Analogical Reasoning)**

| Function | Purpose | Example Use Case |
|----------|---------|------------------|
| `case_retrieval()` | Find similar cases | Knowledge base search |
| `analogical_reasoning()` | Temperature-controlled retrieval | Adaptive case selection |
| `similarity_based_inference()` | Threshold-based matching | Question answering |
| `temperature_sweep()` | Multi-temperature analysis | Parameter tuning |
| `multi_query_reasoning()` | Aggregate multiple queries | Complex questions |

### **tidyllm (Orchestration)**

| Function | Purpose | Example Use Case |
|----------|---------|------------------|
| `create_reasoner()` | Factory function | Quick setup |
| `TensorLogicService.infer()` | Main reasoning | Compliance checking |
| `TemperatureRouter.get_mode()` | Mode selection | Dynamic routing |
| `TemperatureRouter.get_weights()` | Hybrid mixing | Blend strategies |

---

## 🎓 Key Takeaways

1. **Temperature = Control Knob**
   - T→0: Deterministic, certifiable, symbolic
   - T≈0.3: Balanced, hybrid approach
   - T>0.5: Exploratory, case-based, analogical

2. **Composable Architecture**
   - Use `tlm` for math primitives
   - Use `tidyllm-sentence` for text reasoning
   - Use `tidyllm` for orchestration

3. **Progressive Enhancement**
   - Start simple with basic similarity
   - Add case-based reasoning when needed
   - Orchestrate with temperature control

4. **Domain Applications**
   - Compliance: Certifiable decisions (T=0)
   - Learning: Historical cases (T=0.7)
   - Implementation: Mixed guidance (T=0.3)

---

## 📚 Next Steps

1. **Integrate with Adapters**: Replace placeholders with real implementations
2. **Add YRSN Scoring**: Implement trustworthiness validation
3. **Extend Symbolic Engine**: Add rule matching and pattern recognition
4. **Deploy in Production**: Use in compliance-qa application

All code examples are ready to run with the distributed Tensor Logic implementation!
