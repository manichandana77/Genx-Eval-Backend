"""
DeepEval Service - Main gRPC Server - FIXED
"""
import asyncio
import logging
import signal
import sys
import os
from concurrent import futures



# FIX THE IMPORT PATHS FIRST
current_dir = os.path.dirname(os.path.abspath(__file__))
grpc_path = os.path.join(current_dir, 'grpc', 'generated', 'python')
sys.path.insert(0, grpc_path)
sys.path.insert(0, current_dir)

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc
import structlog

# Now import our gRPC code
import deepeval_pb2_grpc
import common_pb2
import deepeval_pb2

# Import our modules
from config import get_settings
from core.metric_factory import MetricFactory

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# Simple DeepEval Service Implementation
class DeepEvalGRPCServer(deepeval_pb2_grpc.DeepEvalServiceServicer):
    def __init__(self):
        self.settings = get_settings()
        self.metric_factory = MetricFactory()
        logger.info("🧠 DeepEval gRPC Server initialized")
    
    async def CalculateBatchMetrics(self, request, context):
        """Main method for batch metrics calculation"""
        import random
        
        logger.info("📤 Received batch metrics request", 
                   process_id=request.process_id,
                   items_count=len(request.evaluation_items))
        
        results = []
        for i, item in enumerate(request.evaluation_items):
            # Create mock scores for now
            scores = {}
            for metric in request.metrics:
                if metric in ['bias', 'toxicity', 'hallucination']:
                    scores[metric] = round(random.uniform(0.0, 0.3), 3)
                else:
                    scores[metric] = round(random.uniform(0.7, 0.95), 3)
            
            result = common_pb2.BatchItemResult(
                item_id=str(i),
                question=item.evaluation_data.question[:50] + "...",
                metric_scores=scores,
                success=True
            )
            results.append(result)
        
        response = deepeval_pb2.BatchMetricsResponse(
            results=results,
            success=True,
            total_processed=len(results),
            successful_count=len(results),
            failed_count=0,
            total_execution_time_ms=random.randint(1000, 3000)
        )
        
        logger.info("📥 Batch metrics response created", count=len(results))
        return response


async def serve():
    """Start the gRPC server"""
    settings = get_settings()
    
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add our service
    deepeval_service = DeepEvalGRPCServer()
    deepeval_pb2_grpc.add_DeepEvalServiceServicer_to_server(deepeval_service, server)
    
    # Add health check
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    listen_addr = f'[::]:{settings.grpc_port}'
    server.add_insecure_port(listen_addr)
    
    logger.info("🚀 Starting DeepEval gRPC server", address=listen_addr)
    
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down gRPC server")
        await server.stop(0)


if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except Exception as e:
        logger.error("💥 Server failed to start", error=str(e))
        print(f"💥 Server failed to start: {e}")
        sys.exit(1)