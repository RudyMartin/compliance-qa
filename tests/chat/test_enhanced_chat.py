#!/usr/bin/env python3
"""
Test Enhanced Chat Function
===========================

Test the new multi-mode chat functionality with different processing types.
"""

def test_enhanced_chat():
    """Test the enhanced chat function with different modes."""
    print("=" * 60)
    print("TESTING ENHANCED CHAT FUNCTION")
    print("=" * 60)

    # Test direct Bedrock mode (should work)
    print("\n1. DIRECT MODE (Bedrock only):")
    print("-" * 40)
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from tidyllm.interfaces.api import chat
        response = chat("Hello, how are you?", chat_type="direct")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Test with custom model and temperature
    print("\n2. DIRECT MODE with custom model/temp:")
    print("-" * 40)
    try:
        response = chat(
            "Explain quantum computing",
            chat_type="direct",
            model_name="gpt-4",
            temperature=0.1
        )
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Test DSPy mode
    print("\n3. DSPY MODE (Prompt optimization):")
    print("-" * 40)
    try:
        response = chat("Write a summary", chat_type="dspy")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    # Test default RAG mode
    print("\n4. DEFAULT MODE (RAG-enhanced):")
    print("-" * 40)
    try:
        response = chat("What is machine learning?")  # default mode
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("CHAT MODES AVAILABLE:")
    print("- default: RAG-enhanced responses with context retrieval")
    print("- direct:  Direct Bedrock model calls (no RAG)")
    print("- dspy:    DSPy prompt optimization -> Bedrock")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_chat()