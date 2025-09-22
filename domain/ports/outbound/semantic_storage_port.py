"""
Semantic Storage Port - Hexagonal Architecture
==============================================

Port interface for storing and retrieving document embeddings.
Follows hexagonal architecture - domain depends on port, not implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime


class SemanticStoragePort(ABC):
    """Port for semantic embedding storage operations."""

    @abstractmethod
    def add_document(self, filename: str, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to semantic storage.

        Args:
            filename: Name of the document file
            content: Full text content of the document
            metadata: Optional metadata about the document

        Returns:
            document_id: Unique identifier for the document
        """
        pass

    @abstractmethod
    def add_embedding(self,
                     document_id: str,
                     chunk_id: int,
                     chunk_text: str,
                     embedding: np.ndarray,
                     metadata: Optional[Dict] = None) -> None:
        """
        Store an embedding for a document chunk.

        Args:
            document_id: ID of the parent document
            chunk_id: Index of the chunk within the document
            chunk_text: Text content of the chunk
            embedding: Embedding vector
            metadata: Optional metadata about the chunk
        """
        pass

    @abstractmethod
    def search_similar(self,
                      query_embedding: np.ndarray,
                      top_k: int = 5,
                      threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings using vector similarity.

        Args:
            query_embedding: Query vector to search with
            top_k: Number of top results to return
            threshold: Minimum similarity score threshold

        Returns:
            List of similar chunks with their similarity scores
        """
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by ID.

        Args:
            document_id: Document identifier

        Returns:
            Document data including metadata, or None if not found
        """
        pass

    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in storage.

        Returns:
            List of document summaries
        """
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its embeddings.

        Args:
            document_id: Document identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage metrics
        """
        pass

    @abstractmethod
    def export_embeddings(self, output_file: str) -> None:
        """
        Export all embeddings to file.

        Args:
            output_file: Path to output file
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close storage connection."""
        pass