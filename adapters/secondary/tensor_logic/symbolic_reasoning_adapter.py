"""
Symbolic Reasoning Adapter
===========================
Adapter implementing symbolic reasoning using compliance rules.

This adapter wraps the existing MVS/VST/SR compliance rules and
provides them as a SymbolicReasoningPort for the TensorLogicService.
"""

from typing import Dict, Any, List, Optional
import logging

from domain.ports.reasoning_ports import SymbolicReasoningPort
from domain.rules.mvs_rules import MVSRules, ComplianceStatus, MVSRequirement


logger = logging.getLogger(__name__)


class ComplianceRulesAdapter(SymbolicReasoningPort):
    """
    Symbolic reasoning adapter using compliance rules.

    This adapter provides deterministic, certifiable reasoning
    by executing compliance rules (MVS, VST, SR) over documents.
    """

    def __init__(self):
        """Initialize the compliance rules adapter."""
        self.mvs_rules = MVSRules()
        logger.info("Initialized ComplianceRulesAdapter with MVS rules")

    def execute(
        self,
        query: str,
        context: Dict[str, Any],
        rules: List[Any]
    ) -> Dict[str, Any]:
        """
        Execute symbolic reasoning using compliance rules.

        Args:
            query: The compliance question to answer
            context: Context with 'document', 'compliance_standard', etc.
            rules: List of compliance rules to check (or None to use all)

        Returns:
            Dict containing:
                - answer: Boolean or status string (COMPLIANT, etc.)
                - rules_used: List of rule IDs that were evaluated
                - violations: List of rule violations found
                - explanation: Natural language explanation
                - confidence: Confidence score (1.0 for symbolic)
                - details: Full compliance check results
        """
        logger.debug(f"Executing symbolic reasoning for query: {query}")

        # Extract document from context
        document = context.get('document', {})
        if not document:
            return self._empty_result("No document provided in context")

        # Get compliance standard if specified
        compliance_standard = context.get('compliance_standard')

        # Execute compliance check
        if compliance_standard and compliance_standard.startswith('MVS'):
            result = self._check_mvs_compliance(document, rules)
        else:
            # Default to MVS check
            result = self._check_mvs_compliance(document, rules)

        # Convert compliance result to symbolic reasoning result
        return self._convert_to_symbolic_result(result, query)

    def _check_mvs_compliance(
        self,
        document: Dict[str, Any],
        rules: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Check MVS compliance for a document.

        Args:
            document: Document content dictionary
            rules: Optional list of specific rules to check

        Returns:
            Compliance check results
        """
        # If specific rules provided, filter to those
        if rules:
            # Save original requirements
            original_reqs = self.mvs_rules.requirements.copy()

            # Filter to requested rules
            rule_ids = [r.id if isinstance(r, MVSRequirement) else str(r) for r in rules]
            self.mvs_rules.requirements = {
                k: v for k, v in original_reqs.items()
                if k in rule_ids
            }

            # Check compliance
            result = self.mvs_rules.check_compliance(document)

            # Restore original requirements
            self.mvs_rules.requirements = original_reqs
        else:
            # Check all requirements
            result = self.mvs_rules.check_compliance(document)

        return result

    def _convert_to_symbolic_result(
        self,
        compliance_result: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Convert compliance check result to symbolic reasoning format.

        Args:
            compliance_result: Result from MVSRules.check_compliance()
            query: Original query

        Returns:
            Symbolic reasoning result dict
        """
        # Extract overall status
        overall_status = compliance_result.get('overall_status', 'NOT_ASSESSED')

        # Determine answer based on query type
        answer = self._interpret_answer(query, overall_status, compliance_result)

        # Get list of rules that were checked
        requirements = compliance_result.get('requirements', {})
        rules_used = list(requirements.keys())

        # Find violations (non-compliant or partially compliant)
        violations = []
        for req_id, req_result in requirements.items():
            status = req_result.get('status')
            if isinstance(status, ComplianceStatus):
                status_value = status.value
            else:
                status_value = str(status)

            if status_value in ['NON_COMPLIANT', 'PARTIALLY_COMPLIANT']:
                violations.append({
                    'rule_id': req_id,
                    'requirement': req_result.get('requirement', ''),
                    'status': status_value,
                    'failed_criteria': [
                        cr['criterion']
                        for cr in req_result.get('criteria_results', [])
                        if not cr.get('met', False)
                    ]
                })

        # Generate explanation
        explanation = self._generate_explanation(
            overall_status,
            requirements,
            compliance_result.get('summary', {})
        )

        return {
            'answer': answer,
            'rules_used': rules_used,
            'violations': violations,
            'explanation': explanation,
            'confidence': 1.0,  # Symbolic reasoning is deterministic
            'details': compliance_result
        }

    def _interpret_answer(
        self,
        query: str,
        overall_status: str,
        compliance_result: Dict[str, Any]
    ) -> Any:
        """
        Interpret the answer based on query and compliance status.

        Args:
            query: Original question
            overall_status: Overall compliance status
            compliance_result: Full compliance result

        Returns:
            Appropriate answer (bool, str, or dict)
        """
        query_lower = query.lower()

        # Boolean questions
        if any(q in query_lower for q in ['is', 'does', 'has', 'compliant', 'satisfy']):
            return overall_status == 'COMPLIANT'

        # Status questions
        if 'status' in query_lower or 'what' in query_lower:
            return overall_status

        # Count questions
        if 'how many' in query_lower:
            summary = compliance_result.get('summary', {})
            if 'violation' in query_lower:
                return summary.get('non_compliant', 0)
            elif 'compliant' in query_lower:
                return summary.get('compliant', 0)
            else:
                return summary.get('total_requirements', 0)

        # Default: return status
        return overall_status

    def _generate_explanation(
        self,
        overall_status: str,
        requirements: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> str:
        """
        Generate natural language explanation of compliance results.

        Args:
            overall_status: Overall compliance status
            requirements: Individual requirement results
            summary: Summary statistics

        Returns:
            Natural language explanation
        """
        total = summary.get('total_requirements', 0)
        compliant = summary.get('compliant', 0)
        partially = summary.get('partially_compliant', 0)
        non_compliant = summary.get('non_compliant', 0)
        rate = summary.get('compliance_rate', 0)

        # Build explanation
        parts = []

        # Overall assessment
        parts.append(f"**Overall Status**: {overall_status}")
        parts.append(f"**Compliance Rate**: {rate}%")
        parts.append("")

        # Summary breakdown
        parts.append(f"**Requirements Assessed**: {total}")
        parts.append(f"- Fully Compliant: {compliant}")
        if partially > 0:
            parts.append(f"- Partially Compliant: {partially}")
        if non_compliant > 0:
            parts.append(f"- Non-Compliant: {non_compliant}")
        parts.append("")

        # Details on non-compliant items
        if non_compliant > 0 or partially > 0:
            parts.append("**Issues Found**:")
            for req_id, req_result in requirements.items():
                status = req_result.get('status')
                if isinstance(status, ComplianceStatus):
                    status_value = status.value
                else:
                    status_value = str(status)

                if status_value in ['NON_COMPLIANT', 'PARTIALLY_COMPLIANT']:
                    req_desc = req_result.get('requirement', req_id)
                    met = req_result.get('met_count', 0)
                    total_criteria = req_result.get('total_count', 0)

                    parts.append(f"- {req_id}: {req_desc}")
                    parts.append(f"  Status: {status_value}")
                    parts.append(f"  Criteria Met: {met}/{total_criteria}")

                    # List failed criteria
                    failed = [
                        cr['criterion']
                        for cr in req_result.get('criteria_results', [])
                        if not cr.get('met', False)
                    ]
                    if failed:
                        parts.append("  Failed Criteria:")
                        for criterion in failed[:3]:  # Limit to 3
                            parts.append(f"    • {criterion}")

        return "\n".join(parts)

    def _empty_result(self, message: str) -> Dict[str, Any]:
        """
        Create an empty result with error message.

        Args:
            message: Error message

        Returns:
            Empty result dict
        """
        return {
            'answer': False,
            'rules_used': [],
            'violations': [],
            'explanation': message,
            'confidence': 0.0,
            'details': {}
        }

    def get_available_rules(self) -> List[MVSRequirement]:
        """
        Get list of available compliance rules.

        Returns:
            List of MVS requirements
        """
        return self.mvs_rules.list_requirements()

    def get_rule_by_id(self, rule_id: str) -> Optional[MVSRequirement]:
        """
        Get a specific rule by ID.

        Args:
            rule_id: Rule identifier (e.g., 'MVS_5.4.3')

        Returns:
            MVS requirement or None
        """
        return self.mvs_rules.get_requirement(rule_id)

    def generate_remediation_plan(
        self,
        compliance_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate remediation plan for non-compliant items.

        Args:
            compliance_result: Result from check_compliance

        Returns:
            List of remediation items with actions
        """
        return self.mvs_rules.generate_remediation_plan(compliance_result)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ComplianceRulesAdapter("
            f"rules={len(self.mvs_rules.requirements)})"
        )
