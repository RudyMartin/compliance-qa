# AI Advisor + Business Signature System Integration

## Overview

The system combines two powerful domain-driven components:

1. **AI Advisor** (`packages/tidyllm/workflows/ai_advisor/workflow_advisor.py`) - DSPy-powered intelligent workflow recommendations
2. **Business Signature System** - Domain-driven DSPy signature generation from business requirements

Together, they create a comprehensive business intelligence system that not only captures business requirements but also provides ongoing AI-powered guidance for workflow optimization.

## AI Advisor Architecture

### Core DSPy Signatures
```python
class WorkflowContextAnalyzer(dspy.Signature):
    """Analyze workflow context to provide intelligent recommendations."""
    workflow_criteria = dspy.InputField(desc="JSON criteria defining workflow requirements")
    template_fields = dspy.InputField(desc="Template fields configuration with validation")
    recent_activity = dspy.InputField(desc="Recent workflow executions and results")
    final_results = dspy.InputField(desc="Latest workflow execution results")
    user_question = dspy.InputField(desc="User's specific question with context")

    advisor_response = dspy.OutputField(desc="Comprehensive workflow advice with recommendations")

class WorkflowOptimizer(dspy.Signature):
    """Provide workflow optimization recommendations."""
    current_workflow = dspy.InputField(desc="Current workflow configuration")
    bottlenecks = dspy.InputField(desc="Identified performance bottlenecks")
    usage_patterns = dspy.InputField(desc="User behavior and usage patterns")

    optimization_plan = dspy.OutputField(desc="Detailed optimization recommendations")

class TemplateFieldAdvisor(dspy.Signature):
    """Advise on template field configuration and validation."""
    current_fields = dspy.InputField(desc="Current template field definitions")
    validation_errors = dspy.InputField(desc="Recent validation errors")

    field_recommendations = dspy.OutputField(desc="Template field improvement suggestions")
```

### AI Advisor Capabilities

1. **Workflow Context Analysis**: Analyzes workflow criteria, template fields, recent activity, and results
2. **Performance Optimization**: Identifies bottlenecks and provides optimization recommendations
3. **Template Field Guidance**: Advises on field configuration and validation rules
4. **RAG-Enhanced Knowledge**: Integrates with knowledge base for domain-specific advice
5. **Learning from Interactions**: Stores interaction patterns for continuous improvement

## Integration Architecture

### Business Signature → AI Advisor Flow

```
Business Requirement Capture
        ↓
Business Signature Generation
        ↓
Signature Deployment as Tool
        ↓
Workflow Execution
        ↓
AI Advisor Analysis ← Performance Data
        ↓
Optimization Recommendations
        ↓
Enhanced Business Signatures
```

### Combined System Benefits

1. **Business-First Approach**: Captures requirements in business language
2. **AI-Powered Guidance**: Provides intelligent recommendations during workflow execution
3. **Continuous Improvement**: AI advisor learns from business signature performance
4. **Domain Intelligence**: Both systems understand business domains and vocabulary
5. **End-to-End Optimization**: From requirement capture to performance enhancement

## Enhanced Integration Implementation

### 1. Business Signature Advisor Service

Let me enhance the business signature service to integrate with the AI advisor:

