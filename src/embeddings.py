"""
Embeddings Module
Handles text chunking and embedding generation using Sentence Transformers
"""

from typing import List, Optional
import numpy as np


class EmbeddingGenerator:
    """
    Generates embeddings from text using Sentence Transformers
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator

        Args:
            model_name: Name of the Sentence Transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Sentence Transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for embedding generation. "
                "Install it with: pip install sentence-transformers"
            )

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if not texts:
            return np.array([])

        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Text string to embed

        Returns:
            numpy array embedding
        """
        return self.generate_embeddings([text])[0]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings

        Returns:
            Dimension of the embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        # Generate a test embedding to get dimension
        test_embedding = self.generate_embedding("test")
        return len(test_embedding)

    def batch_generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings in batches for large text collections

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process at once

        Returns:
            numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if not texts:
            return np.array([])

        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        return embeddings
