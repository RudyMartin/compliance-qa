"""
Portal Domain Model
===================
Core business entity representing a portal in the system.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class PortalStatus(Enum):
    """Portal operational status"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"


class PortalType(Enum):
    """Types of portals in the system"""
    SETUP = "setup"
    CHAT = "chat"
    FLOW = "flow"
    RAG = "rag"
    MONITOR = "monitor"
    ADMIN = "admin"


@dataclass
class Portal:
    """
    Portal domain entity.

    This is a pure domain model with no framework dependencies.
    """
    id: str
    name: str
    port: int
    type: PortalType
    status: PortalStatus
    description: str
    module_path: str
    config: Optional[Dict[str, Any]] = None

    def is_active(self) -> bool:
        """Check if portal is active"""
        return self.status == PortalStatus.RUNNING

    def can_start(self) -> bool:
        """Check if portal can be started"""
        return self.status in [PortalStatus.STOPPED, PortalStatus.ERROR]

    def validate(self) -> bool:
        """Validate portal configuration"""
        if not self.name or not self.module_path:
            return False
        if self.port < 1024 or self.port > 65535:
            return False
        return True