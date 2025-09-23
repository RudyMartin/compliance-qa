#!/usr/bin/env python3
"""
Unified RAG Portal Launcher
===========================
Launches the Unified RAG Portal that manages all 5 RAG systems.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the Unified RAG portal."""
    print("=" * 60)
    print("LAUNCHING UNIFIED RAG PORTAL")
    print("=" * 60)
    print("")
    print("This portal manages all 5 RAG systems:")
    print("1. AI-Powered RAG - AI-enhanced responses")
    print("2. Postgres RAG - Authority-based with SME")
    print("3. Judge RAG - External system integration")
    print("4. Intelligent RAG - Direct database extraction")
    print("5. SME RAG - Full document lifecycle")
    print("")
    print("Starting portal on http://localhost:8527...")
    print("=" * 60)

    # Use PathManager for consistent path handling
    from common.utilities.path_manager import get_path_manager

    path_mgr = get_path_manager()

    # Get the portal file path
    portal_file = Path(path_mgr.get_portal_path("rag")) / "rag_unified_app.py"

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
            "--server.port", "8527",
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