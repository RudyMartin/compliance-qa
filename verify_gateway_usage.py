#!/usr/bin/env python3
"""
Verify that all LLM calls go through CorporateLLMGateway
=========================================================

This script verifies that NO direct AWS/Bedrock calls are being made
and that everything goes through the gateway that tracks all calls.
"""

import sys
from pathlib import Path

# Setup paths using PathManager
qa_root = Path(__file__).parent
if str(qa_root) not in sys.path:
    sys.path.insert(0, str(qa_root))

# Import PathManager and set up paths
from common.utilities.path_manager import PathManager
path_mgr = PathManager()
for path in path_mgr.get_python_paths():
    if path not in sys.path:
        sys.path.insert(0, path)


def test_unified_chat_manager():
    """Test UnifiedChatManager uses gateway."""
    print("\n1. Testing UnifiedChatManager...")
    try:
        from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode

        manager = UnifiedChatManager()

        # Test direct chat mode
        response = manager.chat(
            "Test message",
            mode=ChatMode.DIRECT,
            model="claude-3-haiku",
            reasoning=True
        )

        if isinstance(response, dict):
            method = response.get('method', 'unknown')
            tracked = response.get('gateway_tracked', False)
            print(f"   ✓ Method: {method}")
            print(f"   ✓ Gateway tracked: {tracked}")

            if method == "corporate_gateway" and tracked:
                print("   ✅ PASS: Using CorporateLLMGateway with tracking")
            else:
                print("   ❌ FAIL: Not using gateway properly")
        else:
            print(f"   ❌ FAIL: Unexpected response type: {type(response)}")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")


def test_infra_delegate():
    """Test InfraDelegate uses gateway."""
    print("\n2. Testing InfraDelegate...")
    try:
        from packages.tidyllm.infrastructure.infra_delegate import get_infra_delegate

        delegate = get_infra_delegate()

        # Test invoke_bedrock
        response = delegate.invoke_bedrock("Test prompt", "claude-3-haiku")

        tracked = response.get('gateway_tracked', False)
        success = response.get('success', False)

        print(f"   ✓ Success: {success}")
        print(f"   ✓ Gateway tracked: {tracked}")

        if tracked:
            print("   ✅ PASS: Using gateway with tracking")
        else:
            print("   ❌ FAIL: Not tracking calls through gateway")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")


def test_dspy_service():
    """Test DSPy service uses gateway."""
    print("\n3. Testing DSPy Service...")
    try:
        from packages.tidyllm.services.dspy_service import DSPyService

        service = DSPyService()

        # Check if it has CorporateLLMGateway
        if hasattr(service, 'adapter'):
            adapter_type = type(service.adapter).__name__
            print(f"   ✓ Adapter type: {adapter_type}")

            if adapter_type == "CorporateLLMGateway":
                print("   ✅ PASS: Using CorporateLLMGateway")
            else:
                print(f"   ❌ FAIL: Using {adapter_type} instead of gateway")
        else:
            print("   ❌ FAIL: No adapter found")

    except Exception as e:
        print(f"   ⚠️ WARNING: DSPy not available: {e}")


def test_corporate_gateway():
    """Test CorporateLLMGateway directly."""
    print("\n4. Testing CorporateLLMGateway directly...")
    try:
        from packages.tidyllm.gateways.corporate_llm_gateway import CorporateLLMGateway, LLMRequest

        gateway = CorporateLLMGateway()

        # Check status
        status = gateway.get_status()
        print(f"   ✓ Gateway name: {status['gateway_name']}")
        print(f"   ✓ Cost tracking: {status['cost_tracking']}")

        # Test a request
        request = LLMRequest(
            prompt="Test prompt",
            model_id="claude-3-haiku",
            user_id="test_user",
            audit_reason="verification_test"
        )

        response = gateway.process_request(request)

        if response.audit_trail:
            print(f"   ✓ Audit trail created: {bool(response.audit_trail)}")
            print(f"   ✓ User tracked: {response.audit_trail.get('user_id')}")
            print(f"   ✓ Reason logged: {response.audit_trail.get('audit_reason')}")
            print("   ✅ PASS: Gateway tracking all calls properly")
        else:
            print("   ❌ FAIL: No audit trail created")

    except Exception as e:
        print(f"   ❌ ERROR: {e}")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("VERIFYING ALL LLM CALLS GO THROUGH CORPORATELLMGATEWAY")
    print("=" * 60)
    print("\nNO DIRECT AWS CALLS SHOULD BE MADE!")
    print("ALL CALLS MUST BE TRACKED BY THE GATEWAY!")

    # Run tests
    test_unified_chat_manager()
    test_infra_delegate()
    test_dspy_service()
    test_corporate_gateway()

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()