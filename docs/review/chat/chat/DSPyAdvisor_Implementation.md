# DSPyAdvisor Implementation Documentation

## Overview
DSPyAdvisor is a specialized DSPy service created for AI-powered workflow advice in the TidyLLM Flow Creator. It was implemented as a separate service to avoid breaking existing DSPyService functionality while providing workflow-specific AI guidance.

## Problem Solved
The original AI Advisor in the Flow Creator was experiencing multiple issues:
- DSPy threading errors: "dspy.settings can only be changed by the thread that initially configured it"
- KeyError on 'use_cases' parameter mismatches
- Broken workflow_advisor.py import and configuration conflicts
- Missing MLflow integration for audit logging

## Architecture

### Core Service: `tidyllm/services/dspy_advisor.py`

**Key Components:**
1. **WorkflowAdvice Signature** - Custom DSPy signature for structured workflow advice
2. **DSPyAdvisor Class** - Main service with corporate gateway integration
3. **Gateway Hook** - Uses existing `CorporateDSPyLM` pattern for MLflow logging

### Gateway Integration Pattern
```python
# Same pattern as DSPyService
corporate_lm = CorporateDSPyLM(model_name=model_name)
dspy.configure(lm=corporate_lm)
```

This ensures:
- MLflow activity reporting
- AWS Bedrock integration through CorporateLLMGateway
- Audit trails and experiment tracking
- No new gateway creation required

## DSPy Signature Definition

```python
class WorkflowAdvice(dspy.Signature):
    """DSPy signature for workflow advice generation."""

    criteria = dspy.InputField(desc="Workflow criteria and validation rules as JSON")
    template_fields = dspy.InputField(desc="Template field configuration as JSON")
    recent_activity = dspy.InputField(desc="Recent workflow execution data as JSON")
    final_results = dspy.InputField(desc="Latest workflow results as JSON")
    user_question = dspy.InputField(desc="User's specific question about the workflow")
    use_cases = dspy.InputField(desc="Workflow use cases and context")

    reasoning = dspy.OutputField(desc="Step-by-step analysis of the workflow situation")
    advice = dspy.OutputField(desc="Detailed advice with specific recommendations")
    context_analyzed = dspy.OutputField(desc="Summary of context data analyzed as JSON")
```

## Key Features

### 1. Chain of Thought Reasoning
- Uses `dspy.ChainOfThought(WorkflowAdvice)` for structured reasoning
- Provides step-by-step analysis in the `reasoning` field
- Gives specific, actionable advice in the `advice` field

### 2. Robust Error Handling
- Fallback advice generation when DSPy fails
- Context-aware responses based on question type
- Graceful degradation with helpful static advice

### 3. Context Integration
- Analyzes workflow criteria, template fields, recent activity, and results
- Provides context summary showing what data was analyzed
- Adapts advice based on workflow type and use cases

### 4. Thread Safety
- Avoids DSPy threading issues by using global configuration
- Single advisor instance pattern prevents configuration conflicts
- Compatible with Streamlit's threading model

## Integration Points

### AI Advisor Tab: `tidyllm/portals/flow/t_ai_advisor.py`

**Before (Broken):**
```python
from workflow_advisor import workflow_advisor  # Import errors
advice_result = workflow_advisor.get_workflow_advice(...)  # Threading issues
```

**After (Working):**
```python
from tidyllm.services.dspy_advisor import get_advisor
advisor = get_advisor(model_name="claude-3-sonnet")
advice_result = advisor.get_workflow_advice(...)  # Gateway integration
```

## Response Format

**Successful Response:**
```json
{
    "success": true,
    "advice": "Detailed workflow advice with recommendations...",
    "reasoning": "Step-by-step analysis of the workflow situation...",
    "context_analyzed": {
        "criteria_provided": true,
        "fields_analyzed": 8,
        "recent_executions": 3,
        "results_available": true,
        "use_cases_count": 2
    },
    "model_used": "claude-3-sonnet"
}
```

**Fallback Response:**
```json
{
    "success": false,
    "advice": "Fallback advice based on question type...",
    "error": "Error description",
    "fallback": true
}
```

## Testing

The DSPyAdvisor can be tested using existing patterns in `tidyllm/review/chat/tests/`:

```python
# Test DSPy integration
response = tidyllm.chat("How can I optimize my workflow?", chat_type="dspy", reasoning=True)

# Direct advisor testing
from tidyllm.services.dspy_advisor import get_advisor
advisor = get_advisor()
result = advisor.get_workflow_advice(
    user_question="What are best practices for template fields?",
    use_cases=["document processing", "quality assurance"]
)
```

## Benefits Over Previous Implementation

1. **No Breaking Changes** - DSPyService remains untouched
2. **Gateway Integration** - Full MLflow logging and audit trails
3. **Workflow-Specific** - Custom signature designed for workflow advice
4. **Experimentation Freedom** - Separate service allows safe feature development
5. **Robust Fallbacks** - Works even when DSPy fails
6. **Thread Safe** - Resolves Streamlit threading issues

## Future Enhancements

1. **Custom Use Case Signatures** - Specialized signatures for different workflow types
2. **Advanced Context Analysis** - Deeper integration with workflow execution data
3. **Performance Optimization** - Caching and response time improvements
4. **Multi-Model Support** - Support for different LLM models based on question type

## Dependencies

- `dspy` - Framework for prompt engineering
- `tidyllm.services.corporate_dspy_lm` - Corporate gateway adapter
- `json` - Data serialization
- `pathlib` - File path handling
- `logging` - Error and debug logging

## Deployment Notes

- Service is automatically available through the existing Flow Creator interface
- No additional configuration required beyond existing TidyLLM setup
- MLflow logging inherits existing corporate gateway configuration
- Compatible with all existing workflow types and templates