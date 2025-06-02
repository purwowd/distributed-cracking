from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from entity.result import Result


class ResultRepository:
    """Repository for result data access"""
    
    def __init__(self, database):
        self.db = database
        self.collection = database.results
    
    async def create(self, result: Result) -> Result:
        """Create a new result"""
        result_dict = result.to_dict()
        # Remove id if None
        if result_dict["id"] is None:
            del result_dict["id"]
        
        result_obj = await self.collection.insert_one(result_dict)
        result.id = str(result_obj.inserted_id)
        return result
    
    async def find_by_id(self, result_id: str) -> Optional[Result]:
        """Find result by ID"""
        result_dict = await self.collection.find_one({"_id": ObjectId(result_id)})
        if result_dict:
            result_dict["id"] = str(result_dict.pop("_id"))
            return Result.from_dict(result_dict)
        return None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Result]:
        """Find all results with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        results = []
        async for result_dict in cursor:
            result_dict["id"] = str(result_dict.pop("_id"))
            results.append(Result.from_dict(result_dict))
        return results
    
    async def find_by_task_id(self, task_id: str) -> List[Result]:
        """Find results by task ID"""
        cursor = self.collection.find({"task_id": task_id})
        results = []
        async for result_dict in cursor:
            result_dict["id"] = str(result_dict.pop("_id"))
            results.append(Result.from_dict(result_dict))
        return results
    
    async def find_by_hash(self, hash_value: str) -> Optional[Result]:
        """Find result by hash value"""
        result_dict = await self.collection.find_one({"hash_value": hash_value})
        if result_dict:
            result_dict["id"] = str(result_dict.pop("_id"))
            return Result.from_dict(result_dict)
        return None
    
    async def find_by_agent_id(self, agent_id: str) -> List[Result]:
        """Find results by agent ID"""
        cursor = self.collection.find({"agent_id": agent_id})
        results = []
        async for result_dict in cursor:
            result_dict["id"] = str(result_dict.pop("_id"))
            results.append(Result.from_dict(result_dict))
        return results
    
    async def delete(self, result_id: str) -> bool:
        """Delete a result"""
        result = await self.collection.delete_one({"_id": ObjectId(result_id)})
        return result.deleted_count > 0
    
    async def delete_by_task_id(self, task_id: str) -> int:
        """Delete all results for a task"""
        result = await self.collection.delete_many({"task_id": task_id})
        return result.deleted_count
