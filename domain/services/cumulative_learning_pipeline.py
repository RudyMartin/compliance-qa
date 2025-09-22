"""
Cumulative Learning Pipeline
============================

Connects DSPy, AI Advisor, RL, and Model Router for compound improvements.
Tracks performance metrics across all components to show trending improvements.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import deque

from .step_attributes import BaseStep
from .model_router_service import ModelRouterService, get_model_router
from .dspy_step_integration import DSPyStepIntegration

logger = logging.getLogger(__name__)


@dataclass
class PerformanceLedger:
    """Tracks cumulative performance metrics across all components."""

    # Execution metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0

    # Performance trends
    avg_latency_trend: deque = field(default_factory=lambda: deque(maxlen=100))
    avg_reward_trend: deque = field(default_factory=lambda: deque(maxlen=100))
    success_rate_trend: deque = field(default_factory=lambda: deque(maxlen=100))

    # DSPy metrics
    total_compilations: int = 0
    signatures_optimized: int = 0
    avg_optimization_improvement: float = 0.0

    # Model routing metrics
    model_upgrades: int = 0
    model_downgrades: int = 0
    routing_accuracy: float = 0.0

    # Token usage
    total_tokens_used: int = 0
    avg_tokens_per_step: float = 0.0
    token_efficiency_trend: deque = field(default_factory=lambda: deque(maxlen=100))

    # Learning metrics
    feedback_collected: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0

    def update_execution(self, latency: float, reward: float, success: bool, tokens: int):
        """Update execution metrics."""
        self.total_executions += 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1

        # Update trends
        self.avg_latency_trend.append(latency)
        self.avg_reward_trend.append(reward)

        # Calculate success rate
        success_rate = self.successful_executions / self.total_executions
        self.success_rate_trend.append(success_rate)

        # Update token metrics
        self.total_tokens_used += tokens
        self.avg_tokens_per_step = self.total_tokens_used / self.total_executions
        self.token_efficiency_trend.append(tokens / max(latency, 0.1))  # tokens per second

    def get_trending_metrics(self) -> Dict[str, Any]:
        """Get trending performance indicators."""
        def calculate_trend(values: deque) -> str:
            if len(values) < 2:
                return "stable"
            recent = list(values)[-10:]
            older = list(values)[-20:-10] if len(values) >= 20 else list(values)[:-10]
            if not older:
                return "stable"

            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            if recent_avg > older_avg * 1.1:
                return "improving ↑"
            elif recent_avg < older_avg * 0.9:
                return "degrading ↓"
            else:
                return "stable →"

        return {
            "latency_trend": calculate_trend(self.avg_latency_trend),
            "reward_trend": calculate_trend(self.avg_reward_trend),
            "success_trend": calculate_trend(self.success_rate_trend),
            "token_efficiency_trend": calculate_trend(self.token_efficiency_trend),
            "current_success_rate": round(self.success_rate_trend[-1], 2) if self.success_rate_trend else 0,
            "avg_recent_latency": round(sum(list(self.avg_latency_trend)[-10:]) / 10, 2) if len(self.avg_latency_trend) >= 10 else 0,
            "avg_recent_reward": round(sum(list(self.avg_reward_trend)[-10:]) / 10, 2) if len(self.avg_reward_trend) >= 10 else 0
        }


class CumulativeLearningPipeline:
    """Orchestrates cumulative learning across DSPy, AI Advisor, RL, and Model Router."""

    def __init__(self, project_id: str):
        """Initialize the cumulative learning pipeline."""
        self.project_id = project_id

        # Initialize components
        self.model_router = get_model_router(project_id)
        self.dspy_integration = DSPyStepIntegration()
        self.ledger = PerformanceLedger()

        # Optimization thresholds
        self.optimization_threshold = 10  # Trigger optimization after N feedbacks
        self.reward_threshold = -0.5     # Trigger model upgrade if reward below
        self.success_threshold = 0.8     # Trigger model downgrade if success above

        # Feedback buffer for batch optimization
        self.feedback_buffer: List[Dict[str, Any]] = []

        # Load existing ledger if available
        self._load_ledger()

    def execute_step_with_learning(self, step: BaseStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a step with full learning pipeline integration.

        Flow:
        1. AI Advisor enhances step (if available)
        2. Model Router selects optimal model
        3. DSPy executes with optimization
        4. Collect metrics and feedback
        5. Trigger optimizations if thresholds met
        """
        start_time = datetime.now()

        # 1. AI Advisor enhancement (if integrated)
        if hasattr(step, 'advisor_notes') and not step.advisor_notes:
            advisor_result = self.dspy_integration.integrate_with_advisor(step)
            if advisor_result['success']:
                step.advisor_notes = str(advisor_result.get('recommendations', ''))

        # 2. Route to optimal model
        model = self.model_router.route_step(step)
        logger.info(f"Routed {step.step_name} ({step.kind}) to {model}")

        # 3. Execute with DSPy integration
        try:
            result = self.dspy_integration.execute_step_with_dspy(step, inputs)
            success = result.get('success', False)

            # Calculate execution metrics
            latency = (datetime.now() - start_time).total_seconds()
            tokens = result.get('tokens_used', 100)  # Default if not tracked

            # Initial reward (will be updated with feedback)
            initial_reward = 0.5 if success else -0.5

            # 4. Update performance metrics
            self.ledger.update_execution(latency, initial_reward, success, tokens)
            self.model_router.update_performance(step, initial_reward, latency)

            # 5. Check for automatic optimizations
            self._check_optimization_triggers(step, initial_reward)

            # Add execution metadata to result
            result['execution_metadata'] = {
                'model_used': model,
                'latency': round(latency, 2),
                'tokens_used': tokens,
                'initial_reward': initial_reward,
                'step_kind': step.kind,
                'optimization_status': 'compiled' if step.dspy_compiled else 'unoptimized'
            }

            # Save ledger after execution
            self._save_ledger()

            return result

        except Exception as e:
            logger.error(f"Error executing step {step.step_name}: {e}")

            # Track failure
            latency = (datetime.now() - start_time).total_seconds()
            self.ledger.update_execution(latency, -1.0, False, 0)

            return {
                'success': False,
                'error': str(e),
                'execution_metadata': {
                    'model_used': model,
                    'latency': round(latency, 2),
                    'step_kind': step.kind
                }
            }

    def collect_feedback(self, step_name: str, rating: int, notes: str = ""):
        """
        Collect user feedback and trigger learning.

        Args:
            step_name: Name of the step
            rating: 1-5 rating (1=terrible, 2=poor, 3=ok, 4=good, 5=excellent)
            notes: Optional feedback notes
        """
        # Convert to reward scale (-1 to 1) - matching RL_DSPy adapter pattern
        # Rating mapping: 1->-1, 2->-0.5, 3->0, 4->0.5, 5->1
        reward = (rating - 3) / 2.0

        # Store feedback
        feedback = {
            'step_name': step_name,
            'rating': rating,
            'reward': reward,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }

        self.feedback_buffer.append(feedback)
        self.ledger.feedback_collected += 1

        if reward > 0:
            self.ledger.positive_feedback += 1
        else:
            self.ledger.negative_feedback += 1

        # Trigger batch optimization if threshold reached
        if len(self.feedback_buffer) >= self.optimization_threshold:
            self._trigger_batch_optimization()

    def _check_optimization_triggers(self, step: BaseStep, reward: float):
        """Check if automatic optimizations should be triggered."""

        # Trigger DSPy compilation if not compiled and poor performance
        if not step.dspy_compiled and reward < self.reward_threshold:
            logger.info(f"Triggering DSPy optimization for {step.step_name}")
            self._optimize_step_with_dspy(step)

        # Trigger model upgrade if consistent poor performance
        if step.last_reward and step.last_reward < self.reward_threshold:
            if reward < self.reward_threshold:  # Two poor performances
                logger.info(f"Poor performance detected, considering model upgrade for {step.step_name}")
                self.model_router._adjust_tier_by_reward("balanced", reward)
                self.ledger.model_upgrades += 1

        # Consider model downgrade if consistent high performance
        if step.last_reward and step.last_reward > self.success_threshold:
            if reward > self.success_threshold:  # Two great performances
                logger.info(f"High performance detected, considering efficiency downgrade for {step.step_name}")
                self.ledger.model_downgrades += 1

    def _trigger_batch_optimization(self):
        """Trigger batch optimization using collected feedback."""
        logger.info(f"Triggering batch optimization with {len(self.feedback_buffer)} feedback items")

        # Convert feedback to DSPy examples
        high_reward_feedback = [f for f in self.feedback_buffer if f['reward'] > 0]

        if high_reward_feedback:
            # Group by step for optimization
            step_feedback = {}
            for feedback in high_reward_feedback:
                step_name = feedback['step_name']
                if step_name not in step_feedback:
                    step_feedback[step_name] = []
                step_feedback[step_name].append(feedback)

            # Optimize each step with its feedback
            for step_name, feedbacks in step_feedback.items():
                logger.info(f"Optimizing {step_name} with {len(feedbacks)} positive examples")
                self.ledger.signatures_optimized += 1

        # Clear feedback buffer
        self.feedback_buffer.clear()
        self.ledger.total_compilations += 1

        # Save updated ledger
        self._save_ledger()

    def _optimize_step_with_dspy(self, step: BaseStep):
        """Optimize a step using DSPy."""
        # Use recent successful executions as examples
        examples = []  # Would be populated from execution history

        result = self.dspy_integration.optimize_step_with_dspy(step, examples)

        if result['success']:
            step.dspy_compiled = True
            step.dspy_metrics = result.get('metrics', {})
            self.ledger.signatures_optimized += 1

    def calculate_step_reward(self, step: BaseStep, result: Dict[str, Any],
                              execution_time: float, success: bool) -> float:
        """
        Calculate reward for a step execution.

        Args:
            step: The executed step
            result: Execution result
            execution_time: Time taken for execution
            success: Whether execution was successful

        Returns:
            Calculated reward value
        """
        # Base reward from success/failure
        base_reward = 0.5 if success else -0.5

        # Latency penalty (normalize to reasonable range)
        latency_penalty = min(execution_time / 5.0, 0.3)  # Max 0.3 penalty for >5s

        # Quality bonus from result
        quality_bonus = 0.0
        if success and 'quality_score' in result:
            quality_bonus = (result['quality_score'] - 0.5) * 0.2  # -0.1 to +0.1

        total_reward = base_reward - latency_penalty + quality_bonus

        # Clamp to [-1, 1] range
        return max(-1.0, min(1.0, total_reward))

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        trends = self.ledger.get_trending_metrics()
        routing_stats = self.model_router.get_routing_stats()

        return {
            "execution_summary": {
                "total": self.ledger.total_executions,
                "successful": self.ledger.successful_executions,
                "failed": self.ledger.failed_executions,
                "success_rate": f"{trends['current_success_rate']*100:.1f}%"
            },
            "performance_trends": {
                "latency": f"{trends['avg_recent_latency']}s {trends['latency_trend']}",
                "reward": f"{trends['avg_recent_reward']} {trends['reward_trend']}",
                "success": f"{trends['current_success_rate']*100:.1f}% {trends['success_trend']}",
                "token_efficiency": trends['token_efficiency_trend']
            },
            "optimization_summary": {
                "compilations": self.ledger.total_compilations,
                "signatures_optimized": self.ledger.signatures_optimized,
                "model_upgrades": self.ledger.model_upgrades,
                "model_downgrades": self.ledger.model_downgrades
            },
            "feedback_summary": {
                "total_collected": self.ledger.feedback_collected,
                "positive": self.ledger.positive_feedback,
                "negative": self.ledger.negative_feedback,
                "satisfaction_rate": f"{(self.ledger.positive_feedback / max(self.ledger.feedback_collected, 1)) * 100:.1f}%"
            },
            "model_routing": routing_stats,
            "token_usage": {
                "total": self.ledger.total_tokens_used,
                "avg_per_step": round(self.ledger.avg_tokens_per_step, 0)
            }
        }

    def _save_ledger(self):
        """Save performance ledger to disk."""
        try:
            from core.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            ledger_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "performance_ledger.json"

            # Convert ledger to serializable format
            ledger_data = {
                "total_executions": self.ledger.total_executions,
                "successful_executions": self.ledger.successful_executions,
                "failed_executions": self.ledger.failed_executions,
                "total_compilations": self.ledger.total_compilations,
                "signatures_optimized": self.ledger.signatures_optimized,
                "model_upgrades": self.ledger.model_upgrades,
                "model_downgrades": self.ledger.model_downgrades,
                "total_tokens_used": self.ledger.total_tokens_used,
                "feedback_collected": self.ledger.feedback_collected,
                "positive_feedback": self.ledger.positive_feedback,
                "negative_feedback": self.ledger.negative_feedback,
                "avg_latency_trend": list(self.ledger.avg_latency_trend),
                "avg_reward_trend": list(self.ledger.avg_reward_trend),
                "success_rate_trend": list(self.ledger.success_rate_trend),
                "token_efficiency_trend": list(self.ledger.token_efficiency_trend)
            }

            ledger_file.parent.mkdir(parents=True, exist_ok=True)
            with open(ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)

        except Exception as e:
            logger.debug(f"Could not save ledger: {e}")

    def _load_ledger(self):
        """Load performance ledger from disk."""
        try:
            from core.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            ledger_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "performance_ledger.json"

            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    data = json.load(f)

                    # Restore basic metrics
                    self.ledger.total_executions = data.get("total_executions", 0)
                    self.ledger.successful_executions = data.get("successful_executions", 0)
                    self.ledger.failed_executions = data.get("failed_executions", 0)
                    self.ledger.total_compilations = data.get("total_compilations", 0)
                    self.ledger.signatures_optimized = data.get("signatures_optimized", 0)
                    self.ledger.model_upgrades = data.get("model_upgrades", 0)
                    self.ledger.model_downgrades = data.get("model_downgrades", 0)
                    self.ledger.total_tokens_used = data.get("total_tokens_used", 0)
                    self.ledger.feedback_collected = data.get("feedback_collected", 0)
                    self.ledger.positive_feedback = data.get("positive_feedback", 0)
                    self.ledger.negative_feedback = data.get("negative_feedback", 0)

                    # Restore trends as deques
                    if "avg_latency_trend" in data:
                        self.ledger.avg_latency_trend = deque(data["avg_latency_trend"], maxlen=100)
                    if "avg_reward_trend" in data:
                        self.ledger.avg_reward_trend = deque(data["avg_reward_trend"], maxlen=100)
                    if "success_rate_trend" in data:
                        self.ledger.success_rate_trend = deque(data["success_rate_trend"], maxlen=100)
                    if "token_efficiency_trend" in data:
                        self.ledger.token_efficiency_trend = deque(data["token_efficiency_trend"], maxlen=100)

        except Exception as e:
            logger.debug(f"Could not load ledger: {e}")


def get_cumulative_pipeline(project_id: str) -> CumulativeLearningPipeline:
    """Factory function to get a CumulativeLearningPipeline instance."""
    return CumulativeLearningPipeline(project_id)