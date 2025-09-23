#!/usr/bin/env python3
"""
Quick test to diagnose why chat is returning NONE.
"""

import sys
from pathlib import Path

# Add paths
qa_root = Path(__file__).parent
sys.path.insert(0, str(qa_root))

from common.utilities.path_manager import PathManager
path_mgr = PathManager()
for path in path_mgr.get_python_paths():
    if path not in sys.path:
        sys.path.insert(0, path)

def test_corporate_gateway_directly():
    """Test CorporateLLMGateway directly."""
    print("Testing CorporateLLMGateway directly...")

    try:
        from packages.tidyllm.gateways.corporate_llm_gateway import (
            CorporateLLMGateway, LLMRequest
        )

        gateway = CorporateLLMGateway()
        print("Gateway created")

        request = LLMRequest(
            prompt="Where is Arecibo?",
            model_id="claude-3-haiku",
            user_id="test",
            audit_reason="test"
        )

        print("Processing request...")
        response = gateway.process_request(request)

        print(f"Success: {response.success}")
        if response.success:
            print(f"Response: {response.content}")
        else:
            print(f"Error: {response.error}")

        return response.success

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_usm_bedrock_client():
    """Test UnifiedSessionManager Bedrock client."""
    print("\nTesting UnifiedSessionManager Bedrock client...")

    try:
        from packages.tidyllm.infrastructure.session.unified import UnifiedSessionManager

        usm = UnifiedSessionManager()
        print("USM created")

        bedrock_client = usm.get_bedrock_runtime_client()
        print(f"Bedrock client: {bedrock_client}")
        print(f"Has invoke_model: {hasattr(bedrock_client, 'invoke_model')}")

        if hasattr(bedrock_client, 'invoke_model'):
            print("Testing invoke_model...")
            # This is what CorporateLLMGateway calls
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body='{"messages":[{"role":"user","content":"Where is Arecibo?"}],"max_tokens":100,"anthropic_version":"bedrock-2023-05-31"}',
                contentType="application/json"
            )
            print(f"Response: {response}")
            return True
        else:
            print("No invoke_model method")
            return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_infra_delegate():
    """Test infra_delegate Bedrock."""
    print("\nTesting infra_delegate...")

    try:
        from packages.tidyllm.infrastructure.infra_delegate import get_infra_delegate

        infra = get_infra_delegate()
        print("Infra delegate created")

        result = infra.invoke_bedrock(
            prompt="Where is Arecibo?",
            model_id="claude-3-haiku"
        )

        print(f"Result: {result}")
        return result.get('success', False)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Quick Chat Diagnosis")
    print("=" * 40)

    # Test each layer
    test_corporate_gateway_directly()
    test_usm_bedrock_client()
    test_infra_delegate()