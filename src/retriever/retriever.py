"""Retriever module for Doc Assist."""

import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple


class Retriever:
    """
    Retriever component that performs semantic search with hybrid re-ranking.
    """
    
    def __init__(self, faiss_path, mapping_path, model_name="all-MiniLM-L6-v2", device=None):
        """
        Initialize the retriever.
        
        Args:
            faiss_path: Path to the FAISS index
            mapping_path: Path to the document mapping
            model_name: Name of the sentence-transformer model to use
            device: Device to use for computation (None for auto-detection)
        """
        self.index = faiss.read_index(faiss_path)
        with open(mapping_path, 'r') as f:
            self.mapping = json.load(f)
        self.encoder = SentenceTransformer(model_name, device=device)

    def _lexical_boost(self, query: str, doc_text: str) -> float:
        """
        Calculate lexical overlap boost for hybrid ranking.
        
        Args:
            query: Query text
            doc_text: Document text
            
        Returns:
            Boost factor based on term overlap
        """
        # Crude lexical overlap for hybrid weighting
        q_terms = set(query.lower().split())
        d_terms = set(doc_text.lower().split())
        inter = len(q_terms & d_terms)
        return 1.0 + 0.02 * inter  # Tiny boost per term

    def search(self, query: str, top_k=10) -> List[Tuple[Dict, float]]:
        """
        Search for relevant documents given a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        # Encode query
        qv = self.encoder.encode([query], normalize_embeddings=True).astype("float32")
        
        # Oversample then re-rank
        scores, idx = self.index.search(qv, top_k*5)
        
        # Apply hybrid ranking
        cand = []
        for i, s in zip(idx[0], scores[0]):
            if i < 0 or i >= len(self.mapping):  # Skip invalid indices
                continue
            doc = self.mapping[str(i) if isinstance(self.mapping, dict) else i]
            hybrid_s = float(s) * self._lexical_boost(query, doc["text"])
            cand.append((doc, hybrid_s))
        
        # Sort by score and return top_k
        cand = sorted(cand, key=lambda x: x[1], reverse=True)[:top_k]
        return cand
