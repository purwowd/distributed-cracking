#!/usr/bin/env python
import os
import uvicorn
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import random
import logging
from fastapi_utils.tasks import repeat_every

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the new dependencies module
from config.dependencies import get_task_usecase, get_agent_usecase, get_result_usecase, get_performance_usecase, get_user_usecase
from entity.user import User, UserRole
from usecase.user_usecase import UserUseCase
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add the project root to the Python path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import the real database connection, fall back to mock if not available
try:
    from config.database import connect_to_db, close_db_connection
    print("Using real MongoDB connection")
except ImportError:
    print("MongoDB connection not available, using mock database")
    from config.mock_database import connect_to_db, close_db_connection

# Import base usecase classes for type hints
from usecase.task_usecase import TaskUseCase
from usecase.agent_usecase import AgentUseCase
from usecase.result_usecase import ResultUseCase
from entity.task import TaskStatus, HashType
from model.task import TaskCreate, TaskUpdate
from model.agent import AgentCreate

# Create FastAPI app
app = FastAPI(title="Distributed Hashcat Cracking - Web Dashboard")

# Add middleware to handle authentication redirects
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        # Check if response status code is 401 Unauthorized
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        return response
    except Exception as exc:
        # For any other exceptions, just raise them
        raise

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="cmd/web/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="cmd/web/templates")

# Initialize database connection
@app.on_event("startup")
async def startup_db_client():
    await connect_to_db()
    
    # Initialize user repository and create admin user if needed
    try:
        user_usecase = await get_user_usecase()
        await user_usecase.initialize_admin_user()
    except Exception as e:
        logging.error(f"Error initializing user system: {str(e)}")


# Close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db_connection()


# Authentication dependency
async def get_current_user(session_token: str = Cookie(None), user_usecase: UserUseCase = Depends(get_user_usecase)):
    if not session_token:
        return None
    
    try:
        payload = user_usecase.verify_token(session_token)
        username = payload.get("sub")
        if not username:
            return None
        
        user = await user_usecase.get_user_by_username(username)
        return user
    except Exception:
        return None


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


# Login routes

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, current_user: User = Depends(get_current_user)):
    # If user is already logged in, redirect to dashboard
    if current_user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), user_usecase: UserUseCase = Depends(get_user_usecase)):
    user = await user_usecase.authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    # Create access token
    access_token = user_usecase.create_access_token(
        data={"sub": user.username, "role": user.role.value if isinstance(user.role, UserRole) else user.role}
    )
    
    # Create response with cookie
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_token", value=access_token, httponly=True)
    
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_token")
    return response


# Dashboard routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, 
                   current_user: User = Depends(get_current_active_user),
                   task_usecase: TaskUseCase = Depends(get_task_usecase),
                   agent_usecase: AgentUseCase = Depends(get_agent_usecase),
                   result_usecase: ResultUseCase = Depends(get_result_usecase)):
    """Main dashboard page"""
    tasks = await task_usecase.get_all_tasks()
    agents = await agent_usecase.get_all_agents()
    results = await result_usecase.get_all_results(limit=10)
    
    # Count tasks by status
    task_stats = {
        "total": len(tasks),
        "pending": sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.PENDING),
        "running": sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.RUNNING),
        "completed": sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.COMPLETED),
        "failed": sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.FAILED),
        "cancelled": sum(1 for t in tasks if getattr(t, 'status', t.get('status', None)) == TaskStatus.CANCELLED)
    }
    
    # Count agents by status
    agent_stats = {
        "total": len(agents),
        "online": sum(1 for a in agents if isinstance(a, dict) and a.get('status') == 'online' or hasattr(a, 'is_available') and a.is_available()),
        "busy": sum(1 for a in agents if isinstance(a, dict) and a.get('current_task_id') is not None or hasattr(a, 'current_task_id') and a.current_task_id is not None),
        "offline": sum(1 for a in agents if isinstance(a, dict) and a.get('status') == 'offline' or hasattr(a, 'is_available') and not a.is_available() and getattr(a, 'current_task_id', None) is None)
    }
    
    # Get recent tasks
    recent_tasks = sorted(tasks, key=lambda t: getattr(t, 'created_at', t.get('created_at', datetime.now())), reverse=True)[:5]
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "task_stats": task_stats,
            "agent_stats": agent_stats,
            "recent_tasks": recent_tasks,
            "recent_results": results,
            "active_page": "dashboard",
            "user": current_user
        }
    )


