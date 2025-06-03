"""
Example request and response bodies for API documentation.
"""

# Task examples
TASK_EXAMPLES = {
    "dictionary_attack": {
        "summary": "Dictionary Attack",
        "description": "A standard dictionary attack against MD5 hashes",
        "value": {
            "name": "Web Passwords MD5",
            "description": "Cracking leaked web passwords with dictionary attack",
            "hash_type": "MD5",
            "hash_type_id": 0,
            "attack_mode": 0,
            "priority": 2,
            "hashes": [
                "5f4dcc3b5aa765d61d8327deb882cf99",
                "e10adc3949ba59abbe56e057f20f883e"
            ],
            "wordlist_path": "/wordlists/rockyou.txt",
            "rule_path": "/rules/best64.rule",
            "additional_args": "--force",
            "metadata": {
                "source": "web_leak_2023",
                "owner": "security_team"
            }
        }
    },
    "mask_attack": {
        "summary": "Mask Attack",
        "description": "A mask attack for 8-digit PIN codes",
        "value": {
            "name": "PIN Codes",
            "description": "Cracking 8-digit PIN codes",
            "hash_type": "SHA1",
            "hash_type_id": 100,
            "attack_mode": 3,
            "priority": 1,
            "hashes": [
                "356a192b7913b04c54574d18c28d46e6395428ab",
                "da4b9237bacccdf19c0760cab7aec4a8359010b0"
            ],
            "mask": "?d?d?d?d?d?d?d?d",
            "additional_args": "--increment",
            "metadata": {
                "source": "pin_database",
                "max_length": 8
            }
        }
    }
}

# Agent examples
AGENT_EXAMPLES = {
    "standard_agent": {
        "summary": "Standard Agent",
        "description": "A standard agent with one GPU",
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
            ],
            "status": "ONLINE",
            "metadata": {
                "location": "datacenter-1",
                "owner": "admin"
            }
        }
    },
    "multi_gpu_agent": {
        "summary": "Multi-GPU Agent",
        "description": "An agent with multiple GPUs",
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
            ],
            "status": "ONLINE",
            "metadata": {
                "location": "datacenter-2",
                "owner": "admin"
            }
        }
    }
}

# Task status update examples
TASK_STATUS_EXAMPLES = {
    "running": {
        "summary": "Running Task",
        "description": "Update for a running task with progress",
        "value": {
            "status": "RUNNING",
            "progress": 45.5,
            "speed": 1250000000,  # 1.25 GH/s
            "recovered_hashes": [
                {"hash": "5f4dcc3b5aa765d61d8327deb882cf99", "plaintext": "password"}
            ]
        }
    },
    "completed": {
        "summary": "Completed Task",
        "description": "Update for a completed task",
        "value": {
            "status": "COMPLETED",
            "progress": 100.0,
            "speed": 1350000000,  # 1.35 GH/s
            "recovered_hashes": [
                {"hash": "5f4dcc3b5aa765d61d8327deb882cf99", "plaintext": "password"},
                {"hash": "e10adc3949ba59abbe56e057f20f883e", "plaintext": "123456"}
            ]
        }
    },
    "failed": {
        "summary": "Failed Task",
        "description": "Update for a failed task",
        "value": {
            "status": "FAILED",
            "progress": 23.7,
            "speed": 1150000000,  # 1.15 GH/s
            "error": "GPU memory allocation error: CUDA_ERROR_OUT_OF_MEMORY"
        }
    }
}

# Heartbeat examples
HEARTBEAT_EXAMPLES = {
    "standard": {
        "summary": "Standard Heartbeat",
        "description": "Regular heartbeat from an agent",
        "value": {
            "status": "ONLINE",
            "cpu_usage": 35.2,
            "gpu_usage": [
                {"device_id": 1, "usage": 95.7, "temperature": 72, "power": 320}
            ],
            "memory_usage": 8192
        }
    },
    "busy": {
        "summary": "Busy Agent",
        "description": "Heartbeat from a busy agent with high resource usage",
        "value": {
            "status": "BUSY",
            "cpu_usage": 87.5,
            "gpu_usage": [
                {"device_id": 1, "usage": 99.8, "temperature": 82, "power": 350},
                {"device_id": 2, "usage": 99.5, "temperature": 78, "power": 320}
            ],
            "memory_usage": 14336
        }
    }
}
