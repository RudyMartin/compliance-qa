"""
Domain-Specific Business Signature Templates
===========================================
Templates for generating DSPy signatures based on business domain patterns.
These templates embody domain knowledge and business logic patterns.

Focus: Business domain patterns, not technical implementation patterns.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field

from ..services.business_signature_service import BusinessRequirementType, BusinessContext


@dataclass
class DomainSignatureTemplate:
    """Template for domain-specific signature generation."""
    template_id: str
    domain_context: BusinessContext
    requirement_type: BusinessRequirementType
    business_pattern_name: str
    domain_vocabulary: Dict[str, str]
    signature_structure: Dict[str, Any]
    business_logic_template: str
    validation_patterns: List[str]
    success_metrics: List[str]
    stakeholder_considerations: List[str]


class BusinessSignatureTemplateRegistry:
    """Registry of domain-specific business signature templates."""

    def __init__(self):
        """Initialize the template registry with domain-specific templates."""
        self.templates = self._initialize_domain_templates()

    def _initialize_domain_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Initialize all domain-specific signature templates."""
        templates = {}

        # Financial Analysis Domain Templates
        templates.update(self._create_financial_analysis_templates())

        # Contract Review Domain Templates
        templates.update(self._create_contract_review_templates())

        # Compliance Check Domain Templates
        templates.update(self._create_compliance_check_templates())

        # Quality Assurance Domain Templates
        templates.update(self._create_quality_assurance_templates())

        # Risk Assessment Domain Templates
        templates.update(self._create_risk_assessment_templates())

        # Document Processing Domain Templates
        templates.update(self._create_document_processing_templates())

        return templates

    # ==================== FINANCIAL ANALYSIS DOMAIN ====================

    def _create_financial_analysis_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create financial analysis domain templates."""
        templates = {}

        # Financial Health Assessment Template
        templates["financial_health_assessment"] = DomainSignatureTemplate(
            template_id="financial_health_assessment",
            domain_context=BusinessContext.FINANCIAL_ANALYSIS,
            requirement_type=BusinessRequirementType.ANALYSIS_PATTERN,
            business_pattern_name="Financial Health Assessment",
            domain_vocabulary={
                "liquidity_ratio": "Company's ability to pay short-term obligations",
                "debt_to_equity": "Ratio of total debt to shareholder equity",
                "profitability_margin": "Percentage of revenue retained as profit",
                "working_capital": "Current assets minus current liabilities",
                "cash_flow_trend": "Direction and magnitude of cash flow over time",
                "revenue_growth": "Rate of increase in company revenue",
                "financial_stability": "Consistency and predictability of financial performance"
            },
            signature_structure={
                "inputs": {
                    "financial_statements": "Complete set of company financial statements",
                    "market_context": "Relevant market and industry conditions",
                    "analysis_period": "Time period for financial analysis",
                    "peer_benchmarks": "Industry peer comparison data"
                },
                "outputs": {
                    "financial_health_score": "Overall financial health rating (0-100)",
                    "liquidity_assessment": "Company's liquidity position and risks",
                    "profitability_analysis": "Profitability trends and sustainability",
                    "debt_management_review": "Debt levels and management effectiveness",
                    "growth_potential": "Assessment of future growth prospects",
                    "risk_factors": "Key financial risk factors identified",
                    "management_recommendations": "Strategic financial recommendations"
                }
            },
            business_logic_template="""
            Financial Health Assessment Process:

            1. LIQUIDITY ANALYSIS
               - Calculate current ratio, quick ratio, cash ratio
               - Assess short-term debt coverage ability
               - Evaluate working capital management

            2. PROFITABILITY EVALUATION
               - Analyze gross, operating, and net profit margins
               - Compare profitability trends over time
               - Benchmark against industry standards

            3. LEVERAGE AND DEBT ANALYSIS
               - Calculate debt-to-equity and debt-to-assets ratios
               - Assess debt service coverage ability
               - Evaluate capital structure efficiency

            4. OPERATIONAL EFFICIENCY
               - Analyze asset turnover ratios
               - Evaluate inventory and receivables management
               - Assess operational leverage

            5. GROWTH AND SUSTAINABILITY
               - Evaluate revenue growth trends
               - Assess earnings quality and sustainability
               - Analyze reinvestment and expansion capacity

            6. RISK ASSESSMENT
               - Identify financial vulnerability areas
               - Assess market and operational risks
               - Evaluate management effectiveness
            """,
            validation_patterns=[
                "Financial ratios must be within reasonable business ranges",
                "Analysis must consider industry-specific factors",
                "Recommendations must be actionable and specific",
                "Risk assessment must be comprehensive and balanced",
                "Conclusions must be supported by quantitative evidence"
            ],
            success_metrics=[
                "Accuracy of financial health scoring compared to expert assessment",
                "Relevance and actionability of recommendations",
                "Identification of critical risk factors",
                "Stakeholder confidence in analysis results",
                "Time efficiency compared to manual analysis"
            ],
            stakeholder_considerations=[
                "CFO needs strategic financial insights",
                "Investors need risk-adjusted return expectations",
                "Board needs governance and oversight information",
                "Management needs operational improvement guidance",
                "Auditors need compliance and accuracy validation"
            ]
        )

        # Investment Decision Analysis Template
        templates["investment_decision_analysis"] = DomainSignatureTemplate(
            template_id="investment_decision_analysis",
            domain_context=BusinessContext.FINANCIAL_ANALYSIS,
            requirement_type=BusinessRequirementType.DECISION_PROCESS,
            business_pattern_name="Investment Decision Analysis",
            domain_vocabulary={
                "roi_analysis": "Return on investment calculation and projection",
                "npv_calculation": "Net present value of investment opportunity",
                "payback_period": "Time required to recover initial investment",
                "risk_adjusted_return": "Expected return adjusted for investment risks",
                "market_opportunity": "Size and attractiveness of target market",
                "competitive_advantage": "Sustainable competitive positioning",
                "capital_allocation": "Optimal distribution of financial resources"
            },
            signature_structure={
                "inputs": {
                    "investment_proposal": "Detailed investment opportunity description",
                    "financial_projections": "Projected cash flows and returns",
                    "market_analysis": "Market size, growth, and competitive landscape",
                    "risk_assessment": "Identified risks and mitigation strategies",
                    "strategic_alignment": "Alignment with company strategy and goals"
                },
                "outputs": {
                    "investment_recommendation": "Go/No-Go investment recommendation",
                    "financial_viability": "Detailed financial analysis and projections",
                    "risk_evaluation": "Comprehensive risk assessment and scoring",
                    "strategic_value": "Strategic benefits and alignment assessment",
                    "implementation_roadmap": "Recommended implementation approach",
                    "success_metrics": "Key performance indicators for tracking",
                    "exit_strategy": "Potential exit scenarios and conditions"
                }
            },
            business_logic_template="""
            Investment Decision Analysis Process:

            1. FINANCIAL EVALUATION
               - Calculate NPV, IRR, and payback period
               - Assess cash flow projections and assumptions
               - Evaluate financial risk and return profile

            2. STRATEGIC ASSESSMENT
               - Analyze alignment with business strategy
               - Evaluate market opportunity and timing
               - Assess competitive positioning impact

            3. RISK ANALYSIS
               - Identify and quantify key risk factors
               - Evaluate risk mitigation strategies
               - Assess downside scenarios and impacts

            4. RESOURCE REQUIREMENTS
               - Evaluate capital requirements and availability
               - Assess operational resource needs
               - Analyze opportunity cost of investment

            5. IMPLEMENTATION FEASIBILITY
               - Assess organizational readiness and capability
               - Evaluate timeline and milestone requirements
               - Identify critical success factors

            6. DECISION RECOMMENDATION
               - Synthesize analysis into clear recommendation
               - Provide rationale and supporting evidence
               - Outline next steps and approval requirements
            """,
            validation_patterns=[
                "Financial projections must be realistic and well-supported",
                "Risk assessment must be comprehensive and quantified",
                "Strategic alignment must be clearly demonstrated",
                "Implementation plan must be detailed and feasible",
                "Decision rationale must be clear and compelling"
            ],
            success_metrics=[
                "Accuracy of investment outcome predictions",
                "Quality of risk identification and assessment",
                "Stakeholder confidence in recommendations",
                "Speed of decision-making process",
                "Post-investment performance tracking"
            ],
            stakeholder_considerations=[
                "CEO needs strategic value and competitive impact",
                "CFO needs financial returns and capital efficiency",
                "Board needs governance and risk oversight",
                "Business units need operational impact and synergies",
                "Investors need return expectations and timeline"
            ]
        )

        return templates

    # ==================== CONTRACT REVIEW DOMAIN ====================

    def _create_contract_review_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create contract review domain templates."""
        templates = {}

        # Contract Risk Assessment Template
        templates["contract_risk_assessment"] = DomainSignatureTemplate(
            template_id="contract_risk_assessment",
            domain_context=BusinessContext.CONTRACT_REVIEW,
            requirement_type=BusinessRequirementType.VALIDATION_RULE,
            business_pattern_name="Contract Risk Assessment",
            domain_vocabulary={
                "liability_exposure": "Potential financial and legal liability risks",
                "termination_clause": "Conditions and consequences of contract termination",
                "indemnification": "Protection against losses or damages",
                "intellectual_property": "Rights and obligations regarding IP",
                "force_majeure": "Unforeseeable circumstances preventing performance",
                "governing_law": "Legal jurisdiction for contract interpretation",
                "payment_terms": "Timing, method, and conditions of payment",
                "performance_standards": "Required levels of service or delivery"
            },
            signature_structure={
                "inputs": {
                    "contract_document": "Full contract text for review",
                    "review_criteria": "Specific review requirements and focus areas",
                    "legal_framework": "Applicable laws and regulations",
                    "business_context": "Business purpose and strategic importance",
                    "stakeholder_priorities": "Key stakeholder concerns and priorities"
                },
                "outputs": {
                    "risk_assessment": "Comprehensive risk analysis and scoring",
                    "liability_analysis": "Liability exposure and mitigation options",
                    "compliance_review": "Regulatory and legal compliance status",
                    "commercial_terms": "Business terms evaluation and recommendations",
                    "red_flag_issues": "Critical issues requiring immediate attention",
                    "negotiation_points": "Recommended areas for negotiation",
                    "approval_recommendation": "Overall contract approval recommendation"
                }
            },
            business_logic_template="""
            Contract Risk Assessment Process:

            1. LEGAL COMPLIANCE REVIEW
               - Verify compliance with applicable laws and regulations
               - Check for required legal provisions and disclosures
               - Assess regulatory risk and reporting requirements

            2. LIABILITY AND RISK ANALYSIS
               - Identify and quantify liability exposures
               - Evaluate indemnification and insurance provisions
               - Assess force majeure and risk allocation clauses

            3. COMMERCIAL TERMS EVALUATION
               - Analyze payment terms and conditions
               - Evaluate performance standards and penalties
               - Assess pricing and cost structures

            4. INTELLECTUAL PROPERTY REVIEW
               - Verify IP ownership and usage rights
               - Assess confidentiality and non-disclosure provisions
               - Evaluate IP indemnification and protection

            5. TERMINATION AND EXIT PROVISIONS
               - Analyze termination rights and conditions
               - Evaluate exit costs and obligations
               - Assess post-termination restrictions and rights

            6. OPERATIONAL IMPACT ASSESSMENT
               - Evaluate business process and operational impacts
               - Assess resource requirements and capabilities
               - Identify integration and implementation challenges
            """,
            validation_patterns=[
                "All legal and regulatory requirements must be addressed",
                "Risk assessment must be quantified where possible",
                "Commercial terms must align with business objectives",
                "Recommendations must be specific and actionable",
                "Critical issues must be clearly highlighted and prioritized"
            ],
            success_metrics=[
                "Accuracy of risk identification and assessment",
                "Relevance and actionability of recommendations",
                "Speed of contract review process",
                "Stakeholder satisfaction with review quality",
                "Reduction in post-contract disputes and issues"
            ],
            stakeholder_considerations=[
                "Legal team needs comprehensive risk analysis",
                "Business units need operational impact assessment",
                "Finance needs cost and payment term evaluation",
                "Procurement needs vendor and supplier risk assessment",
                "Management needs strategic alignment and approval guidance"
            ]
        )

        return templates

    # ==================== COMPLIANCE CHECK DOMAIN ====================

    def _create_compliance_check_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create compliance check domain templates."""
        templates = {}

        # Regulatory Compliance Assessment Template
        templates["regulatory_compliance_assessment"] = DomainSignatureTemplate(
            template_id="regulatory_compliance_assessment",
            domain_context=BusinessContext.COMPLIANCE_CHECK,
            requirement_type=BusinessRequirementType.VALIDATION_RULE,
            business_pattern_name="Regulatory Compliance Assessment",
            domain_vocabulary={
                "regulatory_framework": "Set of laws and regulations applicable to business",
                "compliance_obligation": "Specific requirement mandated by regulation",
                "audit_trail": "Documentation of compliance activities and decisions",
                "violation_severity": "Impact level of compliance violation",
                "remediation_plan": "Actions required to achieve compliance",
                "monitoring_control": "Ongoing processes to maintain compliance",
                "regulatory_change": "Updates or modifications to regulatory requirements"
            },
            signature_structure={
                "inputs": {
                    "compliance_document": "Document or process requiring compliance check",
                    "regulatory_framework": "Applicable regulations and standards",
                    "compliance_standards": "Specific compliance requirements and criteria",
                    "business_context": "Business environment and operational context",
                    "previous_assessments": "Historical compliance assessments and results"
                },
                "outputs": {
                    "compliance_status": "Overall compliance determination (Pass/Fail/Conditional)",
                    "violation_details": "Specific compliance violations and gaps",
                    "severity_assessment": "Risk level and impact of violations",
                    "remediation_plan": "Required actions to achieve compliance",
                    "monitoring_requirements": "Ongoing compliance monitoring needs",
                    "certification_readiness": "Readiness for regulatory certification or audit",
                    "implementation_timeline": "Timeline for compliance achievement"
                }
            },
            business_logic_template="""
            Regulatory Compliance Assessment Process:

            1. REGULATORY MAPPING
               - Identify all applicable regulations and standards
               - Map regulatory requirements to business processes
               - Assess current compliance maturity level

            2. GAP ANALYSIS
               - Compare current state to regulatory requirements
               - Identify specific compliance gaps and violations
               - Assess impact and severity of each gap

            3. RISK ASSESSMENT
               - Evaluate regulatory risk exposure
               - Assess potential penalties and consequences
               - Prioritize compliance issues by risk level

            4. REMEDIATION PLANNING
               - Develop specific action plans for each violation
               - Estimate resources and timeline for compliance
               - Identify responsible parties and accountabilities

            5. MONITORING FRAMEWORK
               - Design ongoing compliance monitoring processes
               - Establish key compliance indicators and metrics
               - Create reporting and escalation procedures

            6. CERTIFICATION PREPARATION
               - Assess readiness for regulatory audits
               - Prepare documentation and evidence packages
               - Identify areas requiring additional preparation
            """,
            validation_patterns=[
                "All applicable regulations must be considered",
                "Gap analysis must be comprehensive and accurate",
                "Risk assessment must consider business impact",
                "Remediation plans must be specific and achievable",
                "Monitoring framework must be sustainable and effective"
            ],
            success_metrics=[
                "Accuracy of compliance gap identification",
                "Effectiveness of remediation recommendations",
                "Successful regulatory audit outcomes",
                "Reduction in compliance violations over time",
                "Stakeholder confidence in compliance program"
            ],
            stakeholder_considerations=[
                "Compliance officer needs comprehensive assessment and monitoring",
                "Legal team needs risk analysis and violation details",
                "Business operations need practical remediation plans",
                "Auditors need evidence and documentation packages",
                "Management needs strategic compliance roadmap"
            ]
        )

        return templates

    # ==================== QUALITY ASSURANCE DOMAIN ====================

    def _create_quality_assurance_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create quality assurance domain templates."""
        templates = {}

        # Quality Control Assessment Template
        templates["quality_control_assessment"] = DomainSignatureTemplate(
            template_id="quality_control_assessment",
            domain_context=BusinessContext.QUALITY_ASSURANCE,
            requirement_type=BusinessRequirementType.VALIDATION_RULE,
            business_pattern_name="Quality Control Assessment",
            domain_vocabulary={
                "quality_standard": "Defined criteria for acceptable quality level",
                "defect_rate": "Percentage of products or services not meeting standards",
                "quality_metric": "Measurable indicator of quality performance",
                "root_cause_analysis": "Investigation to identify underlying quality issues",
                "corrective_action": "Steps taken to address quality problems",
                "preventive_measure": "Actions to prevent quality issues from occurring",
                "quality_assurance": "Systematic approach to quality management",
                "continuous_improvement": "Ongoing efforts to enhance quality"
            },
            signature_structure={
                "inputs": {
                    "quality_data": "Quality measurements and performance data",
                    "quality_standards": "Applicable quality standards and criteria",
                    "process_documentation": "Process descriptions and procedures",
                    "historical_trends": "Historical quality performance trends",
                    "customer_feedback": "Customer quality feedback and complaints"
                },
                "outputs": {
                    "quality_assessment": "Overall quality performance evaluation",
                    "defect_analysis": "Analysis of defects and quality issues",
                    "root_cause_identification": "Underlying causes of quality problems",
                    "improvement_recommendations": "Specific quality improvement actions",
                    "quality_metrics": "Key quality performance indicators",
                    "compliance_status": "Quality standard compliance assessment",
                    "action_plan": "Prioritized quality improvement roadmap"
                }
            },
            business_logic_template="""
            Quality Control Assessment Process:

            1. QUALITY PERFORMANCE ANALYSIS
               - Evaluate current quality metrics and trends
               - Compare performance against quality standards
               - Identify areas of quality concern and excellence

            2. DEFECT AND ISSUE IDENTIFICATION
               - Analyze defect patterns and frequencies
               - Categorize quality issues by type and severity
               - Assess impact on customer satisfaction and business

            3. ROOT CAUSE ANALYSIS
               - Investigate underlying causes of quality issues
               - Use structured problem-solving methodologies
               - Identify systemic versus isolated quality problems

            4. PROCESS CAPABILITY ASSESSMENT
               - Evaluate process ability to meet quality standards
               - Identify process variation and control issues
               - Assess adequacy of quality control measures

            5. IMPROVEMENT OPPORTUNITY IDENTIFICATION
               - Identify specific quality improvement opportunities
               - Prioritize improvements by impact and feasibility
               - Develop recommendations for quality enhancement

            6. ACTION PLANNING
               - Create detailed quality improvement action plans
               - Assign responsibilities and timelines
               - Establish monitoring and measurement approaches
            """,
            validation_patterns=[
                "Quality assessment must be based on objective data",
                "Root cause analysis must be thorough and systematic",
                "Improvement recommendations must be specific and measurable",
                "Action plans must be realistic and achievable",
                "Quality metrics must align with business objectives"
            ],
            success_metrics=[
                "Accuracy of quality issue identification",
                "Effectiveness of improvement recommendations",
                "Reduction in defect rates over time",
                "Customer satisfaction improvement",
                "Cost reduction through quality improvements"
            ],
            stakeholder_considerations=[
                "Quality manager needs comprehensive assessment and action plans",
                "Operations needs practical improvement recommendations",
                "Customers need assurance of quality commitment",
                "Management needs quality performance visibility",
                "Regulatory bodies need compliance demonstration"
            ]
        )

        return templates

    # ==================== RISK ASSESSMENT DOMAIN ====================

    def _create_risk_assessment_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create risk assessment domain templates."""
        templates = {}

        # Business Risk Assessment Template
        templates["business_risk_assessment"] = DomainSignatureTemplate(
            template_id="business_risk_assessment",
            domain_context=BusinessContext.RISK_ASSESSMENT,
            requirement_type=BusinessRequirementType.ANALYSIS_PATTERN,
            business_pattern_name="Business Risk Assessment",
            domain_vocabulary={
                "risk_exposure": "Potential impact and likelihood of risk occurrence",
                "risk_appetite": "Level of risk organization is willing to accept",
                "risk_mitigation": "Actions taken to reduce risk probability or impact",
                "residual_risk": "Remaining risk after mitigation measures",
                "risk_tolerance": "Maximum acceptable level of risk variation",
                "business_continuity": "Ability to maintain operations during disruption",
                "risk_monitoring": "Ongoing surveillance of risk factors",
                "enterprise_risk": "Risks that affect overall business strategy"
            },
            signature_structure={
                "inputs": {
                    "business_context": "Business environment and operational context",
                    "risk_universe": "Comprehensive inventory of potential risks",
                    "historical_data": "Past risk events and their impacts",
                    "risk_appetite_statement": "Organization's risk tolerance levels",
                    "current_controls": "Existing risk management controls and processes"
                },
                "outputs": {
                    "risk_profile": "Comprehensive business risk assessment",
                    "priority_risks": "Highest priority risks requiring attention",
                    "risk_ratings": "Quantified risk scores and classifications",
                    "mitigation_strategies": "Recommended risk treatment approaches",
                    "monitoring_plan": "Risk monitoring and reporting framework",
                    "business_impact": "Potential business impact of identified risks",
                    "action_priorities": "Prioritized risk management actions"
                }
            },
            business_logic_template="""
            Business Risk Assessment Process:

            1. RISK IDENTIFICATION
               - Systematically identify all potential business risks
               - Categorize risks by type and business area
               - Consider both internal and external risk factors

            2. RISK ANALYSIS AND EVALUATION
               - Assess probability and impact of each risk
               - Quantify risks using consistent rating scales
               - Consider risk interdependencies and correlations

            3. RISK PRIORITIZATION
               - Rank risks based on overall risk exposure
               - Consider risk appetite and tolerance levels
               - Identify risks requiring immediate attention

            4. CONTROL ASSESSMENT
               - Evaluate effectiveness of existing controls
               - Identify control gaps and weaknesses
               - Assess adequacy of current risk management

            5. MITIGATION STRATEGY DEVELOPMENT
               - Develop risk treatment strategies for priority risks
               - Consider risk avoidance, reduction, transfer, or acceptance
               - Evaluate cost-benefit of mitigation options

            6. MONITORING AND REPORTING
               - Establish risk monitoring and measurement processes
               - Design risk reporting and escalation procedures
               - Create risk dashboard and key risk indicators
            """,
            validation_patterns=[
                "Risk assessment must be comprehensive and systematic",
                "Risk ratings must be consistent and well-supported",
                "Mitigation strategies must be practical and cost-effective",
                "Monitoring plan must be sustainable and actionable",
                "Risk priorities must align with business objectives"
            ],
            success_metrics=[
                "Completeness of risk identification",
                "Accuracy of risk impact and probability assessments",
                "Effectiveness of mitigation recommendations",
                "Stakeholder confidence in risk management",
                "Reduction in risk exposure over time"
            ],
            stakeholder_considerations=[
                "Risk manager needs comprehensive risk profile and monitoring",
                "Executive team needs strategic risk insights and priorities",
                "Board needs enterprise risk oversight and governance",
                "Operations needs practical risk mitigation guidance",
                "Auditors need risk management effectiveness assessment"
            ]
        )

        return templates

    # ==================== DOCUMENT PROCESSING DOMAIN ====================

    def _create_document_processing_templates(self) -> Dict[str, DomainSignatureTemplate]:
        """Create document processing domain templates."""
        templates = {}

        # Document Classification Template
        templates["document_classification"] = DomainSignatureTemplate(
            template_id="document_classification",
            domain_context=BusinessContext.DOCUMENT_PROCESSING,
            requirement_type=BusinessRequirementType.CLASSIFICATION,
            business_pattern_name="Document Classification",
            domain_vocabulary={
                "document_type": "Category or class of document based on content and purpose",
                "content_analysis": "Systematic examination of document content and structure",
                "business_relevance": "Importance and applicability to business processes",
                "retention_policy": "Rules governing document storage and disposal",
                "access_control": "Permissions and restrictions for document access",
                "metadata_extraction": "Identification and extraction of document attributes",
                "classification_confidence": "Degree of certainty in classification decision"
            },
            signature_structure={
                "inputs": {
                    "document_content": "Full text or content of document to classify",
                    "document_metadata": "Available document metadata and attributes",
                    "classification_schema": "Business document classification framework",
                    "business_context": "Business purpose and intended use of document",
                    "quality_indicators": "Document quality and completeness metrics"
                },
                "outputs": {
                    "document_classification": "Primary document type and category",
                    "classification_confidence": "Confidence level in classification decision",
                    "business_importance": "Business relevance and importance rating",
                    "processing_recommendations": "Recommended processing and handling actions",
                    "retention_guidance": "Document retention and disposal recommendations",
                    "access_requirements": "Required access controls and permissions",
                    "metadata_summary": "Key document attributes and characteristics"
                }
            },
            business_logic_template="""
            Document Classification Process:

            1. CONTENT ANALYSIS
               - Analyze document structure, format, and content
               - Identify key terms, phrases, and semantic patterns
               - Extract relevant business entities and concepts

            2. CLASSIFICATION MAPPING
               - Match document characteristics to classification schema
               - Apply business rules and classification criteria
               - Consider context and business purpose

            3. CONFIDENCE ASSESSMENT
               - Evaluate certainty and reliability of classification
               - Identify ambiguous or uncertain classifications
               - Flag documents requiring human review

            4. BUSINESS RELEVANCE EVALUATION
               - Assess document importance to business processes
               - Evaluate business value and criticality
               - Consider regulatory and compliance implications

            5. PROCESSING RECOMMENDATION
               - Recommend appropriate handling and processing actions
               - Suggest workflow routing and approval requirements
               - Identify integration and system requirements

            6. METADATA AND GOVERNANCE
               - Extract and validate document metadata
               - Apply retention and access control policies
               - Ensure compliance with governance requirements
            """,
            validation_patterns=[
                "Classification must align with business document taxonomy",
                "Confidence levels must be calibrated and reliable",
                "Business relevance assessment must consider all stakeholders",
                "Processing recommendations must be specific and actionable",
                "Governance requirements must be fully addressed"
            ],
            success_metrics=[
                "Classification accuracy compared to human experts",
                "Consistency of classification decisions",
                "Processing efficiency improvement",
                "Stakeholder satisfaction with classification quality",
                "Compliance with document governance policies"
            ],
            stakeholder_considerations=[
                "Document managers need accurate classification and routing",
                "Business users need relevant document discovery and access",
                "Compliance teams need governance and retention compliance",
                "IT teams need integration and system requirements",
                "Legal teams need privilege and confidentiality protection"
            ]
        )

        return templates

    # ==================== TEMPLATE REGISTRY METHODS ====================

    def get_template(self, template_id: str) -> Optional[DomainSignatureTemplate]:
        """Get a specific template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_context(self, business_context: BusinessContext) -> List[DomainSignatureTemplate]:
        """Get all templates for a specific business context."""
        return [
            template for template in self.templates.values()
            if template.domain_context == business_context
        ]

    def get_templates_by_requirement_type(self, requirement_type: BusinessRequirementType) -> List[DomainSignatureTemplate]:
        """Get all templates for a specific requirement type."""
        return [
            template for template in self.templates.values()
            if template.requirement_type == requirement_type
        ]

    def list_all_templates(self) -> List[DomainSignatureTemplate]:
        """Get all available templates."""
        return list(self.templates.values())

    def search_templates(self, keywords: List[str]) -> List[DomainSignatureTemplate]:
        """Search templates by keywords in business pattern name or vocabulary."""
        matching_templates = []

        for template in self.templates.values():
            # Search in business pattern name
            pattern_match = any(
                keyword.lower() in template.business_pattern_name.lower()
                for keyword in keywords
            )

            # Search in domain vocabulary
            vocab_match = any(
                keyword.lower() in term.lower() or keyword.lower() in definition.lower()
                for term, definition in template.domain_vocabulary.items()
                for keyword in keywords
            )

            if pattern_match or vocab_match:
                matching_templates.append(template)

        return matching_templates

    def get_domain_vocabulary(self, business_context: BusinessContext) -> Dict[str, str]:
        """Get consolidated domain vocabulary for a business context."""
        vocabulary = {}

        context_templates = self.get_templates_by_context(business_context)
        for template in context_templates:
            vocabulary.update(template.domain_vocabulary)

        return vocabulary

    def validate_template_coverage(self) -> Dict[str, Any]:
        """Validate that all business contexts and requirement types have templates."""
        coverage_report = {
            "total_templates": len(self.templates),
            "business_contexts": {},
            "requirement_types": {},
            "gaps": []
        }

        # Check business context coverage
        for context in BusinessContext:
            context_templates = self.get_templates_by_context(context)
            coverage_report["business_contexts"][context.value] = len(context_templates)

            if len(context_templates) == 0:
                coverage_report["gaps"].append(f"No templates for business context: {context.value}")

        # Check requirement type coverage
        for req_type in BusinessRequirementType:
            type_templates = self.get_templates_by_requirement_type(req_type)
            coverage_report["requirement_types"][req_type.value] = len(type_templates)

            if len(type_templates) == 0:
                coverage_report["gaps"].append(f"No templates for requirement type: {req_type.value}")

        return coverage_report