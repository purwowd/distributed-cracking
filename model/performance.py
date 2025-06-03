from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class PerformanceMetric(BaseModel):
    """Performance metric model for system monitoring.
    
    This model represents a point-in-time snapshot of system performance metrics
    including active agents, completed tasks, and processing speed.
    
    Attributes:
        timestamp: The time when the metric was recorded
        active_agents: Number of agents that are currently online
        completed_tasks: Total number of completed tasks at this point
        speed: Processing speed in hashes/second
        agent_ids: List of IDs of active agents at this point
    """
    timestamp: datetime
    active_agents: int
    completed_tasks: int
    speed: float  # in hashes/second
    agent_ids: List[str] = []  # IDs of active agents