# Task routes
@app.get("/tasks", response_class=HTMLResponse)
async def list_tasks(
    request: Request, 
    status: Optional[str] = None,
    hash_type: Optional[str] = None,
    sort: str = "created_at",
    task_usecase: TaskUseCase = Depends(get_task_usecase),
    current_user: User = Depends(get_current_active_user)
):
    """List all tasks with optional filtering"""
    # Get tasks with status filter if provided
    tasks = await task_usecase.get_tasks(status=status)
    
    # Filter by hash_type if provided
    if hash_type and tasks:
        tasks = [t for t in tasks if (isinstance(t, dict) and t.get("hash_type") == hash_type) or 
                 (not isinstance(t, dict) and getattr(t, "hash_type", "") == hash_type)]
    
    # Sort tasks based on the sort parameter
    if sort == "name":
        tasks = sorted(tasks, key=lambda t: t.get("name") if isinstance(t, dict) else getattr(t, "name", ""))
    elif sort == "priority":
        tasks = sorted(tasks, key=lambda t: t.get("priority") if isinstance(t, dict) else getattr(t, "priority", 0), reverse=True)
    else:  # default to created_at
        tasks = sorted(tasks, key=lambda t: t.get("created_at") if isinstance(t, dict) else getattr(t, "created_at", datetime.datetime.min), reverse=True)
    
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "tasks": tasks, "active_page": "tasks", 
         "current_status": status, "current_hash_type": hash_type, "current_sort": sort,
         "user": current_user}
    )


@app.get("/tasks/new", response_class=HTMLResponse)
async def new_task_form(request: Request, current_user: User = Depends(get_current_active_user)):
    """Form to create a new task"""
    
    hash_types = ["md5", "sha1", "sha256", "ntlm", "wpa"]
    return templates.TemplateResponse(
        "task_new.html",
        {"request": request, "hash_types": hash_types, "active_page": "tasks", "user": current_user}
    )


@app.get("/tasks/new-wpa", response_class=HTMLResponse)
async def new_wpa_task_form(request: Request, current_user: User = Depends(get_current_active_user)):
    """Form to create a new WPA cracking task"""
    
    # Get list of capture files in the captures directory
    captures_dir = Path("data/captures")
    capture_files = [f.name for f in captures_dir.glob("*.cap") if f.is_file()]
    capture_files += [f.name for f in captures_dir.glob("*.hccapx") if f.is_file()]
    
    # Get list of wordlist files
    wordlists_dir = Path("data/wordlists")
    wordlist_files = [f.name for f in wordlists_dir.glob("*.txt") if f.is_file()]
    
    return templates.TemplateResponse(
        "task_new_wpa.html",
        {"request": request, "capture_files": capture_files, "wordlist_files": wordlist_files, "active_page": "tasks", "user": current_user}
    )


@app.get("/files/upload", response_class=HTMLResponse)
async def upload_files_form(request: Request, current_user: User = Depends(get_current_active_user)):
    """Form to upload handshake and wordlist files"""
    # Get list of uploaded handshake files
    handshake_path = Path("uploads/handshakes")
    handshake_files = []
    if handshake_path.exists():
        for file in handshake_path.glob("*"):
            if file.is_file():
                stats = file.stat()
                handshake_files.append({
                    "name": file.name,
                    "path": str(file),
                    "size": f"{stats.st_size / 1024:.1f} KB",
                    "uploaded_at": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                })
    
    # Get list of uploaded wordlist files
    wordlist_path = Path("uploads/wordlists")
    wordlist_files = []
    if wordlist_path.exists():
        for file in wordlist_path.glob("*"):
            if file.is_file():
                stats = file.stat()
                wordlist_files.append({
                    "name": file.name,
                    "path": str(file),
                    "size": f"{stats.st_size / 1024:.1f} KB",
                    "uploaded_at": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                })
    
    return templates.TemplateResponse(
        "file_upload.html",
        {
            "request": request, 
            "active_page": "tasks",
            "handshake_files": handshake_files,
            "wordlist_files": wordlist_files,
            "user": current_user
        }
    )


