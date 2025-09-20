"""
Unified Session Adapter
=======================
Secondary adapter implementing session management ports.

This adapter wraps the existing UnifiedSessionManager to implement the session ports,
maintaining the unified session management while following hexagonal principles.
"""

import asyncio
from typing import Dict, Any, Optional

# Import the actual session management implementation
from infrastructure.session.unified import UnifiedSessionManager

# Import the ports we implement
from domain.ports.outbound.session_port import (
    SessionPort, DatabaseSessionPort, AWSSessionPort, CredentialPort
)


class UnifiedSessionAdapter(SessionPort, DatabaseSessionPort, AWSSessionPort, CredentialPort):
    """
    Unified session adapter implementing all session-related ports.

    This adapter provides a hexagonal-compliant interface to the existing
    UnifiedSessionManager, allowing the application layer to work with
    sessions without knowing implementation details.
    """

    def __init__(self, credential_carrier=None):
        """Initialize the adapter with credential carrier (Resource Carrier Pattern)"""
        self._credential_carrier = credential_carrier
        if credential_carrier:
            # Ensure environment variables are set for legacy session manager
            credential_carrier.set_environment_from_credentials()

        self._session_manager = UnifiedSessionManager()
        self._connections = {}

    # SessionPort implementation
    async def get_database_connection(self) -> Any:
        """Get a database connection from the pool"""
        try:
            return await self._session_manager.get_database_connection()
        except Exception as e:
            # Convert infrastructure exceptions to domain-appropriate ones
            raise ConnectionError(f"Failed to get database connection: {e}")

    async def get_s3_client(self) -> Any:
        """Get an AWS S3 client"""
        try:
            return self._session_manager.get_s3_client()
        except Exception as e:
            raise ConnectionError(f"Failed to get S3 client: {e}")

    async def get_bedrock_client(self) -> Any:
        """Get an AWS Bedrock client"""
        try:
            return self._session_manager.get_bedrock_client()
        except Exception as e:
            raise ConnectionError(f"Failed to get Bedrock client: {e}")

    async def test_connection(self, service: str) -> Dict[str, Any]:
        """Test connection to a specific service"""
        try:
            # Delegate to the session manager's test method
            result = self._session_manager.test_connection(service)
            return {
                "service": service,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "details": result.get("details", {}),
                "via": "UnifiedSessionAdapter"
            }
        except Exception as e:
            return {
                "service": service,
                "success": False,
                "message": str(e),
                "via": "UnifiedSessionAdapter"
            }

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all managed connections"""
        try:
            status = self._session_manager.get_status()
            return {
                "database": status.get("database", {}),
                "aws": status.get("aws", {}),
                "overall_health": "healthy" if status.get("initialized", False) else "unhealthy",
                "via": "UnifiedSessionAdapter"
            }
        except Exception as e:
            return {
                "overall_health": "error",
                "error": str(e),
                "via": "UnifiedSessionAdapter"
            }

    async def close_all_connections(self) -> None:
        """Close all managed connections"""
        try:
            await self._session_manager.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close connections: {e}")

    # DatabaseSessionPort implementation
    async def get_connection(self) -> Any:
        """Get a database connection"""
        return await self.get_database_connection()

    async def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute a database query"""
        try:
            conn = await self.get_database_connection()
            if params:
                return await conn.fetch(query, *params)
            else:
                return await conn.fetch(query)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    async def execute_transaction(self, queries: list) -> bool:
        """Execute multiple queries in a transaction"""
        try:
            conn = await self.get_database_connection()
            async with conn.transaction():
                for query_info in queries:
                    if isinstance(query_info, tuple):
                        query, params = query_info
                        await conn.execute(query, *params)
                    else:
                        await conn.execute(query_info)
            return True
        except Exception as e:
            raise RuntimeError(f"Transaction failed: {e}")

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status"""
        try:
            status = await self.get_connection_status()
            return status.get("database", {})
        except Exception as e:
            return {"error": str(e), "status": "unknown"}

    # AWSSessionPort implementation
    async def get_rds_client(self) -> Any:
        """Get RDS client"""
        try:
            return self._session_manager.get_rds_client()
        except Exception as e:
            raise ConnectionError(f"Failed to get RDS client: {e}")

    async def validate_credentials(self) -> Dict[str, bool]:
        """Validate AWS credentials"""
        try:
            # Use session manager's validation
            test_result = await self.test_connection("aws")
            return {
                "valid": test_result.get("success", False),
                "service": "aws",
                "via": "UnifiedSessionAdapter"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def get_caller_identity(self) -> Dict[str, Any]:
        """Get AWS caller identity"""
        try:
            # This would call the session manager's STS functionality
            result = self._session_manager.get_caller_identity()
            return result
        except Exception as e:
            return {"error": str(e), "identity": None}

    # CredentialPort implementation
    async def validate_database_credentials(self, config: Dict[str, Any]) -> bool:
        """Validate database credentials"""
        try:
            test_result = await self.test_connection("database")
            return test_result.get("success", False)
        except Exception:
            return False

    async def validate_aws_credentials(self, config: Dict[str, Any]) -> bool:
        """Validate AWS credentials"""
        try:
            creds = await self.validate_credentials()
            return creds.get("valid", False)
        except Exception:
            return False

    async def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all credential validations"""
        if self._credential_carrier:
            # Use credential carrier for comprehensive status
            return self._credential_carrier.get_credential_status()
        else:
            # Fallback to legacy validation
            status = {}

            # Test database credentials
            db_valid = await self.validate_database_credentials({})
            status["database"] = {
                "valid": db_valid,
                "service": "postgresql",
                "last_checked": "now",
                "source": "legacy"
            }

            # Test AWS credentials
            aws_valid = await self.validate_aws_credentials({})
            status["aws"] = {
                "valid": aws_valid,
                "service": "aws",
                "last_checked": "now",
                "source": "legacy"
            }

            return status

    async def refresh_credentials(self, service: str) -> bool:
        """Refresh credentials for a service"""
        try:
            # This would trigger a refresh in the session manager
            if service == "aws":
                # Refresh AWS credentials
                return await self.validate_aws_credentials({})
            elif service == "database":
                # Refresh database credentials
                return await self.validate_database_credentials({})
            else:
                return False
        except Exception:
            return False

    # Additional helper methods
    def get_session_manager(self) -> UnifiedSessionManager:
        """
        Get the underlying session manager.

        WARNING: This breaks encapsulation and should only be used
        for migration purposes. Eventually, all functionality should
        be available through the port interfaces.
        """
        return self._session_manager