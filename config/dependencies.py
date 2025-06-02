"""
Dependency injection for FastAPI.
This module provides functions to get the appropriate repository and usecase instances
based on whether we're using mock database or real MongoDB.
"""

import os
from typing import Optional

from fastapi import Depends

from config.database import Database
from config.mock_database import mock_db
from repository.task_repository import TaskRepository
from repository.agent_repository import AgentRepository
from repository.result_repository import ResultRepository
from usecase.task_usecase import TaskUseCase
from usecase.agent_usecase import AgentUseCase
from usecase.result_usecase import ResultUseCase
from usecase.mock_usecases import MockTaskUseCase, MockAgentUseCase, MockResultUseCase

# Check if we should use mock database
USE_MOCK = os.getenv("USE_MOCK_DATABASE", "true").lower() == "true"

# MongoDB database instance
db_instance: Optional[object] = None


async def get_database():
    """Get database instance (MongoDB or mock)"""
    global db_instance
    
    if USE_MOCK:
        return mock_db
    
    if db_instance is None:
        db_instance = await Database.connect()
    
    return db_instance


async def get_task_repository(db=Depends(get_database)):
    """Get task repository instance"""
    if USE_MOCK:
        return None  # Mock usecases don't use repositories
    return TaskRepository(db)


async def get_agent_repository(db=Depends(get_database)):
    """Get agent repository instance"""
    if USE_MOCK:
        return None  # Mock usecases don't use repositories
    return AgentRepository(db)


async def get_result_repository(db=Depends(get_database)):
    """Get result repository instance"""
    if USE_MOCK:
        return None  # Mock usecases don't use repositories
    return ResultRepository(db)


async def get_task_usecase(
    task_repo=Depends(get_task_repository),
    agent_repo=Depends(get_agent_repository),
    result_repo=Depends(get_result_repository)
):
    """Get task usecase instance"""
    if USE_MOCK:
        return MockTaskUseCase()
    return TaskUseCase(task_repo, agent_repo, result_repo)


async def get_agent_usecase(
    agent_repo=Depends(get_agent_repository),
    task_repo=Depends(get_task_repository)
):
    """Get agent usecase instance"""
    if USE_MOCK:
        return MockAgentUseCase()
    return AgentUseCase(agent_repo, task_repo)


async def get_result_usecase(
    result_repo=Depends(get_result_repository)
):
    """Get result usecase instance"""
    if USE_MOCK:
        return MockResultUseCase()
    return ResultUseCase(result_repo)
