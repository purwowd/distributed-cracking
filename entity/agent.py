from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List


class AgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class Agent:
    """Agent entity representing a GPU server running hashcat"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        hostname: str = "",
        ip_address: str = "",
        api_key: str = "",
        status: AgentStatus = AgentStatus.OFFLINE,
        capabilities: Dict[str, Any] = None,
        current_task_id: Optional[str] = None,
        last_seen: Optional[datetime] = None,
        registered_at: Optional[datetime] = None,
        gpu_info: List[Dict[str, Any]] = None,
        cpu_info: Dict[str, Any] = None,
        hashcat_version: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = id
        self.name = name
        self.hostname = hostname
        self.ip_address = ip_address
        self.api_key = api_key
        self.status = status
        self.capabilities = capabilities or {}
        self.current_task_id = current_task_id
        self.last_seen = last_seen or datetime.utcnow()
        self.registered_at = registered_at or datetime.utcnow()
        self.gpu_info = gpu_info or []
        self.cpu_info = cpu_info or {}
        self.hashcat_version = hashcat_version
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "api_key": self.api_key,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "current_task_id": self.current_task_id,
            "last_seen": self.last_seen,
            "registered_at": self.registered_at,
            "gpu_info": self.gpu_info,
            "cpu_info": self.cpu_info,
            "hashcat_version": self.hashcat_version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary"""
        if data.get("status"):
            data["status"] = AgentStatus(data["status"])
        return cls(**data)
    
    def update_heartbeat(self):
        """Update agent's last seen timestamp"""
        self.last_seen = datetime.utcnow()
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return self.status == AgentStatus.ONLINE and self.current_task_id is None
