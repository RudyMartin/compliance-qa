"""
Ask AI Steps Manager Service
=============================

Manages AI conversation and assistance for workflow creation, including:
- Storage of AI conversations in project's ai_interactions folder
- Context management for AI assistance
- Workflow generation from AI suggestions
- Integration with AI models for workflow design
- Learning from previous interactions
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# TidyLLM RL integration
try:
    from packages.tidyllm.services.workflow_rl_optimizer import create_rl_enhanced_step
    TIDYLLM_RL_AVAILABLE = True
except ImportError:
    TIDYLLM_RL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AskAIStepsManager:
    """Manages AI interactions and suggestions for workflow projects."""

    def __init__(self, project_id: str, project_path: Path = None):
        """
        Initialize the ask AI steps manager for a specific project.

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

        # Create AI interactions directory
        self.ai_interactions_path = self.project_path / "ai_interactions"
        self.ai_interactions_path.mkdir(parents=True, exist_ok=True)

        # Path for the main AI interactions configuration
        self.config_path = self.ai_interactions_path / "ai_interactions_config.json"

        # Path for conversation history
        self.conversations_path = self.ai_interactions_path / "conversations"
        self.conversations_path.mkdir(exist_ok=True)

        # Path for AI-generated suggestions
        self.suggestions_path = self.ai_interactions_path / "suggestions"
        self.suggestions_path.mkdir(exist_ok=True)

    def start_conversation(self, conversation_id: str = None) -> Dict[str, Any]:
        """
        Start a new AI conversation session.

        Args:
            conversation_id: Optional specific conversation ID

        Returns:
            Conversation metadata
        """
        if not conversation_id:
            conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        conversation_data = {
            'conversation_id': conversation_id,
            'project_id': self.project_id,
            'started_at': datetime.now().isoformat(),
            'messages': [],
            'context': {
                'workflow_type': None,
                'requirements': [],
                'constraints': [],
                'suggestions_made': []
            },
            'status': 'active'
        }

        # Save initial conversation
        conv_file = self.conversations_path / f"{conversation_id}.json"
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2)

        return {
            'success': True,
            'conversation_id': conversation_id,
            'message': 'New conversation started'
        }

    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Add a message to the conversation.

        Args:
            conversation_id: The conversation to add to
            role: 'user' or 'assistant'
            content: The message content
            metadata: Optional metadata about the message

        Returns:
            Result dictionary
        """
        conv_file = self.conversations_path / f"{conversation_id}.json"

        if not conv_file.exists():
            return {
                'success': False,
                'error': f"Conversation {conversation_id} not found"
            }

        try:
            # Load conversation
            with open(conv_file, 'r', encoding='utf-8') as f:
                conversation = json.load(f)

            # Add message
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            conversation['messages'].append(message)
            conversation['last_updated'] = datetime.now().isoformat()

            # Save updated conversation
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2)

            return {
                'success': True,
                'message_count': len(conversation['messages'])
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Load a conversation history."""
        conv_file = self.conversations_path / f"{conversation_id}.json"

        if not conv_file.exists():
            return None

        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {e}")
            return None

    def save_ai_suggestion(self, suggestion_name: str, suggestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save an AI-generated workflow suggestion.

        Args:
            suggestion_name: Name for the suggestion
            suggestion_data: The suggestion details

        Returns:
            Result dictionary
        """
        try:
            # Add metadata
            suggestion_data['suggestion_name'] = suggestion_name
            suggestion_data['created_at'] = datetime.now().isoformat()
            suggestion_data['project_id'] = self.project_id
            suggestion_data['status'] = suggestion_data.get('status', 'pending')

            # Ensure required fields
            if 'workflow_steps' not in suggestion_data:
                suggestion_data['workflow_steps'] = []
            if 'reasoning' not in suggestion_data:
                suggestion_data['reasoning'] = ""
            if 'confidence_score' not in suggestion_data:
                suggestion_data['confidence_score'] = 0.0

            # Save to file
            file_path = self.suggestions_path / f"{suggestion_name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(suggestion_data, f, indent=2)

            # Update config
            self._update_config(f"suggestion_{suggestion_name}", "created")

            return {
                'success': True,
                'file_path': str(file_path),
                'message': f"AI suggestion '{suggestion_name}' saved successfully"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def enhance_ai_suggestion_with_rl(self, suggestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance AI suggestions with TidyLLM RL optimization.

        Args:
            suggestion_data: AI suggestion data to enhance

        Returns:
            Enhanced suggestion data with RL factors
        """
        if not TIDYLLM_RL_AVAILABLE:
            logger.warning("TidyLLM RL not available for AI suggestion enhancement")
            return suggestion_data

        try:
            # Enhance workflow steps in the AI suggestion
            workflow_steps = suggestion_data.get('workflow_steps', [])
            enhanced_steps = []

            for step in workflow_steps:
                enhanced_step = create_rl_enhanced_step(step, self.project_id)
                enhanced_steps.append(enhanced_step)

            suggestion_data.update({
                'workflow_steps': enhanced_steps,
                'rl_enhanced': True,
                'rl_enhancement_timestamp': datetime.now().isoformat(),
                'rl_enhancement_count': len(enhanced_steps)
            })

            logger.info(f"Successfully enhanced AI suggestion with TidyLLM RL: {suggestion_data.get('suggestion_name', 'unnamed')}")
            return suggestion_data
        except Exception as e:
            logger.error(f"Failed to enhance AI suggestion with RL: {e}")
            return suggestion_data

    def generate_workflow_from_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Generate a workflow based on the AI conversation.

        Args:
            conversation_id: The conversation to analyze

        Returns:
            Generated workflow structure
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {
                'success': False,
                'error': 'Conversation not found'
            }

        try:
            # Analyze conversation to extract requirements
            requirements = self._extract_requirements(conversation['messages'])

            # Generate workflow structure
            workflow = {
                'workflow_name': f"ai_generated_{conversation_id}",
                'description': 'Workflow generated from AI conversation',
                'source': 'ai_assistant',
                'conversation_id': conversation_id,
                'requirements': requirements,
                'steps': self._generate_steps_from_requirements(requirements),
                'created_at': datetime.now().isoformat()
            }

            # Save as suggestion
            suggestion_name = f"workflow_{conversation_id}"
            self.save_ai_suggestion(suggestion_name, {
                'workflow': workflow,
                'conversation_id': conversation_id,
                'workflow_steps': workflow['steps'],
                'reasoning': 'Generated from conversation analysis',
                'confidence_score': 0.75
            })

            return {
                'success': True,
                'workflow': workflow,
                'suggestion_name': suggestion_name
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_requirements(self, messages: List[Dict]) -> List[str]:
        """Extract requirements from conversation messages."""
        requirements = []

        for message in messages:
            if message['role'] == 'user':
                content = message['content'].lower()

                # Look for requirement keywords
                keywords = ['want', 'need', 'should', 'must', 'require', 'process', 'analyze', 'generate', 'extract']
                for keyword in keywords:
                    if keyword in content:
                        requirements.append(message['content'])
                        break

        return requirements

    def _generate_steps_from_requirements(self, requirements: List[str]) -> List[Dict]:
        """Generate workflow steps from requirements."""
        steps = []

        # Basic pattern matching for common operations
        patterns = {
            'extract': {'type': 'extraction', 'template': 'Extract data from input'},
            'analyze': {'type': 'analysis', 'template': 'Analyze extracted data'},
            'process': {'type': 'processing', 'template': 'Process input data'},
            'generate': {'type': 'generation', 'template': 'Generate output'},
            'validate': {'type': 'validation', 'template': 'Validate results'},
            'report': {'type': 'reporting', 'template': 'Create report'}
        }

        for i, req in enumerate(requirements):
            req_lower = req.lower()
            for pattern, step_template in patterns.items():
                if pattern in req_lower:
                    steps.append({
                        'step_name': f"step_{i+1}_{pattern}",
                        'step_type': step_template['type'],
                        'description': req,
                        'template': step_template['template'],
                        'position': i
                    })
                    break

        # If no patterns matched, create generic steps
        if not steps:
            steps = [
                {'step_name': 'input', 'step_type': 'input', 'description': 'Process input data', 'position': 0},
                {'step_name': 'process', 'step_type': 'processing', 'description': 'Main processing', 'position': 1},
                {'step_name': 'output', 'step_type': 'output', 'description': 'Generate output', 'position': 2}
            ]

        return steps

    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights from previous AI interactions.

        Returns:
            Learning insights and patterns
        """
        all_conversations = list(self.conversations_path.glob("*.json"))
        all_suggestions = list(self.suggestions_path.glob("*.json"))

        insights = {
            'total_conversations': len(all_conversations),
            'total_suggestions': len(all_suggestions),
            'common_requirements': {},
            'successful_patterns': [],
            'workflow_types': {}
        }

        # Analyze conversations
        for conv_file in all_conversations:
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv = json.load(f)

                # Extract patterns
                if 'context' in conv:
                    wf_type = conv['context'].get('workflow_type')
                    if wf_type:
                        insights['workflow_types'][wf_type] = insights['workflow_types'].get(wf_type, 0) + 1

                # Count requirements
                for req in conv['context'].get('requirements', []):
                    insights['common_requirements'][req] = insights['common_requirements'].get(req, 0) + 1

            except Exception as e:
                logger.error(f"Error analyzing conversation: {e}")

        # Sort common requirements
        if insights['common_requirements']:
            sorted_reqs = sorted(insights['common_requirements'].items(), key=lambda x: x[1], reverse=True)
            insights['top_requirements'] = [req for req, _ in sorted_reqs[:5]]

        return insights

    def export_conversations(self, export_path: Path = None) -> Dict[str, Any]:
        """
        Export all conversations and suggestions.

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
            bundle_name = f"ai_interactions_{self.project_id}_{timestamp}.json"
            bundle_path = export_path / bundle_name

            # Collect all data
            conversations = []
            for conv_file in self.conversations_path.glob("*.json"):
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conversations.append(json.load(f))

            suggestions = []
            for sugg_file in self.suggestions_path.glob("*.json"):
                with open(sugg_file, 'r', encoding='utf-8') as f:
                    suggestions.append(json.load(f))

            # Create export bundle
            export_data = {
                'project_id': self.project_id,
                'exported_at': datetime.now().isoformat(),
                'conversations_count': len(conversations),
                'suggestions_count': len(suggestions),
                'conversations': conversations,
                'suggestions': suggestions,
                'insights': self.get_learning_insights()
            }

            # Save bundle
            with open(bundle_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            return {
                'success': True,
                'export_path': str(bundle_path),
                'conversations_count': len(conversations),
                'suggestions_count': len(suggestions),
                'message': f"Exported {len(conversations)} conversations and {len(suggestions)} suggestions"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_ai_summary(self) -> Dict[str, Any]:
        """Get a summary of all AI interactions."""
        conversations = list(self.conversations_path.glob("*.json"))
        suggestions = list(self.suggestions_path.glob("*.json"))

        summary = {
            'total_conversations': len(conversations),
            'total_suggestions': len(suggestions),
            'active_conversations': 0,
            'implemented_suggestions': 0,
            'last_interaction': None
        }

        # Analyze conversations
        for conv_file in conversations:
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    conv = json.load(f)

                if conv.get('status') == 'active':
                    summary['active_conversations'] += 1

                # Track last interaction
                if conv.get('last_updated'):
                    if not summary['last_interaction'] or conv['last_updated'] > summary['last_interaction']:
                        summary['last_interaction'] = conv['last_updated']

            except Exception as e:
                logger.error(f"Error reading conversation: {e}")

        # Analyze suggestions
        for sugg_file in suggestions:
            try:
                with open(sugg_file, 'r', encoding='utf-8') as f:
                    sugg = json.load(f)

                if sugg.get('status') == 'implemented':
                    summary['implemented_suggestions'] += 1

            except Exception as e:
                logger.error(f"Error reading suggestion: {e}")

        return summary

    def _update_config(self, item_name: str, action: str):
        """Update the AI interactions configuration file."""
        try:
            # Load existing config or create new
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {
                    'project_id': self.project_id,
                    'created_at': datetime.now().isoformat(),
                    'interactions': {},
                    'history': []
                }

            # Update interactions list
            if action == "created" or action == "updated":
                config['interactions'][item_name] = {
                    'last_modified': datetime.now().isoformat(),
                    'type': 'conversation' if 'conv' in item_name else 'suggestion'
                }
            elif action == "deleted":
                if item_name in config['interactions']:
                    del config['interactions'][item_name]

            # Add to history
            config['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'item': item_name
            })

            # Keep only last 100 history entries
            config['history'] = config['history'][-100:]

            # Save config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.error(f"Error updating config: {e}")


def get_ask_ai_steps_manager(project_id: str) -> AskAIStepsManager:
    """Factory function to get an AskAIStepsManager instance."""
    return AskAIStepsManager(project_id)