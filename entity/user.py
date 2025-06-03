from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User:
    """User entity for authentication and authorization"""
    
    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
        full_name: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user entity to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "hashed_password": self.hashed_password,
            "full_name": self.full_name,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user entity from dictionary"""
        if not data:
            return None
            
        # Convert string dates to datetime objects
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        last_login = data.get("last_login")
        if last_login and isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
            
        # Convert role string to enum
        role = data.get("role")
        if role and isinstance(role, str):
            try:
                role = UserRole(role)
            except ValueError:
                role = UserRole.USER
                
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            hashed_password=data.get("hashed_password"),
            full_name=data.get("full_name"),
            role=role,
            created_at=created_at,
            last_login=last_login,
            metadata=data.get("metadata", {})
        )
