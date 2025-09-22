"""
Model Router Service
====================

Intelligent model routing based on step kind and performance history.
Routes requests to appropriate Claude model tier based on task complexity.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import logging

from .step_attributes import BaseStep

logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Track performance metrics for a model on specific task kinds."""
    model_name: str
    kind: str
    total_uses: int = 0
    total_reward: float = 0.0
    avg_reward: float = 0.0
    avg_latency: float = 0.0
    success_rate: float = 0.0
    recent_rewards: List[float] = field(default_factory=list)

    def update(self, reward: float, latency: float):
        """Update performance metrics with new execution."""
        self.total_uses += 1
        self.total_reward += reward
        self.avg_reward = self.total_reward / self.total_uses

        # Keep last 20 rewards for recent performance
        self.recent_rewards.append(reward)
        if len(self.recent_rewards) > 20:
            self.recent_rewards.pop(0)

        # Calculate success rate (reward > 0 is success)
        self.success_rate = sum(1 for r in self.recent_rewards if r > 0) / len(self.recent_rewards)

        # Update average latency
        self.avg_latency = (self.avg_latency * (self.total_uses - 1) + latency) / self.total_uses


class ModelRouterService:
    """Routes workflow steps to appropriate models based on kind and performance."""

    # Model tiers with speed/quality tradeoffs
    MODEL_TIERS = {
        "speed": "claude-3-haiku",        # Ultra-fast, basic tasks
        "balanced": "claude-3-sonnet",    # Balanced speed/quality
        "quality": "claude-3-5-sonnet",   # High quality
        "premium": "claude-3-opus"        # Premium quality
    }

    # Default mapping of step kinds to model tiers
    KIND_TO_TIER = {
        # Fast tasks
        "classify": "speed",
        "extract": "speed",
        "notify": "speed",

        # Balanced tasks
        "summarize": "balanced",
        "transform": "balanced",

        # Quality tasks
        "report": "quality",
        "analyze": "quality",
        "generate": "quality",

        # Critical tasks
        "validate": "premium",
        "evaluate": "premium"
    }

    # Task complexity indicators
    COMPLEXITY_INDICATORS = {
        "high": ["complex", "detailed", "comprehensive", "thorough", "critical"],
        "medium": ["standard", "typical", "regular", "normal"],
        "low": ["simple", "basic", "quick", "brief"]
    }

    def __init__(self, project_id: str = None):
        """Initialize the model router."""
        self.project_id = project_id
        self.performance_history: Dict[str, ModelPerformance] = {}
        self.routing_history: List[Dict[str, Any]] = []

        # Load performance history if available
        self._load_performance_history()

    def route_step(self, step: BaseStep) -> str:
        """
        Route a step to the appropriate model based on its characteristics.

        Args:
            step: The workflow step to route

        Returns:
            Model identifier for the step
        """
        # Determine step kind
        kind = self._determine_kind(step)
        step.kind = kind

        # Check for explicit model preference in params
        if step.params and "model" in step.params:
            model = step.params["model"]
            step.last_routed_model = model
            self._record_routing(step, model, "explicit")
            return model

        # Analyze complexity from description and validation rules
        complexity = self._analyze_complexity(step)

        # Get base tier from kind
        base_tier = self.KIND_TO_TIER.get(kind, "balanced")

        # Adjust tier based on complexity
        tier = self._adjust_tier_for_complexity(base_tier, complexity)

        # Check performance history for optimization
        if self.performance_history:
            tier = self._optimize_tier_by_performance(kind, tier)

        # Consider RL feedback if available
        if step.last_reward is not None:
            tier = self._adjust_tier_by_reward(tier, step.last_reward)

        # Get model from tier
        model = self.MODEL_TIERS[tier]

        # Update step tracking
        step.last_routed_model = model
        self._record_routing(step, model, f"auto:{tier}")

        return model

    def update_performance(self, step: BaseStep, reward: float, latency: float):
        """
        Update performance metrics after step execution.

        Args:
            step: The executed step
            reward: RL reward (-1 to 1)
            latency: Execution time in seconds
        """
        if not step.kind or not step.last_routed_model:
            return

        # Create performance key
        perf_key = f"{step.last_routed_model}:{step.kind}"

        # Get or create performance tracker
        if perf_key not in self.performance_history:
            self.performance_history[perf_key] = ModelPerformance(
                model_name=step.last_routed_model,
                kind=step.kind
            )

        # Update metrics
        self.performance_history[perf_key].update(reward, latency)

        # Store in step
        step.last_reward = reward

        # Save performance history
        self._save_performance_history()

    def get_best_model_for_kind(self, kind: str) -> str:
        """Get the best performing model for a specific task kind."""
        best_model = None
        best_score = -float('inf')

        for perf_key, perf in self.performance_history.items():
            if perf.kind == kind:
                # Score combines reward and success rate
                score = perf.avg_reward * 0.7 + perf.success_rate * 0.3
                if score > best_score:
                    best_score = score
                    best_model = perf.model_name

        # Fallback to default if no history
        if not best_model:
            tier = self.KIND_TO_TIER.get(kind, "balanced")
            best_model = self.MODEL_TIERS[tier]

        return best_model

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about model routing."""
        stats = {
            "total_routings": len(self.routing_history),
            "models_used": {},
            "kinds_processed": {},
            "performance_summary": {}
        }

        # Count model usage
        for routing in self.routing_history:
            model = routing.get("model")
            if model:
                stats["models_used"][model] = stats["models_used"].get(model, 0) + 1

            kind = routing.get("kind")
            if kind:
                stats["kinds_processed"][kind] = stats["kinds_processed"].get(kind, 0) + 1

        # Summarize performance
        for perf_key, perf in self.performance_history.items():
            stats["performance_summary"][perf_key] = {
                "uses": perf.total_uses,
                "avg_reward": round(perf.avg_reward, 3),
                "success_rate": round(perf.success_rate, 2),
                "avg_latency": round(perf.avg_latency, 2)
            }

        return stats

    def _determine_kind(self, step: BaseStep) -> str:
        """Determine the kind of step from its attributes."""
        # Check if already set
        if step.kind:
            return step.kind

        # Infer from step_type
        step_type = step.step_type.lower()

        # Common mappings
        kind_mappings = {
            "extraction": "extract",
            "analysis": "analyze",
            "generation": "generate",
            "transform": "transform",
            "validation": "validate",
            "process": "transform",
            "prompt": "generate",
            "ai_interaction": "generate"
        }

        # Check direct mapping
        if step_type in kind_mappings:
            return kind_mappings[step_type]

        # Check description for keywords
        desc_lower = step.description.lower() if step.description else ""

        if "classify" in desc_lower:
            return "classify"
        elif "extract" in desc_lower:
            return "extract"
        elif "summar" in desc_lower:
            return "summarize"
        elif "report" in desc_lower:
            return "report"
        elif "validat" in desc_lower:
            return "validate"
        elif "notif" in desc_lower:
            return "notify"

        # Default to transform
        return "transform"

    def _analyze_complexity(self, step: BaseStep) -> str:
        """Analyze the complexity of a step."""
        complexity_score = 0

        # Check description for complexity indicators
        desc_lower = step.description.lower() if step.description else ""

        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in desc_lower:
                    if level == "high":
                        complexity_score += 2
                    elif level == "low":
                        complexity_score -= 1

        # Check validation rules complexity
        if step.validation_rules:
            rules_count = len(step.validation_rules)
            if rules_count > 5:
                complexity_score += 2
            elif rules_count > 2:
                complexity_score += 1

        # Check number of inputs/outputs
        if len(step.requires) > 3:
            complexity_score += 1
        if len(step.produces) > 3:
            complexity_score += 1

        # Determine complexity level
        if complexity_score >= 3:
            return "high"
        elif complexity_score <= 0:
            return "low"
        else:
            return "medium"

    def _adjust_tier_for_complexity(self, base_tier: str, complexity: str) -> str:
        """Adjust model tier based on complexity."""
        tier_order = ["speed", "balanced", "quality", "premium"]

        try:
            current_idx = tier_order.index(base_tier)
        except ValueError:
            return base_tier

        # Adjust based on complexity
        if complexity == "high" and current_idx < len(tier_order) - 1:
            return tier_order[current_idx + 1]
        elif complexity == "low" and current_idx > 0:
            return tier_order[current_idx - 1]

        return base_tier

    def _optimize_tier_by_performance(self, kind: str, tier: str) -> str:
        """Optimize tier selection based on performance history."""
        # Find best performing model for this kind
        best_model = self.get_best_model_for_kind(kind)

        # Map model back to tier
        for t, model in self.MODEL_TIERS.items():
            if model == best_model:
                return t

        return tier

    def _adjust_tier_by_reward(self, tier: str, last_reward: float) -> str:
        """Adjust tier based on previous reward."""
        tier_order = ["speed", "balanced", "quality", "premium"]

        try:
            current_idx = tier_order.index(tier)
        except ValueError:
            return tier

        # Poor performance -> upgrade tier
        if last_reward < -0.5 and current_idx < len(tier_order) - 1:
            return tier_order[current_idx + 1]
        # Good performance -> can downgrade for efficiency
        elif last_reward > 0.8 and current_idx > 0:
            return tier_order[current_idx - 1]

        return tier

    def _record_routing(self, step: BaseStep, model: str, method: str):
        """Record a routing decision."""
        routing = {
            "timestamp": datetime.now().isoformat(),
            "step_name": step.step_name,
            "kind": step.kind,
            "model": model,
            "method": method,
            "complexity": self._analyze_complexity(step)
        }

        self.routing_history.append(routing)

        # Keep only last 100 routings
        if len(self.routing_history) > 100:
            self.routing_history = self.routing_history[-100:]

    def _load_performance_history(self):
        """Load performance history from storage."""
        if not self.project_id:
            return

        try:
            # Try to load from project directory
            from common.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            history_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "model_performance.json"

            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct ModelPerformance objects
                    for key, perf_data in data.items():
                        self.performance_history[key] = ModelPerformance(**perf_data)
        except Exception as e:
            logger.debug(f"Could not load performance history: {e}")

    def _save_performance_history(self):
        """Save performance history to storage."""
        if not self.project_id:
            return

        try:
            # Save to project directory
            from common.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            history_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "model_performance.json"

            # Convert to serializable format
            data = {}
            for key, perf in self.performance_history.items():
                data[key] = {
                    "model_name": perf.model_name,
                    "kind": perf.kind,
                    "total_uses": perf.total_uses,
                    "total_reward": perf.total_reward,
                    "avg_reward": perf.avg_reward,
                    "avg_latency": perf.avg_latency,
                    "success_rate": perf.success_rate,
                    "recent_rewards": perf.recent_rewards
                }

            # Save to file
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.debug(f"Could not save performance history: {e}")


def get_model_router(project_id: str = None) -> ModelRouterService:
    """Factory function to get a ModelRouterService instance."""
    return ModelRouterService(project_id)