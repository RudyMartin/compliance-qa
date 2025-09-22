"""
Semantic Database for Embedding Storage
Stores document embeddings with SQLite and vector similarity search
"""

import sqlite3
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pickle
import hashlib

class SemanticDatabase:
    """Semantic database for storing and querying document embeddings"""

    def __init__(self, db_path: str = "semantic_embeddings.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.initialize_database()

    def initialize_database(self):
        """Create database tables for semantic storage"""
        cursor = self.conn.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                total_chunks INTEGER NOT NULL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding_vector BLOB NOT NULL,
                embedding_dim INTEGER NOT NULL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(document_id),
                UNIQUE(document_id, chunk_id)
            )
        """)

        # Semantic indices table (for similarity search)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_indices (
                index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_name TEXT UNIQUE NOT NULL,
                index_type TEXT NOT NULL,
                total_vectors INTEGER NOT NULL,
                dimension INTEGER NOT NULL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Query history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                query_embedding BLOB,
                results_count INTEGER,
                execution_time_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embeddings_document
            ON embeddings(document_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embeddings_chunk
            ON embeddings(document_id, chunk_id)
        """)

        self.conn.commit()
        print(f"[INFO] Semantic database initialized at: {self.db_path}")

    def add_document(self, filename: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Add a document to the database"""
        # Generate document ID
        content_hash = hashlib.md5(content.encode()).hexdigest()
        document_id = f"doc_{content_hash[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents
            (document_id, filename, content_hash, total_chunks, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            document_id,
            filename,
            content_hash,
            0,  # Will update after adding chunks
            json.dumps(metadata or {})
        ))
        self.conn.commit()

        print(f"[OK] Added document: {filename} (ID: {document_id})")
        return document_id

    def add_embedding(self,
                     document_id: str,
                     chunk_id: int,
                     chunk_text: str,
                     embedding: np.ndarray,
                     metadata: Optional[Dict] = None):
        """Add an embedding to the database"""
        cursor = self.conn.cursor()

        # Serialize the embedding vector
        embedding_blob = pickle.dumps(embedding)

        cursor.execute("""
            INSERT OR REPLACE INTO embeddings
            (document_id, chunk_id, chunk_text, embedding_vector, embedding_dim, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            document_id,
            chunk_id,
            chunk_text,
            embedding_blob,
            len(embedding),
            json.dumps(metadata or {})
        ))

        # Update document chunk count
        cursor.execute("""
            UPDATE documents
            SET total_chunks = (SELECT COUNT(*) FROM embeddings WHERE document_id = ?),
                updated_at = CURRENT_TIMESTAMP
            WHERE document_id = ?
        """, (document_id, document_id))

        self.conn.commit()

    def get_embedding(self, document_id: str, chunk_id: int) -> Optional[np.ndarray]:
        """Retrieve an embedding from the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT embedding_vector
            FROM embeddings
            WHERE document_id = ? AND chunk_id = ?
        """, (document_id, chunk_id))

        result = cursor.fetchone()
        if result:
            return pickle.loads(result[0])
        return None

    def search_similar(self,
                      query_embedding: np.ndarray,
                      top_k: int = 5,
                      threshold: float = 0.7) -> List[Dict]:
        """Search for similar embeddings using cosine similarity"""
        cursor = self.conn.cursor()

        # Get all embeddings
        cursor.execute("""
            SELECT document_id, chunk_id, chunk_text, embedding_vector, metadata
            FROM embeddings
        """)

        results = []
        for row in cursor.fetchall():
            # Deserialize embedding
            stored_embedding = pickle.loads(row['embedding_vector'])

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, stored_embedding)

            if similarity >= threshold:
                results.append({
                    'document_id': row['document_id'],
                    'chunk_id': row['chunk_id'],
                    'chunk_text': row['chunk_text'],
                    'similarity': float(similarity),
                    'metadata': json.loads(row['metadata'] or '{}')
                })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def create_semantic_index(self, index_name: str, index_type: str = "faiss"):
        """Create a semantic index for faster similarity search"""
        cursor = self.conn.cursor()

        # Count total vectors
        cursor.execute("SELECT COUNT(*) as count, MAX(embedding_dim) as dim FROM embeddings")
        result = cursor.fetchone()

        if result['count'] == 0:
            print("[WARNING] No embeddings to index")
            return

        cursor.execute("""
            INSERT OR REPLACE INTO semantic_indices
            (index_name, index_type, total_vectors, dimension, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            index_name,
            index_type,
            result['count'],
            result['dim'],
            json.dumps({'status': 'active'})
        ))
        self.conn.commit()

        print(f"[OK] Created semantic index: {index_name} ({result['count']} vectors)")

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Document stats
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        stats['total_documents'] = cursor.fetchone()['count']

        # Embedding stats
        cursor.execute("""
            SELECT
                COUNT(*) as count,
                AVG(embedding_dim) as avg_dim,
                MIN(embedding_dim) as min_dim,
                MAX(embedding_dim) as max_dim
            FROM embeddings
        """)
        result = cursor.fetchone()
        stats['total_embeddings'] = result['count']
        stats['avg_dimension'] = result['avg_dim']
        stats['dimension_range'] = (result['min_dim'], result['max_dim'])

        # Index stats
        cursor.execute("SELECT COUNT(*) as count FROM semantic_indices")
        stats['total_indices'] = cursor.fetchone()['count']

        # Query stats
        cursor.execute("""
            SELECT
                COUNT(*) as count,
                AVG(execution_time_ms) as avg_time
            FROM query_history
        """)
        result = cursor.fetchone()
        stats['total_queries'] = result['count']
        stats['avg_query_time_ms'] = result['avg_time']

        return stats

    def export_embeddings(self, output_file: str = "embeddings_export.npz"):
        """Export all embeddings to numpy format"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT document_id, chunk_id, embedding_vector
            FROM embeddings
            ORDER BY document_id, chunk_id
        """)

        embeddings_data = {}
        for row in cursor.fetchall():
            key = f"{row['document_id']}_{row['chunk_id']}"
            embeddings_data[key] = pickle.loads(row['embedding_vector'])

        # Save as numpy archive
        np.savez_compressed(output_file, **embeddings_data)
        print(f"[OK] Exported {len(embeddings_data)} embeddings to {output_file}")

    def close(self):
        """Close database connection"""
        self.conn.close()


class EmbeddingGenerator:
    """Generate mock embeddings for testing"""

    @staticmethod
    def generate_embedding(text: str, dimension: int = 768) -> np.ndarray:
        """Generate a mock embedding vector from text"""
        # Simple hash-based embedding for testing
        # In production, use real embedding models
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(dimension)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.astype(np.float32)

    @staticmethod
    def generate_from_chunks(chunks: List[str], dimension: int = 768) -> List[np.ndarray]:
        """Generate embeddings for multiple chunks"""
        embeddings = []
        for chunk in chunks:
            embedding = EmbeddingGenerator.generate_embedding(chunk, dimension)
            embeddings.append(embedding)
        return embeddings


def main():
    """Demo: Create semantic database and store embeddings"""
    print("\n" + "="*60)
    print("SEMANTIC DATABASE DEMO")
    print("="*60)

    # Initialize database
    db = SemanticDatabase("test_semantic.db")

    # Sample documents
    documents = [
        {
            "filename": "risk_report.pdf",
            "content": "This is a risk assessment report. It contains critical risk factors including compliance risks, operational risks, and strategic risks.",
            "metadata": {"type": "risk_report", "department": "compliance"}
        },
        {
            "filename": "validation_report.pdf",
            "content": "Model validation report showing performance metrics. The model achieved 95% accuracy with low false positive rates.",
            "metadata": {"type": "validation", "department": "data_science"}
        },
        {
            "filename": "compliance_doc.pdf",
            "content": "Compliance documentation outlining regulatory requirements. All procedures must follow SOX compliance standards.",
            "metadata": {"type": "compliance", "department": "legal"}
        }
    ]

    print("\n[1] Adding Documents and Embeddings")
    print("-" * 40)

    for doc in documents:
        # Add document
        doc_id = db.add_document(doc["filename"], doc["content"], doc["metadata"])

        # Create chunks (simple word-based chunking for demo)
        words = doc["content"].split()
        chunk_size = 10
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)

        # Generate and store embeddings
        embeddings = EmbeddingGenerator.generate_from_chunks(chunks)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            db.add_embedding(doc_id, i, chunk, embedding, {"chunk_size": chunk_size})

        print(f"  Added {len(chunks)} embeddings for {doc['filename']}")

    # Create semantic index
    print("\n[2] Creating Semantic Index")
    print("-" * 40)
    db.create_semantic_index("main_index")

    # Test similarity search
    print("\n[3] Testing Similarity Search")
    print("-" * 40)

    query = "What are the compliance risks?"
    query_embedding = EmbeddingGenerator.generate_embedding(query)

    print(f"Query: '{query}'")
    print("\nTop similar chunks:")

    results = db.search_similar(query_embedding, top_k=3, threshold=0.0)
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. Document: {result['document_id'][:20]}...")
        print(f"     Chunk: '{result['chunk_text'][:50]}...'")
        print(f"     Similarity: {result['similarity']:.3f}")

    # Show statistics
    print("\n[4] Database Statistics")
    print("-" * 40)
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Export embeddings
    print("\n[5] Exporting Embeddings")
    print("-" * 40)
    db.export_embeddings("semantic_embeddings_export.npz")

    db.close()
    print("\n" + "="*60)
    print("Semantic database demo complete!")


if __name__ == "__main__":
    main()