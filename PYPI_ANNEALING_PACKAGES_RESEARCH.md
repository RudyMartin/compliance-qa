# PyPI Annealing & Optimization Packages Research

## 🎯 Purpose

Research existing PyPI packages related to annealing/optimization to understand naming conventions, API design patterns, and structural approaches that could inform our Tensor Logic library design.

---

## 📦 Packages Researched

### ✅ Found & Analyzed:
1. **anneal** - Simulated annealing and quenching
2. **simanneal** - Classic simulated annealing
3. **adannealing** - Simulated and quantum annealing
4. **pycsa** - Coupled Simulated Annealing
5. **wildcat** - Annealing for Ising Hamiltonians
6. **mosa** - Multi-Objective Simulated Annealing
7. **frigidum** - Simulated annealing with tqdm

### ❌ Not Found:
- **savprogram** - No package with this name exists on PyPI
- **krug** - No package with this name exists on PyPI
- **PottsPlayground** - Exists on PyPI but page content unavailable (JavaScript load error)

### 🔬 Related (Quantum Annealing):
- **quixotic** - Quantum annealing via D-Wave/Amazon Braket
- **amplify** - SDK for quantum annealing and Ising machines
- **v-quantum-annealing** - Framework for Ising model and QUBO
- **sqaod** - Simulated quantum annealing on CPU/GPU

---

## 🏆 Top 3 Most Relevant Packages

### 1. **simanneal** (Most Popular)

**PyPI:** https://pypi.org/project/simanneal/
**GitHub:** https://github.com/perrygeo/simanneal
**Author:** Matthew Perry (perrygeo)
**License:** BSD
**Latest Version:** 0.5.0 (August 2019)

#### **Naming Strategy:**
- **Pattern:** `simulated annealing` → `simanneal` (abbreviation)
- **Why it works:** Clear, memorable, directly describes what it does
- **Searchability:** Excellent (shows up first in searches)

#### **API Design Pattern:**

**Class-Based Inheritance Model:**
```python
from simanneal import Annealer

class TravellingSalesmanProblem(Annealer):
    """Solve TSP by subclassing Annealer."""

    def __init__(self, state):
        self.distance_matrix = load_distance_matrix()
        super(TravellingSalesmanProblem, self).__init__(state)

    def move(self):
        """Randomly modify self.state (swap two cities)."""
        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """Calculate objective function (total distance)."""
        total = 0
        for i in range(len(self.state)):
            total += self.distance_matrix[self.state[i-1]][self.state[i]]
        return total

# Usage
problem = TravellingSalesmanProblem(initial_state)
problem.Tmax = 25000.0  # Starting temperature
problem.Tmin = 2.5      # Ending temperature
problem.steps = 50000   # Number of iterations

best_state, best_energy = problem.anneal()
```

#### **Key Design Patterns:**

1. **Template Method Pattern:**
   - User implements `move()` and `energy()`
   - Framework handles temperature scheduling, acceptance criteria, state tracking

2. **State Management:**
   - Tracks 3 states: current, previous, best
   - Configurable copy strategies: `deepcopy`, `slice`, `method`

3. **Auto-Calibration:**
   - `auto(minutes=X)` - automatically tunes parameters based on exploration

4. **Configuration:**
```python
# Direct attribute setting
problem.Tmax = 25000.0
problem.Tmin = 2.5
problem.steps = 50000

# Or dictionary-based
problem.set_schedule({
    'tmax': 25000.0,
    'tmin': 2.5,
    'steps': 50000,
    'updates': 100
})
```

#### **Lessons for Tensor Logic:**

✅ **Class-based inheritance is intuitive** for optimization problems
✅ **Template method pattern** works well (framework does scheduling, user implements problem-specific logic)
✅ **Simple parameter configuration** via attributes or dict
✅ **Auto-calibration** is a killer feature
✅ **State tracking** (current/previous/best) is essential

❌ **BUT:** Requires subclassing, which might be overkill for simpler use cases

