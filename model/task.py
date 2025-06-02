from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from entity.task import TaskStatus, HashType


class TaskBase(BaseModel):
    """Base model for task data"""
    name: str
    description: Optional[str] = ""
    hash_type: HashType
    hash_type_id: Optional[int] = None
    attack_mode: int = 0
    priority: int = 1
    additional_args: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    hashes: List[str]
    wordlist_path: Optional[str] = None
    rule_path: Optional[str] = None
    mask: Optional[str] = None


class TaskUpdate(BaseModel):
    """Model for updating an existing task"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    additional_args: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    """Model for task response"""
    id: str
    status: TaskStatus
    hashes: List[str]
    wordlist_path: Optional[str] = None
    rule_path: Optional[str] = None
    mask: Optional[str] = None
    agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    speed: Optional[float] = None
    recovered_hashes: List[Dict[str, str]] = Field(default_factory=list)
    error: Optional[str] = None

    class Config:
        orm_mode = True


class TaskStatusUpdate(BaseModel):
    """Model for updating task status from agent"""
    status: TaskStatus
    progress: float = 0.0
    speed: Optional[float] = None
    recovered_hashes: List[Dict[str, str]] = Field(default_factory=list)
    error: Optional[str] = None
