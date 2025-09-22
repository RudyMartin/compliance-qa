"""
Actions Loader Service - Load and Parse Business Workflow Actions
==================================================================

Loads action definitions from actions_spec.json and converts them to
workflow steps for the flow creator portal. Maps action types to DSPy
signatures for execution.

Part of the actions_spec.json → DSPy integration for automated workflows.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

# PathManager for cross-platform paths
try:
    from core.utilities.path_manager import get_path_manager
except ImportError:
    try:
        from common.utilities.path_manager import get_path_manager
    except ImportError:
        def get_path_manager():
            class MockPathManager:
                @property
                def root_folder(self):
                    return Path.cwd()
            return MockPathManager()

logger = logging.getLogger(__name__)


@dataclass
class ActionDefinition:
    """Represents a single action from actions_spec.json"""
    action_type: str
    title: str
    description: str
    requires: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    """Workflow step format for the flow creator portal"""
    step_name: str
    step_type: str
    template: str
    action_def: Optional[ActionDefinition] = None
    position: int = 0
    requires: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)


class ActionsLoaderService:
    """Service to load and manage business workflow actions"""

    def __init__(self):
        """Initialize the actions loader"""
        self.path_manager = get_path_manager()
        self.actions_spec_path = Path(self.path_manager.root_folder) / "domain" / "templates" / "actions_spec.json"
        self.actions: Dict[str, ActionDefinition] = {}
        self.action_chains: List[List[str]] = []
        self._load_actions()

    def _load_actions(self) -> None:
        """Load actions from actions_spec.json"""
        try:
            if not self.actions_spec_path.exists():
                logger.warning(f"actions_spec.json not found at {self.actions_spec_path}")
                return

            with open(self.actions_spec_path, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)

            # Parse each action definition
            for action_data in spec_data.get('actions', []):
                action = ActionDefinition(
                    action_type=action_data.get('type', ''),
                    title=action_data.get('title', ''),
                    description=action_data.get('description', ''),
                    requires=action_data.get('requires', []),
                    produces=action_data.get('produces', []),
                    inputs=action_data.get('inputs', {}),
                    params=action_data.get('params', {}),
                    output_schema=action_data.get('output_schema', {}),
                    validation_rules=action_data.get('validation_rules', []),
                    errors=action_data.get('errors', []),
                    metrics=action_data.get('metrics', [])
                )
                self.actions[action.action_type] = action

            # Build action chains based on dependencies
            self._build_action_chains()

            logger.info(f"Loaded {len(self.actions)} action definitions")

        except Exception as e:
            logger.error(f"Error loading actions spec: {e}")

    def _build_action_chains(self) -> None:
        """Build valid action chains based on requires/produces relationships"""
        # Common workflow chains
        self.action_chains = [
            # Document processing chain
            ["ingest_docs", "classify_intent", "extract_key_terms", "summarize_findings"],

            # Risk assessment chain
            ["ingest_docs", "extract_key_terms", "score_risk", "validate_evidence"],

            # Full reporting chain
            ["ingest_docs", "classify_intent", "extract_key_terms", "score_risk",
             "validate_evidence", "summarize_findings", "generate_report", "notify", "store_results"],

            # Review workflow
            ["ingest_docs", "extract_key_terms", "score_risk", "review_queue"],
        ]

    def get_all_actions(self) -> List[ActionDefinition]:
        """Get all available action definitions"""
        return list(self.actions.values())

    def get_action(self, action_type: str) -> Optional[ActionDefinition]:
        """Get a specific action by type"""
        return self.actions.get(action_type)

    def get_action_chains(self) -> List[List[str]]:
        """Get predefined action chains"""
        return self.action_chains

    def convert_to_workflow_step(self, action_type: str, position: int = 0) -> Optional[WorkflowStep]:
        """Convert an action definition to a workflow step"""
        action = self.get_action(action_type)
        if not action:
            return None

        # Map action type to step type
        step_type_mapping = {
            "ingest_docs": "ingestion",
            "classify_intent": "classification",
            "extract_key_terms": "extraction",
            "summarize_findings": "summarization",
            "score_risk": "scoring",
            "validate_evidence": "validation",
            "generate_report": "reporting",
            "notify": "notification",
            "store_results": "persistence",
            "review_queue": "review"
        }

        step_type = step_type_mapping.get(action_type, "processing")

        return WorkflowStep(
            step_name=action.title.lower().replace(" ", "_"),
            step_type=step_type,
            template=f"action:{action_type}",
            action_def=action,
            position=position,
            requires=action.requires,
            produces=action.produces,
            params=action.params
        )

    def create_workflow_from_chain(self, chain_index: int = 0) -> List[WorkflowStep]:
        """Create a complete workflow from a predefined action chain"""
        if chain_index >= len(self.action_chains):
            return []

        chain = self.action_chains[chain_index]
        workflow_steps = []

        for i, action_type in enumerate(chain):
            step = self.convert_to_workflow_step(action_type, position=i)
            if step:
                workflow_steps.append(step)

        return workflow_steps

    def validate_action_sequence(self, action_types: List[str]) -> Tuple[bool, List[str]]:
        """Validate that a sequence of actions can be chained together"""
        errors = []
        available_artifacts = set()

        for i, action_type in enumerate(action_types):
            action = self.get_action(action_type)
            if not action:
                errors.append(f"Unknown action type: {action_type}")
                continue

            # Check if required inputs are available
            for required in action.requires:
                if required not in available_artifacts:
                    errors.append(f"Action '{action_type}' requires '{required}' which is not available at step {i+1}")

            # Add produced artifacts
            available_artifacts.update(action.produces)

        return len(errors) == 0, errors

    def get_action_categories(self) -> Dict[str, List[str]]:
        """Group actions by category for UI display"""
        categories = {
            "Document Processing": ["ingest_docs", "extract_key_terms"],
            "Analysis": ["classify_intent", "score_risk", "validate_evidence"],
            "Output Generation": ["summarize_findings", "generate_report"],
            "Distribution": ["notify", "store_results", "review_queue"]
        }
        return categories

    def get_action_metadata(self, action_type: str) -> Dict[str, Any]:
        """Get display metadata for an action"""
        action = self.get_action(action_type)
        if not action:
            return {}

        return {
            "title": action.title,
            "description": action.description,
            "icon": self._get_action_icon(action_type),
            "color": self._get_action_color(action_type),
            "requires": action.requires,
            "produces": action.produces,
            "param_count": len(action.params),
            "has_llm": "llm_model" in action.params,
            "validation_count": len(action.validation_rules)
        }

    def _get_action_icon(self, action_type: str) -> str:
        """Get an emoji icon for the action type"""
        icon_map = {
            "ingest_docs": "📄",
            "classify_intent": "🎯",
            "extract_key_terms": "🔍",
            "summarize_findings": "📝",
            "score_risk": "⚠️",
            "validate_evidence": "✅",
            "generate_report": "📊",
            "notify": "📬",
            "store_results": "💾",
            "review_queue": "👤"
        }
        return icon_map.get(action_type, "⚙️")

    def _get_action_color(self, action_type: str) -> str:
        """Get a color for the action type"""
        color_map = {
            "ingest_docs": "blue",
            "classify_intent": "green",
            "extract_key_terms": "orange",
            "summarize_findings": "purple",
            "score_risk": "red",
            "validate_evidence": "green",
            "generate_report": "blue",
            "notify": "yellow",
            "store_results": "gray",
            "review_queue": "pink"
        }
        return color_map.get(action_type, "gray")

    def export_as_dspy_config(self, action_types: List[str]) -> Dict[str, Any]:
        """Export action sequence as DSPy configuration"""
        config = {
            "workflow_name": "action_based_flow",
            "actions": [],
            "artifacts_flow": {},
            "validation_rules": []
        }

        for action_type in action_types:
            action = self.get_action(action_type)
            if action:
                config["actions"].append({
                    "type": action_type,
                    "title": action.title,
                    "inputs": action.requires,
                    "outputs": action.produces,
                    "params": action.params
                })

                # Track artifact flow
                for artifact in action.produces:
                    config["artifacts_flow"][artifact] = action_type

                # Collect validation rules
                config["validation_rules"].extend([
                    f"{action_type}: {rule}" for rule in action.validation_rules
                ])

        return config


# Global service instance
_actions_loader: Optional[ActionsLoaderService] = None


def get_actions_loader() -> ActionsLoaderService:
    """Get global ActionsLoaderService instance"""
    global _actions_loader
    if _actions_loader is None:
        _actions_loader = ActionsLoaderService()
    return _actions_loader


if __name__ == "__main__":
    # Demo the actions loader
    print("Actions Loader Service Demo")
    print("=" * 50)

    loader = get_actions_loader()

    print(f"\nLoaded {len(loader.get_all_actions())} actions")

    print("\nAvailable Actions:")
    for action in loader.get_all_actions():
        print(f"  - {action.title} ({action.action_type})")
        print(f"    {action.description[:60]}...")

    print("\nPredefined Action Chains:")
    for i, chain in enumerate(loader.get_action_chains()):
        print(f"  Chain {i+1}: {' -> '.join(chain)}")

    print("\nCreating workflow from chain 1:")
    workflow = loader.create_workflow_from_chain(0)
    for step in workflow:
        print(f"  Step {step.position+1}: {step.step_name} ({step.step_type})")