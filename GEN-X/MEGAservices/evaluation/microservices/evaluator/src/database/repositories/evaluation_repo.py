"""
Evaluation Repository - Database operations for evaluations
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import structlog

from database.connection import db_manager
from models import EvaluationResult
from config import get_settings

logger = structlog.get_logger()


class EvaluationRepository:
    """Repository for evaluation-related database operations"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def insert_config_record(self, config_data: Dict[str, Any]) -> None:
        """Insert configuration record"""
        try:
            config_collection = db_manager.get_collection(self.settings.config_collection)
            
            await config_collection.insert_one({
                "user_id": config_data['user_id'],
                "process_id": config_data['process_id'], 
                "process_name": config_data["process_name"],
                "model_id": config_data["model_id"],
                "model_name": config_data["model_name"],
                "payload_file_path": config_data["payload_file_path"],
                "timestamp": int(datetime.utcnow().timestamp())
            })
            
            logger.info("📊 Config record inserted", process_id=config_data['process_id'])
            
        except Exception as e:
            logger.error("💥 Failed to insert config record", error=str(e))
            raise
    
    async def update_results_record(
        self, 
        process_id: str, 
        process_name: str, 
        user_id: str, 
        config_type: str, 
        model_id: str, 
        model_name: str, 
        results_data: Dict[str, Any]
    ) -> None:
        """Update results record"""
        try:
            results_collection = db_manager.get_collection(self.settings.results_collection)
            
            result = await results_collection.update_one(
                {
                    "process_id": process_id,
                    "model_id": model_id
                },
                {
                    "": {
                        "process_name": process_name,
                        "user_id": user_id,
                        "config_type": config_type,
                        "model_name": model_name,
                        "results": results_data,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            if result.matched_count > 0:
                logger.info("📊 Results updated", process_id=process_id, model_id=model_id)
            else:
                logger.info("📊 Results inserted", process_id=process_id, model_id=model_id)
                
        except Exception as e:
            logger.error("💥 Failed to update results record", error=str(e))
            raise
    
    async def get_results(self, process_id: str) -> List[Dict[str, Any]]:
        """Get all results for a process"""
        try:
            results_collection = db_manager.get_collection(self.settings.results_collection)
            
            cursor = results_collection.find(
                {"process_id": process_id},
                projection={"_id": 0}
            )
            
            results = []
            async for document in cursor:
                results.append(document)
            
            logger.info("📊 Retrieved results", process_id=process_id, count=len(results))
            return results
            
        except Exception as e:
            logger.error("💥 Failed to get results", error=str(e))
            return []
    
    async def get_process_results(
        self, 
        user_id: str, 
        page: int, 
        page_size: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get process results with pagination"""
        try:
            config_collection = db_manager.get_collection(self.settings.config_collection)
            status_collection = db_manager.get_collection(self.settings.status_collection)
            
            skip = (page - 1) * page_size
            cursor = config_collection.find({"user_id": user_id}).sort("timestamp", -1).skip(skip).limit(page_size)
            
            results = []
            async for document in cursor:
                process_id = document.get("process_id")
                
                # Get status information
                status_document = await status_collection.find_one({"process_id": str(process_id)})
                overall_status = status_document.get("overall_status") if status_document else "Unknown"
                
                results.append({
                    "process_id": process_id,
                    "process_name": document.get("process_name"),
                    "timestamp": document.get("timestamp"),
                    "overall_status": overall_status,
                    "model_name": document.get("model_name"),
                    "payload_file_path": document.get("payload_file_path")
                })
            
            # Get total count
            total_count = await config_collection.count_documents({"user_id": user_id})
            
            logger.info("📊 Retrieved process results", 
                       user_id=user_id, page=page, count=len(results))
            
            return results, total_count
            
        except Exception as e:
            logger.error("💥 Failed to get process results", error=str(e))
            return [], 0
