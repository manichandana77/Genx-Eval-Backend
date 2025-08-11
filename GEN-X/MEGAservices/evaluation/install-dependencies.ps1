# Install All Required Dependencies
Write-Host "📦 Installing all required dependencies..." -ForegroundColor Green

 = @(
    # Core Python packages
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
    
    # gRPC packages
    "grpcio==1.60.0", 
    "grpcio-tools==1.60.0",
    "grpcio-health-checking==1.60.0",
    "protobuf==4.25.0",
    
    # FastAPI and web server
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "python-multipart==0.0.6",
    
    # Database
    "motor==3.3.2",
    "pymongo==4.6.0",
    
    # DeepEval and AI
    "deepeval==0.21.73",
    "openai==1.3.9",
    
    # Logging and utilities
    "structlog==23.2.0",
    "PyYAML==6.0.1",
    "python-dateutil==2.8.2",
    "python-dotenv==1.0.0",
    "aiofiles==23.2.1",
    
    # Data processing
    "numpy==1.25.2",
    "pandas==2.1.4",
    
    # HTTP clients
    "httpx==0.25.2",
    "requests==2.31.0"
)

 = 0
 = 0

foreach (openai==1.3.9 in ) {
    Write-Host "  📥 Installing openai==1.3.9..." -ForegroundColor Gray
    try {
        pip install openai==1.3.9 --quiet --no-warn-script-location
        ++
        Write-Host "    ✅ openai==1.3.9" -ForegroundColor Green
    } catch {
        ++
        Write-Host "    ❌ openai==1.3.9 failed" -ForegroundColor Red
    }
}

Write-Host "
📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Installed: " -ForegroundColor Green
Write-Host "  ❌ Failed: " -ForegroundColor Red

if ( -eq 0) {
    Write-Host "
🎉 All dependencies installed successfully!" -ForegroundColor Green
    Write-Host "🚀 Ready to start services!" -ForegroundColor White
} else {
    Write-Host "
⚠️ Some dependencies failed to install." -ForegroundColor Yellow
    Write-Host "💡 Try running this script as Administrator or check your Python/pip setup." -ForegroundColor White
}
