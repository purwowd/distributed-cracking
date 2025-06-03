#!/usr/bin/env python3
"""
Script untuk memperbaiki pengujian API dengan mock yang tepat
"""
import os
import shutil
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project directory
PROJECT_DIR = Path(os.getcwd())
ORIGINAL_CMD_PATH = PROJECT_DIR / "cmd"
TEMP_CMD_PATH = PROJECT_DIR / "_cmd_temp"

def setup():
    """Persiapkan lingkungan pengujian"""
    logger.info("Temporarily renaming cmd folder to _cmd_temp...")
    
    # Rename cmd folder to avoid import conflicts
    if ORIGINAL_CMD_PATH.exists() and not TEMP_CMD_PATH.exists():
        shutil.move(ORIGINAL_CMD_PATH, TEMP_CMD_PATH)
    
    # Add current directory to Python path
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))

def cleanup():
    """Bersihkan lingkungan pengujian"""
    logger.info("Cleaning up temporary files and restoring cmd folder...")
    
    # Restore cmd folder
    if TEMP_CMD_PATH.exists() and not ORIGINAL_CMD_PATH.exists():
        shutil.move(TEMP_CMD_PATH, ORIGINAL_CMD_PATH)

# ===================== MOCKS FOR TESTING =====================

class MockCollection(AsyncMock):
    """Mock untuk MongoDB collection dengan metode async"""
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.collection_name = name
        
        # Default values
        self.find_one.return_value = {"_id": "123", "name": "Test"}
        
        # Set ID berdasarkan tipe collection
        if name == "agents":
            self.insert_one.return_value = MagicMock(inserted_id="agent123")
        else:
            self.insert_one.return_value = MagicMock(inserted_id="123")
        
        # Setup mock untuk find() yang mendukung skip, limit, dan cursor async
        find_cursor = AsyncMock()
        
        # Implement __aiter__ for find cursor
        async def async_iter():
            items = [
                {"_id": "123", "name": "Test Item 1"},
                {"_id": "456", "name": "Test Item 2"}
            ]
            for item in items:
                yield item
        
        find_cursor.__aiter__.return_value = async_iter()
        
        # Make find() return a non-coroutine that has chainable methods
        self.find = MagicMock()
        self.find.return_value = find_cursor
        find_cursor.skip = MagicMock(return_value=find_cursor)
        find_cursor.limit = MagicMock(return_value=find_cursor)
        find_cursor.sort = MagicMock(return_value=find_cursor)

class MockDatabase:
    """Mock untuk MongoDB database"""
    def __init__(self):
        self.agents = MockCollection(name="agents")
        self.tasks = MockCollection(name="tasks")
        self.users = MockCollection(name="users")
        self.results = MockCollection(name="results")
    
    @staticmethod
    def get_database():
        return MockDatabase()

# ===================== TASK USECASE MOCKS =====================

def setup_task_usecase_mock():
    """Setup mock untuk TaskUseCase"""
    # Create task entity dengan data lengkap
    from entity.task import Task
    
    task_data = {
        "id": "123",
        "name": "Test Task",
        "description": "A test task",
        "hash_type": "md5",
        "hash_type_id": 0,
        "hashes": ["5f4dcc3b5aa765d61d8327deb882cf99"],
        "wordlist_path": "/path/to/wordlist.txt",
        "rule_path": None,
        "mask": None,
        "attack_mode": 0,
        "additional_args": None,
        "priority": 1,
        "status": "pending",
        "agent_id": None,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
        "started_at": None,
        "completed_at": None,
        "progress": 0.0,
        "speed": None,
        "recovered_hashes": [],
        "error": None,
        "metadata": {}
    }
    
    # Create direct mock response untuk TaskUseCase
    task_usecase_mock = AsyncMock()
    
    # Setup mock create_task
    complete_task = Task(**task_data)
    # Override to_dict untuk mengembalikan data yang diharapkan
    complete_task.to_dict = lambda: task_data
    task_usecase_mock.create_task.return_value = complete_task
    
    # Setup mock get_paginated_tasks untuk mengembalikan nilai langsung
    task_usecase_mock.get_paginated_tasks.return_value = {
        "items": [task_data, {**task_data, "id": "456", "name": "Task 2", "status": "running"}],
        "total": 2,
        "page": 1,
        "size": 10,
        "pages": 1
    }
    
    return task_usecase_mock

