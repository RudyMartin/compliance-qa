"""
Test Execution Monitor
=====================

Provides real-time status updates and comprehensive monitoring for A/B/C/D testing.
Handles failures gracefully and ensures users never wait indefinitely.
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
from datetime import datetime, timedelta
import json
import traceback
from pathlib import Path

import logging
from .dual_ai_ab_testing import DualAIResult

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status enumeration."""
    PENDING = "pending"
    STARTING = "starting"
    STAGE1_RUNNING = "stage1_running"
    STAGE1_COMPLETE = "stage1_complete"
    STAGE2_RUNNING = "stage2_running"
    STAGE2_COMPLETE = "stage2_complete"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TestProgress:
    """Individual test progress tracking."""
    test_id: str
    test_name: str
    status: TestStatus
    start_time: Optional[datetime] = None
    stage1_time: Optional[float] = None
    stage2_time: Optional[float] = None
    total_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[DualAIResult] = None

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time since test started."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    @property
    def status_emoji(self) -> str:
        """Get emoji representation of status."""
        emoji_map = {
            TestStatus.PENDING: "⏳",
            TestStatus.STARTING: "🚀",
            TestStatus.STAGE1_RUNNING: "🤖",
            TestStatus.STAGE1_COMPLETE: "✅",
            TestStatus.STAGE2_RUNNING: "🔧",
            TestStatus.STAGE2_COMPLETE: "✅",
            TestStatus.COMPLETED: "🎉",
            TestStatus.FAILED: "❌",
            TestStatus.TIMEOUT: "⏰"
        }
        return emoji_map.get(self.status, "❓")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "elapsed_time": self.elapsed_time,
            "stage1_time": self.stage1_time,
            "stage2_time": self.stage2_time,
            "total_time": self.total_time,
            "error_message": self.error_message,
            "has_result": self.result is not None
        }


@dataclass
class ExecutionSummary:
    """Overall execution summary."""
    total_tests: int
    completed_tests: int
    failed_tests: int
    pending_tests: int
    execution_mode: str
    start_time: datetime
    estimated_completion: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.completed_tests / self.total_tests) * 100

    @property
    def elapsed_time(self) -> float:
        """Get total elapsed time."""
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "total_tests": self.total_tests,
            "completed_tests": self.completed_tests,
            "failed_tests": self.failed_tests,
            "pending_tests": self.pending_tests,
            "success_rate": self.success_rate,
            "execution_mode": self.execution_mode,
            "elapsed_time": self.elapsed_time,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None
        }


