#!/usr/bin/env python3
"""
Run Tensor Logic Examples
==========================
Launcher for tensor logic examples.
"""

import subprocess
import sys
from pathlib import Path

examples_path = Path(__file__).parent / "examples" / "tensor_logic_examples.py"

if not examples_path.exists():
    print(f"❌ Examples not found at: {examples_path}")
    sys.exit(1)

print("🧠 Running Tensor Logic Examples...")
print()

subprocess.run([sys.executable, str(examples_path)])
