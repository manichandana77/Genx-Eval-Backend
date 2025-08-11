#!/bin/bash
# Generate Python gRPC code from proto files

echo "🔧 Generating Python gRPC code..."

# Create output directory
mkdir -p ../generated/python

# Generate Python code for all proto files
python -m grpc_tools.protoc \
    --proto_path=../proto \
    --python_out=../generated/python \
    --grpc_python_out=../generated/python \
    ../proto/*.proto

echo "✅ Python gRPC code generated successfully!"

# Fix import issues in generated files (common Python gRPC issue)
echo "🔧 Fixing import paths..."
cd ../generated/python
find . -name "*_pb2_grpc.py" -exec sed -i 's/import \([^.]*\)_pb2 as/from . import \1_pb2 as/g' {} \;

echo "✅ Python gRPC generation complete!"
