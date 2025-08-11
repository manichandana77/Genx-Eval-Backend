"""
Generated gRPC code for Evaluation Services
Auto-generated from proto files - DO NOT MODIFY MANUALLY
"""

# Import all generated protobuf messages
try:
    from . import common_pb2
    from . import common_pb2_grpc
    from . import deepeval_pb2  
    from . import deepeval_pb2_grpc
    from . import rag_metrics_pb2
    from . import rag_metrics_pb2_grpc
    from . import safety_metrics_pb2
    from . import safety_metrics_pb2_grpc
    from . import task_metrics_pb2
    from . import task_metrics_pb2_grpc
    from . import custom_metrics_pb2
    from . import custom_metrics_pb2_grpc
except ImportError as e:
    print(f"Warning: Could not import all gRPC modules: {e}")

# Export main service stubs for easy import
__all__ = [
    # Common types
    'common_pb2',
    'common_pb2_grpc',
    
    # Main DeepEval service (PRIMARY SERVICE)
    'deepeval_pb2', 
    'deepeval_pb2_grpc',
    
    # Specific metric services
    'rag_metrics_pb2',
    'rag_metrics_pb2_grpc', 
    'safety_metrics_pb2',
    'safety_metrics_pb2_grpc',
    'task_metrics_pb2',
    'task_metrics_pb2_grpc',
    'custom_metrics_pb2',
    'custom_metrics_pb2_grpc',
]

# Version info
__version__ = '1.0.0'
__author__ = 'GEN-X Evaluation Team'
