"""Text and code normalization utilities for Doc Assist."""

import re
import ast
import textwrap
import spacy
from nltk.corpus import stopwords

# Initialize spaCy model
NLP = spacy.load("en_core_web_sm", disable=["ner"])

# Domain-specific stopwords
STOP = set(stopwords.words("english")) | {
    "python", "pandas", "numpy", "matplotlib", "function", "class", "code"
}

# Code symbols to preserve during cleaning
CODE_SYMS = set(list("[]{}().,:=+-/*<>!@#%^&|~"))


def clean_question(q: str) -> str:
    """
    Clean and normalize a question text.
    
    Args:
        q: Question text
        
    Returns:
        Cleaned question text
    """
    try:
        if not isinstance(q, str):
            print(f"Warning: Expected string for question, got {type(q)}")
            if q is None:
                return ""
            q = str(q)
        
        doc = NLP(q)
        toks = []
        for t in doc:
            if t.is_space:
                continue
            if t.is_punct and t.text not in CODE_SYMS:
                continue
            s = t.text.lower()
            if s in STOP:
                continue
            toks.append(s)
        return " ".join(toks)
    except Exception as e:
        print(f"Error cleaning question: {e}")
        return q  # Return original text on error


def normalize_code(src: str) -> str:
    """
    Normalize code by removing extra whitespace and standardizing format.
    
    Args:
        src: Source code string
        
    Returns:
        Normalized code string
    """
    try:
        if not isinstance(src, str):
            print(f"Warning: Expected string for code, got {type(src)}")
            if src is None:
                return ""
            src = str(src)
        
        # Try to parse as valid Python code
        try:
            tree = ast.parse(src)
            # Pretty-print normalized format
            re_src = textwrap.dedent(src).strip()
            return re_src
        except SyntaxError:
            # If parsing fails, just dedent and strip
            return textwrap.dedent(src).strip()
    except Exception as e:
        print(f"Error normalizing code: {e}")
        return src  # Return original text on error