@app.post("/tasks/new")
async def create_task(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    hash_type: str = Form(...),
    hash_type_id: Optional[int] = Form(None),
    hashes: str = Form(...),
    wordlist_path: Optional[str] = Form(None),
    rule_path: Optional[str] = Form(None),
    mask: Optional[str] = Form(None),
    attack_mode: int = Form(0),
    priority: int = Form(1),
    task_usecase: TaskUseCase = Depends(get_task_usecase)
):
    """Create a new task"""
    # Process hashes (split by newlines)
    hash_list = [h.strip() for h in hashes.split("\n") if h.strip()]
    
    task_data = TaskCreate(
        name=name,
        description=description,
        hash_type=hash_type,
        hash_type_id=hash_type_id,
        hashes=hash_list,
        wordlist_path=wordlist_path,
        rule_path=rule_path,
        mask=mask,
        attack_mode=attack_mode,
        priority=priority
    )
    
    await task_usecase.create_task(task_data)
    return RedirectResponse(url="/tasks", status_code=303)


@app.post("/tasks/new-wpa")
async def create_wpa_task(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    capture_file: str = Form(...),
    wordlist: str = Form("rockyou.txt"),
    workload: int = Form(4),
    status_updates: bool = Form(True),
    status_timer: int = Form(5),
    potfile_disable: bool = Form(True),
    priority: int = Form(2),
    task_usecase: TaskUseCase = Depends(get_task_usecase)
):
    """Create a new WPA cracking task with predefined hashcat parameters"""
    # Construct the hashcat command
    hashcat_command = f"hashcat -m 2500 -a 0 {capture_file} {wordlist} -w {workload}"
    
    if status_updates:
        hashcat_command += f" --status --status-timer={status_timer}"
    
    if potfile_disable:
        hashcat_command += " --potfile-disable"
    
    # Create a placeholder hash list - in real implementation, you'd extract hashes from the capture file
    hash_list = [f"WPA-Handshake-{name}"]
    
    task_data = TaskCreate(
        name=name,
        description=description or f"WPA handshake cracking task using {capture_file}",
        hash_type="wpa",
        hash_type_id=2500,  # WPA/WPA2 hash mode in hashcat
        hashes=hash_list,
        wordlist_path=wordlist,
        attack_mode=0,  # Dictionary attack
        priority=priority,
        metadata={
            "capture_file": capture_file,
            "hashcat_command": hashcat_command,
            "workload": workload,
            "status_timer": status_timer
        }
    )
    
    await task_usecase.create_task(task_data)
    return RedirectResponse(url="/tasks", status_code=303)


@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def task_detail(
    request: Request, 
    task_id: str, 
    task_usecase: TaskUseCase = Depends(get_task_usecase),
    result_usecase: ResultUseCase = Depends(get_result_usecase),
    current_user: User = Depends(get_current_active_user)
):
    """Task detail page"""
    task = await task_usecase.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get results for this task
    results = await result_usecase.get_results_by_task_id(task_id)
    
    return templates.TemplateResponse(
        "task_detail.html",
        {"request": request, "task": task, "results": results, "active_page": "tasks", "user": current_user}
    )


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    task_usecase: TaskUseCase = Depends(get_task_usecase)
):
    """Cancel a task"""
    await task_usecase.cancel_task(task_id)
    return RedirectResponse(url="/tasks", status_code=303)


@app.post("/tasks/{task_id}/delete")
async def delete_task(
    task_id: str,
    task_usecase: TaskUseCase = Depends(get_task_usecase)
):
    """Delete a task"""
    await task_usecase.delete_task(task_id)
    return RedirectResponse(url="/tasks", status_code=303)


# Agent routes
@app.get("/agents", response_class=HTMLResponse)
async def list_agents(
    request: Request, 
    status: Optional[str] = None,
    sort: str = "last_seen",
    agent_usecase: AgentUseCase = Depends(get_agent_usecase),
    current_user: User = Depends(get_current_active_user)
):
    """List all agents with optional filtering"""
    # Get agents with status filter if provided
    agents = await agent_usecase.get_agents(status=status)
    
    # Sort agents based on the sort parameter
    if sort == "name":
        agents = sorted(agents, key=lambda a: a.get("name") if isinstance(a, dict) else getattr(a, "name", ""))
    elif sort == "registered_at":
        agents = sorted(agents, key=lambda a: a.get("registered_at") if isinstance(a, dict) else getattr(a, "registered_at", datetime.datetime.min))
    else:  # default to last_seen
        agents = sorted(agents, key=lambda a: a.get("last_seen") if isinstance(a, dict) else getattr(a, "last_seen", datetime.datetime.min), reverse=True)
    
    return templates.TemplateResponse(
        "agents.html",
        {"request": request, "agents": agents, "active_page": "agents", "current_status": status, "current_sort": sort, "user": current_user}
    )


