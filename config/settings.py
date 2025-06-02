import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hashcat_cracking")

# Server settings
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Agent settings
AGENT_POLL_INTERVAL = int(os.getenv("AGENT_POLL_INTERVAL", "5"))  # seconds
AGENT_HEARTBEAT_INTERVAL = int(os.getenv("AGENT_HEARTBEAT_INTERVAL", "30"))  # seconds

# Hashcat settings
HASHCAT_PATH = os.getenv("HASHCAT_PATH", "/usr/bin/hashcat")
DEFAULT_HASHCAT_ARGS = os.getenv("DEFAULT_HASHCAT_ARGS", "--status --status-timer=10")

# Task settings
TASK_CHUNK_SIZE = int(os.getenv("TASK_CHUNK_SIZE", "1000"))  # number of hashes per task
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "3600"))  # seconds
