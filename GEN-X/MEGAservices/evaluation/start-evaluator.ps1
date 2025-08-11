# Start Evaluator Service
Write-Host "⚙️ Starting Evaluator Service..." -ForegroundColor Green

# Navigate to Evaluator service directory
Push-Location "microservices\evaluator\src"

Write-Host "📍 Current directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray

try {
    # Set Python path
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
    
    Write-Host "🌐 Starting Evaluator FastAPI server..." -ForegroundColor Yellow
    python main.py
    
} catch {
    Write-Host "❌ Failed to start Evaluator service: " -ForegroundColor Red
} finally {
    Pop-Location
}
