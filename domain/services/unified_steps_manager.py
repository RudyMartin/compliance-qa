"""
Unified Steps Manager
====================

Revolutionary step manager that handles both action and prompt phases in a single step.
Each step can contain:
- Action phase: TidyLLM functions, file operations, technical processing
- Prompt phase: AI analysis, insights, structured responses
- Or both phases combined for maximum power

This creates hybrid steps that seamlessly bridge technical operations and AI intelligence.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging

from .base_step_manager import BaseStepsManager
from .step_attributes import BaseStep

# TidyLLM integration
try:
    from packages.tidyllm.services.workflow_rl_optimizer import create_rl_enhanced_step
    TIDYLLM_RL_AVAILABLE = True
except ImportError:
    TIDYLLM_RL_AVAILABLE = False

# TidyLLM function imports
try:
    import packages.tidyllm as tidyllm
    TIDYLLM_AVAILABLE = True
except ImportError:
    TIDYLLM_AVAILABLE = False

logger = logging.getLogger(__name__)


class UnifiedStepsManager(BaseStepsManager):
    """Manages unified steps that can contain both action and prompt phases."""

    def __init__(self, project_id: str, project_path: Path = None):
        """
        Initialize the unified steps manager.

        Args:
            project_id: The workflow/project ID
            project_path: Optional custom project path
        """
        super().__init__(project_id, "steps", project_path)

        # Execution context for step chaining
        self.execution_context = {}
        self.step_outputs = {}

    def execute_step(self, step_config: Dict[str, Any], inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a unified step with both action and prompt phases.

        Args:
            step_config: Step configuration with phases
            inputs: Input data for the step

        Returns:
            Combined results from both phases
        """
        step_name = step_config.get('step_name', 'unnamed_step')
        logger.info(f"Executing unified step: {step_name}")

        results = {
            "step_name": step_name,
            "execution_timestamp": datetime.now().isoformat(),
            "success": True,
            "phases_executed": [],
            "outputs": {}
        }

        try:
            # Execute action phase if present
            if "action" in step_config.get("phases", {}):
                action_result = self._execute_action_phase(
                    step_config["phases"]["action"],
                    inputs or {}
                )
                results["outputs"]["action"] = action_result
                results["phases_executed"].append("action")

                # Merge action outputs into execution context
                self.execution_context.update(action_result.get("variables", {}))

            # Execute prompt phase if present
            if "prompt" in step_config.get("phases", {}):
                # Use action outputs + original inputs for prompt
                prompt_inputs = {**(inputs or {}), **self.execution_context}

                prompt_result = self._execute_prompt_phase(
                    step_config["phases"]["prompt"],
                    prompt_inputs
                )
                results["outputs"]["prompt"] = prompt_result
                results["phases_executed"].append("prompt")

                # Merge prompt outputs into execution context
                self.execution_context.update(prompt_result.get("variables", {}))

            # Store step outputs for next steps
            self.step_outputs[step_name] = results["outputs"]

            # Apply RL enhancement if available
            if TIDYLLM_RL_AVAILABLE:
                enhanced_config = create_rl_enhanced_step(step_config, self.project_id)
                results["rl_enhanced"] = True
                results["rl_factors"] = enhanced_config.get("rl_factors", {})

            return results

        except Exception as e:
            logger.error(f"Error executing step {step_name}: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results

    def _execute_action_phase(self, action_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the action phase of a step.

        Args:
            action_config: Action phase configuration
            inputs: Input variables

        Returns:
            Action phase results
        """
        logger.info("Executing action phase")

        results = {
            "phase": "action",
            "success": True,
            "functions_executed": [],
            "variables": {}
        }

        try:
            # Execute TidyLLM functions
            tidyllm_functions = action_config.get("tidyllm_functions", [])
            for func_config in tidyllm_functions:
                func_result = self._execute_tidyllm_function(func_config, inputs)

                function_name = func_config.get("function")
                results["functions_executed"].append(function_name)

                # Store function output
                output_var = func_config.get("output_variable", f"{function_name}_result")
                results["variables"][output_var] = func_result

            # Execute file operations
            file_operations = action_config.get("file_operations", [])
            for file_op in file_operations:
                file_result = self._execute_file_operation(file_op, inputs)
                results["variables"].update(file_result)

            return results

        except Exception as e:
            logger.error(f"Action phase error: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results

    def _execute_prompt_phase(self, prompt_config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the prompt phase of a step.

        Args:
            prompt_config: Prompt phase configuration
            inputs: Input variables (including action outputs)

        Returns:
            Prompt phase results
        """
        logger.info("Executing prompt phase")

        results = {
            "phase": "prompt",
            "success": True,
            "template_used": "",
            "variables": {}
        }

        try:
            # Load prompt template
            template_file = prompt_config.get("template_file")
            if template_file:
                template_path = self.project_path / "templates" / template_file

                if template_path.exists():
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()

                    results["template_used"] = template_file

                    # Substitute variables in template
                    prompt_text = self._substitute_template_variables(template_content, inputs)

                    # For now, store the processed prompt
                    # In real implementation, this would send to AI service
                    results["variables"]["processed_prompt"] = prompt_text
                    results["variables"]["ai_response"] = self._simulate_ai_response(prompt_text)

                else:
                    raise FileNotFoundError(f"Template file not found: {template_path}")

            return results

        except Exception as e:
            logger.error(f"Prompt phase error: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results

    def _execute_tidyllm_function(self, func_config: Dict[str, Any], inputs: Dict[str, Any]) -> Any:
        """
        Execute a TidyLLM function.

        Args:
            func_config: Function configuration
            inputs: Available variables

        Returns:
            Function result
        """
        function_name = func_config.get("function")
        function_inputs = func_config.get("inputs", [])

        logger.info(f"Executing TidyLLM function: {function_name}")

        if not TIDYLLM_AVAILABLE:
            logger.warning("TidyLLM not available, returning mock result")
            return f"mock_result_for_{function_name}"

        try:
            # Get function inputs from available variables
            func_args = []
            for input_name in function_inputs:
                if input_name in inputs:
                    func_args.append(inputs[input_name])
                else:
                    logger.warning(f"Input {input_name} not found for function {function_name}")

            # Execute the function (simplified - would need proper function mapping)
            if function_name == "extract_text_from_pdf":
                return self._mock_extract_text(func_args[0] if func_args else "sample.pdf")
            elif function_name == "generate_embeddings":
                return self._mock_generate_embeddings(func_args[0] if func_args else "sample text")
            elif function_name == "extract_document_metadata":
                return self._mock_extract_metadata(func_args[0] if func_args else "sample.pdf")
            else:
                return f"executed_{function_name}_with_args_{func_args}"

        except Exception as e:
            logger.error(f"TidyLLM function {function_name} failed: {e}")
            return f"error_executing_{function_name}"

    def _execute_file_operation(self, file_op: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operations like read, write, copy."""
        operation = file_op.get("operation")

        if operation == "read_file":
            file_path = file_op.get("file_path")
            if file_path and Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"file_content": content}

        return {"operation_result": f"executed_{operation}"}

    def _substitute_template_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template using {variable_name} format."""
        processed = template
        for key, value in variables.items():
            processed = processed.replace(f"{{{key}}}", str(value))
        return processed

    def _simulate_ai_response(self, prompt: str) -> str:
        """Simulate AI response for testing purposes."""
        return f"AI analysis of prompt: {prompt[:100]}... [Simulated response for testing]"

    # Mock TidyLLM functions for testing
    def _mock_extract_text(self, file_path: str) -> str:
        return f"Extracted text from {file_path}: Lorem ipsum dolor sit amet, consectetur adipiscing elit..."

    def _mock_generate_embeddings(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3, 0.4, 0.5]  # Mock embedding vector

    def _mock_extract_metadata(self, file_path: str) -> Dict[str, Any]:
        return {
            "filename": file_path,
            "file_size": 1024000,
            "creation_date": "2025-01-14",
            "page_count": 10
        }

    def create_hybrid_step(self, step_name: str,
                          tidyllm_functions: List[Dict[str, Any]] = None,
                          prompt_template: str = None,
                          variables: List[str] = None) -> Dict[str, Any]:
        """
        Create a hybrid step configuration with both action and prompt phases.

        Args:
            step_name: Name of the step
            tidyllm_functions: List of TidyLLM functions to execute
            prompt_template: Template file name for AI prompts
            variables: Variables to pass between phases

        Returns:
            Complete step configuration
        """
        step_config = {
            "step_id": step_name.lower().replace(" ", "_"),
            "step_name": step_name,
            "step_type": "unified",
            "phases": {}
        }

        # Add action phase if TidyLLM functions specified
        if tidyllm_functions:
            step_config["phases"]["action"] = {
                "tidyllm_functions": tidyllm_functions
            }

        # Add prompt phase if template specified
        if prompt_template:
            step_config["phases"]["prompt"] = {
                "template_file": prompt_template,
                "variables": variables or []
            }

        return step_config

    def get_execution_context(self) -> Dict[str, Any]:
        """Get current execution context with all step outputs."""
        return {
            "context": self.execution_context,
            "step_outputs": self.step_outputs
        }

    def reset_execution_context(self):
        """Reset execution context for new workflow run."""
        self.execution_context = {}
        self.step_outputs = {}


def get_unified_steps_manager(project_id: str) -> UnifiedStepsManager:
    """Factory function to get a UnifiedStepsManager instance."""
    return UnifiedStepsManager(project_id)