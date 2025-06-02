from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class ResultBase(BaseModel):
    """Base model for result data"""
    task_id: str
    hash_value: str
    plaintext: str


class ResultCreate(ResultBase):
    """Model for creating a new result"""
    agent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ResultResponse(ResultBase):
    """Model for result response"""
    id: str
    cracked_at: datetime
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        orm_mode = True
