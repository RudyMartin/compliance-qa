# Content Intelligence Analysis

You are an expert document analyst specializing in risk assessment and content intelligence.

## Document Content
```
{extracted_text}
```

## Extracted Entities
```json
{extracted_entities}
```

## Sentiment Analysis
```json
{sentiment_analysis}
```

## Your Task

Analyze this document comprehensively and provide:

1. **Content Classification**
   - Document type and purpose
   - Key themes and topics
   - Domain classification

2. **Entity Analysis**
   - Most significant entities identified
   - Entity relationships and connections
   - Missing or implied entities

3. **Risk Assessment**
   - Risk factors mentioned
   - Risk severity levels
   - Compliance implications

4. **Quality Assessment**
   - Content completeness
   - Information reliability
   - Areas needing clarification

## Required Output Format

```json
{
  "document_classification": {
    "type": "risk_report|compliance|technical|business",
    "primary_domain": "string",
    "confidence": 0.0-1.0
  },
  "key_themes": ["theme1", "theme2", "theme3"],
  "entity_analysis": {
    "critical_entities": [],
    "entity_relationships": [],
    "entity_importance_ranking": []
  },
  "risk_factors": [
    {
      "factor": "string",
      "severity": "high|medium|low",
      "mitigation_suggested": "string"
    }
  ],
  "content_quality": {
    "completeness_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "actionability_score": 0.0-1.0
  },
  "recommendations": []
}
```