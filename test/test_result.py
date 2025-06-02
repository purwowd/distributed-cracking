import pytest
from datetime import datetime
from entity.result import Result


def test_result_creation():
    """Test result creation and properties"""
    result = Result(
        task_id="task123",
        hash_value="5f4dcc3b5aa765d61d8327deb882cf99",
        plaintext="password",
        agent_id="agent456"
    )
    
    assert result.task_id == "task123"
    assert result.hash_value == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert result.plaintext == "password"
    assert result.agent_id == "agent456"
    assert isinstance(result.cracked_at, datetime)
    assert result.metadata == {}


def test_result_to_dict():
    """Test result to dictionary conversion"""
    cracked_time = datetime.utcnow()
    result = Result(
        id="789",
        task_id="task123",
        hash_value="5f4dcc3b5aa765d61d8327deb882cf99",
        plaintext="password",
        agent_id="agent456",
        cracked_at=cracked_time
    )
    
    result_dict = result.to_dict()
    
    assert result_dict["id"] == "789"
    assert result_dict["task_id"] == "task123"
    assert result_dict["hash_value"] == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert result_dict["plaintext"] == "password"
    assert result_dict["agent_id"] == "agent456"
    assert result_dict["cracked_at"] == cracked_time


def test_result_from_dict():
    """Test creating result from dictionary"""
    cracked_time = datetime.utcnow()
    result_dict = {
        "id": "789",
        "task_id": "task123",
        "hash_value": "5f4dcc3b5aa765d61d8327deb882cf99",
        "plaintext": "password",
        "agent_id": "agent456",
        "cracked_at": cracked_time,
        "metadata": {"source": "wordlist1"}
    }
    
    result = Result.from_dict(result_dict)
    
    assert result.id == "789"
    assert result.task_id == "task123"
    assert result.hash_value == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert result.plaintext == "password"
    assert result.agent_id == "agent456"
    assert result.cracked_at == cracked_time
    assert result.metadata == {"source": "wordlist1"}
