"""
Configuration Domain Model
==========================
Core configuration entity for the system.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class ConfigurationType(Enum):
    """Types of configuration"""
    DATABASE = "database"
    AWS = "aws"
    PORTAL = "portal"
    ARCHITECTURE = "architecture"
    ENVIRONMENT = "environment"


@dataclass
class DatabaseConfig:
    """Database configuration value object"""
    host: str
    port: int
    name: str
    username: str
    connection_pooling_enabled: bool = False
    max_connections: int = 20
    min_connections: int = 2


@dataclass
class AWSConfig:
    """AWS configuration value object"""
    region: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    services: List[str] = None

    def __post_init__(self):
        if self.services is None:
            self.services = []


@dataclass
class ArchitectureConfig:
    """Architecture configuration value object"""
    pattern: str  # e.g., "4layer_clean", "hexagonal"
    layers: List[str]
    strict_dependencies: bool = True


@dataclass
class Configuration:
    """
    Master configuration domain entity.

    Aggregates all configuration aspects of the system.
    """
    database: Optional[DatabaseConfig] = None
    aws: Optional[AWSConfig] = None
    architecture: Optional[ArchitectureConfig] = None
    portals: Dict[str, Dict[str, Any]] = None
    environment: Dict[str, str] = None

    def __post_init__(self):
        if self.portals is None:
            self.portals = {}
        if self.environment is None:
            self.environment = {}

    def is_valid(self) -> bool:
        """Validate configuration completeness"""
        # At minimum, architecture should be defined
        return self.architecture is not None

    def has_database(self) -> bool:
        """Check if database is configured"""
        return self.database is not None

    def has_aws(self) -> bool:
        """Check if AWS is configured"""
        return self.aws is not None and self.aws.region