# ===================== AGENT USECASE MOCKS =====================

def setup_agent_usecase_mock():
    """Setup mock untuk AgentUseCase"""
    from entity.agent import Agent
    
    agent_data = {
        "id": "agent123",
        "name": "Test Agent",
        "hostname": "test-host",
        "ip_address": "192.168.1.100",
        "status": "online",
        "last_seen": "2023-01-01T00:00:00"
    }
    
    agent_usecase_mock = AsyncMock()
    
    # Setup mock register_agent
    complete_agent = Agent.from_dict(agent_data)
    # Override to_dict untuk mengembalikan data yang diharapkan
    complete_agent.to_dict = lambda: agent_data
    agent_usecase_mock.register_agent.return_value = complete_agent
    
    # Setup mock get_paginated_agents
    agent_usecase_mock.get_paginated_agents.return_value = {
        "items": [agent_data, {**agent_data, "id": "agent456", "name": "Agent 2", "status": "offline"}],
        "total": 2,
        "page": 1,
        "size": 10,
        "pages": 1
    }
    
    return agent_usecase_mock

# ===================== MOCKED TEST CLIENT =====================

@pytest.fixture
def client():
    """Create test client dengan mocks untuk dependencies"""
    # Import app
    from _cmd_temp.server import app
    
    # Mock database
    with patch("_cmd_temp.server.get_database", return_value=MockDatabase()):
        # Mock authentication
        with patch("_cmd_temp.server.oauth2_scheme", return_value="test_token"):
            with patch("_cmd_temp.server.jwt.decode", return_value={"sub": "admin", "is_admin": True}):
                with patch("_cmd_temp.server.get_current_active_user", return_value={"username": "admin", "is_admin": True}):
                    # Mock usecases
                    with patch("_cmd_temp.server.get_task_usecase", return_value=setup_task_usecase_mock()):
                        with patch("_cmd_temp.server.get_agent_usecase", return_value=setup_agent_usecase_mock()):
                            # Create test client
                            return TestClient(app)

# ===================== TEST CASES =====================

def test_register_agent(client):
    """Test untuk mendaftarkan agent melalui API"""
    response = client.post(
        "/agents/register",
        json={
            "name": "Test Agent",
            "hostname": "test-host",
            "ip_address": "192.168.1.100"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Debug output
    print(f"Register agent response: {response.status_code}")
    if response.status_code != 200:
        print(response.json())
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "agent123"
    assert data["name"] == "Test Agent"

def test_get_agents(client):
    """Test untuk mendapatkan daftar agent melalui API"""
    response = client.get(
        "/agents",
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Debug output
    print(f"Get agents response: {response.status_code}")
    if response.status_code != 200:
        print(response.json())
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "agent123"

def test_create_task(client):
    """Test untuk membuat task melalui API"""
    response = client.post(
        "/tasks",
        json={
            "name": "Test Task",
            "description": "A test task",
            "hash_type": "md5",
            "hash_type_id": 0,
            "hashes": ["5f4dcc3b5aa765d61d8327deb882cf99"],
            "wordlist_path": "/path/to/wordlist.txt",
            "rule_path": None,
            "mask": None,
            "attack_mode": 0,
            "additional_args": None,
            "priority": 1
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Debug output
    print(f"Create task response: {response.status_code}")
    if response.status_code != 200:
        print(response.json())
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Test Task"

def test_get_tasks(client):
    """Test untuk mendapatkan daftar task melalui API"""
    response = client.get(
        "/tasks",
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Debug output
    print(f"Get tasks response: {response.status_code}")
    if response.status_code != 200:
        print(response.json())
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "123"

# ===================== MAIN EXECUTION =====================

def run_tests():
    """Run pengujian API"""
    setup()
    try:
        # Run tests dengan pytest
        exit_code = pytest.main(["-xvs", __file__])
        return exit_code
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        exit_code = run_tests()
        print("\n=== Test Results ===")
        if exit_code == 0:
            print("✅ All API tests passed!")
        else:
            print("❌ API tests failed.")
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error running tests: {e}")
        cleanup()
        sys.exit(1)
