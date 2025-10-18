#!/usr/bin/env python
"""Main entry point for Doc Assist."""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Parse arguments and run the appropriate command."""
    parser = argparse.ArgumentParser(description="Doc Assist - Documentation QA System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Build the search index")
    index_parser.add_argument("--config", default="configs/build_index.yaml", help="Path to config file")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    serve_parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    serve_parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    # UI command
    ui_parser = subparsers.add_parser("ui", help="Start the UI server")
    ui_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    ui_parser.add_argument("--port", type=int, default=8501, help="Port to bind to")
    ui_parser.add_argument("--api-url", default="http://127.0.0.1:8080", help="API URL")
    
    # Start command (both API and UI)
    start_parser = subparsers.add_parser("start", help="Start both API and UI servers")
    start_parser.add_argument("--api-host", default="127.0.0.1", help="API host")
    start_parser.add_argument("--api-port", type=int, default=8080, help="API port")
    start_parser.add_argument("--ui-host", default="127.0.0.1", help="UI host")
    start_parser.add_argument("--ui-port", type=int, default=8501, help="UI port")
    start_parser.add_argument("--workers", type=int, default=1, help="Number of API worker processes")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Run a single query")
    query_parser.add_argument("query", help="Query to process")
    query_parser.add_argument("--top-k", type=int, default=3, help="Number of documents to retrieve")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate the system")
    eval_parser.add_argument("--queries-file", help="Path to JSON file with evaluation queries")
    eval_parser.add_argument("--output", default="evaluation_results.json", help="Path to save evaluation results")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "index":
        from scripts.build_index import main as build_index_main
        import yaml
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f)
        build_index_main(cfg)
    
    elif args.command == "serve":
        os.environ["HOST"] = args.host
        os.environ["PORT"] = str(args.port)
        from scripts.start_services import start_api
        api_process = start_api(args.host, args.port, args.workers)
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\nStopping API server...")
            api_process.terminate()
    
    elif args.command == "ui":
        os.environ["API_URL"] = args.api_url
        from scripts.start_services import start_ui
        ui_process = start_ui(args.host, args.port, args.api_url)
        try:
            ui_process.wait()
        except KeyboardInterrupt:
            print("\nStopping UI server...")
            ui_process.terminate()
    
    elif args.command == "start":
        from scripts.start_services import main as start_services_main
        start_services_main(args)
    
    elif args.command == "query":
        from scripts.run_pipeline import main as run_pipeline_main
        args.config = "configs/build_index.yaml"
        args.index_path = "indices/sample_docassist.faiss"
        args.mapping_path = "indices/sample_docassist.mapping.json"
        args.model = "Salesforce/codet5-base"
        run_pipeline_main(args)
    
    elif args.command == "evaluate":
        from scripts.evaluate import main as evaluate_main
        args.eval_retrieval = True
        args.eval_generation = True
        args.eval_pipeline = True
        evaluate_main(args)
    
    elif args.command == "test":
        import pytest
        sys.exit(pytest.main(["-v" if args.verbose else "-q"]))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
