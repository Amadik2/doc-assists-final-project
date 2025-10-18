"""RAG pipeline for Doc Assist."""

from typing import Dict
from src.retriever.retriever import Retriever
from src.generator.generator import CodeGenerator
from src.rag.verify import verify_answer


class RAGPipeline:
    """
    RAG pipeline that orchestrates retrieval, generation, and verification.
    """
    
    def __init__(self, retriever: Retriever, generator: CodeGenerator):
        """
        Initialize the RAG pipeline.
        
        Args:
            retriever: Retriever component
            generator: Generator component
        """
        self.retriever = retriever
        self.generator = generator

    def answer(self, query: str, top_k=5) -> Dict:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer, citations, flags, and contexts
        """
        # Retrieve relevant documents
        hits = self.retriever.search(query, top_k=top_k)
        
        # Extract context texts
        contexts = [h[0]["text"] for h in hits]
        
        # Generate draft answer
        draft = self.generator.generate(query, contexts)
        
        # Verify the answer
        checked = verify_answer(draft, contexts)
        
        # Return the result
        return {
            "answer": checked["answer"],
            "citations": checked["citations"],
            "flags": checked["flags"],
            "contexts": hits
        }
