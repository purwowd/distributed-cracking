from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from model.performance import PerformanceMetric

class PerformanceRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def save_metric(self, metric: PerformanceMetric) -> str:
        """Save a performance metric to the database"""
        result = await self.collection.insert_one(metric.dict())
        return str(result.inserted_id)
    
    async def get_metrics_by_timerange(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get metrics within a specific time range"""
        cursor = self.collection.find({
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).sort("timestamp", 1)
        return await cursor.to_list(length=None)
    
    async def get_hourly_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics for the last N hours"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        return await self.get_metrics_by_timerange(start_time, end_time)
