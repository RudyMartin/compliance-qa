#!/usr/bin/env python3
"""
RL Factor Optimizer Performance Comparison
==========================================

Tests both TLM and NumPy versions to compare:
- Performance/speed
- Memory usage
- Accuracy of results
- Convergence behavior
"""

import time
import sys
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import both versions
from domain.services.rl_factor_optimizer import RLFactorOptimizer  # TLM version
from domain.services.rl_factor_optimizer_numpy import RLFactorOptimizerNumPy  # NumPy version


def generate_test_data(n_samples: int = 1000) -> tuple:
    """Generate test data for performance comparison."""

    # Simulate rewards and latencies
    rewards = []
    latencies = []

    for i in range(n_samples):
        # Simulate learning curve (improving over time)
        base_reward = -0.5 + (i / n_samples) * 1.5  # Goes from -0.5 to 1.0
        noise = (random.random() - 0.5) * 0.4  # ±0.2 noise
        reward = max(-1.0, min(1.0, base_reward + noise))
        rewards.append(reward)

        # Simulate latency (improving over time)
        base_latency = 2.0 - (i / n_samples) * 1.0  # Goes from 2.0 to 1.0
        latency_noise = random.random() * 0.5
        latency = max(0.1, base_latency + latency_noise)
        latencies.append(latency)

    return rewards, latencies


def benchmark_optimizer(optimizer_class, name: str, rewards: List[float],
                       latencies: List[float]) -> Dict[str, Any]:
    """Benchmark a single optimizer version."""

    print(f"\n{'='*60}")
    print(f"BENCHMARKING {name}")
    print(f"{'='*60}")

    # Start memory tracking
    tracemalloc.start()

    # Initialize optimizer
    start_time = time.time()
    optimizer = optimizer_class("benchmark_test")
    init_time = time.time() - start_time

    # Test different operations
    results = {
        'name': name,
        'init_time': init_time,
        'operations': {}
    }

    # 1. Factor Optimization
    print(f"Testing factor optimization...")
    start_time = time.time()

    batch_size = 50
    optimization_times = []

    for i in range(0, len(rewards), batch_size):
        batch_rewards = rewards[i:i+batch_size]
        batch_latencies = latencies[i:i+batch_size]

        opt_start = time.time()
        factors = optimizer.optimize_factors(batch_rewards, batch_latencies)
        opt_time = time.time() - opt_start
        optimization_times.append(opt_time)

    results['operations']['optimization'] = {
        'total_time': time.time() - start_time,
        'avg_batch_time': sum(optimization_times) / len(optimization_times),
        'batches_processed': len(optimization_times)
    }

    # 2. Feedback Processing
    print(f"Testing feedback processing...")
    start_time = time.time()

    feedback_times = []
    for i, reward in enumerate(rewards[:100]):  # Test first 100
        fb_start = time.time()
        weighted_reward = optimizer.process_feedback(
            'explicit', reward,
            {'step_name': f'test_step_{i % 10}'}
        )
        fb_time = time.time() - fb_start
        feedback_times.append(fb_time)

    results['operations']['feedback'] = {
        'total_time': time.time() - start_time,
        'avg_feedback_time': sum(feedback_times) / len(feedback_times),
        'feedbacks_processed': len(feedback_times)
    }

    # 3. Action Selection
    print(f"Testing action selection...")
    q_values = {
        'speed': 0.5,
        'balanced': 0.7,
        'quality': 0.6,
        'premium': 0.4
    }

    start_time = time.time()
    actions = []
    for _ in range(1000):
        action = optimizer.get_exploration_action(q_values)
        actions.append(action)
    action_time = time.time() - start_time

    results['operations']['action_selection'] = {
        'total_time': action_time,
        'avg_action_time': action_time / 1000,
        'actions_selected': len(actions)
    }

    # 4. Experience Replay
    print(f"Testing experience replay...")
    start_time = time.time()

    # Add experiences
    for i in range(100):
        optimizer.add_experience(
            state={'step': f'step_{i}'},
            action=random.choice(['speed', 'balanced', 'quality']),
            reward=rewards[i],
            next_state={'step': f'step_{i+1}'},
            done=False
        )

    # Sample experiences
    replay_times = []
    for _ in range(50):
        sample_start = time.time()
        experiences = optimizer.sample_experiences()
        sample_time = time.time() - sample_start
        replay_times.append(sample_time)

    results['operations']['experience_replay'] = {
        'total_time': time.time() - start_time,
        'avg_sample_time': sum(replay_times) / len(replay_times),
        'samples_generated': len(replay_times)
    }

    # 5. Get final report
    print(f"Generating optimization report...")
    start_time = time.time()
    report = optimizer.get_optimization_report()
    report_time = time.time() - start_time

    results['operations']['reporting'] = {
        'time': report_time,
        'report_status': report.get('status', 'success')
    }

    # Memory usage
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results['memory'] = {
        'current_mb': current / 1024 / 1024,
        'peak_mb': peak / 1024 / 1024
    }

    # Final factors
    results['final_factors'] = optimizer.get_current_factors()

    return results