---

### 2. **frigidum** (Most Flexible)

**PyPI:** https://pypi.org/project/frigidum/
**GitLab:** https://gitlab.com/whendrik/frigidum
**Author:** Willem Hendriks
**License:** MIT
**Python:** ≥3.6

#### **Naming Strategy:**
- **Name:** "Frigidum" (Latin for "cold")
- **Pattern:** Single evocative word (like "Alchemy" for MLN)
- **Why it works:** Memorable, hints at "cold" → temperature → annealing
- **Searchability:** Medium (unique, but not obvious what it does)

#### **API Design Pattern:**

**Function-Based (No Classes Required):**
```python
import frigidum as fr

# Define problem components as functions
def random_start():
    """Generate initial state."""
    return random_solution()

def objective_function(state):
    """Calculate cost/energy."""
    return compute_cost(state)

def neighbour1(state):
    """Coarse neighbor generation."""
    return perturb_large(state)

def neighbour2(state):
    """Fine-grained neighbor generation."""
    return perturb_small(state)

# Run simulated annealing
result = fr.sa(
    random_start=random_start,
    objective_function=objective_function,
    neighbours=[neighbour1, neighbour2],  # Multiple strategies
    T_start=100.0,
    T_stop=0.01,
    alpha=0.95,  # Cooling rate
    repeats=100,  # Iterations per temperature
    copy_state='deepcopy'
)

print(f"Best solution: {result.state}")
print(f"Best energy: {result.energy}")
```

#### **Key Design Patterns:**

1. **Functional Composition:**
   - No classes required
   - Pass functions as parameters
   - Multiple neighbor strategies (randomly selected)

2. **Flat Structure:**
   - All-in-one function call (`fr.sa()`)
   - No inheritance, no boilerplate

3. **Progress Tracking:**
   - Built-in `tqdm` integration
   - Shows temperature, energy, acceptance rate

4. **Post-Processing Hook:**
```python
def post_annealing(state):
    """Refine solution after annealing (e.g., local search)."""
    return refine(state)

result = fr.sa(
    ...,
    post_annealing=post_annealing  # Optional refinement
)
```

5. **Philosophy:**
   - **"Focus on the neighbor function, not the cooling scheme"**
   - Emphasizes problem-specific design (multiple diverse neighbors)
   - Provides examples: Rastrigin, TSP, Knapsack, Graph Coloring

#### **Lessons for Tensor Logic:**

✅ **Function-based API is simpler** for quick usage
✅ **Multiple strategies** (neighbor functions → reasoning modes)
✅ **Progress tracking** is essential for long runs
✅ **Post-processing hooks** for refinement
✅ **Philosophy-driven design** (neighbor function = core)

❌ **BUT:** Less structured than class-based (harder for complex problems)

---

### 3. **anneal** (Most Academic)

**PyPI:** https://pypi.org/project/anneal/
**GitHub:** https://github.com/HaoZeke/anneal
**Author:** Rohit Goswami (rgoswami@ieee.org)
**License:** MIT
**Python:** ≥3.10.1
**Paper:** https://arxiv.org/abs/2302.02811v2

#### **Naming Strategy:**
- **Name:** "anneal" (direct, simple)
- **Pattern:** Single technical verb
- **Why it works:** Shortest possible name, SEO-friendly
- **Searchability:** Excellent (exact match for "annealing")

#### **API Design Pattern:**

**Research-Backed Design:**
- **ArXiV preprint** documents design decisions
- **Multiple algorithms** (annealing + quenching variants)
- **Production-grade tooling:**
  - `pdm` for package management
  - Pre-commit hooks
  - NumPy commit guidelines
  - Automated linting/testing

#### **Development Philosophy:**

```
anneal/
├── anneal/          # Main package
├── tests/           # Test suite
├── docs/source/     # Sphinx docs
├── branding/logo/   # Brand assets
├── .github/workflows/ # CI/CD
├── pyproject.toml   # Poetry/PDM config
└── CHANGELOG.md     # Version history
```

