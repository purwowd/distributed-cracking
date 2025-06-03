from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from entity.task import TaskStatus, HashType
from model.examples import TASK_EXAMPLES, TASK_STATUS_EXAMPLES


class TaskBase(BaseModel):
    """Base model for task data"""
    name: str = Field(..., min_length=1, max_length=100, description="Task name, 1-100 characters")
    description: Optional[str] = Field("", max_length=500, description="Optional task description")
    hash_type: HashType
    hash_type_id: Optional[int] = Field(None, description="Hashcat hash type ID")
    attack_mode: int = Field(0, ge=0, le=9, description="Hashcat attack mode (0-9)")
    priority: int = Field(1, ge=1, le=10, description="Task priority (1-10, higher is more important)")
    additional_args: Optional[str] = Field(None, max_length=500, description="Additional hashcat arguments")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the task")
    
    @validator('attack_mode')
    def validate_attack_mode(cls, v, values):
        """Validate attack mode based on other fields"""
        if v == 0 and 'wordlist_path' not in values and not hasattr(cls, 'wordlist_path'):
            raise ValueError("Dictionary attack (mode 0) requires a wordlist")
        if v == 3 and 'mask' not in values and not hasattr(cls, 'mask'):
            raise ValueError("Mask attack (mode 3) requires a mask pattern")
        return v


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    hashes: List[str] = Field(..., min_items=1, description="List of hashes to crack")
    wordlist_path: Optional[str] = Field(None, description="Path to wordlist file")
    rule_path: Optional[str] = Field(None, description="Path to hashcat rule file")
    mask: Optional[str] = Field(None, description="Hashcat mask pattern")
    
    model_config = {
        "json_schema_extra": {
            "examples": TASK_EXAMPLES
        }
    }
    
    @validator('hashes')
    def validate_hashes(cls, v):
        """Validate hash format"""
        if not v:
            raise ValueError("At least one hash must be provided")
        
        # Basic validation - could be enhanced for specific hash types
        for hash_val in v:
            if not hash_val or len(hash_val.strip()) < 8:
                raise ValueError(f"Invalid hash format: {hash_val}")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_attack_configuration(cls, values):
        """Validate that the necessary files are provided based on attack mode"""
        attack_mode = values.get('attack_mode', 0)
        
        if attack_mode == 0 and not values.get('wordlist_path'):  # Dictionary attack
            raise ValueError("Dictionary attack requires a wordlist path")
        elif attack_mode == 3 and not values.get('mask'):  # Mask attack
            raise ValueError("Mask attack requires a mask pattern")
        return values


class TaskUpdate(BaseModel):
    """Model for updating an existing task"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    additional_args: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError("Priority must be between 1 and 10")
        return v
        
    @validator('status')
    def validate_status_transition(cls, v):
        """Validate status transitions (could be enhanced with task context)"""
        # This is a basic implementation - in a real system, you'd check current status
        # and validate if the transition is allowed
        return v


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

    model_config = {
        "from_attributes": True
    }


class TaskStatusUpdate(BaseModel):
    """Model for updating task status from agent"""
    status: TaskStatus
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage (0-100)")
    speed: Optional[float] = Field(None, ge=0.0, description="Cracking speed in H/s")
    recovered_hashes: List[Dict[str, str]] = Field(default_factory=list, description="Recovered hash:plaintext pairs")
    error: Optional[str] = Field(None, max_length=1000, description="Error message if task failed")
    
    model_config = {
        "json_schema_extra": {
            "examples": TASK_STATUS_EXAMPLES
        }
    }
    
    @validator('recovered_hashes')
    def validate_recovered_hashes(cls, v):
        """Validate recovered hashes format"""
        for item in v:
            if 'hash' not in item or 'plaintext' not in item:
                raise ValueError("Each recovered hash must contain 'hash' and 'plaintext' fields")
        return v
    
    @root_validator(skip_on_failure=True)
    def validate_status_data(cls, values):
        """Validate that the data is consistent with the status"""
        status = values.get('status')
        error = values.get('error')
        
        if status == TaskStatus.FAILED and not error:
            raise ValueError("Error message is required when status is FAILED")
            
        if status == TaskStatus.COMPLETED and values.get('progress', 0) < 100:
            # Auto-correct progress for completed tasks
            values['progress'] = 100.0
            
        return values
