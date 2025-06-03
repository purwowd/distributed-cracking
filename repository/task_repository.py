from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.errors import PyMongoError, DuplicateKeyError
from datetime import datetime
import traceback

from entity.task import Task, TaskStatus
from exception.repository_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    DatabaseConnectionException,
    DatabaseOperationException
)


class TaskRepository:
    """Repository for task data access"""
    
    def __init__(self, database):
        self.db = database
        self.collection = database.tasks
    
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        try:
            task_dict = task.to_dict()
            if task_dict.get("id"):
                task_dict["_id"] = ObjectId(task_dict.pop("id"))
            else:
                task_dict.pop("id", None)
            
            result = await self.collection.insert_one(task_dict)
            task.id = str(result.inserted_id)
            return task
        except DuplicateKeyError as e:
            raise DuplicateEntityException(
                entity_type="Task",
                key="name",
                value=task.name,
                details={"error": str(e)}
            )
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="create",
                message=str(e),
                details={"traceback": traceback.format_exc()}
            )
    
    async def find_by_id(self, id: str) -> Optional[Task]:
        """Find a task by ID"""
        try:
            task_dict = await self.collection.find_one({"_id": ObjectId(id)})
            if task_dict:
                task_dict["id"] = str(task_dict.pop("_id"))
                return Task.from_dict(task_dict)
            return None
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_by_id",
                message=str(e),
                details={"id": id, "traceback": traceback.format_exc()}
            )
        except Exception as e:
            # Handle invalid ObjectId format
            if "ObjectId" in str(e):
                return None
            raise
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Find all tasks with pagination"""
        try:
            cursor = self.collection.find().skip(skip).limit(limit)
            tasks = []
            async for task_dict in cursor:
                task_dict["id"] = str(task_dict.pop("_id"))
                tasks.append(Task.from_dict(task_dict))
            return tasks
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_all",
                message=str(e),
                details={"skip": skip, "limit": limit, "traceback": traceback.format_exc()}
            )
    
    async def count_all(self) -> int:
        """Count all tasks"""
        try:
            return await self.collection.count_documents({})
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="count_all",
                message=str(e),
                details={"traceback": traceback.format_exc()}
            )
    
    async def find_by_status(self, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
        """Find tasks by status"""
        try:
            cursor = self.collection.find({"status": status.value}).skip(skip).limit(limit)
            tasks = []
            async for task_dict in cursor:
                task_dict["id"] = str(task_dict.pop("_id"))
                tasks.append(Task.from_dict(task_dict))
            return tasks
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_by_status",
                message=str(e),
                details={"status": status.value, "skip": skip, "limit": limit, "traceback": traceback.format_exc()}
            )
    
    async def count_by_status(self, status: TaskStatus) -> int:
        """Count tasks by status"""
        try:
            return await self.collection.count_documents({"status": status.value})
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="count_by_status",
                message=str(e),
                details={"status": status.value, "traceback": traceback.format_exc()}
            )
    
    async def find_by_agent_id(self, agent_id: str) -> List[Task]:
        """Find tasks assigned to an agent"""
        try:
            cursor = self.collection.find({"agent_id": agent_id})
            tasks = []
            async for task_dict in cursor:
                task_dict["id"] = str(task_dict.pop("_id"))
                tasks.append(Task.from_dict(task_dict))
            return tasks
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_by_agent_id",
                message=str(e),
                details={"agent_id": agent_id, "traceback": traceback.format_exc()}
            )
    
    async def update(self, task: Task) -> Optional[Task]:
        """Update an existing task"""
        try:
            if not task.id:
                raise EntityNotFoundException(
                    entity_type="Task",
                    entity_id="None",
                    details={"error": "Task ID is required for update"}
                )
            
            task_dict = task.to_dict()
            task_id = ObjectId(task_dict.pop("id"))
            
            result = await self.collection.update_one(
                {"_id": task_id},
                {"$set": task_dict}
            )
            
            if result.matched_count == 0:
                raise EntityNotFoundException(
                    entity_type="Task",
                    entity_id=task.id,
                    details={"error": "Task not found for update"}
                )
                
            return task
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="update",
                message=str(e),
                details={"task_id": task.id, "traceback": traceback.format_exc()}
            )
    
    async def update_status(self, task_id: str, status: TaskStatus, 
                          progress: float = None, speed: float = None,
                          error: str = None) -> Optional[Task]:
        """Update task status"""
        try:
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
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="update_status",
                message=str(e),
                details={"task_id": task_id, "status": status.value, "traceback": traceback.format_exc()}
            )
    
    async def delete(self, id: str) -> bool:
        """Delete a task by ID"""
        try:
            result = await self.collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                raise EntityNotFoundException(
                    entity_type="Task",
                    entity_id=id,
                    details={"error": "Task not found for deletion"}
                )
            return True
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="delete",
                message=str(e),
                details={"task_id": id, "traceback": traceback.format_exc()}
            )
        except Exception as e:
            # Handle invalid ObjectId format
            if "ObjectId" in str(e):
                raise EntityNotFoundException(
                    entity_type="Task",
                    entity_id=id,
                    details={"error": "Invalid task ID format"}
                )
            raise
    
    async def assign_to_agent(self, task_id: str, agent_id: str) -> Optional[Task]:
        """Assign task to an agent"""
        try:
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
            
            if result.modified_count == 0:
                raise EntityNotFoundException(
                    entity_type="Task",
                    entity_id=task_id,
                    details={"error": "Task not found for assignment"}
                )
            return await self.find_by_id(task_id)
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="assign_to_agent",
                message=str(e),
                details={"task_id": task_id, "agent_id": agent_id, "traceback": traceback.format_exc()}
            )
    
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
