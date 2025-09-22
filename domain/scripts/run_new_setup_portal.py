#!/usr/bin/env python3
"""
NEW Setup Portal Launcher (Fixed)
==================================
Easy launcher for the student-friendly setup portal.
Fixed path resolution to correctly locate the portal file.
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

    # Get the portal file path (go up from domain/scripts to root, then to portals/setup)
    # Path: domain/scripts/run_new_setup_portal.py -> compliance-qa/portals/setup/new_setup_portal.py
    portal_file = Path(__file__).parent.parent.parent / "portals" / "setup" / "new_setup_portal.py"

    # Check if the file exists
    if not portal_file.exists():
        print(f"\nERROR: Portal file not found!")
        print(f"Looking for: {portal_file}")
        print(f"Current directory: {Path.cwd()}")
        print(f"Script location: {Path(__file__).parent}")

        # Try alternative path (if running from different location)
        alt_portal = Path("portals") / "setup" / "new_setup_portal.py"
        if alt_portal.exists():
            portal_file = alt_portal
            print(f"Found portal at alternative location: {portal_file}")
        else:
            print("\nPlease ensure you're running this from the compliance-qa root directory")
            return 1

    print(f"\nLaunching portal from: {portal_file}")

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
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())