from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import string

from entity.agent import Agent, AgentStatus
from repository.agent_repository import AgentRepository
from repository.task_repository import TaskRepository


class AgentUseCase:
    """Use case for agent management"""
    
    def __init__(self, agent_repo: AgentRepository, task_repo: TaskRepository):
        self.agent_repo = agent_repo
        self.task_repo = task_repo
    
    async def register_agent(self, agent: Agent) -> Agent:
        """Register a new agent"""
        # Generate API key if not provided
        if not agent.api_key:
            agent.api_key = self._generate_api_key()
        
        # Set initial status
        agent.status = AgentStatus.ONLINE
        agent.last_seen = datetime.utcnow()
        agent.registered_at = datetime.utcnow()
        
        return await self.agent_repo.create(agent)
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return await self.agent_repo.find_by_id(agent_id)
    
    async def get_agent_by_api_key(self, api_key: str) -> Optional[Agent]:
        """Get agent by API key"""
        return await self.agent_repo.find_by_api_key(api_key)
    
    async def get_all_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all agents with pagination"""
        return await self.agent_repo.find_all(skip, limit)
    
    async def get_agents_by_status(self, status: AgentStatus, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get agents by status"""
        return await self.agent_repo.find_by_status(status, skip, limit)
    
    async def update_agent(self, agent: Agent) -> Optional[Agent]:
        """Update an existing agent"""
        return await self.agent_repo.update(agent)
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        # Get agent to check if it has a task
        agent = await self.agent_repo.find_by_id(agent_id)
        if agent and agent.current_task_id:
            # Reset task status to pending
            from entity.task import TaskStatus
            await self.task_repo.update_status(
                agent.current_task_id, 
                TaskStatus.PENDING
            )
        
        # Delete agent
        return await self.agent_repo.delete(agent_id)
    
    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> Optional[Agent]:
        """Update agent status"""
        return await self.agent_repo.update_status(agent_id, status)
    
    async def update_heartbeat(self, agent_id: str, status: AgentStatus, 
                             cpu_usage: float, gpu_usage: List[Dict[str, Any]],
                             memory_usage: int) -> Optional[Agent]:
        """Update agent heartbeat with resource usage information
        
        Args:
            agent_id: Agent ID
            status: Current agent status
            cpu_usage: CPU usage percentage (0-100)
            gpu_usage: List of GPU usage information
            memory_usage: Memory usage in MB
            
        Returns:
            Updated agent or None if agent not found
        """
        # Update agent status
        agent = await self.agent_repo.update_status(agent_id, status)
        if not agent:
            return None
            
        # Update agent heartbeat timestamp
        agent = await self.agent_repo.update_heartbeat(agent_id)
        
        # Update agent resource usage in metadata
        if not agent.metadata:
            agent.metadata = {}
            
        agent.metadata["resource_usage"] = {
            "cpu_usage": cpu_usage,
            "gpu_usage": gpu_usage,
            "memory_usage": memory_usage,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Save updated agent
        return await self.agent_repo.update(agent)
    
    async def process_heartbeat(self, agent_id: str, status: AgentStatus, 
                              current_task_id: Optional[str] = None,
                              task_progress: Optional[float] = None,
                              task_speed: Optional[float] = None) -> Optional[Agent]:
        """Process agent heartbeat"""
        # Update agent status and heartbeat
        agent = await self.agent_repo.update_status(agent_id, status)
        if not agent:
            return None
        
        # Update task progress if provided
        if current_task_id and (task_progress is not None or task_speed is not None):
            from entity.task import TaskStatus
            await self.task_repo.update_status(
                current_task_id,
                TaskStatus.RUNNING,
                progress=task_progress,
                speed=task_speed
            )
        
        return agent
    
    async def get_available_agents(self) -> List[Agent]:
        """Get available agents for task assignment"""
        return await self.agent_repo.find_available_agents()
    
    async def check_offline_agents(self, timeout_minutes: int = 5) -> int:
        """Check for agents that haven't sent heartbeats and mark them as offline"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        # Get all online and busy agents
        online_agents = await self.agent_repo.find_by_status(AgentStatus.ONLINE)
        busy_agents = await self.agent_repo.find_by_status(AgentStatus.BUSY)
        
        # Combine lists
        active_agents = online_agents + busy_agents
        
        # Check last seen timestamp
        offline_count = 0
        for agent in active_agents:
            if agent.last_seen < cutoff_time:
                # Mark agent as offline
                await self.agent_repo.update_status(agent.id, AgentStatus.OFFLINE)
                
                # If agent had a task, reset it to pending
                if agent.current_task_id:
                    from entity.task import TaskStatus
                    await self.task_repo.update_status(
                        agent.current_task_id,
                        TaskStatus.PENDING
                    )
                    # Clear task from agent
                    await self.agent_repo.clear_task(agent.id)
                
                offline_count += 1
        
        return offline_count
    
    def _generate_api_key(self, length: int = 32) -> str:
        """Generate a random API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
