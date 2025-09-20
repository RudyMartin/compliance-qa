"""
Repository Port Interfaces
==========================
Outbound ports for data persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from domain.models.portal import Portal
from domain.models.configuration import Configuration


class PortalRepositoryPort(ABC):
    """Port for portal persistence"""

    @abstractmethod
    async def find_all(self) -> List[Portal]:
        """Find all portals"""
        pass

    @abstractmethod
    async def find_by_id(self, portal_id: str) -> Optional[Portal]:
        """Find portal by ID"""
        pass

    @abstractmethod
    async def find_by_port(self, port: int) -> Optional[Portal]:
        """Find portal by port number"""
        pass

    @abstractmethod
    async def save(self, portal: Portal) -> Portal:
        """Save or update portal"""
        pass

    @abstractmethod
    async def delete(self, portal_id: str) -> bool:
        """Delete portal"""
        pass


class ConfigurationRepositoryPort(ABC):
    """Port for configuration persistence"""

    @abstractmethod
    async def load(self) -> Configuration:
        """Load configuration"""
        pass

    @abstractmethod
    async def save(self, configuration: Configuration) -> bool:
        """Save configuration"""
        pass

    @abstractmethod
    async def reload(self) -> Configuration:
        """Reload configuration from source"""
        pass


class DocumentRepositoryPort(ABC):
    """Port for document operations (from tidyllm)"""

    @abstractmethod
    async def find_by_query(self, query: str, limit: int = 10) -> List:
        """Find documents matching query"""
        pass

    @abstractmethod
    async def save_document(self, document: Any) -> str:
        """Save document"""
        pass

    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Optional[Any]:
        """Get document by ID"""
        pass


class ComplianceRepositoryPort(ABC):
    """Port for compliance operations (from tidyllm)"""

    @abstractmethod
    async def find_rules_by_domain(self, domain: str) -> List:
        """Find compliance rules by domain"""
        pass

    @abstractmethod
    async def find_by_authority_tier(self, tier: int) -> List:
        """Find rules by authority tier"""
        pass

    @abstractmethod
    async def save_rule(self, rule: Any) -> str:
        """Save compliance rule"""
        pass