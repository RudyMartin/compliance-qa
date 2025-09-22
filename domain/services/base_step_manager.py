"""
Base Steps Manager Service
==========================

Abstract base class for all step managers (Action, Prompt, AskAI).
Provides common functionality for workflow step management.
"""

import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseStepsManager(ABC):
    """Abstract base class for all step managers."""

    def __init__(self, project_id: str, step_type: str, project_path: Path = None):
        """
        Initialize the base step manager.

        Args:
            project_id: The workflow/project ID
            step_type: Type of steps being managed (action_steps, prompts, ai_interactions)
            project_path: Optional custom project path
        """
        self.project_id = project_id
        self.step_type = step_type

        # Determine project path
        if project_path:
            self.project_path = Path(project_path)
        else:
            # Try to use path manager if available
            try:
                from core.utilities.path_manager import get_path_manager
                root = get_path_manager().root_folder
            except ImportError:
                # Fallback to relative path
                root = Path(__file__).parent.parent.parent
            self.project_path = Path(root) / "domain" / "workflows" / "projects" / project_id

        # Create step-specific directory
        self.steps_path = self.project_path / step_type
        self.steps_path.mkdir(parents=True, exist_ok=True)

        # Path for the main configuration
        self.config_path = self.steps_path / f"{step_type}_config.json"

    @abstractmethod
    def get_all_steps(self) -> List[Dict[str, Any]]:
        """Get all steps for this project. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def save_step(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a step definition. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def load_step(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific step. Must be implemented by subclasses."""
        pass

    def delete_step(self, step_name: str) -> Dict[str, Any]:
        """Delete a step. Common implementation."""
        try:
            file_path = self.steps_path / f"{step_name}.json"

            if file_path.exists():
                file_path.unlink()
                self._update_config(step_name, "deleted")

                return {
                    'success': True,
                    'message': f"{self.step_type} '{step_name}' deleted"
                }
            else:
                return {
                    'success': False,
                    'error': f"{self.step_type} '{step_name}' not found"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def export_steps(self, export_path: Path = None) -> Dict[str, Any]:
        """Export all steps to a bundle. Common implementation."""
        try:
            if not export_path:
                export_path = self.project_path / "exports"
                export_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bundle_name = f"{self.step_type}_{self.project_id}_{timestamp}.json"
            bundle_path = export_path / bundle_name

            # Collect all steps
            steps = self.get_all_steps()

            # Create export bundle
            export_data = {
                'project_id': self.project_id,
                'step_type': self.step_type,
                'exported_at': datetime.now().isoformat(),
                'steps_count': len(steps),
                'steps': steps
            }

            # Save bundle
            with open(bundle_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return {
                'success': True,
                'export_path': str(bundle_path),
                'steps_count': len(steps),
                'message': f"Exported {len(steps)} {self.step_type} to {bundle_name}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def import_steps_bundle(self, bundle_path: Path, overwrite: bool = False) -> Dict[str, Any]:
        """Import steps from an exported bundle. Common implementation."""
        try:
            if not bundle_path.exists():
                return {
                    'success': False,
                    'error': f"Bundle file not found: {bundle_path}"
                }

            # Load bundle
            with open(bundle_path, 'r', encoding='utf-8') as f:
                bundle_data = json.load(f)

            # Verify bundle type
            if bundle_data.get('step_type') != self.step_type:
                return {
                    'success': False,
                    'error': f"Bundle is for {bundle_data.get('step_type')}, not {self.step_type}"
                }

            imported_count = 0
            skipped_count = 0

            for step_data in bundle_data.get('steps', []):
                step_name = self._extract_step_name(step_data)
                file_path = self.steps_path / f"{step_name}.json"

                if file_path.exists() and not overwrite:
                    skipped_count += 1
                    continue

                # Import the step
                result = self.save_step(step_name, step_data)
                if result['success']:
                    imported_count += 1

            return {
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'message': f"Imported {imported_count} {self.step_type}, skipped {skipped_count}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_step_summary(self) -> Dict[str, Any]:
        """Get a summary of all steps. Common implementation with extensibility."""
        steps = self.get_all_steps()

        summary = {
            'project_id': self.project_id,
            'step_type': self.step_type,
            'total_steps': len(steps),
            'last_modified': None
        }

        # Track last modified
        for step in steps:
            if step.get('last_modified'):
                if not summary['last_modified'] or step['last_modified'] > summary['last_modified']:
                    summary['last_modified'] = step['last_modified']

        # Allow subclasses to add their own summary data
        summary.update(self._get_custom_summary(steps))

        return summary

    def _extract_step_name(self, step_data: Dict[str, Any]) -> str:
        """Extract step name from step data. Can be overridden by subclasses."""
        return step_data.get('step_name', step_data.get('name', 'unnamed'))

    def _get_custom_summary(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get custom summary data. Override in subclasses for specific metrics."""
        return {}

    def _update_config(self, step_name: str, action: str):
        """Update the configuration file. Common implementation."""
        try:
            # Load existing config or create new
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'project_id': self.project_id,
                    'step_type': self.step_type,
                    'created_at': datetime.now().isoformat(),
                    'steps': {},
                    'history': []
                }

            # Update steps list
            if action == "saved" or action == "updated":
                config['steps'][step_name] = {
                    'last_modified': datetime.now().isoformat(),
                    'status': 'active'
                }
            elif action == "deleted":
                if step_name in config['steps']:
                    del config['steps'][step_name]

            # Add to history
            config['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'step_name': step_name
            })

            # Keep only last 100 history entries
            config['history'] = config['history'][-100:]

            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.error(f"Error updating config: {e}")

    def validate_project_structure(self) -> bool:
        """Ensure all required directories exist."""
        required_dirs = ['criteria', 'templates', 'inputs', 'outputs', 'resources']

        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)

        return True

    def get_project_info(self) -> Dict[str, Any]:
        """Get information about the project."""
        return {
            'project_id': self.project_id,
            'project_path': str(self.project_path),
            'step_type': self.step_type,
            'steps_path': str(self.steps_path),
            'config_path': str(self.config_path),
            'exists': self.project_path.exists()
        }