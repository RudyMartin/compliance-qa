# Knowledge Base Analysis Template

## Purpose
Analyze the extracted documents and embeddings to assess knowledge base quality and readiness for RAG operations.

## AI Analysis Prompt

You are an expert knowledge base architect with deep expertise in RAG system optimization and document collection analysis.

**Extracted Documents:**
```
{extracted_texts}
```

**Embedding Information:**
- Total documents processed: {extracted_texts.length}
- Embedding model: text-embedding-3-small
- Chunk size: 1000 words with 200-word overlap
- Vector dimensions: 1536
- Total chunks generated: {knowledge_base_embeddings.total_chunks}

## Your Knowledge Base Assessment Task

### 1. Document Collection Analysis
- Assess the diversity and coverage of the document collection
- Identify primary themes and subject areas represented
- Evaluate document quality and information density
- Note any gaps or imbalances in the knowledge coverage

### 2. RAG Readiness Assessment
- Evaluate how well the documents support question-answering
- Assess the granularity and retrievability of information
- Identify documents that will be most/least useful for RAG
- Note any preprocessing improvements that could enhance RAG performance

### 3. Embedding Quality Evaluation
- Assess whether chunk size and overlap are optimal for this content
- Identify potential chunking issues (split concepts, incomplete thoughts)
- Evaluate semantic coherence within chunks
- Suggest embedding strategy optimizations

### 4. Knowledge Base Optimization
- Recommend improvements to document preprocessing
- Suggest metadata enrichment opportunities
- Identify high-value content for prioritized indexing
- Note potential quality issues requiring attention

## Required Output Format

Provide your analysis in this JSON structure:

```json
{
  "knowledge_base_overview": {
    "total_documents": 5,
    "primary_themes": ["AI implementation", "business strategy", "technical architecture"],
    "content_diversity_score": 8.5,
    "information_density": "high",
    "overall_quality_rating": 9.2
  },
  "document_analysis": [
    {
      "document_id": "doc_1",
      "title": "Extracted document title or identifier",
      "content_type": "research_paper|technical_report|business_document",
      "rag_value": "high|medium|low",
      "key_topics": ["topic1", "topic2", "topic3"],
      "chunk_count": 15,
      "quality_issues": ["issue1", "issue2"]
    }
  ],
  "rag_readiness": {
    "question_answering_potential": "excellent|good|fair|poor",
    "information_retrievability": 8.7,
    "semantic_coherence": 9.1,
    "coverage_completeness": "comprehensive|adequate|limited",
    "expected_query_types": [
      "What are the main approaches to AI implementation?",
      "How do different strategies compare?",
      "What are the key success factors?"
    ]
  },
  "embedding_assessment": {
    "chunk_size_adequacy": "optimal|good|needs_adjustment",
    "overlap_effectiveness": "appropriate|too_much|too_little",
    "semantic_boundary_respect": 8.3,
    "retrieval_granularity": "fine|medium|coarse",
    "optimization_recommendations": [
      "Consider smaller chunks for dense technical content",
      "Increase overlap for documents with complex cross-references"
    ]
  },
  "optimization_recommendations": {
    "preprocessing_improvements": [
      "Extract and index table content separately",
      "Enhance metadata with document structure information"
    ],
    "indexing_strategy": "hierarchical|flat|hybrid",
    "priority_enhancements": [
      "Add document relationship mapping",
      "Implement topic-based sub-indexing"
    ]
  },
  "demo_highlights": [
    "📚 Diverse knowledge base - covers multiple domains effectively",
    "🎯 High RAG potential - content well-suited for Q&A",
    "⚡ Optimal chunking - information properly segmented",
    "🔍 Rich retrieval possibilities - supports complex queries"
  ]
}
```

## Assessment Guidelines

- **Comprehensiveness**: Evaluate how well the knowledge base covers its intended domain
- **Coherence**: Assess whether information is logically organized and accessible
- **Retrievability**: Consider how easily specific information can be found
- **Quality**: Evaluate accuracy, clarity, and usefulness of content
- **RAG Optimization**: Focus on factors that will improve RAG performance
- **Demo Value**: Highlight aspects that will make impressive demo showcases

Your analysis will be used to optimize the RAG system and prepare for an impressive show-and-tell demonstration.

**Show and Tell Focus**: Emphasize the knowledge base's strengths and the sophisticated analysis capabilities that make this RAG system stand out from basic search systems.