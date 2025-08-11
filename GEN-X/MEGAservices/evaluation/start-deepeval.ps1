# Start DeepEval Service
Write-Host "🧠 Starting DeepEval Service..." -ForegroundColor Green

# Navigate to DeepEval service directory
Push-Location "microservices\deepeval\src"

Write-Host "📍 Current directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray

try {
    # Set Python path
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
    
    Write-Host "🐍 Starting DeepEval gRPC server..." -ForegroundColor Yellow
    python main.py
    
} catch {
    Write-Host "❌ Failed to start DeepEval service: " -ForegroundColor Red
} finally {
    Pop-Location
}
