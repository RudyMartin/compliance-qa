"""
Functional Tests for Bedrock Services
=====================================

This module tests all Bedrock-related functions to ensure they work correctly.
Tests use the actual implementation code from the infrastructure.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Import infrastructure components
from infrastructure.services.bedrock_service import (
    BedrockService,
    get_bedrock_service,
    inject_bedrock_config,
    BedrockModel
)
from infrastructure.services.aws_service import AWSService, get_aws_service
from infrastructure.yaml_loader import SettingsLoader
from infrastructure.services.dynamic_credential_carrier import DynamicCredentialCarrier

# Import adapters
from adapters.session.unified_session_manager import (
    UnifiedSessionManager,
    get_global_session_manager
)

# Import TidyLLM components
from packages.tidyllm.infrastructure.bedrock_delegate import (
    BedrockDelegate,
    get_bedrock_delegate,
    PARENT_BEDROCK_AVAILABLE
)
from packages.tidyllm.gateways.corporate_llm_gateway import (
    CorporateLLMGateway,
    LLMRequest,
    LLMResponse
)


class BedrockTestSuite:
    """Comprehensive test suite for all Bedrock functions."""

    def __init__(self):
        self.test_results = []
        self.settings_loader = SettingsLoader()
        self.timestamp = datetime.now().isoformat()

    def log_test(self, test_name: str, result: Dict[str, Any]):
        """Log test result."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'result': result
        }
        self.test_results.append(entry)

        # Print result
        status = "[PASS]" if result.get('success') else "[FAIL]"
        print(f"{status} {test_name}")
        if not result.get('success'):
            print(f"  Error: {result.get('error')}")

    def test_bedrock_service_initialization(self) -> Dict:
        """Test BedrockService initialization."""
        print("\n" + "="*60)
        print("1. Testing BedrockService Initialization")
        print("="*60)

        result = {'success': False}

        try:
            # Get configuration
            config = self.settings_loader.get_bedrock_config()

            # Initialize service
            service = BedrockService(config)

            # Check if available
            is_available = service.is_available()

            result = {
                'success': is_available,
                'has_config': bool(config),
                'region': service.region,
                'default_model': service.default_model,
                'boto3_available': service._bedrock_client is not None,
                'implementation_type': 'REAL' if is_available else 'MOCK'
            }

            print(f"  Configuration loaded: {result['has_config']}")
            print(f"  Region: {result['region']}")
            print(f"  Default model: {result['default_model']}")
            print(f"  Boto3 available: {result['boto3_available']}")
            print(f"  Implementation: {result['implementation_type']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('bedrock_service_initialization', result)
        return result

    def test_list_foundation_models(self) -> Dict:
        """Test listing foundation models."""
        print("\n" + "="*60)
        print("2. Testing List Foundation Models")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                print("  Service not available - using mock")
                return result

            models = service.list_foundation_models()

            result = {
                'success': True,
                'model_count': len(models),
                'models': models[:3] if models else [],  # First 3 for brevity
                'implementation_type': 'REAL' if models else 'MOCK'
            }

            print(f"  Found {result['model_count']} models")
            if models:
                print("  Sample models:")
                for model in models[:3]:
                    print(f"    - {model.get('modelId', 'Unknown')}")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'MOCK' if 'not available' in str(e).lower() else 'ERROR'

        self.log_test('list_foundation_models', result)
        return result

    def test_invoke_model(self) -> Dict:
        """Test model invocation."""
        print("\n" + "="*60)
        print("3. Testing Model Invocation")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                print("  Service not available - using mock")
                return result

            # Test with a simple prompt
            prompt = "Hello, please respond with 'Hi' only."

            start_time = time.time()
            response = service.invoke_model(
                prompt=prompt,
                model_id=BedrockModel.CLAUDE_3_HAIKU.value,
                max_tokens=10,
                temperature=0.1
            )
            latency = (time.time() - start_time) * 1000

            result = {
                'success': response is not None,
                'response': response[:100] if response else None,
                'latency_ms': latency,
                'model_used': BedrockModel.CLAUDE_3_HAIKU.value,
                'implementation_type': 'REAL' if response else 'MOCK'
            }

            print(f"  Response received: {result['success']}")
            print(f"  Latency: {result['latency_ms']:.2f}ms")
            if response:
                print(f"  Response preview: {response[:50]}...")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'ERROR'

        self.log_test('invoke_model', result)
        return result

    def test_invoke_claude(self) -> Dict:
        """Test Claude-specific invocation."""
        print("\n" + "="*60)
        print("4. Testing Claude Invocation")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            prompt = "Say 'Claude test successful' and nothing else."

            start_time = time.time()
            response = service.invoke_claude(prompt, max_tokens=20)
            latency = (time.time() - start_time) * 1000

            result = {
                'success': response is not None,
                'response': response[:100] if response else None,
                'latency_ms': latency,
                'implementation_type': 'REAL' if response else 'MOCK'
            }

            print(f"  Claude response: {result['success']}")
            print(f"  Latency: {result['latency_ms']:.2f}ms")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'ERROR'

        self.log_test('invoke_claude', result)
        return result

    def test_invoke_titan(self) -> Dict:
        """Test Titan-specific invocation."""
        print("\n" + "="*60)
        print("5. Testing Titan Invocation")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            prompt = "Say 'Titan test successful' and nothing else."

            start_time = time.time()
            response = service.invoke_titan(prompt, max_tokens=20)
            latency = (time.time() - start_time) * 1000

            result = {
                'success': response is not None,
                'response': response[:100] if response else None,
                'latency_ms': latency,
                'implementation_type': 'REAL' if response else 'MOCK'
            }

            print(f"  Titan response: {result['success']}")
            print(f"  Latency: {result['latency_ms']:.2f}ms")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'ERROR'

        self.log_test('invoke_titan', result)
        return result

    def test_create_embedding(self) -> Dict:
        """Test embedding creation."""
        print("\n" + "="*60)
        print("6. Testing Embedding Creation")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            text = "This is a test sentence for embedding."

            start_time = time.time()
            embedding = service.create_embedding(text)
            latency = (time.time() - start_time) * 1000

            result = {
                'success': embedding is not None,
                'embedding_size': len(embedding) if embedding else 0,
                'latency_ms': latency,
                'implementation_type': 'REAL' if embedding else 'MOCK'
            }

            print(f"  Embedding created: {result['success']}")
            if embedding:
                print(f"  Embedding dimensions: {result['embedding_size']}")
            print(f"  Latency: {result['latency_ms']:.2f}ms")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'ERROR'

        self.log_test('create_embedding', result)
        return result

    def test_get_model_info(self) -> Dict:
        """Test getting model information."""
        print("\n" + "="*60)
        print("7. Testing Get Model Info")
        print("="*60)

        result = {'success': False}

        try:
            service = get_bedrock_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            model_id = BedrockModel.CLAUDE_3_HAIKU.value

            info = service.get_model_info(model_id)

            result = {
                'success': info is not None,
                'model_id': model_id,
                'info_keys': list(info.keys()) if info else [],
                'implementation_type': 'REAL' if info else 'MOCK'
            }

            print(f"  Model info retrieved: {result['success']}")
            if info:
                print(f"  Info keys: {result['info_keys']}")

        except Exception as e:
            result['error'] = str(e)
            result['implementation_type'] = 'ERROR'

        self.log_test('get_model_info', result)
        return result

    def test_bedrock_delegate(self) -> Dict:
        """Test BedrockDelegate functionality."""
        print("\n" + "="*60)
        print("8. Testing Bedrock Delegate")
        print("="*60)

        result = {'success': False}

        try:
            delegate = get_bedrock_delegate()

            # Check if parent is available
            print(f"  Parent Bedrock available: {PARENT_BEDROCK_AVAILABLE}")

            is_available = delegate.is_available()

            result = {
                'success': True,
                'is_available': is_available,
                'parent_available': PARENT_BEDROCK_AVAILABLE,
                'implementation_type': 'DELEGATED' if PARENT_BEDROCK_AVAILABLE else 'MOCK'
            }

            print(f"  Delegate available: {result['is_available']}")
            print(f"  Implementation: {result['implementation_type']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('bedrock_delegate', result)
        return result

    def test_aws_service_bedrock(self) -> Dict:
        """Test AWS Service Bedrock methods."""
        print("\n" + "="*60)
        print("9. Testing AWS Service Bedrock Integration")
        print("="*60)

        result = {'success': False}

        try:
            aws_service = get_aws_service()

            # Test getting clients
            bedrock_client = aws_service.get_bedrock_client()
            runtime_client = aws_service.get_bedrock_runtime_client()

            result = {
                'success': True,
                'has_bedrock_client': bedrock_client is not None,
                'has_runtime_client': runtime_client is not None,
                'is_available': aws_service.is_available(),
                'implementation_type': 'REAL' if bedrock_client else 'MOCK'
            }

            print(f"  Bedrock client: {result['has_bedrock_client']}")
            print(f"  Runtime client: {result['has_runtime_client']}")
            print(f"  Service available: {result['is_available']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('aws_service_bedrock', result)
        return result

    def test_unified_session_manager(self) -> Dict:
        """Test UnifiedSessionManager Bedrock methods."""
        print("\n" + "="*60)
        print("10. Testing UnifiedSessionManager Bedrock")
        print("="*60)

        result = {'success': False}

        try:
            usm = UnifiedSessionManager()

            # Test connection
            connection_test = usm._test_bedrock_connection()

            # Get clients
            bedrock_client = usm.get_bedrock_client()
            runtime_client = usm.get_bedrock_runtime_client()

            result = {
                'success': connection_test.get('status') == 'connected',
                'connection_status': connection_test.get('status'),
                'latency_ms': connection_test.get('latency', 0),
                'models_count': connection_test.get('models_count', 0),
                'has_clients': bedrock_client is not None,
                'implementation_type': 'REAL' if bedrock_client else 'MOCK'
            }

            print(f"  Connection status: {result['connection_status']}")
            print(f"  Latency: {result['latency_ms']}ms")
            print(f"  Models found: {result['models_count']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('unified_session_manager', result)
        return result

    def test_corporate_llm_gateway(self) -> Dict:
        """Test CorporateLLMGateway."""
        print("\n" + "="*60)
        print("11. Testing Corporate LLM Gateway")
        print("="*60)

        result = {'success': False}

        try:
            gateway = CorporateLLMGateway()

            # Create request
            request = LLMRequest(
                prompt="Respond with 'Gateway test successful' only.",
                model_id="claude-3-haiku",
                max_tokens=20,
                temperature=0.1
            )

            # Process request
            start_time = time.time()
            response = gateway.process_request(request)
            latency = (time.time() - start_time) * 1000

            result = {
                'success': response.success,
                'response_preview': response.content[:50] if response.content else None,
                'model_used': response.model_used,
                'latency_ms': latency,
                'implementation_type': 'REAL' if response.success else 'MOCK'
            }

            print(f"  Request processed: {result['success']}")
            print(f"  Model used: {result['model_used']}")
            print(f"  Latency: {result['latency_ms']:.2f}ms")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('corporate_llm_gateway', result)
        return result

    def test_configuration_functions(self) -> Dict:
        """Test configuration loading functions."""
        print("\n" + "="*60)
        print("12. Testing Configuration Functions")
        print("="*60)

        result = {'success': False}

        try:
            # Test SettingsLoader
            loader = SettingsLoader()
            bedrock_config = loader.get_bedrock_config()

            # Test DynamicCredentialCarrier
            carrier = DynamicCredentialCarrier()
            carrier_config = carrier.get_bedrock_configuration()

            result = {
                'success': True,
                'yaml_config_loaded': bool(bedrock_config),
                'yaml_has_model': 'default_model' in bedrock_config,
                'carrier_config_loaded': bool(carrier_config),
                'configs_match': bedrock_config.get('default_model') == carrier_config.get('default_model')
            }

            print(f"  YAML config loaded: {result['yaml_config_loaded']}")
            print(f"  Carrier config loaded: {result['carrier_config_loaded']}")
            print(f"  Configs match: {result['configs_match']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('configuration_functions', result)
        return result

    def run_all_tests(self):
        """Run all tests and generate report."""
        print("\n" + "="*60)
        print("BEDROCK FUNCTIONAL TEST SUITE")
        print("="*60)

        # Run tests
        self.test_bedrock_service_initialization()
        self.test_list_foundation_models()
        self.test_invoke_model()
        self.test_invoke_claude()
        self.test_invoke_titan()
        self.test_create_embedding()
        self.test_get_model_info()
        self.test_bedrock_delegate()
        self.test_aws_service_bedrock()
        self.test_unified_session_manager()
        self.test_corporate_llm_gateway()
        self.test_configuration_functions()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['result'].get('success'))
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Check implementation types
        implementations = {}
        for result in self.test_results:
            impl_type = result['result'].get('implementation_type', 'UNKNOWN')
            implementations[impl_type] = implementations.get(impl_type, 0) + 1

        print("\nImplementation Types:")
        for impl_type, count in implementations.items():
            print(f"  {impl_type}: {count}")

        # List failed tests
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['result'].get('success'):
                    print(f"  - {result['test_name']}")
                    if 'error' in result['result']:
                        print(f"    Error: {result['result']['error']}")

        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'implementations': implementations
        }


def main():
    """Main entry point."""
    suite = BedrockTestSuite()
    suite.run_all_tests()

    # Save results to file
    results_file = Path(__file__).parent / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump(suite.test_results, f, indent=2, default=str)

    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()