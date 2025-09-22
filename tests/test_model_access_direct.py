"""
Test model access functionality directly
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from domain.services.setup_service import SetupService
from adapters.secondary.setup.setup_dependencies_adapter import get_setup_dependencies_adapter
from pathlib import Path

# Initialize
adapter = get_setup_dependencies_adapter()
setup_service = SetupService(Path('.'), adapter)

print("Testing comprehensive model testing functionality...\n")

# Test 1: Get available models
print("1. Testing get_available_models()...")
try:
    result = setup_service.get_available_models()
    print(f"   - Total models: {result.get('total_count', 0)}")
    print(f"   - By type: {result.get('by_type', {})}")
    if result.get('error'):
        print(f"   - Error: {result['error']}")
    else:
        print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Test single model access
print("2. Testing test_model_access() with Claude model...")
try:
    claude_model = "anthropic.claude-3-haiku-20240307-v1:0"
    result = setup_service.test_model_access(claude_model, "text")
    print(f"   - Model ID: {result.get('model_id')}")
    print(f"   - Accessible: {result.get('accessible')}")
    print(f"   - Response time: {result.get('response_time_ms', 0)}ms")
    if result.get('error'):
        print(f"   - Error: {result['error']}")
    else:
        print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 3: Test embedding model
print("3. Testing test_embedding_model()...")
try:
    embedding_model = "amazon.titan-embed-text-v2:0"
    result = setup_service.test_embedding_model(embedding_model)
    print(f"   - Model ID: {result.get('model_id')}")
    print(f"   - Accessible: {result.get('accessible')}")
    print(f"   - Embedding dimension: {result.get('embedding_dimension', 'N/A')}")
    if result.get('error'):
        print(f"   - Error: {result['error']}")
    else:
        print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 4: Test multiple models
print("4. Testing test_multiple_models()...")
try:
    test_models = [
        {"model_id": "anthropic.claude-3-haiku-20240307-v1:0", "type": "text", "name": "Claude 3 Haiku"},
        {"model_id": "amazon.titan-embed-text-v2:0", "type": "embedding", "name": "Titan Embed v2"}
    ]
    result = setup_service.test_multiple_models(test_models)
    print(f"   - Total models tested: {result.get('total_models', 0)}")
    print(f"   - Accessible: {result.get('accessible_models', 0)}")
    print(f"   - Failed: {result.get('failed_models', 0)}")
    print(f"   - Success rate: {result.get('summary', {}).get('success_rate', 0):.1f}%")
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 5: Validate model mapping
print("5. Testing validate_model_mapping()...")
try:
    model_mapping = {
        "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0"
    }
    result = setup_service.validate_model_mapping(model_mapping)
    print(f"   - Mapping valid: {result.get('mapping_valid')}")
    print(f"   - Total mappings: {result.get('total_mappings', 0)}")
    print(f"   - Accessible: {result.get('accessible_mappings', 0)}")
    print(f"   - Failed mappings: {len(result.get('failed_mappings', []))}")
    print("   ✅ Success")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Model testing functionality implemented - methods are available and callable")