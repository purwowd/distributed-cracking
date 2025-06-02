import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.database import get_database, connect_to_db, close_db_connection


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_mongodb():
    """Mock MongoDB connection for testing"""
    mock_client = MagicMock(spec=AsyncIOMotorClient)
    mock_db = MagicMock(spec=AsyncIOMotorDatabase)
    mock_client.__getitem__.return_value = mock_db
    
    # Mock collections
    mock_tasks_collection = MagicMock()
    mock_agents_collection = MagicMock()
    mock_results_collection = MagicMock()
    
    # Set up the mock db to return our mock collections
    mock_db.tasks = mock_tasks_collection
    mock_db.agents = mock_agents_collection
    mock_db.results = mock_results_collection
    
    # Patch the database connection
    with patch('config.database.AsyncIOMotorClient', return_value=mock_client):
        await connect_to_db()
        yield mock_db
        await close_db_connection()


@pytest.fixture
def test_env_vars():
    """Setup test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
    os.environ["DATABASE_NAME"] = "hashcat_test"
    os.environ["SERVER_HOST"] = "localhost"
    os.environ["SERVER_PORT"] = "8000"
    os.environ["AGENT_POLL_INTERVAL"] = "10"
    os.environ["AGENT_HEARTBEAT_INTERVAL"] = "30"
    os.environ["AGENT_OFFLINE_THRESHOLD"] = "120"
    os.environ["HASHCAT_PATH"] = "/usr/bin/hashcat"
    os.environ["DEFAULT_HASHCAT_ARGS"] = "--status --status-timer=10"
    os.environ["TASK_CHUNK_SIZE"] = "1000"
    os.environ["TASK_TIMEOUT"] = "3600"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
