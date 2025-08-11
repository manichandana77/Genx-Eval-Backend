"""
Test script to verify gRPC code generation
Run this to test if the generated gRPC code works properly
"""

def test_imports():
    """Test if all generated modules can be imported"""
    print("🧪 Testing gRPC imports...")
    
    try:
        # Test importing generated modules
        import common_pb2
        import deepeval_pb2
        import rag_metrics_pb2
        import safety_metrics_pb2
        import task_metrics_pb2
        import custom_metrics_pb2
        
        print("✅ All pb2 modules imported successfully")
        
        # Test importing gRPC service stubs
        import deepeval_pb2_grpc
        import rag_metrics_pb2_grpc
        import safety_metrics_pb2_grpc
        import task_metrics_pb2_grpc
        import custom_metrics_pb2_grpc
        
        print("✅ All gRPC service stubs imported successfully")
        
        # Test client helper
        from client_helper import DeepEvalGRPCClient
        print("✅ Client helper imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_message_creation():
    """Test creating protobuf messages"""
    print("🧪 Testing message creation...")
    
    try:
        import common_pb2
        import deepeval_pb2
        
        # Test creating common messages
        eval_item = common_pb2.EvaluationItem(
            question="What is AI?",
            answer="Artificial Intelligence is...",
            context="AI context here",
            expected_answer="Expected answer"
        )
        
        batch_item = common_pb2.BatchItem(
            item_id="test-1",
            evaluation_data=eval_item
        )
        
        # Test creating request message
        request = deepeval_pb2.BatchMetricsRequest(
            evaluation_items=[batch_item],
            metrics=["answer_relevancy", "faithfulness"],
            process_id="test-process",
            user_id="test-user"
        )
        
        print("✅ Message creation successful")
        print(f"   📄 Request has {len(request.evaluation_items)} items")
        print(f"   📊 Metrics: {list(request.metrics)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Message creation error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing generated gRPC code...\n")
    
    import_success = test_imports()
    message_success = test_message_creation()
    
    if import_success and message_success:
        print("\n🎉 All tests passed! gRPC code generation successful!")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