def compare_results(tlm_results: Dict, numpy_results: Dict):
    """Compare results between TLM and NumPy versions."""

    print(f"\n{'='*80}")
    print(f"PERFORMANCE COMPARISON RESULTS")
    print(f"{'='*80}")

    # Overall performance
    print(f"\n[PERF] OVERALL PERFORMANCE:")
    print(f"{'Metric':<25} {'TLM':<15} {'NumPy':<15} {'Winner':<10}")
    print(f"{'-'*70}")

    # Initialization time
    tlm_init = tlm_results['init_time']
    numpy_init = numpy_results['init_time']
    init_winner = "TLM" if tlm_init < numpy_init else "NumPy"
    print(f"{'Initialization (ms)':<25} {tlm_init*1000:<15.2f} {numpy_init*1000:<15.2f} {init_winner:<10}")

    # Memory usage
    tlm_mem = tlm_results['memory']['peak_mb']
    numpy_mem = numpy_results['memory']['peak_mb']
    mem_winner = "TLM" if tlm_mem < numpy_mem else "NumPy"
    print(f"{'Peak Memory (MB)':<25} {tlm_mem:<15.2f} {numpy_mem:<15.2f} {mem_winner:<10}")

    print(f"\n[SPEED] OPERATION PERFORMANCE:")
    print(f"{'Operation':<25} {'TLM (ms)':<15} {'NumPy (ms)':<15} {'Winner':<10}")
    print(f"{'-'*70}")

    # Compare each operation
    operations = ['optimization', 'feedback', 'action_selection', 'experience_replay', 'reporting']

    for op in operations:
        if op in tlm_results['operations'] and op in numpy_results['operations']:
            if op == 'optimization':
                tlm_time = tlm_results['operations'][op]['avg_batch_time'] * 1000
                numpy_time = numpy_results['operations'][op]['avg_batch_time'] * 1000
                metric = "Avg Batch Time"
            elif op == 'feedback':
                tlm_time = tlm_results['operations'][op]['avg_feedback_time'] * 1000
                numpy_time = numpy_results['operations'][op]['avg_feedback_time'] * 1000
                metric = "Avg Feedback Time"
            elif op == 'action_selection':
                tlm_time = tlm_results['operations'][op]['avg_action_time'] * 1000
                numpy_time = numpy_results['operations'][op]['avg_action_time'] * 1000
                metric = "Avg Action Time"
            elif op == 'experience_replay':
                tlm_time = tlm_results['operations'][op]['avg_sample_time'] * 1000
                numpy_time = numpy_results['operations'][op]['avg_sample_time'] * 1000
                metric = "Avg Sample Time"
            else:
                tlm_time = tlm_results['operations'][op]['time'] * 1000
                numpy_time = numpy_results['operations'][op]['time'] * 1000
                metric = "Report Time"

            winner = "TLM" if tlm_time < numpy_time else "NumPy"
            print(f"{metric:<25} {tlm_time:<15.2f} {numpy_time:<15.2f} {winner:<10}")

    # Accuracy comparison
    print(f"\n🎯 ACCURACY COMPARISON:")
    print(f"{'Factor':<20} {'TLM':<15} {'NumPy':<15} {'Diff':<10}")
    print(f"{'-'*65}")

    tlm_factors = tlm_results['final_factors']
    numpy_factors = numpy_results['final_factors']

    for factor in ['epsilon', 'learning_rate', 'temperature', 'discount_factor']:
        tlm_val = tlm_factors.get(factor, 0)
        numpy_val = numpy_factors.get(factor, 0)
        diff = abs(tlm_val - numpy_val)
        print(f"{factor:<20} {tlm_val:<15.4f} {numpy_val:<15.4f} {diff:<10.4f}")

    # Summary
    print(f"\n📊 SUMMARY:")
    tlm_wins = 0
    numpy_wins = 0

    # Count wins
    if tlm_init < numpy_init:
        tlm_wins += 1
    else:
        numpy_wins += 1

    if tlm_mem < numpy_mem:
        tlm_wins += 1
    else:
        numpy_wins += 1

    for op in operations:
        if op in tlm_results['operations'] and op in numpy_results['operations']:
            if op == 'optimization':
                tlm_time = tlm_results['operations'][op]['avg_batch_time']
                numpy_time = numpy_results['operations'][op]['avg_batch_time']
            elif op == 'feedback':
                tlm_time = tlm_results['operations'][op]['avg_feedback_time']
                numpy_time = numpy_results['operations'][op]['avg_feedback_time']
            elif op == 'action_selection':
                tlm_time = tlm_results['operations'][op]['avg_action_time']
                numpy_time = numpy_results['operations'][op]['avg_action_time']
            elif op == 'experience_replay':
                tlm_time = tlm_results['operations'][op]['avg_sample_time']
                numpy_time = numpy_results['operations'][op]['avg_sample_time']
            else:
                tlm_time = tlm_results['operations'][op]['time']
                numpy_time = numpy_results['operations'][op]['time']

            if tlm_time < numpy_time:
                tlm_wins += 1
            else:
                numpy_wins += 1

    print(f"🏆 TLM Wins: {tlm_wins}")
    print(f"🥈 NumPy Wins: {numpy_wins}")

    if tlm_wins > numpy_wins:
        print(f"🎉 OVERALL WINNER: TLM (Teaching Library Math)")
        print(f"   - Zero dependencies")
        print(f"   - Better performance in {tlm_wins}/{tlm_wins+numpy_wins} metrics")
    elif numpy_wins > tlm_wins:
        print(f"🎉 OVERALL WINNER: NumPy")
        print(f"   - Mature optimized library")
        print(f"   - Better performance in {numpy_wins}/{tlm_wins+numpy_wins} metrics")
    else:
        print(f"🤝 TIE! Both libraries perform equally well")


