#!/usr/bin/env python3
"""
Workflow Script Generator
=========================
Generates downloadable Python workflow scripts with chat mode combinations.
Uses the 5-stage pattern: OBSERVE, ORIENT, DECIDE, ACT, MONITOR
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class WorkflowScriptGenerator:
    """Generates executable Python workflow scripts from step configurations."""

    def __init__(self):
        self.script_template = self._get_base_template()
        self.step_templates = self._get_step_templates()

    def generate_script(self, workflow_config: Dict[str, Any]) -> str:
        """
        Generate a complete workflow script from configuration.

        Args:
            workflow_config: Dict containing:
                - name: Workflow name
                - description: Workflow description
                - steps: List of step configurations
                - author: Optional author name

        Returns:
            Complete Python script as string
        """
        # Extract configuration
        workflow_name = workflow_config.get('name', 'custom_workflow')
        description = workflow_config.get('description', 'Custom workflow script')
        steps = workflow_config.get('steps', [])
        author = workflow_config.get('author', 'TidyLLM Workflow Builder')

        # Generate header
        header = self._generate_header(workflow_name, description, author)

        # Generate step classes
        step_classes = self._generate_step_classes(steps)

        # Generate pipeline class
        pipeline_class = self._generate_pipeline_class(workflow_name, steps)

        # Generate main function
        main_function = self._generate_main_function(workflow_name)

        # Combine all parts
        script = self.script_template.format(
            header=header,
            step_classes=step_classes,
            pipeline_class=pipeline_class,
            main_function=main_function
        )

        return script

    def _get_base_template(self) -> str:
        """Get the base template for the workflow script."""
        return '''#!/usr/bin/env python3
"""
{header}
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try to import TidyLLM modules
try:
    from common.utilities.path_manager import PathManager
    path_mgr = PathManager()
    for path in path_mgr.get_python_paths():
        if path not in sys.path:
            sys.path.insert(0, path)

    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager
    TIDYLLM_AVAILABLE = True
    print("✓ TidyLLM modules loaded successfully")
except ImportError:
    TIDYLLM_AVAILABLE = False
    print("⚠️ TidyLLM not available - running in mock mode")

# ================================================================================
# BASE WORKFLOW STEP CLASS
# ================================================================================

