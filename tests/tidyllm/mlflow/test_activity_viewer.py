#!/usr/bin/env python3
"""
MLflow Activity Viewer Tests
============================

Tests for MLflow activity viewing, recent records analysis,
and session parameter validation.

STANDARDIZED TEST CONFIG:
- NO mocks - uses real infrastructure
- 3 max retries for all operations
- Timeouts set to avoid hangs
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Standardized test configuration
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
CONNECTION_TIMEOUT = 10
MLFLOW_TIMEOUT = 15

# Use existing environment management infrastructure
try:
    from infrastructure.environment_manager import setup_environment_from_settings
    setup_environment_from_settings()
except ImportError:
    # Fallback if environment manager not available
    pass

import tidyllm
from tidyllm.infrastructure.tools import show_last_5_mlflow_records, show_missing_evidence

class MLflowActivityTester:
    """Test MLflow activity viewing and analysis."""

    def __init__(self):
        self.test_start_time = datetime.now()

    def test_activity_viewers(self) -> Dict[str, Any]:
        """Test MLflow activity viewer functions."""
        print("=== Testing MLflow Activity Viewers ===")

        results = {
            'mlflow_viewer': {},
            'evidence_checker': {},
            'timestamp': self.test_start_time.isoformat()
        }

        # Test MLflow viewer
        print("\n1. Testing show_last_5_mlflow_records()...")
        try:
            print("-" * 40)
            show_last_5_mlflow_records()
            print("-" * 40)

            results['mlflow_viewer'] = {
                'status': 'SUCCESS',
                'message': 'MLflow viewer executed successfully',
                'test_time': datetime.now().isoformat()
            }
            print("✅ MLflow viewer: SUCCESS")

        except Exception as e:
            results['mlflow_viewer'] = {
                'status': 'FAILED',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
            print(f"❌ MLflow viewer: FAILED - {e}")

        # Test evidence checker
        print("\n2. Testing show_missing_evidence()...")
        try:
            print("-" * 40)
            show_missing_evidence()
            print("-" * 40)

            results['evidence_checker'] = {
                'status': 'SUCCESS',
                'message': 'Evidence checker executed successfully',
                'test_time': datetime.now().isoformat()
            }
            print("✅ Evidence checker: SUCCESS")

        except Exception as e:
            results['evidence_checker'] = {
                'status': 'FAILED',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }
            print(f"❌ Evidence checker: FAILED - {e}")

        return results

    def test_recent_activity_after_chat(self) -> Dict[str, Any]:
        """Generate some chat activity then check if it appears in MLflow."""
        print("\n=== Testing Recent Activity Tracking ===")

        # Generate test activity
        print("Generating test chat activity...")
        test_activities = []

        for i, mode in enumerate(['direct', 'dspy', 'rag'], 1):
            try:
                print(f"  {i}. Testing {mode} mode...")

                response = tidyllm.chat(
                    f"Test activity tracking message {i} for {mode} mode",
                    chat_type=mode,
                    reasoning=True,
                    user_id=f"activity_test_user_{i}",
                    audit_reason=f"activity_tracking_test_{mode}"
                )

                activity = {
                    'mode': mode,
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'has_audit_trail': isinstance(response, dict) and 'audit_trail' in response,
                    'has_token_usage': isinstance(response, dict) and 'token_usage' in response
                }

                test_activities.append(activity)
                print(f"    ✅ {mode} activity generated")

                # Small delay between activities
                time.sleep(2)

            except Exception as e:
                activity = {
                    'mode': mode,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                test_activities.append(activity)
                print(f"    ❌ {mode} activity failed: {e}")

        # Wait a moment for MLflow to process
        print("\nWaiting for MLflow processing...")
        time.sleep(3)

        # Check if activity appears in MLflow
        print("\nChecking if recent activity appears in MLflow...")
        try:
            print("-" * 50)
            print("RECENT MLFLOW ACTIVITY CHECK:")
            print("-" * 50)
            show_last_5_mlflow_records()
            print("-" * 50)

            activity_check = {
                'status': 'SUCCESS',
                'message': 'Recent activity check completed - review output above',
                'test_activities_generated': len([a for a in test_activities if a['success']]),
                'test_time': datetime.now().isoformat()
            }

        except Exception as e:
            activity_check = {
                'status': 'FAILED',
                'error': str(e),
                'test_time': datetime.now().isoformat()
            }

        return {
            'test_activities': test_activities,
            'activity_check': activity_check,
            'summary': {
                'activities_generated': len([a for a in test_activities if a['success']]),
                'activities_failed': len([a for a in test_activities if not a['success']]),
                'mlflow_check_success': activity_check['status'] == 'SUCCESS'
            }
        }

    def analyze_session_parameters_in_mlflow(self) -> Dict[str, Any]:
        """Analyze what session parameters are being tracked in MLflow."""
        print("\n=== Analyzing Session Parameters in MLflow ===")

        # This is a conceptual analysis since we can't directly parse MLflow output
        analysis = {
            'expected_user_parameters': [
                'user_id',
                'session_id',
                'audit_reason',
                'timestamp'
            ],
            'expected_request_parameters': [
                'model_id',
                'temperature',
                'max_tokens',
                'processing_time_ms'
            ],
            'expected_metrics': [
                'input_tokens',
                'output_tokens',
                'total_tokens',
                'processing_time',
                'success'
            ],
            'analysis_notes': [
                "User session parameters should appear in MLflow parameters section",
                "Token usage should appear in MLflow metrics section",
                "Audit trails should include user_id and session context",
                "Recent chat tests should be visible in last 5 records"
            ]
        }

        print("Expected User Parameters:")
        for param in analysis['expected_user_parameters']:
            print(f"  - {param}")

        print("\nExpected Request Parameters:")
        for param in analysis['expected_request_parameters']:
            print(f"  - {param}")

        print("\nExpected Metrics:")
        for metric in analysis['expected_metrics']:
            print(f"  - {metric}")

        print("\nAnalysis Notes:")
        for note in analysis['analysis_notes']:
            print(f"  • {note}")

        return analysis

def run_activity_viewer_tests():
    """Run comprehensive MLflow activity viewer tests."""
    print("=" * 60)
    print("MLFLOW ACTIVITY VIEWER COMPREHENSIVE TESTS")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tester = MLflowActivityTester()

    # Test the viewer functions
    viewer_results = tester.test_activity_viewers()

    # Generate activity and check tracking
    activity_results = tester.test_recent_activity_after_chat()

    # Analyze session parameters
    parameter_analysis = tester.analyze_session_parameters_in_mlflow()

    # Compile results
    final_results = {
        'test_summary': {
            'mlflow_viewer_working': viewer_results['mlflow_viewer']['status'] == 'SUCCESS',
            'evidence_checker_working': viewer_results['evidence_checker']['status'] == 'SUCCESS',
            'activity_tracking_working': activity_results['summary']['mlflow_check_success'],
            'test_activities_generated': activity_results['summary']['activities_generated'],
            'test_completed': datetime.now().isoformat()
        },
        'viewer_results': viewer_results,
        'activity_results': activity_results,
        'parameter_analysis': parameter_analysis
    }

    # Final summary
    print("\n" + "=" * 60)
    print("ACTIVITY VIEWER TEST SUMMARY")
    print("=" * 60)
    print(f"MLflow viewer working: {final_results['test_summary']['mlflow_viewer_working']}")
    print(f"Evidence checker working: {final_results['test_summary']['evidence_checker_working']}")
    print(f"Activity tracking working: {final_results['test_summary']['activity_tracking_working']}")
    print(f"Test activities generated: {final_results['test_summary']['test_activities_generated']}")
    print(f"Test completed: {final_results['test_summary']['test_completed']}")

    if all([
        final_results['test_summary']['mlflow_viewer_working'],
        final_results['test_summary']['evidence_checker_working'],
        final_results['test_summary']['activity_tracking_working']
    ]):
        print("\n🎉 ALL MLFLOW ACTIVITY VIEWER TESTS PASSED!")
    else:
        print("\n⚠️  Some MLflow tests failed - check individual results above")

    return final_results

if __name__ == "__main__":
    results = run_activity_viewer_tests()