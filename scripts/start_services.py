#!/usr/bin/env python
"""Script to start both the API and UI services."""

import argparse
import subprocess
import sys
import time
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def start_api(host, port, workers):
    """
    Start the API service.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        workers: Number of worker processes
    
    Returns:
        Subprocess object
    """
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.app:app",
        "--host", host,
        "--port", str(port),
        "--workers", str(workers)
    ]
    
    print(f"Starting API on {host}:{port} with {workers} workers...")
    return subprocess.Popen(cmd, cwd=project_root)


def start_ui(host, port, api_url):
    """
    Start the UI service.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        api_url: URL of the API service
    
    Returns:
        Subprocess object
    """
    cmd = [
        sys.executable, "-m", "streamlit",
        "run", "src/ui/app.py",
        "--server.address", host,
        "--server.port", str(port)
    ]
    
    env = os.environ.copy()
    env["API_URL"] = api_url
    
    print(f"Starting UI on {host}:{port} with API URL {api_url}...")
    return subprocess.Popen(cmd, cwd=project_root, env=env)


def main(args):
    """
    Start both services.
    
    Args:
        args: Command line arguments
    """
    # Start API
    api_process = start_api(args.api_host, args.api_port, args.workers)
    
    # Wait for API to start
    print("Waiting for API to start...")
    time.sleep(3)
    
    # Start UI
    api_url = f"http://{args.api_host}:{args.api_port}"
    ui_process = start_ui(args.ui_host, args.ui_port, api_url)
    
    print("\nServices started!")
    print(f"API: http://{args.api_host}:{args.api_port}")
    print(f"UI: http://{args.ui_host}:{args.ui_port}")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for processes to finish
        api_process.wait()
        ui_process.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        ui_process.terminate()
        api_process.terminate()
        print("Services stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Doc Assist services")
    parser.add_argument("--api-host", default="127.0.0.1", help="API host")
    parser.add_argument("--api-port", type=int, default=8080, help="API port")
    parser.add_argument("--ui-host", default="127.0.0.1", help="UI host")
    parser.add_argument("--ui-port", type=int, default=8501, help="UI port")
    parser.add_argument("--workers", type=int, default=1, help="Number of API worker processes")
    
    args = parser.parse_args()
    main(args)
