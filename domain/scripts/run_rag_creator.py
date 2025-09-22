#!/usr/bin/env python3
"""
RAG Creator V3 Portal Launcher
==============================
Launcher for the Knowledge Base and Retrieval System portal.
"""

import subprocess
import sys
from pathlib import Path

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

    # Get the portal file path
    portal_file = Path(__file__).parent / "packages" / "tidyllm" / "knowledge_systems" / "migrated" / "portal_rag" / "rag_creator_v3.py"

    if not portal_file.exists():
        print(f"Error: Portal file not found at {portal_file}")
        print("Please check your installation.")
        return 1

    # Launch with streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(portal_file),
            "--server.port", "8525",
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