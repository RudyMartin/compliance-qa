"""
DSPy Step Integration
=====================

Integrates workflow steps with DSPy signatures and modules.
Bridges the gap between our 8-attribute steps and DSPy execution.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# Import our services
from .step_attributes import BaseStep, ActionStep, PromptStep, AIInteractionStep
from .dspy_compiler_service import DSPyCompilerService
from .dspy_execution_service import DSPyExecutionService

# Try to import DSPy
try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


class DSPyStepIntegration:
    """Integrates workflow steps with DSPy infrastructure."""

    def __init__(self):
        self.compiler = DSPyCompilerService()
        self.executor = DSPyExecutionService()
        self.signature_cache = {}

    def step_to_dspy_signature(self, step: BaseStep) -> Optional[str]:
        """
        Convert a workflow step to a DSPy signature class.

        The 8 attributes map to DSPy as follows:
        - step_name -> Signature class name
        - description -> Signature docstring
        - requires -> InputFields
        - produces -> OutputFields
        - params -> Configuration for signature
        - validation_rules -> Field constraints
        """

        if not DSPY_AVAILABLE:
            return None

        # Generate signature class name
        class_name = f"{self._to_class_name(step.step_name)}Signature"

        # Build input fields from requires
        input_fields = []
        for req in step.requires:
            field_name = self._to_field_name(req)
            field_desc = f"Input data: {req}"
            input_fields.append(f"    {field_name} = dspy.InputField(desc=\"{field_desc}\")")

        # Build output fields from produces
        output_fields = []
        for prod in step.produces:
            field_name = self._to_field_name(prod)
            field_desc = f"Output data: {prod}"
            output_fields.append(f"    {field_name} = dspy.OutputField(desc=\"{field_desc}\")")

        # Generate signature code
        signature_code = f'''
class {class_name}(dspy.Signature):
    """{step.description}"""

{chr(10).join(input_fields)}

{chr(10).join(output_fields)}
'''

        # Cache and return
        self.signature_cache[step.step_name] = signature_code
        return signature_code

    def step_to_dspy_module(self, step: BaseStep) -> Optional[str]:
        """
        Convert a workflow step to a DSPy module.

        Modules handle the execution logic using signatures.
        """

        if not DSPY_AVAILABLE:
            return None

        # First generate the signature
        signature_code = self.step_to_dspy_signature(step)
        if not signature_code:
            return None

        class_name = f"{self._to_class_name(step.step_name)}Module"
        signature_name = f"{self._to_class_name(step.step_name)}Signature"

        # Choose predictor based on step type
        predictor = self._get_predictor_for_step_type(step.step_type)

        module_code = f'''
{signature_code}

class {class_name}(dspy.Module):
    """DSPy module for {step.step_name}"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.{predictor}({signature_name})

    def forward(self, **kwargs):
        """Execute the step with given inputs."""
        return self.predictor(**kwargs)
