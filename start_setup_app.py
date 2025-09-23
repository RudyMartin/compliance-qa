#!/usr/bin/env python3
"""
Setup Portal Launcher
=====================
Launches the main setup portal with proper Python path configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the setup portal."""
    # Use current directory as root
    root_dir = Path(__file__).parent

    # Get portal file path directly
    portal_file = root_dir / "portals" / "setup" / "first_time_setup_app.py"

    # Set up environment to ensure proper imports
    env = os.environ.copy()

    # Set up Python paths
    python_paths = [
        str(root_dir),
        str(root_dir / "packages"),
        str(root_dir / "packages" / "tidyllm")
    ]

    # Preserve existing PYTHONPATH if any
    existing_path = env.get("PYTHONPATH", "")
    if existing_path:
        python_paths.append(existing_path)

    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(portal_file),
            "--server.port", "8501",
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