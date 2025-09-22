# Step 02: Content Analysis and Classification

## Purpose
Analyze document content using AI to identify themes, extract key information, and classify document sections. Use TidyLLM's semantic analysis capabilities.

## Prompt Template

You are an expert content analyst. Analyze the processed document content and provide comprehensive insights.

**Document Content:**
{processed_content}

**Document Metadata:**
{document_metadata}

**Analysis Parameters:**
- Focus areas: {focus_areas}
- Classification taxonomy: {classification_taxonomy}
- Depth level: {analysis_depth}

## TidyLLM Functions Required
- `tidyllm.semantic_analysis()`
- `tidyllm.extract_entities()`
- `tidyllm.classify_content()`
- `tidyllm.generate_embeddings()`

## Analysis Instructions

1. **Theme Identification:**
   - Identify primary and secondary themes
   - Extract key concepts and topics
   - Map content to predefined categories

2. **Entity Extraction:**
   - Extract people, places, organizations
   - Identify dates, numbers, and technical terms
   - Create entity relationship maps

3. **Content Classification:**
   - Classify document sections by type
   - Identify argumentative vs. descriptive content
   - Tag content by complexity level

4. **Semantic Analysis:**
   - Generate content embeddings using TidyLLM
   - Identify semantic relationships
   - Calculate content similarity scores

5. **Key Information Extraction:**
   - Extract main conclusions and findings
   - Identify supporting evidence
   - Summarize methodologies (if applicable)

## Expected Output Format

```json
{
  "content_analysis": {
    "primary_themes": ["theme1", "theme2", "theme3"],
    "secondary_themes": ["subtheme1", "subtheme2"],
    "key_concepts": ["concept1", "concept2"]
  },
  "entities": {
    "persons": ["Dr. Smith", "Jane Doe"],
    "organizations": ["University", "Research Institute"],
    "locations": ["New York", "Laboratory"],
    "dates": ["2025-01-01", "January 2025"],
    "technical_terms": ["algorithm", "methodology"]
  },
  "classification": {
    "document_type": "research_paper",
    "sections": {
      "introduction": "background_information",
      "methodology": "procedural_description",
      "results": "data_presentation"
    },
    "complexity_level": "intermediate"
  },
  "semantic_features": {
    "embeddings": "vector_representation",
    "similarity_scores": {"section1": 0.85, "section2": 0.72},
    "semantic_clusters": ["cluster1", "cluster2"]
  },
  "key_information": {
    "main_conclusions": ["conclusion1", "conclusion2"],
    "supporting_evidence": ["evidence1", "evidence2"],
    "methodology_summary": "brief_description"
  }
}
```

## Success Criteria
- All themes and concepts properly identified
- Entities accurately extracted and categorized
- Content sections correctly classified
- Embeddings generated successfully
- Key information comprehensively extracted

## Input Variables
- `{processed_content}`: Document content from Step 01
- `{document_metadata}`: Metadata from Step 01
- `{focus_areas}`: Specific areas to emphasize in analysis
- `{classification_taxonomy}`: Classification schema to use
- `{analysis_depth}`: Level of detail required (basic/intermediate/advanced)