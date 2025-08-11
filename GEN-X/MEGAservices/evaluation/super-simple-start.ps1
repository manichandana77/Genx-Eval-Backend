# Super Simple Start - Just the basics
Write-Host "🚀 Starting Evaluator Service (Super Simple Version)" -ForegroundColor Green

# Check current directory
Write-Host "📍 Current directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray

# Install basic dependencies
Write-Host "📦 Installing basic dependencies..." -ForegroundColor Yellow
python -m pip install fastapi uvicorn pydantic pydantic-settings structlog python-dotenv

# Navigate to service directory
Write-Host "📂 Navigating to service directory..." -ForegroundColor Yellow
cd microservices\evaluator\src

# Check if main.py exists
if (Test-Path "main.py") {
    Write-Host "✅ Found main.py - starting service..." -ForegroundColor Green
    
    # Set basic environment
     = (Get-Location).Path
     = "INFO"
    
    Write-Host "🌐 Service will start on: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API docs will be at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    
    # Start the service
    python main.py
    
} else {
    Write-Host "❌ main.py not found!" -ForegroundColor Red
    Write-Host "📁 Current directory contents:" -ForegroundColor Yellow
    dir
    Write-Host ""
    Write-Host "💡 Make sure you're in the evaluation directory and have run all setup steps." -ForegroundColor White
}
