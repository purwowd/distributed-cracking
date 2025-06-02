import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from cmd.server import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_task_usecase():
    """Create a mock task usecase"""
    with patch("cmd.server.get_task_usecase") as mock:
        yield mock


@pytest.fixture
def mock_agent_usecase():
    """Create a mock agent usecase"""
    with patch("cmd.server.get_agent_usecase") as mock:
        yield mock


@pytest.fixture
def mock_result_usecase():
    """Create a mock result usecase"""
    with patch("cmd.server.get_result_usecase") as mock:
        yield mock


def test_create_task(client, mock_task_usecase):
    """Test creating a task via API"""
    # Setup mock
    mock_task = MagicMock()
    mock_task.to_dict.return_value = {
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
    mock_task_usecase.return_value.create_task.return_value = mock_task
    
    # Make request
    response = client.post(
        "/tasks",
        json={
            "name": "Test Task",
            "description": "A test task",
            "hash_type": "md5",
            "hashes": ["5f4dcc3b5aa765d61d8327deb882cf99"],
            "wordlist_path": "/path/to/wordlist.txt",
            "attack_mode": 0,
            "priority": 1
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "123"
    assert data["name"] == "Test Task"
    assert data["status"] == "pending"


def test_get_tasks(client, mock_task_usecase):
    """Test getting tasks via API"""
    # Setup mock
    mock_task1 = MagicMock()
    mock_task1.to_dict.return_value = {
        "id": "123",
        "name": "Task 1",
        "description": "",
        "hash_type": "md5",
        "status": "pending",
        "hashes": ["hash1"],
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
        "progress": 0.0,
        "recovered_hashes": []
    }
    mock_task2 = MagicMock()
    mock_task2.to_dict.return_value = {
        "id": "456",
        "name": "Task 2",
        "description": "",
        "hash_type": "sha1",
        "status": "running",
        "hashes": ["hash2"],
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
        "progress": 0.5,
        "recovered_hashes": []
    }
    mock_task_usecase.return_value.get_all_tasks.return_value = [mock_task1, mock_task2]
    
    # Make request
    response = client.get("/tasks")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "123"
    assert data[0]["name"] == "Task 1"
    assert data[1]["id"] == "456"
    assert data[1]["name"] == "Task 2"


def test_register_agent(client, mock_agent_usecase):
    """Test registering an agent via API"""
    # Setup mock
    mock_agent = MagicMock()
    mock_agent.to_dict.return_value = {
        "id": "789",
        "name": "Test Agent",
        "hostname": "gpu-server-01",
        "ip_address": "192.168.1.100",
        "api_key": "test_api_key",
        "status": "online",
        "capabilities": {},
        "current_task_id": None,
        "last_seen": "2025-01-01T00:00:00",
        "registered_at": "2025-01-01T00:00:00",
        "gpu_info": [{"name": "NVIDIA RTX 3090"}],
        "cpu_info": {},
        "hashcat_version": "6.2.5",
        "metadata": {}
    }
    mock_agent_usecase.return_value.register_agent.return_value = mock_agent
    
    # Make request
    response = client.post(
        "/agents",
        json={
            "name": "Test Agent",
            "hostname": "gpu-server-01",
            "ip_address": "192.168.1.100"
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "789"
    assert data["name"] == "Test Agent"
    assert data["status"] == "online"
    assert data["api_key"] == "test_api_key"
