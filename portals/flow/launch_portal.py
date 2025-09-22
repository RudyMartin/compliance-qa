#!/usr/bin/env python3
"""
Launch Flow Portal V4 - Unified Launcher
========================================
Single launcher script with configurable port
"""

import streamlit.web.cli as stcli
import sys
import argparse
from pathlib import Path

def launch_portal(port=8501, theme="default"):
    """
    Launch the Flow Portal on specified port

    Args:
        port: Port number (default: 8501)
        theme: Theme preset - "default", "dark", "special"
    """

    portal_file = Path(__file__).parent / "flow_portal_v4.py"

    if not portal_file.exists():
        print(f"❌ Error: Portal file not found at {portal_file}")
        sys.exit(1)

    # Theme presets
    themes = {
        "default": {
            "primaryColor": "#FF4B4B",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F0F2F6",
            "textColor": "#262730"
        },
        "dark": {
            "primaryColor": "#FF6B6B",
            "backgroundColor": "#0E1117",
            "secondaryBackgroundColor": "#262730",
            "textColor": "#FAFAFA"
        },
        "special": {
            "primaryColor": "#FF6B6B",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F5F5F5",
            "textColor": "#262730"
        }
    }

    theme_config = themes.get(theme, themes["default"])

    sys.argv = [
        "streamlit",
        "run",
        str(portal_file),
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        f"--theme.primaryColor={theme_config['primaryColor']}",
        f"--theme.backgroundColor={theme_config['backgroundColor']}",
        f"--theme.secondaryBackgroundColor={theme_config['secondaryBackgroundColor']}",
        f"--theme.textColor={theme_config['textColor']}"
    ]

    print("=" * 60)
    print("🚀 FLOW PORTAL V4 LAUNCHER")
    print("=" * 60)
    print(f"📍 Port: {port}")
    print(f"🎨 Theme: {theme}")
    print(f"🌐 URL: http://localhost:{port}")
    print("=" * 60)
    print("Press CTRL+C to stop")
    print()

    sys.exit(stcli.main())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch Flow Portal V4")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8501,
        help="Port to run on (default: 8501)"
    )
    parser.add_argument(
        "--theme", "-t",
        choices=["default", "dark", "special"],
        default="default",
        help="Theme preset (default: default)"
    )

    args = parser.parse_args()
    launch_portal(args.port, args.theme)