@dataclass
class BaseWorkflowStep:
    """Base class for all workflow steps with standard attributes."""

    # Core attributes (8 standard fields)
    step_name: str
    step_type: str  # OBSERVE, ORIENT, DECIDE, ACT, MONITOR
    description: str
    requires: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    position: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)

    # Chat configuration
    model: str = "claude-3-haiku"
    temperature: float = 0.7
    mode: str = "direct"
    max_tokens: int = 1000

    # Execution state
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

    def execute(self, context: Dict[str, Any], chat_manager=None) -> Dict[str, Any]:
        """Execute this step with given context."""
        start_time = time.time()
        self.status = "running"

        try:
            # Check dependencies
            for req in self.requires:
                if req not in context:
                    raise ValueError(f"Missing required input: {req}")

            # Execute based on step type
            if self.step_type == "OBSERVE":
                result = self._execute_observe(context, chat_manager)
            elif self.step_type == "ORIENT":
                result = self._execute_orient(context, chat_manager)
            elif self.step_type == "DECIDE":
                result = self._execute_decide(context, chat_manager)
            elif self.step_type == "ACT":
                result = self._execute_act(context, chat_manager)
            elif self.step_type == "MONITOR":
                result = self._execute_monitor(context, chat_manager)
            else:
                result = self._execute_generic(context, chat_manager)

            self.result = result
            self.status = "completed"
            self.execution_time = time.time() - start_time

            # Add produced outputs to context
            for output in self.produces:
                context[output] = result

            return {{
                "success": True,
                "result": result,
                "execution_time": self.execution_time
            }}

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.execution_time = time.time() - start_time
            return {{
                "success": False,
                "error": str(e),
                "execution_time": self.execution_time
            }}

    def _execute_observe(self, context: Dict, chat_manager) -> Any:
        """Execute OBSERVE stage - data gathering."""
        prompt = self.params.get('prompt', f"Observe and gather: {self.description}")
        return self._call_chat(prompt, context, chat_manager)

    def _execute_orient(self, context: Dict, chat_manager) -> Any:
        """Execute ORIENT stage - understanding."""
        prompt = self.params.get('prompt', f"Analyze and understand: {self.description}")
        return self._call_chat(prompt, context, chat_manager)

    def _execute_decide(self, context: Dict, chat_manager) -> Any:
        """Execute DECIDE stage - decision making."""
        prompt = self.params.get('prompt', f"Evaluate and decide: {self.description}")
        return self._call_chat(prompt, context, chat_manager)

    def _execute_act(self, context: Dict, chat_manager) -> Any:
        """Execute ACT stage - taking action."""
        prompt = self.params.get('prompt', f"Execute action: {self.description}")
        return self._call_chat(prompt, context, chat_manager)

    def _execute_monitor(self, context: Dict, chat_manager) -> Any:
        """Execute MONITOR stage - tracking results."""
        prompt = self.params.get('prompt', f"Monitor and validate: {self.description}")
        return self._call_chat(prompt, context, chat_manager)

    def _execute_generic(self, context: Dict, chat_manager) -> Any:
        """Execute generic step."""
        prompt = self.params.get('prompt', self.description)
        return self._call_chat(prompt, context, chat_manager)

    def _call_chat(self, prompt: str, context: Dict, chat_manager) -> str:
        """Call the chat manager with configured settings."""
        if chat_manager and TIDYLLM_AVAILABLE:
            # Use real chat manager
            response = chat_manager.chat(
                message=prompt,
                mode=self.mode,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response
        else:
            # Mock response for testing
            return f"[Mock] Executed {self.step_name}: {prompt[:100]}"

{step_classes}

# ================================================================================
# PIPELINE EXECUTOR
# ================================================================================

{pipeline_class}

# ================================================================================
# MAIN EXECUTION
# ================================================================================

{main_function}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute workflow pipeline")
    parser.add_argument("--input", type=str, help="Input data or file path")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--dry-run", action="store_true", help="Run without executing")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Run the workflow
    success = main(
        input_data=args.input,
        output_path=args.output,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)
'''

    def _get_step_templates(self) -> Dict[str, str]:
        """Get templates for different step types."""
        return {
            'OBSERVE': '''
class {class_name}(BaseWorkflowStep):
    """OBSERVE step: {description}"""

    def __init__(self):
        super().__init__(
            step_name="{step_name}",
            step_type="OBSERVE",
            description="{description}",
            requires={requires},
            produces={produces},
            position={position},
            model="{model}",
            temperature={temperature},
            mode="{mode}",
            max_tokens={max_tokens}
        )
        self.params = {params}
''',
            'ORIENT': '''
class {class_name}(BaseWorkflowStep):
    """ORIENT step: {description}"""

    def __init__(self):
        super().__init__(
            step_name="{step_name}",
            step_type="ORIENT",
            description="{description}",
            requires={requires},
            produces={produces},
            position={position},
            model="{model}",
            temperature={temperature},
            mode="{mode}",
            max_tokens={max_tokens}
        )
        self.params = {params}
''',
            'DECIDE': '''
class {class_name}(BaseWorkflowStep):
    """DECIDE step: {description}"""

    def __init__(self):
        super().__init__(
            step_name="{step_name}",
            step_type="DECIDE",
            description="{description}",
            requires={requires},
            produces={produces},
            position={position},
            model="{model}",
            temperature={temperature},
            mode="{mode}",
            max_tokens={max_tokens}
        )
        self.params = {params}
''',
            'ACT': '''
class {class_name}(BaseWorkflowStep):
    """ACT step: {description}"""

    def __init__(self):
        super().__init__(
            step_name="{step_name}",
            step_type="ACT",
            description="{description}",
            requires={requires},
            produces={produces},
            position={position},
            model="{model}",
            temperature={temperature},
            mode="{mode}",
            max_tokens={max_tokens}
        )
        self.params = {params}
''',
            'MONITOR': '''
class {class_name}(BaseWorkflowStep):
    """MONITOR step: {description}"""

    def __init__(self):
        super().__init__(
            step_name="{step_name}",
            step_type="MONITOR",
            description="{description}",
            requires={requires},
            produces={produces},
            position={position},
            model="{model}",
            temperature={temperature},
            mode="{mode}",
            max_tokens={max_tokens}
        )
        self.params = {params}
'''
        }

    def _generate_header(self, name: str, description: str, author: str) -> str:
        """Generate script header."""
        return f'''================================================================================
FILENAME: {name.lower().replace(' ', '_')}_workflow.py
DATE: {datetime.now().strftime('%Y-%m-%d')}
AUTHOR: {author}
PURPOSE: {description}
================================================================================

This is an auto-generated workflow script from TidyLLM Chat Mode Builder.
It can be run standalone or imported into other Python scripts.

Usage:
    python {name.lower().replace(' ', '_')}_workflow.py --input data.txt --output results.json
================================================================================'''

    def _generate_step_classes(self, steps: List[Dict]) -> str:
        """Generate step class definitions."""
        classes = []

        for i, step in enumerate(steps):
            step_type = step.get('step_type', 'OBSERVE')
            template = self.step_templates.get(step_type, self.step_templates['OBSERVE'])

            # Convert step name to class name
            class_name = ''.join(word.capitalize() for word in step['step_name'].split('_')) + 'Step'

            # Format the template
            class_code = template.format(
                class_name=class_name,
                step_name=step.get('step_name', f'step_{i}'),
                step_type=step_type,
                description=step.get('description', 'Step description'),
                requires=step.get('requires', []),
                produces=step.get('produces', []),
                position=i,
                model=step.get('model', 'claude-3-haiku'),
                temperature=step.get('temperature', 0.7),
                mode=step.get('mode', 'direct'),
                max_tokens=step.get('max_tokens', 1000),
                params=step.get('params', {})
            )

            classes.append(class_code)

        return '\n'.join(classes)

    def _generate_pipeline_class(self, workflow_name: str, steps: List[Dict]) -> str:
        """Generate the pipeline executor class."""

        # Generate step instantiations
        step_instances = []
        for i, step in enumerate(steps):
            class_name = ''.join(word.capitalize() for word in step['step_name'].split('_')) + 'Step'
            step_instances.append(f"            {class_name}(),")

        step_instances_str = '\n'.join(step_instances)

        return f'''class {workflow_name.replace(' ', '')}Pipeline:
    """Pipeline executor for {workflow_name} workflow."""

    def __init__(self):
        self.steps = [
{step_instances_str}
        ]
        self.context = {{}}
        self.chat_manager = None

        if TIDYLLM_AVAILABLE:
            try:
                self.chat_manager = UnifiedChatManager()
                print("✓ Chat manager initialized")
            except Exception as e:
                print(f"⚠️ Could not initialize chat manager: {e}")

    def execute(self, initial_context: Dict = None, verbose: bool = False) -> Dict:
        """Execute the complete pipeline."""
        if initial_context:
            self.context.update(initial_context)

        results = {
            "workflow": "{workflow_name}",
            "started_at": datetime.now().isoformat(),
            "steps": []
        }

        print("\\n" + "="*60)
        print(f"Executing {workflow_name} Pipeline")
        print("="*60)

        for step in self.steps:
            if verbose:
                print(f"\\n▶ Step {step.position + 1}: {step.step_name}")
                print(f"  Type: {step.step_type}")
                print(f"  Model: {step.model} (temp={step.temperature})")

            # Execute the step
            result = step.execute(self.context, self.chat_manager)

            # Record result
            step_result = {
                "step_name": step.step_name,
                "status": step.status,
                "execution_time": step.execution_time,
                "success": result["success"]
            }

            if not result["success"]:
                step_result["error"] = result.get("error")
                print(f"  ❌ Failed: {result.get('error')}")
                results["steps"].append(step_result)
                results["status"] = "failed"
                break
            else:
                if verbose:
                    print(f"  ✓ Completed in {step.execution_time:.2f}s")
                results["steps"].append(step_result)

        results["completed_at"] = datetime.now().isoformat()
        results["status"] = results.get("status", "completed")
        results["final_context"] = self.context

        print("\\n" + "="*60)
        print(f"Pipeline {results['status'].upper()}")
        print("="*60 + "\\n")

        return results

    def save_results(self, results: Dict, output_path: str):
        """Save pipeline results to file."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {output_path}")
'''

    def _generate_main_function(self, workflow_name: str) -> str:
        """Generate the main execution function."""
        return f'''def main(input_data=None, output_path=None, dry_run=False, verbose=False):
    """Main execution function."""

    # Initialize pipeline
    pipeline = {workflow_name.replace(' ', '')}Pipeline()

    # Prepare initial context
    initial_context = {{}}
    if input_data:
        if Path(input_data).exists():
            with open(input_data, 'r') as f:
                initial_context['input'] = f.read()
        else:
            initial_context['input'] = input_data

    if dry_run:
        print("DRY RUN - Pipeline configuration:")
        print(f"Workflow: {workflow_name}")
        print(f"Steps: {len(pipeline.steps)}")
        for step in pipeline.steps:
            print(f"  - {step.step_name} ({step.step_type})")
        return True

    # Execute pipeline
    results = pipeline.execute(initial_context, verbose=verbose)

    # Save results if output path provided
    if output_path:
        pipeline.save_results(results, output_path)

    return results["status"] == "completed"
'''


def generate_workflow_script(config: Dict[str, Any]) -> str:
    """Convenience function to generate a workflow script."""
    generator = WorkflowScriptGenerator()
    return generator.generate_script(config)