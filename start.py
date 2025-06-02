#!/usr/bin/env python
"""
Startup script for the Distributed Hashcat Cracking system.
This script provides a convenient way to start all components of the system.
"""

import os
import sys
import argparse
import subprocess
import time
import signal
import atexit

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Process tracking
processes = []

def cleanup():
    """Kill all child processes on exit"""
    for process in processes:
        try:
            if process.poll() is None:
                process.terminate()
                print(f"Terminated process: {process.args}")
        except Exception as e:
            print(f"Error terminating process: {e}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down all components...")
    cleanup()
    sys.exit(0)

def start_server(args):
    """Start the central server"""
    print("Starting central server...")
    cmd = [sys.executable, "-m", "cmd.server"]
    if args.debug:
        cmd.append("--debug")
    
    server_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if not args.verbose else None,
        stderr=subprocess.PIPE if not args.verbose else None,
        universal_newlines=True
    )
    processes.append(server_process)
    print(f"Central server started (PID: {server_process.pid})")
    return server_process

def start_web_interface(args):
    """Start the web interface"""
    print("Starting web interface...")
    cmd = [sys.executable, "-m", "cmd.web", "--port", str(args.web_port)]
    if args.debug:
        cmd.append("--reload")
    
    web_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if not args.verbose else None,
        stderr=subprocess.PIPE if not args.verbose else None,
        universal_newlines=True
    )
    processes.append(web_process)
    print(f"Web interface started at http://localhost:{args.web_port} (PID: {web_process.pid})")
    return web_process

def start_agent(agent_id, args):
    """Start an agent with the given ID"""
    print(f"Starting agent {agent_id}...")
    cmd = [sys.executable, "-m", "cmd.agent", "--id", f"agent-{agent_id}"]
    if args.debug:
        cmd.append("--debug")
    
    agent_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if not args.verbose else None,
        stderr=subprocess.PIPE if not args.verbose else None,
        universal_newlines=True
    )
    processes.append(agent_process)
    print(f"Agent {agent_id} started (PID: {agent_process.pid})")
    return agent_process

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Start Distributed Hashcat Cracking system')
    parser.add_argument('--server-only', action='store_true',
                        help='Start only the central server')
    parser.add_argument('--web-only', action='store_true',
                        help='Start only the web interface')
    parser.add_argument('--agents-only', action='store_true',
                        help='Start only the agent(s)')
    parser.add_argument('--agents', type=int, default=1,
                        help='Number of agents to start (default: 1)')
    parser.add_argument('--web-port', type=int, default=8080,
                        help='Port for the web interface (default: 8080)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--verbose', action='store_true',
                        help='Show output from all processes')
    
    args = parser.parse_args()
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting Distributed Hashcat Cracking system...")
    print("Press Ctrl+C to stop all components")
    
    # Start components based on arguments
    if args.server_only:
        start_server(args)
    elif args.web_only:
        start_web_interface(args)
    elif args.agents_only:
        for i in range(1, args.agents + 1):
            start_agent(i, args)
    else:
        # Start all components
        server_process = start_server(args)
        time.sleep(2)  # Give the server time to start
        
        web_process = start_web_interface(args)
        time.sleep(1)  # Give the web interface time to start
        
        for i in range(1, args.agents + 1):
            start_agent(i, args)
            time.sleep(0.5)  # Stagger agent starts
    
    print("\nAll components started. Press Ctrl+C to stop.")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
            # Check if any process has exited
            for process in list(processes):
                if process.poll() is not None:
                    print(f"Process exited with code {process.returncode}: {process.args}")
                    processes.remove(process)
            
            if not processes:
                print("All processes have exited. Shutting down.")
                break
    except KeyboardInterrupt:
        print("\nShutting down all components...")

if __name__ == "__main__":
    main()
