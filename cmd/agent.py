import asyncio
import logging
import os
import platform
import socket
import tempfile
import json
import argparse
from datetime import datetime
import aiohttp
from typing import Dict, Any, Optional, List

from config.settings import AGENT_POLL_INTERVAL, AGENT_HEARTBEAT_INTERVAL
from entity.task import TaskStatus
from entity.agent import AgentStatus
from usecase.hashcat_usecase import HashcatUseCase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HashcatAgent:
    """Agent for running hashcat tasks on a GPU server"""
    
    def __init__(self, server_url: str, api_key: str = None, name: str = None):
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.name = name or socket.gethostname()
        self.hostname = socket.gethostname()
        self.ip_address = self._get_ip_address()
        self.hashcat_usecase = HashcatUseCase()
        self.current_task = None
        self.current_process = None
        self.temp_dir = tempfile.mkdtemp(prefix="hashcat_agent_")
        self.registered = False
        self.session = None
    
    async def start(self):
        """Start the agent"""
        logger.info(f"Starting Hashcat Agent on {self.hostname}")
        
        # Create aiohttp session
        self.session = aiohttp.ClientSession(
            headers={"api-key": self.api_key} if self.api_key else {}
        )
        
        # Check hashcat installation
        installed, version = await self.hashcat_usecase.check_hashcat_installation()
        if not installed:
            logger.error(f"Hashcat not installed or not working: {version}")
            await self.session.close()
            return
        
        logger.info(f"Hashcat version: {version}")
        
        # Register with server if not already registered
        if not self.api_key:
            await self.register(version)
        
        # Start main tasks
        await asyncio.gather(
            self.heartbeat_task(),
            self.task_poll_task()
        )
    
    async def register(self, hashcat_version: str):
        """Register agent with server"""
        logger.info("Registering agent with server")
        
        try:
            # Get system info
            gpu_info = await self._get_gpu_info()
            cpu_info = self._get_cpu_info()
            
            # Register with server
            async with self.session.post(
                f"{self.server_url}/agents",
                json={
                    "name": self.name,
                    "hostname": self.hostname,
                    "ip_address": self.ip_address,
                    "capabilities": await self.hashcat_usecase.get_hashcat_capabilities(),
                    "gpu_info": gpu_info,
                    "cpu_info": cpu_info,
                    "hashcat_version": hashcat_version,
                    "metadata": {
                        "os": platform.platform(),
                        "python_version": platform.python_version(),
                    }
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.api_key = data.get("api_key")
                    
                    # Update session headers with API key
                    self.session = aiohttp.ClientSession(
                        headers={"api-key": self.api_key}
                    )
                    
                    logger.info(f"Agent registered successfully with ID: {data.get('id')}")
                    self.registered = True
                else:
                    error = await response.text()
                    logger.error(f"Failed to register agent: {error}")
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
    
    async def heartbeat_task(self):
        """Send periodic heartbeats to server"""
        while True:
            try:
                if self.registered:
                    status = AgentStatus.BUSY if self.current_task else AgentStatus.ONLINE
                    
                    heartbeat_data = {
                        "status": status.value,
                        "current_task_id": self.current_task.get("id") if self.current_task else None,
                    }
                    
                    # Add task progress if available
                    if self.current_task and self.current_process:
                        heartbeat_data["task_progress"] = self.current_task.get("progress", 0)
                        heartbeat_data["task_speed"] = self.current_task.get("speed", 0)
                    
                    async with self.session.post(
                        f"{self.server_url}/agents/heartbeat",
                        json=heartbeat_data
                    ) as response:
                        if response.status == 200:
                            logger.debug("Heartbeat sent successfully")
                        else:
                            error = await response.text()
                            logger.error(f"Failed to send heartbeat: {error}")
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
            
            # Sleep until next heartbeat
            await asyncio.sleep(AGENT_HEARTBEAT_INTERVAL)
    
    async def task_poll_task(self):
        """Poll for tasks from server"""
        while True:
            try:
                if self.registered and not self.current_task:
                    # Check for new task
                    async with self.session.get(
                        f"{self.server_url}/agent/task"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("status") == "ok" and data.get("task"):
                                # Got a new task
                                self.current_task = data["task"]
                                logger.info(f"Received task: {self.current_task['name']}")
                                
                                # Process task in background
                                asyncio.create_task(self.process_task(self.current_task))
            except Exception as e:
                logger.error(f"Error polling for tasks: {e}")
            
            # Sleep until next poll
            await asyncio.sleep(AGENT_POLL_INTERVAL)
    
    async def process_task(self, task: Dict[str, Any]):
        """Process a hashcat task"""
        try:
            logger.info(f"Processing task {task['id']}: {task['name']}")
            
            # Update task status to running
            await self.update_task_status(
                task["id"],
                TaskStatus.RUNNING,
                0.0
            )
            
            # Create output file
            output_file = os.path.join(self.temp_dir, f"task_{task['id']}_output.txt")
            
            # Prepare hashcat command
            command = await self.hashcat_usecase.prepare_task_command(
                task, output_file, self.temp_dir
            )
            
            logger.info(f"Running hashcat command: {' '.join(command)}")
            
            # Run hashcat
            self.current_process = await self.hashcat_usecase.run_hashcat(command)
            
            # Monitor hashcat process
            while True:
                # Check if process is still running
                if self.current_process.returncode is not None:
                    break
                
                # Read output
                stdout_data, stderr_data = await asyncio.gather(
                    self.current_process.stdout.read(1024),
                    self.current_process.stderr.read(1024)
                )
                
                # Parse status
                status_data = await self.hashcat_usecase.parse_hashcat_status(
                    stdout_data, stderr_data
                )
                
                # Update task status
                if status_data["status"] == "error":
                    await self.update_task_status(
                        task["id"],
                        TaskStatus.FAILED,
                        status_data["progress"],
                        status_data["speed"],
                        status_data["error"]
                    )
                    break
                elif status_data["status"] == "completed":
                    # Parse results
                    results = await self.hashcat_usecase.parse_hashcat_results(output_file)
                    
                    # Update task with results
                    await self.update_task_status(
                        task["id"],
                        TaskStatus.COMPLETED,
                        1.0,
                        status_data["speed"],
                        None,
                        results
                    )
                    break
                else:
                    # Update progress
                    task["progress"] = status_data["progress"]
                    task["speed"] = status_data["speed"]
                    
                    await self.update_task_status(
                        task["id"],
                        TaskStatus.RUNNING,
                        status_data["progress"],
                        status_data["speed"]
                    )
                
                # Sleep briefly
                await asyncio.sleep(1)
            
            # Final status update if needed
            if self.current_process.returncode != 0 and task["status"] != TaskStatus.FAILED.value:
                await self.update_task_status(
                    task["id"],
                    TaskStatus.FAILED,
                    task["progress"],
                    task["speed"],
                    f"Hashcat exited with code {self.current_process.returncode}"
                )
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            # Update task status to failed
            await self.update_task_status(
                task["id"],
                TaskStatus.FAILED,
                task.get("progress", 0),
                task.get("speed", 0),
                str(e)
            )
        finally:
            # Clean up
            self.current_task = None
            self.current_process = None
    
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: float,
        speed: float = None,
        error: str = None,
        recovered_hashes: List[Dict[str, str]] = None
    ):
        """Update task status on server"""
        try:
            status_data = {
                "status": status.value,
                "progress": progress,
                "speed": speed,
                "error": error,
                "recovered_hashes": recovered_hashes or []
            }
            
            async with self.session.post(
                f"{self.server_url}/agent/task/{task_id}/status",
                json=status_data
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    logger.error(f"Failed to update task status: {error}")
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
    
    async def _get_gpu_info(self) -> List[Dict[str, Any]]:
        """Get GPU information"""
        # Use hashcat capabilities to get GPU info
        capabilities = await self.hashcat_usecase.get_hashcat_capabilities()
        return capabilities.get("devices", [])
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        info = {
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "cores": os.cpu_count()
        }
        return info
    
    def _get_ip_address(self) -> str:
        """Get primary IP address"""
        try:
            # Create a socket to determine primary IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hashcat Agent for distributed cracking")
    parser.add_argument("--server", required=True, help="Server URL")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--name", help="Agent name")
    args = parser.parse_args()
    
    # Create and start agent
    agent = HashcatAgent(args.server, args.api_key, args.name)
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