```python
class BusinessSignatureAdvisor:
    """Enhanced business signature service with AI advisor integration."""

    def __init__(self):
        self.business_signature_service = BusinessSignatureService(dependencies)
        self.ai_advisor = WorkflowAIAdvisor()

    def generate_signature_with_ai_guidance(self, requirement: BusinessRequirement) -> Dict[str, Any]:
        """Generate business signature with AI advisor recommendations."""

        # Get AI advice for signature generation
        ai_advice = self.ai_advisor.get_workflow_advice(
            criteria=requirement.__dict__,
            template_fields={},
            recent_activity=[],
            final_results={},
            user_question=f"How should I design a DSPy signature for: {requirement.business_question}?",
            use_cases=[requirement.business_context.value]
        )

        # Generate signature
        signature = self.business_signature_service.generate_business_signature(requirement)

        # Enhance signature with AI recommendations
        if ai_advice.get("success"):
            signature.ai_recommendations = ai_advice.get("advice")
            signature.ai_enhanced = True

        return signature

    def optimize_deployed_business_tools(self) -> Dict[str, Any]:
        """Use AI advisor to optimize deployed business signature tools."""

        # Get all deployed business tools
        business_tools = self.business_signature_service.list_business_signatures()

        optimization_results = []

        for tool in business_tools:
            # Get performance data for this tool
            performance_data = self._get_tool_performance_data(tool["signature_id"])

            # Get AI optimization advice
            optimization_advice = self.ai_advisor.optimize_workflow(
                workflow_config=tool,
                performance_data=performance_data
            )

            optimization_results.append({
                "tool_id": tool["signature_id"],
                "tool_name": tool.get("signature_name"),
                "optimization_advice": optimization_advice,
                "performance_score": self._calculate_performance_score(performance_data)
            })

        return {
            "success": True,
            "optimizations": optimization_results,
            "overall_performance": self._calculate_overall_performance(optimization_results)
        }
```

### 2. AI-Guided Business Requirement Refinement

```python
def refine_business_requirement_with_ai(self, initial_requirement: Dict[str, Any]) -> BusinessRequirement:
    """Use AI advisor to refine and improve business requirements."""

    # Get AI advice on requirement structure
    ai_advice = self.ai_advisor.get_workflow_advice(
        criteria={},
        template_fields={},
        recent_activity=[],
        final_results={},
        user_question=f"""
        I want to capture a business requirement for: {initial_requirement.get('business_question')}

        Domain: {initial_requirement.get('business_context')}
        Type: {initial_requirement.get('requirement_type')}

        What additional information should I capture to create the most effective DSPy signature?
        What business rules and success criteria should I consider?
        """,
        use_cases=[initial_requirement.get('business_context', 'general')]
    )

    # Parse AI recommendations to enhance requirement
    enhanced_requirement = self._apply_ai_recommendations_to_requirement(
        initial_requirement,
        ai_advice.get("advice", "")
    )

    return self.business_signature_service.capture_business_requirement(**enhanced_requirement)
```

### 3. Performance-Driven Signature Evolution

```python
def evolve_signature_based_on_performance(self, signature_id: str) -> Dict[str, Any]:
    """Evolve business signatures based on AI advisor performance analysis."""

    # Get signature and its performance data
    signature_data = self.business_signature_service.get_signature_details(signature_id)
    performance_data = self._get_signature_performance_history(signature_id)

    # Get AI advisor analysis
    analysis = self.ai_advisor.get_workflow_advice(
        criteria=signature_data.get("business_requirement", {}),
        template_fields=signature_data.get("domain_inputs", {}),
        recent_activity=performance_data.get("recent_executions", []),
        final_results=performance_data.get("latest_results", {}),
        user_question=f"""
        This business signature has been running for a while. Based on its performance data:
        - Success rate: {performance_data.get('success_rate', 'unknown')}
        - Average execution time: {performance_data.get('avg_execution_time', 'unknown')}
        - Common issues: {performance_data.get('common_issues', [])}

        How can I improve this signature to better serve business needs?
        What patterns suggest the signature should be enhanced or restructured?
        """,
        use_cases=[signature_data.get("business_context", "general")]
    )

    # Generate evolution recommendations
    return {
        "signature_id": signature_id,
        "current_performance": performance_data,
        "ai_analysis": analysis,
        "evolution_recommendations": self._parse_evolution_recommendations(analysis),
        "suggested_improvements": self._generate_signature_improvements(signature_data, analysis)
    }
```

## Enhanced Business Requirement Portal with AI Integration

### AI-Assisted Requirement Capture

