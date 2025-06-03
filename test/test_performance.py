import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from model.performance import PerformanceMetric
from repository.performance_repository import PerformanceRepository
from usecase.performance_usecase import PerformanceUseCase
from entity.task import TaskStatus


@pytest.fixture
def mock_performance_repository():
    """Create a mock performance repository for testing"""
    repo = AsyncMock(spec=PerformanceRepository)
    
    # Mock data for testing
    mock_metrics = [
        {
            "timestamp": datetime.now() - timedelta(hours=3),
            "active_agents": 5,
            "completed_tasks": 10,
            "speed": 1500.0,
            "agent_ids": ["agent1", "agent2", "agent3", "agent4", "agent5"]
        },
        {
            "timestamp": datetime.now() - timedelta(hours=2),
            "active_agents": 3,
            "completed_tasks": 12,
            "speed": 1200.0,
            "agent_ids": ["agent1", "agent3", "agent5"]
        },
        {
            "timestamp": datetime.now() - timedelta(hours=1),
            "active_agents": 4,
            "completed_tasks": 15,
            "speed": 1800.0,
            "agent_ids": ["agent1", "agent2", "agent3", "agent5"]
        }
    ]
    
    # Set up the mock methods
    repo.save_metric.return_value = "mock_metric_id"
    repo.get_hourly_metrics.return_value = mock_metrics
    repo.get_metrics_by_timerange.return_value = mock_metrics
    
    return repo


@pytest.fixture
def mock_agent_usecase():
    """Create a mock agent usecase for testing"""
    usecase = AsyncMock()
    
    # Mock data for testing
    mock_agents = [
        {"id": "agent1", "status": "online", "speed": 500.0},
        {"id": "agent2", "status": "online", "speed": 600.0},
        {"id": "agent3", "status": "online", "speed": 400.0},
        {"id": "agent4", "status": "offline", "speed": 0.0},
        {"id": "agent5", "status": "online", "speed": 300.0}
    ]
    
    usecase.get_all_agents.return_value = mock_agents
    
    return usecase


@pytest.fixture
def mock_task_usecase():
    """Create a mock task usecase for testing"""
    usecase = AsyncMock()
    
    # Mock data for testing
    mock_tasks = [
        {"id": "task1", "status": "COMPLETED"},
        {"id": "task2", "status": "COMPLETED"},
        {"id": "task3", "status": "RUNNING"},
        {"id": "task4", "status": "PENDING"},
        {"id": "task5", "status": "COMPLETED"}
    ]
    
    usecase.get_all_tasks.return_value = mock_tasks
    
    return usecase


@pytest.fixture
def performance_usecase(mock_performance_repository, mock_agent_usecase, mock_task_usecase):
    """Create a performance usecase with mock dependencies for testing"""
    return PerformanceUseCase(
        repository=mock_performance_repository,
        agent_usecase=mock_agent_usecase,
        task_usecase=mock_task_usecase
    )


class TestPerformanceUseCase:
    """Test cases for the PerformanceUseCase class"""
    
    async def test_record_current_metrics(self, performance_usecase, mock_performance_repository, mock_task_usecase):
        """Test recording current performance metrics"""
        # Modify mock_task_usecase to return tasks with completed status
        # TaskStatus.COMPLETED is 'completed' (lowercase) not 'COMPLETED'
        mock_tasks = [
            {"id": "task1", "status": TaskStatus.COMPLETED},
            {"id": "task2", "status": TaskStatus.COMPLETED},
            {"id": "task3", "status": TaskStatus.COMPLETED},
            {"id": "task4", "status": TaskStatus.PENDING},
            {"id": "task5", "status": TaskStatus.RUNNING}
        ]
        mock_task_usecase.get_all_tasks.return_value = mock_tasks
        
        # Call the method
        metric_id = await performance_usecase.record_current_metrics()
        
        # Verify the result
        assert metric_id == "mock_metric_id"
        
        # Verify the repository was called with the correct data
        mock_performance_repository.save_metric.assert_called_once()
        saved_metric = mock_performance_repository.save_metric.call_args[0][0]
        
        # Verify the metric data
        assert isinstance(saved_metric, PerformanceMetric)
        assert saved_metric.active_agents == 4  # 4 online agents
        assert saved_metric.completed_tasks == 3  # 3 completed tasks from our mock
        assert saved_metric.speed == 1800.0  # Sum of speeds of online agents
        assert len(saved_metric.agent_ids) == 4  # 4 online agent IDs
    
    async def test_get_hourly_performance_data(self, performance_usecase, mock_performance_repository):
        """Test getting hourly performance data in Chart.js format"""
        # Call the method
        chart_data = await performance_usecase.get_hourly_performance_data(hours=4)
        
        # Verify the repository was called
        mock_performance_repository.get_hourly_metrics.assert_called_once_with(4)
        
        # Verify the chart data structure
        assert "labels" in chart_data
        assert "datasets" in chart_data
        assert len(chart_data["datasets"]) == 3  # active_agents, completed_tasks, speed
        
        # Verify the data points - we expect 4 labels because we requested hours=4
        assert len(chart_data["labels"]) == 4  # 4 time labels for 4 hours
        assert len(chart_data["datasets"][0]["data"]) == 4  # 4 data points for active_agents
        assert len(chart_data["datasets"][1]["data"]) == 4  # 4 data points for completed_tasks
        assert len(chart_data["datasets"][2]["data"]) == 4  # 4 data points for speed
    
    async def test_mock_data_generation(self):
        """Test mock data generation when repository is None"""
        # Create a usecase with no repository (mock mode)
        usecase = PerformanceUseCase(
            repository=None,
            agent_usecase=AsyncMock(),
            task_usecase=AsyncMock()
        )
        
        # Call the method
        chart_data = await usecase.get_hourly_performance_data(hours=24)
        
        # Verify mock data was generated
        assert "labels" in chart_data
        assert "datasets" in chart_data
        assert len(chart_data["datasets"]) == 3
        
        # Verify the data points (should be 24 for hourly data)
        assert len(chart_data["labels"]) == 24
        assert len(chart_data["datasets"][0]["data"]) == 24
        assert len(chart_data["datasets"][1]["data"]) == 24
        assert len(chart_data["datasets"][2]["data"]) == 24
