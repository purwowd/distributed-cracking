from typing import List, Optional, Dict, Any
from datetime import datetime

from entity.task import Task, TaskStatus
from entity.agent import Agent
from repository.task_repository import TaskRepository
from repository.agent_repository import AgentRepository
from repository.result_repository import ResultRepository


class TaskUseCase:
    """Use case for task management"""
    
    def __init__(self, task_repo: TaskRepository, agent_repo: AgentRepository, result_repo: ResultRepository):
        self.task_repo = task_repo
        self.agent_repo = agent_repo
        self.result_repo = result_repo
    
    async def create_task(self, task: Task) -> Task:
        """Create a new task"""
        return await self.task_repo.create(task)
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return await self.task_repo.find_by_id(task_id)
    
    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        return await self.task_repo.find_all(skip, limit)
    
    async def get_tasks_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by status"""
        return await self.task_repo.find_by_status(status, skip, limit)
    
    async def update_task(self, task: Task) -> Optional[Task]:
        """Update an existing task"""
        return await self.task_repo.update(task)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        # Delete associated results
        await self.result_repo.delete_by_task_id(task_id)
        
        # Get task to check if assigned to an agent
        task = await self.task_repo.find_by_id(task_id)
        if task and task.agent_id:
            # Clear task from agent
            await self.agent_repo.clear_task(task.agent_id)
        
        # Delete task
        return await self.task_repo.delete(task_id)
    
    async def assign_task_to_agent(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign task to an agent"""
        # Check if task exists and is pending
        task = await self.task_repo.find_by_id(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return None
        
        # Check if agent exists and is available
        agent = await self.agent_repo.find_by_id(agent_id)
        if not agent or not agent.is_available():
            return None
        
        # Assign task to agent
        await self.agent_repo.assign_task(agent_id, task_id)
        return await self.task_repo.assign_to_agent(task_id, agent_id)
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                               progress: float = None, speed: float = None,
                               error: str = None) -> Optional[Task]:
        """Update task status"""
        task = await self.task_repo.update_status(task_id, status, progress, speed, error)
        
        # If task completed or failed, clear from agent
        if task and task.agent_id and status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            await self.agent_repo.clear_task(task.agent_id)
        
        return task
    
    async def add_recovered_hash(self, task_id: str, hash_value: str, plaintext: str, agent_id: str = None) -> Optional[Task]:
        """Add a recovered hash to the task"""
        # Add to task's recovered hashes
        task = await self.task_repo.add_recovered_hash(task_id, hash_value, plaintext)
        
        # Create result record
        if task:
            from entity.result import Result
            result = Result(
                task_id=task_id,
                hash_value=hash_value,
                plaintext=plaintext,
                agent_id=agent_id or task.agent_id
            )
            await self.result_repo.create(result)
        
        return task
    
    async def get_next_pending_task(self) -> Optional[Task]:
        """Get the next pending task based on priority"""
        return await self.task_repo.find_next_pending_task()
    
    async def auto_assign_tasks(self) -> int:
        """Auto-assign pending tasks to available agents"""
        # Get available agents
        agents = await self.agent_repo.find_available_agents()
        if not agents:
            return 0
        
        # Assign tasks to agents
        assigned_count = 0
        for agent in agents:
            # Get next pending task
            task = await self.task_repo.find_next_pending_task()
            if not task:
                break
            
            # Assign task to agent
            await self.assign_task_to_agent(task.id, agent.id)
            assigned_count += 1
        
        return assigned_count
    
    async def cancel_task(self, task_id: str) -> Optional[Task]:
        """Cancel a task"""
        task = await self.task_repo.find_by_id(task_id)
        if not task:
            return None
        
        # If task is assigned to an agent, clear it
        if task.agent_id and task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
            await self.agent_repo.clear_task(task.agent_id)
        
        # Update task status to cancelled
        return await self.task_repo.update_status(task_id, TaskStatus.CANCELLED)
