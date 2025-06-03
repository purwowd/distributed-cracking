from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from entity.agent import AgentStatus
from model.examples import AGENT_EXAMPLES, HEARTBEAT_EXAMPLES


class AgentBase(BaseModel):
    """Base model for agent data"""
    name: str
    hostname: str
    ip_address: str


class AgentCreate(AgentBase):
    """Model for creating a new agent"""
    api_key: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = Field(default_factory=dict)
    gpu_info: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    cpu_info: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hashcat_version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": AGENT_EXAMPLES
        }
    }


class AgentUpdate(BaseModel):
    """Model for updating an existing agent"""
    name: Optional[str] = None
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[AgentStatus] = None
    capabilities: Optional[Dict[str, Any]] = None
    current_task_id: Optional[str] = None
    gpu_info: Optional[List[Dict[str, Any]]] = None
    cpu_info: Optional[Dict[str, Any]] = None
    hashcat_version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    """Model for agent response"""
    id: str
    status: AgentStatus
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    current_task_id: Optional[str] = None
    last_seen: datetime
    registered_at: datetime
    gpu_info: List[Dict[str, Any]] = Field(default_factory=list)
    cpu_info: Dict[str, Any] = Field(default_factory=dict)
    hashcat_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True


class AgentHeartbeat(BaseModel):
    """Model for agent heartbeat"""
    status: AgentStatus
    cpu_usage: float = Field(0.0, ge=0.0, le=100.0, description="CPU usage percentage")
    gpu_usage: List[Dict[str, Any]] = Field(default_factory=list, description="GPU usage information")
    memory_usage: int = Field(0, ge=0, description="Memory usage in MB")
    
    model_config = {
        "json_schema_extra": {
            "examples": HEARTBEAT_EXAMPLES
        }
    }
