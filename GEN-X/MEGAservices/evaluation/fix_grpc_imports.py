"""
Import Fix Script - Updates gRPC imports in service files
This script updates the import statements in service files to use the copied gRPC code
"""
import os
import re
from pathlib import Path

def fix_grpc_imports_in_file(file_path, service_name):
    """Fix gRPC imports in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Fix imports for gRPC generated code
        # Replace: from grpc.generated.python import
        # With:    from grpc.generated.python import
        
        # The imports should already be correct, but let's make sure
        patterns_to_fix = [
            (r'from grpc\.generated\.python import', 'from grpc.generated.python import'),
            (r'import grpc\.generated\.python', 'import grpc.generated.python'),
        ]
        
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ Fixed imports in {file_path}")
            return True
        else:
            print(f"📝 No import fixes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing imports in {file_path}: {e}")
        return False

def fix_service_imports(service_path, service_name):
    """Fix imports in all Python files in a service"""
    print(f"🔧 Fixing imports in {service_name} service...")
    
    fixed_count = 0
    
    # Find all Python files in the service
    for root, dirs, files in os.walk(service_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__pycache__'):
                file_path = os.path.join(root, file)
                if fix_grpc_imports_in_file(file_path, service_name):
                    fixed_count += 1
    
    print(f"✅ Fixed imports in {fixed_count} files for {service_name}")
    return fixed_count

if __name__ == "__main__":
    print("🔧 Starting gRPC import fix...")
    
    # Fix imports in DeepEval service
    deepeval_path = "microservices/deepeval/src"
    if os.path.exists(deepeval_path):
        fix_service_imports(deepeval_path, "DeepEval")
    else:
        print(f"⚠️ DeepEval service path not found: {deepeval_path}")
    
    # Fix imports in Evaluator service  
    evaluator_path = "microservices/evaluator/src"
    if os.path.exists(evaluator_path):
        fix_service_imports(evaluator_path, "Evaluator")
    else:
        print(f"⚠️ Evaluator service path not found: {evaluator_path}")
    
    print("🎉 Import fix complete!")
