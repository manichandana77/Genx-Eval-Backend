# Start Evaluator Service - Fixed Version  
Write-Host "⚙️ Starting Evaluator Service (Fixed)..." -ForegroundColor Green

try {
    # Navigate to Evaluator directory
    Push-Location "microservices\evaluator\src"
    
    # Set Python path
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
    
    Write-Host "📍 Directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray
    Write-Host "🐍 Python path configured" -ForegroundColor Gray
    
    # Install dependencies if needed
    Write-Host "📦 Ensuring dependencies are installed..." -ForegroundColor Gray
    pip install -q pydantic-settings fastapi uvicorn structlog motor pymongo
    
    # Start the service
    Write-Host "🚀 Starting Evaluator FastAPI server..." -ForegroundColor Yellow
    python main.py
    
} catch {
    Write-Host "❌ Error starting Evaluator service: " -ForegroundColor Red
    Write-Host "💡 Try installing dependencies manually: pip install pydantic-settings fastapi uvicorn" -ForegroundColor Yellow
} finally {
    Pop-Location
}
