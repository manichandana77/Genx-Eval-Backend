"""
Quick Verification Script
Verifies that the gRPC setup is working correctly
"""
import os
import sys

def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - File not found: {file_path}")
        return False

def check_grpc_setup():
    """Check if gRPC setup is complete"""
    print("🔍 Verifying gRPC setup...\n")
    
    checks_passed = 0
    total_checks = 0
    
    # Check DeepEval service files
    print("🧠 DeepEval Service:")
    deepeval_files = [
        ("microservices/deepeval/src/main.py", "Main server file"),
        ("microservices/deepeval/src/grpc/generated/python/__init__.py", "gRPC generated code"),
        ("microservices/deepeval/src/grpc/generated/python/deepeval_pb2.py", "Protobuf messages"),
        ("microservices/deepeval/src/grpc/generated/python/deepeval_pb2_grpc.py", "gRPC service stubs"),
        ("microservices/deepeval/src/config.py", "Configuration"),
        ("microservices/deepeval/src/models.py", "Data models")
    ]
    
    for file_path, description in deepeval_files:
        if check_file_exists(file_path, f"  {description}"):
            checks_passed += 1
        total_checks += 1
    
    print()
    
    # Check Evaluator service files
    print("⚙️ Evaluator Service:")
    evaluator_files = [
        ("microservices/evaluator/src/main.py", "Main server file"),
        ("microservices/evaluator/src/grpc/generated/python/__init__.py", "gRPC generated code"),
        ("microservices/evaluator/src/grpc/generated/python/deepeval_pb2.py", "Protobuf messages"),
        ("microservices/evaluator/src/grpc/generated/python/deepeval_pb2_grpc.py", "gRPC service stubs"),
        ("microservices/evaluator/src/core/grpc_client.py", "gRPC client"),
        ("microservices/evaluator/src/core/evaluation_handler.py", "Evaluation handler")
    ]
    
    for file_path, description in evaluator_files:
        if check_file_exists(file_path, f"  {description}"):
            checks_passed += 1
        total_checks += 1
    
    print()
    
    # Check start scripts
    print("🚀 Start Scripts:")
    start_scripts = [
        ("start-deepeval.ps1", "DeepEval start script"),
        ("start-evaluator.ps1", "Evaluator start script"),
        ("start-both-services.ps1", "Combined start script")
    ]
    
    for file_path, description in start_scripts:
        if check_file_exists(file_path, f"  {description}"):
            checks_passed += 1
        total_checks += 1
    
    print()
    
    # Results
    print("📊 Verification Results:")
    print(f"  ✅ Files present: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("🎉 All verification checks passed!")
        print("\n🚀 Ready to start services:")
        print("  1. Run: .\\start-both-services.ps1")
        print("  2. Access: http://localhost:8000")
        print("  3. Test: http://localhost:8000/health")
        return True
    else:
        print("❌ Some files are missing. Check the setup steps.")
        return False

if __name__ == "__main__":
    success = check_grpc_setup()
    sys.exit(0 if success else 1)
