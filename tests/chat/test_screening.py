#!/usr/bin/env python3
"""
Minimal test to see what's happening
"""

import time
from pathlib import Path

def test_basic_functionality():
    print("🚀 Starting minimal test...")
    print("💓 Test 1: Basic print")
    
    time.sleep(1)
    print("💓 Test 2: After 1 second")
    
    base_path = Path("C:/Users/marti/AI-Scoring")
    print(f"💓 Test 3: Base path exists: {base_path.exists()}")
    
    if base_path.exists():
        print("💓 Test 4: Checking directories...")
        dirs_to_check = ['tidyllm', 'v2', 'onboarding', 'pending']
        
        for dir_name in dirs_to_check:
            dir_path = base_path / dir_name
            exists = dir_path.exists()
            print(f"💓   {dir_name}: {'EXISTS' if exists else 'NOT FOUND'}")
            
            if exists:
                try:
                    # Quick file count
                    files = list(dir_path.rglob('*.py'))[:5]  # Just first 5 Python files
                    print(f"💓     Found {len(files)} Python files (showing first 5)")
                    for f in files:
                        print(f"💓       - {f.name}")
                except Exception as e:
                    print(f"💓     Error scanning {dir_name}: {e}")
    
    print("💓 Test 5: Completed successfully!")
    return True

if __name__ == "__main__":
    try:
        result = test_basic_functionality()
        print(f"✅ Test result: {result}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
