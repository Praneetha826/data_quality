"""
Vector Store Module
Handles FAISS vector storage and similarity search operations
"""

import numpy as np
from typing import List, Optional, Dict, Any, Tuple
import pickle
from pathlib import Path

try:
    import faiss
except ImportError:
    faiss = None


class VectorStore:
    """
    Manages FAISS vector storage and similarity search
    """

    def __init__(self, dimension: int, index_type: str = "flat"):
        """
        Initialize the vector store

        Args:
            dimension: Dimension of the embedding vectors
            index_type: Type of FAISS index to use ("flat", "ivf", "hnsw")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.documents = []  # Store document metadata
        self.embeddings = None
        self._initialize_index()

    def _initialize_index(self):
        """Initialize the FAISS index"""
        if faiss is None:
            raise ImportError(
                "faiss-cpu is required for vector storage. "
                "Install it with: pip install faiss-cpu"
            )

        if self.index_type == "flat":
            # Flat L2 distance index
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # IVF (Inverted File) index
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        else:
            # Default to flat index
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_embeddings(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]):
        """
        Add embeddings and their associated documents to the index

        Args:
            embeddings: numpy array of embeddings
            documents: List of document metadata dictionaries
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")

        if len(embeddings) == 0:
            return

        # Ensure embeddings are in the correct format
        embeddings = np.array(embeddings).astype('float32')

        # Normalize embeddings for L2 distance
        if faiss is not None:
            faiss.normalize_L2(embeddings)

        # Add to index
        self.index.add(embeddings)

        # Store documents
        self.documents.extend(documents)

        # Store embeddings for reference
        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search for similar documents

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return

        Returns:
            List of tuples (distance, document_metadata)
        """
        if self.index.ntotal == 0:
            return []

        # Cap k at actual index size to avoid FAISS sentinel values
        actual_count = self.index.ntotal
        effective_k = min(k, actual_count)
        
        # Ensure query embedding is in correct format
        query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)

        # Normalize query embedding
        if faiss is not None:
            faiss.normalize_L2(query_embedding)

        # Search with effective_k
        distances, indices = self.index.search(query_embedding, effective_k)

        # Return results with document metadata, validating indices
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Validate index is within range
            if idx >= 0 and idx < len(self.documents):
                # Validate distance is finite (not a sentinel value)
                if np.isfinite(dist):
                    results.append((float(dist), self.documents[idx]))
                else:
                    # Skip invalid distance results
                    continue

        return results

    def save(self, file_path: str):
        """
        Save the vector store to disk

        Args:
            file_path: Path to save the index
        """
        save_data = {
            'dimension': self.dimension,
            'index_type': self.index_type,
            'documents': self.documents,
            'embeddings': self.embeddings,
            'ntotal': self.index.ntotal
        }

        with open(file_path, 'wb') as f:
            pickle.dump(save_data, f)

    def load(self, file_path: str):
        """
        Load the vector store from disk

        Args:
            file_path: Path to load the index from
        """
        with open(file_path, 'rb') as f:
            load_data = pickle.load(f)

        self.dimension = load_data['dimension']
        self.index_type = load_data['index_type']
        self.documents = load_data['documents']
        self.embeddings = load_data['embeddings']

        # Reinitialize index
        self._initialize_index()

        # Rebuild index
        if self.embeddings is not None and len(self.embeddings) > 0:
            embeddings = np.array(self.embeddings).astype('float32')
            if faiss is not None:
                faiss.normalize_L2(embeddings)
            self.index.add(embeddings)

    def get_size(self) -> int:
        """
        Get the number of documents in the store

        Returns:
            Number of documents
        """
        return self.index.ntotal

    def is_empty(self) -> bool:
        """
        Check if the vector store is empty

        Returns:
            True if empty, False otherwise
        """
        return self.index.ntotal == 0