```python
def render_ai_assisted_capture(self):
    """Render AI-assisted business requirement capture interface."""

    st.subheader("🤖 AI-Assisted Requirement Refinement")

    # Initial business question
    business_question = st.text_area(
        "What business problem are you trying to solve?",
        placeholder="Example: How do I assess the financial risk in supplier contracts?"
    )

    if business_question and st.button("🧠 Get AI Guidance"):
        # Get AI suggestions for requirement structure
        with st.spinner("AI is analyzing your business question..."):
            ai_guidance = self.ai_advisor.get_workflow_advice(
                criteria={},
                template_fields={},
                recent_activity=[],
                final_results={},
                user_question=f"""
                The user wants to solve this business problem: {business_question}

                What business context and requirement type would be most appropriate?
                What key information should they provide to create an effective solution?
                What business rules and success criteria should they consider?
                """,
                use_cases=["business_requirement_analysis"]
            )

        if ai_guidance.get("success"):
            st.success("🎯 AI Analysis Complete!")

            with st.expander("🤖 AI Recommendations", expanded=True):
                st.write(ai_guidance.get("advice"))

            # Pre-fill form based on AI recommendations
            self._render_ai_enhanced_form(business_question, ai_guidance)
```

### AI-Powered Signature Optimization

```python
def render_signature_optimization(self):
    """Render AI-powered signature optimization interface."""

    st.subheader("⚡ AI-Powered Signature Optimization")

    # Get deployed signatures
    deployed_signatures = self.business_signature_service.list_business_signatures()

    if deployed_signatures:
        for signature in deployed_signatures:
            with st.expander(f"🔧 {signature.get('signature_name')}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Signature ID:** {signature.get('signature_id')}")
                    st.markdown(f"**Business Context:** {signature.get('business_context')}")
                    st.markdown(f"**Deployed:** {signature.get('created_at', 'Unknown')}")

                with col2:
                    if st.button(f"🤖 Get AI Optimization", key=f"opt_{signature.get('signature_id')}"):
                        with st.spinner("AI is analyzing signature performance..."):
                            optimization = self.business_signature_advisor.evolve_signature_based_on_performance(
                                signature.get('signature_id')
                            )

                        st.success("🎯 Optimization Analysis Complete!")

                        # Display AI recommendations
                        if optimization.get("ai_analysis", {}).get("success"):
                            st.markdown("**AI Recommendations:**")
                            st.write(optimization["ai_analysis"]["advice"])

                        # Display specific improvements
                        if optimization.get("suggested_improvements"):
                            st.markdown("**Suggested Improvements:**")
                            for improvement in optimization["suggested_improvements"]:
                                st.markdown(f"• {improvement}")
```

## Flow Macro Integration with AI Advisor

### Enhanced Flow Macro Execution

```python
def execute_business_tool_with_ai_monitoring(self, tool_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute business tool with AI advisor monitoring and optimization."""

    start_time = datetime.now()

    # Execute business signature tool
    result = self.workflow_service.execute_business_tool_macro(tool_id, inputs)

    execution_time = (datetime.now() - start_time).total_seconds() * 1000

    # Get AI analysis of execution
    if result.get("success"):
        ai_analysis = self.ai_advisor.get_workflow_advice(
            criteria={"tool_id": tool_id},
            template_fields=inputs,
            recent_activity=[],
            final_results=result,
            user_question=f"""
            This business tool just executed:
            - Tool: {tool_id}
            - Execution time: {execution_time}ms
            - Success: {result.get('success')}

            Based on the results, how can the user improve their inputs or workflow?
            Are there any patterns that suggest optimization opportunities?
            """,
            use_cases=["business_tool_optimization"]
        )

        # Enhance result with AI insights
        result["ai_insights"] = ai_analysis.get("advice") if ai_analysis.get("success") else None
        result["execution_time_ms"] = execution_time
        result["optimization_available"] = execution_time > 1000  # Suggest optimization if slow

    return result
```

### AI-Enhanced Flow Macro Commands

The system now supports AI-enhanced Flow Macro commands:

