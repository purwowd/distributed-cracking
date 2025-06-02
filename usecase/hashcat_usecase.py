import asyncio
import logging
import re
import os
import json
from typing import List, Dict, Any, Optional, Tuple

from config.settings import HASHCAT_PATH, DEFAULT_HASHCAT_ARGS
from entity.task import Task, HashType

logger = logging.getLogger(__name__)


class HashcatUseCase:
    """Use case for hashcat operations"""
    
    def __init__(self, hashcat_path: str = None):
        self.hashcat_path = hashcat_path or HASHCAT_PATH
    
    async def check_hashcat_installation(self) -> Tuple[bool, str]:
        """Check if hashcat is installed and get version"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.hashcat_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return False, stderr.decode().strip()
            
            version = stdout.decode().strip()
            return True, version
        except Exception as e:
            logger.error(f"Error checking hashcat installation: {e}")
            return False, str(e)
    
    async def get_hashcat_capabilities(self) -> Dict[str, Any]:
        """Get hashcat capabilities (supported hash types, devices, etc.)"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.hashcat_path, "--benchmark", "--machine-readable",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Parse capabilities
            capabilities = {
                "hash_types": {},
                "devices": []
            }
            
            # Get devices
            device_pattern = re.compile(r"Device #(\d+): (.*), (\d+)/(\d+) MB")
            for line in stderr.decode().split("\n"):
                device_match = device_pattern.search(line)
                if device_match:
                    device_id, device_name, mem_used, mem_total = device_match.groups()
                    capabilities["devices"].append({
                        "id": int(device_id),
                        "name": device_name,
                        "memory_used_mb": int(mem_used),
                        "memory_total_mb": int(mem_total)
                    })
            
            return capabilities
        except Exception as e:
            logger.error(f"Error getting hashcat capabilities: {e}")
            return {"error": str(e)}
    
    async def prepare_task_command(self, task: Task, output_file: str, temp_dir: str) -> List[str]:
        """Prepare hashcat command for a task"""
        # Create hash file
        hash_file = os.path.join(temp_dir, f"task_{task.id}_hashes.txt")
        with open(hash_file, "w") as f:
            for hash_value in task.hashes:
                f.write(f"{hash_value}\n")
        
        # Base command
        command = [
            self.hashcat_path,
            "-m", str(task.hash_type_id or self._get_hash_type_id(task.hash_type)),
            "-a", str(task.attack_mode),
            "-o", output_file,
            "--outfile-format=3",
            "--status",
            "--machine-readable"
        ]
        
        # Add default args
        if DEFAULT_HASHCAT_ARGS:
            command.extend(DEFAULT_HASHCAT_ARGS.split())
        
        # Add hash file
        command.append(hash_file)
        
        # Add attack-specific options
        if task.attack_mode == 0:  # Dictionary attack
            if task.wordlist_path:
                command.append(task.wordlist_path)
            if task.rule_path:
                command.extend(["-r", task.rule_path])
        elif task.attack_mode == 3:  # Brute force with mask
            if task.mask:
                command.append(task.mask)
        
        # Add additional args if provided
        if task.additional_args:
            command.extend(task.additional_args.split())
        
        return command
    
    async def run_hashcat(self, command: List[str]) -> asyncio.subprocess.Process:
        """Run hashcat command"""
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return process
    
    async def parse_hashcat_status(self, stdout: bytes, stderr: bytes) -> Dict[str, Any]:
        """Parse hashcat status output"""
        status = {
            "progress": 0.0,
            "speed": 0.0,
            "recovered_hashes": [],
            "status": "running",
            "error": None
        }
        
        try:
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            
            # Check for errors
            if "ERROR" in stderr_str:
                error_match = re.search(r"ERROR: (.*)", stderr_str)
                if error_match:
                    status["error"] = error_match.group(1)
                    status["status"] = "error"
                    return status
            
            # Parse progress
            progress_match = re.search(r"Progress\.+: (\d+)/(\d+) \((\d+\.\d+)%\)", stdout_str)
            if progress_match:
                current, total, percentage = progress_match.groups()
                status["progress"] = float(percentage) / 100.0
            
            # Parse speed
            speed_match = re.search(r"Speed\.+: (\d+(?:\.\d+)?)\s+([MKG]?H/s)", stdout_str)
            if speed_match:
                speed_value, speed_unit = speed_match.groups()
                speed = float(speed_value)
                if speed_unit == "KH/s":
                    speed *= 1000
                elif speed_unit == "MH/s":
                    speed *= 1000000
                elif speed_unit == "GH/s":
                    speed *= 1000000000
                status["speed"] = speed
            
            # Check if completed
            if "Stopped" in stdout_str or "Exhausted" in stdout_str:
                status["status"] = "completed"
                status["progress"] = 1.0
            
            return status
        except Exception as e:
            logger.error(f"Error parsing hashcat status: {e}")
            status["error"] = str(e)
            status["status"] = "error"
            return status
    
    async def parse_hashcat_results(self, output_file: str) -> List[Dict[str, str]]:
        """Parse hashcat results file"""
        results = []
        try:
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            parts = line.split(":")
                            if len(parts) >= 2:
                                hash_value = parts[0]
                                plaintext = ":".join(parts[1:])
                                results.append({
                                    "hash": hash_value,
                                    "plaintext": plaintext
                                })
        except Exception as e:
            logger.error(f"Error parsing hashcat results: {e}")
        
        return results
    
    def _get_hash_type_id(self, hash_type: HashType) -> int:
        """Get hashcat hash type ID from enum"""
        hash_type_map = {
            HashType.MD5: 0,
            HashType.SHA1: 100,
            HashType.SHA256: 1400,
            HashType.SHA512: 1700,
            HashType.NTLM: 1000,
            HashType.WPA: 2500,
            HashType.BCRYPT: 3200,
            HashType.CUSTOM: 0  # Default to MD5 for custom
        }
        return hash_type_map.get(hash_type, 0)