class TestExecutionMonitor:
    """
    Monitor and report on A/B/C/D test execution with real-time status updates.

    Features:
    - Real-time progress tracking
    - Timeout detection and handling
    - Status callbacks for UI integration
    - Comprehensive failure reporting
    - Executive report generation triggers
    """

    def __init__(self,
                 selected_tests: List[str],
                 execution_mode: str = "parallel",
                 timeout_seconds: int = 300,
                 status_callback: Optional[Callable] = None,
                 project_name: str = "alex_qaqc"):
        """
        Initialize test execution monitor.

        Args:
            selected_tests: List of test IDs to monitor
            execution_mode: 'parallel' or 'sequential'
            timeout_seconds: Maximum time to wait for each test
            status_callback: Optional callback for status updates
            project_name: Project name for output folder structure
        """
        self.selected_tests = selected_tests
        self.execution_mode = execution_mode
        self.timeout_seconds = timeout_seconds
        self.status_callback = status_callback
        self.project_name = project_name

        # Test tracking
        self.test_progress: Dict[str, TestProgress] = {}
        self.execution_summary: Optional[ExecutionSummary] = None
        self.start_time: Optional[datetime] = None

        # Status monitoring
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Error logging
        self.error_log = []

        # Get portable output path using USM Project Paths service - PORTABLE for any environment
        try:
            from ..infrastructure.session.unified import UnifiedSessionManager
            session_mgr = UnifiedSessionManager()
            self.outputs_folder = session_mgr.ensure_project_outputs_exist(project_name)
            logger.info(f"Using USM Project Paths service - Error logs: {self.outputs_folder.absolute()}")
        except Exception as e:
            logger.error(f"CRITICAL: Could not get USM Project Paths service: {e}")
            # Emergency fallback - but this will break when moved
            self.outputs_folder = Path("tidyllm/workflows/projects") / project_name / "outputs"
            self.outputs_folder.mkdir(parents=True, exist_ok=True)

        # Test configurations for display names (Windows-safe)
        self.test_names = {
            "A": "Speed Focus (Haiku->Sonnet)",
            "B": "Quality Focus (Sonnet->3.5-Sonnet)",
            "C": "Premium Focus (Haiku->3.5-Sonnet)",
            "D": "DSPy Optimized (Haiku->Sonnet+DSPy)"
        }

        logger.info(f"Test monitor initialized for {len(selected_tests)} tests in {execution_mode} mode")
        logger.info(f"Error logs will be saved to: {self.outputs_folder}")

    def start_monitoring(self) -> None:
        """Start monitoring test execution."""
        self.start_time = datetime.now()

        # Initialize test progress tracking
        for test_id in self.selected_tests:
            self.test_progress[test_id] = TestProgress(
                test_id=test_id,
                test_name=self.test_names.get(test_id, f"Test {test_id}"),
                status=TestStatus.PENDING
            )

        # Initialize execution summary
        self.execution_summary = ExecutionSummary(
            total_tests=len(self.selected_tests),
            completed_tests=0,
            failed_tests=0,
            pending_tests=len(self.selected_tests),
            execution_mode=self.execution_mode,
            start_time=self.start_time
        )

        # Start background monitoring
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        logger.info(f"Started monitoring {len(self.selected_tests)} tests")
        self._broadcast_status("Monitoring started")

    def update_test_status(self, test_id: str, status: TestStatus, **kwargs) -> None:
        """Update the status of a specific test."""
        with self._lock:
            if test_id not in self.test_progress:
                logger.warning(f"Unknown test ID: {test_id}")
                return

            progress = self.test_progress[test_id]
            old_status = progress.status
            progress.status = status

            # Handle status-specific updates
            if status == TestStatus.STARTING and not progress.start_time:
                progress.start_time = datetime.now()
            elif status == TestStatus.STAGE1_COMPLETE and 'stage1_time' in kwargs:
                progress.stage1_time = kwargs['stage1_time']
            elif status == TestStatus.STAGE2_COMPLETE and 'stage2_time' in kwargs:
                progress.stage2_time = kwargs['stage2_time']
            elif status == TestStatus.COMPLETED:
                progress.total_time = progress.elapsed_time
                if 'result' in kwargs:
                    progress.result = kwargs['result']
                self._update_summary_counts()
            elif status == TestStatus.FAILED:
                error_msg = kwargs.get('error', 'Unknown error')
                progress.error_message = error_msg
                self._log_test_error(test_id, error_msg, kwargs.get('exception', None))
                self._update_summary_counts()

            logger.info(f"Test {test_id} status: {old_status.value} -> {status.value}")
            self._broadcast_status(f"Test {test_id}: {status.value}")

    def _update_summary_counts(self) -> None:
        """Update execution summary counts."""
        if not self.execution_summary:
            return

        completed = sum(1 for p in self.test_progress.values() if p.status == TestStatus.COMPLETED)
        failed = sum(1 for p in self.test_progress.values() if p.status == TestStatus.FAILED)
        pending = sum(1 for p in self.test_progress.values()
                     if p.status in [TestStatus.PENDING, TestStatus.STARTING,
                                   TestStatus.STAGE1_RUNNING, TestStatus.STAGE2_RUNNING])

        self.execution_summary.completed_tests = completed
        self.execution_summary.failed_tests = failed
        self.execution_summary.pending_tests = pending

    def _log_test_error(self, test_id: str, error_message: str, exception: Exception = None) -> None:
        """Log detailed error information to outputs folder."""
        timestamp = datetime.now().isoformat()

        error_entry = {
            "timestamp": timestamp,
            "test_id": test_id,
            "test_name": self.test_names.get(test_id, f"Test {test_id}"),
            "error_message": error_message,
            "execution_mode": self.execution_mode,
            "project": self.project_name
        }

        # Add exception details if available
        if exception:
            error_entry.update({
                "exception_type": type(exception).__name__,
                "exception_str": str(exception),
                "traceback": traceback.format_exception(type(exception), exception, exception.__traceback__)
            })

        # Add to in-memory log
        self.error_log.append(error_entry)

        # Save individual error log file
        error_filename = f"test_{test_id}_error_{timestamp.replace(':', '-').split('.')[0]}.json"
        error_filepath = self.outputs_folder / error_filename

        try:
            with open(error_filepath, 'w', encoding='utf-8') as f:
                json.dump(error_entry, f, indent=2, ensure_ascii=False)
            logger.info(f"Error details saved to: {error_filepath}")
        except Exception as e:
            logger.error(f"Failed to save error log: {e}")

        # Also save to master error log
        self._update_master_error_log()

    def _update_master_error_log(self) -> None:
        """Update the master error log with all test errors."""
        if not self.error_log:
            return

        master_log = {
            "execution_session": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "execution_mode": self.execution_mode,
                "selected_tests": self.selected_tests,
                "project": self.project_name
            },
            "errors": self.error_log,
            "summary": {
                "total_errors": len(self.error_log),
                "failed_tests": list(set(error["test_id"] for error in self.error_log))
            }
        }

        master_log_path = self.outputs_folder / f"test_execution_errors_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(master_log_path, 'w', encoding='utf-8') as f:
                json.dump(master_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to update master error log: {e}")

    def log_system_error(self, error_context: str, error_message: str, exception: Exception = None) -> None:
        """Log system-level errors (not specific to a test)."""
        timestamp = datetime.now().isoformat()

        system_error = {
            "timestamp": timestamp,
            "context": error_context,
            "error_message": error_message,
            "execution_mode": self.execution_mode,
            "project": self.project_name,
            "is_system_error": True
        }

        if exception:
            system_error.update({
                "exception_type": type(exception).__name__,
                "exception_str": str(exception),
                "traceback": traceback.format_exception(type(exception), exception, exception.__traceback__)
            })

        # Save system error log
        system_error_filename = f"system_error_{timestamp.replace(':', '-').split('.')[0]}.json"
        system_error_path = self.outputs_folder / system_error_filename

        try:
            with open(system_error_path, 'w', encoding='utf-8') as f:
                json.dump(system_error, f, indent=2, ensure_ascii=False)
            logger.error(f"System error logged to: {system_error_path}")
        except Exception as e:
            logger.error(f"Failed to save system error log: {e}")

    def save_execution_summary(self) -> str:
        """Save complete execution summary including errors to outputs folder."""
        if not self.start_time:
            return ""

        summary = {
            "execution_metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "execution_mode": self.execution_mode,
                "selected_tests": self.selected_tests,
                "project": self.project_name,
                "timeout_seconds": self.timeout_seconds
            },
            "test_results": {
                test_id: progress.to_dict()
                for test_id, progress in self.test_progress.items()
            },
            "execution_summary": self.execution_summary.to_dict() if self.execution_summary else {},
            "error_summary": {
                "total_errors": len(self.error_log),
                "error_log": self.error_log
            },
            "recommendations": self._generate_recommendations()
        }

        summary_filename = f"test_execution_summary_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        summary_path = self.outputs_folder / summary_filename

        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Execution summary saved to: {summary_path}")
            return str(summary_path)
        except Exception as e:
            logger.error(f"Failed to save execution summary: {e}")
            return ""

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results and errors."""
        recommendations = []

        if not self.test_progress:
            return ["No test data available for analysis"]

        # Analyze failure patterns
        failed_tests = [test_id for test_id, progress in self.test_progress.items()
                       if progress.status == TestStatus.FAILED]

        if len(failed_tests) == len(self.selected_tests):
            recommendations.append("All tests failed - check AWS/USM configuration and network connectivity")
            recommendations.append("Verify model availability and access permissions")
            recommendations.append("Check system logs for initialization errors")
        elif len(failed_tests) > 0:
            recommendations.append(f"Tests {', '.join(failed_tests)} failed - review individual error logs")
            recommendations.append("Consider running failed tests individually for debugging")

        # Performance analysis
        completed_tests = [progress for progress in self.test_progress.values()
                          if progress.status == TestStatus.COMPLETED]

        if completed_tests:
            times = [p.total_time for p in completed_tests if p.total_time]
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > 60:
                    recommendations.append("Average execution time > 60s - consider faster model combinations")
                if max(times) - min(times) > 30:
                    recommendations.append("High variance in execution times - check for network/system issues")

        # Timeout analysis
        timeout_tests = [test_id for test_id, progress in self.test_progress.items()
                        if progress.status == TestStatus.TIMEOUT]

        if timeout_tests:
            recommendations.append(f"Tests {', '.join(timeout_tests)} timed out - increase timeout or check for hanging requests")

        return recommendations if recommendations else ["All tests completed successfully - no issues detected"]

    def _monitor_loop(self) -> None:
        """Background monitoring loop for timeout detection."""
        while self._monitoring:
            try:
                with self._lock:
                    current_time = datetime.now()

                    # Check for timeouts
                    for test_id, progress in self.test_progress.items():
                        if (progress.status not in [TestStatus.COMPLETED, TestStatus.FAILED, TestStatus.TIMEOUT]
                            and progress.start_time
                            and progress.elapsed_time > self.timeout_seconds):

                            logger.warning(f"Test {test_id} timed out after {progress.elapsed_time:.1f}s")
                            progress.status = TestStatus.TIMEOUT
                            progress.error_message = f"Test timed out after {self.timeout_seconds}s"
                            self._update_summary_counts()
                            self._broadcast_status(f"Test {test_id}: TIMEOUT")

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(10)

    def stop_monitoring(self) -> str:
        """Stop monitoring and cleanup. Returns path to execution summary."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)

        # Save final execution summary
        summary_path = self.save_execution_summary()

        logger.info("Test monitoring stopped")
        if summary_path:
            logger.info(f"Final execution summary saved to: {summary_path}")

        return summary_path

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        with self._lock:
            return {
                "execution_summary": self.execution_summary.to_dict() if self.execution_summary else None,
                "test_progress": {test_id: progress.to_dict()
                                for test_id, progress in self.test_progress.items()},
                "timestamp": datetime.now().isoformat(),
                "is_complete": self.is_complete(),
                "should_generate_report": self.should_generate_report()
            }

    def is_complete(self) -> bool:
        """Check if all tests are complete (success or failure)."""
        if not self.test_progress:
            return False

        final_statuses = {TestStatus.COMPLETED, TestStatus.FAILED, TestStatus.TIMEOUT}
        return all(progress.status in final_statuses for progress in self.test_progress.values())

    def should_generate_report(self) -> bool:
        """Determine if it's time to generate the executive report."""
        if not self.is_complete():
            return False

        # Generate report if we have at least one successful test
        return any(progress.status == TestStatus.COMPLETED for progress in self.test_progress.values())

    def get_results_for_report(self) -> Dict[str, Any]:
        """Get results formatted for executive report generation."""
        if not self.should_generate_report():
            return {}

        # Format results for executive report
        summary_tests = {}
        for test_id, progress in self.test_progress.items():
            if progress.result:
                summary_tests[test_id] = {
                    "label": progress.test_name,
                    "models": self._get_model_combination(test_id),
                    "total_time_ms": progress.result.total_processing_time_ms,
                    "confidence_improvement": progress.result.confidence_improvement,
                    "total_tokens": getattr(progress.result, 'total_tokens', 0),
                    "status": "completed"
                }
            else:
                summary_tests[test_id] = {
                    "label": progress.test_name,
                    "models": self._get_model_combination(test_id),
                    "total_time_ms": 0,
                    "confidence_improvement": 0,
                    "total_tokens": 0,
                    "status": progress.status.value,
                    "error": progress.error_message
                }

        return {
            "execution_mode": self.execution_mode,
            "summary": {
                "tests": summary_tests,
                "execution_summary": self.execution_summary.to_dict() if self.execution_summary else {}
            }
        }

    def _get_model_combination(self, test_id: str) -> str:
        """Get model combination string for test ID."""
        combinations = {
            "A": "haiku -> sonnet",
            "B": "sonnet -> 3.5-sonnet",
            "C": "haiku -> 3.5-sonnet",
            "D": "haiku -> sonnet+DSPy"
        }
        return combinations.get(test_id, "unknown")

    def _broadcast_status(self, message: str) -> None:
        """Broadcast status update via callback."""
        if self.status_callback:
            try:
                self.status_callback(message, self.get_status_report())
            except Exception as e:
                logger.error(f"Status callback error: {e}")

    def print_status_summary(self) -> None:
        """Print a formatted status summary to console."""
        if not self.execution_summary:
            return

        print("\n" + "="*60)
        print(f"A/B/C/D Test Execution Status")
        print(f"Mode: {self.execution_mode.upper()} | Elapsed: {self.execution_summary.elapsed_time:.1f}s")
        print(f"Progress: {self.execution_summary.completed_tests}/{self.execution_summary.total_tests} completed")
        print(f"Success Rate: {self.execution_summary.success_rate:.1f}%")
        print("="*60)

        for test_id, progress in self.test_progress.items():
            # Use text-based status instead of emojis for Windows compatibility
            status_text = self._get_status_text(progress.status)
            status_line = f"{status_text} Test {test_id}: {progress.test_name}"
            if progress.status == TestStatus.COMPLETED and progress.total_time:
                status_line += f" ({progress.total_time:.1f}s)"
            elif progress.status == TestStatus.FAILED and progress.error_message:
                status_line += f" - {progress.error_message[:50]}..."
            elif progress.start_time:
                status_line += f" ({progress.elapsed_time:.1f}s elapsed)"

            print(status_line)

        if self.is_complete():
            print("\nAll tests complete! Ready for executive report generation.")
        elif self.execution_summary.pending_tests > 0:
            print(f"\n{self.execution_summary.pending_tests} tests still running...")

        print("="*60 + "\n")

    def _get_status_text(self, status: TestStatus) -> str:
        """Get text representation of status (Windows-safe)."""
        status_map = {
            TestStatus.PENDING: "[PENDING]",
            TestStatus.STARTING: "[STARTING]",
            TestStatus.STAGE1_RUNNING: "[STAGE1]",
            TestStatus.STAGE1_COMPLETE: "[STAGE1_OK]",
            TestStatus.STAGE2_RUNNING: "[STAGE2]",
            TestStatus.STAGE2_COMPLETE: "[STAGE2_OK]",
            TestStatus.COMPLETED: "[COMPLETED]",
            TestStatus.FAILED: "[FAILED]",
            TestStatus.TIMEOUT: "[TIMEOUT]"
        }
        return status_map.get(status, "[UNKNOWN]")


def create_monitored_test_wrapper(selected_tests: List[str],
                                execution_mode: str = "parallel",
                                timeout_seconds: int = 300) -> TestExecutionMonitor:
    """
    Factory function to create a test execution monitor.

    Args:
        selected_tests: List of test IDs to monitor
        execution_mode: 'parallel' or 'sequential'
        timeout_seconds: Maximum time to wait for each test

    Returns:
        Configured TestExecutionMonitor instance
    """
    return TestExecutionMonitor(
        selected_tests=selected_tests,
        execution_mode=execution_mode,
        timeout_seconds=timeout_seconds
    )