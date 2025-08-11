"""
Evaluator Service - Main FastAPI Server
🎯 This service orchestrates evaluations and calls DeepEval service for metrics
"""
import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.routes import evaluation, health
from database.connection import db_manager
from config import get_settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - handle startup and shutdown"""
    settings = get_settings()
    
    # Startup
    logger.info("🚀 Starting Evaluator Service", 
                version=settings.service_version,
                environment=settings.environment)
    
    try:
        # Initialize database connection
        await db_manager.connect()
        logger.info("📊 Database connection established")
        
        # Test gRPC connection to DeepEval service
        from core.grpc_client_fixed import test_deepeval_connection
        if await test_deepeval_connection():
            logger.info("🧠 DeepEval service connection verified")
        else:
            logger.warning("⚠️ DeepEval service not accessible - will retry on demand")
        
        yield
        
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Evaluator Service")
        await db_manager.disconnect()
        logger.info("📊 Database connection closed")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Evaluation Backend - Evaluator Service",
        version=settings.service_version,
        description="Main orchestration service for ML model evaluations",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["Health"])
    app.include_router(evaluation.router, prefix="/api/v1/evaluations", tags=["Evaluations"])
    
    return app


# Create app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint"""
    settings = get_settings()
    return {
        "service": "evaluator",
        "version": settings.service_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    settings = get_settings()
    
    logger.info("🌟 Starting Evaluator Service",
                host="0.0.0.0",
                port=settings.http_port,
                environment=settings.environment)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.http_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
        access_log=True
    )
