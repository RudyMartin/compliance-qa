#!/usr/bin/env python3
"""
Launch Tensor Logic Chat Portal
================================
Convenience launcher for the tensor logic Streamlit chat interface.
"""

import subprocess
import sys
from pathlib import Path

# Get portal path
portal_path = Path(__file__).parent / "portals" / "chat" / "tensor_logic_chat.py"

if not portal_path.exists():
    print(f"❌ Portal not found at: {portal_path}")
    sys.exit(1)

print("🧠 Launching Tensor Logic Chat Portal...")
print(f"   Portal: {portal_path}")
print()
print("📝 Tips:")
print("   - Use T=0.0 for certifiable compliance checks")
print("   - Use T=0.2-0.4 for hybrid risk assessment")
print("   - Use T=0.5+ for exploratory similarity search")
print()
print("🌐 Opening in browser...")
print()

# Launch Streamlit
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(portal_path),
    "--server.port=8504",
    "--theme.base=light"
])
