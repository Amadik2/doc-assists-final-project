"""Tests for the generator module."""

import pytest
from src.generator.generator import CodeGenerator


def test_format_prompt():
    """Test prompt formatting."""
    gen = CodeGenerator()
    prompt = gen.format_prompt(
        "How to sort a list in Python?",
        ["Use list.sort() method", "Use sorted() function"]
    )
    
    # Check that the prompt contains the query
    assert "How to sort a list in Python?" in prompt
    
    # Check that the prompt contains the contexts
    assert "[1] Use list.sort() method" in prompt
    assert "[2] Use sorted() function" in prompt


@pytest.mark.slow
def test_gen_smoke():
    """Smoke test for generation (marked as slow)."""
    gen = CodeGenerator()
    ans = gen.generate(
        "How to sort list x descending in Python?",
        ["Use list.sort(reverse=True)"]
    )
    
    # Check that we get a non-empty string
    assert isinstance(ans, str)
    assert len(ans) > 0
