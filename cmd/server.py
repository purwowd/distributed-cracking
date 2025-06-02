import asyncio
import logging
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from config.database import Database
from config.settings import SERVER_HOST, SERVER_PORT

from entity.task import Task, TaskStatus
from entity.agent import Agent, AgentStatus
from entity.result import Result

from repository.task_repository import TaskRepository
from repository.agent_repository import AgentRepository
from repository.result_repository import ResultRepository

from usecase.task_usecase import TaskUseCase
from usecase.agent_usecase import AgentUseCase
from usecase.result_usecase import ResultUseCase

from model.task import TaskCreate, TaskResponse, TaskUpdate, TaskStatusUpdate
from model.agent import AgentCreate, AgentResponse, AgentUpdate, AgentHeartbeat
from model.result import ResultCreate, ResultResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Distributed Hashcat Cracking System",
    description="API for distributed password cracking using Hashcat",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database connection
async def get_db():
    db = Database.get_database()
    return db

# Dependency to get repositories
async def get_task_repo(db=Depends(get_db)):
    return TaskRepository(db)

async def get_agent_repo(db=Depends(get_db)):
    return AgentRepository(db)

async def get_result_repo(db=Depends(get_db)):
    return ResultRepository(db)

# Dependency to get use cases
async def get_task_usecase(
    task_repo=Depends(get_task_repo),
    agent_repo=Depends(get_agent_repo),
    result_repo=Depends(get_result_repo),
):
    return TaskUseCase(task_repo, agent_repo, result_repo)

async def get_agent_usecase(
    agent_repo=Depends(get_agent_repo),
    task_repo=Depends(get_task_repo),
):
    return AgentUseCase(agent_repo, task_repo)

async def get_result_usecase(result_repo=Depends(get_result_repo)):
    return ResultUseCase(result_repo)

# Dependency to verify agent API key
async def verify_agent_api_key(
    api_key: str = Header(..., description="Agent API key"),
    agent_usecase=Depends(get_agent_usecase),
):
    agent = await agent_usecase.get_agent_by_api_key(api_key)
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return agent


# Background tasks
async def check_offline_agents(agent_usecase: AgentUseCase):
    """Check for offline agents periodically"""
    while True:
        try:
            offline_count = await agent_usecase.check_offline_agents()
            if offline_count > 0:
                logger.info(f"Marked {offline_count} agents as offline")
        except Exception as e:
            logger.error(f"Error checking offline agents: {e}")
        
        # Sleep for 1 minute
        await asyncio.sleep(60)

async def auto_assign_tasks(task_usecase: TaskUseCase):
    """Auto-assign pending tasks to available agents periodically"""
    while True:
        try:
            assigned_count = await task_usecase.auto_assign_tasks()
            if assigned_count > 0:
                logger.info(f"Auto-assigned {assigned_count} tasks to agents")
        except Exception as e:
            logger.error(f"Error auto-assigning tasks: {e}")
        
        # Sleep for 10 seconds
        await asyncio.sleep(10)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Connect to database
    await Database.connect()
    
    # Start background tasks
    agent_usecase = AgentUseCase(
        AgentRepository(Database.get_database()),
        TaskRepository(Database.get_database())
    )
    task_usecase = TaskUseCase(
        TaskRepository(Database.get_database()),
        AgentRepository(Database.get_database()),
        ResultRepository(Database.get_database())
    )
    
    asyncio.create_task(check_offline_agents(agent_usecase))
    asyncio.create_task(auto_assign_tasks(task_usecase))
    
    logger.info("Server started")

@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    await Database.close()
    logger.info("Server shutdown")


# Task endpoints
@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    task_create: TaskCreate,
    task_usecase=Depends(get_task_usecase),
):
    """Create a new task"""
    task = Task(
        name=task_create.name,
        description=task_create.description,
        hash_type=task_create.hash_type,
        hash_type_id=task_create.hash_type_id,
        hashes=task_create.hashes,
        wordlist_path=task_create.wordlist_path,
        rule_path=task_create.rule_path,
        mask=task_create.mask,
        attack_mode=task_create.attack_mode,
        additional_args=task_create.additional_args,
        priority=task_create.priority,
        metadata=task_create.metadata,
    )
    
    created_task = await task_usecase.create_task(task)
    return TaskResponse(**created_task.to_dict())

@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    task_usecase=Depends(get_task_usecase),
):
    """Get all tasks with optional filtering"""
    if status:
        try:
            task_status = TaskStatus(status)
            tasks = await task_usecase.get_tasks_by_status(task_status, skip, limit)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        tasks = await task_usecase.get_all_tasks(skip, limit)
    
    return [TaskResponse(**task.to_dict()) for task in tasks]

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
):
    """Get a task by ID"""
    task = await task_usecase.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())

@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    task_usecase=Depends(get_task_usecase),
):
    """Update a task"""
    # Get existing task
    task = await task_usecase.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    if task_update.name is not None:
        task.name = task_update.name
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.additional_args is not None:
        task.additional_args = task_update.additional_args
    if task_update.metadata is not None:
        task.metadata = task_update.metadata
    
    # Save changes
    updated_task = await task_usecase.update_task(task)
    return TaskResponse(**updated_task.to_dict())

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
):
    """Delete a task"""
    deleted = await task_usecase.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted"}

@app.post("/tasks/{task_id}/cancel", response_model=TaskResponse, tags=["Tasks"])
async def cancel_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
):
    """Cancel a task"""
    task = await task_usecase.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())


