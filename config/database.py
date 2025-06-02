from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

from config.settings import MONGODB_URI, DATABASE_NAME

logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(MONGODB_URI)
            # Verify connection
            await cls.client.admin.command('ping')
            cls.db = cls.client[DATABASE_NAME]
            logger.info(f"Connected to MongoDB at {MONGODB_URI}")
            return cls.db
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        if not cls.db:
            raise ConnectionError("Database not connected. Call connect() first.")
        return cls.db
