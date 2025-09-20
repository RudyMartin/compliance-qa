#!/usr/bin/env python3
"""
NEW Setup Portal Launcher
=========================
Easy launcher for the student-friendly setup portal.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the new setup portal."""
    print("=" * 60)
    print("LAUNCHING SETUP PORTAL - SPECIAL EDITION")
    print("=" * 60)
    print("")
    print("This portal is designed for 12th graders!")
    print("It will guide you step-by-step through setting up your AI system.")
    print("")
    print("Features:")
    print("- Step-by-step setup wizard")
    print("- Clear, simple instructions")
    print("- 4 AI models available")
    print("- All portals accessible")
    print("- Example data included")
    print("")
    print("Starting portal on http://localhost:8512...")
    print("=" * 60)

    # Get the portal file path
    portal_file = Path(__file__).parent / "portals" / "setup" / "new_setup_portal.py"

    # Launch with streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(portal_file),
            "--server.port", "8512",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\nPortal stopped by user.")
    except Exception as e:
        print(f"\nError launching portal: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()