# Agent endpoints
@app.post("/agents", response_model=AgentResponse, tags=["Agents"])
async def register_agent(
    agent_create: AgentCreate,
    agent_usecase=Depends(get_agent_usecase),
):
    """Register a new agent"""
    agent = Agent(
        name=agent_create.name,
        hostname=agent_create.hostname,
        ip_address=agent_create.ip_address,
        api_key=agent_create.api_key,
        capabilities=agent_create.capabilities,
        gpu_info=agent_create.gpu_info,
        cpu_info=agent_create.cpu_info,
        hashcat_version=agent_create.hashcat_version,
        metadata=agent_create.metadata,
    )
    
    registered_agent = await agent_usecase.register_agent(agent)
    return AgentResponse(**registered_agent.to_dict())

@app.get("/agents", response_model=List[AgentResponse], tags=["Agents"])
async def get_agents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    agent_usecase=Depends(get_agent_usecase),
):
    """Get all agents with optional filtering"""
    if status:
        try:
            agent_status = AgentStatus(status)
            agents = await agent_usecase.get_agents_by_status(agent_status, skip, limit)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        agents = await agent_usecase.get_all_agents(skip, limit)
    
    return [AgentResponse(**agent.to_dict()) for agent in agents]

@app.get("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def get_agent(
    agent_id: str,
    agent_usecase=Depends(get_agent_usecase),
):
    """Get an agent by ID"""
    agent = await agent_usecase.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AgentResponse(**agent.to_dict())

@app.put("/agents/{agent_id}", response_model=AgentResponse, tags=["Agents"])
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    agent_usecase=Depends(get_agent_usecase),
):
    """Update an agent"""
    # Get existing agent
    agent = await agent_usecase.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields
    if agent_update.name is not None:
        agent.name = agent_update.name
    if agent_update.hostname is not None:
        agent.hostname = agent_update.hostname
    if agent_update.ip_address is not None:
        agent.ip_address = agent_update.ip_address
    if agent_update.status is not None:
        agent.status = agent_update.status
    if agent_update.capabilities is not None:
        agent.capabilities = agent_update.capabilities
    if agent_update.current_task_id is not None:
        agent.current_task_id = agent_update.current_task_id
    if agent_update.gpu_info is not None:
        agent.gpu_info = agent_update.gpu_info
    if agent_update.cpu_info is not None:
        agent.cpu_info = agent_update.cpu_info
    if agent_update.hashcat_version is not None:
        agent.hashcat_version = agent_update.hashcat_version
    if agent_update.metadata is not None:
        agent.metadata = agent_update.metadata
    
    # Save changes
    updated_agent = await agent_usecase.update_agent(agent)
    return AgentResponse(**updated_agent.to_dict())

@app.delete("/agents/{agent_id}", tags=["Agents"])
async def delete_agent(
    agent_id: str,
    agent_usecase=Depends(get_agent_usecase),
):
    """Delete an agent"""
    deleted = await agent_usecase.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent deleted"}

@app.post("/agents/heartbeat", response_model=AgentResponse, tags=["Agents"])
async def agent_heartbeat(
    heartbeat: AgentHeartbeat,
    agent=Depends(verify_agent_api_key),
    agent_usecase=Depends(get_agent_usecase),
):
    """Send agent heartbeat"""
    updated_agent = await agent_usecase.process_heartbeat(
        agent.id,
        heartbeat.status,
        heartbeat.current_task_id,
        heartbeat.task_progress,
        heartbeat.task_speed,
    )
    
    return AgentResponse(**updated_agent.to_dict())


# Agent API endpoints (for agent-server communication)
@app.get("/agent/task", tags=["Agent API"])
async def get_agent_task(
    agent=Depends(verify_agent_api_key),
    task_usecase=Depends(get_task_usecase),
):
    """Get current task for agent"""
    if not agent.current_task_id:
        return {"status": "no_task"}
    
    task = await task_usecase.get_task(agent.current_task_id)
    if not task:
        return {"status": "no_task"}
    
    return {"status": "ok", "task": task.to_dict()}

@app.post("/agent/task/{task_id}/status", tags=["Agent API"])
async def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate,
    agent=Depends(verify_agent_api_key),
    task_usecase=Depends(get_task_usecase),
):
    """Update task status from agent"""
    # Verify agent is assigned to this task
    if agent.current_task_id != task_id:
        raise HTTPException(status_code=403, detail="Agent not assigned to this task")
    
    # Update task status
    task = await task_usecase.update_task_status(
        task_id,
        status_update.status,
        status_update.progress,
        status_update.speed,
        status_update.error,
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Add recovered hashes
    for hash_result in status_update.recovered_hashes:
        await task_usecase.add_recovered_hash(
            task_id,
            hash_result["hash"],
            hash_result["plaintext"],
            agent.id,
        )
    
    return {"status": "ok"}


# Result endpoints
@app.get("/results", response_model=List[ResultResponse], tags=["Results"])
async def get_results(
    skip: int = 0,
    limit: int = 100,
    task_id: Optional[str] = None,
    result_usecase=Depends(get_result_usecase),
):
    """Get all results with optional filtering"""
    if task_id:
        results = await result_usecase.get_results_by_task_id(task_id)
    else:
        results = await result_usecase.get_all_results(skip, limit)
    
    return [ResultResponse(**result.to_dict()) for result in results]

@app.get("/results/{result_id}", response_model=ResultResponse, tags=["Results"])
async def get_result(
    result_id: str,
    result_usecase=Depends(get_result_usecase),
):
    """Get a result by ID"""
    result = await result_usecase.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return ResultResponse(**result.to_dict())

@app.get("/results/hash/{hash_value}", response_model=ResultResponse, tags=["Results"])
async def get_result_by_hash(
    hash_value: str,
    result_usecase=Depends(get_result_usecase),
):
    """Get a result by hash value"""
    result = await result_usecase.get_result_by_hash(hash_value)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return ResultResponse(**result.to_dict())


# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cmd.server:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
