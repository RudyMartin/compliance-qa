"""
In-Memory Portal Repository Adapter
===================================
Secondary adapter for portal persistence in memory.
"""

from typing import List, Optional, Dict
from domain.ports.outbound.repository_port import PortalRepositoryPort
from domain.models.portal import Portal, PortalStatus, PortalType


class InMemoryPortalRepository(PortalRepositoryPort):
    """
    In-memory portal repository implementation.

    This is a secondary adapter that implements the PortalRepositoryPort.
    Useful for testing and simple portal management.
    """

    def __init__(self):
        self.portals: Dict[str, Portal] = {}
        self._initialize_default_portals()

    def _initialize_default_portals(self):
        """Initialize with default portal configurations"""
        default_portals = [
            Portal(
                id="setup",
                name="Setup Portal",
                port=8512,
                type=PortalType.SETUP,
                status=PortalStatus.STOPPED,
                description="System configuration and setup",
                module_path="portals.setup.setup_portal",
                config={"theme": "light"}
            ),
            Portal(
                id="chat",
                name="Chat Portal",
                port=8502,
                type=PortalType.CHAT,
                status=PortalStatus.STOPPED,
                description="Interactive chat interface",
                module_path="portals.chat.chat_portal",
                config={"model": "claude-3"}
            ),
            Portal(
                id="flow",
                name="Flow Creator",
                port=8550,
                type=PortalType.FLOW,
                status=PortalStatus.STOPPED,
                description="Workflow creation and management",
                module_path="portals.flow.flow_creator",
                config={"version": "v3"}
            ),
            Portal(
                id="rag",
                name="RAG Creator",
                port=8525,
                type=PortalType.RAG,
                status=PortalStatus.STOPPED,
                description="RAG pipeline configuration",
                module_path="portals.rag.rag_creator",
                config={"version": "v3"}
            ),
            Portal(
                id="monitor",
                name="System Monitor",
                port=8506,
                type=PortalType.MONITOR,
                status=PortalStatus.STOPPED,
                description="System monitoring dashboard",
                module_path="portals.monitor.monitor_portal",
                config={"refresh_rate": 5}
            ),
            Portal(
                id="admin1",
                name="Admin Portal 1",
                port=8505,
                type=PortalType.ADMIN,
                status=PortalStatus.STOPPED,
                description="Administration interface",
                module_path="portals.admin.admin_portal",
                config={"role": "primary"}
            ),
            Portal(
                id="admin2",
                name="Admin Portal 2",
                port=8511,
                type=PortalType.ADMIN,
                status=PortalStatus.STOPPED,
                description="Secondary administration interface",
                module_path="portals.admin.admin_portal",
                config={"role": "secondary"}
            )
        ]

        for portal in default_portals:
            self.portals[portal.id] = portal

    async def find_all(self) -> List[Portal]:
        """Find all portals"""
        return list(self.portals.values())

    async def find_by_id(self, portal_id: str) -> Optional[Portal]:
        """Find portal by ID"""
        return self.portals.get(portal_id)

    async def find_by_port(self, port: int) -> Optional[Portal]:
        """Find portal by port number"""
        for portal in self.portals.values():
            if portal.port == port:
                return portal
        return None

    async def save(self, portal: Portal) -> Portal:
        """Save or update portal"""
        if not portal.validate():
            raise ValueError(f"Invalid portal configuration: {portal.id}")

        self.portals[portal.id] = portal
        return portal

    async def delete(self, portal_id: str) -> bool:
        """Delete portal"""
        if portal_id in self.portals:
            del self.portals[portal_id]
            return True
        return False