**Contribution Guidelines:**
- `pdm all` before submitting
- NumPy-style commits
- Co-author attribution

#### **Key Design Patterns:**

1. **Multiple Algorithms:**
   - Not just SA, but "various annealing and quenching techniques"
   - Each algorithm is a separate module

2. **Research Credibility:**
   - Academic paper explains design
   - References theory in documentation

3. **Professional Tooling:**
   - Modern Python packaging (pyproject.toml)
   - PDM instead of pip
   - Pre-commit hooks
   - Automated CI/CD

#### **Lessons for Tensor Logic:**

✅ **Academic credibility** matters (cite Domingos papers)
✅ **Multiple variants** in one package (symbolic, hybrid, analogical)
✅ **Professional tooling** from day one
✅ **Clear contribution guidelines**
✅ **Brand identity** (logo, consistent naming)

❌ **BUT:** Requires Python ≥3.10.1 (high barrier)

---

## 🔍 Other Notable Packages

### **adannealing** - Simulated and Quantum Annealing
- **PyPI:** https://pypi.org/project/adannealing/
- **Pattern:** Prefix abbreviation (`ada` + `annealing`)
- **Lesson:** Hybrid classical/quantum annealing in one package

### **pycsa** - Coupled Simulated Annealing
- **PyPI:** https://pypi.org/project/pycsa/
- **Author:** Boudhayan Banerjee, Evan 'Pete' Walsh
- **Pattern:** `py` + acronym (`CSA`)
- **Key Idea:** Multiple SA processes coupled together
- **Lesson:** "Coupled" = calculate acceptance across all m processes

### **wildcat** - Ising Hamiltonian Solver
- **PyPI:** https://pypi.org/project/wildcat/
- **Author:** Shumpei Kobayashi
- **Pattern:** Single evocative word (unrelated to function)
- **Use Case:** Optimization via Ising Hamiltonians
- **Lesson:** Can use metaphorical names (wildcat ≠ annealing)

### **mosa** - Multi-Objective Simulated Annealing
- **PyPI:** https://pypi.org/project/mosa/
- **GitHub:** https://github.com/rgaveiga/mosa
- **Author:** Roberto Veiga (roberto.veiga@ufabc.edu.br)
- **License:** GPL-3.0
- **Pattern:** Acronym (MOSA)
- **Key Feature:** Approximates Pareto front for multi-objective problems
- **Lesson:** Academic contact info + references to papers

---

## 📊 Naming Pattern Analysis

### **Naming Strategies Observed:**

| Package | Pattern | Example | Pros | Cons |
|---------|---------|---------|------|------|
| **simanneal** | Abbreviation | `simulated annealing` → `simanneal` | Clear, searchable | Longer name |
| **anneal** | Direct verb | `anneal` | Shortest, SEO-friendly | Generic |
| **frigidum** | Latin metaphor | "cold" → `frigidum` | Memorable, unique | Obscure |
| **wildcat** | Unrelated word | (evocative) | Unique branding | No hint of function |
| **mosa** | Acronym | Multi-Objective SA → `MOSA` | Compact | Requires explanation |
| **pycsa** | Py + acronym | `py` + `CSA` | Python-specific | Generic prefix |
| **adannealing** | Prefix + word | `ada` + `annealing` | Descriptive | Unclear what "ada" means |

### **Lessons for Tensor Logic Naming:**

#### **Option 1: Direct/Technical (Like `anneal`, `simanneal`)**
```
tidyllm-tensor      (direct reference to Domingos)
tidyllm-reasoning   (describes function)
tidyllm-logic       (simple)
```
✅ Clear, searchable, professional
❌ Generic, no metaphorical depth

#### **Option 2: Metaphorical (Like `frigidum`, `wildcat`)**
```
tidyllm-annealing   (temperature metaphor)
tidyllm-temper      (tempering = controlled heating/cooling)
annealing           (standalone, like frigidum)
```
✅ Memorable, hints at temperature control
❌ Less obvious what it does