```
# Standard business tool execution
[BUSINESS_TOOL:financial_health_assessment] company_data.pdf

# AI-guided execution with optimization
[AI_BUSINESS_TOOL:financial_health_assessment] company_data.pdf

# AI advisor query for workflow guidance
[AI_ADVISOR] "How can I improve my contract review workflow?"

# Performance analysis for business tools
[AI_ANALYZE:contract_risk_assessment] performance_data.json
```

## Combined System Capabilities

### 1. Intelligent Requirement Capture
- AI advisor guides business stakeholders in defining comprehensive requirements
- Suggests missing business rules, success criteria, and validation needs
- Recommends appropriate business contexts and requirement types

### 2. Smart Signature Generation
- Business signature service creates domain-driven DSPy signatures
- AI advisor provides generation guidance and optimization suggestions
- Templates enhanced with AI-recommended business patterns

### 3. Performance-Driven Evolution
- AI advisor continuously monitors business tool performance
- Identifies optimization opportunities and bottlenecks
- Suggests signature improvements based on usage patterns

### 4. Business Intelligence Integration
- Both systems share domain vocabulary and business concepts
- AI advisor learns from business signature performance data
- Business signatures benefit from AI advisor's optimization insights

### 5. End-to-End Business Value
- From natural language business questions to optimized executable tools
- Continuous improvement loop between requirement capture and performance
- Business stakeholders get ongoing AI guidance for workflow optimization

## Usage Examples

### Example 1: AI-Guided Financial Analysis Signature

```python
# 1. Business stakeholder asks AI for guidance
ai_guidance = ai_advisor.get_workflow_advice(
    user_question="I need to assess financial health of potential suppliers",
    use_cases=["supplier_analysis", "financial_assessment"]
)

# 2. Use AI guidance to capture comprehensive business requirement
enhanced_requirement = business_signature_advisor.refine_business_requirement_with_ai({
    "business_question": "How do I assess financial health of potential suppliers?",
    "business_context": "financial_analysis",
    "requirement_type": "analysis_pattern"
})

# 3. Generate signature with AI recommendations
signature = business_signature_advisor.generate_signature_with_ai_guidance(enhanced_requirement)

# 4. Deploy and monitor with AI
deployment_result = business_signature_service.deploy_business_signature_as_tool(signature.signature_id)

# 5. Execute with AI monitoring
result = flow_orchestration_service.execute_business_tool_with_ai_monitoring(
    f"business_tool_{signature.signature_id}",
    {"supplier_financials": "supplier_data.pdf"}
)

# 6. Get AI optimization recommendations
optimization = business_signature_advisor.evolve_signature_based_on_performance(signature.signature_id)
```

### Example 2: AI-Enhanced Flow Macro Workflow

```bash
# Execute with AI insights
[AI_BUSINESS_TOOL:supplier_financial_assessment] supplier_data.pdf

# Get AI advice on workflow improvement
[AI_ADVISOR] "My supplier assessment takes too long, how can I optimize it?"

# Analyze performance patterns
[AI_ANALYZE:supplier_financial_assessment] recent_performance.json
```

## Benefits of Integration

### For Business Stakeholders
- **Guided Requirement Capture**: AI helps define comprehensive business needs
- **Continuous Optimization**: Ongoing AI recommendations for workflow improvement
- **Performance Insights**: Understanding of how business tools perform over time
- **Natural Language Interaction**: Ask AI questions about workflow optimization

### For Technical Teams
- **Intelligent Code Generation**: AI-enhanced DSPy signature creation
- **Performance Monitoring**: Automated detection of optimization opportunities
- **Pattern Recognition**: AI identifies common issues and improvement patterns
- **Continuous Learning**: System improves based on usage patterns and feedback

### For Organizations
- **Business-IT Alignment**: Bridge between business needs and technical optimization
- **Continuous Improvement**: AI-driven evolution of business processes
- **Knowledge Preservation**: Business intelligence captured and reused
- **Competitive Advantage**: Rapidly evolving, optimized business workflows

This integration creates a powerful business intelligence system that not only captures and implements business requirements but also continuously optimizes them using AI-powered insights, creating a truly intelligent, domain-driven workflow platform.