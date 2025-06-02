"""
Mock database module for testing the web interface without a MongoDB connection.
This provides sample data for the web interface to display.
"""

import asyncio
import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(str, Enum):
    ONLINE = "online"
    BUSY = "busy"
    OFFLINE = "offline"

# Sample data for tasks
mock_tasks = [
    {
        "id": "task1",
        "name": "WPA Handshake Crack",
        "description": "Cracking captured WPA handshake from corporate network",
        "hash_type": "2500",  # WPA/WPA2
        "hash_file": "wpa_handshake.hccapx",
        "status": TaskStatus.COMPLETED,
        "progress": 1.0,
        "created_at": datetime.datetime.now() - datetime.timedelta(days=2),
        "updated_at": datetime.datetime.now() - datetime.timedelta(days=1),
        "completed_at": datetime.datetime.now() - datetime.timedelta(days=1),
        "attack_mode": "0",  # Dictionary attack
        "wordlist": "rockyou.txt",
        "rules": "best64.rule",
        "agent_id": "agent1",
        "recovered_hashes": ["hash1", "hash2"],
        "hashes": ["hash1", "hash2", "hash3", "hash4"],
        "speed": "45.2 kH/s"
    },
    {
        "id": "task2",
        "name": "MD5 Password Dump",
        "description": "Cracking MD5 password dump from database breach",
        "hash_type": "0",  # MD5
        "hash_file": "md5_dump.txt",
        "status": TaskStatus.RUNNING,
        "progress": 0.65,
        "created_at": datetime.datetime.now() - datetime.timedelta(days=1),
        "updated_at": datetime.datetime.now() - datetime.timedelta(hours=2),
        "attack_mode": "3",  # Brute force
        "mask": "?a?a?a?a?a?a?a?a",
        "agent_id": "agent2",
        "recovered_hashes": ["hash5"],
        "hashes": ["hash5", "hash6", "hash7", "hash8", "hash9"],
        "speed": "1.2 GH/s"
    },
    {
        "id": "task3",
        "name": "NTLM Domain Hashes",
        "description": "Cracking NTLM hashes from domain controller",
        "hash_type": "1000",  # NTLM
        "hash_file": "ntlm_dump.txt",
        "status": TaskStatus.PENDING,
        "progress": 0.0,
        "created_at": datetime.datetime.now() - datetime.timedelta(hours=2),
        "updated_at": datetime.datetime.now() - datetime.timedelta(hours=2),
        "attack_mode": "0",  # Dictionary attack
        "wordlist": "rockyou.txt",
        "recovered_hashes": [],
        "hashes": ["hash10", "hash11", "hash12", "hash13", "hash14", "hash15"]
    },
    {
        "id": "task4",
        "name": "SHA-256 Web App",
        "description": "Cracking SHA-256 hashes from web application",
        "hash_type": "1400",  # SHA-256
        "hash_file": "sha256_dump.txt",
        "status": TaskStatus.FAILED,
        "progress": 0.32,
        "created_at": datetime.datetime.now() - datetime.timedelta(days=3),
        "updated_at": datetime.datetime.now() - datetime.timedelta(days=2),
        "error": "Agent disconnected unexpectedly",
        "attack_mode": "0",  # Dictionary attack
        "wordlist": "rockyou.txt",
        "agent_id": "agent3",
        "recovered_hashes": [],
        "hashes": ["hash16", "hash17", "hash18"]
    },
    {
        "id": "task5",
        "name": "bcrypt Slow Hash",
        "description": "Cracking bcrypt hashes from user database",
        "hash_type": "3200",  # bcrypt
        "hash_file": "bcrypt_dump.txt",
        "status": TaskStatus.CANCELLED,
        "progress": 0.05,
        "created_at": datetime.datetime.now() - datetime.timedelta(days=5),
        "updated_at": datetime.datetime.now() - datetime.timedelta(days=4),
        "attack_mode": "0",  # Dictionary attack
        "wordlist": "rockyou.txt",
        "agent_id": "agent1",
        "recovered_hashes": [],
        "hashes": ["hash19", "hash20"]
    }
]

