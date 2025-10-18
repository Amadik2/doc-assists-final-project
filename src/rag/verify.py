"""Verification utilities for Doc Assist."""

import re

# Regular expression to extract code blocks
CODE_BLOCK = re.compile(r"```(?:python)?\n(.*?)```", re.DOTALL)


def claims_supported(text: str, contexts: list[str]) -> bool:
    """
    Check if claims in the text are supported by the contexts.
    
    Args:
        text: Text to check
        contexts: List of context documents
        
    Returns:
        True if claims are supported, False otherwise
    """
    # Heuristic: key sentences appear in contexts
    for sent in [s.strip() for s in text.split(".") if s.strip()]:
        if any(sent.lower() in c.lower() for c in contexts):
            return True
    return False


def extract_code_blocks(ans: str):
    """
    Extract code blocks from an answer.
    
    Args:
        ans: Answer text
        
    Returns:
        List of code blocks
    """
    return CODE_BLOCK.findall(ans)


def verify_answer(ans: str, contexts: list[str]):
    """
    Verify an answer against contexts.
    
    Args:
        ans: Answer text
        contexts: List of context documents
        
    Returns:
        Dictionary with answer, flags, and citations
    """
    flags, citations = [], []
    
    # Check if claims are supported
    if not claims_supported(ans, contexts):
        flags.append("unsupported_claims")
    
    # Extract and check code blocks
    code_blocks = extract_code_blocks(ans)
    for i, c in enumerate(code_blocks):
        if "import" not in c and "def " not in c and "class " not in c:
            # Not necessarily wrong, but note minimal examples
            citations.append({"block": i, "note": "Minimal snippet"})
    
    return {"answer": ans, "flags": flags, "citations": citations}
