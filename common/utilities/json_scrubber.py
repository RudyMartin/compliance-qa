"""
JSON Scrubber Utility
====================

Simple JSON cleaning utility for the common utilities package.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Tuple

logger = logging.getLogger(__name__)


class JSONScrubber:
    """Simple JSON scrubber for cleaning JSON content."""

    def __init__(self):
        pass

    def scrub_text(self, text: str, fix_json_structure: bool = True) -> Tuple[str, List[str]]:
        """
        Clean JSON text content.

        Args:
            text: JSON text to clean
            fix_json_structure: Whether to fix JSON structure issues

        Returns:
            Tuple of (cleaned_text, list_of_fixes_applied)
        """
        fixes_applied = []

        try:
            # Test if it's already valid JSON
            json.loads(text)
            return text, fixes_applied
        except json.JSONDecodeError:
            # Apply basic fixes
            cleaned_text = text

            # Fix common JSON issues
            if fix_json_structure:
                # Remove trailing commas
                import re
                if re.search(r',\s*}', cleaned_text):
                    cleaned_text = re.sub(r',(\s*})', r'\1', cleaned_text)
                    fixes_applied.append("Removed trailing commas before }")

                if re.search(r',\s*]', cleaned_text):
                    cleaned_text = re.sub(r',(\s*])', r'\1', cleaned_text)
                    fixes_applied.append("Removed trailing commas before ]")

            return cleaned_text, fixes_applied


def safe_load_json_with_scrubbing(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file with automatic scrubbing if needed.

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary with keys: success, data, scrubbing_required, error, fixes_applied
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try loading as-is first
        try:
            data = json.loads(content)
            return {
                'success': True,
                'data': data,
                'scrubbing_required': False
            }
        except json.JSONDecodeError:
            # Try scrubbing
            scrubber = JSONScrubber()
            cleaned_content, fixes = scrubber.scrub_text(content, fix_json_structure=True)

            try:
                data = json.loads(cleaned_content)
                return {
                    'success': True,
                    'data': data,
                    'scrubbing_required': True,
                    'fixes_applied': fixes
                }
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f"JSON parsing failed even after scrubbing: {e}",
                    'scrubbing_required': True,
                    'fixes_applied': fixes
                }

    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to read file: {e}"
        }