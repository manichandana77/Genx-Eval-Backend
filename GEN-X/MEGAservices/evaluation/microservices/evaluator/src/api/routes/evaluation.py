"""
Main Evaluation Routes
🎯 Adapted from your original evaluation routes with gRPC integration
"""
import asyncio
import json
import uuid
from typing import Dict, Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import StreamingResponse
import structlog

from models import (
    EvaluationRequest, EvaluationRequestPayload, EvaluationResponse, 
    StatusRequest, ResultsRequest, StopEvaluationRequest,
    APIResponse
)
from core.evaluation_handler import EvaluationHandler
from database.repositories.status_repo import StatusRepository
from database.repositories.evaluation_repo import EvaluationRepository
from database.repositories.metrics_repo import MetricsRepository
from config import get_settings

logger = structlog.get_logger()
router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_dataset(
    request_data: EvaluationRequestPayload,
    background_tasks: BackgroundTasks
):
    """
    🚀 Main evaluation endpoint - adapted from your original with gRPC integration
    
    Starts evaluation process and calls DeepEval service for metrics calculation
    """
    try:
        logger.info("📤 Starting dataset evaluation", request_data=request_data.dict())
        
        # Validate input (same as your original)
        if not isinstance(request_data.dict(), dict) or "orgId" not in request_data.dict() or "payload" not in request_data.dict():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data. Expected a dictionary with 'orgId' and 'payload' keys."
            )

        org_id = request_data.orgId
        payload_data = request_data.payload
        
        logger.info("🔍 Processing evaluation request", org_id=org_id, payload=payload_data)
        
        # Create EvaluationRequest from payload
        try:
            evaluation_request = EvaluationRequest(
                file_path=payload_data.get("payload_file_path", ""),
                user_id=payload_data.get("user_id", "default_user"),
                session_id=payload_data.get("session_id", str(uuid.uuid4())),
                config_id=payload_data.get("config_id", [{"default": "default_model"}]),
                client_api_key=payload_data.get("client_api_key", ""),
                process_name=payload_data.get("process_name", "evaluation"),
                metrics=payload_data.get("metrics", ["answer_relevancy", "faithfulness", "bias"])
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Payload validation error: {str(e)}"
            )

        # Check for ongoing tasks
        status_repo = StatusRepository()
        if await status_repo.check_ongoing_task(evaluation_request.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an ongoing evaluation task."
            )

        # Generate process ID
        process_id = str(uuid.uuid4()).replace("-", "")[:8]
        logger.info("🆔 Generated process ID", process_id=process_id)

        # Initialize evaluation handler
        evaluation_handler = EvaluationHandler(evaluation_request, org_id)
        
        # 🔥 Add background task - this will call DeepEval service via gRPC
        background_tasks.add_task(evaluation_handler.background_evaluation, process_id)

        logger.info("🚀 Evaluation task started", process_id=process_id)

        return EvaluationResponse(
            status_code=200,
            process_id=process_id,
            message="Evaluation has been started in the background"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("💥 Unexpected error in evaluate_dataset", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error occurred: {str(e)}"
        )


@router.get("/status")
async def check_process_status(
    process_id: str = Query(...), 
    service: str = Query(...)
):
    """
    📊 Check evaluation status with Server-Sent Events (SSE)
    
    Same SSE logic as your original
    """
    async def event_generator():
        try:
            while True:
                logger.info("🔍 Checking status", process_id=process_id, service=service)
                
                # Get status details
                model_statuses, overall_status = await EvaluationHandler.get_status_details(
                    process_id, service
                )

                if model_statuses is None:
                    yield f"data: {json.dumps({'error': overall_status})}\\n\\n"
                    await asyncio.sleep(2)
                    continue

                # Prepare response data
                response_data = {
                    "models": model_statuses,
                    "overall_status": overall_status
                }
                logger.info("📊 Status data", response_data=response_data)
                yield f"data: {json.dumps(response_data)}\\n\\n"

                # Check if all models complete
                all_tasks_complete = all(
                    model["status"] in ["Completed", "Failed"]
                    for model in model_statuses
                )

                if all_tasks_complete:
                    break

                await asyncio.sleep(2)

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\\n\\n"
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.post("/results")
async def get_process_results(request_data: ResultsRequest):
    """
    📋 Get evaluation results with pagination
    
    Same logic as your original
    """
    try:
        logger.info("📊 Getting process results", request_data=request_data.dict())
        
        # Extract pagination info
        org_id = request_data.orgId
        user_id = request_data.user_id
        page = request_data.page
        page_size = request_data.page_size
        
        # Get results
        eval_repo = EvaluationRepository()
        results, total_count = await eval_repo.get_process_results(user_id, page, page_size)
        
        return {
            "status_code": 200,
            "data": {
                "results": results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                }
            }
        }
        
    except Exception as e:
        logger.error("💥 Error getting process results", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving results: {str(e)}"
        )


@router.get("/metrics")
async def get_available_metrics():
    """Get available metrics from DeepEval service"""
    try:
        # 🔥 Call DeepEval service to get available metrics
        from core.grpc_client_fixed import DeepEvalGRPCClient
        
        async with DeepEvalGRPCClient() as client:
            metrics_info = await client.get_available_metrics()
        
        return APIResponse(
            success=True,
            message="Available metrics retrieved successfully",
            data=metrics_info
        )
        
    except Exception as e:
        logger.error("💥 Error getting available metrics", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/metrics/results")
async def get_metrics_results(
    process_id: str = Query(...),
    org_id: str = Query(...)
):
    """Get metrics results for a completed evaluation"""
    try:
        metrics_repo = MetricsRepository()
        metrics_data = await metrics_repo.get_metrics_results(process_id)
        
        if not metrics_data:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for process {process_id}"
            )
        
        return {
            "status_code": 200,
            "data": metrics_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("💥 Error getting metrics results", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving metrics: {str(e)}"
        )


@router.post("/stop")
async def stop_evaluation_task(request_data: StopEvaluationRequest):
    """
    🛑 Stop evaluation task
    
    Same logic as your original
    """
    try:
        process_id = request_data.process_id
        org_id = request_data.orgId
        
        # Update status to stopped
        status_repo = StatusRepository()
        
        status_document = await status_repo.get_status_document_by_process_id(process_id)
        if status_document:
            status_document["overall_status"] = "Stopped"
            await status_repo.update_status_record(status_document)
        
        # Update in-memory status if exists
        if process_id in EvaluationHandler.task_statuses:
            EvaluationHandler.task_statuses[process_id]["overall_status"] = "Stopped"
        
        return {
            "status_code": 200,
            "message": f"Evaluation task {process_id} has been stopped"
        }
        
    except Exception as e:
        logger.error("💥 Error stopping evaluation task", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping task: {str(e)}"
        )
