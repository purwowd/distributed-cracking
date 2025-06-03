#!/usr/bin/env python3
"""
Script to initialize MongoDB for the distributed cracking system.
This script creates necessary collections, indexes, and default users.
Usage: python init_mongodb.py [--with-sample-data]
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entity.user import User, UserRole
from config.settings import MONGODB_URI, DATABASE_NAME

# Configure password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

async def init_database(with_sample_data=False):
    """Initialize MongoDB database with collections and indexes"""
    print(f"Connecting to MongoDB at {MONGODB_URI}")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    try:
        # Create collections if they don't exist
        collections = ["users", "tasks", "agents", "results", "files"]
        for collection_name in collections:
            if collection_name not in await db.list_collection_names():
                await db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
        
        # Create indexes for users collection
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        print("Created indexes for users collection")
        
        # Create indexes for tasks collection
        await db.tasks.create_index("name")
        await db.tasks.create_index("status")
        await db.tasks.create_index("created_at")
        print("Created indexes for tasks collection")
        
        # Create indexes for agents collection
        await db.agents.create_index("name", unique=True)
        await db.agents.create_index("status")
        await db.agents.create_index("last_heartbeat")
        print("Created indexes for agents collection")
        
        # Create indexes for results collection
        await db.results.create_index("task_id")
        await db.results.create_index("hash")
        await db.results.create_index("plaintext")
        print("Created indexes for results collection")
        
        # Create default admin and user accounts
        await create_default_users(db)
        
        # Add sample data if requested
        if with_sample_data:
            await create_sample_data(db)
        
        print(f"Database '{DATABASE_NAME}' initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        client.close()

async def create_default_users(db):
    """Create default admin and user accounts"""
    # Check if users already exist
    admin_exists = await db.users.find_one({"username": "admin"})
    user_exists = await db.users.find_one({"username": "user"})
    
    if not admin_exists:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN,
            full_name="Administrator",
            created_at=datetime.utcnow(),
            metadata={"is_default": True}
        )
        admin_dict = admin_user.to_dict()
        if admin_dict.get("id") is None:
            admin_dict.pop("id", None)
        
        result = await db.users.insert_one(admin_dict)
        print(f"Created default admin user with ID: {result.inserted_id}")
    else:
        print("Default admin user already exists")
    
    if not user_exists:
        regular_user = User(
            username="user",
            email="user@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.USER,
            full_name="Regular User",
            created_at=datetime.utcnow(),
            metadata={"is_default": True}
        )
        user_dict = regular_user.to_dict()
        if user_dict.get("id") is None:
            user_dict.pop("id", None)
        
        result = await db.users.insert_one(user_dict)
        print(f"Created default regular user with ID: {result.inserted_id}")
    else:
        print("Default regular user already exists")

async def create_sample_data(db):
    """Create sample data for testing"""
    # This function would create sample tasks, agents, and results
    # Implementation depends on the specific data structures needed
    print("Sample data creation not implemented yet")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Initialize MongoDB for the distributed cracking system")
    parser.add_argument("--with-sample-data", action="store_true", help="Add sample data for testing")
    return parser.parse_args()

async def main():
    """Main function"""
    args = parse_args()
    await init_database(with_sample_data=args.with_sample_data)

if __name__ == "__main__":
    asyncio.run(main())
