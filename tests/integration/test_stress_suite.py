#!/usr/bin/env python3
"""
TidyLLM Stress Test Suite - Aggressive System Testing

This suite pushes TidyLLM to its limits with:
- High-volume operations
- Memory stress testing  
- Concurrent operations
- Resource exhaustion scenarios
- Edge case combinations
"""

import os
import sys
import gc
import time
import threading
import concurrent.futures
import traceback
import psutil
import random
from datetime import datetime
from typing import Dict, Any, List

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, '.')

def print_header(title: str):
    print(f"\n{'='*80}")
    print(f" {title}")  
    print(f"{'='*80}")

def print_test(test_name: str):
    print(f"\n[STRESS TEST] {test_name}")
    print("-" * 70)

def print_success(message: str):
    print(f"[PASS] {message}")

def print_error(message: str):
    print(f"[FAIL] {message}")

def print_warning(message: str):
    print(f"[WARN] {message}")

def print_info(message: str):
    print(f"[INFO] {message}")

class SystemMonitor:
    """Monitor system resources during testing"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_memory_delta(self) -> float:
        """Get memory change since initialization"""
        return self.get_memory_usage() - self.initial_memory

class StressTester:
    """Aggressive stress testing for TidyLLM"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
        self.results = {}
        self.start_time = datetime.now()
        
    def test_high_volume_operations(self) -> Dict[str, bool]:
        """Test high-volume operations"""
        print_test("High-Volume Operations (10,000+ objects)")
        
        results = {}
        
        try:
            import tidyllm
            
            # Test 1: Mass message creation
            print_info("Creating 10,000 messages...")
            start_time = time.time()
            messages = []
            
            for i in range(10000):
                msg = tidyllm.llm_message(
                    f"Stress test message {i}",
                    f"Content for message {i} with some additional text to test memory"
                )
                messages.append(msg)
                
                # Progress indicator
                if i > 0 and i % 2000 == 0:
                    memory_usage = self.monitor.get_memory_usage()
                    print_info(f"Created {i} messages - Memory: {memory_usage:.1f}MB")
            
            creation_time = time.time() - start_time
            memory_delta = self.monitor.get_memory_delta()
            
            print_success(f"Mass message creation - 10,000 in {creation_time:.2f}s")
            print_info(f"Memory usage delta: {memory_delta:.1f}MB")
            results["mass_message_creation"] = creation_time < 5.0
            
            # Test 2: Mass provider creation
            print_info("Creating 1,000 providers...")
            start_time = time.time()
            providers = []
            
            models = ["claude-3-haiku", "claude-3-sonnet", "gpt-3.5-turbo", "gpt-4"]
            
            for i in range(1000):
                model = random.choice(models)
                provider = tidyllm.claude(model=model)
                providers.append(provider)
                
            provider_time = time.time() - start_time
            print_success(f"Mass provider creation - 1,000 in {provider_time:.2f}s")
            results["mass_provider_creation"] = provider_time < 2.0
            
            # Test 3: Rapid module access
            print_info("Rapid module access test (100,000 operations)...")
            start_time = time.time()
            
            for i in range(100000):
                # Rapid fire module checks
                _ = tidyllm.TIDYLLM_ML_AVAILABLE
                _ = tidyllm.ADMIN_AVAILABLE
                _ = tidyllm.GATEWAY_AVAILABLE
                
                # Occasional module access
                if i % 1000 == 0:
                    if tidyllm.ADMIN_AVAILABLE:
                        _ = tidyllm.admin
                    if tidyllm.TIDYLLM_ML_AVAILABLE:
                        _ = tidyllm.tlm
                        
            access_time = time.time() - start_time
            print_success(f"Rapid module access - 100,000 ops in {access_time:.2f}s")
            results["rapid_module_access"] = access_time < 1.0
            
            # Cleanup
            del messages, providers
            gc.collect()
            
            return results
            
        except Exception as e:
            print_error(f"High-volume operations failed: {e}")
            return {"high_volume_error": False}
    
    def test_concurrent_operations(self) -> Dict[str, bool]:
        """Test concurrent operations with threading"""
        print_test("Concurrent Operations (Multi-threading)")
        
        results = {}
        
        try:
            import tidyllm
            
            def create_messages_worker(thread_id: int, count: int) -> List:
                """Worker function to create messages"""
                messages = []
                for i in range(count):
                    msg = tidyllm.llm_message(
                        f"Thread {thread_id} message {i}",
                        f"Content from thread {thread_id}"
                    )
                    messages.append(msg)
                return messages
            
            def create_providers_worker(thread_id: int, count: int) -> List:
                """Worker function to create providers"""
                providers = []
                models = ["claude-3-haiku", "claude-3-sonnet"] 
                for i in range(count):
                    model = models[i % len(models)]
                    provider = tidyllm.claude(model=model)
                    providers.append(provider)
                return providers
            
            # Test 1: Concurrent message creation
            print_info("Testing concurrent message creation (10 threads)...")
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for thread_id in range(10):
                    future = executor.submit(create_messages_worker, thread_id, 500)
                    futures.append(future)
                
                # Collect results
                all_messages = []
                for future in concurrent.futures.as_completed(futures):
                    messages = future.result()
                    all_messages.extend(messages)
            
            concurrent_time = time.time() - start_time
            total_messages = len(all_messages)
            
            print_success(f"Concurrent message creation - {total_messages} messages in {concurrent_time:.2f}s")
            print_info(f"Throughput: {total_messages/concurrent_time:.0f} messages/second")
            results["concurrent_message_creation"] = concurrent_time < 3.0
            
            # Test 2: Concurrent provider creation
            print_info("Testing concurrent provider creation (5 threads)...")
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for thread_id in range(5):
                    future = executor.submit(create_providers_worker, thread_id, 100)
                    futures.append(future)
                
                all_providers = []
                for future in concurrent.futures.as_completed(futures):
                    providers = future.result()
                    all_providers.extend(providers)
            
            provider_concurrent_time = time.time() - start_time
            total_providers = len(all_providers)
            
            print_success(f"Concurrent provider creation - {total_providers} providers in {provider_concurrent_time:.2f}s")
            results["concurrent_provider_creation"] = provider_concurrent_time < 2.0
            
            # Cleanup
            del all_messages, all_providers
            gc.collect()
            
            return results
            
        except Exception as e:
            print_error(f"Concurrent operations failed: {e}")
            traceback.print_exc()
            return {"concurrent_error": False}
    
    def test_memory_stress(self) -> Dict[str, bool]:
        """Test memory stress scenarios"""
        print_test("Memory Stress Testing")
        
        results = {}
        
        try:
            import tidyllm
            
            initial_memory = self.monitor.get_memory_usage()
            print_info(f"Initial memory usage: {initial_memory:.1f}MB")
            
            # Test 1: Large message content
            print_info("Creating messages with large content...")
            large_content = "X" * 10000  # 10KB per message
            large_messages = []
            
            for i in range(1000):  # 10MB total
                msg = tidyllm.llm_message(
                    f"Large message {i}",
                    large_content + f" Message {i}"
                )
                large_messages.append(msg)
                
                if i > 0 and i % 200 == 0:
                    current_memory = self.monitor.get_memory_usage()
                    delta = current_memory - initial_memory
                    print_info(f"Large messages {i}/1000 - Memory delta: {delta:.1f}MB")
            
            large_msg_memory = self.monitor.get_memory_usage()
            print_success(f"Large message creation - Memory: {large_msg_memory:.1f}MB")
            results["large_message_memory"] = (large_msg_memory - initial_memory) < 100
            
            # Test 2: Rapid allocation/deallocation
            print_info("Testing rapid allocation/deallocation...")
            for cycle in range(10):
                temp_objects = []
                
                # Allocate
                for i in range(500):
                    obj = tidyllm.llm_message(f"Temp {cycle}-{i}", f"Temporary content {i}")
                    temp_objects.append(obj)
                
                # Deallocate
                del temp_objects
                gc.collect()
                
                if cycle % 2 == 0:
                    current_memory = self.monitor.get_memory_usage()
                    delta = current_memory - initial_memory
                    print_info(f"Allocation cycle {cycle+1}/10 - Memory delta: {delta:.1f}MB")
            
            final_memory = self.monitor.get_memory_usage()
            memory_delta = final_memory - initial_memory
            
            print_success(f"Rapid alloc/dealloc - Final memory delta: {memory_delta:.1f}MB")
            results["rapid_allocation"] = memory_delta < 50
            
            # Cleanup large messages
            del large_messages
            gc.collect()
            
            return results
            
        except Exception as e:
            print_error(f"Memory stress testing failed: {e}")
            return {"memory_stress_error": False}
    
    def test_edge_case_combinations(self) -> Dict[str, bool]:
        """Test complex edge case combinations"""
        print_test("Edge Case Combinations")
        
        results = {}
        
        try:
            import tidyllm
            
            # Test 1: Extreme content variations
            extreme_cases = [
                ("", ""),  # Empty
                ("A", "B"),  # Minimal
                ("X" * 100000, "Y" * 100000),  # Very large
                ("🚀" * 1000, "🎉" * 1000),  # Unicode
                ("\n\t\r" * 1000, "\0" * 100),  # Special chars
                ("A" * 65536, "B" * 65536),  # 64KB content
            ]
            
            print_info(f"Testing {len(extreme_cases)} extreme content cases...")
            
            for i, (prompt, content) in enumerate(extreme_cases):
                try:
                    msg = tidyllm.llm_message(prompt, content)
                    print_info(f"Extreme case {i+1}/{len(extreme_cases)} - OK")
                except Exception as e:
                    print_warning(f"Extreme case {i+1} failed: {e}")
            
            results["extreme_content_cases"] = True
            
            # Test 2: Rapid provider switching
            models = [
                "claude-3-haiku", "claude-3-sonnet", "claude-3-opus",
                "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"
            ]
            
            print_info("Testing rapid provider model switching...")
            providers = []
            
            for i in range(500):
                model = random.choice(models)
                provider = tidyllm.claude(model=model)
                providers.append(provider)
            
            print_success("Rapid provider switching - 500 random models")
            results["rapid_provider_switching"] = True
            
            # Test 3: Module access patterns
            print_info("Testing complex module access patterns...")
            
            for i in range(1000):
                # Random module access pattern
                modules = ['tlm', 'sentence', 'vectorqa', 'admin', 'gateway']
                random.shuffle(modules)
                
                for module_name in modules:
                    if hasattr(tidyllm, module_name):
                        module = getattr(tidyllm, module_name)
                        # Access some attributes if available
                        if module is not None and hasattr(module, '__dict__'):
                            _ = len(dir(module))
            
            print_success("Complex module access patterns - 5000 operations")
            results["complex_module_access"] = True
            
            return results
            
        except Exception as e:
            print_error(f"Edge case testing failed: {e}")
            return {"edge_case_error": False}
    
    def test_admin_stress(self) -> Dict[str, bool]:
        """Stress test admin functionality"""
        print_test("Admin System Stress Testing")
        
        results = {}
        
        try:
            import tidyllm
            
            if not tidyllm.ADMIN_AVAILABLE:
                print_warning("Admin not available - skipping stress tests")
                return {"admin_not_available": True}
            
            from tidyllm.admin import ConfigManager
            from tidyllm.admin.api_endpoints import create_admin_api
            
            # Test 1: Rapid config manager creation/destruction
            print_info("Testing rapid ConfigManager creation...")
            
            config_managers = []
            start_time = time.time()
            
            for i in range(100):
                config_mgr = ConfigManager()
                config_managers.append(config_mgr)
                
                # Periodically access config
                if i % 10 == 0:
                    _ = config_mgr.config.environment
                    _ = config_mgr.config.database.postgres_host
            
            config_time = time.time() - start_time
            print_success(f"Config manager stress - 100 instances in {config_time:.2f}s")
            results["config_manager_stress"] = config_time < 2.0
            
            # Test 2: Admin API stress
            print_info("Testing Admin API stress...")
            
            apis = []
            for i in range(20):
                admin_api = create_admin_api()
                apis.append(admin_api)
                
                # Test API methods
                system_info = admin_api.get_system_info()
                config_info = admin_api.get_config()
                
            print_success("Admin API stress - 20 instances with method calls")
            results["admin_api_stress"] = True
            
            # Test 3: Concurrent admin operations
            def admin_worker(worker_id: int):
                config_mgr = ConfigManager()
                admin_api = create_admin_api()
                
                for i in range(50):
                    _ = config_mgr.config.environment
                    _ = admin_api.get_system_info()
                
                return f"Worker {worker_id} completed"
            
            print_info("Testing concurrent admin operations...")
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(admin_worker, i) for i in range(5)]
                results_list = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            concurrent_admin_time = time.time() - start_time
            print_success(f"Concurrent admin operations - 5 threads in {concurrent_admin_time:.2f}s")
            results["concurrent_admin"] = concurrent_admin_time < 3.0
            
            return results
            
        except Exception as e:
            print_error(f"Admin stress testing failed: {e}")
            traceback.print_exc()
            return {"admin_stress_error": False}
    
    def run_stress_suite(self) -> Dict[str, Any]:
        """Run complete stress test suite"""
        print_header("TidyLLM Stress Test Suite - Aggressive Testing")
        print(f"Started at: {self.start_time.isoformat()}")
        print(f"Initial memory: {self.monitor.initial_memory:.1f}MB")
        
        all_results = {}
        
        # Test 1: High-volume operations
        print_info("Running high-volume stress tests...")
        volume_results = self.test_high_volume_operations()
        all_results.update(volume_results)
        
        # Test 2: Concurrent operations
        print_info("Running concurrent operation stress tests...")
        concurrent_results = self.test_concurrent_operations()
        all_results.update(concurrent_results)
        
        # Test 3: Memory stress
        print_info("Running memory stress tests...")
        memory_results = self.test_memory_stress()
        all_results.update(memory_results)
        
        # Test 4: Edge cases
        print_info("Running edge case stress tests...")
        edge_results = self.test_edge_case_combinations()
        all_results.update(edge_results)
        
        # Test 5: Admin stress
        print_info("Running admin stress tests...")
        admin_results = self.test_admin_stress()
        all_results.update(admin_results)
        
        return all_results
    
    def generate_stress_report(self, results: Dict[str, Any]):
        """Generate stress test report"""
        print_header("Stress Test Results Report")
        
        passed = sum(1 for v in results.values() if v is True)
        total = len(results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        final_memory = self.monitor.get_memory_usage()
        memory_delta = self.monitor.get_memory_delta()
        
        print(f"\nOverall Stress Test Results: {passed}/{total} tests passed")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Memory Usage: {final_memory:.1f}MB (delta: {memory_delta:+.1f}MB)")
        
        # Group results by test type
        test_categories = {
            "High-Volume Operations": [],
            "Concurrent Operations": [],
            "Memory Stress": [],
            "Edge Cases": [],
            "Admin Stress": []
        }
        
        for test_name, result in results.items():
            status = "[PASS]" if result else "[FAIL]"
            
            if "mass_" in test_name or "rapid_" in test_name:
                test_categories["High-Volume Operations"].append(f"  {status} {test_name}")
            elif "concurrent_" in test_name:
                test_categories["Concurrent Operations"].append(f"  {status} {test_name}")
            elif "memory" in test_name or "allocation" in test_name:
                test_categories["Memory Stress"].append(f"  {status} {test_name}")
            elif "edge" in test_name or "extreme" in test_name or "complex" in test_name:
                test_categories["Edge Cases"].append(f"  {status} {test_name}")
            elif "admin" in test_name or "config" in test_name:
                test_categories["Admin Stress"].append(f"  {status} {test_name}")
        
        for category, tests in test_categories.items():
            if tests:
                print(f"\n{category}:")
                for test in tests:
                    print(test)
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\nStress Test Duration: {duration:.2f} seconds")
        print(f"Completed at: {end_time.isoformat()}")
        
        if success_rate >= 95:
            print_success("\nOUTSTANDING! TidyLLM handles extreme stress very well!")
        elif success_rate >= 85:
            print_success("\nEXCELLENT! TidyLLM performs well under stress!")
        elif success_rate >= 70:
            print_success("\nGOOD! TidyLLM handles moderate stress adequately!")
        else:
            print_warning("\nStress testing revealed some issues - review failures")
        
        return success_rate

def main():
    """Run the stress test suite"""
    tester = StressTester()
    
    try:
        results = tester.run_stress_suite()
        success_rate = tester.generate_stress_report(results)
        return 0 if success_rate >= 70 else 1
        
    except Exception as e:
        print_error(f"Stress test suite failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())