# PowerShell script to generate Python gRPC code

Write-Host "🔧 Generating Python gRPC code..." -ForegroundColor Yellow

# Ensure we're in the scripts directory
Push-Location

try {
    # Navigate to proto directory for generation
    Set-Location "..\proto"
    
    # Create output directory
    New-Item -ItemType Directory -Force -Path "..\generated\python"
    
    # Generate Python code for all proto files
    Write-Host "Generating proto files..." -ForegroundColor Gray
    
    # Generate each proto file individually
     = Get-ChildItem -Name "*.proto"
    foreach ( in ) {
        Write-Host "  Processing ..." -ForegroundColor Gray
        python -m grpc_tools.protoc --proto_path=. --python_out="..\generated\python" --grpc_python_out="..\generated\python" 
    }
    
    Write-Host "✅ Python gRPC code generated successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error generating gRPC code: " -ForegroundColor Red
} finally {
    Pop-Location
}

Write-Host "✅ gRPC generation complete!" -ForegroundColor Green
Write-Host "📁 Generated files are in: grpc/generated/python/" -ForegroundColor Cyan
