#!/usr/bin/env python3
"""
Visual Demo Portal Launcher
============================
Launches the Visual Demo Portal for TidyLLM demo systems interface.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the Visual Demo portal."""
    print("=" * 60)
    print("LAUNCHING VISUAL DEMO PORTAL")
    print("=" * 60)
    print("")
    print("Visual interface for demo team interactions.")
    print("")
    print("Starting portal on http://localhost:8504...")
    print("=" * 60)

    # Use PathManager for consistent path handling
    from common.utilities.path_manager import get_path_manager

    path_mgr = get_path_manager()

    # Get the portal file path
    portal_file = Path(path_mgr.get_portal_path("demo")) / "visual_demo_app.py"

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
            "--server.port", "8504",
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