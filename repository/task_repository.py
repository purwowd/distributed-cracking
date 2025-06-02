from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from entity.task import Task, TaskStatus


class TaskRepository:
    """Repository for task data access"""
    
    def __init__(self, database):
        self.db = database
        self.collection = database.tasks
    
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        task_dict = task.to_dict()
        # Remove id if None
        if task_dict["id"] is None:
            del task_dict["id"]
        
        result = await self.collection.insert_one(task_dict)
        task.id = str(result.inserted_id)
        return task
    
    async def find_by_id(self, task_id: str) -> Optional[Task]:
        """Find task by ID"""
        task_dict = await self.collection.find_one({"_id": ObjectId(task_id)})
        if task_dict:
            task_dict["id"] = str(task_dict.pop("_id"))
            return Task.from_dict(task_dict)
        return None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Find all tasks with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        tasks = []
        async for task_dict in cursor:
            task_dict["id"] = str(task_dict.pop("_id"))
            tasks.append(Task.from_dict(task_dict))
        return tasks
    
    async def find_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """Find tasks by status"""
        cursor = self.collection.find({"status": status.value}).skip(skip).limit(limit)
        tasks = []
        async for task_dict in cursor:
            task_dict["id"] = str(task_dict.pop("_id"))
            tasks.append(Task.from_dict(task_dict))
        return tasks
    
    async def find_by_agent_id(self, agent_id: str) -> List[Task]:
        """Find tasks assigned to an agent"""
        cursor = self.collection.find({"agent_id": agent_id})
        tasks = []
        async for task_dict in cursor:
            task_dict["id"] = str(task_dict.pop("_id"))
            tasks.append(Task.from_dict(task_dict))
        return tasks
    
    async def update(self, task: Task) -> Optional[Task]:
        """Update an existing task"""
        task_dict = task.to_dict()
        task_id = task_dict.pop("id")
        task_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": task_dict}
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(task_id)
        return None
    
    async def update_status(self, task_id: str, status: TaskStatus, 
                          progress: float = None, speed: float = None,
                          error: str = None) -> Optional[Task]:
        """Update task status"""
        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow()
        }
        
        if progress is not None:
            update_data["progress"] = progress
        
        if speed is not None:
            update_data["speed"] = speed
            
        if error is not None:
            update_data["error"] = error
            
        if status == TaskStatus.RUNNING and progress == 0:
            update_data["started_at"] = datetime.utcnow()
            
        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(task_id)
        return None
    
    async def delete(self, task_id: str) -> bool:
        """Delete a task"""
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
    async def assign_to_agent(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign task to an agent"""
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$set": {
                    "agent_id": agent_id,
                    "status": TaskStatus.ASSIGNED.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(task_id)
        return None
    
    async def add_recovered_hash(self, task_id: str, hash_value: str, plaintext: str) -> Optional[Task]:
        """Add a recovered hash to the task"""
        recovered_hash = {
            "hash": hash_value,
            "plaintext": plaintext,
            "cracked_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(task_id)},
            {
                "$push": {"recovered_hashes": recovered_hash},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(task_id)
        return None
    
    async def find_next_pending_task(self) -> Optional[Task]:
        """Find the next pending task based on priority"""
        task_dict = await self.collection.find_one(
            {"status": TaskStatus.PENDING.value},
            sort=[("priority", -1), ("created_at", 1)]
        )
        
        if task_dict:
            task_dict["id"] = str(task_dict.pop("_id"))
            return Task.from_dict(task_dict)
        return None
