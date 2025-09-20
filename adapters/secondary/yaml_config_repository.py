"""
YAML Configuration Repository Adapter
=====================================
Secondary adapter for configuration persistence using YAML.
"""

import yaml
from typing import Optional
from domain.ports.outbound.repository_port import ConfigurationRepositoryPort
from domain.models.configuration import (
    Configuration, DatabaseConfig, AWSConfig, ArchitectureConfig
)


class YamlConfigRepository(ConfigurationRepositoryPort):
    """
    YAML-based configuration repository implementation.

    This is a secondary adapter that implements the ConfigurationRepositoryPort.
    """

    def __init__(self, settings_loader):
        self.settings_loader = settings_loader
        self._cached_config = None

    async def load(self) -> Configuration:
        """Load configuration from YAML file"""
        if self._cached_config:
            return self._cached_config

        try:
            # Load raw YAML data
            raw_config = self.settings_loader.load_settings()

            # Map to domain model
            config = Configuration()

            # Map database configuration
            if "database" in raw_config:
                db = raw_config["database"]
                config.database = DatabaseConfig(
                    host=db.get("host", "localhost"),
                    port=db.get("port", 5432),
                    name=db.get("name", ""),
                    username=db.get("username", ""),
                    connection_pooling_enabled=db.get("connection_pooling", {}).get("enabled", False),
                    max_connections=db.get("connection_pooling", {}).get("max_connections", 20),
                    min_connections=db.get("connection_pooling", {}).get("min_connections", 2)
                )

            # Map AWS configuration
            if "aws" in raw_config:
                aws = raw_config["aws"]
                config.aws = AWSConfig(
                    region=aws.get("region", "us-east-1"),
                    services=aws.get("services", [])
                )

            # Map architecture configuration
            if "system" in raw_config and "architecture" in raw_config["system"]:
                arch = raw_config["system"]["architecture"]
                config.architecture = ArchitectureConfig(
                    pattern=arch.get("pattern", "4layer_clean"),
                    layers=arch.get("layers", ["portals", "packages", "adapters", "infrastructure"]),
                    strict_dependencies=arch.get("strict_dependencies", True)
                )

            # Map portals
            if "portals" in raw_config:
                config.portals = raw_config["portals"]

            # Map environment
            if "environment" in raw_config:
                config.environment = raw_config["environment"]

            self._cached_config = config
            return config

        except Exception as e:
            # Return minimal valid configuration on error
            config = Configuration()
            config.architecture = ArchitectureConfig(
                pattern="4layer_clean",
                layers=["portals", "packages", "adapters", "infrastructure"]
            )
            return config

    async def save(self, configuration: Configuration) -> bool:
        """Save configuration to YAML file"""
        try:
            # Convert domain model to dict
            data = {
                "system": {
                    "architecture": {
                        "pattern": configuration.architecture.pattern,
                        "layers": configuration.architecture.layers,
                        "strict_dependencies": configuration.architecture.strict_dependencies
                    } if configuration.architecture else {}
                }
            }

            if configuration.database:
                data["database"] = {
                    "host": configuration.database.host,
                    "port": configuration.database.port,
                    "name": configuration.database.name,
                    "username": configuration.database.username,
                    "connection_pooling": {
                        "enabled": configuration.database.connection_pooling_enabled,
                        "max_connections": configuration.database.max_connections,
                        "min_connections": configuration.database.min_connections
                    }
                }

            if configuration.aws:
                data["aws"] = {
                    "region": configuration.aws.region,
                    "services": configuration.aws.services
                }

            if configuration.portals:
                data["portals"] = configuration.portals

            if configuration.environment:
                data["environment"] = configuration.environment

            # Save to file
            with open(self.settings_loader.settings_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)

            # Clear cache
            self._cached_config = None
            return True

        except Exception as e:
            return False

    async def reload(self) -> Configuration:
        """Reload configuration from source"""
        self._cached_config = None
        return await self.load()