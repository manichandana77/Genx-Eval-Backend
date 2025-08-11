"""
Status Repository - Database operations for status tracking
"""
from datetime import datetime
from typing import Optional, Dict, Any
import structlog

from database.connection import db_manager
from models import StatusRecord
from config import get_settings

logger = structlog.get_logger()


class StatusRepository:
    """Repository for status-related database operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def update_status_record(self, status_record: StatusRecord) -> None:
        """Update status record"""
        try:
            status_collection = db_manager.get_collection(self.settings.status_collection)
            
            # Convert StatusRecord to dict
            if isinstance(status_record, StatusRecord):
                status_data = status_record.dict()
            else:
                status_data = status_record
            
            status_data["updated_at"] = datetime.utcnow()
            
            await status_collection.update_one(
                {"process_id": status_data["process_id"]},
                {"": status_data},
                upsert=True
            )
            
            logger.info("📊 Status record updated", process_id=status_data["process_id"])
            
        except Exception as e:
            logger.error("💥 Failed to update status record", error=str(e))
            raise
    
    async def get_status_document_by_process_id(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get status document by process ID"""
        try:
            status_collection = db_manager.get_collection(self.settings.status_collection)
            
            document = await status_collection.find_one({"process_id": process_id})
            
            if document:
                logger.info("📊 Status document retrieved", process_id=process_id)
            else:
                logger.warning("⚠️ Status document not found", process_id=process_id)
            
            return document
            
        except Exception as e:
            logger.error("💥 Failed to get status document", error=str(e))
            return None
    
    async def get_status_details(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status information"""
        try:
            status_collection = db_manager.get_collection(self.settings.status_collection)
            
            cursor = status_collection.find(
                {"process_id": process_id},
                projection={"models": 1, "overall_status": 1, "_id": 0}
            )
            
            status_list = []
            async for document in cursor:
                models = document.get("models", [])
                overall_status = document.get("overall_status", "Unknown")
                
                status_list.append({
                    "process_id": process_id,
                    "models": models,
                    "overall_status": overall_status
                })
            
            if status_list:
                return {"statuses": status_list}
            
            return None
            
        except Exception as e:
            logger.error("💥 Failed to get status details", error=str(e))
            return None
    
    async def check_ongoing_task(self, user_id: str) -> bool:
        """Check if user has ongoing task"""
        try:
            status_collection = db_manager.get_collection(self.settings.status_collection)
            
            document = await status_collection.find_one({
                "user_id": user_id, 
                "overall_status": "In Progress"
            })
            
            is_ongoing = document is not None
            logger.info("🔍 Ongoing task check", user_id=user_id, ongoing=is_ongoing)
            
            return is_ongoing
            
        except Exception as e:
            logger.error("💥 Failed to check ongoing task", error=str(e))
            return False
