"""
Use Case Port Interfaces
========================
Inbound ports defining application use cases.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SetupRequest:
    """Request for setup operations"""
    environment: str
    validate_credentials: bool = True
    install_packages: bool = False


@dataclass
class SetupResponse:
    """Response from setup operations"""
    success: bool
    message: str
    details: Dict[str, Any]


class SetupUseCasePort(ABC):
    """Port for setup use cases"""

    @abstractmethod
    async def setup_environment(self, request: SetupRequest) -> SetupResponse:
        """Setup environment"""
        pass

    @abstractmethod
    async def validate_configuration(self) -> SetupResponse:
        """Validate current configuration"""
        pass

    @abstractmethod
    async def install_packages(self, package_names: List[str]) -> SetupResponse:
        """Install specified packages"""
        pass


class PortalManagementPort(ABC):
    """Port for portal management use cases"""

    @abstractmethod
    async def start_portal(self, portal_id: str) -> Dict[str, Any]:
        """Start a portal"""
        pass

    @abstractmethod
    async def stop_portal(self, portal_id: str) -> Dict[str, Any]:
        """Stop a portal"""
        pass

    @abstractmethod
    async def restart_portal(self, portal_id: str) -> Dict[str, Any]:
        """Restart a portal"""
        pass

    @abstractmethod
    async def get_portal_status(self, portal_id: str) -> Dict[str, Any]:
        """Get portal status"""
        pass

    @abstractmethod
    async def list_active_portals(self) -> List[Dict[str, Any]]:
        """List all active portals"""
        pass


class ChatUseCasePort(ABC):
    """Port for chat use cases"""

    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process chat message"""
        pass

    @abstractmethod
    async def create_session(self, user_id: str) -> str:
        """Create chat session"""
        pass

    @abstractmethod
    async def end_session(self, session_id: str) -> bool:
        """End chat session"""
        pass