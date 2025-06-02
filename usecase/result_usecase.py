from typing import List, Optional, Dict, Any

from entity.result import Result
from repository.result_repository import ResultRepository


class ResultUseCase:
    """Use case for result management"""
    
    def __init__(self, result_repo: ResultRepository):
        self.result_repo = result_repo
    
    async def create_result(self, result: Result) -> Result:
        """Create a new result"""
        return await self.result_repo.create(result)
    
    async def get_result(self, result_id: str) -> Optional[Result]:
        """Get result by ID"""
        return await self.result_repo.find_by_id(result_id)
    
    async def get_all_results(self, skip: int = 0, limit: int = 100) -> List[Result]:
        """Get all results with pagination"""
        return await self.result_repo.find_all(skip, limit)
    
    async def get_results_by_task_id(self, task_id: str) -> List[Result]:
        """Get results by task ID"""
        return await self.result_repo.find_by_task_id(task_id)
    
    async def get_result_by_hash(self, hash_value: str) -> Optional[Result]:
        """Get result by hash value"""
        return await self.result_repo.find_by_hash(hash_value)
    
    async def get_results_by_agent_id(self, agent_id: str) -> List[Result]:
        """Get results by agent ID"""
        return await self.result_repo.find_by_agent_id(agent_id)
    
    async def delete_result(self, result_id: str) -> bool:
        """Delete a result"""
        return await self.result_repo.delete(result_id)
    
    async def delete_results_by_task_id(self, task_id: str) -> int:
        """Delete all results for a task"""
        return await self.result_repo.delete_by_task_id(task_id)
    
    async def batch_create_results(self, results: List[Result]) -> List[Result]:
        """Create multiple results in batch"""
        created_results = []
        for result in results:
            created_result = await self.result_repo.create(result)
            created_results.append(created_result)
        return created_results
