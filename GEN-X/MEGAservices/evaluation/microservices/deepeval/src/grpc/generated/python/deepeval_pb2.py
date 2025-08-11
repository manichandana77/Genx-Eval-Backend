
# Mock protobuf messages
class BatchMetricsRequest:
    def __init__(self, **kwargs):
        self.evaluation_items = kwargs.get('evaluation_items', [])
        self.metrics = kwargs.get('metrics', [])
        self.process_id = kwargs.get('process_id', '')
        self.user_id = kwargs.get('user_id', '')
        self.global_config = kwargs.get('global_config', {})

class BatchMetricsResponse:
    def __init__(self, **kwargs):
        self.success = kwargs.get('success', True)
        self.results = kwargs.get('results', [])
        self.total_processed = kwargs.get('total_processed', 0)
        self.successful_count = kwargs.get('successful_count', 0)
        self.failed_count = kwargs.get('failed_count', 0)
        self.total_execution_time_ms = kwargs.get('total_execution_time_ms', 0)
        self.summary_stats = kwargs.get('summary_stats', {})
        self.error_message = kwargs.get('error_message', '')

class GetMetricsRequest:
    def __init__(self, **kwargs):
        self.category = kwargs.get('category', 'all')

class AvailableMetricsResponse:
    def __init__(self, **kwargs):
        self.metrics_by_category = kwargs.get('metrics_by_category', {})
        self.all_metrics = kwargs.get('all_metrics', [])
