#!/usr/bin/env python3
"""
Portal Startup Script for qa-shipping Portal System

Orchestrated startup of all 7 portals with dependency management.
Part of Phase 1: Security & Configuration Cleanup.
"""

import asyncio
import sys
import os
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.portal_config import get_portal_config_manager, PortalDefinition
from config.credential_validator import quick_health_check


def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("QA-SHIPPING PORTAL SYSTEM - Portal Startup")
    print("=" * 60)
    print("Orchestrated startup of 7 portal system")
    print()


class PortalStartupManager:
    """Manages the orchestrated startup of all portals."""

    def __init__(self):
        self.config_mgr = get_portal_config_manager()
        self.running_portals: Dict[str, subprocess.Popen] = {}
        self.startup_order = self.config_mgr._get_startup_order()

    async def validate_prerequisites(self) -> bool:
        """Validate system prerequisites."""
        print("🔍 Validating system prerequisites...")

        # Run environment validation script
        validation_script = Path(__file__).parent / "validate_environment.py"
        if validation_script.exists():
            result = subprocess.run([sys.executable, str(validation_script)],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Environment validation failed")
                print(result.stdout)
                return False
        else:
            # Fallback to quick health check
            healthy = await quick_health_check()
            if not healthy:
                print("❌ Quick health check failed")
                return False

        print("✅ Prerequisites validated")
        return True

    def start_portal(self, portal: PortalDefinition) -> bool:
        """Start a single portal."""
        print(f"🚀 Starting {portal.title} (Port {portal.port})...")

        # Check if port is already in use
        if self.is_port_in_use(portal.port):
            print(f"⚠️  Port {portal.port} already in use - skipping {portal.name}")
            return False

        # Build command
        script_path = Path(portal.script_path)
        if not script_path.exists():
            print(f"❌ Script not found: {portal.script_path}")
            return False

        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(script_path),
            "--server.port", str(portal.port),
            "--server.address", "localhost",
            "--server.headless", "true"
        ]

        try:
            # Start the portal process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(Path(__file__).parent.parent)  # Run from qa-shipping root
            )

            self.running_portals[portal.name] = process

            # Wait a moment for startup
            time.sleep(2)

            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {portal.title} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {portal.title} failed to start")
                print(f"   Error: {stderr}")
                return False

        except Exception as e:
            print(f"❌ Failed to start {portal.title}: {e}")
            return False

    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        try:
            response = requests.get(f"http://localhost:{port}", timeout=1)
            return True
        except requests.exceptions.RequestException:
            return False

    def wait_for_portal_health(self, portal: PortalDefinition, timeout: int = 30) -> bool:
        """Wait for portal to become healthy."""
        if not portal.health_check_url:
            return True  # No health check available

        print(f"🏥 Waiting for {portal.title} health check...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(portal.health_check_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {portal.title} is healthy")
                    return True
            except requests.exceptions.RequestException:
                pass

            time.sleep(2)

        print(f"⚠️  {portal.title} health check timeout")
        return False

    def validate_portal_dependencies(self, portal: PortalDefinition) -> bool:
        """Validate portal dependencies are met."""
        if not portal.dependencies:
            return True

        print(f"🔗 Validating dependencies for {portal.title}...")

        validation_results = self.config_mgr.validate_portal_dependencies(portal.name)

        for dependency, valid in validation_results.items():
            status = "✅" if valid else "❌"
            print(f"  {status} {dependency}")

        all_valid = all(validation_results.values())
        if not all_valid:
            print(f"❌ {portal.title} has unmet dependencies")
            return False

        return True

    async def start_all_portals(self) -> Dict[str, bool]:
        """Start all enabled portals in dependency order."""
        print("🚀 Starting all portals in dependency order...")
        print(f"📋 Startup order: {' → '.join(self.startup_order)}")
        print()

        results = {}
        enabled_portals = self.config_mgr.get_enabled_portals()

        for portal_name in self.startup_order:
            # Find the portal definition
            portal = next((p for p in enabled_portals if p.name == portal_name), None)
            if not portal:
                print(f"⚠️  Portal '{portal_name}' not found or disabled - skipping")
                results[portal_name] = False
                continue

            # Validate dependencies
            if not self.validate_portal_dependencies(portal):
                results[portal_name] = False
                continue

            # Start the portal
            success = self.start_portal(portal)
            results[portal_name] = success

            if success:
                # Wait for health check
                self.wait_for_portal_health(portal)
            else:
                print(f"⚠️  Continuing with remaining portals...")

            print()  # Add spacing between portals

        return results

    def stop_portal(self, portal_name: str):
        """Stop a specific portal."""
        if portal_name in self.running_portals:
            print(f"🛑 Stopping {portal_name}...")
            process = self.running_portals[portal_name]
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.running_portals[portal_name]
            print(f"✅ {portal_name} stopped")

    def stop_all_portals(self):
        """Stop all running portals."""
        print("🛑 Stopping all portals...")
        for portal_name in list(self.running_portals.keys()):
            self.stop_portal(portal_name)
        print("✅ All portals stopped")

    def get_portal_status(self) -> Dict[str, str]:
        """Get status of all portals."""
        status = {}
        all_portals = self.config_mgr.get_all_portals()

        for name, portal in all_portals.items():
            if not portal.enabled:
                status[name] = "disabled"
            elif self.is_port_in_use(portal.port):
                status[name] = "running"
            else:
                status[name] = "stopped"

        return status

    def print_portal_status(self):
        """Print current portal status."""
        print("📊 Portal Status:")
        status = self.get_portal_status()
        urls = self.config_mgr.get_portal_urls()

        for name, state in status.items():
            portal = self.config_mgr.get_portal(name)
            icon = {"running": "🟢", "stopped": "🔴", "disabled": "⚪"}[state]
            print(f"  {icon} {portal.title} ({name}): {state.upper()}")
            if state == "running" and name in urls:
                print(f"     URL: {urls[name]}")


async def main():
    """Main startup routine."""
    print_banner()

    startup_mgr = PortalStartupManager()

    try:
        # Validate prerequisites
        if not await startup_mgr.validate_prerequisites():
            print("❌ Prerequisites not met. Please fix issues and try again.")
            return 1

        # Start all portals
        results = await startup_mgr.start_all_portals()

        # Print summary
        print("=" * 60)
        print("STARTUP SUMMARY")
        print("=" * 60)

        successful = sum(results.values())
        total = len(results)

        print(f"✅ Successfully started: {successful}/{total} portals")

        if successful < total:
            print(f"❌ Failed to start: {total - successful} portals")
            for name, success in results.items():
                if not success:
                    print(f"  • {name}")

        print()
        startup_mgr.print_portal_status()

        if successful > 0:
            print(f"\n🎉 Portal system is running!")
            print(f"💡 Use Ctrl+C to stop all portals")

            # Keep running until interrupted
            try:
                while True:
                    await asyncio.sleep(10)
            except KeyboardInterrupt:
                print(f"\n🛑 Shutdown requested...")
                startup_mgr.stop_all_portals()
                print(f"👋 Portal system stopped")

        return 0 if successful == total else 1

    except Exception as e:
        print(f"❌ Startup failed: {e}")
        startup_mgr.stop_all_portals()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n👋 Startup interrupted")
        sys.exit(130)