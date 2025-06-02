import pytest
from datetime import datetime
from entity.agent import Agent, AgentStatus


def test_agent_creation():
    """Test agent creation and properties"""
    agent = Agent(
        name="Test Agent",
        hostname="gpu-server-01",
        ip_address="192.168.1.100",
        api_key="test_api_key",
        gpu_info=[{"name": "NVIDIA RTX 3090", "memory_total_mb": 24576}]
    )
    
    assert agent.name == "Test Agent"
    assert agent.hostname == "gpu-server-01"
    assert agent.ip_address == "192.168.1.100"
    assert agent.api_key == "test_api_key"
    assert agent.status == AgentStatus.OFFLINE
    assert agent.current_task_id is None
    assert isinstance(agent.last_seen, datetime)
    assert isinstance(agent.registered_at, datetime)
    assert len(agent.gpu_info) == 1
    assert agent.gpu_info[0]["name"] == "NVIDIA RTX 3090"


def test_agent_to_dict():
    """Test agent to dictionary conversion"""
    agent = Agent(
        id="123",
        name="Test Agent",
        hostname="gpu-server-01",
        ip_address="192.168.1.100",
        api_key="test_api_key",
        status=AgentStatus.ONLINE
    )
    
    agent_dict = agent.to_dict()
    
    assert agent_dict["id"] == "123"
    assert agent_dict["name"] == "Test Agent"
    assert agent_dict["hostname"] == "gpu-server-01"
    assert agent_dict["ip_address"] == "192.168.1.100"
    assert agent_dict["api_key"] == "test_api_key"
    assert agent_dict["status"] == "online"


def test_agent_from_dict():
    """Test creating agent from dictionary"""
    agent_dict = {
        "id": "123",
        "name": "Test Agent",
        "hostname": "gpu-server-01",
        "ip_address": "192.168.1.100",
        "api_key": "test_api_key",
        "status": "online",
        "capabilities": {},
        "current_task_id": None,
        "last_seen": datetime.utcnow(),
        "registered_at": datetime.utcnow(),
        "gpu_info": [{"name": "NVIDIA RTX 3090", "memory_total_mb": 24576}],
        "cpu_info": {"cores": 32},
        "hashcat_version": "6.2.5",
        "metadata": {}
    }
    
    agent = Agent.from_dict(agent_dict)
    
    assert agent.id == "123"
    assert agent.name == "Test Agent"
    assert agent.hostname == "gpu-server-01"
    assert agent.status == AgentStatus.ONLINE
    assert agent.hashcat_version == "6.2.5"


def test_agent_is_available():
    """Test agent availability check"""
    # Available agent
    agent1 = Agent(
        status=AgentStatus.ONLINE,
        current_task_id=None
    )
    assert agent1.is_available() is True
    
    # Busy agent
    agent2 = Agent(
        status=AgentStatus.ONLINE,
        current_task_id="task123"
    )
    assert agent2.is_available() is False
    
    # Offline agent
    agent3 = Agent(
        status=AgentStatus.OFFLINE,
        current_task_id=None
    )
    assert agent3.is_available() is False


def test_agent_update_heartbeat():
    """Test agent heartbeat update"""
    agent = Agent()
    old_timestamp = agent.last_seen
    
    # Wait a tiny bit to ensure timestamp changes
    import time
    time.sleep(0.001)
    
    agent.update_heartbeat()
    assert agent.last_seen > old_timestamp
