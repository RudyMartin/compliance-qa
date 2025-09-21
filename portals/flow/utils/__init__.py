"""
Portal Utilities Package
========================

Common utilities and workaround patterns extracted from the TidyLLM Flow Portal.
These utilities handle common issues like:

- Streamlit type consistency errors
- Dict vs List data structure mismatches
- Defensive programming patterns
- Graceful fallback mechanisms
- File access with fallbacks
"""

from .streamlit_helpers import (
    ensure_numeric_type_consistency,
    safe_get_rag_systems,
    format_status_icon,
    safe_dict_iteration
)

from .data_handling import (
    safe_workflow_access,
    safe_status_counts,
    safe_get_available_items,
    safe_check_availability,
    safe_iterate_with_status,
    safe_any_check,
    normalize_workflow_types,
    safe_context_check
)

from .fallback_patterns import (
    safe_file_access,
    safe_json_parse,
    safe_criteria_access,
    get_default_use_cases,
    safe_template_field_access,
    safe_workflow_selection,
    graceful_error_message,
    safe_directory_fallback,
    create_safe_default,
    retry_with_fallback
)

__all__ = [
    # Streamlit helpers
    'ensure_numeric_type_consistency',
    'safe_get_rag_systems',
    'format_status_icon',
    'safe_dict_iteration',

    # Data handling
    'safe_workflow_access',
    'safe_status_counts',
    'safe_get_available_items',
    'safe_check_availability',
    'safe_iterate_with_status',
    'safe_any_check',
    'normalize_workflow_types',
    'safe_context_check',

    # Fallback patterns
    'safe_file_access',
    'safe_json_parse',
    'safe_criteria_access',
    'get_default_use_cases',
    'safe_template_field_access',
    'safe_workflow_selection',
    'graceful_error_message',
    'safe_directory_fallback',
    'create_safe_default',
    'retry_with_fallback'
]