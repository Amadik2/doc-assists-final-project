"""Tests for the retriever module."""

import os
import pytest
from src.retriever.retriever import Retriever


@pytest.mark.skipif(
    not os.path.exists("indices/docassist.faiss") or not os.path.exists("indices/docassist.mapping.json"),
    reason="Index files not found"
)
def test_retriever_basic():
    """Test basic retriever functionality."""
    r = Retriever("indices/docassist.faiss", "indices/docassist.mapping.json")
    out = r.search("pandas groupby sum", top_k=3)
    
    # Check output structure
    assert len(out) <= 3
    if len(out) > 0:
        assert isinstance(out[0][0]["text"], str)
        assert isinstance(out[0][1], float)


@pytest.mark.skipif(
    not os.path.exists("indices/docassist.faiss") or not os.path.exists("indices/docassist.mapping.json"),
    reason="Index files not found"
)
def test_retriever_lexical_boost():
    """Test lexical boost functionality."""
    r = Retriever("indices/docassist.faiss", "indices/docassist.mapping.json")
    
    # Test internal method
    boost = r._lexical_boost("pandas dataframe", "This is a pandas dataframe example")
    assert boost > 1.0
    
    # Test with no overlap
    boost = r._lexical_boost("numpy array", "This is a pandas dataframe example")
    assert boost == 1.0
