#!/usr/bin/env python3
"""
First Time Setup Portal Launcher
=================================
Easy launcher for first-time users and students to configure the system.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the first-time setup portal."""
    print("=" * 60)
    print("LAUNCHING FIRST-TIME SETUP PORTAL")
    print("=" * 60)
    print("")
    print("Welcome! This portal helps first-time users set up the system.")
    print("Perfect for students and new users - guides you step-by-step!")
    print("")
    print("Features:")
    print("- Modular 5-step setup wizard")
    print("- System status overview")
    print("- AWS S3 configuration")
    print("- AI model setup (Bedrock)")
    print("- Database maintenance tools")
    print("- Portal discovery and launch")
    print("")
    print("Starting portal on http://localhost:8512...")
    print("=" * 60)

    # Use PathManager for consistent path handling
    from common.utilities.path_manager import get_path_manager

    path_mgr = get_path_manager()

    # Get the portal file path - using new modular version
    portal_file = Path(path_mgr.get_portal_path("setup")) / "first_time_setup_app_new.py"

    # Set up environment to ensure proper imports
    env = os.environ.copy()

    # Get Python paths from PathManager
    python_paths = path_mgr.get_python_paths()

    # Preserve existing PYTHONPATH if any
    existing_path = env.get("PYTHONPATH", "")
    if existing_path:
        python_paths.append(existing_path)

    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    # Launch with streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(portal_file),
            "--server.port", "8512",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ], env=env)
    except KeyboardInterrupt:
        print("\n\nPortal stopped by user.")
    except Exception as e:
        print(f"\nError launching portal: {e}")
        print("Make sure Streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()