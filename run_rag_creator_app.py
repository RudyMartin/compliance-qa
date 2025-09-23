#!/usr/bin/env python3
"""
RAG Creator V3 Portal Launcher
==============================
Launcher for the Knowledge Base and Retrieval System portal.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the RAG Creator V3 portal."""
    print("=" * 60)
    print("LAUNCHING RAG CREATOR V3 - Knowledge System Portal")
    print("=" * 60)
    print("")
    print("This portal helps you build knowledge bases and retrieval systems.")
    print("")
    print("Features:")
    print("- Document ingestion and processing")
    print("- Embedding generation")
    print("- Vector database management")
    print("- Retrieval testing")
    print("- RAG pipeline configuration")
    print("")
    print("Starting portal on http://localhost:8525...")
    print("=" * 60)

    # Use PathManager for consistent path handling
    from common.utilities.path_manager import get_path_manager

    path_mgr = get_path_manager()

    # Get the portal file path
    portal_file = Path(path_mgr.tidyllm_package_path) / "knowledge_systems" / "migrated" / "portal_rag" / "rag_creator_v3_app.py"

    if not portal_file.exists():
        print(f"Error: Portal file not found at {portal_file}")
        print("Please check your installation.")
        return 1

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
            "--server.port", "8525",
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