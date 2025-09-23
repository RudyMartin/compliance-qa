#!/usr/bin/env python3
"""
================================================================================
FILENAME: chat_mode_examples.py
DATE: 2025-09-23
PURPOSE: Simple examples of using different chat modes for various business needs
AUTHOR: TidyLLM Team
================================================================================

This file contains ready-to-use chat mode configurations for different domains.
Just copy the function you need and modify for your specific use case.

SETUP REQUIRED:
1. Make sure you have the compliance-qa project installed
2. Ensure AWS credentials are configured
3. Run: python chat_mode_examples.py
================================================================================
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the project to Python path (adjust this path if needed)
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the required modules
try:
    from common.utilities.path_manager import PathManager
    path_mgr = PathManager()
    for path in path_mgr.get_python_paths():
        if path not in sys.path:
            sys.path.insert(0, path)

    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager
    print("✓ Successfully imported chat manager")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the compliance-qa directory")
    sys.exit(1)


# ================================================================================
# SIMPLE CHAT MODE EXAMPLES
# ================================================================================

class SimpleChatModes:
    """
    Easy-to-use chat modes for different business purposes.
    Each method is a pre-configured "recipe" for a specific use case.
    """

    def __init__(self):
        """Initialize the chat manager once for all modes."""
        try:
            self.chat_manager = UnifiedChatManager()
            print("✓ Chat manager initialized")
        except Exception as e:
            print(f"❌ Failed to initialize chat manager: {e}")
            self.chat_manager = None

    # ============================================================================
    # EXAMPLE 1: CUSTOMER SERVICE MODE
    # Use this for: Customer inquiries, support tickets, friendly responses
    # ============================================================================
    def customer_service_chat(self, customer_message):
        """
        Friendly, helpful mode for customer interactions.

        Settings:
        - Model: claude-3-haiku (fast responses)
        - Temperature: 0.7 (conversational tone)
        - Mode: direct (simple Q&A)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=customer_message,
                mode="direct",              # Simple direct response
                model="claude-3-haiku",     # Fast model for quick responses
                temperature=0.7,            # Warm, friendly tone
                max_tokens=500              # Keep responses concise
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    # ============================================================================
    # EXAMPLE 2: LEGAL DOCUMENT MODE
    # Use this for: Contracts, compliance docs, legal analysis
    # ============================================================================
    def legal_document_chat(self, legal_query):
        """
        High-accuracy mode for legal and compliance matters.

        Settings:
        - Model: claude-3-opus (highest accuracy)
        - Temperature: 0.1 (very precise, consistent)
        - Mode: direct (controlled responses)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=f"[Legal Context - Require Precision] {legal_query}",
                mode="direct",
                model="claude-3-opus",      # Most accurate model
                temperature=0.1,            # Very low - need consistency
                max_tokens=2000             # Allow detailed analysis
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    # ============================================================================
    # EXAMPLE 3: TECHNICAL SUPPORT MODE
    # Use this for: Bug reports, technical questions, troubleshooting
    # ============================================================================
    def technical_support_chat(self, technical_issue):
        """
        Problem-solving mode for technical issues.

        Settings:
        - Model: claude-3-sonnet (good balance)
        - Temperature: 0.4 (logical, structured)
        - Mode: hybrid (chooses best approach)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=f"Technical Issue: {technical_issue}",
                mode="hybrid",              # Let it choose best approach
                model="claude-3-sonnet",    # Balanced model
                temperature=0.4,            # Logical, structured responses
                max_tokens=1500             # Room for detailed steps
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    # ============================================================================
    # EXAMPLE 4: FINANCIAL ANALYSIS MODE
    # Use this for: Financial reports, risk assessment, market analysis
    # ============================================================================
    def financial_analysis_chat(self, financial_query):
        """
        Analytical mode for financial and business analysis.

        Settings:
        - Model: claude-3-opus (complex analysis)
        - Temperature: 0.2 (accurate, careful)
        - Mode: rag (uses knowledge base)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=f"Financial Analysis Request: {financial_query}",
                mode="rag",                 # Use knowledge base
                model="claude-3-opus",      # Best for complex analysis
                temperature=0.2,            # Low for accuracy
                max_tokens=2000             # Detailed analysis
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    # ============================================================================
    # EXAMPLE 5: CREATIVE WRITING MODE
    # Use this for: Marketing copy, content creation, brainstorming
    # ============================================================================
    def creative_writing_chat(self, creative_prompt):
        """
        Creative mode for content generation and brainstorming.

        Settings:
        - Model: claude-3-sonnet (creative but coherent)
        - Temperature: 0.8 (creative, varied)
        - Mode: direct (no constraints)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=creative_prompt,
                mode="direct",
                model="claude-3-sonnet",    # Good for creative tasks
                temperature=0.8,            # High for creativity
                max_tokens=1000             # Room for creative content
            )
            return response
        except Exception as e:
            return f"Error: {e}"

    # ============================================================================
    # EXAMPLE 6: QUICK FACT CHECK MODE
    # Use this for: Quick answers, fact checking, simple queries
    # ============================================================================
    def quick_fact_check(self, question):
        """
        Fast mode for simple questions and fact checking.

        Settings:
        - Model: claude-3-haiku (fastest)
        - Temperature: 0.3 (factual)
        - Mode: direct (simple)
        """
        if not self.chat_manager:
            return "Chat service is not available"

        try:
            response = self.chat_manager.chat(
                message=question,
                mode="direct",
                model="claude-3-haiku",     # Fastest model
                temperature=0.3,            # Factual responses
                max_tokens=200              # Brief answers
            )
            return response
        except Exception as e:
            return f"Error: {e}"


