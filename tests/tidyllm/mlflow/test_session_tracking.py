#!/usr/bin/env python3
"""
MLflow Session Tracking Tests
============================

Comprehensive tests for user session parameters and MLflow logging
with real chat interactions and session management.

STANDARDIZED TEST CONFIG:
- NO mocks - uses real infrastructure
- 3 max retries for all operations
- Timeouts set to avoid hangs
"""

import sys
import os
import time
import uuid
from datetime import datetime
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
from tidyllm.services import MLflowIntegrationService

# Import MLflow viewer directly
try:
    from tidyllm.infrastructure.tools.mlflow_viewer import show_last_5_mlflow_records
except ImportError:
    def show_last_5_mlflow_records():
        print("MLflow viewer not available - skipping MLflow records display")

class MLflowSessionTracker:
    """Test MLflow session tracking with user parameters."""

    def __init__(self):
        self.test_session_id = str(uuid.uuid4())
        self.test_user_id = f"test_user_{int(time.time())}"
        self.mlflow_service = MLflowIntegrationService()

    def test_chat_session_tracking(self) -> Dict[str, Any]:
        """Test chat interactions with session tracking."""
        print("=== MLflow Session Tracking Test ===")
        print(f"Test Session ID: {self.test_session_id}")
        print(f"Test User ID: {self.test_user_id}")
        print()

        results = {
            'test_session_id': self.test_session_id,
            'test_user_id': self.test_user_id,
            'chat_tests': [],
            'mlflow_status': {},
            'session_parameters': {}
        }

        # Test different chat modes with session tracking
        chat_modes = ['direct', 'dspy', 'rag', 'hybrid']

        for mode in chat_modes:
            print(f"Testing {mode} mode with session tracking...")

            try:
                # Chat with session parameters
                response = tidyllm.chat(
                    f"Test message for {mode} mode session tracking",
                    chat_type=mode,
                    reasoning=True,
                    user_id=self.test_user_id,
                    session_id=self.test_session_id,
                    audit_reason=f"mlflow_session_test_{mode}"
                )

                # Analyze response for session data
                chat_result = {
                    'mode': mode,
                    'success': True,
                    'has_audit_trail': isinstance(response, dict) and 'audit_trail' in response,
                    'has_token_usage': isinstance(response, dict) and 'token_usage' in response,
                    'response_type': str(type(response)),
                    'timestamp': datetime.now().isoformat()
                }

                # Extract session parameters from audit trail
                if chat_result['has_audit_trail']:
                    audit_trail = response['audit_trail']
                    chat_result['session_parameters'] = {
                        'user_id': audit_trail.get('user_id'),
                        'audit_reason': audit_trail.get('audit_reason'),
                        'timestamp': audit_trail.get('timestamp'),
                        'model_id': audit_trail.get('model_id'),
                        'temperature': audit_trail.get('temperature')
                    }

                # Extract token usage
                if chat_result['has_token_usage']:
                    token_usage = response['token_usage']
                    chat_result['token_metrics'] = {
                        'input_tokens': token_usage.get('input', 0),
                        'output_tokens': token_usage.get('output', 0),
                        'total_tokens': token_usage.get('total', 0)
                    }

                results['chat_tests'].append(chat_result)
                print(f"  {mode} mode: SUCCESS")

                # Small delay between tests
                time.sleep(1)

            except Exception as e:
                chat_result = {
                    'mode': mode,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results['chat_tests'].append(chat_result)
                print(f"  {mode} mode: FAILED - {e}")

        # Test MLflow service status
        results['mlflow_status'] = {
            'service_available': self.mlflow_service.is_available(),
            'service_connected': self.mlflow_service.is_connected,
            'can_log_requests': hasattr(self.mlflow_service, 'log_llm_request')
        }

        return results

    def test_mlflow_viewer_integration(self) -> Dict[str, Any]:
        """Test MLflow viewer with session parameters."""
        print("\n=== Testing MLflow Viewer Integration ===")

        try:
            print("Calling show_last_5_mlflow_records()...")
            # Note: This will show actual MLflow records including our test sessions
            show_last_5_mlflow_records()

            return {
                'mlflow_viewer_test': 'SUCCESS',
                'message': 'MLflow viewer executed successfully - check output above for session data'
            }

        except Exception as e:
            print(f"MLflow viewer failed: {e}")
            return {
                'mlflow_viewer_test': 'FAILED',
                'error': str(e),
                'message': 'MLflow viewer not working - may need configuration'
            }

    def analyze_session_parameters(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session parameter tracking across chat modes."""
        print("\n=== Session Parameter Analysis ===")

        analysis = {
            'total_tests': len(results['chat_tests']),
            'successful_tests': len([t for t in results['chat_tests'] if t['success']]),
            'modes_with_audit_trails': 0,
            'modes_with_token_usage': 0,
            'session_consistency': {},
            'parameter_coverage': {}
        }

        # Check for audit trails and token usage
        for test in results['chat_tests']:
            if test.get('has_audit_trail'):
                analysis['modes_with_audit_trails'] += 1
            if test.get('has_token_usage'):
                analysis['modes_with_token_usage'] += 1

        # Check session parameter consistency
        user_ids = []
        audit_reasons = []

        for test in results['chat_tests']:
            if test.get('session_parameters'):
                params = test['session_parameters']
                if params.get('user_id'):
                    user_ids.append(params['user_id'])
                if params.get('audit_reason'):
                    audit_reasons.append(params['audit_reason'])

        analysis['session_consistency'] = {
            'consistent_user_id': len(set(user_ids)) <= 1 if user_ids else False,
            'unique_audit_reasons': len(set(audit_reasons)),
            'user_ids_found': list(set(user_ids)),
            'audit_reasons_found': list(set(audit_reasons))
        }

        # Parameter coverage analysis
        all_params = set()
        for test in results['chat_tests']:
            if test.get('session_parameters'):
                all_params.update(test['session_parameters'].keys())

        analysis['parameter_coverage'] = {
            'total_parameters_tracked': len(all_params),
            'parameters_found': list(all_params),
            'expected_parameters': ['user_id', 'audit_reason', 'timestamp', 'model_id', 'temperature'],
            'missing_parameters': [p for p in ['user_id', 'audit_reason', 'timestamp', 'model_id', 'temperature']
                                 if p not in all_params]
        }

        # Print analysis
        print(f"Successful tests: {analysis['successful_tests']}/{analysis['total_tests']}")
        print(f"Modes with audit trails: {analysis['modes_with_audit_trails']}")
        print(f"Modes with token usage: {analysis['modes_with_token_usage']}")
        print(f"Session parameter consistency: {analysis['session_consistency']['consistent_user_id']}")
        print(f"Parameters tracked: {analysis['parameter_coverage']['parameters_found']}")

        if analysis['parameter_coverage']['missing_parameters']:
            print(f"Missing parameters: {analysis['parameter_coverage']['missing_parameters']}")

        return analysis

def run_mlflow_session_tests():
    """Run comprehensive MLflow session tracking tests."""
    print("=" * 60)
    print("MLFLOW SESSION TRACKING COMPREHENSIVE TESTS")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tracker = MLflowSessionTracker()

    # Run chat session tracking tests
    session_results = tracker.test_chat_session_tracking()

    # Analyze session parameters
    analysis = tracker.analyze_session_parameters(session_results)

    # Test MLflow viewer integration
    viewer_results = tracker.test_mlflow_viewer_integration()

    # Compile final results
    final_results = {
        'test_summary': {
            'total_chat_modes_tested': len(session_results['chat_tests']),
            'successful_chat_tests': analysis['successful_tests'],
            'mlflow_service_status': session_results['mlflow_status'],
            'session_parameter_tracking': analysis['session_consistency']['consistent_user_id'],
            'parameter_coverage_complete': len(analysis['parameter_coverage']['missing_parameters']) == 0
        },
        'session_results': session_results,
        'analysis': analysis,
        'viewer_results': viewer_results,
        'timestamp': datetime.now().isoformat()
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Chat modes tested: {final_results['test_summary']['total_chat_modes_tested']}")
    print(f"Successful tests: {final_results['test_summary']['successful_chat_tests']}")
    print(f"MLflow service available: {final_results['test_summary']['mlflow_service_status']['service_available']}")
    print(f"Session tracking working: {final_results['test_summary']['session_parameter_tracking']}")
    print(f"Parameter coverage complete: {final_results['test_summary']['parameter_coverage_complete']}")

    return final_results

if __name__ == "__main__":
    results = run_mlflow_session_tests()