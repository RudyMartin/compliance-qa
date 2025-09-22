"""
RL Factor Optimizer
===================

Optimizes reinforcement learning hyperparameters for maximum cumulative effect.
Manages exploration/exploitation, learning rates, discount factors, and temperature.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from collections import deque
import random
import math


# TLM: Teaching Library Math (numpy-free) - Pure Python implementations
class TLM:
    """Teaching Library Math - NumPy-like functions using pure Python."""

    @staticmethod
    def mean(values: List[float]) -> float:
        """Calculate mean of values."""
        return sum(values) / len(values) if values else 0

    @staticmethod
    def variance(values: List[float]) -> float:
        """Calculate variance of values."""
        if len(values) < 2:
            return 0
        mean_val = TLM.mean(values)
        return sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)

    @staticmethod
    def sum(values: List[float]) -> float:
        """Sum of values."""
        return sum(values)

    @staticmethod
    def max(values: List[float]) -> float:
        """Maximum value."""
        return max(values) if values else 0

    @staticmethod
    def min(values: List[float]) -> float:
        """Minimum value."""
        return min(values) if values else 0

    @staticmethod
    def clip(value: float, min_val: float, max_val: float) -> float:
        """Clip value to range."""
        return max(min_val, min(max_val, value))

    @staticmethod
    def correlation(x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0

        n = len(x)
        mean_x = TLM.mean(x)
        mean_y = TLM.mean(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))

        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        return numerator / denominator if denominator > 0 else 0

    @staticmethod
    def choice_weighted(items: List[Any], weights: List[float], k: int = 1) -> List[Any]:
        """Weighted random choice."""
        if not items or not weights:
            return []

        total = sum(weights)
        normalized = [w / total for w in weights]

        result = []
        for _ in range(k):
            r = random.random()
            cumsum = 0
            for i, prob in enumerate(normalized):
                cumsum += prob
                if r <= cumsum:
                    result.append(items[i])
                    break
        return result

    @staticmethod
    def sample(items: List[Any], k: int) -> List[int]:
        """Random sample without replacement."""
        return random.sample(list(items), min(k, len(items)))


# Use our TLM implementation
tlm = TLM()

logger = logging.getLogger(__name__)


@dataclass
class RLFactors:
    """Core RL hyperparameters that affect learning."""

    # Exploration vs Exploitation
    epsilon: float = 0.1                # Exploration rate (0=exploit, 1=explore)
    epsilon_decay: float = 0.995        # How fast to reduce exploration
    epsilon_min: float = 0.01           # Minimum exploration rate

    # Learning Parameters
    learning_rate: float = 0.01         # Alpha - how fast to update Q-values
    learning_decay: float = 0.999       # How fast to reduce learning rate
    learning_min: float = 0.001         # Minimum learning rate

    # Reward Processing
    discount_factor: float = 0.95       # Gamma - future reward importance
    reward_smoothing: float = 0.1       # Exponential smoothing for rewards
    reward_clipping: float = 2.0        # Clip rewards to [-2, 2] for stability

    # Temperature (for softmax action selection)
    temperature: float = 1.0            # Higher = more random, lower = more deterministic
    temperature_decay: float = 0.99     # Cool down over time
    temperature_min: float = 0.1        # Minimum temperature

    # Feedback Factors
    feedback_weight: float = 1.0        # Weight of user feedback in reward
    implicit_weight: float = 0.5        # Weight of implicit signals (latency, errors)
    expert_weight: float = 2.0          # Weight of expert/validated feedback
    feedback_decay: float = 0.9         # How fast old feedback loses importance

    # Memory and Experience Replay
    replay_buffer_size: int = 1000      # Size of experience replay buffer
    replay_sample_size: int = 32        # Sample size for experience replay
    prioritized_replay: bool = True     # Use prioritized experience replay
    priority_alpha: float = 0.6         # Prioritization exponent

    # Optimization Triggers
    batch_size: int = 32                # Batch size for learning updates
    update_frequency: int = 10          # Update model every N steps
    optimization_threshold: int = 100   # Major optimization every N feedbacks

    # Performance Windows
    history_window: int = 100           # Window for performance tracking
    trend_window: int = 20              # Window for trend analysis

    # Regularization
    l2_penalty: float = 0.001           # L2 regularization for Q-values
    entropy_bonus: float = 0.01         # Entropy bonus for exploration

    # Credit Assignment
    eligibility_trace_decay: float = 0.9  # Lambda for eligibility traces
    n_step_return: int = 5              # N-step returns for better credit assignment

    def decay_epsilon(self):
        """Apply epsilon decay for reduced exploration over time."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def decay_learning_rate(self):
        """Apply learning rate decay for stability."""
        self.learning_rate = max(self.learning_min, self.learning_rate * self.learning_decay)

    def decay_temperature(self):
        """Cool down temperature for more deterministic behavior."""
        self.temperature = max(self.temperature_min, self.temperature * self.temperature_decay)

    def adapt_to_performance(self, recent_performance: float):
        """Adapt factors based on recent performance."""
        if recent_performance < 0.3:
            # Poor performance - increase exploration
            self.epsilon = min(0.3, self.epsilon * 1.1)
            self.temperature = min(2.0, self.temperature * 1.05)
        elif recent_performance > 0.8:
            # Good performance - decrease exploration
            self.epsilon = max(self.epsilon_min, self.epsilon * 0.95)
            self.temperature = max(self.temperature_min, self.temperature * 0.95)


