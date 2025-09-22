"""
Path Utilities for Flow Portal
================================
Provides universal path handling for cross-platform compatibility.
Based on common/utilities/path_manager.py but simplified for portal needs.
"""

import os
from pathlib import Path
from typing import Optional

class PathManager:
    """Simplified PathManager for Flow Portal with universal path handling."""

    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure consistent paths"""
        if cls._instance is None:
            cls._instance = super(PathManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize path manager once"""
        if self._initialized:
            return

        self._root_folder = self._detect_root_folder()
        self._initialized = True

    def _detect_root_folder(self) -> Path:
        """Detect project root folder - works on any platform"""
        current_dir = Path.cwd()

        # Look for key indicators of the project root
        root_indicators = [
            "infrastructure/settings.yaml",
            "domain/workflows",
            "portals/flow",
            "packages/tidyllm",
            "common/utilities"
        ]

        # Search up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            # Check if any indicator exists
            for indicator in root_indicators:
                if (parent / indicator.replace('/', os.sep)).exists():
                    return parent

        # Fallback: assume we're in portals/flow, go up 2 levels
        if "portals" in str(current_dir) and "flow" in str(current_dir):
            return current_dir.parent.parent

        # Last resort: use current directory
        return current_dir

    @property
    def root_folder(self) -> Path:
        """Get the root folder path as Path object"""
        return self._root_folder

    @property
    def domain_path(self) -> Path:
        """Get the domain folder path"""
        return self.root_folder / "domain"

    @property
    def workflows_path(self) -> Path:
        """Get the workflows folder path"""
        return self.domain_path / "workflows"

    @property
    def projects_path(self) -> Path:
        """Get the projects folder path"""
        return self.workflows_path / "projects"

    @property
    def portals_path(self) -> Path:
        """Get the portals folder path"""
        return self.root_folder / "portals"

    @property
    def flow_portal_path(self) -> Path:
        """Get the flow portal folder path"""
        return self.portals_path / "flow"

    def get_project_path(self, project_name: str) -> Path:
        """Get a specific project's path"""
        return self.projects_path / project_name

    def get_project_workflows_file(self, project_name: Optional[str] = None) -> Path:
        """Get the workflows.json file for a project or global"""
        if project_name:
            return self.get_project_path(project_name) / "workflows.json"
        else:
            return self.workflows_path / "portal_workflows.json"

    def ensure_project_structure(self, project_name: str):
        """Ensure project directory structure exists"""
        project_path = self.get_project_path(project_name)

        # Create standard project folders
        folders = ["criteria", "templates", "prompts", "inputs", "uploads", "versions", "outputs"]
        for folder in folders:
            (project_path / folder).mkdir(parents=True, exist_ok=True)

        return project_path

# Singleton instance for easy import
path_manager = PathManager()

def get_path_manager() -> PathManager:
    """Get the singleton PathManager instance"""
    return path_manager