#!/usr/bin/env python3
"""
Universal App Launcher - Auto-Discovery Version
================================================
Automatically discovers and launches all *_app.py files in the portals/ directory.
Each app runs on its own port, starting from 8501.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def discover_apps() -> List[Dict[str, Any]]:
    """Discover all *_app.py files in the portals directory."""
    print("Discovering apps in portals/ directory...")

    apps = []
    base_port = 8501
    used_ports = set()

    # Special port assignments for known apps
    special_ports = {
        "setup_app.py": 8501,
        "chat_app.py": 8502,
        "first_time_setup_app.py": 8512,
        "rag_app.py": 8525,
        "rag_creator_v3_app.py": 8526,
        "flow_app.py": 8550,
    }

    portals_dir = Path(__file__).parent / "portals"

    # Find all *_app.py files
    for app_file in sorted(portals_dir.glob("**/*_app.py")):
        # Skip __pycache__ and other hidden directories
        if "__pycache__" in str(app_file) or any(part.startswith('.') for part in app_file.parts):
            continue

        # Get relative path from portals directory
        rel_path = app_file.relative_to(portals_dir)
        portal_name = rel_path.parts[0]  # First directory under portals/
        file_name = app_file.name

        # Generate a friendly name
        name = file_name.replace("_app.py", "").replace("_", " ").title()
        full_name = f"{portal_name.title()}/{name}"

        # Assign port
        if file_name in special_ports:
            port = special_ports[file_name]
        else:
            # Find next available port
            while base_port in used_ports or base_port in special_ports.values():
                base_port += 1
            port = base_port
            base_port += 1

        used_ports.add(port)

        apps.append({
            "name": full_name,
            "path": str(app_file),
            "portal": portal_name,
            "file": file_name,
            "port": port
        })

    return sorted(apps, key=lambda x: x["port"])

def launch_app(app_config: Dict[str, Any]) -> Optional[subprocess.Popen]:
    """Launch a single Streamlit app and return its process."""
    name = app_config["name"]
    path = app_config["path"]
    port = app_config["port"]

    print(f"  Launching {name} on port {port}...")

    # Get environment with proper PYTHONPATH
    from common.utilities.path_manager import get_path_manager
    path_mgr = get_path_manager()
    env = os.environ.copy()
    python_paths = path_mgr.get_python_paths()
    if "PYTHONPATH" in env:
        python_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    # Launch streamlit app
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]

    try:
        # Launch without showing window (runs in background)
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return process
    except Exception as e:
        print(f"    [CANCELLED] Failed to launch: {e}")
        return None

def main():
    """Discover and launch all apps."""
    print("=" * 60)
    print("COMPLIANCE QA UNIVERSAL APP LAUNCHER")
    print("=" * 60)

    # Discover all apps
    apps = discover_apps()

    print(f"\n[FOUND] Found {len(apps)} apps to launch:")

    # Group by portal for nice display
    by_portal = {}
    for app in apps:
        portal = app["portal"]
        if portal not in by_portal:
            by_portal[portal] = []
        by_portal[portal].append(app)

    for portal, portal_apps in sorted(by_portal.items()):
        print(f"\n   {portal}/")
        for app in portal_apps:
            print(f"     - {app['file']:<30} -> port {app['port']}")

    print("\n" + "=" * 60)

    # Ask for confirmation
    response = input("\n Launch all apps? (y/n): ").strip().lower()
    if response != 'y':
        print("[CANCELLED] Cancelled")
        return

    print("\n" + "=" * 60)
    print("LAUNCHING SEQUENCE INITIATED")
    print("=" * 60)

    processes = []

    try:
        # Launch each app
        for i, app in enumerate(apps, 1):
            print(f"\n[{i}/{len(apps)}] {app['name']}:")
            process = launch_app(app)

            if process:
                processes.append((app['name'], app['port'], process))
                time.sleep(1.5)  # Small delay between launches
            else:
                print(f"     [SKIPPED]  Skipped")

        # Summary
        print("\n" + "=" * 60)
        print("[SUCCESS] LAUNCH COMPLETE!")
        print("=" * 60)
        print(f"\n[STATUS] Successfully launched {len(processes)} apps:")

        # Group by portal for display
        by_portal_launched = {}
        for name, port, _ in processes:
            portal = name.split("/")[0]
            if portal not in by_portal_launched:
                by_portal_launched[portal] = []
            by_portal_launched[portal].append((name.split("/")[1], port))

        for portal, portal_apps in sorted(by_portal_launched.items()):
            print(f"\n  {portal}:")
            for name, port in portal_apps:
                print(f"    - {name:<25} http://localhost:{port}")

        print("\n Press Ctrl+C to stop all apps")
        print("=" * 60)

        # Keep running until interrupted
        while True:
            time.sleep(5)
            # Check if any process has died
            dead = []
            for name, port, proc in processes:
                if proc.poll() is not None:
                    print(f"\n[SKIPPED]  {name} (port {port}) has stopped")
                    dead.append((name, port, proc))

            for item in dead:
                processes.remove(item)

    except KeyboardInterrupt:
        print("\n\n[STOPPING] STOPPING ALL APPS...")
        print("-" * 40)
        for name, _, proc in processes:
            print(f"  Stopping {name}...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("-" * 40)
        print("[SUCCESS] All apps stopped successfully")

    except Exception as e:
        print(f"\n[CANCELLED] Error: {e}")
        # Clean up any launched processes
        for _, _, proc in processes:
            try:
                proc.terminate()
            except:
                pass

if __name__ == "__main__":
    main()