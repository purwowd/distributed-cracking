"""
Logging configuration for the distributed cracking system.
Provides structured logging with different handlers for console and file output.
"""
import os
import logging
import logging.handlers
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log file paths
SERVER_LOG = os.path.join(LOG_DIR, "server.log")
AGENT_LOG = os.path.join(LOG_DIR, "agent.log")
ERROR_LOG = os.path.join(LOG_DIR, "error.log")


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields if available
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)


def get_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger with console and file handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console_handler.setFormatter(logging.Formatter(console_format))
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting for structured logging
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        
    # Error file handler for ERROR and above
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG, maxBytes=10*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JsonFormatter())
    logger.addHandler(error_handler)
    
    return logger


def get_server_logger() -> logging.Logger:
    """Get server logger"""
    return get_logger("server", SERVER_LOG)


def get_agent_logger() -> logging.Logger:
    """Get agent logger"""
    return get_logger("agent", AGENT_LOG)


def log_with_context(logger: logging.Logger, level: int, message: str, **context) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: Logger instance
        level: Logging level
        message: Log message
        **context: Additional context fields
    """
    extra = {"extra": context}
    logger.log(level, message, extra=extra)


# Example usage:
# logger = get_server_logger()
# log_with_context(logger, logging.INFO, "Task started", task_id="123", priority=5)
