"""
Path Manager - Common Foundational Utility

Moved from tidyllm/infrastructure/path_utils.py to common/utilities/
Now properly positioned as foundational utility in 4-layer architecture.

Handles cross-platform path resolution and root folder configuration.
Supports the new compliance-qa 4-layer architecture.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PathManager:
    """Manages path resolution for compliance-qa system with 4-layer architecture support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PathManager with configuration."""
        self.config = config or {}
        self._root_folder = None
        self._config_folder = None
        self._data_folder = None
        self._logs_folder = None

        # Initialize paths
        self._initialize_paths()

    def _initialize_paths(self):
        """Initialize all path configurations for 4-layer architecture."""
        # Get system configuration
        system_config = self.config.get("system", {})

        # Set root path
        self._root_folder = system_config.get("root_path")
        if not self._root_folder:
            # Fallback: try to detect from current working directory
            self._root_folder = self._detect_root_folder()

        # Set relative folders for 4-layer architecture
        self._config_folder = system_config.get("config_folder", "infrastructure")
        self._data_folder = system_config.get("data_folder", "data")
        self._logs_folder = system_config.get("logs_folder", "logs")

        logger.info(f"PathManager initialized with root: {self._root_folder}")

    def _detect_root_folder(self) -> str:
        """Detect root folder using settings.yaml configuration."""
        # Try to load root path from settings.yaml
        try:
            import yaml
            current_dir = Path.cwd()

            # Look for settings.yaml in current or parent directories
            for parent in [current_dir] + list(current_dir.parents):
                settings_file = parent / "infrastructure" / "settings.yaml"
                if settings_file.exists():
                    with open(settings_file, 'r') as f:
                        settings = yaml.safe_load(f)
                    if settings and 'paths' in settings and 'root_path' in settings['paths']:
                        return settings['paths']['root_path']
                    break
        except Exception:
            pass

        # Fallback: use current working directory
        return os.getcwd()

    @property
    def root_folder(self) -> str:
        """Get the root folder path."""
        return self._root_folder or "."

    @property
    def config_folder(self) -> str:
        """Get the infrastructure folder path."""
        return os.path.join(self.root_folder, self._config_folder)

    @property
    def data_folder(self) -> str:
        """Get the data folder path."""
        return os.path.join(self.root_folder, self._data_folder)

    @property
    def logs_folder(self) -> str:
        """Get the logs folder path."""
        return os.path.join(self.root_folder, self._logs_folder)

    # 4-Layer Architecture Specific Methods
    @property
    def portals_folder(self) -> str:
        """Get the portals folder path (presentation layer)."""
        return os.path.join(self.root_folder, "portals")

    @property
    def packages_folder(self) -> str:
        """Get the packages folder path (domain logic)."""
        return os.path.join(self.root_folder, "packages")

    @property
    def adapters_folder(self) -> str:
        """Get the adapters folder path (infrastructure)."""
        return os.path.join(self.root_folder, "adapters")

    @property
    def common_folder(self) -> str:
        """Get the common folder path (foundational utilities)."""
        return os.path.join(self.root_folder, "common")

    def get_config_path(self, filename: str) -> str:
        """Get full path to a config file."""
        return os.path.join(self.config_folder, filename)

    def get_data_path(self, filename: str) -> str:
        """Get full path to a data file."""
        return os.path.join(self.data_folder, filename)

    def get_logs_path(self, filename: str) -> str:
        """Get full path to a log file."""
        return os.path.join(self.logs_folder, filename)

    def get_portal_path(self, portal_name: str) -> str:
        """Get path to specific portal."""
        return os.path.join(self.portals_folder, portal_name)

    def get_package_path(self, package_name: str) -> str:
        """Get path to specific package."""
        return os.path.join(self.packages_folder, package_name)

    def get_adapter_path(self, adapter_type: str) -> str:
        """Get path to specific adapter type."""
        return os.path.join(self.adapters_folder, adapter_type)

    # Core Package Convenience Methods
    @property
    def tidyllm_package_path(self) -> str:
        """Get path to tidyllm package (core business logic)."""
        return self.get_package_path("tidyllm")

    @property
    def tlm_package_path(self) -> str:
        """Get path to tlm package (TLM core functionality)."""
        return self.get_package_path("tlm")

    @property
    def tidyllm_sentence_package_path(self) -> str:
        """Get path to tidyllm-sentence package (sentence processing logic)."""
        return self.get_package_path("tidyllm-sentence")

    def ensure_folders_exist(self):
        """Ensure all required folders exist for 4-layer architecture."""
        folders = [
            self.config_folder,
            self.data_folder,
            self.logs_folder,
            self.portals_folder,
            self.packages_folder,
            self.adapters_folder,
            self.common_folder
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            logger.debug(f"Ensured folder exists: {folder}")

    def get_relative_path(self, full_path: str) -> str:
        """Get relative path from root folder."""
        try:
            return os.path.relpath(full_path, self.root_folder)
        except ValueError:
            return full_path

    def is_absolute_path(self, path: str) -> bool:
        """Check if path is absolute."""
        return os.path.isabs(path)

    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform."""
        return os.path.normpath(path)

    def get_architecture_summary(self) -> Dict[str, str]:
        """Get summary of 4-layer architecture paths."""
        return {
            "root": self.root_folder,
            "portals": self.portals_folder,
            "packages": self.packages_folder,
            "adapters": self.adapters_folder,
            "common": self.common_folder,
            "infrastructure": self.config_folder,
            "data": self.data_folder,
            "logs": self.logs_folder
        }

# Global path manager instance
_path_manager: Optional[PathManager] = None

def get_path_manager(config: Optional[Dict[str, Any]] = None) -> PathManager:
    """Get global PathManager instance."""
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager(config)
    return _path_manager

def set_path_manager(path_manager: PathManager):
    """Set global PathManager instance."""
    global _path_manager
    _path_manager = path_manager

def get_config_path(filename: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get config file path using global PathManager."""
    return get_path_manager(config).get_config_path(filename)

def get_data_path(filename: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get data file path using global PathManager."""
    return get_path_manager(config).get_data_path(filename)

def get_logs_path(filename: str, config: Optional[Dict[str, Any]] = None) -> str:
    """Get log file path using global PathManager."""
    return get_path_manager(config).get_logs_path(filename)

def get_architecture_paths(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """Get all 4-layer architecture paths."""
    return get_path_manager(config).get_architecture_summary()

if __name__ == "__main__":
    # Demo the path manager
    print("Compliance QA Path Manager Demo")
    print("=" * 40)

    path_mgr = PathManager()
    summary = path_mgr.get_architecture_summary()

    for layer, path in summary.items():
        print(f"{layer.upper()}: {path}")

    print("\nPath manager configured for 4-layer architecture!")