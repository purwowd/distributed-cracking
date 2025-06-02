from datetime import datetime
from typing import Dict, Any, Optional


class Result:
    """Result entity representing a cracked hash"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        task_id: str = "",
        hash_value: str = "",
        plaintext: str = "",
        cracked_at: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = id
        self.task_id = task_id
        self.hash_value = hash_value
        self.plaintext = plaintext
        self.cracked_at = cracked_at or datetime.utcnow()
        self.agent_id = agent_id
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "hash_value": self.hash_value,
            "plaintext": self.plaintext,
            "cracked_at": self.cracked_at,
            "agent_id": self.agent_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Result':
        """Create result from dictionary"""
        return cls(**data)
