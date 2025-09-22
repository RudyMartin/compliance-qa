"""
Prompt Steps Manager Service
============================

Manages prompt templates at the project level, including:
- Storage in project's prompts folder
- Import/export functionality
- Template variable management
- Version control for prompts
- Integration with AI services
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from .base_step_manager import BaseStepsManager

# TidyLLM RL integration
try:
    from packages.tidyllm.services.workflow_rl_optimizer import create_rl_enhanced_step
    TIDYLLM_RL_AVAILABLE = True
except ImportError:
    TIDYLLM_RL_AVAILABLE = False
from .step_attributes import PromptStep

logger = logging.getLogger(__name__)


class PromptStepsManager(BaseStepsManager):
    """Manages prompt templates for workflow projects."""

    def __init__(self, project_id: str, project_path: Path = None):
        """
        Initialize the prompt steps manager for a specific project.

        Args:
            project_id: The workflow/project ID
            project_path: Optional custom project path
        """
        self.project_id = project_id

        # Determine project path
        if project_path:
            self.project_path = Path(project_path)
        else:
            # Try to use path manager if available
            try:
                from common.utilities.path_manager import get_path_manager
                root = get_path_manager().root_folder
            except ImportError:
                # Fallback to relative path
                root = Path(__file__).parent.parent.parent
            self.project_path = Path(root) / "domain" / "workflows" / "projects" / project_id

        # Create prompts directory
        self.prompts_path = self.project_path / "prompts"
        self.prompts_path.mkdir(parents=True, exist_ok=True)

        # Path for the main prompts configuration
        self.config_path = self.prompts_path / "prompts_config.json"

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """Get all prompts for this project."""
        prompts = []

        # Load from individual JSON files
        json_files = list(self.prompts_path.glob("*.json"))
        for json_file in json_files:
            if json_file.name != "prompts_config.json":
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        prompt_data = json.load(f)
                        prompts.append(prompt_data)
                except Exception as e:
                    logger.error(f"Error loading {json_file}: {e}")

        return prompts

    def save_prompt(self, prompt_name: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a prompt template definition.

        Args:
            prompt_name: Name/ID of the prompt
            prompt_data: Prompt template data including text and variables

        Returns:
            Result dictionary with success status
        """
        try:
            # Add metadata
            prompt_data['prompt_name'] = prompt_name
            prompt_data['last_modified'] = datetime.now().isoformat()
            prompt_data['project_id'] = self.project_id

            # Ensure required fields
            if 'template' not in prompt_data:
                prompt_data['template'] = ""
            if 'variables' not in prompt_data:
                prompt_data['variables'] = []
            if 'version' not in prompt_data:
                prompt_data['version'] = "1.0.0"

            # Save to file
            file_path = self.prompts_path / f"{prompt_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(prompt_data, f, indent=2)

            # Update config
            self._update_config(prompt_name, "saved")

            return {
                'success': True,
                'file_path': str(file_path),
                'message': f"Prompt '{prompt_name}' saved successfully"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def load_prompt(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Load a specific prompt template."""
        file_path = self.prompts_path / f"{prompt_name}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {e}")
            return None

    def delete_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """Delete a prompt template."""
        try:
            file_path = self.prompts_path / f"{prompt_name}.json"

            if file_path.exists():
                file_path.unlink()
                self._update_config(prompt_name, "deleted")

                return {
                    'success': True,
                    'message': f"Prompt '{prompt_name}' deleted"
                }
            else:
                return {
                    'success': False,
                    'error': f"Prompt '{prompt_name}' not found"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def render_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Render a prompt template with variables.

        Args:
            prompt_name: Name of the prompt to render
            variables: Dictionary of variable values

        Returns:
            Rendered prompt text or None if prompt not found
        """
        prompt_data = self.load_prompt(prompt_name)
        if not prompt_data:
            return None

        template = prompt_data.get('template', '')

        # Simple variable replacement
        rendered = template
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            rendered = rendered.replace(placeholder, str(var_value))

        return rendered

    def create_from_text(self, prompt_name: str, text: str, auto_extract_variables: bool = True) -> Dict[str, Any]:
        """
        Create a prompt from plain text, optionally extracting variables.

        Args:
            prompt_name: Name for the prompt
            text: Plain text to convert to prompt template
            auto_extract_variables: Whether to auto-detect {variables}

        Returns:
            Result dictionary
        """
        try:
            variables = []

            if auto_extract_variables:
                # Extract {variable_name} patterns
                import re
                pattern = r'\{([^}]+)\}'
                matches = re.findall(pattern, text)
                variables = list(set(matches))  # Unique variables

            prompt_data = {
                'template': text,
                'variables': variables,
                'description': f"Prompt created from text",
                'category': 'custom',
                'version': '1.0.0',
                'examples': [],
                'tags': []
            }

            return self.save_prompt(prompt_name, prompt_data)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def enhance_prompt_with_rl(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a prompt step with TidyLLM RL optimization.

        Args:
            prompt_data: Prompt data to enhance

        Returns:
            Enhanced prompt data with RL factors
        """
        if not TIDYLLM_RL_AVAILABLE:
            logger.warning("TidyLLM RL not available for prompt enhancement")
            return prompt_data

        try:
            # Convert to step format for RL enhancement
            step_data = {
                'step_name': prompt_data.get('template', 'unnamed_prompt')[:50],
                'step_type': 'prompt',
                'description': prompt_data.get('description', ''),
                'template': prompt_data.get('template', ''),
                'variables': prompt_data.get('variables', [])
            }

            enhanced_step = create_rl_enhanced_step(step_data, self.project_id)

            # Merge back RL enhancements
            prompt_data.update({
                'rl_factors': enhanced_step.get('rl_factors', {}),
                'rl_enhanced': True,
                'rl_enhancement_timestamp': datetime.now().isoformat()
            })

            logger.info(f"Successfully enhanced prompt with TidyLLM RL: {prompt_data.get('template', 'unnamed')[:30]}...")
            return prompt_data
        except Exception as e:
            logger.error(f"Failed to enhance prompt with RL: {e}")
            return prompt_data

    def export_prompts(self, export_path: Path = None) -> Dict[str, Any]:
        """
        Export all prompts to a bundle.

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
            bundle_name = f"prompts_{self.project_id}_{timestamp}.json"
            bundle_path = export_path / bundle_name

            # Collect all prompts
            prompts = self.get_all_prompts()

            # Create export bundle
            export_data = {
                'project_id': self.project_id,
                'exported_at': datetime.now().isoformat(),
                'prompts_count': len(prompts),
                'prompts': prompts
            }

            # Save bundle
            with open(bundle_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return {
                'success': True,
                'export_path': str(bundle_path),
                'prompts_count': len(prompts),
                'message': f"Exported {len(prompts)} prompts to {bundle_name}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def import_prompts_bundle(self, bundle_path: Path, overwrite: bool = False) -> Dict[str, Any]:
        """
        Import prompts from an exported bundle.

        Args:
            bundle_path: Path to the bundle file
            overwrite: Whether to overwrite existing prompts

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

            for prompt_data in bundle_data.get('prompts', []):
                prompt_name = prompt_data.get('prompt_name', prompt_data.get('name', 'unknown'))
                file_path = self.prompts_path / f"{prompt_name}.json"

                if file_path.exists() and not overwrite:
                    skipped_count += 1
                    continue

                # Import the prompt
                result = self.save_prompt(prompt_name, prompt_data)
                if result['success']:
                    imported_count += 1

            return {
                'success': True,
                'imported': imported_count,
                'skipped': skipped_count,
                'message': f"Imported {imported_count} prompts, skipped {skipped_count}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_prompt_categories(self) -> Dict[str, List[str]]:
        """Get prompts organized by category."""
        prompts = self.get_all_prompts()
        categories = {}

        for prompt in prompts:
            category = prompt.get('category', 'uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(prompt.get('prompt_name', 'unnamed'))

        return categories

    def get_prompt_summary(self) -> Dict[str, Any]:
        """Get a summary of all prompts."""
        prompts = self.get_all_prompts()

        summary = {
            'total_prompts': len(prompts),
            'categories': {},
            'total_variables': 0,
            'versions': {},
            'last_modified': None
        }

        for prompt in prompts:
            # Count by category
            category = prompt.get('category', 'uncategorized')
            summary['categories'][category] = summary['categories'].get(category, 0) + 1

            # Count variables
            summary['total_variables'] += len(prompt.get('variables', []))

            # Track versions
            version = prompt.get('version', 'unknown')
            summary['versions'][version] = summary['versions'].get(version, 0) + 1

            # Track last modified
            if prompt.get('last_modified'):
                if not summary['last_modified'] or prompt['last_modified'] > summary['last_modified']:
                    summary['last_modified'] = prompt['last_modified']

        return summary

    def _update_config(self, prompt_name: str, action: str):
        """Update the prompts configuration file."""
        try:
            # Load existing config or create new
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'project_id': self.project_id,
                    'created_at': datetime.now().isoformat(),
                    'prompts': {},
                    'history': []
                }

            # Update prompts list
            if action == "saved":
                config['prompts'][prompt_name] = {
                    'last_modified': datetime.now().isoformat(),
                    'status': 'active'
                }
            elif action == "deleted":
                if prompt_name in config['prompts']:
                    del config['prompts'][prompt_name]

            # Add to history
            config['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'prompt_name': prompt_name
            })

            # Keep only last 100 history entries
            config['history'] = config['history'][-100:]

            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.error(f"Error updating config: {e}")


def get_prompt_steps_manager(project_id: str) -> PromptStepsManager:
    """Factory function to get a PromptStepsManager instance."""
    return PromptStepsManager(project_id)