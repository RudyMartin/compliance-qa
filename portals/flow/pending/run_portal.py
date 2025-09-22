"""
Run Flow Portal V4 - Launch Script with Port Configuration
==========================================================
"""

import streamlit.web.cli as stcli
import sys
from pathlib import Path

def run_portal(port=8501):
    """Launch the Flow Portal on specified port"""

    portal_file = Path(__file__).parent / "flow_portal_v4.py"

    sys.argv = [
        "streamlit",
        "run",
        str(portal_file),
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--theme.primaryColor=#FF4B4B",
        "--theme.backgroundColor=#FFFFFF",
        "--theme.secondaryBackgroundColor=#F0F2F6",
        "--theme.textColor=#262730"
    ]

    print(f"🚀 Launching Flow Portal V4 on port {port}")
    print(f"📍 URL: http://localhost:{port}")
    print("Press CTRL+C to stop")

    sys.exit(stcli.main())

if __name__ == "__main__":
    # Check for custom port
    import argparse
    parser = argparse.ArgumentParser(description="Run Flow Portal V4")
    parser.add_argument("--port", type=int, default=8501, help="Port to run on (default: 8501)")
    args = parser.parse_args()

    run_portal(args.port)