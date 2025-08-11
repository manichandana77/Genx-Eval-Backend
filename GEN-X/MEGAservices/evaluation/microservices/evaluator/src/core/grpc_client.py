"""
gRPC Client for DeepEval Service Communication
🎯 This client handles all communication from Evaluator → DeepEval
"""
import asyncio
import grpc
from typing import List, Dict, Any, Optional
import structlog

from config import get_settings

logger = structlog.get_logger()

# Import generated gRPC code (will be copied from grpc/generated/python)
try:
    from grpc.generated.python import deepeval_pb2
    from grpc.generated.python import deepeval_pb2_grpc  
    from grpc.generated.python import common_pb2
except ImportError as e:
    logger.warning("⚠️ gRPC generated code not found - will be available after copying", error=str(e))
    # Create dummy classes for development
    class deepeval_pb2:
        class BatchMetricsRequest: pass
        class BatchMetricsResponse: pass
    class deepeval_pb2_grpc:
        class DeepEvalServiceStub: pass
    class common_pb2:
        class EvaluationItem: pass
        class BatchItem: pass


class DeepEvalGRPCClient:
    """
    🔥 MAIN gRPC CLIENT - Handles all Evaluator → DeepEval communication
    """
    
    def __init__(self, server_address: Optional[str] = None):
        settings = get_settings()
        self.server_address = server_address or settings.deepeval_grpc_host
        self.timeout = settings.grpc_timeout_seconds
        self.max_retries = settings.grpc_max_retries
        self.retry_delay = settings.grpc_retry_delay
        
        self.channel = None
        self.stub = None
        
        logger.info("📡 DeepEval gRPC client initialized", server=self.server_address)
    
    async def __aenter__(self):
        """Async context manager entry"""
        try:
            # Create gRPC channel with options for reliability
            channel_options = [
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.max_connection_idle_ms', 300000),
            ]
            
            self.channel = grpc.aio.insecure_channel(self.server_address, options=channel_options)
            self.stub = deepeval_pb2_grpc.DeepEvalServiceStub(self.channel)
            
            # Test connection
            await self._test_connection()
            logger.info("✅ Connected to DeepEval service", server=self.server_address)
            
        except Exception as e:
            logger.error("❌ Failed to connect to DeepEval service", 
                        server=self.server_address, error=str(e))
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
        
        This is the main method called by EvaluationHandler to get metric scores
        
        Args:
            evaluation_data: List of evaluation items with questions, answers, context
            metrics: List of metric names to calculate (e.g., ["answer_relevancy", "faithfulness"])
            process_id: Unique process identifier
            user_id: User identifier
            global_config: Optional global configuration
            
        Returns:
            Dict with success status, results, and statistics
        """
        try:
            logger.info("📤 Sending batch metrics request to DeepEval", 
                       process_id=process_id,
                       items_count=len(evaluation_data),
                       metrics=metrics)
            
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
            
            # Call DeepEval service with retries
            response = await self._call_with_retries(
                self.stub.CalculateBatchMetrics,
                request
            )
            
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
            
            logger.info("📥 Received batch metrics response from DeepEval",
                       process_id=process_id,
                       successful_count=response.successful_count,
                       failed_count=response.failed_count,
                       execution_time_ms=response.total_execution_time_ms)
            
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
            error_msg = f"gRPC communication error: {e.code()}: {e.details()}"
            logger.error("❌ gRPC error calling DeepEval service", 
                        error=error_msg, process_id=process_id)
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to communicate with DeepEval service: {str(e)}"
            logger.error("❌ Unexpected error calling DeepEval service", 
                        error=str(e), process_id=process_id)
            raise Exception(error_msg)
    
    async def get_available_metrics(self, category: str = "all") -> Dict[str, Any]:
        """Get available metrics from DeepEval service"""
        try:
            request = deepeval_pb2.GetMetricsRequest(category=category)
            response = await self._call_with_retries(
                self.stub.GetAvailableMetrics,
                request
            )
            
            return {
                "metrics_by_category": dict(response.metrics_by_category),
                "all_metrics": list(response.all_metrics)
            }
            
        except Exception as e:
            logger.error("❌ Failed to get available metrics", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if DeepEval service is healthy"""
        try:
            request = common_pb2.HealthCheckRequest(service="deepeval")
            response = await self._call_with_retries(
                self.stub.HealthCheck,
                request,
                timeout=10  # Shorter timeout for health checks
            )
            
            is_healthy = response.status == common_pb2.HealthCheckResponse.SERVING
            logger.info("🏥 DeepEval health check", healthy=is_healthy, message=response.message)
            return is_healthy
            
        except Exception as e:
            logger.error("❌ DeepEval health check failed", error=str(e))
            return False
    
    async def _test_connection(self):
        """Test gRPC connection"""
        try:
            # Try to call health check to test connection
            await grpc.aio.channel_ready_future(self.channel, timeout=5)
        except asyncio.TimeoutError:
            raise Exception("Connection timeout to DeepEval service")
        except Exception as e:
            raise Exception(f"Connection failed to DeepEval service: {str(e)}")
    
    async def _call_with_retries(self, rpc_method, request, timeout: Optional[int] = None):
        """Call gRPC method with retries"""
        timeout = timeout or self.timeout
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    rpc_method(request),
                    timeout=timeout
                )
                return response
                
            except (grpc.RpcError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:  # Last attempt
                    raise
                
                logger.warning("🔄 gRPC call failed, retrying",
                              attempt=attempt + 1,
                              max_retries=self.max_retries,
                              error=str(e))
                
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        raise Exception("Max retries exceeded")


# Convenience functions for one-off calls
async def calculate_metrics(
    evaluation_data: List[Dict[str, Any]],
    metrics: List[str], 
    process_id: str,
    user_id: str,
    server_address: Optional[str] = None,
    global_config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Convenience function for calculating metrics without context manager
    """
    async with DeepEvalGRPCClient(server_address) as client:
        return await client.calculate_batch_metrics(
            evaluation_data=evaluation_data,
            metrics=metrics,
            process_id=process_id,
            user_id=user_id,
            global_config=global_config
        )


async def test_deepeval_connection(server_address: Optional[str] = None) -> bool:
    """Test connection to DeepEval service"""
    try:
        async with DeepEvalGRPCClient(server_address) as client:
            return await client.health_check()
    except Exception as e:
        logger.error("❌ DeepEval connection test failed", error=str(e))
        return False
