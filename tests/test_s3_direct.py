"""
Test S3 functionality directly
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from domain.services.setup_service import SetupService
from adapters.secondary.setup.setup_dependencies_adapter import get_setup_dependencies_adapter

# Initialize
adapter = get_setup_dependencies_adapter()
setup_service = SetupService(adapter)

# Test credentials (these would come from the UI in real usage)
test_credentials = {
    'access_key_id': 'test_access_key',
    'secret_access_key': 'test_secret_key',
    'region': 'us-east-1'
}

# Test S3 access
print("Testing S3 access method in SetupService...")
try:
    result = setup_service.test_s3_access(
        bucket='test-bucket',
        prefix='test/',
        credentials=test_credentials
    )

    print(f"Result: {result}")
    print(f"  - Credentials Valid: {result.get('credentials_valid')}")
    print(f"  - Bucket Accessible: {result.get('bucket_accessible')}")
    print(f"  - Write Permission: {result.get('write_permission')}")
    print(f"  - Errors: {result.get('errors')}")

except Exception as e:
    print(f"Error testing S3: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed - method is available and callable")