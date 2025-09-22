"""
Action Steps Manager Service
============================

Manages action step definitions at the project level, including:
- Storage in project's action_steps folder
- Import/export functionality
- Integration with actions_spec.json templates
- DSPy signature generation support
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ActionStepsManager:
    """Manages action steps for workflow projects."""

    def __init__(self, project_id: str, project_path: Path = None):
        """
        Initialize the action steps manager for a specific project.

        Args:
            project_id: The workflow/project ID
            project_path: Optional custom project path
        """
        self.project_id = project_id

        # Determine project path
        if project_path:
            self.project_path = Path(project_path)
        else:
            from core.utilities.path_manager import get_path_manager
            root = get_path_manager().root_folder
            self.project_path = Path(root) / "domain" / "workflows" / "projects" / project_id

        # Create action_steps directory
        self.action_steps_path = self.project_path / "action_steps"
        self.action_steps_path.mkdir(parents=True, exist_ok=True)

        # Path for the main action steps configuration
        self.config_path = self.action_steps_path / "action_steps_config.json"

    def get_all_action_steps(self) -> List[Dict[str, Any]]:
        """Get all action steps for this project."""
        action_steps = []

        # Load from individual JSON files
        json_files = list(self.action_steps_path.glob("*.json"))
        for json_file in json_files:
            if json_file.name != "action_steps_config.json":
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        step_data = json.load(f)
                        action_steps.append(step_data)
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")

        return action_steps

    def save_action_step(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save an action step definition.

        Args:
            step_name: Name/ID of the action step
            step_data: Action step definition data

        Returns:
            Result dictionary with success status
        """
        try:
            # Add metadata
            step_data['step_name'] = step_name
            step_data['last_modified'] = datetime.now().isoformat()
            step_data['project_id'] = self.project_id

            # Save to file
            file_path = self.action_steps_path / f"{step_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(step_data, f, indent=2)

            # Update config
            self._update_config(step_name, "saved")

            return {
                'success': True,
                'file_path': str(file_path),
                'message': f"Action step '{step_name}' saved successfully"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def load_action_step(self, step_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific action step."""
        file_path = self.action_steps_path / f"{step_name}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading action step {step_name}: {e}")
            return None

    def delete_action_step(self, step_name: str) -> Dict[str, Any]:
        """Delete an action step."""
        try:
            file_path = self.action_steps_path / f"{step_name}.json"

            if file_path.exists():
                file_path.unlink()
                self._update_config(step_name, "deleted")

                return {
                    'success': True,
                    'message': f"Action step '{step_name}' deleted"
                }
            else:
                return {
                    'success': False,
                    'error': f"Action step '{step_name}' not found"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def import_from_actions_spec(self, action_type: str) -> Dict[str, Any]:
        """
        Import an action definition from actions_spec.json.

        Args:
            action_type: The action type to import

        Returns:
            Result dictionary
        """
        try:
            # Load from actions_spec.json
            from domain.services.actions_loader_service import get_actions_loader
            loader = get_actions_loader()
            action_def = loader.get_action(action_type)

            if not action_def:
                return {
                    'success': False,
                    'error': f"Action type '{action_type}' not found in actions_spec.json"
                }

            # Convert to action step format
            step_data = {
                'step_type': action_def.action_type,
                'title': action_def.title,
                'description': action_def.description,
                'requires': action_def.requires,
                'produces': action_def.produces,
                'inputs': action_def.inputs,
                'params': action_def.params,
                'output_schema': action_def.output_schema,
                'validation_rules': action_def.validation_rules,
                'source': 'actions_spec.json',
                'imported_at': datetime.now().isoformat()
            }

            # Save as action step
            step_name = f"{action_type}_imported"
            result = self.save_action_step(step_name, step_data)

            if result['success']:
                result['message'] = f"Imported '{action_type}' from actions_spec.json"

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def export_action_steps(self, export_path: Path = None) -> Dict[str, Any]:
        """
        Export all action steps to a bundle.

        Args:
            export_path: Optional path to export to

        Returns:
            Result dictionary with export location
        """
        try:
            if not export_path:
                export_path = self.project_path / "exports"
                export_path.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bundle_name = f"action_steps_{self.project_id}_{timestamp}.json"
            bundle_path = export_path / bundle_name

            # Collect all action steps
            action_steps = self.get_all_action_steps()

            # Create export bundle
            export_data = {
                'project_id': self.project_id,
                'exported_at': datetime.now().isoformat(),
                'action_steps_count': len(action_steps),
                'action_steps': action_steps
            }

            # Save bundle
            with open(bundle_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return {
                'success': True,
                'export_path': str(bundle_path),
                'action_steps_count': len(action_steps),
                'message': f"Exported {len(action_steps)} action steps to {bundle_name}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def import_action_steps_bundle(self, bundle_path: Path, overwrite: bool = False) -> Dict[str, Any]:
        """
        Import action steps from an exported bundle.

        Args:
            bundle_path: Path to the bundle file
            overwrite: Whether to overwrite existing action steps

        Returns:
            Result dictionary
        """
        try:
            if not bundle_path.exists():
                return {
                    'success': False,
                    'error': f"Bundle file not found: {bundle_path}"
                }

            # Load bundle
            with open(bundle_path, 'r', encoding='utf-8') as f:
                bundle_data = json.load(f)

            imported_count = 0
            skipped_count = 0

            for step_data in bundle_data.get('action_steps', []):
                step_name = step_data.get('step_name', step_data.get('step_type', 'unknown'))
                file_path = self.action_steps_path / f"{step_name}.json"

                if file_path.exists() and not overwrite:
                    skipped_count += 1
                    continue

                # Import the step
                result = self.save_action_step(step_name, step_data)
                if result['success']:
                    imported_count += 1

            return {
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'message': f"Imported {imported_count} action steps, skipped {skipped_count}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def create_from_workflow_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an action step from a workflow step definition.

        Args:
            step_data: Workflow step data

        Returns:
            Result dictionary
        """
        try:
            # Extract relevant fields
            action_step = {
                'step_name': step_data.get('step_name', 'unnamed'),
                'step_type': step_data.get('step_type', 'custom'),
                'template': step_data.get('template', ''),
                'description': step_data.get('description', ''),
                'params': step_data.get('params', {}),
                'requires': step_data.get('requires', []),
                'produces': step_data.get('produces', []),
                'created_from': 'workflow_step',
                'created_at': datetime.now().isoformat()
            }

            # Save the action step
            step_name = action_step['step_name']
            return self.save_action_step(step_name, action_step)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_action_step_summary(self) -> Dict[str, Any]:
        """Get a summary of all action steps."""
        action_steps = self.get_all_action_steps()

        summary = {
            'total_steps': len(action_steps),
            'step_types': {},
            'sources': {},
            'last_modified': None
        }

        for step in action_steps:
            # Count by type
            step_type = step.get('step_type', 'unknown')
            summary['step_types'][step_type] = summary['step_types'].get(step_type, 0) + 1

            # Count by source
            source = step.get('source', 'custom')
            summary['sources'][source] = summary['sources'].get(source, 0) + 1

            # Track last modified
            if step.get('last_modified'):
                if not summary['last_modified'] or step['last_modified'] > summary['last_modified']:
                    summary['last_modified'] = step['last_modified']

        return summary

    def _update_config(self, step_name: str, action: str):
        """Update the action steps configuration file."""
        try:
            # Load existing config or create new
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'project_id': self.project_id,
                    'created_at': datetime.now().isoformat(),
                    'action_steps': {},
                    'history': []
                }

            # Update action steps list
            if action == "saved":
                config['action_steps'][step_name] = {
                    'last_modified': datetime.now().isoformat(),
                    'status': 'active'
                }
            elif action == "deleted":
                if step_name in config['action_steps']:
                    del config['action_steps'][step_name]

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


def get_action_steps_manager(project_id: str) -> ActionStepsManager:
    """Factory function to get an ActionStepsManager instance."""
    return ActionStepsManager(project_id)