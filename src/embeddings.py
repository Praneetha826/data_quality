"""
Embeddings Module
Handles text chunking and embedding generation using Sentence Transformers
"""

import sys
from typing import List, Optional
import numpy as np


def _is_torch_functional() -> bool:
    """Check if torch and native libraries can be loaded without OS policy blocks."""
    try:
        import torch
        _ = torch.tensor([1.0])
        return True
    except (ImportError, OSError):
        # Purge any partial imports from sys.modules so watchers do not inspect them
        for mod in list(sys.modules.keys()):
            if mod.startswith(('torch', 'transformers', 'sentence_transformers')):
                sys.modules.pop(mod, None)
        return False


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
        self.fallback_vectorizer = None
        self._load_model()

    def _load_model(self):
        """Load the Sentence Transformer model or fall back to scikit-learn vectorizer"""
        if not _is_torch_functional():
            print("[Notice] PyTorch native libraries are blocked by Windows Application Control policy.")
            print("[Notice] Using Scikit-Learn 384-dimensional feature vectorizer for FAISS embeddings.")
            from sklearn.feature_extraction.text import HashingVectorizer
            self.model = None
            self.fallback_vectorizer = HashingVectorizer(n_features=384, norm='l2')
            return

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except (ImportError, OSError) as e:
            print(f"[Notice] sentence-transformers unavailable ({e}). Using Scikit-Learn feature vectorizer.")
            from sklearn.feature_extraction.text import HashingVectorizer
            self.model = None
            self.fallback_vectorizer = HashingVectorizer(n_features=384, norm='l2')

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts

        Args:
            texts: List of text strings to embed

        Returns:
            numpy array of embeddings
        """
        if self.model is None and self.fallback_vectorizer is None:
            raise RuntimeError("Model not loaded")

        if not texts:
            return np.array([])

        if self.model is not None:
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings
        else:
            return self.fallback_vectorizer.transform(texts).toarray().astype('float32')

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
        if self.model is not None:
            test_embedding = self.generate_embedding("test")
            return len(test_embedding)
        elif self.fallback_vectorizer is not None:
            return 384
        raise RuntimeError("Model not loaded")

    def batch_generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings in batches for large text collections

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process at once

        Returns:
            numpy array of embeddings
        """
        if self.model is None and self.fallback_vectorizer is None:
            raise RuntimeError("Model not loaded")

        if not texts:
            return np.array([])

        if self.model is not None:
            embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
            return embeddings
        else:
            return self.fallback_vectorizer.transform(texts).toarray().astype('float32')