class RLFactorOptimizer:
    """Optimizes RL factors for maximum cumulative learning effect."""

    def __init__(self, project_id: str):
        """Initialize the RL factor optimizer."""
        self.project_id = project_id
        self.factors = RLFactors()

        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.factor_performance: Dict[str, List[float]] = {
            'epsilon': [],
            'learning_rate': [],
            'temperature': [],
            'discount_factor': []
        }

        # Feedback buffers
        self.experience_replay_buffer = deque(maxlen=self.factors.replay_buffer_size)
        self.feedback_history = deque(maxlen=500)
        self.eligibility_traces: Dict[str, float] = {}

        # Meta-optimization state
        self.meta_learning_rate = 0.001
        self.factor_gradients: Dict[str, float] = {}

        # Load saved factors if available
        self._load_factors()

    def optimize_factors(self, recent_rewards: List[float],
                         recent_latencies: List[float]) -> Dict[str, float]:
        """
        Optimize RL factors based on recent performance.

        Uses meta-learning to adjust hyperparameters for better cumulative effect.
        """

        # Calculate performance metrics using TLM
        avg_reward = tlm.mean(recent_rewards) if recent_rewards else 0
        reward_variance = tlm.variance(recent_rewards) if len(recent_rewards) > 1 else 1
        avg_latency = tlm.mean(recent_latencies) if recent_latencies else 1

        # Update performance history
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'avg_reward': avg_reward,
            'reward_variance': reward_variance,
            'avg_latency': avg_latency,
            'epsilon': self.factors.epsilon,
            'learning_rate': self.factors.learning_rate,
            'temperature': self.factors.temperature
        })

        # Adapt factors based on performance
        self.factors.adapt_to_performance(avg_reward)

        # Meta-optimization: adjust factors based on gradients
        self._compute_factor_gradients(avg_reward, reward_variance)
        self._update_factors_with_gradients()

        # Apply decay schedules
        self.factors.decay_epsilon()
        self.factors.decay_learning_rate()
        self.factors.decay_temperature()

        # Save updated factors
        self._save_factors()

        return self.get_current_factors()

    def _compute_factor_gradients(self, reward: float, variance: float):
        """
        Compute gradients for each factor based on performance correlation.

        Uses simple finite differences to estimate impact of each factor.
        """

        if len(self.performance_history) < 10:
            return  # Not enough data for gradient estimation

        # Analyze correlation between factors and performance
        recent = list(self.performance_history)[-50:]

        # Epsilon gradient (exploration impact)
        epsilon_values = [p['epsilon'] for p in recent]
        rewards = [p['avg_reward'] for p in recent]

        if len(set(epsilon_values)) > 1:  # Need variation to compute correlation
            # Simple correlation as gradient proxy using TLM
            epsilon_corr = tlm.correlation(epsilon_values, rewards)
            self.factor_gradients['epsilon'] = epsilon_corr * self.meta_learning_rate

        # Learning rate gradient
        lr_values = [p['learning_rate'] for p in recent]
        if len(set(lr_values)) > 1:
            lr_corr = tlm.correlation(lr_values, rewards)
            self.factor_gradients['learning_rate'] = lr_corr * self.meta_learning_rate

        # Temperature gradient (inverse correlation with variance is good)
        temp_values = [p['temperature'] for p in recent]
        variances = [p.get('reward_variance', 1) for p in recent]
        if len(set(temp_values)) > 1:
            temp_corr = -tlm.correlation(temp_values, variances)  # Negative for stability
            self.factor_gradients['temperature'] = temp_corr * self.meta_learning_rate

    def _update_factors_with_gradients(self):
        """Apply computed gradients to update factors."""

        # Update epsilon
        if 'epsilon' in self.factor_gradients:
            gradient = self.factor_gradients['epsilon']
            if gradient > 0 and self.factors.epsilon < 0.3:
                # Positive correlation - increase exploration
                self.factors.epsilon = min(0.3, self.factors.epsilon * (1 + abs(gradient)))
            elif gradient < 0 and self.factors.epsilon > self.factors.epsilon_min:
                # Negative correlation - decrease exploration
                self.factors.epsilon = max(self.factors.epsilon_min,
                                          self.factors.epsilon * (1 - abs(gradient)))

        # Update learning rate
        if 'learning_rate' in self.factor_gradients:
            gradient = self.factor_gradients['learning_rate']
            if gradient > 0:
                self.factors.learning_rate = min(0.1,
                                                self.factors.learning_rate * (1 + abs(gradient)))
            elif gradient < 0:
                self.factors.learning_rate = max(self.factors.learning_min,
                                                self.factors.learning_rate * (1 - abs(gradient)))

        # Update temperature
        if 'temperature' in self.factor_gradients:
            gradient = self.factor_gradients['temperature']
            if gradient > 0:  # Negative correlation with variance is good
                self.factors.temperature = max(self.factors.temperature_min,
                                              self.factors.temperature * (1 - abs(gradient)))

    def get_exploration_action(self, q_values: Dict[str, float]) -> str:
        """
        Select action using current exploration strategy.

        Uses epsilon-greedy with temperature-based softmax.
        """

        if not q_values:
            return None

        # Epsilon-greedy exploration using TLM
        if random.random() < self.factors.epsilon:
            # Explore: random action
            return random.choice(list(q_values.keys()))
        else:
            # Exploit: use softmax with temperature
            return self._softmax_action_selection(q_values)

    def _softmax_action_selection(self, q_values: Dict[str, float]) -> str:
        """Select action using softmax with temperature."""

        actions = list(q_values.keys())
        values = list(q_values.values())

        # Apply temperature scaling using TLM
        scaled_values = [v / self.factors.temperature for v in values]

        # Compute softmax probabilities using TLM
        max_val = tlm.max(scaled_values)
        exp_values = [math.exp(v - max_val) for v in scaled_values]  # Stability trick
        exp_sum = tlm.sum(exp_values)
        probabilities = [exp_val / exp_sum for exp_val in exp_values]

        # Sample action based on probabilities using TLM
        return tlm.choice_weighted(actions, weights=probabilities, k=1)[0]

    def compute_td_error(self, reward: float, current_q: float,
                         next_q: float) -> float:
        """
        Compute temporal difference error for Q-learning.

        TD Error = reward + gamma * max(Q_next) - Q_current
        """
        return reward + self.factors.discount_factor * next_q - current_q

    def update_q_value(self, current_q: float, td_error: float) -> float:
        """
        Update Q-value using current learning rate.

        Q_new = Q_old + alpha * TD_error
        """
        return current_q + self.factors.learning_rate * td_error

    def get_current_factors(self) -> Dict[str, float]:
        """Get current RL factor values."""
        return {
            'epsilon': round(self.factors.epsilon, 4),
            'learning_rate': round(self.factors.learning_rate, 5),
            'discount_factor': round(self.factors.discount_factor, 3),
            'temperature': round(self.factors.temperature, 3),
            'batch_size': self.factors.batch_size,
            'update_frequency': self.factors.update_frequency
        }

    def process_feedback(self, feedback_type: str, value: float,
                         context: Dict[str, Any] = None) -> float:
        """
        Process different types of feedback into weighted rewards.

        Args:
            feedback_type: 'explicit', 'implicit', 'expert', 'system'
            value: Raw feedback value
            context: Additional context (step_name, latency, error_rate, etc.)

        Returns:
            Weighted reward value
        """

        # Clip raw value using TLM
        value = tlm.clip(value, -self.factors.reward_clipping, self.factors.reward_clipping)

        # Apply feedback type weighting
        if feedback_type == 'expert':
            weighted_value = value * self.factors.expert_weight
        elif feedback_type == 'explicit':
            weighted_value = value * self.factors.feedback_weight
        elif feedback_type == 'implicit':
            weighted_value = value * self.factors.implicit_weight
        else:  # system
            weighted_value = value * 0.3

        # Add to feedback history with decay
        self.feedback_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': feedback_type,
            'value': value,
            'weighted_value': weighted_value,
            'context': context or {}
        })

        # Update eligibility traces if step_name provided
        if context and 'step_name' in context:
            step_name = context['step_name']
            if step_name not in self.eligibility_traces:
                self.eligibility_traces[step_name] = 0
            self.eligibility_traces[step_name] = 1.0  # Reset trace

            # Decay all traces
            for name in list(self.eligibility_traces.keys()):
                if name != step_name:
                    self.eligibility_traces[name] *= self.factors.eligibility_trace_decay
                    if self.eligibility_traces[name] < 0.01:
                        del self.eligibility_traces[name]

        return weighted_value

    def add_experience(self, state: Dict, action: str, reward: float,
                      next_state: Dict, done: bool):
        """
        Add experience to replay buffer for learning.

        Uses prioritized experience replay if enabled.
        """

        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.now().isoformat()
        }

        # Calculate priority for prioritized replay
        if self.factors.prioritized_replay:
            # Use TD error magnitude as priority
            td_error = abs(reward)  # Simplified - should use actual TD error
            priority = (td_error + 0.01) ** self.factors.priority_alpha
            experience['priority'] = priority

        self.experience_replay_buffer.append(experience)

    def sample_experiences(self) -> List[Dict]:
        """
        Sample experiences from replay buffer.

        Uses prioritized sampling if enabled.
        """

        if len(self.experience_replay_buffer) < self.factors.replay_sample_size:
            return list(self.experience_replay_buffer)

        if self.factors.prioritized_replay:
            # Prioritized sampling
            experiences = list(self.experience_replay_buffer)
            priorities = [exp.get('priority', 1.0) for exp in experiences]
            total_priority = sum(priorities)
            probabilities = [p / total_priority for p in priorities]

            # TLM-based weighted random sampling
            indices = tlm.choice_weighted(
                range(len(experiences)),
                weights=probabilities,
                k=self.factors.replay_sample_size
            )
            return [experiences[i] for i in indices]
        else:
            # Uniform sampling using TLM
            indices = tlm.sample(
                range(len(self.experience_replay_buffer)),
                k=self.factors.replay_sample_size
            )
            return [self.experience_replay_buffer[i] for i in indices]

    def compute_n_step_return(self, rewards: List[float], final_value: float = 0) -> float:
        """
        Compute n-step return for better credit assignment.

        Uses the configured n_step_return parameter.
        """

        n = min(self.factors.n_step_return, len(rewards))
        n_step_return = final_value * (self.factors.discount_factor ** n)

        for i, reward in enumerate(rewards[:n]):
            n_step_return += reward * (self.factors.discount_factor ** i)

        return n_step_return

    def apply_regularization(self, q_values: Dict[str, float]) -> Dict[str, float]:
        """
        Apply L2 regularization and entropy bonus to Q-values.

        Helps prevent overfitting and encourages exploration.
        """

        regularized_values = {}

        # L2 regularization
        for action, q_value in q_values.items():
            regularized_values[action] = q_value * (1 - self.factors.l2_penalty)

        # Entropy bonus (encourages uniform action distribution) using TLM
        values_list = list(regularized_values.values())
        if len(values_list) > 1:
            # Calculate entropy of softmax distribution using TLM
            max_val = tlm.max(values_list)
            exp_values = [math.exp(v - max_val) for v in values_list]
            exp_sum = tlm.sum(exp_values)
            probs = [exp_val / exp_sum for exp_val in exp_values]
            entropy = -tlm.sum([p * math.log(p + 1e-10) for p in probs])

            # Add entropy bonus to all actions
            for action in regularized_values:
                regularized_values[action] += self.factors.entropy_bonus * entropy

        return regularized_values

    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate report on factor optimization performance."""

        if len(self.performance_history) < 10:
            return {'status': 'insufficient_data'}

        recent = list(self.performance_history)[-100:]
        older = list(self.performance_history)[-200:-100] if len(self.performance_history) > 100 else []

        recent_reward = tlm.mean([p['avg_reward'] for p in recent])
        older_reward = tlm.mean([p['avg_reward'] for p in older]) if older else recent_reward

        improvement = ((recent_reward - older_reward) / max(abs(older_reward), 0.01)) * 100

        return {
            'current_factors': self.get_current_factors(),
            'performance_trend': {
                'recent_avg_reward': round(recent_reward, 3),
                'older_avg_reward': round(older_reward, 3),
                'improvement_pct': round(improvement, 1)
            },
            'factor_gradients': {k: round(v, 5) for k, v in self.factor_gradients.items()},
            'optimization_history': len(self.performance_history),
            'convergence_status': self._check_convergence()
        }

    def _check_convergence(self) -> str:
        """Check if factors have converged to stable values."""

        if len(self.performance_history) < 50:
            return 'warming_up'

        recent = list(self.performance_history)[-20:]

        # Check epsilon stability using TLM
        epsilon_values = [p['epsilon'] for p in recent]
        epsilon_variance = tlm.variance(epsilon_values)

        # Check learning rate stability using TLM
        lr_values = [p['learning_rate'] for p in recent]
        lr_variance = tlm.variance(lr_values)

        if epsilon_variance < 0.0001 and lr_variance < 0.00001:
            return 'converged'
        elif epsilon_variance < 0.001 and lr_variance < 0.0001:
            return 'stabilizing'
        else:
            return 'optimizing'

    def _save_factors(self):
        """Save current factors to disk."""
        try:
            from core.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            factors_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "rl_factors.json"

            factors_data = {
                'factors': {
                    'epsilon': self.factors.epsilon,
                    'epsilon_decay': self.factors.epsilon_decay,
                    'learning_rate': self.factors.learning_rate,
                    'learning_decay': self.factors.learning_decay,
                    'discount_factor': self.factors.discount_factor,
                    'temperature': self.factors.temperature,
                    'temperature_decay': self.factors.temperature_decay
                },
                'meta_learning_rate': self.meta_learning_rate,
                'last_updated': datetime.now().isoformat()
            }

            factors_file.parent.mkdir(parents=True, exist_ok=True)
            with open(factors_file, 'w') as f:
                json.dump(factors_data, f, indent=2)

        except Exception as e:
            logger.debug(f"Could not save RL factors: {e}")

    def _load_factors(self):
        """Load saved factors from disk."""
        try:
            from core.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            factors_file = Path(root) / "domain" / "workflows" / "projects" / self.project_id / "rl_factors.json"

            if factors_file.exists():
                with open(factors_file, 'r') as f:
                    data = json.load(f)

                    # Restore factors
                    factors = data.get('factors', {})
                    self.factors.epsilon = factors.get('epsilon', 0.1)
                    self.factors.learning_rate = factors.get('learning_rate', 0.01)
                    self.factors.discount_factor = factors.get('discount_factor', 0.95)
                    self.factors.temperature = factors.get('temperature', 1.0)

                    self.meta_learning_rate = data.get('meta_learning_rate', 0.001)

                logger.info(f"Loaded RL factors from {factors_file}")

        except Exception as e:
            logger.debug(f"Could not load RL factors: {e}")


def get_rl_optimizer(project_id: str) -> RLFactorOptimizer:
    """Factory function to get an RLFactorOptimizer instance."""
    return RLFactorOptimizer(project_id)