#!/usr/bin/env python3
"""
Relaunch Flow Portal V4
======================
Kills existing instance and restarts to pick up tab file changes
"""

import os
import sys
import time
import signal
import psutil
import subprocess
from pathlib import Path

def kill_port_process(port):
    """Kill process using a specific port"""
    print(f"Checking for processes on port {port}...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"  Killing {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    time.sleep(1)
                    if proc.is_running():
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def launch_portal(port=8516):
    """Launch the Flow Portal V4"""
    print("\n" + "="*50)
    print("RELAUNCHING FLOW PORTAL V4")
    print("="*50 + "\n")

    # Kill existing instance
    kill_port_process(port)

    print(f"\nStarting Flow Portal V4 on port {port}...")
    print(f"URL: http://localhost:{port}")
    print("\nPress Ctrl+C to stop\n")
    print("="*50 + "\n")

    # Change to portal directory
    portal_dir = Path(__file__).parent
    os.chdir(portal_dir)

    # Launch streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "flow_portal_v4.py",
        "--server.port", str(port),
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nPortal stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    # Allow custom port as argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8516
    launch_portal(port)