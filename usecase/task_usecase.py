from typing import List, Optional, Dict, Any
import logging
import traceback
from datetime import datetime

from entity.task import Task, TaskStatus
from repository.task_repository import TaskRepository
from repository.agent_repository import AgentRepository
from exception.repository_exception import EntityNotFoundException, DatabaseOperationException
from exception.usecase_exception import (
    ResourceNotFoundException,
    ResourceConflictException,
    InvalidOperationException,
    BusinessRuleViolationException
)
from repository.result_repository import ResultRepository


class TaskUseCase:
    """Use case for task management"""
    
    def __init__(self, task_repo: TaskRepository, agent_repo: AgentRepository, result_repo: ResultRepository):
        self.task_repo = task_repo
        self.agent_repo = agent_repo
        self.result_repo = result_repo
    
    async def create_task(self, task: Task) -> Task:
        """Create a new task"""
        try:
            return await self.task_repo.create(task)
        except Exception as e:
            logging.error(f"Error creating task: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        try:
            task = await self.task_repo.find_by_id(task_id)
            if not task:
                raise ResourceNotFoundException(
                    resource_type="Task",
                    resource_id=task_id
                )
            return task
        except EntityNotFoundException as e:
            raise ResourceNotFoundException(
                resource_type="Task",
                resource_id=task_id,
                details={"original_error": str(e)}
            )
        except Exception as e:
            logging.error(f"Error getting task by ID: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        try:
            return await self.task_repo.find_all(skip, limit)
        except Exception as e:
            logging.error(f"Error getting all tasks: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def count_all_tasks(self) -> int:
        """Count all tasks"""
        try:
            return await self.task_repo.count_all()
        except Exception as e:
            logging.error(f"Error counting all tasks: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_tasks_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get tasks by status"""
        try:
            return await self.task_repo.find_by_status(status, skip, limit)
        except Exception as e:
            logging.error(f"Error getting tasks by status: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def count_tasks_by_status(self, status: TaskStatus) -> int:
        """Count tasks by status"""
        try:
            return await self.task_repo.count_by_status(status)
        except Exception as e:
            logging.error(f"Error counting tasks by status: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def update_task(self, task: Task) -> Optional[Task]:
        """Update an existing task"""
        try:
            return await self.task_repo.update(task)
        except Exception as e:
            logging.error(f"Error updating task: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            # Check if task exists and is not running
            task = await self.task_repo.find_by_id(task_id)
            if not task:
                raise ResourceNotFoundException(
                    resource_type="Task",
                    resource_id=task_id
                )
                
            if task.status == TaskStatus.RUNNING:
                raise InvalidOperationException(
                    operation="delete_task",
                    reason="Cannot delete a running task"
                )
                
            # Delete associated results
            await self.result_repo.delete_by_task_id(task_id)
            
            # Get task to check if assigned to an agent
            if task.agent_id:
                # Clear task from agent
                await self.agent_repo.clear_task(task.agent_id)
            
            # Delete task
            return await self.task_repo.delete(task_id)
        except EntityNotFoundException as e:
            raise ResourceNotFoundException(
                resource_type="Task",
                resource_id=task_id,
                details={"original_error": str(e)}
            )
        except Exception as e:
            logging.error(f"Error deleting task: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def assign_task_to_agent(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign a task to an agent"""
        try:
            # Validate task
            task = await self.task_repo.find_by_id(task_id)
            if not task:
                raise ResourceNotFoundException(
                    resource_type="Task",
                    resource_id=task_id
                )
            
            if task.status != TaskStatus.PENDING:
                raise InvalidOperationException(
                    operation="assign_task",
                    reason=f"Task is not in PENDING state (current state: {task.status.name})"
                )
                
            # Validate agent
            agent = await self.agent_repo.find_by_id(agent_id)
            if not agent:
                raise ResourceNotFoundException(
                    resource_type="Agent",
                    resource_id=agent_id
                )
                
            if not agent.is_available():
                raise ResourceConflictException(
                    resource_type="Agent",
                    message=f"Agent {agent_id} is not available"
                )
                
            # Assign task to agent
            await self.agent_repo.assign_task(agent_id, task_id)
            return await self.task_repo.assign_to_agent(task_id, agent_id)
        except (EntityNotFoundException, DatabaseOperationException) as e:
            logging.error(f"Repository error in assign_task_to_agent: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error assigning task to agent: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                               progress: float = None, speed: float = None,
                               error: str = None) -> Optional[Task]:
        """Update task status"""
        try:
            task = await self.task_repo.update_status(task_id, status, progress, speed, error)
            
            # If task completed or failed, clear from agent
            if task and task.agent_id and status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                await self.agent_repo.clear_task(task.agent_id)
            
            return task
        except Exception as e:
            logging.error(f"Error updating task status: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def add_recovered_hash(self, task_id: str, hash_value: str, plaintext: str, agent_id: str = None) -> Optional[Task]:
        """Add a recovered hash to the task"""
        try:
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
        except Exception as e:
            logging.error(f"Error adding recovered hash: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_next_pending_task(self) -> Optional[Task]:
        """Get the next pending task based on priority"""
        try:
            return await self.task_repo.find_next_pending_task()
        except Exception as e:
            logging.error(f"Error getting next pending task: {str(e)}\n{traceback.format_exc()}")
            raise
    
    
    async def auto_assign_tasks(self) -> List[Task]:
        """Auto-assign pending tasks to available agents"""
        try:
            # Cari task dengan status PENDING
            pending_tasks = await self.task_repo.find_by_status(TaskStatus.PENDING)
            pending_tasks = list(pending_tasks) if pending_tasks else []
            if not pending_tasks:
                return []
                
            # Cari agent yang tersedia
            available_agents = await self.agent_repo.find_available_agents()
            if not available_agents:
                return []
                
            assigned_tasks = []
            for agent in available_agents:
                if not pending_tasks:
                    break
                    
                task = pending_tasks.pop(0)
                try:
                    assigned_task = await self.assign_task_to_agent(task.id, agent.id)
                    if assigned_task:
                        assigned_tasks.append(assigned_task)
                except Exception as e:
                    logging.error(f"Error auto-assigning task {task.id} to agent {agent.id}: {str(e)}")
                    # Continue with next task/agent pair
                    continue
                    
            return assigned_tasks
        except Exception as e:
            logging.error(f"Error in auto_assign_tasks: {str(e)}")
            logging.error(traceback.format_exc())
            raise

    async def cancel_task(self, task_id: str) -> Optional[Task]:
        """Cancel a task"""
        try:
            task = await self.task_repo.find_by_id(task_id)
            if not task:
                raise ResourceNotFoundException(
                    resource_type="Task",
                    resource_id=task_id
                )
            
            # If task is assigned to an agent, clear it
            if task.agent_id and task.status in [TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                await self.agent_repo.clear_task(task.agent_id)
            
            # Update task status to cancelled
            return await self.task_repo.update_status(task_id, TaskStatus.CANCELLED)
        except Exception as e:
            logging.error(f"Error cancelling task: {str(e)}\n{traceback.format_exc()}")
            raise
