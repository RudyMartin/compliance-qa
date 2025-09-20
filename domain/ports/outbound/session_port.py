"""
Session Management Port
======================
Outbound port for managing external service connections.

This port abstracts session and connection management from the domain,
allowing the application to work with external services without knowing
the implementation details.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class SessionPort(ABC):
    """
    Port for session and connection management.

    This port defines the interface for managing connections to external services
    like databases, AWS services, and other infrastructure without coupling
    the domain to specific implementations.
    """

    @abstractmethod
    async def get_database_connection(self) -> Any:
        """Get a database connection from the pool"""
        pass

    @abstractmethod
    async def get_s3_client(self) -> Any:
        """Get an AWS S3 client"""
        pass

    @abstractmethod
    async def get_bedrock_client(self) -> Any:
        """Get an AWS Bedrock client"""
        pass

    @abstractmethod
    async def test_connection(self, service: str) -> Dict[str, Any]:
        """Test connection to a specific service"""
        pass

    @abstractmethod
    async def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all managed connections"""
        pass

    @abstractmethod
    async def close_all_connections(self) -> None:
        """Close all managed connections"""
        pass


class DatabaseSessionPort(ABC):
    """
    Specialized port for database session management.

    Separates database concerns for cleaner architecture.
    """

    @abstractmethod
    async def get_connection(self) -> Any:
        """Get a database connection"""
        pass

    @abstractmethod
    async def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a database query"""
        pass

    @abstractmethod
    async def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction"""
        pass

    @abstractmethod
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        pass


class AWSSessionPort(ABC):
    """
    Specialized port for AWS service session management.

    Abstracts AWS SDK details from the application layer.
    """

    @abstractmethod
    async def get_s3_client(self) -> Any:
        """Get S3 client"""
        pass

    @abstractmethod
    async def get_bedrock_client(self) -> Any:
        """Get Bedrock client"""
        pass

    @abstractmethod
    async def get_rds_client(self) -> Any:
        """Get RDS client"""
        pass

    @abstractmethod
    async def validate_credentials(self) -> Dict[str, bool]:
        """Validate AWS credentials"""
        pass

    @abstractmethod
    async def get_caller_identity(self) -> Dict[str, Any]:
        """Get AWS caller identity"""
        pass


class CredentialPort(ABC):
    """
    Port for credential validation and management.

    Abstracts credential handling from the business logic.
    """

    @abstractmethod
    async def validate_database_credentials(self, config: Dict[str, Any]) -> bool:
        """Validate database credentials"""
        pass

    @abstractmethod
    async def validate_aws_credentials(self, config: Dict[str, Any]) -> bool:
        """Validate AWS credentials"""
        pass

    @abstractmethod
    async def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all credential validations"""
        pass

    @abstractmethod
    async def refresh_credentials(self, service: str) -> bool:
        """Refresh credentials for a service"""
        pass