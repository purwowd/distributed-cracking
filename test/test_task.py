import pytest
from datetime import datetime
from entity.task import Task, TaskStatus, HashType


def test_task_creation():
    """Test task creation and properties"""
    task = Task(
        name="Test Task",
        description="A test task",
        hash_type=HashType.MD5,
        hash_type_id=0,
        hashes=["5f4dcc3b5aa765d61d8327deb882cf99"],
        wordlist_path="/path/to/wordlist.txt",
        attack_mode=0,
        priority=1
    )
    
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.hash_type == HashType.MD5
    assert task.hash_type_id == 0
    assert task.hashes == ["5f4dcc3b5aa765d61d8327deb882cf99"]
    assert task.wordlist_path == "/path/to/wordlist.txt"
    assert task.attack_mode == 0
    assert task.priority == 1
    assert task.status == TaskStatus.PENDING
    assert task.agent_id is None
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_to_dict():
    """Test task to dictionary conversion"""
    task = Task(
        id="123",
        name="Test Task",
        hash_type=HashType.MD5,
        hashes=["5f4dcc3b5aa765d61d8327deb882cf99"]
    )
    
    task_dict = task.to_dict()
    
    assert task_dict["id"] == "123"
    assert task_dict["name"] == "Test Task"
    assert task_dict["hash_type"] == "md5"
    assert task_dict["hashes"] == ["5f4dcc3b5aa765d61d8327deb882cf99"]
    assert task_dict["status"] == "pending"


def test_task_from_dict():
    """Test creating task from dictionary"""
    task_dict = {
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "progress": 0.0,
        "speed": None,
        "recovered_hashes": [],
        "error": None,
        "metadata": {}
    }
    
    task = Task.from_dict(task_dict)
    
    assert task.id == "123"
    assert task.name == "Test Task"
    assert task.description == "A test task"
    assert task.hash_type == HashType.MD5
    assert task.hash_type_id == 0
    assert task.hashes == ["5f4dcc3b5aa765d61d8327deb882cf99"]
    assert task.status == TaskStatus.PENDING
