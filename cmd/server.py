import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Header, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from typing import List, Optional, Dict, Any

from model.pagination import PaginationParams, PaginatedResponse
from config.auth import User, Token, get_current_active_user, admin_required, create_access_token, verify_password
from config.api_docs import API_DESCRIPTION, TAGS_METADATA
from model.examples import TASK_EXAMPLES, AGENT_EXAMPLES, TASK_STATUS_EXAMPLES, HEARTBEAT_EXAMPLES
from model.recovered_hash import RecoveredHashCreate

from config.logging_config import get_server_logger, log_with_context

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

# Get configured logger
logger = get_server_logger()

# Create FastAPI app
app = FastAPI(
    title="Distributed Hashcat Cracking System",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=TAGS_METADATA
)

# Add exception handler for better error logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with detailed logging"""
    error_id = f"{id(exc)}"
    error_msg = str(exc)
    error_type = type(exc).__name__
    
    # Log detailed error information
    log_with_context(
        logger, 
        logging.ERROR, 
        f"Unhandled exception: {error_type}: {error_msg}",
        error_id=error_id,
        error_type=error_type,
        path=request.url.path,
        method=request.method,
        client=request.client.host if request.client else "unknown",
        traceback=traceback.format_exc()
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
            "type": error_type
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication endpoints
@app.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and get JWT access token.
    
    - **username**: User's username
    - **password**: User's password
    - Returns an access token and token type for authentication
    
    Use this token in the Authorization header for subsequent requests.
    Format: 'Bearer {token}'
    """
    # In a real application, you would validate against database
    # For now, we'll use a hardcoded user for demonstration
    if form_data.username != "admin" or not verify_password(form_data.password, "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": form_data.username, "role": "admin"},
        expires_delta=access_token_expires
    )
    
    log_with_context(
        logger,
        logging.INFO,
        f"User {form_data.username} logged in",
        username=form_data.username
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User, tags=["Authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

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
                log_with_context(
                    logger, 
                    logging.INFO, 
                    f"Marked {offline_count} agents as offline",
                    offline_count=offline_count,
                    task="check_offline_agents"
                )
        except Exception as e:
            log_with_context(
                logger, 
                logging.ERROR, 
                f"Error checking offline agents: {str(e)}",
                error_type=type(e).__name__,
                task="check_offline_agents",
                traceback=traceback.format_exc()
            )
        
        # Sleep for 1 minute
        await asyncio.sleep(60)

async def auto_assign_tasks(task_usecase: TaskUseCase):
    """Auto-assign pending tasks to available agents periodically"""
    while True:
        try:
            assigned_count = await task_usecase.auto_assign_tasks()
            if assigned_count > 0:
                log_with_context(
                    logger, 
                    logging.INFO, 
                    f"Auto-assigned {assigned_count} tasks to agents",
                    assigned_count=assigned_count,
                    task="auto_assign_tasks"
                )
        except Exception as e:
            log_with_context(
                logger, 
                logging.ERROR, 
                f"Error auto-assigning tasks: {str(e)}",
                error_type=type(e).__name__,
                task="auto_assign_tasks",
                traceback=traceback.format_exc()
            )
        
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
    
    log_with_context(
        logger, 
        logging.INFO, 
        "Server started",
        version="1.0.0",
        host=SERVER_HOST,
        port=SERVER_PORT
    )

@app.on_event("shutdown")
async def shutdown_event():
    # Close database connection
    await Database.close()
    log_with_context(
        logger, 
        logging.INFO, 
        "Server shutdown",
        host=SERVER_HOST,
        port=SERVER_PORT
    )

# Task endpoints
@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(
    task_create: TaskCreate,
    task_usecase=Depends(get_task_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new password cracking task.
    
    - **task_create**: Task details including name, attack mode, hash type, etc.
    - Returns the created task with its assigned ID.
    
    Attack modes:
    - 0: Dictionary attack
    - 1: Combination attack
    - 3: Mask attack
    - 6: Hybrid dictionary + mask
    - 7: Hybrid mask + dictionary
    """
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

@app.get("/tasks", response_model=PaginatedResponse[TaskResponse], tags=["Tasks"])
async def get_tasks(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    task_usecase=Depends(get_task_usecase),
):
    """
    Get all tasks with optional filtering and pagination.
    
    - **pagination**: Skip and limit parameters for pagination
    - **status**: Optional filter by task status (PENDING, ASSIGNED, RUNNING, COMPLETED, FAILED, CANCELLED)
    - Returns a paginated list of tasks with total count and pagination metadata
    """
    try:
        # Get total count first
        if status:
            try:
                task_status = TaskStatus(status)
                total = await task_usecase.count_tasks_by_status(task_status)
                tasks = await task_usecase.get_tasks_by_status(task_status, pagination.skip, pagination.limit)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        else:
            total = await task_usecase.count_all_tasks()
            tasks = await task_usecase.get_all_tasks(pagination.skip, pagination.limit)
        
        # Convert tasks to response models
        task_responses = [TaskResponse(**task.to_dict()) for task in tasks]
        
        # Create paginated response
        return PaginatedResponse.create(
            items=task_responses,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error retrieving tasks: {str(e)}",
            error_type=type(e).__name__,
            traceback=traceback.format_exc()
        )
        raise

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
):
    """
    Get a specific task by ID.
    
    - **task_id**: The unique identifier of the task
    - Returns the task details including status, progress, and recovered hashes
    """
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

