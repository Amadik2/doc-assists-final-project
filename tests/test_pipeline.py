"""Tests for the RAG pipeline."""

import os
import pytest
from unittest.mock import MagicMock, patch
from src.rag.pipeline import RAGPipeline


@pytest.mark.skipif(
    not os.path.exists("indices/docassist.faiss") or not os.path.exists("indices/docassist.mapping.json"),
    reason="Index files not found"
)
@pytest.mark.slow
def test_end_to_end():
    """End-to-end test for the RAG pipeline."""
    # Import here to avoid loading models during test collection
    from src.retriever.retriever import Retriever
    from src.generator.generator import CodeGenerator
    
    r = Retriever("indices/docassist.faiss", "indices/docassist.mapping.json")
    g = CodeGenerator()
    rag = RAGPipeline(r, g)
    
    out = rag.answer("read csv with pandas and handle missing values")
    
    # Check output structure
    assert "answer" in out
    assert "flags" in out and isinstance(out["flags"], list)
    assert "citations" in out
    assert "contexts" in out


def test_pipeline_with_mocks():
    """Test pipeline with mock components."""
    # Create mock retriever
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = [
        ({"text": "Sample context 1"}, 0.9),
        ({"text": "Sample context 2"}, 0.8)
    ]
    
    # Create mock generator
    mock_generator = MagicMock()
    mock_generator.generate.return_value = "This is a sample answer."
    
    # Create pipeline with mocks
    rag = RAGPipeline(mock_retriever, mock_generator)
    
    # Test answer method
    result = rag.answer("test query")
    
    # Check that the retriever and generator were called
    mock_retriever.search.assert_called_once()
    mock_generator.generate.assert_called_once()
    
    # Check output structure
    assert "answer" in result
    assert result["answer"] == "This is a sample answer."