@app.get("/agents/add", response_class=HTMLResponse)
async def add_agent_form(request: Request, current_user: User = Depends(get_current_active_user)):
    """Show form to add a new agent"""
    # Generate a random API key for the new agent
    import secrets
    import string
    api_key = 'api_key_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
    
    return templates.TemplateResponse(
        "add_agent.html",
        {"request": request, "active_page": "agents", "api_key": api_key, "user": current_user}
    )


@app.post("/agents/add", response_class=HTMLResponse)
async def add_agent(
    request: Request,
    name: str = Form(...),
    hostname: str = Form(...),
    ip_address: str = Form(...),
    api_key: str = Form(...),
    hardware_info: str = Form(""),
    agent_usecase: AgentUseCase = Depends(get_agent_usecase)
):
    """Add a new agent"""
    # Parse hardware_info if provided
    hw_info = {}
    if hardware_info:
        try:
            import json
            hw_info = json.loads(hardware_info)
        except:
            # If JSON parsing fails, just use the string as is
            hw_info = {"raw": hardware_info}
    
    # Create agent data
    from datetime import datetime
    agent_data = {
        "name": name,
        "hostname": hostname,
        "ip_address": ip_address,
        "api_key": api_key,
        "status": "offline",
        "registered_at": datetime.now(),
        "last_seen": datetime.now(),
        "hardware_info": hw_info,
        "capabilities": {},
        "metadata": {}
    }
    
    # Add agent to database
    await agent_usecase.create_agent(agent_data)
    
    # Redirect to agents list
    return RedirectResponse(url="/agents", status_code=303)


@app.get("/agents/{agent_id}", response_class=HTMLResponse)
async def agent_detail(
    request: Request,
    agent_id: str,
    agent_usecase: AgentUseCase = Depends(get_agent_usecase),
    task_usecase: TaskUseCase = Depends(get_task_usecase),
    current_user: User = Depends(get_current_active_user)
):
    """Agent detail page"""
    agent = await agent_usecase.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get current task if any
    current_task = None
    current_task_id = getattr(agent, 'current_task_id', agent.get('current_task_id') if isinstance(agent, dict) else None)
    if current_task_id:
        current_task = await task_usecase.get_task_by_id(current_task_id)
    
    return templates.TemplateResponse(
        "agent_detail.html",
        {"request": request, "agent": agent, "current_task": current_task, "active_page": "agents", "user": current_user}
    )


# Results routes
@app.get("/results", response_class=HTMLResponse)
async def list_results(
    request: Request,
    task_id: Optional[str] = None,
    hash_value: Optional[str] = None,
    plaintext: Optional[str] = None,
    result_usecase: ResultUseCase = Depends(get_result_usecase),
    current_user: User = Depends(get_current_active_user)
):
    """List all results with optional filtering"""
    if task_id:
        results = await result_usecase.get_results_by_task_id(task_id)
    else:
        results = await result_usecase.get_all_results()
    
    # Filter by hash_value if provided
    if hash_value and results:
        results = [r for r in results if (
            isinstance(r, dict) and r.get("hash_value", "").lower().startswith(hash_value.lower())
        ) or (
            not isinstance(r, dict) and getattr(r, "hash_value", "").lower().startswith(hash_value.lower())
        )]
    
    # Filter by plaintext if provided
    if plaintext and results:
        results = [r for r in results if (
            isinstance(r, dict) and plaintext.lower() in r.get("plaintext", "").lower()
        ) or (
            not isinstance(r, dict) and plaintext.lower() in getattr(r, "plaintext", "").lower()
        )]
    
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request, 
            "results": results, 
            "task_id": task_id,
            "hash_value": hash_value,
            "plaintext": plaintext,
            "active_page": "results",
            "user": current_user
        }
    )


@app.post("/upload/handshake")
async def upload_handshake(file: UploadFile = File(...)):
    """Upload a handshake file"""
    # Ensure uploads directory exists
    upload_dir = Path("uploads/handshakes")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if filename is valid
    if not file.filename:
        # Generate a random filename if none provided
        import uuid
        filename = f"handshake_{uuid.uuid4()}.hccapx"
    else:
        filename = file.filename
    
    # Save the file
    file_path = upload_dir / filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return RedirectResponse(url="/files/upload", status_code=303)


