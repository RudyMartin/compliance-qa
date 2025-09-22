# Step 01: Document Pairing and Initial Assessment

## Purpose
Analyze and compare two documents to identify similarities, differences, and prepare for detailed comparison analysis.

## Prompt Template

You are a document comparison specialist with expertise in comparative analysis and content evaluation.

**Document A Content:**
{document_a_content}

**Document B Content:**
{document_b_content}

**Comparison Parameters:**
- Comparison type: {comparison_type}
- Focus areas: {focus_areas}
- Analysis depth: {analysis_depth}
- Similarity threshold: {similarity_threshold}

**Your Task:**
Analyze both documents and provide an initial assessment of their relationship, structure, and content for detailed comparison. Identify key similarities and differences at a high level.

## AI Analysis Request

**Please provide initial comparison analysis:**

1. **Document Overview Comparison:**
   - Compare document types, lengths, and overall structure
   - Identify primary purposes of each document
   - Assess comparative complexity and scope

2. **Structural Similarity Assessment:**
   - Compare section organization and hierarchy
   - Identify matching or corresponding sections
   - Note structural differences and unique elements

3. **Content Domain Mapping:**
   - Identify overlapping topic areas
   - Map corresponding themes and concepts
   - Note unique content areas in each document

4. **Initial Similarity Scoring:**
   - Provide high-level similarity assessment
   - Identify areas of high vs. low similarity
   - Suggest comparison strategies for detailed analysis

5. **Comparison Strategy Recommendation:**
   - Recommend optimal comparison approach
   - Identify key comparison dimensions
   - Suggest prioritization for detailed analysis

## Expected Output Format

```json
{
  "document_assessment": {
    "document_a": {
      "type": "research_paper",
      "estimated_length": 2500,
      "primary_purpose": "methodology_presentation",
      "complexity_level": "intermediate"
    },
    "document_b": {
      "type": "technical_report",
      "estimated_length": 1800,
      "primary_purpose": "results_presentation",
      "complexity_level": "basic"
    }
  },
  "structural_comparison": {
    "matching_sections": ["introduction", "methodology"],
    "unique_to_a": ["literature_review"],
    "unique_to_b": ["appendices"],
    "structural_similarity": 0.65
  },
  "content_mapping": {
    "overlapping_topics": ["data_analysis", "statistical_methods"],
    "unique_topics_a": ["theoretical_framework"],
    "unique_topics_b": ["implementation_details"],
    "topical_overlap": 0.72
  },
  "similarity_assessment": {
    "overall_similarity": 0.68,
    "content_similarity": 0.70,
    "structural_similarity": 0.65,
    "stylistic_similarity": 0.60
  },
  "comparison_strategy": {
    "recommended_approach": "section_by_section",
    "priority_areas": ["methodology", "results"],
    "comparison_dimensions": ["content", "approach", "conclusions"]
  }
}
```

## Success Criteria
- Both documents thoroughly assessed
- Structural and content similarities identified
- Clear comparison strategy developed
- Similarity scores calculated
- Ready for detailed comparative analysis

## Input Variables
- `{document_a_content}`: Full content of first document
- `{document_b_content}`: Full content of second document
- `{comparison_type}`: Type of comparison (content, style, methodology, etc.)
- `{focus_areas}`: Specific areas to emphasize
- `{analysis_depth}`: Level of detail required
- `{similarity_threshold}`: Minimum similarity to report