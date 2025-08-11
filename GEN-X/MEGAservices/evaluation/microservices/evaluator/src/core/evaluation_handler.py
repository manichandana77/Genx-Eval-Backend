"""
Evaluation Handler - Main Orchestration Logic
🎯 Modified from your existing code to use DeepEval service via gRPC
"""
import asyncio
import os
import time
import uuid
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional

import structlog

from core.grpc_client_fixed import DeepEvalGRPCClient
from database.repositories.evaluation_repo import EvaluationRepository
from database.repositories.status_repo import StatusRepository  
from database.repositories.metrics_repo import MetricsRepository
from models import EvaluationRequest, StatusRecord, ModelStatus
from config import get_settings

logger = structlog.get_logger()


class EvaluationHandler:
    """
    🔥 MAIN EVALUATION ORCHESTRATOR
    
    Modified from your existing evaluation_handler.py to:
    1. Keep all the existing evaluation logic
    2. Replace metrics calculation with gRPC calls to DeepEval service
    """
    
    # Class-level task status storage (same as your original)
    task_statuses = {}
    results_path = "results"
    
    def __init__(self, payload: EvaluationRequest, org_id: str = "default"):
        self.payload = payload
        self.org_id = org_id
        self.settings = get_settings()
        
        # Initialize repositories
        self.eval_repo = EvaluationRepository()
        self.status_repo = StatusRepository()
        self.metrics_repo = MetricsRepository()
        
        # Extract config data (same as your original logic)
        self.user_id = getattr(payload, 'user_id', 'default_user')
        self.session_id = getattr(payload, 'session_id', str(uuid.uuid4()))
        self.process_name = getattr(payload, 'process_name', 'evaluation')
        
        # Model configuration
        self.config_ids = []
        self.model_names = []
        
        # Extract model configurations
        config_id = getattr(payload, 'config_id', [])
        if isinstance(config_id, list):
            for config in config_id:
                if isinstance(config, dict):
                    for config_id, model_name in config.items():
                        self.config_ids.append(config_id)
                        self.model_names.append(model_name)
                else:
                    # Handle simple string configs
                    self.config_ids.append(str(config))
                    self.model_names.append(f"model_{config}")
        
        logger.info("🎯 EvaluationHandler initialized", 
                   user_id=self.user_id,
                   models=self.model_names,
                   metrics=payload.metrics if hasattr(payload, 'metrics') else 'default')
    
    async def background_evaluation(self, process_id: str):
        """
        🚀 MAIN EVALUATION METHOD
        
        Same structure as your original but with gRPC metrics calculation
        """
        start_time = datetime.now()
        
        # Initialize in-memory storage (same as original)
        EvaluationHandler.task_statuses[process_id] = {
            "models": {model_id: "Not Started" for model_id in self.config_ids},
            "overall_status": "In Progress",
            "start_time": start_time,
            "end_time": None,
            "async_task": asyncio.current_task()
        }
        
        try:
            # Store initial configuration (same as original)
            await self._store_initial_config(process_id)
            
            # Create initial status record (same as original)
            await self._create_initial_status_record(process_id, start_time)
            
            # Process each model (same structure as original)
            await self._process_all_models(process_id)
            
            # 🔥 NEW: Calculate metrics using DeepEval service via gRPC
            await self._calculate_metrics_via_grpc(process_id)
            
            # Finalize evaluation (same as original)
            await self._finalize_evaluation(process_id, start_time)
            
            return {"status": EvaluationHandler.task_statuses, "detail": "Evaluation completed"}
            
        except Exception as e:
            logger.error("💥 Evaluation failed", process_id=process_id, error=str(e))
            await self._handle_evaluation_failure(process_id, str(e))
            raise Exception(f"Evaluation failed: {str(e)}")
    
    async def _store_initial_config(self, process_id: str):
        """Store initial configuration (same as original)"""
        config_data = {
            "user_id": self.user_id,
            "process_id": process_id,
            "process_name": self.process_name,
            "model_id": self.config_ids,
            "model_name": self.model_names,
            "payload_file_path": self.payload.file_path
        }
        await self.eval_repo.insert_config_record(config_data)
    
    async def _create_initial_status_record(self, process_id: str, start_time: datetime):
        """Create initial status record (same as original)"""
        status_record = StatusRecord(
            process_id=process_id,
            user_id=self.user_id,
            models=[
                ModelStatus(
                    config_id=model_id,
                    model_name=self.model_names[index],
                    status="Not Started"
                )
                for index, model_id in enumerate(self.config_ids)
            ],
            overall_status="In Progress",
            start_time=start_time
        )
        
        await self.status_repo.update_status_record(status_record)
    
    async def _process_all_models(self, process_id: str):
        """Process all models sequentially (same logic as original)"""
        for index, model_id in enumerate(self.config_ids):
            try:
                await self._evaluate_single_model(process_id, index, model_id)
                
            except Exception as e:
                logger.error("💥 Model evaluation failed", 
                           model_id=model_id, error=str(e))
                await self._mark_model_failed(process_id, index, model_id, str(e))
    
    async def _evaluate_single_model(self, process_id: str, index: int, model_id: str):
        """Evaluate single model (same structure as original)"""
        try:
            # Update model status to "In Progress"
            await self._update_model_status(process_id, index, model_id, "In Progress")
            
            # Load and process evaluation data (same logic as your original)
            evaluation_data = await self._load_and_process_dataset(model_id)
            
            # Store model evaluation results
            model_name = self.model_names[index]
            await self.eval_repo.update_results_record(
                process_id=process_id,
                process_name=self.process_name,
                user_id=self.user_id,
                config_type="LLM",  # Default type
                model_id=model_id,
                model_name=model_name,
                results_data={"evaluation_data": evaluation_data}
            )
            
            # Mark model as completed
            await self._update_model_status(process_id, index, model_id, "Completed")
            
        except Exception as e:
            await self._mark_model_failed(process_id, index, model_id, str(e))
            raise
    
    async def _load_and_process_dataset(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Load and process dataset (adapted from your original logic)
        """
        try:
            # Load YAML data (same as your original)
            if os.path.isfile(self.payload.file_path):
                with open(self.payload.file_path, 'r') as file:
                    collection = yaml.safe_load(file)
            else:
                raise ValueError(f"Dataset file not found: {self.payload.file_path}")
            
            # Process dataset based on structure (same logic as original)
            evaluation_data = []
            
            # Handle task-type based YAML structure
            if "data" in collection and isinstance(collection["data"], list):
                for item in collection["data"]:
                    processed_item = self._process_dataset_item(item, model_id)
                    evaluation_data.append(processed_item)
            else:
                # Handle legacy format
                for key, value in collection.items():
                    if key not in ["task_type", "description", "metadata"]:
                        for item in value:
                            processed_item = self._process_dataset_item(item, model_id)
                            evaluation_data.append(processed_item)
            
            logger.info("📊 Dataset processed", 
                       model_id=model_id, 
                       items_count=len(evaluation_data))
            
            return evaluation_data
            
        except Exception as e:
            logger.error("💥 Dataset processing failed", error=str(e))
            raise
    
    def _process_dataset_item(self, item: Dict[str, Any], model_id: str) -> Dict[str, Any]:
        """Process individual dataset item (adapted from your original)"""
        model_name = self.model_names[self.config_ids.index(model_id)]
        
        # Extract model response for this specific model
        model_response = item.get("model_responses", {}).get(model_name, "")
        
        return {
            "question": item.get("question", ""),
            "expected_answer": item.get("expected_answer", ""),
            "context": item.get("context", ""),
            "model_response": model_response,
            "reference_output": item.get("reference_output", ""),
            "category": item.get("category", ""),
            "difficulty": item.get("difficulty", ""),
            "metadata": item.get("metadata", {})
        }
    
    async def _calculate_metrics_via_grpc(self, process_id: str):
        """
        🔥 NEW: Calculate metrics using DeepEval service via gRPC
        
        This replaces your original evaluation_service.calculate_metrics_for_results()
        """
        try:
            logger.info("🧠 Starting metrics calculation via DeepEval service", 
                       process_id=process_id)
            
            # Get all evaluation results
            all_results = await self.eval_repo.get_results(process_id)
            
            if not all_results:
                logger.warning("⚠️ No evaluation results found for metrics calculation")
                return
            
            # Extract evaluation data for metrics calculation
            all_evaluation_data = []
            for model_data in all_results:
                model_results = model_data.get('results', {})
                eval_data = model_results.get('evaluation_data', [])
                all_evaluation_data.extend(eval_data)
            
            if not all_evaluation_data:
                logger.warning("⚠️ No evaluation data found for metrics calculation")
                return
            
            # Get metrics to calculate
            metrics = (self.payload.metrics if hasattr(self.payload, 'metrics') and self.payload.metrics
                      else self.settings.default_metrics_list)
            
            # 🚀 Call DeepEval service via gRPC
            async with DeepEvalGRPCClient() as deepeval_client:
                metrics_result = await deepeval_client.calculate_batch_metrics(
                    evaluation_data=all_evaluation_data,
                    metrics=metrics,
                    process_id=process_id,
                    user_id=self.user_id
                )
            
            # Store metrics results in database
            if metrics_result["success"]:
                metrics_record = {
                    "process_id": process_id,
                    "user_id": self.user_id,
                    "metrics_results": metrics_result["results"],
                    "metrics_calculated": metrics,
                    "calculation_timestamp": time.time(),
                    "execution_time_ms": metrics_result["execution_time_ms"],
                    "summary_stats": metrics_result["summary_stats"]
                }
                
                await self.metrics_repo.store_metrics_results(process_id, metrics_record)
                
                logger.info("✅ Metrics calculation complete via DeepEval service",
                           process_id=process_id,
                           metrics=metrics,
                           execution_time_ms=metrics_result["execution_time_ms"])
            else:
                logger.error("💥 Metrics calculation failed", 
                           process_id=process_id)
                
        except Exception as e:
            logger.error("💥 DeepEval metrics calculation failed", 
                        process_id=process_id, error=str(e))
            # Don't fail the whole evaluation if metrics fail
    
    async def _update_model_status(self, process_id: str, index: int, model_id: str, status: str):
        """Update model status"""
        # Update in-memory status
        EvaluationHandler.task_statuses[process_id]["models"][model_id] = status
        
        # Update in database
        status_record = await self.status_repo.get_status_document_by_process_id(process_id)
        if status_record and "models" in status_record:
            if index < len(status_record["models"]):
                status_record["models"][index]["status"] = status
                await self.status_repo.update_status_record(status_record)
    
    async def _mark_model_failed(self, process_id: str, index: int, model_id: str, error: str):
        """Mark model as failed"""
        await self._update_model_status(process_id, index, model_id, "Failed")
        logger.error("❌ Model marked as failed", 
                    model_id=model_id, error=error)
    
    async def _finalize_evaluation(self, process_id: str, start_time: datetime):
        """Finalize evaluation (same as original)"""
        end_time = datetime.now()
        
        # Determine overall status
        model_statuses = EvaluationHandler.task_statuses[process_id]["models"]
        all_completed = all(status == "Completed" for status in model_statuses.values())
        
        overall_status = "Completed" if all_completed else "Failed"
        
        # Update final status
        EvaluationHandler.task_statuses[process_id].update({
            "overall_status": overall_status,
            "end_time": end_time
        })
        
        # Update database
        status_record = await self.status_repo.get_status_document_by_process_id(process_id)
        if status_record:
            status_record["overall_status"] = overall_status
            status_record["end_time"] = end_time
            await self.status_repo.update_status_record(status_record)
        
        logger.info("🏁 Evaluation finalized", 
                   process_id=process_id,
                   status=overall_status,
                   duration=(end_time - start_time).total_seconds())
    
    async def _handle_evaluation_failure(self, process_id: str, error: str):
        """Handle evaluation failure"""
        EvaluationHandler.task_statuses[process_id].update({
            "overall_status": "Failed",
            "end_time": datetime.now(),
            "error": error
        })
        
        # Update database status
        status_record = await self.status_repo.get_status_document_by_process_id(process_id)
        if status_record:
            status_record["overall_status"] = "Failed"
            await self.status_repo.update_status_record(status_record)
    
    @staticmethod
    async def get_status_details(process_id: str, service: str):
        """Get status details (same as original)"""
        try:
            # Try in-memory first
            if process_id in EvaluationHandler.task_statuses:
                task_status = EvaluationHandler.task_statuses[process_id]
                models = task_status.get("models", {})
                overall_status = task_status.get("overall_status", "Unknown")
                
                # Convert models dict to list format
                if isinstance(models, dict):
                    models_list = [
                        {"model_id": model_id, "status": status}
                        for model_id, status in models.items()
                    ]
                    return models_list, overall_status
                
                return models, overall_status
            
            # Fallback to database
            status_repo = StatusRepository()
            status_doc = await status_repo.get_status_document_by_process_id(process_id)
            
            if status_doc:
                return status_doc.get("models", []), status_doc.get("overall_status", "Unknown")
            
            return None, "Process not found"
            
        except Exception as e:
            logger.error("💥 Error getting status details", error=str(e))
            return None, f"Error: {str(e)}"
