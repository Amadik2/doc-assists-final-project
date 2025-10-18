#!/usr/bin/env python
"""Script to run the entire Doc Assist pipeline on a sample query."""

import argparse
import os
import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retriever.retriever import Retriever
from src.generator.generator import CodeGenerator
from src.rag.pipeline import RAGPipeline


def main(args):
    """
    Run the Doc Assist pipeline on a sample query.
    
    Args:
        args: Command line arguments
    """
    # Check if index exists
    if not os.path.exists(args.index_path) or not os.path.exists(args.mapping_path):
        print(f"Index not found at {args.index_path} or {args.mapping_path}")
        print("Building index first...")
        
        # Import build_index here to avoid circular imports
        from scripts.build_index import main as build_index_main
        
        # Load config
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f)
        
        # Build index
        build_index_main(cfg)
    
    # Initialize components
    print(f"Initializing retriever with {args.index_path}...")
    retriever = Retriever(args.index_path, args.mapping_path)
    
    print(f"Initializing generator with {args.model}...")
    generator = CodeGenerator(args.model)
    
    print("Initializing RAG pipeline...")
    rag = RAGPipeline(retriever, generator)
    
    # Run pipeline
    print(f"\nProcessing query: {args.query}")
    result = rag.answer(args.query, top_k=args.top_k)
    
    # Print results
    print("\n" + "="*50)
    print("ANSWER:")
    print("="*50)
    print(result["answer"])
    
    print("\n" + "="*50)
    print("RETRIEVED CONTEXTS:")
    print("="*50)
    for i, (ctx, score) in enumerate([(x[0]["text"], x[1]) for x in result["contexts"]]):
        print(f"\nContext {i+1} (score={score:.3f}):")
        print("-"*30)
        print(ctx)
    
    if result["flags"]:
        print("\n" + "="*50)
        print("FLAGS:")
        print("="*50)
        for flag in result["flags"]:
            print(f"- {flag}")
    
    if result["citations"]:
        print("\n" + "="*50)
        print("CITATIONS:")
        print("="*50)
        for citation in result["citations"]:
            print(f"- {citation}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Doc Assist pipeline")
    parser.add_argument("--query", default="How to sort a list in Python?", help="Query to process")
    parser.add_argument("--top-k", type=int, default=3, help="Number of documents to retrieve")
    parser.add_argument("--index-path", default="indices/docassist.faiss", help="Path to FAISS index")
    parser.add_argument("--mapping-path", default="indices/docassist.mapping.json", help="Path to document mapping")
    parser.add_argument("--model", default="Salesforce/codet5-base", help="Generator model name")
    parser.add_argument("--config", default="configs/build_index.yaml", help="Path to config file")
    
    args = parser.parse_args()
    main(args)
