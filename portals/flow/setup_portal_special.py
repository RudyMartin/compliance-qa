"""
🚀 Setup Portal - Special Edition
==================================
Port 8510 - Avoiding conflicts with 9 existing Streamlit instances
"""

import streamlit as st
import streamlit.web.cli as stcli
import sys
from pathlib import Path
import time

# Using port 8510 to avoid conflicts with existing 9 instances (likely 8501-8509)
SPECIAL_PORT = 8510

def launch_special_edition():
    """Launch the special edition setup portal on port 8510"""

    print("=" * 60)
    print("🚀 SETUP PORTAL - SPECIAL EDITION")
    print("=" * 60)
    print(f"📍 Port: {SPECIAL_PORT} (avoiding 9 active instances)")
    print(f"🌐 URL: http://localhost:{SPECIAL_PORT}")
    print("=" * 60)

    # Create the special edition portal file if needed
    portal_file = Path(__file__).parent / "flow_portal_v4.py"

    if not portal_file.exists():
        print("⚠️ Portal file not found, using existing flow_portal_v4.py")

    # Launch with special configuration
    sys.argv = [
        "streamlit",
        "run",
        str(portal_file),
        f"--server.port={SPECIAL_PORT}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--theme.primaryColor=#FF6B6B",
        "--theme.backgroundColor=#FFFFFF",
        "--theme.secondaryBackgroundColor=#F5F5F5",
        "--theme.textColor=#262730"
    ]

    print(f"🔥 Launching Flow Portal V4 on port {SPECIAL_PORT}...")
    print("Press CTRL+C to stop")

    sys.exit(stcli.main())

if __name__ == "__main__":
    launch_special_edition()