'''

        return module_code

    def execute_step_with_dspy(self, step: BaseStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow step using DSPy.

        This bridges our 8-attribute steps with DSPy execution.
        """

        # Generate DSPy program
        dspy_code = self.step_to_dspy_module(step)

        # Map step's requires to input data
        dspy_inputs = {}
        for req in step.requires:
            field_name = self._to_field_name(req)
            if req in inputs:
                dspy_inputs[field_name] = inputs[req]

        # Add params as configuration
        if step.params:
            dspy_inputs['config'] = step.params

        # Execute through DSPy executor
        result = self.executor.execute(dspy_code, dspy_inputs)

        # Map outputs back to step's produces
        outputs = {}
        for prod in step.produces:
            field_name = self._to_field_name(prod)
            if field_name in result.get('outputs', {}):
                outputs[prod] = result['outputs'][field_name]

        return {
            'success': result.get('success', False),
            'outputs': outputs,
            'execution_time': result.get('execution_time', 0),
            'dspy_metrics': result.get('metrics', {})
        }

    def optimize_step_with_dspy(self, step: BaseStep, examples: List[Dict]) -> Dict[str, Any]:
        """
        Optimize a step using DSPy's optimization capabilities.

        Uses examples to improve the step's performance.
        """

        if not DSPY_AVAILABLE:
            return {'success': False, 'error': 'DSPy not available'}

        try:
            # Generate module
            module_code = self.step_to_dspy_module(step)

            # Create optimizer based on step type
            if step.step_type in ['extraction', 'analysis']:
                optimizer = dspy.BootstrapFewShot(metric=self._accuracy_metric)
            else:
                optimizer = dspy.MIPRO(metric=self._quality_metric)

            # Compile with examples
            compiled_module = optimizer.compile(
                module_code,
                trainset=examples[:int(len(examples)*0.8)],
                valset=examples[int(len(examples)*0.8):]
            )

            # Store optimization metrics
            step.dspy_compiled = True
            step.dspy_metrics = {
                'optimization_method': optimizer.__class__.__name__,
                'training_examples': len(examples),
                'validation_score': compiled_module.score
            }

            return {
                'success': True,
                'compiled_module': compiled_module,
                'metrics': step.dspy_metrics
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def integrate_with_advisor(self, step: BaseStep) -> Dict[str, Any]:
        """
        Integrate step with the AI Advisor for recommendations.
        """

        try:
            from domain.workflows.ai_advisor.workflow_advisor import WorkflowAIAdvisor

            advisor = WorkflowAIAdvisor()

            # Prepare context for advisor
            context = {
                'step_definition': step.to_dict(),
                'dspy_signature': step.dspy_signature,
                'validation_rules': step.validation_rules,
                'params': step.params
            }

            # Get advisor recommendations
            advice = advisor.get_workflow_advice(
                criteria={'step_type': step.step_type},
                template_fields={'step': step.step_name},
                recent_activity=[],
                final_results={},
                user_question=f"How can I optimize this {step.step_type} step?"
            )

            return {
                'success': True,
                'recommendations': advice
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _to_class_name(self, name: str) -> str:
        """Convert step name to valid Python class name."""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_field_name(self, name: str) -> str:
        """Convert field name to valid Python variable name."""
        return name.lower().replace(' ', '_').replace('-', '_')

    def _get_predictor_for_step_type(self, step_type: str) -> str:
        """Get appropriate DSPy predictor for step type."""
        predictors = {
            'extraction': 'ChainOfThought',
            'analysis': 'ChainOfThought',
            'generation': 'Predict',
            'transform': 'Predict',
            'validation': 'ReAct',
            'process': 'Predict'
        }
        return predictors.get(step_type, 'Predict')

    def _accuracy_metric(self, example, prediction):
        """Accuracy metric for DSPy optimization."""
        # Simple accuracy based on output presence
        return len(prediction.outputs) > 0

    def _quality_metric(self, example, prediction):
        """Quality metric for DSPy optimization."""
        # Quality based on validation rules
        return all(prediction.validation_results.values()) if hasattr(prediction, 'validation_results') else True


# Integration functions for step managers
def enhance_action_step_with_dspy(action_step: ActionStep) -> ActionStep:
    """Enhance an action step with DSPy capabilities."""
    integrator = DSPyStepIntegration()

    # Generate DSPy signature
    signature = integrator.step_to_dspy_signature(action_step)
    if signature:
        action_step.dspy_signature = signature

    # Generate DSPy module
    module = integrator.step_to_dspy_module(action_step)
    if module:
        action_step.dspy_module = module

    return action_step


def enhance_prompt_step_with_dspy(prompt_step: PromptStep) -> PromptStep:
    """Enhance a prompt step with DSPy capabilities."""
    integrator = DSPyStepIntegration()

    # Prompts are naturally DSPy signatures
    # Convert template to DSPy format
    prompt_step.dspy_signature = f"""
class {integrator._to_class_name(prompt_step.step_name)}Prompt(dspy.Signature):
    \"\"\"{prompt_step.description}\"\"\"

    # Template variables become input fields
    {chr(10).join([f"    {var} = dspy.InputField()" for var in prompt_step.variables])}

    # Produces become output fields
    {chr(10).join([f"    {integrator._to_field_name(prod)} = dspy.OutputField()" for prod in prompt_step.produces])}
"""

    return prompt_step


def integrate_workflow_with_dspy(steps: List[BaseStep]) -> Dict[str, Any]:
    """Integrate an entire workflow with DSPy."""
    integrator = DSPyStepIntegration()

    enhanced_steps = []
    for step in steps:
        if isinstance(step, ActionStep):
            enhanced = enhance_action_step_with_dspy(step)
        elif isinstance(step, PromptStep):
            enhanced = enhance_prompt_step_with_dspy(step)
        else:
            enhanced = step

        enhanced_steps.append(enhanced)

    # Generate complete DSPy program
    program = {
        'signatures': [s.dspy_signature for s in enhanced_steps if s.dspy_signature],
        'modules': [s.dspy_module for s in enhanced_steps if s.dspy_module],
        'execution_order': [s.step_name for s in sorted(enhanced_steps, key=lambda x: x.position)]
    }

    return {
        'success': True,
        'enhanced_steps': enhanced_steps,
        'dspy_program': program
    }