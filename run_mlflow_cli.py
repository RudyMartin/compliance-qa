#!/usr/bin/env python3
"""
MLflow Dashboard Launcher
=========================
Launches the MLflow tracking dashboard.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the MLflow dashboard."""
    print("=" * 60)
    print("LAUNCHING MLFLOW DASHBOARD")
    print("=" * 60)
    print("")
    print("Starting MLflow tracking server on http://localhost:5000...")
    print("")

    # Use PathManager for consistent path handling
    from common.utilities.path_manager import get_path_manager

    path_mgr = get_path_manager()

    # Get portal file path
    portal_file = Path(path_mgr.get_portal_path("mlflow")) / "start_mlflow_dashboard.py"

    # Set up environment to ensure proper imports
    env = os.environ.copy()

    # Get Python paths from PathManager
    python_paths = path_mgr.get_python_paths()

    # Preserve existing PYTHONPATH if any
    existing_path = env.get("PYTHONPATH", "")
    if existing_path:
        python_paths.append(existing_path)

    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    # MLflow dashboard is a regular Python script that launches MLflow server
    try:
        subprocess.run([
            sys.executable, str(portal_file)
        ], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nMLflow dashboard failed to start. Exit code: {e.returncode}")
    except KeyboardInterrupt:
        print("\n\nMLflow dashboard stopped by user.")
    except Exception as e:
        print(f"\nError launching MLflow dashboard: {e}")
        print("Make sure MLflow is installed: pip install mlflow")

if __name__ == "__main__":
    main()