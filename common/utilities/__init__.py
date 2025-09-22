"""
Common Utilities Package

Foundational utilities shared across the qa-shipping system.
Part of the 4-layer clean architecture as the Common layer.

Available modules:
- path_manager: Path management utilities
- clean_json_io: JSON loading and saving with automatic cleaning
- data_normalizer: Data normalization utilities for portals
- step_ordering: Step and workflow ordering utilities
- json_scrubber: JSON content cleaning utilities
"""

from .path_manager import PathManager, get_path_manager, get_config_path, get_data_path, get_logs_path

# Import key utilities from our new modules
from .clean_json_io import load_json, save_json, CleanJSONIO
from .data_normalizer import DataNormalizer, normalize_status, get_system_counts
from .step_ordering import (
    reorder_steps_by_position,
    check_for_order_changes,
    renumber_steps,
    validate_step_order
)
from .json_scrubber import JSONScrubber, safe_load_json_with_scrubbing

__all__ = [
    # Path management
    'PathManager',
    'get_path_manager',
    'get_config_path',
    'get_data_path',
    'get_logs_path',

    # JSON I/O
    'load_json',
    'save_json',
    'CleanJSONIO',

    # Data normalization
    'DataNormalizer',
    'normalize_status',
    'get_system_counts',

    # Step ordering
    'reorder_steps_by_position',
    'check_for_order_changes',
    'renumber_steps',
    'validate_step_order',

    # JSON scrubbing
    'JSONScrubber',
    'safe_load_json_with_scrubbing'
]