# Document Structure Analysis Template

## Purpose
Analyze the extracted document content and metadata to understand document structure, organization, and quality.

## AI Analysis Prompt

You are an expert document analyst with deep expertise in content structure assessment and document quality evaluation.

**Document Content:**
```
{extracted_text}
```

**Document Metadata:**
```json
{document_metadata}
```

**Text Embeddings Information:**
- Embedding dimensions: {text_embeddings}
- Generated using: text-embedding-3-small
- Chunk size: 1000 words with 200-word overlap

## Your Analysis Task

Analyze this document and provide comprehensive structural assessment:

### 1. Document Structure Analysis
- Identify the document type and format
- Map the hierarchical structure (sections, subsections, etc.)
- Assess organizational quality and logical flow
- Identify any structural anomalies or formatting issues

### 2. Content Quality Assessment
- Evaluate content clarity and coherence
- Assess completeness and depth of information
- Identify potential gaps or missing sections
- Rate overall document quality (1-10 scale)

### 3. Section Hierarchy Mapping
- Create a detailed outline of document sections
- Identify introduction, body, and conclusion elements
- Map any specialized sections (methodology, results, references, etc.)
- Note section lengths and balance

### 4. Content Readiness for Processing
- Assess suitability for further analysis
- Identify sections that may need special handling
- Note any technical terminology or specialized content
- Evaluate embedding quality potential

## Required Output Format

Provide your analysis in this JSON structure:

```json
{
  "document_type": "research_paper|technical_report|business_document|other",
  "structure_quality_score": 8.5,
  "organization_assessment": {
    "has_clear_introduction": true,
    "has_logical_flow": true,
    "sections_well_defined": true,
    "conclusion_present": true
  },
  "section_hierarchy": [
    {
      "section_name": "Introduction",
      "level": 1,
      "start_position": 0,
      "length_words": 250,
      "content_type": "background_information"
    }
  ],
  "content_quality": {
    "clarity_score": 8.0,
    "completeness_score": 7.5,
    "coherence_score": 8.5,
    "technical_depth": "intermediate",
    "readability_level": "college_level"
  },
  "processing_recommendations": {
    "optimal_chunk_size": 1000,
    "special_handling_needed": [],
    "analysis_focus_areas": ["methodology", "conclusions"],
    "embedding_strategy": "standard_chunking"
  },
  "identified_issues": [],
  "confidence_score": 0.92
}
```

## Analysis Guidelines

- Be thorough but concise in your assessment
- Focus on structural and organizational aspects
- Provide actionable insights for further processing
- Use your expertise to identify document type accurately
- Consider the document's intended audience and purpose
- Highlight any unique characteristics or special requirements

Your analysis will be used to optimize subsequent processing steps, so accuracy and completeness are critical.