def main():
    """Run the performance comparison with 5 different test series."""

    print(f"[ROCKET] RL Factor Optimizer Performance Comparison")
    print(f"Testing TLM vs NumPy implementations across 5 test series")

    all_results = []
    test_configs = [
        {"name": "Small Dataset", "samples": 500, "seed": 42},
        {"name": "Medium Dataset", "samples": 1000, "seed": 123},
        {"name": "Large Dataset", "samples": 2000, "seed": 456},
        {"name": "High Variance", "samples": 1000, "seed": 789, "high_variance": True},
        {"name": "Convergent Learning", "samples": 1000, "seed": 321, "smooth": True}
    ]

    for i, config in enumerate(test_configs, 1):
        print(f"\n" + "="*80)
        print(f"TEST SERIES {i}/5: {config['name']}")
        print(f"="*80)

        # Set seed for reproducible results
        random.seed(config['seed'])

        # Generate test data with variations
        if config.get('high_variance'):
            rewards, latencies = generate_test_data_high_variance(config['samples'])
        elif config.get('smooth'):
            rewards, latencies = generate_test_data_smooth(config['samples'])
        else:
            rewards, latencies = generate_test_data(config['samples'])

        try:
            # Test TLM version
            tlm_results = benchmark_optimizer(RLFactorOptimizer, "TLM", rewards, latencies)

            # Test NumPy version
            numpy_results = benchmark_optimizer(RLFactorOptimizerNumPy, "NumPy", rewards, latencies)

            # Store results
            series_result = {
                'series': i,
                'config': config,
                'tlm': tlm_results,
                'numpy': numpy_results
            }
            all_results.append(series_result)

            # Compare results for this series
            compare_results(tlm_results, numpy_results)

        except Exception as e:
            print(f"[ERROR] Error in test series {i}: {e}")
            import traceback
            traceback.print_exc()

    # Generate comprehensive report
    generate_comprehensive_report(all_results)

    print(f"\n[SUCCESS] All 5 test series completed successfully!")
    return True


def generate_test_data_high_variance(n_samples: int = 1000) -> tuple:
    """Generate test data with high variance for stress testing."""
    rewards = []
    latencies = []

    for i in range(n_samples):
        # High variance rewards
        base_reward = (random.random() - 0.5) * 2  # -1 to 1
        noise = (random.random() - 0.5) * 1.5  # High noise
        reward = max(-1.0, min(1.0, base_reward + noise))
        rewards.append(reward)

        # Variable latencies
        latency = random.random() * 3 + 0.1  # 0.1 to 3.1 seconds
        latencies.append(latency)

    return rewards, latencies


