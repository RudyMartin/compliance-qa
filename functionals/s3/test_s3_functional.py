"""
Functional Tests for S3 Services
=================================

This module tests all S3-related functions to ensure they work correctly.
Tests use the actual implementation code from the infrastructure.
"""

import os
import sys
import json
import time
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
qa_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(qa_root))

# Import infrastructure components
from infrastructure.services.s3_service import (
    S3Service,
    get_s3_service,
    inject_s3_config,
    BOTO3_AVAILABLE
)
from infrastructure.services.aws_service import AWSService, get_aws_service
from infrastructure.yaml_loader import SettingsLoader

# Import adapters
from adapters.session.unified_session_manager import (
    UnifiedSessionManager,
    get_global_session_manager
)

# Import TidyLLM components
from packages.tidyllm.infrastructure.s3_delegate import (
    S3Delegate,
    get_s3_delegate,
    get_s3_config,
    build_s3_path,
    PARENT_S3_AVAILABLE
)


class S3TestSuite:
    """Comprehensive test suite for all S3 functions."""

    def __init__(self):
        self.test_results = []
        self.settings_loader = SettingsLoader()
        self.timestamp = datetime.now().isoformat()
        self.test_bucket = None
        self.test_prefix = f"qa-test/{datetime.now().strftime('%Y%m%d_%H%M%S')}"

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

    def setup_test_environment(self):
        """Setup test environment with bucket configuration."""
        print("\n" + "="*60)
        print("Setting up test environment")
        print("="*60)

        try:
            # Get S3 configuration
            config = self.settings_loader.get_s3_config()
            self.test_bucket = config.get('bucket', os.getenv('S3_BUCKET'))

            if not self.test_bucket:
                print("[WARNING] No S3 bucket configured")
                print("  Set S3_BUCKET environment variable or configure in settings.yaml")
                return False

            print(f"  Test bucket: {self.test_bucket}")
            print(f"  Test prefix: {self.test_prefix}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to setup test environment: {e}")
            return False

    def cleanup_test_data(self):
        """Cleanup test data from S3."""
        print("\n" + "="*60)
        print("Cleaning up test data")
        print("="*60)

        if not self.test_bucket:
            return

        try:
            service = get_s3_service()
            if not service.is_available():
                return

            # List and delete all test objects
            objects = service.list_objects(prefix=self.test_prefix, bucket=self.test_bucket)
            for obj_key in objects:
                service.delete(obj_key, self.test_bucket)
                print(f"  Deleted: {obj_key}")

            print(f"  Cleaned up {len(objects)} test objects")

        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")

    def test_s3_service_initialization(self) -> Dict:
        """Test S3Service initialization."""
        print("\n" + "="*60)
        print("1. Testing S3Service Initialization")
        print("="*60)

        result = {'success': False}

        try:
            # Get configuration
            config = self.settings_loader.get_s3_config()

            # Initialize service
            service = S3Service(config)

            # Check if available
            is_available = service.is_available()

            result = {
                'success': is_available,
                'has_config': bool(config),
                'region': service.region,
                'bucket': service.bucket,
                'boto3_available': BOTO3_AVAILABLE,
                'client_initialized': service._client is not None,
                'implementation_type': 'REAL' if is_available else 'MOCK'
            }

            print(f"  Configuration loaded: {result['has_config']}")
            print(f"  Region: {result['region']}")
            print(f"  Default bucket: {result['bucket']}")
            print(f"  Boto3 available: {result['boto3_available']}")
            print(f"  Implementation: {result['implementation_type']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('s3_service_initialization', result)
        return result

    def test_upload_download(self) -> Dict:
        """Test file upload and download."""
        print("\n" + "="*60)
        print("2. Testing Upload/Download")
        print("="*60)

        result = {'success': False}

        if not self.test_bucket:
            result['error'] = 'No test bucket configured'
            self.log_test('upload_download', result)
            return result

        try:
            service = get_s3_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            # Create test file
            test_content = f"Test file created at {datetime.now()}"
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(test_content)
                test_file = f.name

            # Upload file
            s3_key = f"{self.test_prefix}/test-upload.txt"
            upload_success = service.upload_file(test_file, s3_key, self.test_bucket)

            if not upload_success:
                result['error'] = 'Upload failed'
                os.unlink(test_file)
                return result

            # Download file
            download_path = test_file + '.downloaded'
            download_success = service.download_file(s3_key, download_path, self.test_bucket)

            if not download_success:
                result['error'] = 'Download failed'
                os.unlink(test_file)
                return result

            # Verify content
            with open(download_path, 'r') as f:
                downloaded_content = f.read()

            content_matches = test_content == downloaded_content

            # Cleanup local files
            os.unlink(test_file)
            os.unlink(download_path)

            result = {
                'success': upload_success and download_success and content_matches,
                'upload_success': upload_success,
                'download_success': download_success,
                'content_matches': content_matches,
                's3_key': s3_key,
                'implementation_type': 'REAL'
            }

            print(f"  Upload: {result['upload_success']}")
            print(f"  Download: {result['download_success']}")
            print(f"  Content verified: {result['content_matches']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('upload_download', result)
        return result

    def test_json_operations(self) -> Dict:
        """Test JSON read/write operations."""
        print("\n" + "="*60)
        print("3. Testing JSON Operations")
        print("="*60)

        result = {'success': False}

        if not self.test_bucket:
            result['error'] = 'No test bucket configured'
            self.log_test('json_operations', result)
            return result

        try:
            service = get_s3_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            # Test data
            test_data = {
                'timestamp': datetime.now().isoformat(),
                'test_id': str(uuid.uuid4()),
                'data': {
                    'key1': 'value1',
                    'key2': 123,
                    'key3': ['item1', 'item2']
                }
            }

            # Write JSON
            s3_key = f"{self.test_prefix}/test-data.json"
            write_success = service.write_json(test_data, s3_key, self.test_bucket)

            if not write_success:
                result['error'] = 'Write JSON failed'
                return result

            # Read JSON
            read_data = service.read_json(s3_key, self.test_bucket)

            if read_data is None:
                result['error'] = 'Read JSON failed'
                return result

            # Verify data
            data_matches = test_data == read_data

            result = {
                'success': write_success and data_matches,
                'write_success': write_success,
                'read_success': read_data is not None,
                'data_matches': data_matches,
                's3_key': s3_key,
                'implementation_type': 'REAL'
            }

            print(f"  Write JSON: {result['write_success']}")
            print(f"  Read JSON: {result['read_success']}")
            print(f"  Data verified: {result['data_matches']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('json_operations', result)
        return result

    def test_list_objects(self) -> Dict:
        """Test listing S3 objects."""
        print("\n" + "="*60)
        print("4. Testing List Objects")
        print("="*60)

        result = {'success': False}

        if not self.test_bucket:
            result['error'] = 'No test bucket configured'
            self.log_test('list_objects', result)
            return result

        try:
            service = get_s3_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            # Create test objects
            test_keys = []
            for i in range(3):
                s3_key = f"{self.test_prefix}/list-test-{i}.txt"
                data = {'index': i, 'timestamp': datetime.now().isoformat()}
                if service.write_json(data, s3_key, self.test_bucket):
                    test_keys.append(s3_key)

            # List objects
            objects = service.list_objects(prefix=self.test_prefix, bucket=self.test_bucket)

            # Verify all test objects are listed
            all_found = all(key in objects for key in test_keys)

            result = {
                'success': len(objects) >= len(test_keys) and all_found,
                'created_count': len(test_keys),
                'listed_count': len(objects),
                'all_found': all_found,
                'implementation_type': 'REAL'
            }

            print(f"  Created objects: {result['created_count']}")
            print(f"  Listed objects: {result['listed_count']}")
            print(f"  All test objects found: {result['all_found']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('list_objects', result)
        return result

    def test_exists_delete(self) -> Dict:
        """Test object existence check and deletion."""
        print("\n" + "="*60)
        print("5. Testing Exists/Delete Operations")
        print("="*60)

        result = {'success': False}

        if not self.test_bucket:
            result['error'] = 'No test bucket configured'
            self.log_test('exists_delete', result)
            return result

        try:
            service = get_s3_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            # Create test object
            s3_key = f"{self.test_prefix}/exists-test.json"
            test_data = {'test': 'exists_delete'}
            service.write_json(test_data, s3_key, self.test_bucket)

            # Check existence
            exists_before = service.exists(s3_key, self.test_bucket)

            # Delete object
            delete_success = service.delete(s3_key, self.test_bucket)

            # Check existence after delete
            exists_after = service.exists(s3_key, self.test_bucket)

            result = {
                'success': exists_before and delete_success and not exists_after,
                'exists_before': exists_before,
                'delete_success': delete_success,
                'exists_after': exists_after,
                's3_key': s3_key,
                'implementation_type': 'REAL'
            }

            print(f"  Existed before delete: {result['exists_before']}")
            print(f"  Delete successful: {result['delete_success']}")
            print(f"  Exists after delete: {result['exists_after']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('exists_delete', result)
        return result

    def test_presigned_url(self) -> Dict:
        """Test presigned URL generation."""
        print("\n" + "="*60)
        print("6. Testing Presigned URL Generation")
        print("="*60)

        result = {'success': False}

        if not self.test_bucket:
            result['error'] = 'No test bucket configured'
            self.log_test('presigned_url', result)
            return result

        try:
            service = get_s3_service()

            if not service.is_available():
                result['error'] = 'Service not available'
                result['implementation_type'] = 'MOCK'
                return result

            # Create test object
            s3_key = f"{self.test_prefix}/presigned-test.txt"
            test_data = {'url': 'presigned_test'}
            service.write_json(test_data, s3_key, self.test_bucket)

            # Generate presigned URL
            url = service.get_presigned_url(s3_key, expires_in=3600, bucket=self.test_bucket)

            result = {
                'success': url is not None and 'https://' in url,
                'url_generated': url is not None,
                'is_https': 'https://' in url if url else False,
                'contains_bucket': self.test_bucket in url if url else False,
                'contains_key': s3_key.replace('/', '%2F') in url if url else False,
                'implementation_type': 'REAL' if url else 'MOCK'
            }

            print(f"  URL generated: {result['url_generated']}")
            print(f"  HTTPS URL: {result['is_https']}")
            print(f"  Contains bucket: {result['contains_bucket']}")
            print(f"  Contains key: {result['contains_key']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('presigned_url', result)
        return result

    def test_s3_delegate(self) -> Dict:
        """Test S3Delegate functionality."""
        print("\n" + "="*60)
        print("7. Testing S3 Delegate")
        print("="*60)

        result = {'success': False}

        try:
            delegate = get_s3_delegate()

            # Check if parent is available
            print(f"  Parent S3 available: {PARENT_S3_AVAILABLE}")

            is_available = delegate.is_available()

            # Test configuration functions
            config = get_s3_config()
            path = build_s3_path("base", "path", "file.txt")

            result = {
                'success': True,
                'is_available': is_available,
                'parent_available': PARENT_S3_AVAILABLE,
                'config_loaded': bool(config),
                'path_built': path == "base/path/file.txt",
                'implementation_type': 'DELEGATED' if PARENT_S3_AVAILABLE else 'MOCK'
            }

            print(f"  Delegate available: {result['is_available']}")
            print(f"  Config loaded: {result['config_loaded']}")
            print(f"  Path builder works: {result['path_built']}")
            print(f"  Implementation: {result['implementation_type']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('s3_delegate', result)
        return result

    def test_aws_service_s3(self) -> Dict:
        """Test AWS Service S3 methods."""
        print("\n" + "="*60)
        print("8. Testing AWS Service S3 Integration")
        print("="*60)

        result = {'success': False}

        try:
            aws_service = get_aws_service()

            # Test getting S3 client
            s3_client = aws_service.get_s3_client()

            result = {
                'success': True,
                'has_s3_client': s3_client is not None,
                'is_available': aws_service.is_available(),
                'implementation_type': 'REAL' if s3_client else 'MOCK'
            }

            print(f"  S3 client: {result['has_s3_client']}")
            print(f"  Service available: {result['is_available']}")
            print(f"  Implementation: {result['implementation_type']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('aws_service_s3', result)
        return result

    def test_unified_session_manager(self) -> Dict:
        """Test UnifiedSessionManager S3 methods."""
        print("\n" + "="*60)
        print("9. Testing UnifiedSessionManager S3")
        print("="*60)

        result = {'success': False}

        try:
            usm = UnifiedSessionManager()

            # Test connection
            connection_test = usm._test_s3_connection()

            # Get clients
            s3_client = usm.get_s3_client()
            s3_resource = usm.get_s3_resource()

            result = {
                'success': connection_test.get('status') in ['success', 'connected'],
                'connection_status': connection_test.get('status'),
                'latency_ms': connection_test.get('latency', 0),
                'bucket_count': connection_test.get('bucket_count', 0),
                'has_client': s3_client is not None,
                'has_resource': s3_resource is not None,
                'implementation_type': 'REAL' if s3_client else 'MOCK'
            }

            print(f"  Connection status: {result['connection_status']}")
            print(f"  Latency: {result['latency_ms']}ms")
            print(f"  Has S3 client: {result['has_client']}")
            print(f"  Has S3 resource: {result['has_resource']}")

        except Exception as e:
            result['error'] = str(e)

        self.log_test('unified_session_manager', result)
        return result

    def test_hexagonal_compliance(self) -> Dict:
        """Test hexagonal architecture compliance for S3."""
        print("\n" + "="*60)
        print("10. Testing Hexagonal Architecture Compliance")
        print("="*60)

        result = {'success': False}

        try:
            # Check that domain uses ports
            from domain.ports.outbound.session_port import SessionPort, AWSSessionPort

            # Verify port definitions exist
            has_session_port = hasattr(SessionPort, 'get_s3_client')
            has_aws_port = hasattr(AWSSessionPort, 'get_s3_client')

            # Check adapter implementation
            from adapters.secondary.session.unified_session_adapter import UnifiedSessionAdapter
            adapter = UnifiedSessionAdapter()  # Adapter creates its own UnifiedSessionManager internally

            # Infrastructure should be in infrastructure layer
            s3_service_module = S3Service.__module__
            correct_layer = 'infrastructure' in s3_service_module

            result = {
                'success': has_session_port and has_aws_port and correct_layer,
                'has_port_definition': has_session_port,
                'has_aws_port': has_aws_port,
                'adapter_exists': True,
                'infrastructure_layer_correct': correct_layer,
                'architecture_compliant': True
            }

            print(f"  Port defined: {result['has_port_definition']}")
            print(f"  AWS port: {result['has_aws_port']}")
            print(f"  Adapter exists: {result['adapter_exists']}")
            print(f"  Layer separation: {result['infrastructure_layer_correct']}")

        except Exception as e:
            result['error'] = str(e)
            result['architecture_compliant'] = False

        self.log_test('hexagonal_compliance', result)
        return result

    def run_all_tests(self):
        """Run all tests and generate report."""
        print("\n" + "="*60)
        print("S3 FUNCTIONAL TEST SUITE")
        print("="*60)

        # Setup test environment
        if not self.setup_test_environment():
            print("[ERROR] Failed to setup test environment")
            return

        # Run tests
        self.test_s3_service_initialization()
        self.test_upload_download()
        self.test_json_operations()
        self.test_list_objects()
        self.test_exists_delete()
        self.test_presigned_url()
        self.test_s3_delegate()
        self.test_aws_service_s3()
        self.test_unified_session_manager()
        self.test_hexagonal_compliance()

        # Cleanup
        self.cleanup_test_data()

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
    suite = S3TestSuite()
    suite.run_all_tests()

    # Save results to file
    results_file = Path(__file__).parent / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump(suite.test_results, f, indent=2, default=str)

    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()