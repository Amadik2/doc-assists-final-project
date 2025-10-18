"""Embedding generation utilities for Doc Assist."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List


class Embedder:
    """
    Text embedding generator using Sentence Transformers.
    """
    
    def __init__(self, model_name="all-MiniLM-L6-v2", device=None):
        """
        Initialize the embedder with a specific model.
        
        Args:
            model_name: Name of the sentence-transformer model to use
            device: Device to use for computation (None for auto-detection)
        """
        self.model = SentenceTransformer(model_name, device=device)
        
    def encode(self, texts: List[str], batch_size=64) -> np.ndarray:
        """
        Encode a list of texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            batch_size: Batch size for encoding
            
        Returns:
            NumPy array of embeddings
        """
        return self.model.encode(
            texts, 
            show_progress_bar=True, 
            batch_size=batch_size,
            normalize_embeddings=True
        )