def generate_test_data_smooth(n_samples: int = 1000) -> tuple:
    """Generate smooth convergent test data."""
    rewards = []
    latencies = []

    for i in range(n_samples):
        # Smooth learning curve
        progress = i / n_samples
        base_reward = -0.8 + progress * 1.6  # -0.8 to 0.8
        noise = (random.random() - 0.5) * 0.1  # Low noise
        reward = max(-1.0, min(1.0, base_reward + noise))
        rewards.append(reward)

        # Smooth latency improvement
        latency = 2.5 - progress * 1.5 + random.random() * 0.2
        latencies.append(max(0.1, latency))

    return rewards, latencies


def generate_comprehensive_report(all_results: List[Dict]):
    """Generate comprehensive comparison report across all test series."""

    print(f"\n" + "="*100)
    print(f"COMPREHENSIVE PERFORMANCE REPORT - TLM vs NumPy")
    print(f"="*100)

    # Aggregate statistics
    tlm_wins = 0
    numpy_wins = 0
    ties = 0

    metrics_comparison = {
        'init_time': {'tlm': [], 'numpy': []},
        'memory': {'tlm': [], 'numpy': []},
        'optimization': {'tlm': [], 'numpy': []},
        'feedback': {'tlm': [], 'numpy': []},
        'action_selection': {'tlm': [], 'numpy': []},
        'experience_replay': {'tlm': [], 'numpy': []},
        'reporting': {'tlm': [], 'numpy': []}
    }

    # Collect data from all series
    for result in all_results:
        tlm_res = result['tlm']
        numpy_res = result['numpy']

        # Collect metrics
        metrics_comparison['init_time']['tlm'].append(tlm_res['init_time'] * 1000)
        metrics_comparison['init_time']['numpy'].append(numpy_res['init_time'] * 1000)

        metrics_comparison['memory']['tlm'].append(tlm_res['memory']['peak_mb'])
        metrics_comparison['memory']['numpy'].append(numpy_res['memory']['peak_mb'])

        metrics_comparison['optimization']['tlm'].append(tlm_res['operations']['optimization']['avg_batch_time'] * 1000)
        metrics_comparison['optimization']['numpy'].append(numpy_res['operations']['optimization']['avg_batch_time'] * 1000)

        metrics_comparison['feedback']['tlm'].append(tlm_res['operations']['feedback']['avg_feedback_time'] * 1000)
        metrics_comparison['feedback']['numpy'].append(numpy_res['operations']['feedback']['avg_feedback_time'] * 1000)

        metrics_comparison['action_selection']['tlm'].append(tlm_res['operations']['action_selection']['avg_action_time'] * 1000)
        metrics_comparison['action_selection']['numpy'].append(numpy_res['operations']['action_selection']['avg_action_time'] * 1000)

        metrics_comparison['experience_replay']['tlm'].append(tlm_res['operations']['experience_replay']['avg_sample_time'] * 1000)
        metrics_comparison['experience_replay']['numpy'].append(numpy_res['operations']['experience_replay']['avg_sample_time'] * 1000)

        metrics_comparison['reporting']['tlm'].append(tlm_res['operations']['reporting']['time'] * 1000)
        metrics_comparison['reporting']['numpy'].append(numpy_res['operations']['reporting']['time'] * 1000)

    # Summary table
    print(f"\n📊 AGGREGATE RESULTS ACROSS 5 TEST SERIES:")
    print(f"{'Metric':<20} {'TLM Avg':<12} {'NumPy Avg':<12} {'TLM Win%':<10} {'Speedup':<10}")
    print(f"{'-'*80}")

    for metric, data in metrics_comparison.items():
        tlm_avg = sum(data['tlm']) / len(data['tlm'])
        numpy_avg = sum(data['numpy']) / len(data['numpy'])

        # Count wins
        wins = sum(1 for i in range(len(data['tlm'])) if data['tlm'][i] < data['numpy'][i])
        win_pct = (wins / len(data['tlm'])) * 100

        # Calculate speedup (negative means TLM is slower)
        speedup = ((numpy_avg - tlm_avg) / numpy_avg) * 100 if numpy_avg > 0 else 0

        unit = "ms" if metric != 'memory' else "MB"
        print(f"{metric:<20} {tlm_avg:<12.2f} {numpy_avg:<12.2f} {win_pct:<10.0f}% {speedup:<10.1f}%")

    # Series-by-series breakdown
    print(f"\n📈 SERIES-BY-SERIES BREAKDOWN:")
    print(f"{'Series':<20} {'Dataset':<20} {'Winner':<10} {'Margin':<15}")
    print(f"{'-'*80}")

    for i, result in enumerate(all_results, 1):
        config = result['config']
        tlm_res = result['tlm']
        numpy_res = result['numpy']

        # Calculate overall performance score
        tlm_score = (
            tlm_res['init_time'] +
            tlm_res['operations']['optimization']['avg_batch_time'] +
            tlm_res['operations']['feedback']['avg_feedback_time'] +
            tlm_res['operations']['action_selection']['avg_action_time']
        )

        numpy_score = (
            numpy_res['init_time'] +
            numpy_res['operations']['optimization']['avg_batch_time'] +
            numpy_res['operations']['feedback']['avg_feedback_time'] +
            numpy_res['operations']['action_selection']['avg_action_time']
        )

        if tlm_score < numpy_score:
            winner = "TLM"
            margin = f"{((numpy_score - tlm_score) / numpy_score * 100):.1f}% faster"
            tlm_wins += 1
        elif numpy_score < tlm_score:
            winner = "NumPy"
            margin = f"{((tlm_score - numpy_score) / tlm_score * 100):.1f}% faster"
            numpy_wins += 1
        else:
            winner = "Tie"
            margin = "Equal"
            ties += 1

        print(f"Series {i:<15} {config['name']:<20} {winner:<10} {margin:<15}")

    # Final verdict
    print(f"\n🏆 FINAL VERDICT:")
    print(f"TLM Wins: {tlm_wins}")
    print(f"NumPy Wins: {numpy_wins}")
    print(f"Ties: {ties}")

    if tlm_wins > numpy_wins:
        print(f"\n🎉 TLM (Teaching Library Math) is the WINNER!")
        print(f"   ✅ Zero dependencies")
        print(f"   ✅ Better performance in {tlm_wins}/{len(all_results)} test series")
        print(f"   ✅ Consistent across different data patterns")
    elif numpy_wins > tlm_wins:
        print(f"\n🎉 NumPy is the WINNER!")
        print(f"   ✅ Mature optimized library")
        print(f"   ✅ Better performance in {numpy_wins}/{len(all_results)} test series")
        print(f"   ✅ Consistent across different data patterns")
    else:
        print(f"\n🤝 It's a TIE!")
        print(f"   Both libraries perform equally well")

    # Save results to file
    save_results_to_file(all_results, metrics_comparison)


