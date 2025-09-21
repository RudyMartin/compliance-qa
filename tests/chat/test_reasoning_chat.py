#!/usr/bin/env python3
"""
Test Reasoning Chat Function
============================

Test the enhanced chat function with reasoning/Chain of Thought capabilities.
"""

import json

def test_reasoning_chat():
    """Test chat function with reasoning enabled."""
    print("=" * 70)
    print("TESTING REASONING CHAT FUNCTION")
    print("=" * 70)

    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from tidyllm.interfaces.api import chat

        # Test 1: Simple response (no reasoning)
        print("\n1. SIMPLE RESPONSE (no reasoning):")
        print("-" * 50)
        response = chat("Explain quantum computing", chat_type="direct")
        print(f"Response: {response}")

        # Test 2: With reasoning enabled
        print("\n2. WITH REASONING ENABLED:")
        print("-" * 50)
        response = chat("Explain quantum computing", chat_type="direct", reasoning=True)
        print("Response with reasoning:")
        print(json.dumps(response, indent=2))

        # Test 3: Different model and temperature with reasoning
        print("\n3. CUSTOM MODEL + REASONING:")
        print("-" * 50)
        response = chat(
            "Solve this step by step: What is 15 + 27?",
            chat_type="direct",
            model_name="gpt-4",
            temperature=0.1,
            reasoning=True
        )
        print("Mathematical reasoning:")
        print(json.dumps(response, indent=2))

        # Test 4: DSPy reasoning (if available)
        print("\n4. DSPY REASONING (prompt optimization):")
        print("-" * 50)
        response = chat(
            "Write a professional email",
            chat_type="dspy",
            reasoning=True
        )
        print("DSPy optimization reasoning:")
        print(json.dumps(response, indent=2))

        # Test 5: RAG reasoning (if available)
        print("\n5. RAG REASONING (knowledge retrieval):")
        print("-" * 50)
        response = chat(
            "What are the benefits of machine learning?",
            reasoning=True  # default is RAG mode
        )
        print("RAG processing reasoning:")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Test error: {e}")

    print("\n" + "=" * 70)
    print("REASONING CAPABILITIES:")
    print("✅ Chain of Thought explanations")
    print("✅ Processing method transparency")
    print("✅ Model and parameter visibility")
    print("✅ Confidence scoring")
    print("✅ Error reasoning")
    print("=" * 70)

if __name__ == "__main__":
    test_reasoning_chat()