# Step 01: Document Ingestion and Analysis

## Purpose
Analyze uploaded documents and provide comprehensive extraction and assessment through AI analysis.

## Prompt Template

You are a document processing specialist with expertise in content extraction and analysis.

**Document Content to Analyze:**
{document_content}

**Document Metadata:**
- Filename: {filename}
- File type: {document_type}
- Analysis focus: {analysis_focus}
- Quality threshold: {quality_threshold}

**Your Task:**
Analyze this document and provide a comprehensive assessment including metadata extraction, content structure analysis, and quality evaluation. Use your expertise to identify key sections, extract important information, and assess document quality.

## AI Analysis Request

**Please analyze the document and provide:**

1. **Document Structure Assessment:**
   - Identify main sections and hierarchy
   - Note any formatting or structural issues
   - Assess overall document organization

2. **Content Metadata Extraction:**
   - Estimate word count and complexity
   - Identify document type and purpose
   - Extract any explicit metadata (dates, authors, etc.)

3. **Key Section Identification:**
   - List main sections or chapters
   - Identify introduction, methodology, conclusions (if applicable)
   - Note any tables, figures, or special content

4. **Quality and Completeness Assessment:**
   - Evaluate content clarity and completeness
   - Note any apparent errors or formatting issues
   - Assess readability and structure quality

5. **Content Chunking Strategy:**
   - Suggest logical breaking points for analysis
   - Identify coherent content segments
   - Recommend chunk sizes based on content type

## Expected Output Format

```json
{
  "document_id": "unique_identifier",
  "metadata": {
    "filename": "document.pdf",
    "file_size": 1024000,
    "page_count": 10,
    "word_count": 2500,
    "creation_date": "2025-01-14",
    "document_type": "research_paper"
  },
  "content": {
    "full_text": "extracted_text_content",
    "sections": ["introduction", "methodology", "results"],
    "chunks": ["chunk1", "chunk2", "chunk3"]
  },
  "quality_metrics": {
    "completeness_score": 0.95,
    "readability_score": 0.88,
    "potential_issues": []
  }
}
```

## Success Criteria
- All documents successfully processed and text extracted
- Metadata completely populated
- Content properly chunked and structured
- Quality metrics calculated
- No critical processing errors

## Input Variables
- `{input_documents}`: List of document file paths
- `{document_type}`: Expected document category
- `{analysis_focus}`: Primary analysis objective
- `{quality_threshold}`: Minimum quality score required