"""FAISS index building utilities for Doc Assist."""

import faiss
import numpy as np
import json
from pathlib import Path


def build_faiss(emb: np.ndarray, out_path: str, ivf_centroids=4096, pq_m=16, use_ivfpq=True):
    """
    Build a FAISS index from embeddings.
    
    Args:
        emb: NumPy array of embeddings
        out_path: Path to save the index
        ivf_centroids: Number of centroids for IVF
        pq_m: Number of subquantizers for PQ
        use_ivfpq: Whether to use IVFPQ (faster but less accurate) or FlatIP (exact but slower)
        
    Returns:
        Path to the saved index
    """
    d = emb.shape[1]  # Embedding dimension
    
    if use_ivfpq:
        # Create quantizer
        quantizer = faiss.IndexFlatIP(d)
        # Create IVFPQ index
        index = faiss.IndexIVFPQ(quantizer, d, ivf_centroids, pq_m, 8)  # 8-bit codes
        # Train the index
        index.train(emb)
        # Add vectors to the index
        index.add(emb)
    else:
        # Create FlatIP index (exact search)
        index = faiss.IndexFlatIP(d)
        # Add vectors to the index
        index.add(emb)
    
    # Save the index to disk
    faiss.write_index(index, out_path)
    return out_path


def save_mapping(objs, out_path: str):
    """
    Save mapping from index positions to document objects.
    
    Args:
        objs: List of document objects
        out_path: Path to save the mapping
        
    Returns:
        None
    """
    Path(out_path).write_text(json.dumps(objs, ensure_ascii=False))