#### **Option 3: Academic (Like `anneal` with paper)**
```
tidyllm-domingos    (credits researcher)
tidyllm-softunify   (references "soft unification")
tensor-logic        (literal name from papers)
```
✅ Academic credibility, citable
❌ Obscure to non-academics

---

## 🎨 API Design Pattern Analysis

### **Pattern 1: Class-Based Inheritance (`simanneal`)**

**Pros:**
- ✅ Structured, enforces interface
- ✅ Easy to extend (subclass)
- ✅ State management handled by framework
- ✅ Familiar to OOP developers

**Cons:**
- ❌ Requires subclassing (boilerplate)
- ❌ Overkill for simple problems
- ❌ Less flexible than functional

**Best For:**
- Complex problems with shared structure
- When users need to customize multiple behaviors
- Large-scale systems

**Tensor Logic Fit:**
- ✅ Good for `TensorLogicService` (hexagonal architecture)
- ✅ Adapters already use class-based ports
- ✅ Matches existing compliance-qa architecture

---

### **Pattern 2: Function-Based Composition (`frigidum`)**

**Pros:**
- ✅ No boilerplate, minimal code
- ✅ Flexible (pass functions as parameters)
- ✅ Easy for quick experiments
- ✅ Multiple strategies (neighbor functions)

**Cons:**
- ❌ Less structured (no enforced interface)
- ❌ Harder to manage state
- ❌ Can become messy for complex problems

**Best For:**
- Prototyping, experimentation
- Simple optimization tasks
- Jupyter notebooks, interactive use

**Tensor Logic Fit:**
- ✅ Could offer `infer()` function as convenience
- ✅ Good for examples/tutorials
- ❌ Core service already class-based

---

### **Pattern 3: Hybrid (Both Class and Function)**

**Example:**
```python
# Option 1: Class-based (advanced)
from tidyllm_tensor import TensorLogicService
service = TensorLogicService(...)
result = service.infer(query, context, temperature=0.0)

# Option 2: Function-based (simple)
from tidyllm_tensor import infer
result = infer(query, context, temperature=0.0)  # Uses defaults
```

**Pros:**
- ✅ Best of both worlds
- ✅ Simple API for beginners
- ✅ Advanced API for power users

**Cons:**
- ❌ Maintenance overhead (two APIs)
- ❌ Can confuse users (which to use?)

**Tensor Logic Fit:**
- ✅✅ **BEST APPROACH** for our use case
- ✅ Class-based for compliance-qa integration
- ✅ Function-based for standalone usage

---

## 🛠️ Package Structure Patterns

### **Minimal Structure (`simanneal`):**
```
simanneal/
├── simanneal/
│   ├── __init__.py
│   └── anneal.py       # Single module
├── setup.py
├── README.md
└── LICENSE
```
**Lesson:** Can be extremely simple for focused libraries

---

### **Research-Grade Structure (`anneal`, `mosa`):**
```
anneal/
├── anneal/             # Main package
├── tests/              # Test suite
├── docs/source/        # Sphinx documentation
├── branding/logo/      # Brand assets
├── .github/workflows/  # CI/CD
├── pyproject.toml      # Modern packaging
├── environment.yml     # Conda env
└── CHANGELOG.md        # Version history
```
**Lesson:** Professional packaging from day one

---

### **Our Proposed Structure (Hybrid):**
```
tidyllm-tensor/
├── tidyllm_tensor/
│   ├── __init__.py              # Public API (both class + function)
│   ├── core/                    # Core reasoning engine
│   │   ├── service.py           # TensorLogicService (class-based)
│   │   ├── temperature.py       # TemperatureRouter
│   │   └── inference.py         # InferenceResult
│   ├── ports/                   # Hexagonal architecture
│   │   ├── symbolic.py
│   │   ├── embedding.py
│   │   └── trustworthiness.py
│   ├── adapters/                # Adapter implementations
│   │   ├── symbolic_rules.py
│   │   ├── embedding_similarity.py
│   │   └── yrsn_scorer.py
│   ├── yrsn/                    # YRSN framework
│   │   ├── quality.py
│   │   ├── evidence.py
│   │   └── consistency.py
│   └── factory.py               # Convenience factory
│
├── examples/                    # Usage examples
├── tests/                       # Test suite
├── docs/                        # Documentation
├── pyproject.toml               # Modern packaging
├── README.md
└── LICENSE
```

