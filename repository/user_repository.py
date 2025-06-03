from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, PyMongoError

from entity.user import User, UserRole
from exception.repository_exception import (
    EntityNotFoundException,
    DuplicateEntityException,
    DatabaseOperationException
)


class UserRepository:
    """Repository for user management"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.users
    
    async def initialize(self):
        """Initialize the repository with indexes"""
        await self.collection.create_index("username", unique=True)
        await self.collection.create_index("email", unique=True)
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        try:
            user_dict = user.to_dict()
            # Remove ID if it's None
            if user_dict.get("id") is None:
                user_dict.pop("id", None)
                
            result = await self.collection.insert_one(user_dict)
            user.id = str(result.inserted_id)
            return user
        except DuplicateKeyError as e:
            raise DuplicateEntityException(
                entity_type="User",
                field="username or email",
                value=f"{user.username}, {user.email}"
            ) from e
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="create",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        try:
            user_dict = await self.collection.find_one({"_id": user_id})
            if user_dict:
                user_dict["id"] = str(user_dict.pop("_id"))
                return User.from_dict(user_dict)
            return None
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_by_id",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        try:
            # Handle both MongoDB collection and mock database list
            if hasattr(self.collection, "find_one"):
                user_dict = await self.collection.find_one({"username": username})
                if user_dict:
                    user_dict["id"] = str(user_dict.pop("_id"))
                    return User.from_dict(user_dict)
            else:
                # For mock database, collection is a list
                for user_dict in self.collection:
                    if user_dict.get("username") == username:
                        return User.from_dict(user_dict)
            return None
        except Exception as e:
            raise DatabaseOperationException(
                operation="find_by_username",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        try:
            user_dict = await self.collection.find_one({"email": email})
            if user_dict:
                user_dict["id"] = str(user_dict.pop("_id"))
                return User.from_dict(user_dict)
            return None
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_by_email",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find all users with pagination"""
        try:
            users = []
            cursor = self.collection.find().skip(skip).limit(limit)
            async for user_dict in cursor:
                user_dict["id"] = str(user_dict.pop("_id"))
                users.append(User.from_dict(user_dict))
            return users
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="find_all",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def update(self, user: User) -> Optional[User]:
        """Update an existing user"""
        try:
            user_dict = user.to_dict()
            user_id = user_dict.pop("id")
            
            result = await self.collection.update_one(
                {"_id": user_id},
                {"$set": user_dict}
            )
            
            if result.matched_count == 0:
                raise EntityNotFoundException(
                    entity_type="User",
                    entity_id=user_id
                )
                
            return user
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="update",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            result = await self.collection.delete_one({"_id": user_id})
            if result.deleted_count == 0:
                raise EntityNotFoundException(
                    entity_type="User",
                    entity_id=user_id
                )
            return True
        except PyMongoError as e:
            raise DatabaseOperationException(
                operation="delete",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def update_last_login(self, username: str) -> Optional[User]:
        """Update user's last login timestamp"""
        try:
            # Handle both MongoDB collection and mock database list
            if hasattr(self.collection, "update_one"):
                result = await self.collection.update_one(
                    {"username": username},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
                
                if result.matched_count == 0:
                    raise EntityNotFoundException(
                        entity_type="User",
                        entity_id=username
                    )
            else:
                # For mock database, collection is a list
                user_found = False
                for i, user_dict in enumerate(self.collection):
                    if user_dict.get("username") == username:
                        self.collection[i]["last_login"] = datetime.utcnow()
                        user_found = True
                        break
                        
                if not user_found:
                    raise EntityNotFoundException(
                        entity_type="User",
                        entity_id=username
                    )
            
            return await self.find_by_username(username)
        except Exception as e:
            raise DatabaseOperationException(
                operation="update_last_login",
                entity_type="User",
                details=str(e)
            ) from e
    
    async def count(self) -> int:
        """Count total number of users"""
        try:
            # Handle both MongoDB collection and mock database list
            if hasattr(self.collection, "count_documents"):
                return await self.collection.count_documents({})
            else:
                # For mock database, collection is a list
                return len(self.collection)
        except Exception as e:
            raise DatabaseOperationException(
                operation="count",
                entity_type="User",
                details=str(e)
            ) from e
