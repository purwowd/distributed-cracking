from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HashType(str, Enum):
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    NTLM = "ntlm"
    WPA = "wpa"
    BCRYPT = "bcrypt"
    CUSTOM = "custom"


class Task:
    """Task entity representing a password cracking job"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        description: str = "",
        hash_type: HashType = HashType.MD5,
        hash_type_id: Optional[int] = None,  # Hashcat hash type ID
        hashes: List[str] = None,
        wordlist_path: Optional[str] = None,
        rule_path: Optional[str] = None,
        mask: Optional[str] = None,
        attack_mode: int = 0,  # 0=dict, 1=combo, 3=mask, 6=hybrid, etc.
        additional_args: Optional[str] = None,
        priority: int = 1,
        status: TaskStatus = TaskStatus.PENDING,
        agent_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        progress: float = 0.0,
        speed: Optional[float] = None,  # H/s
        recovered_hashes: List[Dict[str, str]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.hash_type = hash_type
        self.hash_type_id = hash_type_id
        self.hashes = hashes or []
        self.wordlist_path = wordlist_path
        self.rule_path = rule_path
        self.mask = mask
        self.attack_mode = attack_mode
        self.additional_args = additional_args
        self.priority = priority
        self.status = status
        self.agent_id = agent_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.started_at = started_at
        self.completed_at = completed_at
        self.progress = progress
        self.speed = speed
        self.recovered_hashes = recovered_hashes or []
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "hash_type": self.hash_type.value,
            "hash_type_id": self.hash_type_id,
            "hashes": self.hashes,
            "wordlist_path": self.wordlist_path,
            "rule_path": self.rule_path,
            "mask": self.mask,
            "attack_mode": self.attack_mode,
            "additional_args": self.additional_args,
            "priority": self.priority,
            "status": self.status.value,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "speed": self.speed,
            "recovered_hashes": self.recovered_hashes,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        if data.get("hash_type"):
            data["hash_type"] = HashType(data["hash_type"])
        if data.get("status"):
            data["status"] = TaskStatus(data["status"])
        return cls(**data)
