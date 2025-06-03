from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import traceback
import secrets
import string
from passlib.context import CryptContext
from jose import JWTError, jwt

from entity.user import User, UserRole
from repository.user_repository import UserRepository
from exception.usecase_exception import (
    ResourceNotFoundException,
    ResourceConflictException,
    AuthorizationException
)

# Configure password hashing
# Use more specific configuration to handle different bcrypt versions
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Work factor
    bcrypt__ident="2b"   # Force bcrypt ident
)

# JWT settings (should be moved to config)
SECRET_KEY = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY"  # Should be loaded from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserUseCase:
    """Use case for user management"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        try:
            # Hash the password before storing
            user.hashed_password = self.get_password_hash(user.hashed_password)
            return await self.user_repo.create(user)
        except Exception as e:
            logging.error(f"Error creating user: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user = await self.user_repo.find_by_id(user_id)
            if not user:
                raise ResourceNotFoundException(
                    resource_type="User",
                    resource_id=user_id
                )
            return user
        except Exception as e:
            logging.error(f"Error getting user: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return await self.user_repo.find_by_username(username)
        except Exception as e:
            logging.error(f"Error getting user by username: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        try:
            return await self.user_repo.find_all(skip, limit)
        except Exception as e:
            logging.error(f"Error getting all users: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        """Update user information"""
        try:
            user = await self.user_repo.find_by_id(user_id)
            if not user:
                raise ResourceNotFoundException(
                    resource_type="User",
                    resource_id=user_id
                )
            
            # Update user fields
            if "email" in update_data:
                user.email = update_data["email"]
            if "full_name" in update_data:
                user.full_name = update_data["full_name"]
            if "role" in update_data:
                user.role = update_data["role"]
            if "password" in update_data and update_data["password"]:
                user.hashed_password = self.get_password_hash(update_data["password"])
            
            return await self.user_repo.update(user)
        except Exception as e:
            logging.error(f"Error updating user: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            return await self.user_repo.delete(user_id)
        except Exception as e:
            logging.error(f"Error deleting user: {str(e)}\n{traceback.format_exc()}")
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            user = await self.user_repo.find_by_username(username)
            if not user:
                return None
            if not self.verify_password(password, user.hashed_password):
                return None
            
            # Update last login time
            await self.user_repo.update_last_login(username)
            return user
        except Exception as e:
            logging.error(f"Error authenticating user: {str(e)}\n{traceback.format_exc()}")
            raise
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise AuthorizationException("Could not validate credentials")
            return payload
        except JWTError:
            raise AuthorizationException("Could not validate credentials")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    def generate_password(self, length: int = 12) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def initialize_admin_user(self) -> Optional[User]:
        """Initialize admin user if no users exist"""
        try:
            # Check if any users exist
            user_count = await self.user_repo.count()
            if user_count > 0:
                return None
                
            # Create admin user
            admin_password = self.generate_password()
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=admin_password,  # Will be hashed in create_user
                full_name="Administrator",
                role=UserRole.ADMIN
            )
            
            created_user = await self.create_user(admin_user)
            
            # Log the generated password (in a real system, this should be sent to the admin securely)
            logging.info(f"Created initial admin user with password: {admin_password}")
            print(f"Created initial admin user with password: {admin_password}")
            
            return created_user
        except Exception as e:
            logging.error(f"Error initializing admin user: {str(e)}\n{traceback.format_exc()}")
            raise
