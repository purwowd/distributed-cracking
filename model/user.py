from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base model for user data"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    role: UserRole = Field(default=UserRole.USER, description="User role for access control")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=8, description="User password (will be hashed)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "Administrator",
                    "role": "admin",
                    "password": "securepassword123"
                },
                {
                    "username": "user1",
                    "email": "user1@example.com",
                    "full_name": "Regular User",
                    "role": "user",
                    "password": "userpassword456"
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """Model for updating user information"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Model for user response data"""
    id: str
    created_at: str
    last_login: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    """Model for user login"""
    username: str
    password: str
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "securepassword123"
                }
            ]
        }
    }


class Token(BaseModel):
    """Model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    
    
class TokenData(BaseModel):
    """Model for token data"""
    username: str
    role: Optional[str] = None
