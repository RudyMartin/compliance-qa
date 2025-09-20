"""
Common Layer - Foundational Utilities

This layer contains shared utilities and foundational components
used across the qa-shipping system. Part of the 4-layer architecture.

Architecture:
- Portals: Presentation layer
- Packages: Domain logic
- Adapters: Infrastructure
- Common: Foundational utilities (this layer)
"""

from .utilities import PathManager, get_path_manager

__all__ = [
    'PathManager',
    'get_path_manager'
]