# Sample data for agents
mock_agents = [
    {
        "id": "agent1",
        "name": "GPU-Server-01",
        "hostname": "gpu-server-01.local",
        "ip_address": "192.168.1.101",
        "api_key": "api_key_1",
        "status": AgentStatus.ONLINE,
        "last_seen": datetime.datetime.now() - datetime.timedelta(minutes=5),
        "registered_at": datetime.datetime.now() - datetime.timedelta(days=30),
        "hashcat_version": "6.2.6",
        "hardware_info": {
            "cpu": "AMD Ryzen 9 5950X",
            "gpu": "NVIDIA RTX 3090",
            "ram": "64GB DDR4",
            "os": "Ubuntu 22.04"
        },
        "gpu_info": [
            {"name": "NVIDIA RTX 3090", "memory_total_mb": 24576}
        ],
        "capabilities": {
            "hash_types": ["0", "100", "1000", "1400", "1700", "2500", "3200"],
            "attack_modes": ["0", "1", "3", "6", "7"]
        },
        "current_task_id": None
    },
    {
        "id": "agent2",
        "name": "GPU-Server-02",
        "hostname": "gpu-server-02.local",
        "ip_address": "192.168.1.102",
        "api_key": "api_key_2",
        "status": AgentStatus.BUSY,
        "last_seen": datetime.datetime.now(),
        "registered_at": datetime.datetime.now() - datetime.timedelta(days=15),
        "hashcat_version": "6.2.6",
        "hardware_info": {
            "cpu": "Intel Core i9-12900K",
            "gpu": "NVIDIA RTX 4090",
            "ram": "128GB DDR5",
            "os": "Windows Server 2022"
        },
        "gpu_info": [
            {"name": "NVIDIA RTX 4090", "memory_total_mb": 24576}
        ],
        "capabilities": {
            "hash_types": ["0", "100", "1000", "1400", "1700", "2500", "3200"],
            "attack_modes": ["0", "1", "3", "6", "7"]
        },
        "current_task_id": "task2"
    },
    {
        "id": "agent3",
        "name": "GPU-Server-03",
        "hostname": "gpu-server-03.local",
        "ip_address": "192.168.1.103",
        "api_key": "api_key_3",
        "status": AgentStatus.OFFLINE,
        "last_seen": datetime.datetime.now() - datetime.timedelta(days=2),
        "registered_at": datetime.datetime.now() - datetime.timedelta(days=45),
        "hashcat_version": "6.2.5",
        "hardware_info": {
            "cpu": "AMD EPYC 7763",
            "gpu": "AMD Radeon Pro W6800",
            "ram": "256GB DDR4 ECC",
            "os": "CentOS 8"
        },
        "gpu_info": [
            {"name": "AMD Radeon Pro W6800", "memory_total_mb": 32768}
        ],
        "capabilities": {
            "hash_types": ["0", "100", "1000", "1400", "1700"],
            "attack_modes": ["0", "1", "3"]
        },
        "current_task_id": None
    }
]

# Sample data for results
mock_results = [
    {
        "id": "result1",
        "task_id": "task1",
        "agent_id": "agent1",
        "hash_value": "5f4dcc3b5aa765d61d8327deb882cf99",
        "plaintext": "password",
        "cracked_at": datetime.datetime.now() - datetime.timedelta(days=1, hours=2)
    },
    {
        "id": "result2",
        "task_id": "task1",
        "agent_id": "agent1",
        "hash_value": "e10adc3949ba59abbe56e057f20f883e",
        "plaintext": "123456",
        "cracked_at": datetime.datetime.now() - datetime.timedelta(days=1, hours=3)
    },
    {
        "id": "result3",
        "task_id": "task2",
        "agent_id": "agent2",
        "hash_value": "25d55ad283aa400af464c76d713c07ad",
        "plaintext": "12345678",
        "cracked_at": datetime.datetime.now() - datetime.timedelta(hours=5)
    }
]

# Mock database client
class MockDatabase:
    def __init__(self):
        self.tasks = mock_tasks
        self.agents = mock_agents
        self.results = mock_results
    
    async def get_tasks(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [task for task in self.tasks if task["status"] == status][skip:skip+limit]
        return self.tasks[skip:skip+limit]
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    async def get_agents(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [agent for agent in self.agents if agent["status"] == status][skip:skip+limit]
        return self.agents[skip:skip+limit]
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        for agent in self.agents:
            if agent["id"] == agent_id:
                return agent
        return None
    
    async def get_results(self, skip: int = 0, limit: int = 100, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if task_id:
            return [result for result in self.results if result["task_id"] == task_id][skip:skip+limit]
        return self.results[skip:skip+limit]
    
    async def get_task_stats(self) -> Dict[str, int]:
        stats = {
            "total": len(self.tasks),
            "pending": len([t for t in self.tasks if t["status"] == TaskStatus.PENDING]),
            "running": len([t for t in self.tasks if t["status"] == TaskStatus.RUNNING]),
            "completed": len([t for t in self.tasks if t["status"] == TaskStatus.COMPLETED]),
            "failed": len([t for t in self.tasks if t["status"] == TaskStatus.FAILED]),
            "cancelled": len([t for t in self.tasks if t["status"] == TaskStatus.CANCELLED])
        }
        return stats
    
    async def get_agent_stats(self) -> Dict[str, int]:
        stats = {
            "total": len(self.agents),
            "online": len([a for a in self.agents if a["status"] == AgentStatus.ONLINE]),
            "busy": len([a for a in self.agents if a["status"] == AgentStatus.BUSY]),
            "offline": len([a for a in self.agents if a["status"] == AgentStatus.OFFLINE])
        }
        return stats
    
    async def get_result_stats(self) -> Dict[str, int]:
        total_hashes = sum(len(task["hashes"]) for task in self.tasks)
        recovered_hashes = len(self.results)
        
        stats = {
            "total_hashes": total_hashes,
            "recovered_hashes": recovered_hashes,
            "recovery_rate": recovered_hashes / total_hashes if total_hashes > 0 else 0
        }
        return stats

# Mock database connection
mock_db = MockDatabase()

async def connect_to_db():
    """Mock connection to database"""
    await asyncio.sleep(0.1)  # Simulate connection delay
    return mock_db

async def close_db_connection():
    """Mock close database connection"""
    await asyncio.sleep(0.1)  # Simulate disconnection delay
    return True
