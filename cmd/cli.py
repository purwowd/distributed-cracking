#!/usr/bin/env python
import argparse
import asyncio
import json
import sys
import requests
from typing import Dict, Any, List, Optional

SERVER_URL = "http://localhost:8000"


class DistributedCrackingCLI:
    """Command-line interface for the Distributed Hashcat Cracking System"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
    
    def run(self):
        """Run the CLI"""
        parser = argparse.ArgumentParser(
            description="Distributed Hashcat Cracking System CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Create a new task
  python -m cmd.cli task create --name "Test Task" --hash-type md5 --hashes hashes.txt --wordlist /path/to/wordlist.txt
  
  # List all tasks
  python -m cmd.cli task list
  
  # Get task details
  python -m cmd.cli task get <task_id>
  
  # List all agents
  python -m cmd.cli agent list
  
  # Register a new agent
  python -m cmd.cli agent register --name "GPU Server 1" --hostname "gpu01" --ip "192.168.1.10"
  
  # List all results
  python -m cmd.cli result list
"""
        )
        
        subparsers = parser.add_subparsers(dest="entity", help="Entity to manage")
        
        # Task commands
        task_parser = subparsers.add_parser("task", help="Manage tasks")
        task_subparsers = task_parser.add_subparsers(dest="action", help="Action to perform")
        
        # Task list
        task_list_parser = task_subparsers.add_parser("list", help="List all tasks")
        task_list_parser.add_argument("--status", help="Filter by status")
        task_list_parser.add_argument("--skip", type=int, default=0, help="Number of items to skip")
        task_list_parser.add_argument("--limit", type=int, default=100, help="Number of items to return")
        
        # Task get
        task_get_parser = task_subparsers.add_parser("get", help="Get task details")
        task_get_parser.add_argument("id", help="Task ID")
        
        # Task create
        task_create_parser = task_subparsers.add_parser("create", help="Create a new task")
        task_create_parser.add_argument("--name", required=True, help="Task name")
        task_create_parser.add_argument("--description", help="Task description")
        task_create_parser.add_argument("--hash-type", required=True, choices=["md5", "sha1", "sha256", "sha512", "ntlm", "wpa", "bcrypt", "custom"], help="Hash type")
        task_create_parser.add_argument("--hash-type-id", type=int, help="Hashcat hash type ID")
        task_create_parser.add_argument("--hashes", required=True, help="File containing hashes (one per line)")
        task_create_parser.add_argument("--wordlist", help="Path to wordlist")
        task_create_parser.add_argument("--rule", help="Path to rule file")
        task_create_parser.add_argument("--mask", help="Mask for brute force")
        task_create_parser.add_argument("--attack-mode", type=int, default=0, help="Attack mode (0=dict, 3=mask, etc.)")
        task_create_parser.add_argument("--priority", type=int, default=1, help="Task priority")
        
        # Task cancel
        task_cancel_parser = task_subparsers.add_parser("cancel", help="Cancel a task")
        task_cancel_parser.add_argument("id", help="Task ID")
        
        # Task delete
        task_delete_parser = task_subparsers.add_parser("delete", help="Delete a task")
        task_delete_parser.add_argument("id", help="Task ID")
        
        # Agent commands
        agent_parser = subparsers.add_parser("agent", help="Manage agents")
        agent_subparsers = agent_parser.add_subparsers(dest="action", help="Action to perform")
        
        # Agent list
        agent_list_parser = agent_subparsers.add_parser("list", help="List all agents")
        agent_list_parser.add_argument("--status", help="Filter by status")
        agent_list_parser.add_argument("--skip", type=int, default=0, help="Number of items to skip")
        agent_list_parser.add_argument("--limit", type=int, default=100, help="Number of items to return")
        
        # Agent get
        agent_get_parser = agent_subparsers.add_parser("get", help="Get agent details")
        agent_get_parser.add_argument("id", help="Agent ID")
        
        # Agent register
        agent_register_parser = agent_subparsers.add_parser("register", help="Register a new agent")
        agent_register_parser.add_argument("--name", required=True, help="Agent name")
        agent_register_parser.add_argument("--hostname", required=True, help="Agent hostname")
        agent_register_parser.add_argument("--ip", required=True, help="Agent IP address")
        
        # Agent delete
        agent_delete_parser = agent_subparsers.add_parser("delete", help="Delete an agent")
        agent_delete_parser.add_argument("id", help="Agent ID")
        
        # Result commands
        result_parser = subparsers.add_parser("result", help="Manage results")
        result_subparsers = result_parser.add_subparsers(dest="action", help="Action to perform")
        
        # Result list
        result_list_parser = result_subparsers.add_parser("list", help="List all results")
        result_list_parser.add_argument("--task-id", help="Filter by task ID")
        result_list_parser.add_argument("--skip", type=int, default=0, help="Number of items to skip")
        result_list_parser.add_argument("--limit", type=int, default=100, help="Number of items to return")
        
        # Result get
        result_get_parser = result_subparsers.add_parser("get", help="Get result details")
        result_get_parser.add_argument("id", help="Result ID")
        
        # Result get by hash
        result_get_hash_parser = result_subparsers.add_parser("get-by-hash", help="Get result by hash")
        result_get_hash_parser.add_argument("hash", help="Hash value")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Handle commands
        if not args.entity:
            parser.print_help()
            return
        
        if args.entity == "task":
            self.handle_task_commands(args)
        elif args.entity == "agent":
            self.handle_agent_commands(args)
        elif args.entity == "result":
            self.handle_result_commands(args)
    
    def handle_task_commands(self, args):
        """Handle task commands"""
        if args.action == "list":
            params = {}
            if args.status:
                params["status"] = args.status
            if args.skip:
                params["skip"] = args.skip
            if args.limit:
                params["limit"] = args.limit
            
            response = requests.get(f"{self.server_url}/tasks", params=params)
            self.handle_response(response)
        
        elif args.action == "get":
            response = requests.get(f"{self.server_url}/tasks/{args.id}")
            self.handle_response(response)
        
        elif args.action == "create":
            # Read hashes from file
            try:
                with open(args.hashes, "r") as f:
                    hashes = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error reading hashes file: {e}")
                return
            
            data = {
                "name": args.name,
                "description": args.description or "",
                "hash_type": args.hash_type,
                "hash_type_id": args.hash_type_id,
                "hashes": hashes,
                "wordlist_path": args.wordlist,
                "rule_path": args.rule,
                "mask": args.mask,
                "attack_mode": args.attack_mode,
                "priority": args.priority
            }
            
            response = requests.post(f"{self.server_url}/tasks", json=data)
            self.handle_response(response)
        
        elif args.action == "cancel":
            response = requests.post(f"{self.server_url}/tasks/{args.id}/cancel")
            self.handle_response(response)
        
        elif args.action == "delete":
            response = requests.delete(f"{self.server_url}/tasks/{args.id}")
            self.handle_response(response)
        
        else:
            print("Unknown task action")
    
    def handle_agent_commands(self, args):
        """Handle agent commands"""
        if args.action == "list":
            params = {}
            if args.status:
                params["status"] = args.status
            if args.skip:
                params["skip"] = args.skip
            if args.limit:
                params["limit"] = args.limit
            
            response = requests.get(f"{self.server_url}/agents", params=params)
            self.handle_response(response)
        
        elif args.action == "get":
            response = requests.get(f"{self.server_url}/agents/{args.id}")
            self.handle_response(response)
        
        elif args.action == "register":
            data = {
                "name": args.name,
                "hostname": args.hostname,
                "ip_address": args.ip
            }
            
            response = requests.post(f"{self.server_url}/agents", json=data)
            self.handle_response(response)
        
        elif args.action == "delete":
            response = requests.delete(f"{self.server_url}/agents/{args.id}")
            self.handle_response(response)
        
        else:
            print("Unknown agent action")
    
    def handle_result_commands(self, args):
        """Handle result commands"""
        if args.action == "list":
            params = {}
            if args.task_id:
                params["task_id"] = args.task_id
            if args.skip:
                params["skip"] = args.skip
            if args.limit:
                params["limit"] = args.limit
            
            response = requests.get(f"{self.server_url}/results", params=params)
            self.handle_response(response)
        
        elif args.action == "get":
            response = requests.get(f"{self.server_url}/results/{args.id}")
            self.handle_response(response)
        
        elif args.action == "get-by-hash":
            response = requests.get(f"{self.server_url}/results/hash/{args.hash}")
            self.handle_response(response)
        
        else:
            print("Unknown result action")
    
    def handle_response(self, response):
        """Handle API response"""
        try:
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2))
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error processing response: {e}")


def main():
    """Main entry point"""
    cli = DistributedCrackingCLI(SERVER_URL)
    cli.run()


if __name__ == "__main__":
    main()
