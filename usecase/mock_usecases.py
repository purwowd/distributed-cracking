"""
Mock implementations of usecase classes for the web interface.
These will be used when the real MongoDB connection is not available.
"""

from typing import List, Dict, Any, Optional
from fastapi import Depends

from config.mock_database import mock_db

class MockTaskUseCase:
    """Mock implementation of TaskUseCase"""
    
    async def get_tasks(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        return await mock_db.get_tasks(skip, limit, status)
        
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks without pagination"""
        return await mock_db.get_tasks(0, 1000)
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return await mock_db.get_task(task_id)
    
    async def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_task to maintain compatibility with the real usecase"""
        return await mock_db.get_task(task_id)
    
    async def get_task_stats(self) -> Dict[str, int]:
        return await mock_db.get_task_stats()
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # Generate a unique ID for the new task
        task_data["id"] = f"task{len(mock_db.tasks) + 1}"
        
        # Add default fields if not present
        import datetime
        if "created_at" not in task_data:
            task_data["created_at"] = datetime.datetime.now()
        if "updated_at" not in task_data:
            task_data["updated_at"] = datetime.datetime.now()
        if "status" not in task_data:
            task_data["status"] = "pending"
        if "progress" not in task_data:
            task_data["progress"] = 0.0
            
        # Add the task to the mock database
        mock_db.tasks.append(task_data)
        
        return task_data
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = await self.get_task(task_id)
        if not task:
            return None
        
        # Update task fields
        for key, value in task_data.items():
            task[key] = value
            
        return task
    
    async def delete_task(self, task_id: str) -> bool:
        task = await self.get_task(task_id)
        if not task:
            return False
        
        # Remove task from mock database
        mock_db.tasks = [t for t in mock_db.tasks if t["id"] != task_id]
        return True
    
    async def cancel_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = await self.get_task(task_id)
        if not task:
            return None
        
        task["status"] = "cancelled"
        return task

class MockAgentUseCase:
    """Mock implementation of AgentUseCase"""
    
    async def get_agents(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        return await mock_db.get_agents(skip, limit, status)
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all agents without pagination"""
        return await mock_db.get_agents(0, 1000)
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return await mock_db.get_agent(agent_id)
    
    async def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_agent to maintain compatibility with the real usecase"""
        return await mock_db.get_agent(agent_id)
    
    async def get_agent_stats(self) -> Dict[str, int]:
        return await mock_db.get_agent_stats()
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent in the mock database"""
        # Generate a unique ID for the new agent
        agent_data["id"] = f"agent{len(mock_db.agents) + 1}"
        
        # Add the agent to the mock database
        mock_db.agents.append(agent_data)
        
        return agent_data

class MockResultUseCase:
    """Mock implementation of ResultUseCase"""
    
    async def get_results(self, skip: int = 0, limit: int = 100, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return await mock_db.get_results(skip, limit, task_id)
    
    async def get_all_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all results with optional limit"""
        return await mock_db.get_results(0, limit)
    
    async def get_results_by_task_id(self, task_id: str) -> List[Dict[str, Any]]:
        """Get results for a specific task"""
        return await mock_db.get_results(0, 1000, task_id)
    
    async def get_result_stats(self) -> Dict[str, int]:
        return await mock_db.get_result_stats()

# Factory functions to get usecase instances
def get_mock_task_usecase() -> MockTaskUseCase:
    return MockTaskUseCase()

def get_mock_agent_usecase() -> MockAgentUseCase:
    return MockAgentUseCase()

def get_mock_result_usecase() -> MockResultUseCase:
    return MockResultUseCase()
