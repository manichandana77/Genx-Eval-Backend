"""
Metrics Repository - Database operations for metrics storage
"""
from datetime import datetime
from typing import Optional, Dict, Any
import structlog

from database.connection import db_manager
from config import get_settings

logger = structlog.get_logger()


class MetricsRepository:
    """Repository for metrics-related database operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def store_metrics_results(self, process_id: str, metrics_record: Dict[str, Any]) -> None:
        """Store metrics calculation results"""
        try:
            metrics_collection = db_manager.get_collection(self.settings.metrics_collection)
            
            # Add timestamp if not present
            if "created_at" not in metrics_record:
                metrics_record["created_at"] = datetime.utcnow()
            
            await metrics_collection.update_one(
                {"process_id": process_id},
                {"": metrics_record},
                upsert=True
            )
            
            logger.info("📊 Metrics results stored", process_id=process_id)
            
        except Exception as e:
            logger.error("💥 Failed to store metrics results", error=str(e))
            raise
    
    async def get_metrics_results(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics results for a process"""
        try:
            metrics_collection = db_manager.get_collection(self.settings.metrics_collection)
            
            document = await metrics_collection.find_one(
                {"process_id": process_id},
                projection={"_id": 0}
            )
            
            if document:
                logger.info("📊 Metrics results retrieved", process_id=process_id)
            else:
                logger.warning("⚠️ Metrics results not found", process_id=process_id)
            
            return document
            
        except Exception as e:
            logger.error("💥 Failed to get metrics results", error=str(e))
            return None
