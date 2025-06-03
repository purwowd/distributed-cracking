from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from repository.performance_repository import PerformanceRepository
from model.performance import PerformanceMetric
from usecase.agent_usecase import AgentUseCase
from usecase.task_usecase import TaskUseCase
from entity.task import TaskStatus
import logging

logger = logging.getLogger(__name__)

class PerformanceUseCase:
    def __init__(self, repository: PerformanceRepository, 
                 agent_usecase: AgentUseCase,
                 task_usecase: TaskUseCase):
        self.repository = repository
        self.agent_usecase = agent_usecase
        self.task_usecase = task_usecase
    
    async def record_current_metrics(self) -> str:
        """Record current system performance metrics"""
        logger.info("Recording current performance metrics")
        
        try:
            agents = await self.agent_usecase.get_all_agents()
            tasks = await self.task_usecase.get_all_tasks()
            
            active_agents = [a for a in agents if getattr(a, 'status', a.get('status', None)) == 'online']
            active_agent_ids = [getattr(a, 'id', a.get('id', None)) for a in active_agents]
            
            completed_tasks_count = sum(1 for t in tasks 
                                      if getattr(t, 'status', t.get('status', None)) == TaskStatus.COMPLETED)
            
            # In a real system, you would get the actual speed from agents
            # This is a placeholder
            total_speed = sum(getattr(a, 'speed', a.get('speed', 0)) for a in active_agents)
            
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                active_agents=len(active_agents),
                completed_tasks=completed_tasks_count,
                speed=total_speed,
                agent_ids=active_agent_ids
            )
            
            metric_id = await self.repository.save_metric(metric)
            logger.info(f"Recorded performance metric with ID: {metric_id}")
            return metric_id
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {str(e)}")
            logger.exception("Exception details:")
            raise
    
    async def get_hourly_performance_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance data for the last N hours in Chart.js format"""
        logger.info(f"Getting performance data for the last {hours} hours")
        
        try:
            # Check if we're using mock database (repository is None)
            if self.repository is None:
                logger.info("Using mock data for performance metrics")
                # Generate mock data
                now = datetime.now()
                time_labels = [(now - timedelta(hours=i)).strftime('%H:00') for i in range(hours, 0, -1)]
                
                # Get all tasks and agents
                tasks = await self.task_usecase.get_all_tasks()
                agents = await self.agent_usecase.get_all_agents()
                
                # Calculate active agents over time (simulated data)
                active_agents = [min(len(agents), random.randint(0, len(agents))) for _ in range(hours)]
                
                # Calculate completed tasks over time (simulated data)
                completed_tasks_count = sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.COMPLETED)
                completed_tasks = [random.randint(0, completed_tasks_count) for _ in range(hours)]
                
                # Calculate average speed in hashes/second (simulated data)
                speed_data = [random.randint(100000, 10000000) for _ in range(hours)]
                
                logger.info("Generated mock performance data successfully")
                
                return {
                    "labels": time_labels,
                    "datasets": [
                        {
                            "label": "Active Agents",
                            "data": active_agents,
                            "borderColor": "rgba(54, 162, 235, 1)",
                            "backgroundColor": "rgba(54, 162, 235, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.4,
                            "yAxisID": "y"
                        },
                        {
                            "label": "Completed Tasks",
                            "data": completed_tasks,
                            "borderColor": "rgba(75, 192, 192, 1)",
                            "backgroundColor": "rgba(75, 192, 192, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.4,
                            "yAxisID": "y"
                        },
                        {
                            "label": "Speed (MH/s)",
                            "data": [speed / 1000000 for speed in speed_data],  # Convert to MH/s
                            "borderColor": "rgba(255, 99, 132, 1)",
                            "backgroundColor": "rgba(255, 99, 132, 0.2)",
                            "borderWidth": 2,
                            "tension": 0.4,
                            "yAxisID": "y1"
                        }
                    ]
                }
            
            # If using real database, get metrics from repository
            metrics = await self.repository.get_hourly_metrics(hours)
            logger.info(f"Retrieved {len(metrics)} performance metrics from database")
            
            # If no metrics are available, return empty data
            if not metrics:
                logger.warning("No performance metrics found in database")
                now = datetime.now()
                time_labels = [(now - timedelta(hours=i)).strftime('%H:00') for i in range(hours, 0, -1)]
                return {
                    "labels": time_labels,
                    "datasets": [
                        {"label": "Active Agents", "data": [0] * hours, "borderColor": "rgba(54, 162, 235, 1)", 
                         "backgroundColor": "rgba(54, 162, 235, 0.2)", "borderWidth": 2, "tension": 0.4, "yAxisID": "y"},
                        {"label": "Completed Tasks", "data": [0] * hours, "borderColor": "rgba(75, 192, 192, 1)", 
                         "backgroundColor": "rgba(75, 192, 192, 0.2)", "borderWidth": 2, "tension": 0.4, "yAxisID": "y"},
                        {"label": "Speed (MH/s)", "data": [0] * hours, "borderColor": "rgba(255, 99, 132, 1)", 
                         "backgroundColor": "rgba(255, 99, 132, 0.2)", "borderWidth": 2, "tension": 0.4, "yAxisID": "y1"}
                    ]
                }
            
            # Process metrics into hourly buckets
            now = datetime.now()
            time_buckets = {}
            
            for i in range(hours):
                bucket_time = now - timedelta(hours=i)
                bucket_key = bucket_time.strftime('%Y-%m-%d %H:00')
                time_buckets[bucket_key] = {"active_agents": 0, "completed_tasks": 0, "speed": 0, "count": 0}
            
            for metric in metrics:
                bucket_key = metric["timestamp"].strftime('%Y-%m-%d %H:00')
                if bucket_key in time_buckets:
                    time_buckets[bucket_key]["active_agents"] += metric["active_agents"]
                    time_buckets[bucket_key]["completed_tasks"] += metric["completed_tasks"]
                    time_buckets[bucket_key]["speed"] += metric["speed"]
                    time_buckets[bucket_key]["count"] += 1
            
            # Average the values in each bucket
            for bucket in time_buckets.values():
                if bucket["count"] > 0:
                    bucket["active_agents"] /= bucket["count"]
                    bucket["completed_tasks"] /= bucket["count"]
                    bucket["speed"] /= bucket["count"]
            
            # Format data for Chart.js
            time_labels = [(now - timedelta(hours=i)).strftime('%H:00') for i in range(hours, 0, -1)]
            active_agents = []
            completed_tasks = []
            speed_data = []
            
            for i in range(hours):
                bucket_time = now - timedelta(hours=i)
                bucket_key = bucket_time.strftime('%Y-%m-%d %H:00')
                bucket = time_buckets.get(bucket_key, {"active_agents": 0, "completed_tasks": 0, "speed": 0})
                
                active_agents.append(bucket["active_agents"])
                completed_tasks.append(bucket["completed_tasks"])
                speed_data.append(bucket["speed"])
            
            logger.info("Successfully processed performance data for Chart.js")
            
            return {
                "labels": time_labels,
                "datasets": [
                    {
                        "label": "Active Agents",
                        "data": active_agents,
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderWidth": 2,
                        "tension": 0.4,
                        "yAxisID": "y"
                    },
                    {
                        "label": "Completed Tasks",
                        "data": completed_tasks,
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "borderWidth": 2,
                        "tension": 0.4,
                        "yAxisID": "y"
                    },
                    {
                        "label": "Speed (MH/s)",
                        "data": [speed / 1000000 for speed in speed_data],  # Convert to MH/s
                        "borderColor": "rgba(255, 99, 132, 1)",
                        "backgroundColor": "rgba(255, 99, 132, 0.2)",
                        "borderWidth": 2,
                        "tension": 0.4,
                        "yAxisID": "y1"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Error getting performance data: {str(e)}")
            logger.exception("Exception details:")
            raise
