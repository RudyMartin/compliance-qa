#!/usr/bin/env python3
"""
MVS Compliance Rules
====================
Model Validation Standards (MVS) compliance rules.
Extracted from TidyLLM to domain layer for clean separation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_ASSESSED = "NOT_ASSESSED"

@dataclass
class MVSRequirement:
    """MVS requirement definition."""
    id: str
    section: str
    description: str
    mandatory: bool
    validation_criteria: List[str]

class MVSRules:
    """MVS 5.4.3 compliance rules engine."""

    def __init__(self):
        self.requirements = self._load_requirements()

    def _load_requirements(self) -> Dict[str, MVSRequirement]:
        """Load MVS requirements."""
        return {
            'MVS_5.4.3': MVSRequirement(
                id='MVS_5.4.3',
                section='5.4.3',
                description='Model Validation Standards - Main Requirements',
                mandatory=True,
                validation_criteria=[
                    'Model documentation must be complete',
                    'Validation methodology must be documented',
                    'Testing procedures must be defined',
                    'Performance metrics must be reported'
                ]
            ),
            'MVS_5.4.3.1': MVSRequirement(
                id='MVS_5.4.3.1',
                section='5.4.3.1',
                description='Data Quality and Integrity',
                mandatory=True,
                validation_criteria=[
                    'Data sources must be documented',
                    'Data quality checks must be performed',
                    'Data lineage must be traceable',
                    'Missing data handling must be defined'
                ]
            ),
            'MVS_5.4.3.2': MVSRequirement(
                id='MVS_5.4.3.2',
                section='5.4.3.2',
                description='Model Performance Testing',
                mandatory=True,
                validation_criteria=[
                    'Performance metrics must be defined',
                    'Testing methodology must be documented',
                    'Backtesting results must be provided',
                    'Sensitivity analysis must be performed'
                ]
            ),
            'MVS_5.4.3.3': MVSRequirement(
                id='MVS_5.4.3.3',
                section='5.4.3.3',
                description='Model Assumptions and Limitations',
                mandatory=True,
                validation_criteria=[
                    'All assumptions must be documented',
                    'Limitations must be clearly stated',
                    'Assumption testing must be performed',
                    'Impact of violations must be assessed'
                ]
            ),
            'MVS_5.4.3.4': MVSRequirement(
                id='MVS_5.4.3.4',
                section='5.4.3.4',
                description='Ongoing Monitoring',
                mandatory=True,
                validation_criteria=[
                    'Monitoring plan must be established',
                    'Performance triggers must be defined',
                    'Escalation procedures must be documented',
                    'Review frequency must be specified'
                ]
            )
        }

    def check_compliance(self, document_content: Dict[str, Any]) -> Dict[str, Any]:
        """Check document compliance against MVS requirements."""
        results = {}
        overall_status = ComplianceStatus.COMPLIANT

        for req_id, requirement in self.requirements.items():
            result = self._check_requirement(requirement, document_content)
            results[req_id] = result

            # Update overall status
            if result['status'] == ComplianceStatus.NON_COMPLIANT:
                overall_status = ComplianceStatus.NON_COMPLIANT
            elif result['status'] == ComplianceStatus.PARTIALLY_COMPLIANT and overall_status == ComplianceStatus.COMPLIANT:
                overall_status = ComplianceStatus.PARTIALLY_COMPLIANT

        return {
            'overall_status': overall_status.value,
            'requirements': results,
            'summary': self._generate_summary(results)
        }

    def _check_requirement(self, requirement: MVSRequirement, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check a specific requirement."""

        # Extract relevant content sections
        relevant_sections = self._extract_relevant_sections(requirement, content)

        # Check each validation criterion
        criteria_results = []
        for criterion in requirement.validation_criteria:
            met = self._check_criterion(criterion, relevant_sections)
            criteria_results.append({
                'criterion': criterion,
                'met': met
            })

        # Determine compliance status
        met_count = sum(1 for r in criteria_results if r['met'])
        total_count = len(criteria_results)

        if met_count == total_count:
            status = ComplianceStatus.COMPLIANT
        elif met_count >= total_count * 0.7:  # 70% threshold
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT

        return {
            'status': status,
            'requirement': requirement.description,
            'mandatory': requirement.mandatory,
            'criteria_results': criteria_results,
            'met_count': met_count,
            'total_count': total_count,
            'confidence': self._calculate_confidence(relevant_sections)
        }

    def _extract_relevant_sections(self, requirement: MVSRequirement, content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sections relevant to a requirement."""
        # This would use TidyLLM's document processing in production
        # For now, return mock relevant sections

        section_map = {
            'MVS_5.4.3': ['executive_summary', 'methodology', 'validation'],
            'MVS_5.4.3.1': ['data_quality', 'data_sources', 'data_validation'],
            'MVS_5.4.3.2': ['performance', 'testing', 'results'],
            'MVS_5.4.3.3': ['assumptions', 'limitations', 'sensitivity'],
            'MVS_5.4.3.4': ['monitoring', 'controls', 'governance']
        }

        relevant = {}
        for section in section_map.get(requirement.id, []):
            if section in content:
                relevant[section] = content[section]

        return relevant

    def _check_criterion(self, criterion: str, sections: Dict[str, Any]) -> bool:
        """Check if a specific criterion is met."""
        # Simplified check - in production would use NLP
        criterion_lower = criterion.lower()

        # Check for key terms in sections
        sections_text = str(sections).lower()

        key_terms = {
            'documented': ['document', 'description', 'defined'],
            'performed': ['performed', 'conducted', 'executed'],
            'defined': ['defined', 'specified', 'established'],
            'provided': ['provided', 'included', 'presented']
        }

        for term, synonyms in key_terms.items():
            if term in criterion_lower:
                return any(syn in sections_text for syn in synonyms)

        # Default to partial compliance for demo
        return len(sections) > 0

    def _calculate_confidence(self, sections: Dict[str, Any]) -> float:
        """Calculate confidence score for the assessment."""
        if not sections:
            return 0.0

        # Simple confidence based on content availability
        base_confidence = 0.5
        content_bonus = min(0.4, len(sections) * 0.1)

        return min(1.0, base_confidence + content_bonus)

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance summary."""
        total_requirements = len(results)
        compliant = sum(1 for r in results.values() if r['status'] == ComplianceStatus.COMPLIANT)
        partially = sum(1 for r in results.values() if r['status'] == ComplianceStatus.PARTIALLY_COMPLIANT)
        non_compliant = sum(1 for r in results.values() if r['status'] == ComplianceStatus.NON_COMPLIANT)

        return {
            'total_requirements': total_requirements,
            'compliant': compliant,
            'partially_compliant': partially,
            'non_compliant': non_compliant,
            'compliance_rate': round(compliant / total_requirements * 100, 1) if total_requirements > 0 else 0
        }

    def get_requirement(self, requirement_id: str) -> Optional[MVSRequirement]:
        """Get a specific requirement by ID."""
        return self.requirements.get(requirement_id)

    def list_requirements(self) -> List[MVSRequirement]:
        """List all MVS requirements."""
        return list(self.requirements.values())

    def generate_remediation_plan(self, compliance_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate remediation plan for non-compliant items."""
        remediation_items = []

        for req_id, result in compliance_results.get('requirements', {}).items():
            if result['status'] != ComplianceStatus.COMPLIANT:
                requirement = self.requirements.get(req_id)
                if requirement:
                    # Find failed criteria
                    failed_criteria = [
                        cr['criterion']
                        for cr in result.get('criteria_results', [])
                        if not cr['met']
                    ]

                    remediation_items.append({
                        'requirement_id': req_id,
                        'requirement': requirement.description,
                        'priority': 'HIGH' if requirement.mandatory else 'MEDIUM',
                        'current_status': result['status'].value if isinstance(result['status'], ComplianceStatus) else result['status'],
                        'failed_criteria': failed_criteria,
                        'actions': self._generate_actions(req_id, failed_criteria)
                    })

        return remediation_items

    def _generate_actions(self, requirement_id: str, failed_criteria: List[str]) -> List[str]:
        """Generate specific actions for remediation."""
        action_map = {
            'MVS_5.4.3': [
                'Complete model documentation sections',
                'Review and update validation methodology',
                'Ensure all testing procedures are documented'
            ],
            'MVS_5.4.3.1': [
                'Document all data sources with metadata',
                'Implement comprehensive data quality checks',
                'Create data lineage documentation'
            ],
            'MVS_5.4.3.2': [
                'Define and document performance metrics',
                'Conduct comprehensive backtesting',
                'Perform sensitivity analysis'
            ],
            'MVS_5.4.3.3': [
                'Document all model assumptions',
                'Clearly state model limitations',
                'Test assumption validity'
            ],
            'MVS_5.4.3.4': [
                'Establish monitoring plan with KPIs',
                'Define performance triggers and thresholds',
                'Document escalation procedures'
            ]
        }

        return action_map.get(requirement_id, ['Review and update documentation'])