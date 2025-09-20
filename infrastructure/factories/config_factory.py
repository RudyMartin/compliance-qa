"""
Configuration Factory
====================
Factory for creating configuration objects from various sources.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from domain.models.configuration import (
    Configuration, DatabaseConfig, AWSConfig, ArchitectureConfig
)


class ConfigurationFactory:
    """
    Factory for creating Configuration domain objects.

    Supports creation from various sources:
    - YAML files
    - JSON files
    - Environment variables
    - Dictionary objects
    """

    @staticmethod
    def create_from_yaml(yaml_path: Path) -> Configuration:
        """Create configuration from YAML file"""
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            return ConfigurationFactory._create_from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to create configuration from YAML: {e}")

    @staticmethod
    def create_from_json(json_path: Path) -> Configuration:
        """Create configuration from JSON file"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return ConfigurationFactory._create_from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to create configuration from JSON: {e}")

    @staticmethod
    def create_from_env() -> Configuration:
        """Create configuration from environment variables"""
        config = Configuration()

        # Database from environment
        if os.getenv("DB_HOST"):
            config.database = DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                name=os.getenv("DB_NAME", ""),
                username=os.getenv("DB_USERNAME", ""),
                connection_pooling_enabled=os.getenv("DB_POOLING_ENABLED", "false").lower() == "true",
                max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "20")),
                min_connections=int(os.getenv("DB_MIN_CONNECTIONS", "2"))
            )

        # AWS from environment
        if os.getenv("AWS_REGION"):
            config.aws = AWSConfig(
                region=os.getenv("AWS_REGION", "us-east-1"),
                access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                services=os.getenv("AWS_SERVICES", "s3,bedrock,rds").split(",")
            )

        # Architecture from environment
        config.architecture = ArchitectureConfig(
            pattern=os.getenv("ARCHITECTURE_PATTERN", "4layer_clean"),
            layers=os.getenv("ARCHITECTURE_LAYERS", "portals,packages,adapters,infrastructure").split(","),
            strict_dependencies=os.getenv("ARCHITECTURE_STRICT", "true").lower() == "true"
        )

        # Collect all environment variables
        config.environment = dict(os.environ)

        return config

    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> Configuration:
        """Create configuration from dictionary"""
        return ConfigurationFactory._create_from_dict(data)

    @staticmethod
    def create_default() -> Configuration:
        """Create default configuration"""
        config = Configuration()

        # Default architecture
        config.architecture = ArchitectureConfig(
            pattern="4layer_clean",
            layers=["portals", "packages", "adapters", "infrastructure"],
            strict_dependencies=True
        )

        # Default database (local development)
        config.database = DatabaseConfig(
            host="localhost",
            port=5432,
            name="qa_shipping",
            username="developer",
            connection_pooling_enabled=True,
            max_connections=20,
            min_connections=2
        )

        # Default AWS
        config.aws = AWSConfig(
            region="us-east-1",
            services=["s3", "bedrock", "rds"]
        )

        return config

    @staticmethod
    def merge_configurations(*configs: Configuration) -> Configuration:
        """
        Merge multiple configurations with priority.

        Later configurations override earlier ones.
        """
        result = Configuration()

        for config in configs:
            if config.database:
                result.database = config.database
            if config.aws:
                result.aws = config.aws
            if config.architecture:
                result.architecture = config.architecture
            if config.portals:
                result.portals.update(config.portals)
            if config.environment:
                result.environment.update(config.environment)

        return result

    @staticmethod
    def _create_from_dict(data: Dict[str, Any]) -> Configuration:
        """Internal method to create configuration from dictionary"""
        config = Configuration()

        # Map database
        if "database" in data:
            db = data["database"]
            config.database = DatabaseConfig(
                host=db.get("host", "localhost"),
                port=db.get("port", 5432),
                name=db.get("name", ""),
                username=db.get("username", ""),
                connection_pooling_enabled=db.get("connection_pooling", {}).get("enabled", False),
                max_connections=db.get("connection_pooling", {}).get("max_connections", 20),
                min_connections=db.get("connection_pooling", {}).get("min_connections", 2)
            )

        # Map AWS
        if "aws" in data:
            aws = data["aws"]
            config.aws = AWSConfig(
                region=aws.get("region", "us-east-1"),
                access_key_id=aws.get("access_key_id"),
                secret_access_key=aws.get("secret_access_key"),
                services=aws.get("services", [])
            )

        # Map architecture
        if "system" in data and "architecture" in data["system"]:
            arch = data["system"]["architecture"]
            config.architecture = ArchitectureConfig(
                pattern=arch.get("pattern", "4layer_clean"),
                layers=arch.get("layers", ["portals", "packages", "adapters", "infrastructure"]),
                strict_dependencies=arch.get("strict_dependencies", True)
            )
        elif "architecture" in data:
            arch = data["architecture"]
            config.architecture = ArchitectureConfig(
                pattern=arch.get("pattern", "4layer_clean"),
                layers=arch.get("layers", ["portals", "packages", "adapters", "infrastructure"]),
                strict_dependencies=arch.get("strict_dependencies", True)
            )

        # Map portals
        if "portals" in data:
            config.portals = data["portals"]

        # Map environment
        if "environment" in data:
            config.environment = data["environment"]

        return config