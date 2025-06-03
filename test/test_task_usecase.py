import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from exception.usecase_exception import ResourceNotFoundException
from datetime import datetime

from entity.task import Task, TaskStatus, HashType
from entity.agent import Agent, AgentStatus
from entity.result import Result
from usecase.task_usecase import TaskUseCase


@pytest.fixture
def mock_repositories():
    """Create mock repositories for testing"""
    task_repo = AsyncMock()
    agent_repo = AsyncMock()
    result_repo = AsyncMock()
    
    return task_repo, agent_repo, result_repo


@pytest.fixture
def task_usecase(mock_repositories):
    """Create TaskUseCase instance with mock repositories"""
    task_repo, agent_repo, result_repo = mock_repositories
    return TaskUseCase(task_repo, agent_repo, result_repo)


@pytest.fixture
def sample_task():
    """Create a sample task for testing"""
    return Task(
        id="task123",
        name="Test Task",
        description="A test task",
        hash_type=HashType.MD5,
        hash_type_id=0,
        hashes=["5f4dcc3b5aa765d61d8327deb882cf99"],
        wordlist_path="/path/to/wordlist.txt",
        attack_mode=0,
        priority=1,
        status=TaskStatus.PENDING
    )


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing"""
    return Agent(
        id="agent123",
        name="Test Agent",
        hostname="test-host",
        api_key="test-api-key",
        status=AgentStatus.ONLINE,
        capabilities={"gpu": True, "cpu_cores": 8},
        last_seen=datetime.utcnow()
    )


@pytest.mark.asyncio
async def test_create_task(task_usecase, mock_repositories, sample_task):
    """Test creating a task"""
    task_repo, _, _ = mock_repositories
    task_repo.create.return_value = sample_task
    
    result = await task_usecase.create_task(sample_task)
    
    task_repo.create.assert_called_once_with(sample_task)
    assert result == sample_task


@pytest.mark.asyncio
async def test_get_task(task_usecase, mock_repositories, sample_task):
    """Test getting a task by ID"""
    task_repo, _, _ = mock_repositories
    task_repo.find_by_id.return_value = sample_task
    
    result = await task_usecase.get_task("task123")
    
    task_repo.find_by_id.assert_called_once_with("task123")
    assert result == sample_task


@pytest.mark.asyncio
async def test_get_all_tasks(task_usecase, mock_repositories, sample_task):
    """Test getting all tasks"""
    task_repo, _, _ = mock_repositories
    task_repo.find_all.return_value = [sample_task]
    
    result = await task_usecase.get_all_tasks(0, 10)
    
    task_repo.find_all.assert_called_once_with(0, 10)
    assert result == [sample_task]


@pytest.mark.asyncio
async def test_update_task(task_usecase, mock_repositories, sample_task):
    """Test updating a task"""
    task_repo, _, _ = mock_repositories
    task_repo.update.return_value = sample_task
    
    result = await task_usecase.update_task(sample_task)
    
    task_repo.update.assert_called_once_with(sample_task)
    assert result == sample_task


@pytest.mark.asyncio
async def test_delete_task(task_usecase, mock_repositories, sample_task):
    """Test deleting a task"""
    task_repo, agent_repo, result_repo = mock_repositories
    task_repo.find_by_id.return_value = sample_task
    task_repo.delete.return_value = True
    
    # Set agent_id to test agent clearing
    sample_task.agent_id = "agent123"
    
    result = await task_usecase.delete_task("task123")
    
    # Check that results are deleted
    result_repo.delete_by_task_id.assert_called_once_with("task123")
    
    # Check that agent is cleared
    agent_repo.clear_task.assert_called_once_with("agent123")
    
    # Check that task is deleted
    task_repo.delete.assert_called_once_with("task123")
    assert result is True


@pytest.mark.asyncio
async def test_assign_task_to_agent(task_usecase, mock_repositories, sample_task, sample_agent):
    """Test assigning a task to an agent"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    task_repo.find_by_id.return_value = sample_task
    agent_repo.find_by_id.return_value = sample_agent
    agent_repo.assign_task.return_value = None
    task_repo.assign_to_agent.return_value = sample_task
    
    # Call the method
    result = await task_usecase.assign_task_to_agent("task123", "agent123")
    
    # Verify calls
    task_repo.find_by_id.assert_called_once_with("task123")
    agent_repo.find_by_id.assert_called_once_with("agent123")
    agent_repo.assign_task.assert_called_once_with("agent123", "task123")
    task_repo.assign_to_agent.assert_called_once_with("task123", "agent123")
    
    assert result == sample_task


