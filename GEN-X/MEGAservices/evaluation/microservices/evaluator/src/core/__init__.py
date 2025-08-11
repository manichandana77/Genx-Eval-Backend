"""Core package"""

from .evaluation_handler import EvaluationHandler
from .grpc_client import DeepEvalGRPCClient, test_deepeval_connection

__all__ = ["EvaluationHandler", "DeepEvalGRPCClient", "test_deepeval_connection"]
