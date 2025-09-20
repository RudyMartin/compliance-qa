"""
Common Utilities Package

Foundational utilities shared across the qa-shipping system.
Part of the 4-layer clean architecture as the Common layer.
"""

from .path_manager import PathManager, get_path_manager, get_config_path, get_data_path, get_logs_path

__all__ = [
    'PathManager',
    'get_path_manager',
    'get_config_path',
    'get_data_path',
    'get_logs_path'
]