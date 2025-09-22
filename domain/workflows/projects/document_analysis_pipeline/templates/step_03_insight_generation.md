# Step 03: Insight Generation and Synthesis

## Purpose
Generate actionable insights from the analyzed content using TidyLLM's synthesis capabilities. Create comprehensive analysis summaries and recommendations.

## Prompt Template

You are an expert research analyst. Generate valuable insights and actionable recommendations based on the document analysis.

**Content Analysis Results:**
{content_analysis}

**Document Context:**
{document_context}

**Insight Parameters:**
- Target audience: {target_audience}
- Business context: {business_context}
- Decision requirements: {decision_requirements}

## TidyLLM Functions Required
- `tidyllm.synthesize_insights()`
- `tidyllm.generate_recommendations()`
- `tidyllm.create_executive_summary()`
- `tidyllm.identify_patterns()`

## Synthesis Instructions

1. **Pattern Recognition:**
   - Identify recurring themes and patterns
   - Analyze relationships between concepts
   - Detect emerging trends or anomalies

2. **Insight Generation:**
   - Transform analysis into actionable insights
   - Connect findings to business implications
   - Prioritize insights by potential impact

3. **Recommendation Development:**
   - Create specific, actionable recommendations
   - Provide implementation guidance
   - Estimate resource requirements and timelines

4. **Executive Summary Creation:**
   - Synthesize key findings into concise summary
   - Highlight critical decision points
   - Present findings in business-friendly language

5. **Validation and Quality Check:**
   - Verify insight accuracy against source content
   - Ensure recommendations are feasible
   - Check for logical consistency

## Expected Output Format

```json
{
  "executive_summary": {
    "key_findings": ["finding1", "finding2", "finding3"],
    "critical_insights": ["insight1", "insight2"],
    "strategic_implications": ["implication1", "implication2"],
    "confidence_level": 0.92
  },
  "detailed_insights": {
    "patterns_identified": [
      {
        "pattern": "pattern_description",
        "frequency": 0.75,
        "significance": "high",
        "supporting_evidence": ["evidence1", "evidence2"]
      }
    ],
    "emerging_themes": ["theme1", "theme2"],
    "anomalies_detected": ["anomaly1", "anomaly2"]
  },
  "recommendations": [
    {
      "recommendation": "specific_action",
      "priority": "high",
      "impact_assessment": "significant_improvement",
      "implementation_effort": "medium",
      "timeline": "3-6 months",
      "resource_requirements": ["resource1", "resource2"]
    }
  ],
  "next_steps": {
    "immediate_actions": ["action1", "action2"],
    "further_research_needed": ["research_area1", "research_area2"],
    "stakeholder_engagement": ["stakeholder1", "stakeholder2"]
  },
  "quality_metrics": {
    "insight_relevance": 0.89,
    "recommendation_feasibility": 0.85,
    "evidence_support": 0.91
  }
}
```

## Success Criteria
- High-quality insights generated from analysis
- Actionable recommendations with clear implementation paths
- Executive summary suitable for decision-makers
- All insights properly supported by evidence
- Quality metrics meet minimum thresholds

## Input Variables
- `{content_analysis}`: Results from Step 02
- `{document_context}`: Original document purpose and context
- `{target_audience}`: Intended recipients of insights
- `{business_context}`: Organizational context for recommendations
- `{decision_requirements}`: Specific decisions that need to be made