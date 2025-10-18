#!/usr/bin/env python
"""Script to evaluate the Doc Assist system."""

import argparse
import json
import time
import sys
from pathlib import Path
import numpy as np
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retriever.retriever import Retriever
from src.generator.generator import CodeGenerator
from src.rag.pipeline import RAGPipeline


# Sample evaluation queries
SAMPLE_QUERIES = [
    "How to read a CSV file with pandas?",
    "How to sort a list in descending order in Python?",
    "How to create a numpy array?",
    "How to loop through numbers from 1 to 10?",
    "How to convert a string to lowercase?",
    "How to group by and sum in pandas?",
    "How to get the current date in Python?",
    "How to read a file line by line in Python?",
    "How to create a simple function in Python?",
    "How to create a pandas DataFrame from a dictionary?"
]


def evaluate_retrieval(retriever, queries, top_k=5):
    """
    Evaluate retrieval performance.
    
    Args:
        retriever: Retriever instance
        queries: List of queries
        top_k: Number of documents to retrieve
        
    Returns:
        Dictionary of metrics
    """
    results = []
    times = []
    
    for query in tqdm(queries, desc="Evaluating retrieval"):
        start_time = time.time()
        hits = retriever.search(query, top_k=top_k)
        elapsed = time.time() - start_time
        
        results.append(hits)
        times.append(elapsed)
    
    # Calculate metrics
    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)
    
    return {
        "avg_retrieval_time": avg_time,
        "p95_retrieval_time": p95_time,
        "num_queries": len(queries),
        "top_k": top_k
    }


def evaluate_generation(generator, queries, contexts, max_tokens=200):
    """
    Evaluate generation performance.
    
    Args:
        generator: Generator instance
        queries: List of queries
        contexts: List of context lists
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Dictionary of metrics
    """
    results = []
    times = []
    
    for query, ctx in tqdm(zip(queries, contexts), desc="Evaluating generation", total=len(queries)):
        start_time = time.time()
        answer = generator.generate(query, [c[0]["text"] for c in ctx], max_tokens=max_tokens)
        elapsed = time.time() - start_time
        
        results.append(answer)
        times.append(elapsed)
    
    # Calculate metrics
    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)
    avg_length = np.mean([len(r.split()) for r in results])
    
    return {
        "avg_generation_time": avg_time,
        "p95_generation_time": p95_time,
        "avg_answer_length": avg_length,
        "num_queries": len(queries)
    }


def evaluate_pipeline(rag, queries, top_k=5):
    """
    Evaluate the full RAG pipeline.
    
    Args:
        rag: RAG pipeline instance
        queries: List of queries
        top_k: Number of documents to retrieve
        
    Returns:
        Dictionary of metrics
    """
    results = []
    times = []
    
    for query in tqdm(queries, desc="Evaluating pipeline"):
        start_time = time.time()
        result = rag.answer(query, top_k=top_k)
        elapsed = time.time() - start_time
        
        results.append(result)
        times.append(elapsed)
    
    # Calculate metrics
    avg_time = np.mean(times)
    p95_time = np.percentile(times, 95)
    
    # Calculate flag frequency
    all_flags = [flag for r in results for flag in r["flags"]]
    flag_counts = {}
    for flag in all_flags:
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    return {
        "avg_pipeline_time": avg_time,
        "p95_pipeline_time": p95_time,
        "flag_counts": flag_counts,
        "num_queries": len(queries)
    }


def main(args):
    """
    Run the evaluation.
    
    Args:
        args: Command line arguments
    """
    # Load queries
    if args.queries_file:
        with open(args.queries_file, "r") as f:
            queries = json.load(f)
    else:
        queries = SAMPLE_QUERIES
    
    print(f"Evaluating with {len(queries)} queries")
    
    # Initialize components
    print(f"Initializing retriever with {args.index_path}...")
    retriever = Retriever(args.index_path, args.mapping_path)
    
    print(f"Initializing generator with {args.model}...")
    generator = CodeGenerator(args.model)
    
    print("Initializing RAG pipeline...")
    rag = RAGPipeline(retriever, generator)
    
    # Evaluate retrieval
    if args.eval_retrieval:
        print("\nEvaluating retrieval...")
        retrieval_metrics = evaluate_retrieval(retriever, queries, top_k=args.top_k)
        print(f"Retrieval metrics: {json.dumps(retrieval_metrics, indent=2)}")
    
    # Evaluate generation (using retrieval results)
    if args.eval_generation:
        print("\nRetrieving contexts for generation evaluation...")
        contexts = [retriever.search(q, top_k=args.top_k) for q in tqdm(queries)]
        
        print("\nEvaluating generation...")
        generation_metrics = evaluate_generation(generator, queries, contexts, max_tokens=args.max_tokens)
        print(f"Generation metrics: {json.dumps(generation_metrics, indent=2)}")
    
    # Evaluate full pipeline
    if args.eval_pipeline:
        print("\nEvaluating full pipeline...")
        pipeline_metrics = evaluate_pipeline(rag, queries, top_k=args.top_k)
        print(f"Pipeline metrics: {json.dumps(pipeline_metrics, indent=2)}")
    
    # Save results
    if args.output:
        results = {
            "config": vars(args),
            "num_queries": len(queries),
            "retrieval_metrics": retrieval_metrics if args.eval_retrieval else None,
            "generation_metrics": generation_metrics if args.eval_generation else None,
            "pipeline_metrics": pipeline_metrics if args.eval_pipeline else None
        }
        
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Doc Assist system")
    parser.add_argument("--queries-file", help="Path to JSON file with evaluation queries")
    parser.add_argument("--index-path", default="indices/docassist.faiss", help="Path to FAISS index")
    parser.add_argument("--mapping-path", default="indices/docassist.mapping.json", help="Path to document mapping")
    parser.add_argument("--model", default="Salesforce/codet5-base", help="Generator model name")
    parser.add_argument("--top-k", type=int, default=5, help="Number of documents to retrieve")
    parser.add_argument("--max-tokens", type=int, default=200, help="Maximum number of tokens to generate")
    parser.add_argument("--eval-retrieval", action="store_true", help="Evaluate retrieval")
    parser.add_argument("--eval-generation", action="store_true", help="Evaluate generation")
    parser.add_argument("--eval-pipeline", action="store_true", help="Evaluate full pipeline")
    parser.add_argument("--output", help="Path to save evaluation results")
    
    args = parser.parse_args()
    
    # Default to evaluating everything if nothing specified
    if not (args.eval_retrieval or args.eval_generation or args.eval_pipeline):
        args.eval_retrieval = True
        args.eval_generation = True
        args.eval_pipeline = True
    
    main(args)
