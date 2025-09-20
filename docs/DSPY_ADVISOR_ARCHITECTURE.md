# DSPy Advisor Architecture - Creating New AI Advisors

## How DSPy Fits: The Adapter Pattern

DSPy acts as an **adapter** between business requirements and LLM capabilities:

```
Business Definition (Markdown/YAML)
    ↓ [DSPy Adapter]
Structured AI Program (Signatures + Modules)
    ↓ [Corporate Gateway]
LLM Execution (Claude, GPT, etc.)
```

## Current DSPy Implementation

### 1. **CorporateDSPyLM** - The LLM Adapter
```python
class CorporateDSPyLM(dspy.BaseLM):
    """Adapts DSPy to use corporate LLM gateway instead of OpenAI"""

    def __call__(self, prompt, messages, **kwargs):
        # Converts DSPy format → Corporate Gateway format
        # Routes through MLflow tracking
        # Returns in DSPy expected format
```

### 2. **DSPy Signatures** - Define What AI Does
```python
class WorkflowAdvice(dspy.Signature):
    """Defines inputs and outputs for an advisor"""

    # Inputs (what the advisor needs)
    criteria = dspy.InputField(desc="Workflow rules")
    user_question = dspy.InputField(desc="User's question")

    # Outputs (what the advisor produces)
    advice = dspy.OutputField(desc="Recommendations")
    reasoning = dspy.OutputField(desc="Step-by-step logic")
```

### 3. **DSPy Modules** - How AI Thinks
```python
# Different thinking patterns
advisor = dspy.ChainOfThought(WorkflowAdvice)  # Reasoning chain
advisor = dspy.ReAct(WorkflowAdvice)          # Reason + Act
advisor = dspy.ProgramOfThought(WorkflowAdvice) # Programmatic
```

## Creating New Advisors: The Pattern

### Step 1: Business User Defines in Markdown

```markdown
# Financial Risk Advisor

## Purpose
Assess financial risks in model validation reports

## Inputs
- model_report: The MVR document
- risk_threshold: Acceptable risk level
- regulatory_framework: Which regulations apply

## Process
1. Identify risk factors in the model
2. Quantify each risk's potential impact
3. Check against regulatory requirements
4. Generate mitigation recommendations

## Outputs
- risk_score: Overall risk rating (1-10)
- findings: List of specific risks
- recommendations: How to address each risk
```

### Step 2: DSPy Compiler Converts to Signature

```python
class FinancialRiskAdvisor(dspy.Signature):
    """Auto-generated from markdown"""

    # Inputs from markdown
    model_report = dspy.InputField(desc="The MVR document")
    risk_threshold = dspy.InputField(desc="Acceptable risk level")
    regulatory_framework = dspy.InputField(desc="Which regulations apply")

    # Outputs from markdown
    risk_score = dspy.OutputField(desc="Overall risk rating (1-10)")
    findings = dspy.OutputField(desc="List of specific risks")
    recommendations = dspy.OutputField(desc="How to address each risk")
```

### Step 3: Create Advisor Module

```python
# Automatically select best module based on task
def create_advisor(signature, task_type):
    if task_type == "analysis":
        return dspy.ChainOfThought(signature)
    elif task_type == "action":
        return dspy.ReAct(signature)
    elif task_type == "calculation":
        return dspy.ProgramOfThought(signature)
    else:
        return dspy.Predict(signature)
```

## The Service Layer Architecture

```python
class AdvisorFactory:
    """Creates new advisors from business definitions"""

    def create_from_markdown(self, markdown_def):
        # 1. Parse markdown
        spec = self.parse_markdown(markdown_def)

        # 2. Generate signature class
        signature_class = self.generate_signature(spec)

        # 3. Create DSPy module
        advisor = self.create_module(signature_class, spec.task_type)

        # 4. Configure with corporate gateway
        dspy.configure(lm=CorporateDSPyLM())

        return advisor

    def register_advisor(self, name, advisor):
        """Save for reuse"""
        self.advisor_registry[name] = advisor
```

## Example: Complete Flow for New Advisor

### 1. Business User Request
"I need an advisor that reviews code for security vulnerabilities"

### 2. Generated Markdown Template
```markdown
# Security Code Review Advisor

## Inputs
- code: The code to review
- language: Programming language
- security_standards: OWASP, CWE, etc.

## Analysis Steps
1. Identify potential vulnerabilities
2. Classify by severity
3. Check against security standards
4. Suggest fixes

## Outputs
- vulnerabilities: List of issues found
- severity_scores: Risk level for each
- remediation: How to fix each issue
```

### 3. Automatic DSPy Program
```python
class SecurityReviewSignature(dspy.Signature):
    code = dspy.InputField()
    language = dspy.InputField()
    security_standards = dspy.InputField()

    vulnerabilities = dspy.OutputField()
    severity_scores = dspy.OutputField()
    remediation = dspy.OutputField()

security_advisor = dspy.ChainOfThought(SecurityReviewSignature)
```

### 4. Usage in Application
```python
# Business user can now use their custom advisor
result = security_advisor(
    code=uploaded_code,
    language="python",
    security_standards="OWASP Top 10"
)

print(result.vulnerabilities)
print(result.remediation)
```

## Benefits of DSPy Adapter Pattern

1. **No Coding Required** - Business users define in markdown
2. **Automatic Optimization** - DSPy optimizes prompts
3. **Consistent Interface** - All advisors work the same way
4. **Traceable** - MLflow tracks all advisor executions
5. **Reusable** - Save and share advisors across teams
6. **Testable** - DSPy provides testing frameworks

## Integration Points

### With TidyLLM
- DSPy uses TidyLLM's LLM interfaces
- Leverages RAG for context-aware advisors
- Uses vector search for similar examples

### With Compliance-QA
- Advisors for compliance checking
- MVR document analysis
- Finding classification

### With Infrastructure
- Routes through corporate gateway
- Tracks in MLflow
- Stores in advisor registry

## Creating Domain-Specific Advisor Libraries

```python
# Compliance Advisors
compliance_advisors = {
    "mvr_reviewer": MVRReviewAdvisor(),
    "vst_checker": VSTComplianceAdvisor(),
    "finding_classifier": FindingClassificationAdvisor()
}

# Risk Advisors
risk_advisors = {
    "credit_risk": CreditRiskAdvisor(),
    "market_risk": MarketRiskAdvisor(),
    "operational_risk": OperationalRiskAdvisor()
}

# QA Advisors
qa_advisors = {
    "test_generator": TestGenerationAdvisor(),
    "bug_analyzer": BugAnalysisAdvisor(),
    "code_reviewer": CodeReviewAdvisor()
}
```

## The Power of DSPy as Adapter

DSPy acts as a **universal adapter** that:
1. **Adapts** business language → AI programs
2. **Adapts** different LLMs → consistent interface
3. **Adapts** various tasks → appropriate thinking patterns
4. **Adapts** raw outputs → structured results

This allows business users to create new AI capabilities without programming, while developers get consistent, optimized, and traceable AI components.