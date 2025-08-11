# Start Evaluator Service - Minimal Version for Testing
Write-Host "⚙️ Starting Evaluator Service (Minimal Test Version)..." -ForegroundColor Green

try {
    # Install essential database dependencies first
    Write-Host "📦 Installing database dependencies..." -ForegroundColor Yellow
    python -m pip install motor pymongo --quiet
    
    # Navigate to evaluator directory
    Push-Location "microservices\evaluator\src"
    
    # Set environment variables for testing
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
     = "mongodb://localhost:27017/evaluation_db"  # Local MongoDB for testing
     = "localhost:50051"
     = "INFO"
    
    Write-Host "📍 Directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray
    Write-Host "🌍 Environment configured for testing" -ForegroundColor Gray
    
    # Check if main.py exists
    if (!(Test-Path "main.py")) {
        Write-Host "❌ main.py not found in current directory" -ForegroundColor Red
        Get-ChildItem | Format-Table Name
        exit 1
    }
    
    Write-Host "🚀 Starting Evaluator FastAPI server..." -ForegroundColor Yellow
    Write-Host "🌐 Will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "🏥 Health check at: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    
    # Start the service
    python main.py
    
} catch {
    Write-Host "❌ Error starting Evaluator service: " -ForegroundColor Red
    Write-Host "💡 Possible solutions:" -ForegroundColor Yellow
    Write-Host "  - Check if you're in the right directory" -ForegroundColor White
    Write-Host "  - Install missing dependencies: python -m pip install motor pymongo" -ForegroundColor White
    Write-Host "  - Try running python main.py directly from microservices\evaluator\src" -ForegroundColor White
} finally {
    Pop-Location
}