# ================================================================================
# HOW TO USE THIS FILE
# ================================================================================

def main():
    """
    Example usage of the different chat modes.
    Run this file directly to see the modes in action.
    """
    print("\n" + "="*80)
    print("CHAT MODE EXAMPLES - DEMONSTRATION")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # Initialize the chat modes
    chat = SimpleChatModes()

    # Example conversations for each mode
    examples = [
        {
            "mode": "Customer Service",
            "function": chat.customer_service_chat,
            "message": "How do I reset my password?"
        },
        {
            "mode": "Legal Document",
            "function": chat.legal_document_chat,
            "message": "What are the key risks in this non-disclosure agreement?"
        },
        {
            "mode": "Technical Support",
            "function": chat.technical_support_chat,
            "message": "My application crashes when I click the submit button"
        },
        {
            "mode": "Financial Analysis",
            "function": chat.financial_analysis_chat,
            "message": "What is the impact of rising interest rates on tech stocks?"
        },
        {
            "mode": "Creative Writing",
            "function": chat.creative_writing_chat,
            "message": "Write a catchy tagline for an eco-friendly coffee brand"
        },
        {
            "mode": "Quick Fact Check",
            "function": chat.quick_fact_check,
            "message": "What is the capital of Australia?"
        }
    ]

    # Run each example
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['mode']} Mode")
        print("-" * 40)
        print(f"Query: {example['message']}")
        print(f"Response: ", end="")

        # Get the response
        response = example['function'](example['message'])

        # Print first 200 characters of response
        if len(str(response)) > 200:
            print(f"{str(response)[:200]}...")
        else:
            print(response)

    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)


# ================================================================================
# QUICK START GUIDE
# ================================================================================
"""
TO USE IN YOUR OWN CODE:

1. Import this file:
   from chat_mode_examples import SimpleChatModes

2. Create an instance:
   chat = SimpleChatModes()

3. Use any mode:
   response = chat.customer_service_chat("How can I track my order?")
   print(response)

CUSTOMIZATION TIPS:

- Temperature: Lower (0.1-0.3) = Consistent, Higher (0.7-0.9) = Creative
- Model: haiku = Fast, sonnet = Balanced, opus = Most Accurate
- Max Tokens: 200 = Brief, 1000 = Detailed, 4000 = Maximum

COMMON ISSUES:

1. Import Error: Make sure you're in the compliance-qa directory
2. No Response: Check your AWS credentials are configured
3. Slow Response: Try using claude-3-haiku for faster responses
"""


if __name__ == "__main__":
    # Run the demonstration
    main()

    # Print usage instructions
    print("\nTO USE THIS IN YOUR CODE:")
    print("-" * 40)
    print("from chat_mode_examples import SimpleChatModes")
    print("chat = SimpleChatModes()")
    print('response = chat.customer_service_chat("Your question here")')
    print("print(response)")