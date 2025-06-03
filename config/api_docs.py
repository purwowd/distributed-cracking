"""
API documentation configuration for the distributed cracking system.
"""

# Main API description
API_DESCRIPTION = """
# Distributed Hashcat Cracking System API

This API provides endpoints for managing a distributed password cracking system using Hashcat.

## Features

* Create and manage cracking tasks
* Register and monitor agent nodes
* Track cracking results
* Automatic task assignment to available agents
* Real-time status updates

## Authentication

Most endpoints require authentication using JWT tokens. To authenticate:

1. Use the `/token` endpoint with your username and password
2. Include the token in the Authorization header for subsequent requests

## Agent API Keys

Agent nodes authenticate using API keys. Each agent must be registered with a unique API key.
"""

# Tags metadata for API documentation
TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "Operations for user authentication and authorization",
    },
    {
        "name": "Tasks",
        "description": "Operations for managing password cracking tasks",
    },
    {
        "name": "Agents",
        "description": "Operations for managing agent nodes",
    },
    {
        "name": "Results",
        "description": "Operations for accessing cracking results",
    },
]

# Examples for request bodies
TASK_EXAMPLES = {
    "normal": {
        "summary": "Normal dictionary attack",
        "description": "A standard dictionary attack against MD5 hashes",
        "value": {
            "name": "Web Passwords MD5",
            "attack_mode": 0,
            "hash_type": "MD5",
            "hash_file": "hashes.txt",
            "wordlist": "rockyou.txt",
            "rules": ["best64.rule"],
            "priority": 1
        }
    },
    "advanced": {
        "summary": "Advanced mask attack",
        "description": "A mask attack with custom character sets",
        "value": {
            "name": "WiFi WPA Passwords",
            "attack_mode": 3,
            "hash_type": "WPA",
            "hash_file": "wifi_captures.hccapx",
            "mask": "?d?d?d?d?d?d?d?d",
            "custom_charset_1": "?l?u?d",
            "custom_charset_2": "?l?u",
            "custom_charset_3": "?d?s",
            "custom_charset_4": "?l?d",
            "priority": 2
        }
    }
}

AGENT_EXAMPLES = {
    "standard": {
        "summary": "Standard agent registration",
        "description": "Register a standard agent with one GPU",
        "value": {
            "name": "Agent-01",
            "hostname": "worker-01.local",
            "api_key": "agent_api_key_123",
            "platform": "Linux",
            "devices": [
                {
                    "device_id": 1,
                    "name": "NVIDIA GeForce RTX 3080",
                    "type": "GPU",
                    "memory": 10240
                }
            ]
        }
    },
    "multi_gpu": {
        "summary": "Multi-GPU agent registration",
        "description": "Register an agent with multiple GPUs",
        "value": {
            "name": "Agent-02",
            "hostname": "worker-02.local",
            "api_key": "agent_api_key_456",
            "platform": "Windows",
            "devices": [
                {
                    "device_id": 1,
                    "name": "NVIDIA GeForce RTX 3090",
                    "type": "GPU",
                    "memory": 24576
                },
                {
                    "device_id": 2,
                    "name": "NVIDIA GeForce RTX 3080",
                    "type": "GPU",
                    "memory": 10240
                }
            ]
        }
    }
}
