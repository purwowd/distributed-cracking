"""
Usecase layer exceptions for the distributed cracking system.
"""
from typing import Optional, Any, Dict


class UseCaseException(Exception):
    """Base exception for usecase layer"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class BusinessRuleViolationException(UseCaseException):
    """Exception raised when a business rule is violated"""
    def __init__(self, rule: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Business rule '{rule}' violated: {message}", details)
        self.rule = rule


class ResourceNotFoundException(UseCaseException):
    """Exception raised when a required resource is not found"""
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ResourceConflictException(UseCaseException):
    """Exception raised when there's a conflict with existing resources"""
    def __init__(self, resource_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"{resource_type} conflict: {message}", details)
        self.resource_type = resource_type


class InvalidOperationException(UseCaseException):
    """Exception raised when an operation is invalid in the current state"""
    def __init__(self, operation: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Invalid operation '{operation}': {reason}", details)
        self.operation = operation
        self.reason = reason


class AuthorizationException(UseCaseException):
    """Exception raised when an operation is not authorized"""
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Not authorized to perform operation: '{operation}'", details)
        self.operation = operation
