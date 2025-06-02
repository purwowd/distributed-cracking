from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from entity.agent import Agent, AgentStatus


class AgentRepository:
    """Repository for agent data access"""
    
    def __init__(self, database):
        self.db = database
        self.collection = database.agents
    
    async def create(self, agent: Agent) -> Agent:
        """Create a new agent"""
        agent_dict = agent.to_dict()
        # Remove id if None
        if agent_dict["id"] is None:
            del agent_dict["id"]
        
        result = await self.collection.insert_one(agent_dict)
        agent.id = str(result.inserted_id)
        return agent
    
    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """Find agent by ID"""
        agent_dict = await self.collection.find_one({"_id": ObjectId(agent_id)})
        if agent_dict:
            agent_dict["id"] = str(agent_dict.pop("_id"))
            return Agent.from_dict(agent_dict)
        return None
    
    async def find_by_api_key(self, api_key: str) -> Optional[Agent]:
        """Find agent by API key"""
        agent_dict = await self.collection.find_one({"api_key": api_key})
        if agent_dict:
            agent_dict["id"] = str(agent_dict.pop("_id"))
            return Agent.from_dict(agent_dict)
        return None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Find all agents with pagination"""
        cursor = self.collection.find().skip(skip).limit(limit)
        agents = []
        async for agent_dict in cursor:
            agent_dict["id"] = str(agent_dict.pop("_id"))
            agents.append(Agent.from_dict(agent_dict))
        return agents
    
    async def find_by_status(self, status: AgentStatus, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Find agents by status"""
        cursor = self.collection.find({"status": status.value}).skip(skip).limit(limit)
        agents = []
        async for agent_dict in cursor:
            agent_dict["id"] = str(agent_dict.pop("_id"))
            agents.append(Agent.from_dict(agent_dict))
        return agents
    
    async def find_available_agents(self) -> List[Agent]:
        """Find available agents for task assignment"""
        cursor = self.collection.find({
            "status": AgentStatus.ONLINE.value,
            "current_task_id": None
        })
        agents = []
        async for agent_dict in cursor:
            agent_dict["id"] = str(agent_dict.pop("_id"))
            agents.append(Agent.from_dict(agent_dict))
        return agents
    
    async def update(self, agent: Agent) -> Optional[Agent]:
        """Update an existing agent"""
        agent_dict = agent.to_dict()
        agent_id = agent_dict.pop("id")
        
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": agent_dict}
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(agent_id)
        return None
    
    async def update_status(self, agent_id: str, status: AgentStatus) -> Optional[Agent]:
        """Update agent status"""
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "status": status.value,
                    "last_seen": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(agent_id)
        return None
    
    async def update_heartbeat(self, agent_id: str) -> Optional[Agent]:
        """Update agent heartbeat"""
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {"$set": {"last_seen": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(agent_id)
        return None
    
    async def assign_task(self, agent_id: str, task_id: str) -> Optional[Agent]:
        """Assign task to agent"""
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "current_task_id": task_id,
                    "status": AgentStatus.BUSY.value,
                    "last_seen": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(agent_id)
        return None
    
    async def clear_task(self, agent_id: str) -> Optional[Agent]:
        """Clear current task from agent"""
        result = await self.collection.update_one(
            {"_id": ObjectId(agent_id)},
            {
                "$set": {
                    "current_task_id": None,
                    "status": AgentStatus.ONLINE.value,
                    "last_seen": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(agent_id)
        return None
    
    async def delete(self, agent_id: str) -> bool:
        """Delete an agent"""
        result = await self.collection.delete_one({"_id": ObjectId(agent_id)})
        return result.deleted_count > 0
