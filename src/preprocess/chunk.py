"""Document chunking utilities for Doc Assist."""

from typing import List, Dict
from .normalize import clean_question, normalize_code


def chunk_document(text: str, max_tokens: int = 512) -> List[str]:
    """
    Split a document into chunks of approximately max_tokens.
    
    Args:
        text: Document text
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of document chunks
    """
    # Simple paragraph chunking; replace with token-aware logic if tokenizer available
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) < max_tokens:
            buf = f"{buf}\n\n{p}" if buf else p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks


def build_corpus(records: List[Dict]) -> List[Dict]:
    """
    Build a corpus from records with question and code fields.
    
    Args:
        records: List of dictionaries with question and code fields
        
    Returns:
        List of dictionaries with doc_id, text, and meta fields
    """
    corpus = []
    for i, r in enumerate(records):
        q = clean_question(r["question"])
        c = normalize_code(r.get("code", ""))
        unit = f"Question: {q}\nCode:\n{c}"
        corpus.append({"doc_id": i, "text": unit, "meta": r})
    return corpus
