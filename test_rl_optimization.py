#!/usr/bin/env python3
"""
TidyLLM RL Optimization Testing Script
=====================================

Test TidyLLM RL functions across 5 different step flows and 5 different prompt flows
to measure RL optimization performance and adaptation.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import TidyLLM RL functions
try:
    from packages.tidyllm.services.workflow_rl_optimizer import (
        optimize_workflow_execution,
        calculate_step_reward,
        update_rl_factors,
        get_rl_performance_summary,
        create_rl_enhanced_step
    )
    TIDYLLM_RL_AVAILABLE = True
    print("TidyLLM RL functions imported successfully")
except ImportError as e:
    TIDYLLM_RL_AVAILABLE = False
    print(f"TidyLLM RL functions not available: {e}")

# Import step managers for testing
try:
    from domain.services.action_steps_manager import ActionStepsManager
    from domain.services.prompt_steps_manager import PromptStepsManager
    STEP_MANAGERS_AVAILABLE = True
    print("Step managers imported successfully")
except ImportError as e:
    STEP_MANAGERS_AVAILABLE = False
    print(f"Step managers not available: {e}")


class RLOptimizationTester:
    """Test RL optimization across different workflow types."""

    def __init__(self):
        """Initialize the RL optimization tester."""
        self.test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "tidyllm_rl_available": TIDYLLM_RL_AVAILABLE,
            "step_managers_available": STEP_MANAGERS_AVAILABLE,
            "step_flow_tests": {},
            "prompt_flow_tests": {},
            "performance_summary": {},
            "rl_learning_progression": []
        }

        # Test project IDs for different flow types
        self.test_projects = {
            "data_processing": "test_data_pipeline",
            "ml_training": "test_ml_model",
            "document_analysis": "test_doc_proc",
            "api_integration": "test_api_flow",
            "business_automation": "test_biz_auto",
            "content_generation": "test_content_gen",
            "code_analysis": "test_code_review",
            "customer_support": "test_support",
            "research_analysis": "test_research",
            "creative_storytelling": "test_creative"
        }

    def load_test_flows(self) -> Dict[str, Any]:
        """Load all test flows from the test_flows directory."""
        flows = {"step_flows": {}, "prompt_flows": {}}

        # Load step flows
        step_flow_dir = Path("test_flows/step_flows")
        if step_flow_dir.exists():
            for flow_file in step_flow_dir.glob("*.json"):
                try:
                    with open(flow_file, 'r', encoding='utf-8') as f:
                        flow_data = json.load(f)
                        flows["step_flows"][flow_file.stem] = flow_data
                        print(f"Loaded step flow: {flow_file.stem}")
                except Exception as e:
                    print(f"❌ Failed to load step flow {flow_file.stem}: {e}")

        # Load prompt flows
        prompt_flow_dir = Path("test_flows/prompt_flows")
        if prompt_flow_dir.exists():
            for flow_file in prompt_flow_dir.glob("*.json"):
                try:
                    with open(flow_file, 'r', encoding='utf-8') as f:
                        flow_data = json.load(f)
                        flows["prompt_flows"][flow_file.stem] = flow_data
                        print(f"✓ Loaded prompt flow: {flow_file.stem}")
                except Exception as e:
                    print(f"❌ Failed to load prompt flow {flow_file.stem}: {e}")

        return flows

    def test_step_flow_optimization(self, flow_name: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test RL optimization on a step flow."""
        if not TIDYLLM_RL_AVAILABLE:
            return {"error": "TidyLLM RL not available", "test_skipped": True}

        print(f"\n🧪 Testing step flow: {flow_name}")
        project_id = self.test_projects.get(flow_name, f"test_{flow_name}")

        test_start = time.time()

        try:
            # Test 1: Workflow optimization
            print(f"  → Testing workflow optimization...")
            optimization_result = optimize_workflow_execution(
                project_id=project_id,
                workflow_config=flow_data,
                context={"test_mode": True, "flow_type": "step_flow"}
            )

            # Test 2: Individual step enhancement
            print(f"  → Testing step enhancement...")
            steps = flow_data.get('steps', {})
            enhanced_steps = []

            for step_id, step_config in steps.items():
                enhanced_step = create_rl_enhanced_step(step_config, project_id)
                enhanced_steps.append(enhanced_step)

            # Test 3: Simulate step execution and reward calculation
            print(f"  → Testing reward calculation...")
            step_rewards = []

            for i, step_config in enumerate(list(steps.values())[:3]):  # Test first 3 steps
                # Simulate step execution
                execution_time = 0.5 + (i * 0.3)  # Varying execution times
                success = True

                execution_result = {
                    "status": "success",
                    "step_type": step_config.get('step_type', 'process'),
                    "execution_time": execution_time,
                    "output_quality": 0.8 + (i * 0.05)
                }

                reward = calculate_step_reward(
                    step_config=step_config,
                    execution_result=execution_result,
                    execution_time=execution_time,
                    success=success
                )

                step_rewards.append(reward)

                # Update RL factors with feedback
                update_rl_factors(
                    project_id=project_id,
                    step_type=step_config.get('step_type', 'process'),
                    reward=reward
                )

            # Test 4: Get performance summary
            print(f"  → Getting performance summary...")
            performance_summary = get_rl_performance_summary(project_id)

            test_duration = time.time() - test_start

            return {
                "test_successful": True,
                "test_duration": test_duration,
                "optimization_result": optimization_result,
                "enhanced_steps_count": len(enhanced_steps),
                "step_rewards": step_rewards,
                "average_reward": sum(step_rewards) / len(step_rewards) if step_rewards else 0,
                "performance_summary": performance_summary,
                "flow_complexity": flow_data.get('metadata', {}).get('workflow_complexity', 'unknown'),
                "step_count": len(steps)
            }

        except Exception as e:
            return {
                "test_successful": False,
                "error": str(e),
                "test_duration": time.time() - test_start
            }

    def test_prompt_flow_optimization(self, flow_name: str, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test RL optimization on a prompt flow."""
        if not TIDYLLM_RL_AVAILABLE:
            return {"error": "TidyLLM RL not available", "test_skipped": True}

        print(f"\n🎯 Testing prompt flow: {flow_name}")
        project_id = self.test_projects.get(flow_name, f"test_{flow_name}")

        test_start = time.time()

        try:
            # Convert prompt flow to step format for RL testing
            prompt_steps = flow_data.get('prompt_steps', {})
            converted_steps = {}

            for step_id, prompt_step in prompt_steps.items():
                converted_step = {
                    "step_id": step_id,
                    "step_name": prompt_step.get('step_name', f'Prompt Step {step_id}'),
                    "step_type": "prompt",
                    "step_number": prompt_step.get('step_number', step_id),
                    "description": prompt_step.get('description', ''),
                    "template": prompt_step.get('template', ''),
                    "variables": prompt_step.get('variables', []),
                    "kind": prompt_step.get('kind', 'generate'),
                    "params": prompt_step.get('params', {})
                }
                converted_steps[step_id] = converted_step

            workflow_config = {
                "workflow_id": flow_data.get('workflow_id', flow_name),
                "workflow_type": "prompt_flow",
                "steps": converted_steps
            }

            # Test 1: Workflow optimization for prompt flow
            print(f"  → Testing prompt workflow optimization...")
            optimization_result = optimize_workflow_execution(
                project_id=project_id,
                workflow_config=workflow_config,
                context={"test_mode": True, "flow_type": "prompt_flow"}
            )

            # Test 2: Prompt-specific step enhancement
            print(f"  → Testing prompt step enhancement...")
            enhanced_prompts = []

            for step_config in list(converted_steps.values())[:3]:  # Test first 3 prompts
                enhanced_step = create_rl_enhanced_step(step_config, project_id)
                enhanced_prompts.append(enhanced_step)

            # Test 3: Simulate prompt execution and reward calculation
            print(f"  → Testing prompt reward calculation...")
            prompt_rewards = []

            for i, step_config in enumerate(list(converted_steps.values())[:3]):
                # Simulate prompt execution with varying quality
                execution_time = 1.0 + (i * 0.5)  # Prompts take longer
                success = True

                execution_result = {
                    "status": "success",
                    "step_type": "prompt",
                    "execution_time": execution_time,
                    "response_quality": 0.75 + (i * 0.08),
                    "prompt_effectiveness": 0.8 + (i * 0.05)
                }

                reward = calculate_step_reward(
                    step_config=step_config,
                    execution_result=execution_result,
                    execution_time=execution_time,
                    success=success
                )

                prompt_rewards.append(reward)

                # Update RL factors for prompt optimization
                update_rl_factors(
                    project_id=project_id,
                    step_type="prompt",
                    reward=reward,
                    context={"prompt_category": step_config.get('category', 'general')}
                )

            # Test 4: Get performance summary
            print(f"  → Getting prompt performance summary...")
            performance_summary = get_rl_performance_summary(project_id)

            test_duration = time.time() - test_start

            return {
                "test_successful": True,
                "test_duration": test_duration,
                "optimization_result": optimization_result,
                "enhanced_prompts_count": len(enhanced_prompts),
                "prompt_rewards": prompt_rewards,
                "average_reward": sum(prompt_rewards) / len(prompt_rewards) if prompt_rewards else 0,
                "performance_summary": performance_summary,
                "flow_complexity": flow_data.get('metadata', {}).get('workflow_complexity', 'unknown'),
                "prompt_count": len(prompt_steps)
            }

        except Exception as e:
            return {
                "test_successful": False,
                "error": str(e),
                "test_duration": time.time() - test_start
            }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive RL optimization tests across all flows."""
        print("🚀 Starting Comprehensive TidyLLM RL Optimization Tests")
        print("=" * 60)

        if not TIDYLLM_RL_AVAILABLE:
            print("❌ TidyLLM RL functions not available - tests cannot run")
            return self.test_results

        # Load all test flows
        flows = self.load_test_flows()

        print(f"\n📊 Test Summary:")
        print(f"  Step flows loaded: {len(flows['step_flows'])}")
        print(f"  Prompt flows loaded: {len(flows['prompt_flows'])}")

        # Test step flows
        print(f"\n🔧 Testing Step Flow RL Optimization:")
        print("-" * 40)

        for flow_name, flow_data in flows["step_flows"].items():
            test_result = self.test_step_flow_optimization(flow_name, flow_data)
            self.test_results["step_flow_tests"][flow_name] = test_result

        # Test prompt flows
        print(f"\n💬 Testing Prompt Flow RL Optimization:")
        print("-" * 40)

        for flow_name, flow_data in flows["prompt_flows"].items():
            test_result = self.test_prompt_flow_optimization(flow_name, flow_data)
            self.test_results["prompt_flow_tests"][flow_name] = test_result

        # Generate overall performance summary
        self.generate_performance_summary()

        return self.test_results

    def generate_performance_summary(self):
        """Generate overall performance summary across all tests."""
        print(f"\n📈 Generating Performance Summary...")

        # Analyze step flow results
        step_results = self.test_results["step_flow_tests"]
        successful_step_tests = [r for r in step_results.values() if r.get("test_successful", False)]

        # Analyze prompt flow results
        prompt_results = self.test_results["prompt_flow_tests"]
        successful_prompt_tests = [r for r in prompt_results.values() if r.get("test_successful", False)]

        # Calculate aggregate metrics
        step_rewards = []
        prompt_rewards = []

        for result in successful_step_tests:
            step_rewards.extend(result.get("step_rewards", []))

        for result in successful_prompt_tests:
            prompt_rewards.extend(result.get("prompt_rewards", []))

        self.test_results["performance_summary"] = {
            "total_flows_tested": len(step_results) + len(prompt_results),
            "successful_tests": len(successful_step_tests) + len(successful_prompt_tests),
            "step_flow_performance": {
                "tests_run": len(step_results),
                "successful_tests": len(successful_step_tests),
                "average_reward": sum(step_rewards) / len(step_rewards) if step_rewards else 0,
                "total_steps_optimized": sum(r.get("enhanced_steps_count", 0) for r in successful_step_tests),
                "avg_test_duration": sum(r.get("test_duration", 0) for r in successful_step_tests) / len(successful_step_tests) if successful_step_tests else 0
            },
            "prompt_flow_performance": {
                "tests_run": len(prompt_results),
                "successful_tests": len(successful_prompt_tests),
                "average_reward": sum(prompt_rewards) / len(prompt_rewards) if prompt_rewards else 0,
                "total_prompts_optimized": sum(r.get("enhanced_prompts_count", 0) for r in successful_prompt_tests),
                "avg_test_duration": sum(r.get("test_duration", 0) for r in successful_prompt_tests) / len(successful_prompt_tests) if successful_prompt_tests else 0
            },
            "overall_metrics": {
                "success_rate": (len(successful_step_tests) + len(successful_prompt_tests)) / (len(step_results) + len(prompt_results)) if (len(step_results) + len(prompt_results)) > 0 else 0,
                "total_rewards_calculated": len(step_rewards) + len(prompt_rewards),
                "overall_average_reward": (sum(step_rewards) + sum(prompt_rewards)) / (len(step_rewards) + len(prompt_rewards)) if (len(step_rewards) + len(prompt_rewards)) > 0 else 0
            }
        }

    def save_results(self, filename: str = None):
        """Save test results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rl_optimization_test_results_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

    def print_summary(self):
        """Print a formatted summary of test results."""
        print(f"\n🎯 TidyLLM RL Optimization Test Results")
        print("=" * 50)

        summary = self.test_results.get("performance_summary", {})

        print(f"📊 Overall Results:")
        print(f"  Total flows tested: {summary.get('total_flows_tested', 0)}")
        print(f"  Successful tests: {summary.get('successful_tests', 0)}")
        print(f"  Success rate: {summary.get('overall_metrics', {}).get('success_rate', 0):.2%}")
        print(f"  Overall avg reward: {summary.get('overall_metrics', {}).get('overall_average_reward', 0):.3f}")

        step_perf = summary.get("step_flow_performance", {})
        print(f"\n🔧 Step Flow Performance:")
        print(f"  Tests: {step_perf.get('successful_tests', 0)}/{step_perf.get('tests_run', 0)}")
        print(f"  Avg reward: {step_perf.get('average_reward', 0):.3f}")
        print(f"  Steps optimized: {step_perf.get('total_steps_optimized', 0)}")

        prompt_perf = summary.get("prompt_flow_performance", {})
        print(f"\n💬 Prompt Flow Performance:")
        print(f"  Tests: {prompt_perf.get('successful_tests', 0)}/{prompt_perf.get('tests_run', 0)}")
        print(f"  Avg reward: {prompt_perf.get('average_reward', 0):.3f}")
        print(f"  Prompts optimized: {prompt_perf.get('total_prompts_optimized', 0)}")


def main():
    """Main execution function."""
    print("🧠 TidyLLM RL Optimization Test Suite")
    print("=" * 50)

    # Create tester and run tests
    tester = RLOptimizationTester()
    results = tester.run_comprehensive_test()

    # Print summary
    tester.print_summary()

    # Save results
    tester.save_results()

    print(f"\n✅ Testing complete!")


if __name__ == "__main__":
    main()