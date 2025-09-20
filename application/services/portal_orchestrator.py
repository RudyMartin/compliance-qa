"""
Portal Orchestrator Service
===========================
Application service for orchestrating portal operations.
"""

from typing import List, Dict, Any, Optional
import asyncio
from domain.ports.inbound.use_case_port import PortalManagementPort
from domain.ports.outbound.repository_port import PortalRepositoryPort
from domain.models.portal import Portal, PortalStatus, PortalType


class PortalOrchestrator(PortalManagementPort):
    """
    Orchestrates portal operations.

    This service coordinates between multiple portals,
    managing their lifecycle and interactions.
    """

    def __init__(self, portal_repo: PortalRepositoryPort, portal_runner):
        self.portal_repo = portal_repo
        self.portal_runner = portal_runner
        self.active_portals = {}

    async def start_portal(self, portal_id: str) -> Dict[str, Any]:
        """Start a portal"""
        try:
            # Get portal from repository
            portal = await self.portal_repo.find_by_id(portal_id)

            if not portal:
                return {
                    "success": False,
                    "message": f"Portal {portal_id} not found"
                }

            # Business rule: Cannot start if already running
            if portal.is_active():
                return {
                    "success": False,
                    "message": f"Portal {portal.name} is already running"
                }

            # Business rule: Validate before starting
            if not portal.validate():
                return {
                    "success": False,
                    "message": f"Portal {portal.name} has invalid configuration"
                }

            # Start the portal using the runner
            result = await self.portal_runner.start(portal)

            if result.get("success"):
                # Update status in repository
                portal.status = PortalStatus.RUNNING
                await self.portal_repo.save(portal)

                # Track in memory
                self.active_portals[portal_id] = portal

                return {
                    "success": True,
                    "message": f"Portal {portal.name} started on port {portal.port}",
                    "portal": {
                        "id": portal.id,
                        "name": portal.name,
                        "port": portal.port,
                        "status": portal.status.value
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to start portal: {result.get('error', 'Unknown error')}"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting portal: {str(e)}"
            }

    async def stop_portal(self, portal_id: str) -> Dict[str, Any]:
        """Stop a portal"""
        try:
            portal = await self.portal_repo.find_by_id(portal_id)

            if not portal:
                return {
                    "success": False,
                    "message": f"Portal {portal_id} not found"
                }

            # Business rule: Cannot stop if not running
            if not portal.is_active():
                return {
                    "success": False,
                    "message": f"Portal {portal.name} is not running"
                }

            # Stop the portal
            result = await self.portal_runner.stop(portal)

            if result.get("success"):
                # Update status
                portal.status = PortalStatus.STOPPED
                await self.portal_repo.save(portal)

                # Remove from active tracking
                self.active_portals.pop(portal_id, None)

                return {
                    "success": True,
                    "message": f"Portal {portal.name} stopped"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to stop portal: {result.get('error', 'Unknown error')}"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping portal: {str(e)}"
            }

    async def restart_portal(self, portal_id: str) -> Dict[str, Any]:
        """Restart a portal"""
        # Business logic: Stop then start
        stop_result = await self.stop_portal(portal_id)

        if not stop_result.get("success"):
            return stop_result

        # Wait briefly before restarting
        await asyncio.sleep(1)

        return await self.start_portal(portal_id)

    async def get_portal_status(self, portal_id: str) -> Dict[str, Any]:
        """Get portal status"""
        try:
            portal = await self.portal_repo.find_by_id(portal_id)

            if not portal:
                return {
                    "success": False,
                    "message": f"Portal {portal_id} not found"
                }

            # Get runtime status from runner if active
            runtime_status = None
            if portal.is_active() and portal_id in self.active_portals:
                runtime_status = await self.portal_runner.get_status(portal)

            return {
                "success": True,
                "portal": {
                    "id": portal.id,
                    "name": portal.name,
                    "port": portal.port,
                    "type": portal.type.value,
                    "status": portal.status.value,
                    "runtime": runtime_status
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting status: {str(e)}"
            }

    async def list_active_portals(self) -> List[Dict[str, Any]]:
        """List all active portals"""
        try:
            all_portals = await self.portal_repo.find_all()

            active_portals = []
            for portal in all_portals:
                if portal.is_active():
                    active_portals.append({
                        "id": portal.id,
                        "name": portal.name,
                        "port": portal.port,
                        "type": portal.type.value,
                        "status": portal.status.value,
                        "description": portal.description
                    })

            return active_portals

        except Exception as e:
            return []