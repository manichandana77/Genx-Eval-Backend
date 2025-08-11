
# Mock common protobuf messages
class EvaluationItem:
    def __init__(self, **kwargs):
        self.question = kwargs.get('question', '')
        self.answer = kwargs.get('answer', '')
        self.context = kwargs.get('context', '')
        self.expected_answer = kwargs.get('expected_answer', '')
        self.reference_output = kwargs.get('reference_output', '')
        self.metadata = kwargs.get('metadata', {})

class BatchItem:
    def __init__(self, **kwargs):
        self.item_id = kwargs.get('item_id', '')
        self.evaluation_data = kwargs.get('evaluation_data', EvaluationItem())

class HealthCheckRequest:
    def __init__(self, **kwargs):
        self.service = kwargs.get('service', 'deepeval')

class HealthCheckResponse:
    SERVING = "SERVING"
    NOT_SERVING = "NOT_SERVING"
    
    def __init__(self, **kwargs):
        self.status = kwargs.get('status', self.SERVING)
        self.message = kwargs.get('message', 'OK')
