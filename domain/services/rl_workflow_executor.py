"""
RL-Enhanced Workflow Executor Service
=====================================

Modular service that handles workflow execution with RL optimization.
Separated from the monolithic portal files for better maintainability.

Features:
- Step-by-step RL factor optimization
- Performance tracking and feedback
- Adaptive model routing
- Cumulative learning across executions
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import logging

from .rl_factor_optimizer import RLFactorOptimizer
from .cumulative_learning_pipeline import CumulativeLearningPipeline
from .model_router_service import ModelRouterService
from .step_attributes import BaseStep
from .action_steps_manager import ActionStepsManager
from .prompt_steps_manager import PromptStepsManager
from .ask_ai_steps_manager import AskAIStepsManager

logger = logging.getLogger(__name__)


class RLWorkflowExecutor:
    """RL-enhanced workflow execution service."""

    def __init__(self, project_id: str):
        """Initialize the RL workflow executor."""
        self.project_id = project_id
        self.session_id = f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize RL components
        self.rl_optimizer = RLFactorOptimizer(project_id=project_id)
        self.learning_pipeline = CumulativeLearningPipeline(
            project_id=project_id,
            rl_optimizer=self.rl_optimizer
        )
        self.model_router = ModelRouterService()

        # Initialize step managers
        self.action_manager = ActionStepsManager(project_id)
        self.prompt_manager = PromptStepsManager(project_id)
        self.ask_ai_manager = AskAIStepsManager(project_id)

        # Execution state
        self.workflow_results = {}
        self.step_results = []
        self.performance_metrics = {}

    def execute_workflow_with_rl(
        self,
        workflow: Dict[str, Any],
        uploaded_files: List = None,
        field_values: Dict = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Execute workflow with RL optimization and performance tracking.

        Args:
            workflow: Workflow definition
            uploaded_files: List of uploaded files
            field_values: Form field values
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing execution results and RL metrics
        """
        if uploaded_files is None:
            uploaded_files = []
        if field_values is None:
            field_values = {}

        start_time = datetime.now()

        try:
            # Load and sort workflow steps
            steps_config = self._load_step_configuration(workflow)
            sorted_steps = self._sort_steps_by_number(steps_config)

            if progress_callback:
                progress_callback("🚀 RL-enhanced execution pipeline initialized")

            # Execute each step with RL optimization
            for i, step_config in enumerate(sorted_steps):
                step_result = self._execute_step_with_rl(
                    step_config,
                    uploaded_files,
                    field_values,
                    progress_callback
                )

                # Update progress
                if progress_callback:
                    progress = (i + 1) / len(sorted_steps)
                    progress_callback(
                        f"Step {i+1}/{len(sorted_steps)} completed",
                        progress
                    )

            # Generate final results with RL summary
            execution_time = (datetime.now() - start_time).total_seconds()
            final_results = self._generate_final_results(execution_time)

            if progress_callback:
                progress_callback("✅ Workflow execution completed", 1.0)

            return final_results

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return self._generate_error_results(str(e))

    def _execute_step_with_rl(
        self,
        step_config: Dict[str, Any],
        uploaded_files: List,
        field_values: Dict,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Execute a single step with RL optimization."""
        step_start_time = datetime.now()
        step_id = step_config['step_id']
        step_name = step_config['step_name']
        step_type = step_config['step_type']

        try:
            # Convert to BaseStep for RL integration
            base_step = BaseStep(
                step_name=step_name,
                step_type=step_type,
                description=step_config.get('description', ''),
                requires=step_config.get('requires', []),
                produces=step_config.get('produces', []),
                position=int(step_config.get('order', 0)),
                params=step_config.get('params', {}),
                validation_rules=step_config.get('validation_rules', {}),
                kind=step_config.get('kind', step_type)
            )

            # Get RL-optimized factors
            rl_factors = self.rl_optimizer.optimize_step_factors(
                step_type=step_type,
                historical_data=self.workflow_results,
                context={'project_id': self.project_id, 'session_id': self.session_id}
            )

            if progress_callback:
                progress_callback(
                    f"🧠 RL factors - ε:{rl_factors['epsilon']:.3f}, "
                    f"lr:{rl_factors['learning_rate']:.4f}, "
                    f"T:{rl_factors['temperature']:.2f}"
                )

            # Execute step (placeholder for actual execution)
            # In real implementation, this would call tidyllm.chat or similar
            result = self._simulate_step_execution(step_config, rl_factors)

            # Calculate execution metrics
            step_duration = (datetime.now() - step_start_time).total_seconds()

            # RL feedback for successful execution
            reward = self.learning_pipeline.calculate_step_reward(
                step=base_step,
                result=result,
                execution_time=step_duration,
                success=True
            )

            # Update RL factors with feedback
            self.rl_optimizer.update_with_feedback(
                step_type=step_type,
                reward=reward,
                context={'execution_time': step_duration, 'result_quality': len(str(result))}
            )

            # Update step attributes
            base_step.last_reward = reward
            base_step.last_modified = datetime.now().isoformat()

            # Store results
            self.workflow_results[step_id] = result
            self.step_results.append({
                'step': step_config.get('step_number', 0),
                'name': step_id,
                'type': step_type,
                'status': 'completed',
                'result': result,
                'rl_reward': reward,
                'execution_time': step_duration,
                'rl_factors': rl_factors
            })

            if progress_callback:
                progress_callback(
                    f"✓ Step {step_name} completed (reward: {reward:.3f})"
                )

            return result

        except Exception as e:
            # Handle step failure with RL feedback
            step_duration = (datetime.now() - step_start_time).total_seconds()
            reward = -0.5  # Penalty for failure

            self.rl_optimizer.update_with_feedback(
                step_type=step_type,
                reward=reward,
                context={'execution_time': step_duration, 'error': str(e)}
            )

            self.step_results.append({
                'step': step_config.get('step_number', 0),
                'name': step_id,
                'type': step_type,
                'status': 'failed',
                'error': str(e),
                'rl_reward': reward,
                'execution_time': step_duration
            })

            if progress_callback:
                progress_callback(f"❌ Step {step_name} failed: {e}")

            raise e

    def _simulate_step_execution(self, step_config: Dict, rl_factors: Dict) -> Dict[str, Any]:
        """Simulate step execution (replace with actual execution logic)."""
        return {
            'step_id': step_config['step_id'],
            'step_name': step_config['step_name'],
            'status': 'completed',
            'rl_factors_used': rl_factors,
            'timestamp': datetime.now().isoformat(),
            'simulated_result': f"Executed {step_config['step_name']} with RL optimization"
        }

    def _load_step_configuration(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Load step configuration from workflow definition."""
        # Placeholder - implement based on your workflow structure
        return workflow.get('steps', {})

    def _sort_steps_by_number(self, steps_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort steps by step number."""
        def sort_key(step_config):
            step_num = step_config.get('step_number', '0')
            if isinstance(step_num, str):
                try:
                    return [int(x) for x in step_num.split('.')]
                except:
                    return [999, step_config.get('order', 0)]
            else:
                return [int(step_num), 0]

        return sorted(steps_config.values(), key=sort_key)

    def _generate_final_results(self, execution_time: float) -> Dict[str, Any]:
        """Generate final workflow results with RL summary."""
        try:
            # Get RL performance summaries
            rl_summary = self.rl_optimizer.get_performance_summary()
            learning_summary = self.learning_pipeline.get_cumulative_performance()

            # Calculate success metrics
            successful_steps = len([s for s in self.step_results if s['status'] == 'completed'])
            total_steps = len(self.step_results)
            success_rate = successful_steps / total_steps if total_steps > 0 else 0

            # Generate comprehensive results
            final_results = {
                'session_id': self.session_id,
                'project_id': self.project_id,
                'execution_timestamp': datetime.now().isoformat(),
                'execution_time_seconds': execution_time,
                'workflow_summary': {
                    'total_steps': total_steps,
                    'successful_steps': successful_steps,
                    'success_rate': success_rate,
                    'step_results': self.step_results
                },
                'workflow_results': self.workflow_results,
                'rl_optimization': {
                    'enabled': True,
                    'performance_summary': rl_summary,
                    'learning_summary': learning_summary,
                    'total_optimizations': rl_summary.get('total_optimizations', 0),
                    'average_reward': rl_summary.get('average_reward', 0),
                    'current_epsilon': rl_summary.get('current_epsilon', 0),
                    'current_learning_rate': rl_summary.get('current_learning_rate', 0),
                    'performance_trend': learning_summary.get('trend', 'stable')
                }
            }

            return final_results

        except Exception as e:
            logger.error(f"Failed to generate final results: {e}")
            return self._generate_error_results(f"Results generation failed: {e}")

    def _generate_error_results(self, error_message: str) -> Dict[str, Any]:
        """Generate error results structure."""
        return {
            'session_id': self.session_id,
            'project_id': self.project_id,
            'execution_timestamp': datetime.now().isoformat(),
            'status': 'failed',
            'error': error_message,
            'step_results': self.step_results,
            'rl_optimization': {'enabled': True, 'error': error_message}
        }

    def get_step_managers(self) -> Dict[str, Any]:
        """Get step managers for external use."""
        return {
            'action_manager': self.action_manager,
            'prompt_manager': self.prompt_manager,
            'ask_ai_manager': self.ask_ai_manager
        }

    def get_rl_components(self) -> Dict[str, Any]:
        """Get RL components for external use."""
        return {
            'rl_optimizer': self.rl_optimizer,
            'learning_pipeline': self.learning_pipeline,
            'model_router': self.model_router
        }