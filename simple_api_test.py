#!/usr/bin/env python3
"""
Script sederhana untuk menjalankan test API dengan mocking yang tepat
"""
import os
import sys
import shutil
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock, Mock
from fastapi.testclient import TestClient
from typing import List, Dict, Any, Optional, AsyncIterator
import importlib
from contextlib import contextmanager, ExitStack

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Project directory
PROJECT_DIR = Path(os.getcwd())
ORIGINAL_CMD_PATH = PROJECT_DIR / "cmd"
TEMP_CMD_PATH = PROJECT_DIR / "_cmd_temp"

def setup_environment():
    """Persiapkan lingkungan pengujian"""
    logger.info("Temporarily renaming cmd folder to _cmd_temp...")
    
    # Rename cmd folder to avoid import conflicts
    if ORIGINAL_CMD_PATH.exists() and not TEMP_CMD_PATH.exists():
        shutil.move(ORIGINAL_CMD_PATH, TEMP_CMD_PATH)
    
    # Add current directory to Python path
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))

def cleanup_environment():
    """Bersihkan lingkungan pengujian"""
    logger.info("Cleaning up temporary files and restoring cmd folder...")
    
    # Restore cmd folder
    if TEMP_CMD_PATH.exists() and not ORIGINAL_CMD_PATH.exists():
        shutil.move(TEMP_CMD_PATH, ORIGINAL_CMD_PATH)

# ===================== MOCK CLASSES =====================

class MockUser:
    """Mock user entity for authentication"""
    def __init__(self, id="123", username="test_user", email="test@example.com"):
        self.id = id
        self.username = username
        self.email = email
        self.is_active = True
        self.is_admin = True
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin
        }