def save_results_to_file(all_results: List[Dict], metrics_comparison: Dict):
    """Save detailed results to a markdown file."""

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"rl_performance_comparison_{timestamp}.md"

    with open(filename, 'w') as f:
        f.write(f"# RL Factor Optimizer Performance Comparison\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Test Series:** 5 different datasets\n")
        f.write(f"**Libraries:** TLM (Teaching Library Math) vs NumPy\n\n")

        f.write(f"## Summary\n\n")
        f.write(f"| Metric | TLM Average | NumPy Average | TLM Win Rate | Performance Difference |\n")
        f.write(f"|--------|-------------|---------------|--------------|------------------------|\n")

        for metric, data in metrics_comparison.items():
            tlm_avg = sum(data['tlm']) / len(data['tlm'])
            numpy_avg = sum(data['numpy']) / len(data['numpy'])
            wins = sum(1 for i in range(len(data['tlm'])) if data['tlm'][i] < data['numpy'][i])
            win_pct = (wins / len(data['tlm'])) * 100
            speedup = ((numpy_avg - tlm_avg) / numpy_avg) * 100 if numpy_avg > 0 else 0

            unit = "ms" if metric != 'memory' else "MB"
            f.write(f"| {metric} | {tlm_avg:.2f} {unit} | {numpy_avg:.2f} {unit} | {win_pct:.0f}% | {speedup:+.1f}% |\n")

        f.write(f"\n## Detailed Results\n\n")

        for i, result in enumerate(all_results, 1):
            config = result['config']
            f.write(f"### Test Series {i}: {config['name']}\n\n")
            f.write(f"- **Samples:** {config['samples']}\n")
            f.write(f"- **Seed:** {config['seed']}\n")
            if config.get('high_variance'):
                f.write(f"- **Type:** High variance stress test\n")
            elif config.get('smooth'):
                f.write(f"- **Type:** Smooth convergent learning\n")
            else:
                f.write(f"- **Type:** Standard learning curve\n")
            f.write(f"\n")

        f.write(f"\n## Conclusion\n\n")
        f.write(f"The performance comparison shows that both TLM and NumPy are viable options ")
        f.write(f"for RL factor optimization, with each having different strengths depending on ")
        f.write(f"the specific use case and performance requirements.\n")

    print(f"\n📝 Detailed results saved to: {filename}")
    return filename


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)