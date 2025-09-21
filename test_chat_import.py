#!/usr/bin/env python3
"""
Test Chat Import and Functionality
===================================
Verifies that the chat imports work correctly.
"""

import sys
from pathlib import Path

# Add qa_root to path (same as portal does)
qa_root = Path(__file__).parent
sys.path.insert(0, str(qa_root))

print("=" * 60)
print("TESTING CHAT IMPORTS")
print("=" * 60)

# Test 1: Import UnifiedChatManager using local path
try:
    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
    print("[OK] Import UnifiedChatManager from packages.tidyllm - SUCCESS")

    # Initialize the chat manager
    chat_manager = UnifiedChatManager()
    print("[OK] UnifiedChatManager initialized")

    # Test chat modes
    modes = [mode.value for mode in ChatMode]
    print(f"[OK] Available chat modes: {', '.join(modes)}")

except ImportError as e:
    print(f"[FAIL] Import UnifiedChatManager: {e}")
except Exception as e:
    print(f"[ERROR] UnifiedChatManager initialization: {e}")

# Test 2: Import infrastructure services
try:
    from infrastructure.yaml_loader import get_settings_loader
    from infrastructure.services.aws_service import get_aws_service

    settings_loader = get_settings_loader()
    aws_service = get_aws_service()

    print("[OK] Infrastructure services imported successfully")
    print(f"[OK] AWS Service available: {aws_service.is_available()}")

except ImportError as e:
    print(f"[FAIL] Import infrastructure services: {e}")
except Exception as e:
    print(f"[ERROR] Infrastructure services: {e}")

# Test 3: Test a simple chat call
if 'chat_manager' in locals():
    try:
        print("\n" + "=" * 60)
        print("TESTING CHAT FUNCTIONALITY")
        print("=" * 60)

        response = chat_manager.chat(
            message="Hello, test message",
            mode=ChatMode.DIRECT,
            model="claude-3-sonnet"
        )

        if response:
            print("[OK] Chat call successful")
            print(f"Response type: {type(response)}")
            print(f"Response preview: {str(response)[:100]}...")
        else:
            print("[WARN] Chat returned empty response")

    except Exception as e:
        print(f"[ERROR] Chat call failed: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)