class MockEntity:
    """Base class untuk entity mock dengan to_dict method"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

# Task entity mock
class MockTask(MockEntity):
    """Mock untuk entity Task"""
    pass

# Agent entity mock
class MockAgent(MockEntity):
    """Mock untuk entity Agent"""
    pass

# ===================== MOCK USE CASES =====================

class MockTaskUseCase:
    """Mock untuk TaskUseCase"""
    async def create_task(self, task):
        """Mock create_task method"""
        mock_task = MockTask(
            id="123",
            name=task.name,
            description=task.description,
            hash_type=task.hash_type,
            hash_type_id=task.hash_type_id,
            hashes=task.hashes,
            wordlist_path=task.wordlist_path,
            rule_path=task.rule_path,
            mask=task.mask,
            attack_mode=task.attack_mode,
            additional_args=task.additional_args,
            priority=task.priority,
            status="pending",
            agent_id=None,
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00"
        )
        return mock_task
    
    async def get_paginated_tasks(self, *args, **kwargs):
        """Mock get_paginated_tasks method"""
        mock_task1 = MockTask(
            id="123",
            name="Task 1",
            description="Test task 1",
            hash_type="md5",
            hash_type_id=0,
            status="pending"
        )
        
        mock_task2 = MockTask(
            id="456",
            name="Task 2",
            description="Test task 2",
            hash_type="sha1",
            hash_type_id=100,
            status="running"
        )
        
        return {
            "items": [mock_task1.to_dict(), mock_task2.to_dict()],
            "total": 2,
            "page": 1,
            "size": 10,
            "pages": 1
        }

class MockAgentUseCase:
    """Mock untuk AgentUseCase"""
    async def register_agent(self, agent):
        """Mock register_agent method"""
        mock_agent = MockAgent(
            id="agent123",
            name=agent.name,
            hostname=agent.hostname,
            ip_address=agent.ip_address,
            status="online",
            last_seen="2023-01-01T00:00:00"
        )
        return mock_agent
    
    async def get_paginated_agents(self, *args, **kwargs):
        """Mock get_paginated_agents method"""
        mock_agent1 = MockAgent(
            id="agent123",
            name="Agent 1",
            hostname="host1",
            ip_address="192.168.1.1",
            status="online"
        )
        
        mock_agent2 = MockAgent(
            id="agent456",
            name="Agent 2",
            hostname="host2",
            ip_address="192.168.1.2",
            status="offline"
        )
        
        return {
            "items": [mock_agent1.to_dict(), mock_agent2.to_dict()],
            "total": 2,
            "page": 1,
            "size": 10,
            "pages": 1
        }

class MockResultUseCase:
    """Mock untuk ResultUseCase"""
    async def get_paginated_results(self, *args, **kwargs):
        """Mock get_paginated_results method"""
        return {
            "items": [],
            "total": 0,
            "page": 1,
            "size": 10,
            "pages": 0
        }

# ===================== MOCK DATABASE =====================

class MockCollection:
    """Mock untuk MongoDB collection"""
    def __init__(self, name=None):
        self.name = name
        
        # Setup ID generator
        self.counter = 0
        
        # Setup ID override for agents collection
        if name == "agents":
            self.inserted_id = "agent123"
        else:
            self.inserted_id = "123"
    
    async def insert_one(self, document):
        """Mock insert_one method"""
        return MagicMock(inserted_id=self.inserted_id)
    
    async def find_one(self, query):
        """Mock find_one method"""
        if self.name == "users":
            # Return mock user for authentication
            if query.get("username") == "admin":
                return {
                    "_id": "user123",
                    "username": "admin",
                    "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                    "is_admin": True
                }
        return None
    
    async def update_one(self, query, update):
        """Mock update_one method"""
        return MagicMock(modified_count=1)
    
    def find(self, query=None):
        """Mock find method that returns a cursor with chainable methods"""
        cursor = AsyncMock()
        
        # Setup cursor methods
        cursor.skip.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.sort.return_value = cursor
        
        # Setup async iterator for cursor
        mock_data = []
        if self.name == "agents":
            mock_data = [
                {"_id": "agent123", "name": "Agent 1", "status": "online"},
                {"_id": "agent456", "name": "Agent 2", "status": "offline"}
            ]
        elif self.name == "tasks":
            mock_data = [
                {"_id": "123", "name": "Task 1", "status": "pending"},
                {"_id": "456", "name": "Task 2", "status": "running"}
            ]
        
        # Setup async iterator
        async def async_iter():
            for item in mock_data:
                yield item
        
        cursor.__aiter__.return_value = async_iter()
        return cursor

class MockDatabase:
    """Mock database dengan collections"""
    def __init__(self):
        self.agents = MockCollection(name="agents")
        self.tasks = MockCollection(name="tasks")
        self.users = MockCollection(name="users")
        self.results = MockCollection(name="results")

# ===================== SETUP DATABASE MOCK FUNCTION =====================

@contextmanager
def setup_database_mock():
    """Setup database mock for testing"""
    # Create a mock database
    mock_db = MockDatabase()
    
    # Create patchers
    db_patcher = patch('config.database.Database')
    
    try:
        # Start patchers
        MockDatabase_cls = db_patcher.start()
        
        # Configure mock class
        MockDatabase_cls.db = mock_db
        MockDatabase_cls.get_database.return_value = mock_db
        MockDatabase_cls.connect.return_value = None
        
        # Return the mock database
        yield mock_db
    finally:
        # Stop patchers
        db_patcher.stop()

# ===================== TEST CLIENT FIXTURE =====================

@pytest.fixture
def client(request):
    """Create test client with mocked dependencies"""
    # Temporarily rename cmd folder to avoid import conflicts
    if os.path.exists("cmd") and os.path.isdir("cmd"):
        os.rename("cmd", "_cmd_temp")
        logger.info("Renamed cmd folder to _cmd_temp")
    
    # Register cleanup
    def cleanup():
        if os.path.exists("_cmd_temp") and os.path.isdir("_cmd_temp"):
            if os.path.exists("cmd"):
                shutil.rmtree("cmd")
            os.rename("_cmd_temp", "cmd")
            logger.info("Cleaned up temporary files and restored cmd folder")
    
    # Add to pytest cleanup
    request.addfinalizer(cleanup)
    
    # Setup database mock BEFORE importing server module
    with setup_database_mock() as mock_db:
        # Now it's safe to import app
        sys.path.append(os.getcwd())
        from _cmd_temp.server import app
        
        # Create mock user for authentication
        mock_user = MockUser(id="123", username="test_user", email="test@example.com")
        mock_token = "test_token"
        
        # Create mock usecases
        task_usecase = MockTaskUseCase()
        agent_usecase = MockAgentUseCase()
        result_usecase = MockResultUseCase()
        
        # Import dependency functions yang digunakan dalam app
        from _cmd_temp.server import admin_required, get_current_active_user
        from _cmd_temp.server import get_db
        from _cmd_temp.server import get_task_usecase, get_agent_usecase, get_result_usecase
        from config.auth import oauth2_scheme
        
        # Override dependencies
        app.dependency_overrides = {
            # Auth dependencies - override langsung objek fungsi
            admin_required: lambda: mock_user,
            get_current_active_user: lambda: mock_user,
            
            # Database dependency - override get_db
            get_db: lambda: mock_db,
            
            # Usecase dependencies - override langsung
            get_task_usecase: lambda: task_usecase,
            get_agent_usecase: lambda: agent_usecase,
            get_result_usecase: lambda: result_usecase,
            
            # Auth token dependency
            oauth2_scheme: lambda: "test_token"
        }
        
        # Return test client
        yield TestClient(app)

# ===================== TEST CASES =====================

def test_register_agent(client):
    """Test register agent API endpoint"""
    response = client.post(
        "/agents",
        json={
            "name": "Test Agent",
            "hostname": "test-host",
            "ip_address": "192.168.1.100",
            "api_key": "test-api-key",
            "capabilities": {},
            "gpu_info": [{}],  # Harus berupa array/list of dictionaries
            "cpu_info": {},
            "hashcat_version": "6.2.6",
            "metadata": {}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    print(f"Register agent response: {response.status_code}")
    print(f"Response JSON: {response.json() if response.status_code < 300 else response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "agent123"
    assert data["name"] == "Test Agent"

def test_get_agents(client):
    """Test get agents API endpoint"""
    response = client.get(
        "/agents",
        headers={"Authorization": "Bearer test_token"}
    )
    
    print(f"Get agents response: {response.status_code}")
    print(f"Response JSON: {response.json() if response.status_code < 300 else response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "agent123"

def test_create_task(client):
    """Test create task API endpoint"""
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
    
    print(f"Create task response: {response.status_code}")
    print(f"Response JSON: {response.json() if response.status_code < 300 else response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Test Task"

def test_get_tasks(client):
    """Test get tasks API endpoint"""
    response = client.get(
        "/tasks",
        headers={"Authorization": "Bearer test_token"}
    )
    
    print(f"Get tasks response: {response.status_code}")
    print(f"Response JSON: {response.json() if response.status_code < 300 else response.text}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "123"

# ===================== MAIN FUNCTION =====================

def run_tests():
    """Run API tests"""
    setup_environment()
    
    try:
        # Run tests with pytest
        exit_code = pytest.main(["-xvs", __file__])
        return exit_code
    finally:
        # Always clean up
        cleanup_environment()

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
        cleanup_environment()
        sys.exit(1)
