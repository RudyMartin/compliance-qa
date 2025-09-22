#!/usr/bin/env python3
"""
Test Chat with Real Bedrock Implementation
"""

import sys
from pathlib import Path

# Add parent to path
qa_root = Path(__file__).parent
sys.path.insert(0, str(qa_root))

from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode

def test_direct_chat():
    """Test direct chat mode with real Bedrock."""
    print("\n" + "="*60)
    print("TESTING DIRECT CHAT WITH REAL BEDROCK")
    print("="*60)

    chat_manager = UnifiedChatManager()

    # Test with a simple message
    test_message = "What is 2+2?"

    print(f"\nSending message: {test_message}")
    print("-" * 40)

    response = chat_manager.chat(
        message=test_message,
        mode=ChatMode.DIRECT,
        model="claude-3-haiku",
        temperature=0.5,
        reasoning=True
    )

    if isinstance(response, dict):
        print(f"Response: {response.get('response', 'No response')}")
        print(f"Method: {response.get('method', 'unknown')}")
        print(f"Model: {response.get('model', 'unknown')}")
        print(f"Confidence: {response.get('confidence', 0)}")

        # Check if it's a real response or mock
        if 'fallback' in response.get('method', ''):
            print("\n[WARNING] Got fallback/mock response!")
        elif 'direct_bedrock' in response.get('method', ''):
            print("\n[SUCCESS] Got real Bedrock response!")
        else:
            print(f"\n[INFO] Got response via: {response.get('method', 'unknown')}")
    else:
        print(f"Response: {response}")

def test_multiple_models():
    """Test multiple Claude models."""
    print("\n" + "="*60)
    print("TESTING MULTIPLE CLAUDE MODELS")
    print("="*60)

    chat_manager = UnifiedChatManager()
    models = ['claude-3-haiku', 'claude-3-sonnet', 'claude-2']
    test_message = "Hi, what model are you?"

    for model in models:
        print(f"\nTesting {model}...")
        print("-" * 30)

        try:
            response = chat_manager.chat(
                message=test_message,
                mode=ChatMode.DIRECT,
                model=model,
                temperature=0.5,
                reasoning=False
            )

            if isinstance(response, str):
                # Truncate long responses
                if len(response) > 100:
                    print(f"Response: {response[:100]}...")
                else:
                    print(f"Response: {response}")
            else:
                print(f"Response type: {type(response)}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Chat with Real Bedrock Implementation")
    print("=" * 60)

    # Test direct chat
    test_direct_chat()

    # Test multiple models
    test_multiple_models()

    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)