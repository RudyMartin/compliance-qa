"""
Step Attributes Definition
==========================

Standard 8-attribute pattern for all workflow steps.
Used by ActionStepsManager, PromptStepsManager, and AskAIStepsManager.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class BaseStep:
    """Base step with 8 standard attributes for all workflow steps."""

    # Core 8 attributes (required fields first)
    step_name: str                              # 1. Unique identifier
    step_type: str                              # 2. Category (process, transform, analyze, etc.)
    description: str                            # 3. Human-readable explanation

    # Core 8 attributes (optional fields with defaults)
    requires: List[str] = field(default_factory=list)    # 4. Input dependencies
    produces: List[str] = field(default_factory=list)    # 5. Output artifacts
    position: int = 0                          # 6. Order in sequence
    params: Dict[str, Any] = field(default_factory=dict)  # 7. Configuration parameters
    validation_rules: Dict[str, Any] = field(default_factory=dict)  # 8. Validation rules

    # Metadata (added automatically)
    last_modified: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    version: str = "1.0.0"

    # DSPy Integration Fields
    dspy_signature: Optional[str] = None        # DSPy signature class name
    dspy_module: Optional[str] = None          # DSPy module class name
    dspy_compiled: bool = False                # Whether DSPy program is compiled
    dspy_metrics: Dict[str, Any] = field(default_factory=dict)  # DSPy optimization metrics

    # Model Routing and Tracking Fields
    kind: Optional[str] = None                  # classify|extract|summarize|report|validate|notify
    last_routed_model: Optional[str] = None     # Last model used for this step
    last_reward: Optional[float] = None         # RL reward from last execution
    advisor_notes: Optional[str] = None         # AI Advisor recommendations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Add timestamp if not set
        if not data['last_modified']:
            data['last_modified'] = datetime.now().isoformat()
        return data

    def validate(self) -> tuple[bool, List[str]]:
        """Validate the step has required attributes."""
        errors = []

        if not self.step_name:
            errors.append("step_name is required")
        if not self.step_type:
            errors.append("step_type is required")
        if not self.description:
            errors.append("description is required")
        if self.position < 0:
            errors.append("position must be non-negative")

        return len(errors) == 0, errors


@dataclass
class ActionStep(BaseStep):
    """Action step with workflow-specific attributes."""

    def __post_init__(self):
        """Set action-specific defaults."""
        # Set default step_type if not already set
        if not self.step_type:
            self.step_type = "process"
        elif self.step_type not in ["process", "transform", "analyze", "output", "validation"]:
            self.step_type = "process"


@dataclass
class PromptStep(BaseStep):
    """Prompt step with template-specific attributes."""

    # Prompt-specific attributes
    template: str = ""                          # The prompt template text
    variables: List[str] = field(default_factory=list)  # Template variables
    category: str = "custom"                    # Prompt category
    examples: List[str] = field(default_factory=list)   # Example outputs


    def __post_init__(self):
        """Extract variables from template if not provided."""
        # Set default step_type if not already set
        if not self.step_type:
            self.step_type = "prompt"

        if self.template and not self.variables:
            import re
            # Extract {variable_name} patterns
            pattern = r'\{([^}]+)\}'
            matches = re.findall(pattern, self.template)
            self.variables = list(set(matches))

    def render(self, values: Dict[str, Any]) -> str:
        """Render the prompt template with values."""
        rendered = self.template
        for var_name, var_value in values.items():
            placeholder = f"{{{var_name}}}"
            rendered = rendered.replace(placeholder, str(var_value))
        return rendered


@dataclass
class AIInteractionStep(BaseStep):
    """AI interaction step with conversation-specific attributes."""

    # AI-specific attributes
    conversation_id: str = ""                   # Conversation reference
    role: str = "assistant"                     # user or assistant
    content: str = ""                           # Message content
    context: Dict[str, Any] = field(default_factory=dict)  # Conversation context
    suggestions: List[Dict] = field(default_factory=list)  # AI suggestions
    confidence_score: float = 0.0               # Confidence in suggestion
    reasoning: str = ""                         # AI's reasoning


    def __post_init__(self):
        """Set default step_type if not already set."""
        if not self.step_type:
            self.step_type = "ai_interaction"

    def add_suggestion(self, suggestion: Dict[str, Any]):
        """Add an AI suggestion to this step."""
        self.suggestions.append({
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat(),
            "confidence": self.confidence_score
        })


# Step type mapping
STEP_TYPES = {
    "action": ActionStep,
    "prompt": PromptStep,
    "ai_interaction": AIInteractionStep
}


def create_step(step_type: str, **kwargs) -> BaseStep:
    """Factory function to create the appropriate step type."""
    step_class = STEP_TYPES.get(step_type, BaseStep)
    return step_class(**kwargs)


def validate_step_sequence(steps: List[BaseStep]) -> tuple[bool, List[str]]:
    """Validate a sequence of steps for dependency consistency."""
    errors = []
    produced_outputs = set()

    for i, step in enumerate(sorted(steps, key=lambda s: s.position)):
        # Check individual step validity
        is_valid, step_errors = step.validate()
        if not is_valid:
            errors.extend([f"Step {i+1} ({step.step_name}): {e}" for e in step_errors])

        # Check dependencies
        for req in step.requires:
            if req not in produced_outputs:
                errors.append(f"Step {i+1} ({step.step_name}) requires '{req}' but it's not produced by previous steps")

        # Add this step's outputs
        produced_outputs.update(step.produces)

    return len(errors) == 0, errors


# Standard step types for each manager
ACTION_STEP_TYPES = ["process", "transform", "analyze", "output", "validation", "aggregation"]
PROMPT_STEP_TYPES = ["extraction", "analysis", "generation", "validation", "custom"]
AI_STEP_TYPES = ["conversation", "suggestion", "learning", "feedback", "evaluation"]