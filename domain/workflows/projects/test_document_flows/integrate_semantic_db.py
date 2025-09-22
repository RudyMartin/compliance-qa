"""
Integrate Semantic Database with Document Workflows
Process real PDFs and store their embeddings in the semantic database
"""

import os
import sys
from pathlib import Path
import PyPDF2
import numpy as np
from datetime import datetime
import json

# Import our semantic database
from semantic_database import SemanticDatabase, EmbeddingGenerator

class DocumentEmbeddingPipeline:
    """Pipeline to process documents and store embeddings in semantic database"""

    def __init__(self, db_path: str = "production_semantic.db"):
        self.db = SemanticDatabase(db_path)
        self.inputs_dir = Path("inputs")
        self.outputs_dir = Path("outputs/semantic_db")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def process_all_documents(self):
        """Process all PDFs and store embeddings in semantic database"""
        print("\n" + "="*60)
        print("DOCUMENT EMBEDDING PIPELINE")
        print("="*60)

        pdf_files = list(self.inputs_dir.glob("*.pdf"))
        print(f"\nFound {len(pdf_files)} PDF files to process")

        total_embeddings = 0

        for pdf_file in pdf_files:
            print(f"\n[Processing] {pdf_file.name}")
            print("-" * 40)

            # Extract text from PDF
            text = self.extract_pdf_text(pdf_file)
            print(f"  Extracted {len(text)} characters")

            # Add document to database
            metadata = {
                "file_size": pdf_file.stat().st_size,
                "extraction_date": datetime.now().isoformat(),
                "pdf_path": str(pdf_file)
            }
            doc_id = self.db.add_document(pdf_file.name, text, metadata)

            # Create chunks
            chunks = self.create_intelligent_chunks(text)
            print(f"  Created {len(chunks)} chunks")

            # Generate embeddings
            embeddings = EmbeddingGenerator.generate_from_chunks(chunks, dimension=768)

            # Store embeddings in database
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = {
                    "chunk_method": "intelligent",
                    "chunk_index": i,
                    "chunk_length": len(chunk)
                }
                self.db.add_embedding(doc_id, i, chunk, embedding, chunk_metadata)

            total_embeddings += len(embeddings)
            print(f"  Stored {len(embeddings)} embeddings in database")

        # Create semantic index
        print(f"\n[Creating Index]")
        self.db.create_semantic_index("production_index", "faiss")

        # Generate summary report
        self.generate_report(total_embeddings)

        return total_embeddings

    def extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"  [ERROR] Failed to extract text: {e}")
            text = f"Error extracting {pdf_path.name}"
        return text

    def create_intelligent_chunks(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list:
        """Create overlapping chunks with intelligent boundaries"""
        words = text.split()
        chunks = []

        if not words:
            return []

        # Create overlapping chunks
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)

            # Try to end at sentence boundary
            if chunk and not chunk[-1] in '.!?':
                # Look for the last sentence ending
                for j in range(len(chunk) - 1, max(0, len(chunk) - 50), -1):
                    if chunk[j] in '.!?':
                        chunk = chunk[:j + 1]
                        break

            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk.strip())

        return chunks

    def test_semantic_search(self):
        """Test semantic search capabilities"""
        print("\n" + "="*60)
        print("SEMANTIC SEARCH TEST")
        print("="*60)

        test_queries = [
            "What are the risk factors?",
            "Tell me about compliance requirements",
            "What validation metrics were used?",
            "Describe operational risks",
            "What are the regulatory standards?"
        ]

        for query in test_queries:
            print(f"\nQuery: '{query}'")
            print("-" * 40)

            # Generate query embedding
            query_embedding = EmbeddingGenerator.generate_embedding(query, dimension=768)

            # Search similar chunks
            results = self.db.search_similar(query_embedding, top_k=3, threshold=0.0)

            if results:
                for i, result in enumerate(results[:3], 1):
                    print(f"  {i}. Similarity: {result['similarity']:.4f}")
                    print(f"     Document: {result['document_id'][:30]}...")
                    print(f"     Chunk: '{result['chunk_text'][:80]}...'")
            else:
                print("  No results found")

    def generate_report(self, total_embeddings: int):
        """Generate embedding report"""
        stats = self.db.get_statistics()

        report = {
            "pipeline_run": datetime.now().isoformat(),
            "total_embeddings_created": total_embeddings,
            "database_statistics": stats,
            "configuration": {
                "embedding_dimension": 768,
                "chunk_method": "intelligent",
                "chunk_size": 500,
                "overlap": 100
            }
        }

        report_file = self.outputs_dir / "embedding_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n[Report] Saved to {report_file}")
        print(f"  Total Documents: {stats['total_documents']}")
        print(f"  Total Embeddings: {stats['total_embeddings']}")
        print(f"  Average Dimension: {stats['avg_dimension']:.0f}")
        print(f"  Indices Created: {stats['total_indices']}")

    def export_for_analysis(self):
        """Export embeddings for analysis"""
        export_file = self.outputs_dir / "embeddings_export.npz"
        self.db.export_embeddings(str(export_file))
        print(f"\n[Export] Embeddings saved to {export_file}")

class SemanticRAGIntegration:
    """Integrate semantic database with RAG system"""

    def __init__(self, db: SemanticDatabase):
        self.db = db

    def rag_query(self, query: str, top_k: int = 5) -> dict:
        """Perform RAG query using semantic database"""
        # Generate query embedding
        query_embedding = EmbeddingGenerator.generate_embedding(query, dimension=768)

        # Search for similar chunks
        similar_chunks = self.db.search_similar(query_embedding, top_k=top_k)

        # Build context from retrieved chunks
        context = "\n\n".join([chunk['chunk_text'] for chunk in similar_chunks])

        # Generate response (simplified for demo)
        response = {
            "query": query,
            "retrieved_chunks": len(similar_chunks),
            "context_length": len(context),
            "top_similarity": similar_chunks[0]['similarity'] if similar_chunks else 0,
            "answer": f"Based on {len(similar_chunks)} retrieved chunks, here's the answer to '{query}'...",
            "sources": [chunk['document_id'] for chunk in similar_chunks]
        }

        return response


def main():
    """Main pipeline execution"""
    print("Starting Semantic Database Integration...")

    # Initialize pipeline
    pipeline = DocumentEmbeddingPipeline("production_semantic.db")

    # Process all documents
    total = pipeline.process_all_documents()

    # Test semantic search
    pipeline.test_semantic_search()

    # Export embeddings
    pipeline.export_for_analysis()

    # Test RAG integration
    print("\n" + "="*60)
    print("RAG INTEGRATION TEST")
    print("="*60)

    rag = SemanticRAGIntegration(pipeline.db)
    rag_result = rag.rag_query("What are the main compliance risks in the documents?")

    print(f"\nRAG Query: '{rag_result['query']}'")
    print(f"Retrieved Chunks: {rag_result['retrieved_chunks']}")
    print(f"Context Length: {rag_result['context_length']} chars")
    print(f"Top Similarity: {rag_result['top_similarity']:.4f}")
    print(f"Answer: {rag_result['answer']}")

    # Close database
    pipeline.db.close()

    print("\n" + "="*60)
    print(f"Semantic database integration complete!")
    print(f"Total embeddings stored: {total}")
    print("="*60)


if __name__ == "__main__":
    main()