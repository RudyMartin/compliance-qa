"""
Stub Detection Test for Bedrock Services
=========================================

This module specifically detects when stub/mock implementations are being used
instead of real AWS Bedrock services.
"""

import os
import sys
import json
import inspect
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Import all Bedrock-related modules
from infrastructure.services.bedrock_service import (
    BedrockService,
    get_bedrock_service,
    BOTO3_AVAILABLE
)
from packages.tidyllm.infrastructure.bedrock_delegate import (
    BedrockDelegate,
    get_bedrock_delegate,
    PARENT_BEDROCK_AVAILABLE
)
from packages.tidyllm.gateways.corporate_llm_gateway import (
    CorporateLLMGateway,
    LLMRequest
)
from adapters.session.unified_session_manager import UnifiedSessionManager
from infrastructure.services.aws_service import get_aws_service


class StubDetector:
    """Detects stub/mock implementations in Bedrock services."""

    def __init__(self):
        self.findings = []

    def log_finding(self, component: str, status: str, details: Dict):
        """Log a finding about stub/real implementation."""
        finding = {
            'component': component,
            'status': status,  # REAL, STUB, PARTIAL_STUB, ERROR
            'details': details
        }
        self.findings.append(finding)

        # Print finding
        symbol = "[OK]" if status == "REAL" else "[WARN]" if status == "PARTIAL_STUB" else "[FAIL]"
        print(f"{symbol} {component}: {status}")
        for key, value in details.items():
            print(f"  {key}: {value}")

    def detect_bedrock_service(self) -> str:
        """Detect if BedrockService is real or stub."""
        print("\n" + "="*60)
        print("1. Checking BedrockService")
        print("="*60)

        service = get_bedrock_service()

        # Check boto3 availability
        if not BOTO3_AVAILABLE:
            self.log_finding('BedrockService', 'STUB', {
                'reason': 'boto3 not available',
                'boto3_available': False
            })
            return 'STUB'

        # Check if service has real clients
        has_bedrock_client = hasattr(service, '_bedrock_client') and service._bedrock_client is not None
        has_runtime_client = hasattr(service, '_bedrock_runtime_client') and service._bedrock_runtime_client is not None

        if not (has_bedrock_client and has_runtime_client):
            self.log_finding('BedrockService', 'STUB', {
                'reason': 'No boto3 clients initialized',
                'has_bedrock_client': has_bedrock_client,
                'has_runtime_client': has_runtime_client
            })
            return 'STUB'

        # Test actual functionality
        try:
            # Try to list models
            models = service.list_foundation_models()
            if not models:
                self.log_finding('BedrockService', 'PARTIAL_STUB', {
                    'reason': 'list_foundation_models returned empty',
                    'boto3_available': True,
                    'clients_initialized': True,
                    'likely_cause': 'AWS credentials or permissions issue'
                })
                return 'PARTIAL_STUB'

            # Try to invoke a model with minimal test
            response = service.invoke_model("Return 'test'", max_tokens=10)

            if response is None:
                self.log_finding('BedrockService', 'PARTIAL_STUB', {
                    'reason': 'invoke_model returned None',
                    'models_available': len(models),
                    'likely_cause': 'Model invocation failed'
                })
                return 'PARTIAL_STUB'

            # Check if response is mock
            if response and ('Mock' in response or 'mock' in response):
                self.log_finding('BedrockService', 'STUB', {
                    'reason': 'Returned mock response',
                    'response_preview': response[:100]
                })
                return 'STUB'

            self.log_finding('BedrockService', 'REAL', {
                'boto3_available': True,
                'clients_initialized': True,
                'models_found': len(models),
                'invocation_works': True
            })
            return 'REAL'

        except Exception as e:
            self.log_finding('BedrockService', 'ERROR', {
                'error': str(e),
                'boto3_available': True,
                'clients_initialized': has_bedrock_client and has_runtime_client
            })
            return 'ERROR'

    def detect_bedrock_delegate(self) -> str:
        """Detect if BedrockDelegate is using real or mock service."""
        print("\n" + "="*60)
        print("2. Checking BedrockDelegate")
        print("="*60)

        delegate = get_bedrock_delegate()

        # Check if parent is available
        if not PARENT_BEDROCK_AVAILABLE:
            self.log_finding('BedrockDelegate', 'STUB', {
                'reason': 'Parent infrastructure not available',
                'parent_available': False,
                'using_mock': True
            })
            return 'STUB'

        # Check the actual service being used
        if hasattr(delegate, '_service'):
            service = delegate._service
            service_type = type(service).__name__
            service_module = type(service).__module__

            # Check if it's the mock class
            if 'bedrock_delegate' in service_module and service_type == 'BedrockService':
                # This is the local mock, not the parent
                if not service.is_available():
                    self.log_finding('BedrockDelegate', 'STUB', {
                        'reason': 'Using local mock BedrockService',
                        'service_type': service_type,
                        'service_module': service_module,
                        'is_available': False
                    })
                    return 'STUB'

            # Test actual functionality
            is_available = delegate.is_available()
            models = delegate.list_foundation_models()

            if not is_available:
                self.log_finding('BedrockDelegate', 'STUB', {
                    'reason': 'Delegate not available',
                    'parent_available': PARENT_BEDROCK_AVAILABLE,
                    'is_available': is_available
                })
                return 'STUB'

            self.log_finding('BedrockDelegate', 'REAL', {
                'parent_available': PARENT_BEDROCK_AVAILABLE,
                'is_available': is_available,
                'models_found': len(models) if models else 0,
                'service_type': service_type,
                'delegation_working': True
            })
            return 'REAL'

        return 'UNKNOWN'

    def detect_corporate_gateway(self) -> str:
        """Detect if CorporateLLMGateway is using real or mock implementation."""
        print("\n" + "="*60)
        print("3. Checking CorporateLLMGateway")
        print("="*60)

        gateway = CorporateLLMGateway()

        # Check USM availability
        has_usm = gateway.usm is not None

        # Try to process a request
        try:
            request = LLMRequest(
                prompt="Return 'test'",
                model_id="claude-3-haiku",
                max_tokens=10
            )

            response = gateway.process_request(request)

            # Check if response content is mock
            if response.content and ('Mock' in response.content or 'mock' in response.content):
                self.log_finding('CorporateLLMGateway', 'STUB', {
                    'reason': 'Using MockBedrockClient',
                    'has_usm': has_usm,
                    'response_preview': response.content[:100],
                    'fallback_level': 'Mock client (level 3)'
                })
                return 'STUB'

            if response.success:
                self.log_finding('CorporateLLMGateway', 'REAL', {
                    'has_usm': has_usm,
                    'response_success': True,
                    'model_used': response.model_used,
                    'implementation': 'Real AWS Bedrock'
                })
                return 'REAL'

            self.log_finding('CorporateLLMGateway', 'PARTIAL_STUB', {
                'reason': 'Request failed but not using mock',
                'has_usm': has_usm,
                'error': response.error
            })
            return 'PARTIAL_STUB'

        except Exception as e:
            self.log_finding('CorporateLLMGateway', 'ERROR', {
                'error': str(e),
                'has_usm': has_usm
            })
            return 'ERROR'

    def detect_unified_session_manager(self) -> str:
        """Detect if UnifiedSessionManager has real Bedrock clients."""
        print("\n" + "="*60)
        print("4. Checking UnifiedSessionManager")
        print("="*60)

        try:
            usm = UnifiedSessionManager()

            # Check for Bedrock clients
            has_bedrock = usm._bedrock_client is not None
            has_runtime = usm._bedrock_runtime_client is not None

            if not (has_bedrock or has_runtime):
                # Try to initialize
                bedrock_client = usm.get_bedrock_client()
                runtime_client = usm.get_bedrock_runtime_client()

                has_bedrock = bedrock_client is not None
                has_runtime = runtime_client is not None

            # Test connection
            test_result = usm._test_bedrock_connection()

            if test_result['status'] == 'success':
                self.log_finding('UnifiedSessionManager', 'REAL', {
                    'has_bedrock_client': has_bedrock,
                    'has_runtime_client': has_runtime,
                    'connection_status': test_result['status'],
                    'model_count': test_result.get('model_count', 0)
                })
                return 'REAL'
            elif test_result['status'] == 'corporate_restricted':
                self.log_finding('UnifiedSessionManager', 'PARTIAL_STUB', {
                    'reason': 'Corporate restrictions',
                    'has_clients': has_bedrock and has_runtime,
                    'status': test_result['status'],
                    'message': test_result.get('message')
                })
                return 'PARTIAL_STUB'
            else:
                self.log_finding('UnifiedSessionManager', 'STUB', {
                    'reason': 'Connection test failed',
                    'has_bedrock_client': has_bedrock,
                    'has_runtime_client': has_runtime,
                    'status': test_result['status'],
                    'error': test_result.get('error')
                })
                return 'STUB'

        except Exception as e:
            self.log_finding('UnifiedSessionManager', 'ERROR', {
                'error': str(e)
            })
            return 'ERROR'

    def detect_aws_service(self) -> str:
        """Detect if AWSService has real Bedrock clients."""
        print("\n" + "="*60)
        print("5. Checking AWSService")
        print("="*60)

        try:
            aws_service = get_aws_service()

            # Check availability
            if not aws_service.is_available():
                self.log_finding('AWSService', 'STUB', {
                    'reason': 'AWS service not available',
                    'is_available': False
                })
                return 'STUB'

            # Get clients
            bedrock_client = aws_service.get_bedrock_client()
            runtime_client = aws_service.get_bedrock_runtime_client()

            if not (bedrock_client and runtime_client):
                self.log_finding('AWSService', 'STUB', {
                    'reason': 'No Bedrock clients available',
                    'has_bedrock_client': bedrock_client is not None,
                    'has_runtime_client': runtime_client is not None
                })
                return 'STUB'

            # Test invocation
            response = aws_service.invoke_model("Return 'test'", max_tokens=10)

            if response and ('Mock' in response or 'mock' in response):
                self.log_finding('AWSService', 'STUB', {
                    'reason': 'Returned mock response',
                    'response_preview': response[:100]
                })
                return 'STUB'

            self.log_finding('AWSService', 'REAL', {
                'is_available': True,
                'has_bedrock_client': True,
                'has_runtime_client': True,
                'invocation_works': response is not None
            })
            return 'REAL'

        except Exception as e:
            self.log_finding('AWSService', 'ERROR', {
                'error': str(e)
            })
            return 'ERROR'

    def run_detection(self):
        """Run all stub detection tests."""
        print("\n" + "="*60)
        print("BEDROCK STUB DETECTION ANALYSIS")
        print("="*60)

        results = {
            'BedrockService': self.detect_bedrock_service(),
            'BedrockDelegate': self.detect_bedrock_delegate(),
            'CorporateLLMGateway': self.detect_corporate_gateway(),
            'UnifiedSessionManager': self.detect_unified_session_manager(),
            'AWSService': self.detect_aws_service()
        }

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        real_count = sum(1 for v in results.values() if v == 'REAL')
        stub_count = sum(1 for v in results.values() if v == 'STUB')
        partial_count = sum(1 for v in results.values() if v == 'PARTIAL_STUB')
        error_count = sum(1 for v in results.values() if v == 'ERROR')

        print(f"Total Components: {len(results)}")
        print(f"Real Implementations: {real_count}")
        print(f"Stub Implementations: {stub_count}")
        print(f"Partial Stubs: {partial_count}")
        print(f"Errors: {error_count}")

        print("\nComponent Status:")
        for component, status in results.items():
            symbol = "[OK]" if status == "REAL" else "[WARN]" if status == "PARTIAL_STUB" else "[FAIL]"
            print(f"  {symbol} {component}: {status}")

        # Recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)

        if stub_count > 0 or partial_count > 0:
            print("To use real implementations:")
            print("1. Ensure AWS credentials are configured")
            print("2. Check boto3 is installed: pip install boto3")
            print("3. Verify IAM permissions for Bedrock")
            print("4. Set AWS_REGION environment variable")

            if 'BedrockDelegate' in [k for k, v in results.items() if v == 'STUB']:
                print("5. Ensure parent infrastructure is properly set up")

        return results


def main():
    """Main entry point."""
    detector = StubDetector()
    results = detector.run_detection()

    # Save results
    output_file = Path(__file__).parent / 'stub_detection_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'results': results,
            'findings': detector.findings
        }, f, indent=2, default=str)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()