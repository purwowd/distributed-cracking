#!/usr/bin/env python3
"""
Script to create a new user in MongoDB for the distributed cracking system.
Usage: python create_user.py <username> <email> <password> <role>
Role can be: admin, user, or viewer (default is user if not specified)
"""

import os
import sys
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from enum import Enum

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entity.user import User, UserRole
from config.settings import MONGODB_URI, DATABASE_NAME

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Work factor
    bcrypt__ident="2b"   # Force bcrypt ident
)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

async def create_user(username, email, password, role_str="user"):
    """Create a new user in MongoDB"""
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db.users
    
    # Check if username already exists
    existing_user = await collection.find_one({"username": username})
    if existing_user:
        print(f"Error: User with username '{username}' already exists.")
        return False
    
    # Check if email already exists
    existing_email = await collection.find_one({"email": email})
    if existing_email:
        print(f"Error: User with email '{email}' already exists.")
        return False
    
    # Determine role
    try:
        role = UserRole(role_str.lower())
    except ValueError:
        print(f"Warning: Invalid role '{role_str}'. Using 'user' as default.")
        role = UserRole.USER
    
    # Create user object
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=role,
        full_name=None,  # Optional
        created_at=datetime.utcnow(),
        last_login=None,
        metadata={}
    )
    
    # Insert user into database
    user_dict = user.to_dict()
    # Remove ID if it's None
    if user_dict.get("id") is None:
        user_dict.pop("id", None)
    
    try:
        result = await collection.insert_one(user_dict)
        print(f"Success: User '{username}' created with ID: {result.inserted_id}")
        print(f"Role: {role.value}")
        return True
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False
    finally:
        client.close()

def print_usage():
    """Print usage instructions"""
    print("Usage: python create_user.py <username> <email> <password> <role>")
    print("Role can be: admin, user, or viewer (default is user if not specified)")
    print("Example: python create_user.py admin admin@example.com password123 admin")

async def main():
    """Main function"""
    if len(sys.argv) < 4:
        print_usage()
        return
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) > 4 else "user"
    
    await create_user(username, email, password, role)

if __name__ == "__main__":
    asyncio.run(main())
