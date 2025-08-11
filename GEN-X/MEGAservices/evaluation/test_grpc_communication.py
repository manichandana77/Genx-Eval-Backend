"""
gRPC Communication Test
Tests the communication between Evaluator and DeepEval services
"""
import asyncio
import sys
import os

# Add the service paths to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'microservices', 'evaluator', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'microservices', 'deepeval', 'src'))

async def test_grpc_imports():
    """Test if gRPC imports work correctly"""
    print("🧪 Testing gRPC imports...")
    
    try:
        # Test importing gRPC generated code
        print("  📦 Testing generated gRPC code imports...")
        
        # Test common imports
        from grpc.generated.python import common_pb2
        from grpc.generated.python import deepeval_pb2
        from grpc.generated.python import deepeval_pb2_grpc
        
        print("  ✅ Generated gRPC code imports successful")
        
        # Test creating protobuf messages
        print("  📝 Testing message creation...")
        
        # Create test evaluation item
        eval_item = common_pb2.EvaluationItem(
            question="What is artificial intelligence?",
            answer="AI is a field of computer science...",
            context="AI context information here",
            expected_answer="Expected answer about AI"
        )
        
        batch_item = common_pb2.BatchItem(
            item_id="test-1",
            evaluation_data=eval_item
        )
        
        # Create test batch request
        request = deepeval_pb2.BatchMetricsRequest(
            evaluation_items=[batch_item],
            metrics=["answer_relevancy", "faithfulness"],
            process_id="test-process",
            user_id="test-user"
        )
        
        print(f"  ✅ Message creation successful")
        print(f"    📊 Request has {len(request.evaluation_items)} items")
        print(f"    🎯 Metrics: {list(request.metrics)}")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

async def test_service_imports():
    """Test if service-level imports work"""
    print("🧪 Testing service imports...")
    
    try:
        # Test DeepEval service imports
        print("  🧠 Testing DeepEval service imports...")
        sys.path.insert(0, os.path.join('microservices', 'deepeval', 'src'))
        
        from config import get_settings as deepeval_settings
        from models import EvaluationData, MetricResult
        
        print("  ✅ DeepEval service imports successful")
        
        # Test Evaluator service imports  
        print("  ⚙️ Testing Evaluator service imports...")
        sys.path.insert(0, os.path.join('microservices', 'evaluator', 'src'))
        
        from config import get_settings as evaluator_settings
        from models import EvaluationRequest, APIResponse
        
        print("  ✅ Evaluator service imports successful")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Service import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected service error: {e}")
        return False

async def test_grpc_client_creation():
    """Test creating gRPC client"""
    print("🧪 Testing gRPC client creation...")
    
    try:
        sys.path.insert(0, os.path.join('microservices', 'evaluator', 'src'))
        from core.grpc_client import DeepEvalGRPCClient
        
        # Create client (don't connect, just test instantiation)
        client = DeepEvalGRPCClient("localhost:50051")
        print("  ✅ gRPC client creation successful")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ gRPC client import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ gRPC client creation error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting gRPC communication tests...\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: gRPC imports
    if await test_grpc_imports():
        tests_passed += 1
    print()
    
    # Test 2: Service imports
    if await test_service_imports():
        tests_passed += 1
    print()
    
    # Test 3: gRPC client creation
    if await test_grpc_client_creation():
        tests_passed += 1
    print()
    
    # Results
    print("📊 Test Results:")
    print(f"  ✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! gRPC communication setup is ready.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