@app.delete("/tasks/{task_id}", response_model=bool, tags=["Tasks"])
async def delete_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
    current_user: User = Depends(admin_required),
):
    """
    Delete a task by ID.
    
    - **task_id**: The unique identifier of the task to delete
    - Returns true if the task was successfully deleted
    
    This endpoint is restricted to admin users only.
    Running tasks cannot be deleted - they must be cancelled first.
    """
    deleted = await task_usecase.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return deleted

@app.post("/tasks/{task_id}/cancel", response_model=TaskResponse, tags=["Tasks"])
async def cancel_task(
    task_id: str,
    task_usecase=Depends(get_task_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Cancel a running or assigned task.
    
    - **task_id**: The unique identifier of the task to cancel
    - Returns the updated task with CANCELLED status
    
    This will stop the task if it's running and free up the assigned agent.
    """
    task = await task_usecase.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())

@app.post("/tasks/{task_id}/recovered", response_model=TaskResponse, tags=["Tasks"])
async def add_recovered_hash(
    task_id: str,
    recovered_hash: RecoveredHashCreate,
    api_key: str = Header(...),
    task_usecase=Depends(get_task_usecase),
    agent_usecase=Depends(get_agent_usecase),
):
    """
    Add a recovered hash to a task (agent endpoint).
    
    - **task_id**: The unique identifier of the task
    - **recovered_hash**: Details of the recovered hash including hash value and plaintext
    - **api_key**: Agent API key for authentication
    - Returns the updated task with the new recovered hash added
    
    This endpoint is used by agent nodes to report successfully cracked passwords.
    """
    # Verify agent is assigned to this task
    if agent.current_task_id != task_id:
        raise HTTPException(status_code=403, detail="Agent not assigned to this task")
    
    # Add recovered hash
    task = await task_usecase.add_recovered_hash(task_id, recovered_hash.hash, recovered_hash.plaintext, agent.id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())

@app.post("/tasks/{task_id}/assign/{agent_id}", response_model=TaskResponse, tags=["Tasks"])
async def assign_task(
    task_id: str,
    agent_id: str,
    task_usecase=Depends(get_task_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Manually assign a task to a specific agent.
    
    - **task_id**: The unique identifier of the task to assign
    - **agent_id**: The unique identifier of the agent to assign the task to
    - Returns the updated task with assignment details
    
    The task must be in PENDING status and the agent must be available.
    """
    task = await task_usecase.assign_task(task_id, agent_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())

@app.post("/tasks/{task_id}/status", response_model=TaskResponse, tags=["Tasks"])
async def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate,
    api_key: str = Header(...),
    task_usecase=Depends(get_task_usecase),
    agent_usecase=Depends(get_agent_usecase),
):
    """
    Update task status (agent endpoint).
    
    - **task_id**: The unique identifier of the task to update
    - **status_update**: New status details including status, progress, speed, and error message
    - **api_key**: Agent API key for authentication
    - Returns the updated task with new status information
    
    This endpoint is primarily used by agent nodes to report task progress and status changes.
    """
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
    
    return TaskResponse(**task.to_dict())

# Agent endpoints
@app.post("/agents", response_model=AgentResponse, tags=["Agents"])
async def register_agent(
    agent_create: AgentCreate,
    agent_usecase=Depends(get_agent_usecase),
    current_user: User = Depends(admin_required),
):
    """
    Register a new agent node.
    
    - **agent_create**: Agent details including name, hostname, API key, and device information
    - Returns the registered agent with its assigned ID
    
    This endpoint is restricted to admin users only.
    """
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

@app.get("/agents", response_model=PaginatedResponse[AgentResponse], tags=["Agents"])
async def get_agents(
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    agent_usecase=Depends(get_agent_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all agents with optional filtering and pagination.
    
    - **pagination**: Skip and limit parameters for pagination
    - **status**: Optional filter by agent status (ONLINE, OFFLINE, BUSY)
    - Returns a paginated list of agents with total count and pagination metadata
    """
    try:
        # Get total count first
        if status:
            try:
                agent_status = AgentStatus(status)
                total = await agent_usecase.count_agents_by_status(agent_status)
                agents = await agent_usecase.get_agents_by_status(agent_status, pagination.skip, pagination.limit)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        else:
            total = await agent_usecase.count_all_agents()
            agents = await agent_usecase.get_all_agents(pagination.skip, pagination.limit)
        
        # Convert agents to response models
        agent_responses = [AgentResponse(**agent.to_dict()) for agent in agents]
        
        # Create paginated response
        return PaginatedResponse.create(
            items=agent_responses,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error retrieving agents: {str(e)}",
            error_type=type(e).__name__,
            traceback=traceback.format_exc()
        )
        raise

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
    """
    Update agent heartbeat status.
    
    - **heartbeat**: Heartbeat information including status, CPU/GPU usage, and memory usage
    - Returns the updated agent information
    
    This endpoint is used by agent nodes to periodically report their status and resource usage.
    """
    updated_agent = await agent_usecase.update_heartbeat(
        agent.id,
        heartbeat.status,
        heartbeat.cpu_usage,
        heartbeat.gpu_usage,
        heartbeat.memory_usage
    )
    
    return AgentResponse(**updated_agent.to_dict())

# Agent API endpoints (for agent-server communication)
@app.get("/agent/task", tags=["Agent API"])
async def get_agent_task(
    agent=Depends(verify_agent_api_key),
    task_usecase=Depends(get_task_usecase),
):
    """
    Get the current task assigned to an agent.
    
    - Returns the task details if a task is assigned, or null if no task is assigned
    
    This endpoint is used by agent nodes to check for assigned tasks.
    """
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
@app.get("/results", response_model=PaginatedResponse[ResultResponse], tags=["Results"])
async def get_results(
    pagination: PaginationParams = Depends(),
    task_id: Optional[str] = None,
    result_usecase=Depends(get_result_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all cracking results with optional filtering and pagination.
    
    - **pagination**: Skip and limit parameters for pagination
    - **task_id**: Optional filter to get results for a specific task only
    - Returns a paginated list of results with total count and pagination metadata
    
    Each result represents a successfully cracked password, including the hash value,
    plaintext password, and which agent cracked it.
    """
    try:
        # Get total count first
        if task_id:
            total = await result_usecase.count_results_by_task(task_id)
            results = await result_usecase.get_results_by_task(task_id, pagination.skip, pagination.limit)
        else:
            total = await result_usecase.count_all_results()
            results = await result_usecase.get_all_results(pagination.skip, pagination.limit)
        
        # Convert results to response models
        result_responses = [ResultResponse(**result.to_dict()) for result in results]
        
        # Create paginated response
        return PaginatedResponse.create(
            items=result_responses,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit
        )
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error retrieving results: {str(e)}",
            error_type=type(e).__name__,
            traceback=traceback.format_exc()
        )
        raise

@app.get("/results/{result_id}", response_model=ResultResponse, tags=["Results"])
async def get_result(
    result_id: str,
    result_usecase=Depends(get_result_usecase),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific cracking result by ID.
    
    - **result_id**: The unique identifier of the result
    - Returns the result details including the hash value, plaintext, and which agent cracked it
    """
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
