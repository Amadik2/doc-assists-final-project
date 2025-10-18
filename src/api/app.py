"""FastAPI application for Doc Assist."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from src.retriever.retriever import Retriever
from src.generator.generator import CodeGenerator
from src.rag.pipeline import RAGPipeline


# Initialize FastAPI app
app = FastAPI(
    title="Doc Assist API",
    description="API for Doc Assist, a domain-specific question-answering system for software documentation",
    version="1.0.0"
)

# Define request model
class Question(BaseModel):
    question: str
    top_k: int = 5


# Initialize components directly
print("Initializing Doc Assist components...")

# Check if index files exist
index_path = os.environ.get("FAISS_INDEX_PATH", "indices/sample_docassist.faiss")
mapping_path = os.environ.get("MAPPING_PATH", "indices/sample_docassist.mapping.json")

if not os.path.exists(index_path) or not os.path.exists(mapping_path):
    print(f"Warning: Index files not found at {index_path} or {mapping_path}")
    print("API will fail until index is built. Run 'python scripts/build_index.py' first.")
    retriever = None
    generator = None
    rag = None
else:
    try:
        print(f"Initializing retriever with {index_path} and {mapping_path}...")
        retriever = Retriever(index_path, mapping_path)
        print("Retriever initialized successfully")
        
        print("Initializing generator...")
        generator = CodeGenerator()
        print("Generator initialized successfully")
        
        print("Initializing RAG pipeline...")
        rag = RAGPipeline(retriever, generator)
        print("Doc Assist components initialized successfully")
    except Exception as e:
        import traceback
        print(f"Error initializing components: {e}")
        print("Traceback:")
        traceback.print_exc()
        retriever = None
        generator = None
        rag = None


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to Doc Assist API", "status": "active"}


@app.post("/answer")
def answer(q: Question):
    """
    Answer a question using the RAG pipeline.
    
    Args:
        q: Question model with question and top_k fields
        
    Returns:
        Dictionary with answer, citations, flags, and contexts
    """
    if rag is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Record start time
    start_time = time.time()
    
    # Get answer
    try:
        out = rag.answer(q.question, top_k=q.top_k)
        
        # Add timing information
        out["timing"] = {
            "total_seconds": time.time() - start_time
        }
        
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    if rag is None:
        return {"status": "initializing"}
    return {"status": "healthy"}