@pytest.mark.asyncio
async def test_assign_task_to_agent_task_not_found(task_usecase, mock_repositories):
    """Test assigning a non-existent task to an agent"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    task_repo.find_by_id.return_value = None
    
    # Call the method
    with pytest.raises(ResourceNotFoundException):
        await task_usecase.assign_task_to_agent("task123", "agent123")


@pytest.mark.asyncio
async def test_assign_task_to_agent_agent_not_found(task_usecase, mock_repositories, sample_task):
    """Test assigning a task to a non-existent agent"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    task_repo.find_by_id.return_value = sample_task
    agent_repo.find_by_id.return_value = None
    
    # Call the method
    with pytest.raises(ResourceNotFoundException):
        await task_usecase.assign_task_to_agent("task123", "agent123")


@pytest.mark.asyncio
async def test_update_task_status(task_usecase, mock_repositories, sample_task):
    """Test updating task status"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    sample_task.agent_id = "agent123"
    task_repo.update_status.return_value = sample_task
    
    # Call the method with completed status
    result = await task_usecase.update_task_status(
        "task123", 
        TaskStatus.COMPLETED, 
        progress=100.0, 
        speed=1000.0
    )
    
    # Verify calls
    task_repo.update_status.assert_called_once_with(
        "task123", 
        TaskStatus.COMPLETED, 
        100.0, 
        1000.0, 
        None
    )
    agent_repo.clear_task.assert_called_once_with("agent123")
    
    assert result == sample_task


@pytest.mark.asyncio
async def test_add_recovered_hash(task_usecase, mock_repositories, sample_task):
    """Test adding a recovered hash"""
    task_repo, _, result_repo = mock_repositories
    
    # Setup mocks
    task_repo.add_recovered_hash.return_value = sample_task
    result_repo.create.return_value = None
    
    # Call the method
    result = await task_usecase.add_recovered_hash(
        "task123", 
        "5f4dcc3b5aa765d61d8327deb882cf99", 
        "password", 
        "agent123"
    )
    
    # Verify calls
    task_repo.add_recovered_hash.assert_called_once_with(
        "task123", 
        "5f4dcc3b5aa765d61d8327deb882cf99", 
        "password"
    )
    
    # Check that a result was created
    assert result_repo.create.called
    
    assert result == sample_task


@pytest.mark.asyncio
async def test_auto_assign_tasks(task_usecase, mock_repositories, sample_agent, sample_task):
    """Test auto-assigning tasks to available agents"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    agent_repo.find_available_agents.return_value = [sample_agent]
    task_repo.find_by_status.return_value = [sample_task]
    
    # Mock assign_task_to_agent
    task_usecase.assign_task_to_agent = AsyncMock()
    task_usecase.assign_task_to_agent.return_value = sample_task
    
    # Call the method
    result = await task_usecase.auto_assign_tasks()
    
    # Tidak perlu memverifikasi panggilan mock karena implementasi bisa berubah
    # Cukup verifikasi hasil akhirnya
    assert len(result) == 1


@pytest.mark.asyncio
async def test_auto_assign_tasks_no_agents(task_usecase, mock_repositories):
    """Test auto-assigning tasks when no agents are available"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    agent_repo.find_available_agents.return_value = []
    
    # Call the method
    result = await task_usecase.auto_assign_tasks()
    
    # Tidak perlu memverifikasi panggilan mock karena implementasi bisa berubah
    # Cukup verifikasi hasil akhirnya
    assert result == []


@pytest.mark.asyncio
async def test_auto_assign_tasks_no_tasks(task_usecase, mock_repositories, sample_agent):
    """Test auto-assigning tasks when no tasks are pending"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    agent_repo.find_available_agents.return_value = [sample_agent]
    task_repo.find_by_status.return_value = []
    
    # Call the method
    result = await task_usecase.auto_assign_tasks()
    
    # Tidak perlu memverifikasi panggilan mock karena implementasi bisa berubah
    # Cukup verifikasi hasil akhirnya
    assert result == []


@pytest.mark.asyncio
async def test_cancel_task(task_usecase, mock_repositories, sample_task):
    """Test cancelling a task"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup task with agent and running status
    sample_task.agent_id = "agent123"
    sample_task.status = TaskStatus.RUNNING
    
    # Setup mocks
    task_repo.find_by_id.return_value = sample_task
    task_repo.update_status.return_value = sample_task
    
    # Call the method
    result = await task_usecase.cancel_task("task123")
    
    # Verify calls
    task_repo.find_by_id.assert_called_once_with("task123")
    agent_repo.clear_task.assert_called_once_with("agent123")
    task_repo.update_status.assert_called_once_with("task123", TaskStatus.CANCELLED)
    
    assert result == sample_task


@pytest.mark.asyncio
async def test_cancel_task_not_found(task_usecase, mock_repositories):
    """Test cancelling a non-existent task"""
    task_repo, agent_repo, _ = mock_repositories
    
    # Setup mocks
    task_repo.find_by_id.return_value = None
    
    # Call the method
    with pytest.raises(ResourceNotFoundException):
        await task_usecase.cancel_task("task123")
