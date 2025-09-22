#!/usr/bin/env python3
"""
Watch for file changes and automatically restart Streamlit
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class StreamlitReloader(FileSystemEventHandler):
    def __init__(self, port=8515):
        self.port = port
        self.process = None
        self.restart_streamlit()

    def on_modified(self, event):
        if event.is_directory:
            return

        # Only restart for Python files
        if event.src_path.endswith('.py'):
            print(f"\n[*] Detected change in: {event.src_path}")
            print("[~] Restarting Streamlit...")
            self.restart_streamlit()

    def restart_streamlit(self):
        # Kill existing process if running
        if self.process:
            print("[!] Stopping current Streamlit instance...")
            self.process.terminate()
            time.sleep(1)
            if self.process.poll() is None:
                self.process.kill()

        # Start new process
        print(f"[>] Starting Streamlit on port {self.port}...")
        self.process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "flow_portal_v4.py",
            "--server.port", str(self.port),
            "--server.headless", "true"
        ])
        print(f"[OK] Streamlit running on http://localhost:{self.port}")
        print("[...] Watching for changes... (Press Ctrl+C to stop)\n")

def main():
    # Get port from command line or use default
    port = 8515
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default {port}")

    # Set up file watcher
    event_handler = StreamlitReloader(port=port)
    observer = Observer()

    # Watch current directory for Python file changes
    watch_path = Path(__file__).parent
    observer.schedule(event_handler, str(watch_path), recursive=True)

    # Start watching
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Stopping file watcher...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()

    observer.join()
    print("[BYE] Watcher stopped")

if __name__ == "__main__":
    main()