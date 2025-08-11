"""
MongoDB Connection Management
"""
import asyncio
from datetime import datetime
import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError
import structlog

from config import get_settings

logger = structlog.get_logger()


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
        
    async def connect(self) -> None:
        """Establish database connection"""
        try:
            logger.info("🔌 Connecting to MongoDB", uri=self.settings.mongo_uri)
            
            self.client = AsyncIOMotorClient(
                self.settings.mongo_uri,
                serverSelectionTimeoutMS=10000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[self.settings.db_name]
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("✅ Successfully connected to MongoDB", 
                       database=self.settings.db_name)
            
        except ServerSelectionTimeoutError as e:
            logger.error("❌ Failed to connect to MongoDB", error=str(e))
            raise
        except Exception as e:
            logger.error("💥 Unexpected database connection error", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create necessary database indexes"""
        if self.database is not None:
            try:
                # Results collection indexes
                results_collection = self.database[self.settings.results_collection]
                await results_collection.create_index("process_id")
                await results_collection.create_index("user_id")
                await results_collection.create_index("created_at")
                
                # Status collection indexes
                status_collection = self.database[self.settings.status_collection]
                await status_collection.create_index("process_id")
                await status_collection.create_index("user_id")
                await status_collection.create_index("overall_status")
                
                # Config collection indexes
                config_collection = self.database[self.settings.config_collection]
                await config_collection.create_index("process_id")
                await config_collection.create_index("user_id")
                await config_collection.create_index("timestamp")
                
                # Metrics collection indexes
                metrics_collection = self.database[self.settings.metrics_collection]
                await metrics_collection.create_index("process_id")
                await metrics_collection.create_index("user_id")
                await metrics_collection.create_index("calculation_timestamp")
                
                logger.info("📊 Database indexes created successfully")
                
            except Exception as e:
                logger.error("💥 Failed to create database indexes", error=str(e))
    
    def get_collection(self, collection_name: str):
        """Get database collection"""
        if self.database is None:
            raise Exception("Database not connected")
        return self.database[collection_name]
    
    async def health_check(self) -> bool:
        """Check database health"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        except Exception as e:
            logger.error("💥 Database health check failed", error=str(e))
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    if db_manager.database is None:
        await db_manager.connect()
    return db_manager.database
