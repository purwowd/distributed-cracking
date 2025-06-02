#!/usr/bin/env python
"""
Main entry point for running the web interface directly with:
python -m cmd.web
"""

import os
import sys
import uvicorn
import argparse

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    """Run the web interface server"""
    parser = argparse.ArgumentParser(description='Distributed Hashcat Cracking - Web Interface')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind the server to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080,
                        help='Port to bind the server to (default: 8080)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    print(f"Starting Distributed Hashcat Cracking Web Interface on {args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "cmd.web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
