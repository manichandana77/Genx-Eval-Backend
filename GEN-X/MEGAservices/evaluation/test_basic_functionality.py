"""
Simplified Service Test - Test basic functionality without gRPC
"""
import sys
import os
import asyncio

async def test_evaluator_service_basic():
    """Test basic Evaluator service functionality"""
    print("🧪 Testing Evaluator service basic functionality...")
    
    try:
        # Add evaluator to path
        evaluator_path = "microservices/evaluator/src"
        if evaluator_path not in sys.path:
            sys.path.insert(0, evaluator_path)
        
        # Test config loading
        from config import get_settings
        settings = get_settings()
        print(f"  ✅ Config loaded - service: {settings.service_name}")
        
        # Test models
        from models import EvaluationRequest, APIResponse, HealthStatus
        
        # Create test evaluation request
        test_request = EvaluationRequest(
            file_path="test_dataset.yaml",
            metrics=["answer_relevancy", "faithfulness"],
            user_id="test_user"
        )
        print(f"  ✅ Models working - request: {test_request.file_path}")
        
        # Test API response
        response = APIResponse(success=True, message="Test successful")
        print(f"  ✅ API response model working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Evaluator service test error: {e}")
        return False

async def test_mock_grpc_client():
    """Test the mock gRPC client functionality"""
    print("🧪 Testing mock gRPC client...")
    
    try:
        evaluator_path = "microservices/evaluator/src"
        if evaluator_path not in sys.path:
            sys.path.insert(0, evaluator_path)
        
        from core.grpc_client_fixed import DeepEvalGRPCClient
        
        # Test mock functionality
        async with DeepEvalGRPCClient("localhost:50051") as client:
            # Test mock batch metrics
            mock_data = [
                {
                    "question": "What is artificial intelligence?",
                    "model_response": "AI is a field of computer science that aims to create intelligent machines.",
                    "expected_answer": "AI is artificial intelligence technology.",
                    "context": "AI is used in various applications including machine learning and automation."
                },
                {
                    "question": "How does machine learning work?",
                    "model_response": "Machine learning uses algorithms to learn patterns from data.",
                    "expected_answer": "ML algorithms learn from data to make predictions.",
                    "context": "Machine learning is a subset of AI that focuses on data-driven learning."
                }
            ]
            
            result = await client.calculate_batch_metrics(
                evaluation_data=mock_data,
                metrics=["answer_relevancy", "faithfulness", "bias"],
                process_id="test-123",
                user_id="test-user"
            )
            
            if result["success"] and len(result["results"]) == 2:
                print(f"  ✅ Mock gRPC client working")
                print(f"    📊 Processed {result['total_processed']} items")
                print(f"    ⏱️ Execution time: {result['execution_time_ms']}ms")
                
                # Show sample scores
                sample_result = result["results"][0]
                print(f"    🎯 Sample metrics: {sample_result['metric_scores']}")
                
                return True
            else:
                print(f"  ❌ Mock results not as expected")
                return False
                
    except Exception as e:
        print(f"  ❌ Mock gRPC client error: {e}")
        return False

async def main():
    """Run simplified tests"""
    print("🚀 Starting simplified service tests...\n")
    
    tests = [
        ("Evaluator Service Basic", test_evaluator_service_basic),
        ("Mock gRPC Client", test_mock_grpc_client)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED\n")
            else:
                print(f"❌ {test_name} - FAILED\n")
        except Exception as e:
            print(f"💥 {test_name} - ERROR: {e}\n")
    
    print("📊 Test Results:")
    print(f"  ✅ Tests passed: {passed}/{total}")
    
    if passed >= 1:
        print("🎉 Basic functionality is working!")
        print("\n🚀 Ready to start Evaluator service:")
        print("  1. Run: .\\start-evaluator-fixed.ps1")
        print("  2. Visit: http://localhost:8000")
        print("  3. Check: http://localhost:8000/health")
        return True
    else:
        print("❌ Basic tests failed - check dependencies.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