**Rationale:**
- ✅ Class-based core (like `simanneal`)
- ✅ Convenience factory (like `frigidum`'s functional API)
- ✅ Professional structure (like `anneal`)
- ✅ Hexagonal architecture (unique to our domain)

---

## 🎯 Key Takeaways for Tensor Logic

### **1. Naming Recommendations:**

**Top 3 Choices:**

#### **A. `tidyllm-annealing`** (Temperature Metaphor)
```python
from tidyllm_annealing import TemperatureReasoner
```
- ✅ Evocative (like `frigidum`)
- ✅ Hints at core mechanism (temperature control)
- ✅ Fits TidyLLM ecosystem
- ✅ Searchable (annealing is well-known)
- ❌ Might confuse people expecting optimization algorithms

#### **B. `tidyllm-tensor`** (Academic Reference)
```python
from tidyllm_tensor import TensorLogicService
```
- ✅ References Domingos's work
- ✅ Academic credibility
- ✅ Unique positioning
- ✅ Fits TidyLLM ecosystem
- ❌ "Tensor" might imply TensorFlow

#### **C. `annealing`** (Standalone, Evocative)
```python
from annealing import AdaptiveReasoner
```
- ✅ Shortest, most memorable
- ✅ Perfect metaphor (like `frigidum`)
- ✅ Unique brand identity
- ❌ Breaks TidyLLM naming convention
- ❌ Name already taken by HaoZeke's package

---

### **2. API Design Recommendations:**

**Hybrid Approach (Class + Function):**

#### **Simple API (90% of users):**
```python
from tidyllm_tensor import infer

# One-liner inference
result = infer(
    query="Is document compliant?",
    context={'document': doc},
    temperature=0.0  # Symbolic reasoning
)

print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence}")
print(f"Certifiable: {result.certifiable}")
```

#### **Advanced API (10% of users):**
```python
from tidyllm_tensor import TensorLogicService
from tidyllm_tensor.adapters import (
    SymbolicRulesAdapter,
    EmbeddingSimilarityAdapter,
    YRSNTrustworthinessAdapter
)

# Custom configuration
service = TensorLogicService(
    symbolic_engine=SymbolicRulesAdapter(rules=my_rules),
    embedding_engine=EmbeddingSimilarityAdapter(method='lsa'),
    trustworthiness_scorer=YRSNTrustworthinessAdapter()
)

result = service.infer(query, context, temperature=0.0)
```

---

### **3. Package Structure Recommendations:**

**Core Principles:**
1. ✅ Class-based service (like `simanneal`)
2. ✅ Convenience factory (like `frigidum`)
3. ✅ Professional tooling (like `anneal`)
4. ✅ Hexagonal architecture (ports + adapters)

**Directory Structure:**
```
tidyllm-tensor/
├── tidyllm_tensor/
│   ├── __init__.py              # Public API
│   ├── core/                    # Core engine
│   ├── ports/                   # Interfaces
│   ├── adapters/                # Implementations
│   ├── yrsn/                    # YRSN scoring
│   └── factory.py               # Simple API
├── examples/                    # Usage demos
├── tests/                       # Test suite
├── docs/                        # Documentation
├── pyproject.toml               # Modern packaging
└── README.md
```

---

### **4. Documentation Recommendations:**

**From Research:**
- ✅ **ArXiV paper** (like `anneal`) - cite Domingos
- ✅ **Usage examples** (like `frigidum`) - TSP, Rastrigin equivalents
- ✅ **API reference** (Sphinx docs)
- ✅ **Philosophy section** - "Why temperature control?"
- ✅ **Comparison table** - When to use T=0.0 vs T=0.3 vs T=0.7

**README Hero Section (Inspired by Research):**
```markdown
# 🧠 tidyllm-tensor

**Temperature-Controlled Reasoning for Certifiable Compliance**

Based on Pedro Domingos's Tensor Logic, `tidyllm-tensor` provides
adjustable reasoning modes from pure symbolic logic (certifiable)
to analogical learning (adaptive), with YRSN trustworthiness scoring.

```python
from tidyllm_tensor import infer

# Symbolic reasoning (T=0.0 - certifiable)
result = infer(query="Is document compliant?",
               context={'document': doc},
               temperature=0.0)
```

Part of the TidyLLM ecosystem - transparent, dependency-free AI.
```

---

### **5. Features to Steal:**

#### **From `simanneal`:**
- ✅ Template method pattern (user implements problem-specific logic)
- ✅ State tracking (current/previous/best)
- ✅ Auto-calibration (`auto(minutes=X)`)
- ✅ Multiple copy strategies

#### **From `frigidum`:**
- ✅ Multiple strategies (neighbor functions → reasoning modes)
- ✅ Progress tracking (tqdm integration)
- ✅ Post-processing hooks
- ✅ Philosophy-driven design

#### **From `anneal`:**
- ✅ Research credibility (cite papers)
- ✅ Professional tooling (pyproject.toml, PDM)
- ✅ Contribution guidelines
- ✅ Brand identity

---

## 💡 Final Recommendation

### **Name:** `tidyllm-tensor` or `tidyllm-annealing`

**Why `tidyllm-tensor`:**
- References Domingos directly
- Academic credibility
- Unique in PyPI space
- Fits TidyLLM ecosystem

**Why `tidyllm-annealing`:**
- Perfect temperature metaphor
- Follows pattern of successful packages (`simanneal`, `frigidum`)
- Hints at core mechanism
- More memorable

**Hybrid Naming Approach:**
```python
# Package name: tidyllm-tensor (PyPI, academic)
# Main class: TemperatureReasoner (user-facing, intuitive)
# Factory: create_reasoner() (simple API)

from tidyllm_tensor import TemperatureReasoner  # Class-based
from tidyllm_tensor import infer                # Function-based
```

### **API Pattern:** Hybrid (Class + Function)

**Simple API for 90% of users:**
```python
from tidyllm_tensor import infer
result = infer(query, context, temperature=0.0)
```

**Advanced API for 10% of users:**
```python
from tidyllm_tensor import TensorLogicService
service = TensorLogicService(...)
result = service.infer(query, context, temperature=0.0)
```

### **Package Structure:** Research-Grade + Hexagonal

```
tidyllm-tensor/
├── tidyllm_tensor/          # Main package
│   ├── __init__.py          # Public API (both patterns)
│   ├── core/                # Core engine
│   ├── ports/               # Interfaces
│   ├── adapters/            # Implementations
│   ├── yrsn/                # Scoring
│   └── factory.py           # Simple API
├── examples/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

---

## 🔄 Next Steps

1. **Decide on final name:** `tidyllm-tensor` vs `tidyllm-annealing`
2. **Design public API:** Implement both class-based and function-based
3. **Extract code:** Move from `compliance-qa` to standalone library
4. **Packaging:** Create `pyproject.toml`, `setup.py`
5. **Documentation:** README, API reference, examples
6. **Testing:** Unit tests, integration tests
7. **Publish to PyPI** (optional)

---

**Key Insight from Research:**

> **"Focus on the neighbor function, not the cooling scheme."** - Frigidum

**Applied to Tensor Logic:**

> **"Focus on the reasoning modes (symbolic/analogical), not the temperature scheduling."**

The temperature is a **control parameter**, but the **reasoning strategies** (symbolic rules, embedding similarity, YRSN scoring) are what make it unique.

---

**End of Research Document**
