"""
gRPC Client Helper for Easy Service Communication
"""
import grpc
from typing import List, Dict, Any, Optional
import asyncio
import logging

# Import generated gRPC code
from . import deepeval_pb2
from . import deepeval_pb2_grpc
from . import common_pb2

logger = logging.getLogger(__name__)


class DeepEvalGRPCClient:
    """
    🎯 Main gRPC Client for Evaluator → DeepEval communication
    
    This is the PRIMARY client used by Evaluator service to call DeepEval service
    """
    
    def __init__(self, server_address: str = "deepeval:50051"):
        self.server_address = server_address
        self.channel = None
        self.stub = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.channel = grpc.aio.insecure_channel(self.server_address)
        self.stub = deepeval_pb2_grpc.DeepEvalServiceStub(self.channel)
        
        # Wait for channel to be ready
        try:
            await grpc.aio.channel_ready_future(self.channel)
            logger.info(f"✅ Connected to DeepEval service at {self.server_address}")
        except grpc.RpcError as e:
            logger.error(f"❌ Failed to connect to DeepEval service: {e}")
            raise
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.channel:
            await self.channel.close()
            logger.info("🔌 Disconnected from DeepEval service")
    
    async def calculate_batch_metrics(
        self,
        evaluation_data: List[Dict[str, Any]],
        metrics: List[str],
        process_id: str,
        user_id: str,
        global_config: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        🔥 PRIMARY METHOD: Calculate metrics for batch of evaluation data
        
        This method is called by Evaluator service to get metric scores
        
        Args:
            evaluation_data: List of evaluation items (questions, answers, context)
            metrics: List of metric names to calculate
            process_id: Evaluation process identifier
            user_id: User identifier
            global_config: Optional global configuration
            
        Returns:
            Dict with success status and results
        """
        try:
            # Convert evaluation data to gRPC format
            batch_items = []
            for i, item in enumerate(evaluation_data):
                evaluation_item = common_pb2.EvaluationItem(
                    question=item.get('question', ''),
                    answer=item.get('model_response', '') or item.get('answer', ''),
                    context=item.get('context', ''),
                    expected_answer=item.get('expected_answer', ''),
                    reference_output=item.get('reference_output', ''),
                    metadata=item.get('metadata', {})
                )
                
                batch_items.append(common_pb2.BatchItem(
                    item_id=str(i),
                    evaluation_data=evaluation_item
                ))
            
            # Create gRPC request
            request = deepeval_pb2.BatchMetricsRequest(
                evaluation_items=batch_items,
                metrics=metrics,
                process_id=process_id,
                user_id=user_id,
                global_config=global_config or {}
            )
            
            logger.info(f"📤 Sending batch metrics request: {len(batch_items)} items, metrics: {metrics}")
            
            # Call DeepEval service
            response = await self.stub.CalculateBatchMetrics(request)
            
            if not response.success:
                raise Exception(f"DeepEval service error: {response.error_message}")
            
            # Convert response to Python dict
            results = []
            for result in response.results:
                results.append({
                    "item_id": result.item_id,
                    "question": result.question,
                    "metric_scores": dict(result.metric_scores),
                    "success": result.success,
                    "error_message": result.error_message
                })
            
            logger.info(f"📥 Received batch metrics response: {response.successful_count} successful, {response.failed_count} failed")
            
            return {
                "success": True,
                "results": results,
                "total_processed": response.total_processed,
                "successful_count": response.successful_count,
                "failed_count": response.failed_count,
                "execution_time_ms": response.total_execution_time_ms,
                "summary_stats": dict(response.summary_stats)
            }
            
        except grpc.RpcError as e:
            logger.error(f"❌ gRPC error: {e.code()}: {e.details()}")
            raise Exception(f"Failed to communicate with DeepEval service: {e.details()}")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise
    
    async def get_available_metrics(self, category: str = "all") -> Dict[str, Any]:
        """Get available metrics from DeepEval service"""
        try:
            request = deepeval_pb2.GetMetricsRequest(category=category)
            response = await self.stub.GetAvailableMetrics(request)
            
            return {
                "metrics_by_category": dict(response.metrics_by_category),
                "all_metrics": list(response.all_metrics)
            }
        except grpc.RpcError as e:
            logger.error(f"❌ Failed to get available metrics: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if DeepEval service is healthy"""
        try:
            request = common_pb2.HealthCheckRequest(service="deepeval")
            response = await self.stub.HealthCheck(request)
            
            return response.status == common_pb2.HealthCheckResponse.SERVING
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False


# Convenience function for one-off calls
async def calculate_metrics(
    evaluation_data: List[Dict[str, Any]], 
    metrics: List[str],
    process_id: str,
    user_id: str,
    server_address: str = "deepeval:50051"
) -> Dict[str, Any]:
    """
    Convenience function for calculating metrics without context manager
    """
    async with DeepEvalGRPCClient(server_address) as client:
        return await client.calculate_batch_metrics(
            evaluation_data=evaluation_data,
            metrics=metrics, 
            process_id=process_id,
            user_id=user_id
        )
