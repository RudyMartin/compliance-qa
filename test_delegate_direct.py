#!/usr/bin/env python3
"""Test Bedrock delegate directly."""

import sys
from pathlib import Path

# Add packages to path
qa_root = Path(__file__).parent
sys.path.insert(0, str(qa_root / 'packages'))
sys.path.insert(0, str(qa_root))

# Now import the delegate
from tidyllm.infrastructure.bedrock_delegate import get_bedrock_delegate

def test_delegate():
    print("Testing Bedrock Delegate")
    print("=" * 60)

    delegate = get_bedrock_delegate()

    print(f"Delegate type: {type(delegate)}")
    print(f"Delegate available: {delegate.is_available()}")

    # Test a simple call
    print("\nTesting invoke_model...")
    response = delegate.invoke_model(
        prompt="What is 2+2?",
        model_id="anthropic.claude-3-haiku-20240307-v1:0"
    )

    print(f"Response: {response}")

    # Test list models
    print("\nTesting list_foundation_models...")
    models = delegate.list_foundation_models()
    print(f"Found {len(models)} models")
    if models:
        print(f"First model: {models[0] if isinstance(models[0], str) else models[0].get('modelId', 'unknown')}")

if __name__ == "__main__":
    test_delegate()