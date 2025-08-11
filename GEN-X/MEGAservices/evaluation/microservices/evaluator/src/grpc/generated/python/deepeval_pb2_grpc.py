
# Mock gRPC service stubs
class DeepEvalServiceStub:
    def __init__(self, channel):
        self.channel = channel
    
    async def CalculateBatchMetrics(self, request):
        # Mock response
        import random
        results = []
        for i, item in enumerate(request.evaluation_items):
            metric_scores = {}
            for metric in request.metrics:
                score = round(random.uniform(0.6, 0.95), 3)
                metric_scores[metric] = score
            
            from . import deepeval_pb2
            result = type('BatchItemResult', (), {
                'item_id': str(i),
                'question': getattr(item.evaluation_data, 'question', f'Question {i}'),
                'metric_scores': metric_scores,
                'success': True,
                'error_message': ''
            })()
            results.append(result)
        
        response = deepeval_pb2.BatchMetricsResponse(
            success=True,
            results=results,
            total_processed=len(results),
            successful_count=len(results),
            failed_count=0,
            total_execution_time_ms=random.randint(1000, 3000),
            summary_stats={'mock_mode': True}
        )
        return response
    
    async def GetAvailableMetrics(self, request):
        from . import deepeval_pb2
        return deepeval_pb2.AvailableMetricsResponse(
            metrics_by_category={'rag': ['answer_relevancy', 'faithfulness']},
            all_metrics=['answer_relevancy', 'faithfulness', 'bias']
        )
    
    async def HealthCheck(self, request):
        from . import common_pb2
        return common_pb2.HealthCheckResponse(
            status=common_pb2.HealthCheckResponse.SERVING,
            message="Mock gRPC service healthy"
        )
