"""
Script Discovery Utility
========================
Provides context awareness for scripts and modules.
Helps identify which portal/script is running and its version.
"""

import os
import sys
import inspect
from pathlib import Path
from typing import Optional, Dict, Any

class ScriptContext:
    """Provides context about the running script"""

    def __init__(self):
        self._main_script = None
        self._script_name = None
        self._script_version = None
        self._script_dir = None
        self._discover()

    def _discover(self):
        """Discover information about the running script"""
        # Get main script from sys.argv
        if sys.argv and len(sys.argv) > 0:
            main_file = sys.argv[0]
            if main_file:
                self._main_script = Path(main_file).resolve()
                self._script_name = self._main_script.stem
                self._script_dir = self._main_script.parent

                # Extract version from filename (e.g., flow_portal_v4 -> v4)
                if '_v' in self._script_name:
                    parts = self._script_name.split('_v')
                    if len(parts) > 1 and parts[-1].isdigit():
                        self._script_version = f"v{parts[-1]}"
                    else:
                        self._script_version = "v1"
                else:
                    self._script_version = "v1"

        # Fallback to inspect if sys.argv not available
        if not self._main_script:
            try:
                # Get the calling frame
                frame = inspect.currentframe()
                if frame:
                    # Walk up the stack to find the main module
                    while frame.f_back:
                        frame = frame.f_back

                    # Get the filename from the frame
                    filename = frame.f_code.co_filename
                    if filename and filename != '<stdin>':
                        self._main_script = Path(filename).resolve()
                        self._script_name = self._main_script.stem
                        self._script_dir = self._main_script.parent
            except:
                pass

    @property
    def script_name(self) -> str:
        """Get the name of the main script (without extension)"""
        return self._script_name or "unknown"

    @property
    def script_version(self) -> str:
        """Get the version extracted from script name"""
        return self._script_version or "v1"

    @property
    def script_path(self) -> Optional[Path]:
        """Get the full path to the main script"""
        return self._main_script

    @property
    def script_dir(self) -> Optional[Path]:
        """Get the directory containing the main script"""
        return self._script_dir

    @property
    def is_streamlit(self) -> bool:
        """Check if running in Streamlit context"""
        return 'streamlit' in sys.modules

    @property
    def portal_type(self) -> str:
        """Identify the portal type based on script name and location"""
        if not self._script_name:
            return "unknown"

        # Check for flow portal versions
        if 'flow_portal' in self._script_name:
            return f"flow_portal_{self.script_version}"
        elif 'flow_creator' in self._script_name:
            return f"flow_creator_{self.script_version}"

        # Check directory for context
        if self._script_dir:
            dir_str = str(self._script_dir).lower()
            if 'flow' in dir_str:
                return "flow"
            elif 'chat' in dir_str:
                return "chat"
            elif 'mlflow' in dir_str:
                return "mlflow"

        return "generic"

    def get_tab_version_suffix(self) -> str:
        """Get the appropriate tab file suffix based on script version"""
        if self.script_version and self.script_version != "v1":
            return f"_{self.script_version}"
        return ""

    def get_tab_module_name(self, tab_name: str) -> str:
        """Get the correct tab module name for the current script version"""
        suffix = self.get_tab_version_suffix()
        return f"t_{tab_name}{suffix}"

    def to_dict(self) -> Dict[str, Any]:
        """Get all context information as a dictionary"""
        return {
            "script_name": self.script_name,
            "script_version": self.script_version,
            "script_path": str(self.script_path) if self.script_path else None,
            "script_dir": str(self.script_dir) if self.script_dir else None,
            "portal_type": self.portal_type,
            "is_streamlit": self.is_streamlit,
            "tab_suffix": self.get_tab_version_suffix()
        }


# Global singleton instance
_script_context = None

def get_script_context() -> ScriptContext:
    """Get the singleton ScriptContext instance"""
    global _script_context
    if _script_context is None:
        _script_context = ScriptContext()
    return _script_context

def discover_script_info() -> Dict[str, Any]:
    """Quick function to get script information"""
    return get_script_context().to_dict()

def get_tab_import_name(tab_name: str) -> str:
    """Get the correct import name for a tab module"""
    return get_script_context().get_tab_module_name(tab_name)

def is_running_version(version: str) -> bool:
    """Check if running a specific version"""
    context = get_script_context()
    return context.script_version == version

# Convenience exports
__all__ = [
    'ScriptContext',
    'get_script_context',
    'discover_script_info',
    'get_tab_import_name',
    'is_running_version'
]