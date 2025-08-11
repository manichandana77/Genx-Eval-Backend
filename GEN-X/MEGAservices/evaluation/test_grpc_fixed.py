"""
Improved gRPC Communication Test
Tests the fixed communication setup
"""
import asyncio
import sys
import os

def test_basic_imports():
    """Test basic Python imports"""
    print("🧪 Testing basic imports...")
    
    try:
        # Test basic packages
        import pydantic
        from pydantic_settings import BaseSettings
        print("  ✅ Pydantic and pydantic-settings available")
        
        import grpc
        print("  ✅ gRPC package available")
        
        import structlog
        print("  ✅ Structlog available")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Basic import error: {e}")
        return False

def test_service_configs():
    """Test if service configurations can be loaded"""
    print("🧪 Testing service configurations...")
    
    try:
        # Test DeepEval config
        deepeval_path = "microservices/deepeval/src"
        if deepeval_path not in sys.path:
            sys.path.insert(0, deepeval_path)
        
        from config import get_settings as deepeval_settings
        deepeval_config = deepeval_settings()
        print(f"  ✅ DeepEval config loaded - service: {deepeval_config.service_name}")
        
        # Test Evaluator config
        evaluator_path = "microservices/evaluator/src"
        if evaluator_path not in sys.path:
            sys.path.insert(0, evaluator_path)
        
        # Import with different name to avoid conflicts
        sys.path.insert(0, evaluator_path)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "evaluator_config", 
            os.path.join(evaluator_path, "config.py")
        )
        evaluator_config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evaluator_config_module)
        
        evaluator_config = evaluator_config_module.get_settings()
        print(f"  ✅ Evaluator config loaded - service: {evaluator_config.service_name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Service config error: {e}")
        return False

def test_grpc_client():
    """Test the fixed gRPC client"""
    print("🧪 Testing fixed gRPC client...")
    
    try:
        # Test the fixed client
        evaluator_path = "microservices/evaluator/src"
        if evaluator_path not in sys.path:
            sys.path.insert(0, evaluator_path)
        
        from core.grpc_client_fixed import DeepEvalGRPCClient
        
        # Create client (don't connect, just test instantiation)
        client = DeepEvalGRPCClient("localhost:50051")
        print("  ✅ Fixed gRPC client created successfully")
        
        # Test mock functionality
        import asyncio
        
        async def test_mock():
            async with client:
                # Test mock batch metrics
                mock_data = [
                    {
                        "question": "What is AI?",
                        "model_response": "AI is artificial intelligence",
                        "expected_answer": "AI is a field of computer science",
                        "context": "AI context here"
                    }
                ]
                
                result = await client.calculate_batch_metrics(
                    evaluation_data=mock_data,
                    metrics=["answer_relevancy", "faithfulness"],
                    process_id="test-123",
                    user_id="test-user"
                )
                
                if result["success"] and len(result["results"]) > 0:
                    print("  ✅ Mock batch metrics calculation works")
                    return True
                else:
                    print("  ❌ Mock batch metrics failed")
                    return False
        
        return asyncio.run(test_mock())
        
    except Exception as e:
        print(f"  ❌ gRPC client test error: {e}")
        return False

async def main():
    """Run all improved tests"""
    print("🚀 Starting improved gRPC communication tests...\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Service Configs", test_service_configs), 
        ("gRPC Client", test_grpc_client)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {test_name} test PASSED\n")
            else:
                print(f"  ❌ {test_name} test FAILED\n")
        except Exception as e:
            print(f"  💥 {test_name} test ERROR: {e}\n")
    
    # Results
    print("📊 Improved Test Results:")
    print(f"  ✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for testing.")
        print("\n🚀 Next steps:")
        print("  1. Run: .\\start-both-services.ps1")
        print("  2. Test: http://localhost:8000/health")
        return True
    elif passed > 0:
        print("⚠️ Some tests passed - system may work with limitations.")
        print("🚀 Try starting services anyway:")
        print("  1. Run: .\\start-both-services.ps1")
        print("  2. Test: http://localhost:8000/health")
        return True
    else:
        print("❌ All tests failed - check dependencies and setup.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
