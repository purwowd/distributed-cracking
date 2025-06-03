"""
Repository layer exceptions for the distributed cracking system.
"""
from typing import Optional, Any, Dict


class RepositoryException(Exception):
    """Base exception for repository layer"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundException(RepositoryException):
    """Exception raised when an entity is not found"""
    def __init__(self, entity_type: str, entity_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{entity_type} with id '{entity_id}' not found"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.entity_id = entity_id


class DuplicateEntityException(RepositoryException):
    """Exception raised when trying to create a duplicate entity"""
    def __init__(self, entity_type: str, key: str, value: Any, details: Optional[Dict[str, Any]] = None):
        message = f"{entity_type} with {key}='{value}' already exists"
        super().__init__(message, details)
        self.entity_type = entity_type
        self.key = key
        self.value = value


class DatabaseConnectionException(RepositoryException):
    """Exception raised when there's a database connection issue"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Database connection error: {message}", details)


class DatabaseOperationException(RepositoryException):
    """Exception raised when a database operation fails"""
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Database operation '{operation}' failed: {message}", details)
        self.operation = operation