@app.post("/upload/wordlist")
async def upload_wordlist(file: UploadFile = File(...)):
    """Upload a wordlist file"""
    # Ensure uploads directory exists
    upload_dir = Path("uploads/wordlists")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if filename is valid
    if not file.filename:
        # Generate a random filename if none provided
        import uuid
        filename = f"wordlist_{uuid.uuid4()}.txt"
    else:
        filename = file.filename
    
    # Save the file
    file_path = upload_dir / filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return RedirectResponse(url="/files/upload", status_code=303)


@app.get("/delete/file")
async def delete_file(request: Request, path: str):
    """Delete an uploaded file"""
    file_path = Path(path)
    
    # Security check: only allow deleting files in the uploads directory
    if "uploads" in str(file_path) and file_path.exists():
        file_path.unlink()
    
    return RedirectResponse(url="/files/upload", status_code=303)


# User Profile route
@app.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request, current_user: User = Depends(get_current_active_user)):
    """User profile page"""
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": current_user, "active_page": "profile"}
    )


# Simple debug endpoint to test API functionality
@app.get("/api/debug", tags=["API"])
async def debug_api():
    """Simple debug endpoint to test if API is working"""
    logger.info("Debug API endpoint called")
    return {"status": "ok", "message": "API is working", "timestamp": str(datetime.now())}

# API endpoint for performance data
@app.get("/api/performance-data", tags=["API"])
async def get_performance_data(
    performance_usecase = Depends(get_performance_usecase)
):
    """Get system performance data for charts.
    
    Returns performance metrics for the dashboard charts including:
    - Active agents over time
    - Completed tasks over time
    - System speed in MH/s over time
    
    The data is returned in a format suitable for Chart.js.
    """
    logger.info("Performance data API endpoint called")
    
    try:
        # Get performance data from the usecase
        result = await performance_usecase.get_hourly_performance_data(24)
        
        logger.info("Retrieved performance data successfully")
        logger.info("Returning performance data response")
        return result
    except Exception as e:
        logger.error(f"Error in performance data API: {str(e)}")
        logger.exception("Exception details:")
        return {"error": str(e)}


# Scheduled task to record performance metrics every 30 seconds
@app.on_event("startup")
@repeat_every(seconds=30)  # Record metrics every 30 seconds
async def record_performance_metrics():
    """Record current performance metrics to the database"""
    try:
        # Get dependencies directly instead of using Depends
        # This is necessary because we're outside of a request context
        task_usecase = await get_task_usecase()
        agent_usecase = await get_agent_usecase()
        
        # Get all tasks and agents
        tasks = await task_usecase.get_all_tasks()
        agents = await agent_usecase.get_all_agents()
        
        # Calculate metrics
        active_agents = [a for a in agents if getattr(a, 'status', a.get('status', None)) == 'online']
        active_agent_ids = [getattr(a, 'id', a.get('id', None)) for a in active_agents]
        
        completed_tasks_count = sum(1 for t in tasks 
                                  if getattr(t, 'status', t.get('status', None)) == TaskStatus.COMPLETED)
        
        # In a real system, you would get the actual speed from agents
        total_speed = sum(getattr(a, 'speed', a.get('speed', 0)) for a in active_agents)
        
        # Log the metrics
        logger.info(f"Recorded performance metrics: {len(active_agents)} active agents, {completed_tasks_count} completed tasks, {total_speed/1000000:.2f} MH/s")
        
        # If we're using a real database, save the metrics
        if not os.getenv("USE_MOCK_DATABASE", "true").lower() == "true":
            from model.performance import PerformanceMetric
            from repository.performance_repository import PerformanceRepository
            
            db = await get_database()
            repo = PerformanceRepository(db.performance_metrics)
            
            metric = PerformanceMetric(
                timestamp=datetime.datetime.now(),
                active_agents=len(active_agents),
                completed_tasks=completed_tasks_count,
                speed=total_speed,
                agent_ids=active_agent_ids
            )
            
            await repo.save_metric(metric)
            logger.info("Saved performance metrics to database")
    except Exception as e:
        logger.error(f"Failed to record performance metrics: {str(e)}")
        logger.exception("Exception details:")


async def main():
    """Run the web dashboard"""
    host = os.getenv("WEB_HOST", "localhost")
    port = int(os.getenv("WEB_PORT", "8080"))
    uvicorn.run("cmd.web.app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    main()
