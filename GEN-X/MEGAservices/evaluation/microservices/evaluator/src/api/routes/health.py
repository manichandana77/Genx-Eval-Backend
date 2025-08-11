"""
Health Check Routes
"""
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
import structlog

from models import HealthStatus, ServiceInfo
from database.connection import db_manager, get_database
from core.grpc_client_fixed import test_deepeval_connection
from config import get_settings

logger = structlog.get_logger()
router = APIRouter()

# Track service start time
_service_start_time = time.time()


@router.get("/", response_model=HealthStatus)
async def health_check():
    """Main health check endpoint"""
    try:
        settings = get_settings()
        
        # Check database
        db_healthy = await db_manager.health_check()
        
        # Check DeepEval service
        deepeval_healthy = await test_deepeval_connection()
        
        # Calculate uptime
        uptime = time.time() - _service_start_time
        
        # Overall status
        overall_healthy = db_healthy and deepeval_healthy
        status = "healthy" if overall_healthy else "unhealthy"
        
        return HealthStatus(
            status=status,
            version=settings.service_version,
            uptime_seconds=uptime,
            services={
                "database": db_healthy,
                "deepeval_service": deepeval_healthy
            }
        )
        
    except Exception as e:
        logger.error("💥 Health check failed", error=str(e))
        return HealthStatus(
            status="unhealthy",
            services={"error": False}
        )


@router.get("/detailed", response_model=Dict[str, Any])
async def detailed_health_check():
    """Detailed health check with more information"""
    try:
        settings = get_settings()
        uptime = time.time() - _service_start_time
        
        # Database health
        db_healthy = await db_manager.health_check()
        
        # DeepEval service health
        deepeval_healthy = await test_deepeval_connection()
        
        return {
            "service": "evaluator",
            "version": settings.service_version,
            "status": "healthy" if (db_healthy and deepeval_healthy) else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime,
            "environment": settings.environment,
            "services": {
                "database": {
                    "healthy": db_healthy,
                    "uri": settings.mongo_uri.split("@")[-1],  # Hide credentials
                    "database": settings.db_name
                },
                "deepeval_service": {
                    "healthy": deepeval_healthy,
                    "host": settings.deepeval_grpc_host
                }
            },
            "configuration": {
                "max_concurrent_evaluations": settings.max_concurrent_evaluations,
                "default_metrics": settings.default_metrics_list,
                "grpc_timeout": settings.grpc_timeout_seconds
            }
        }
        
    except Exception as e:
        logger.error("💥 Detailed health check failed", error=str(e))
        return {
            "service": "evaluator",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/info", response_model=ServiceInfo)
async def service_info():
    """Get service information"""
    settings = get_settings()
    return ServiceInfo(
        service="evaluator",
        version=settings.service_version,
        status="running"
    )
