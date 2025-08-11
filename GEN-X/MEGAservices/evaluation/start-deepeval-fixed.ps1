# Start DeepEval Service - Fixed Version
Write-Host "🧠 Starting DeepEval Service (Fixed)..." -ForegroundColor Green

try {
    # Navigate to DeepEval directory
    Push-Location "microservices\deepeval\src"
    
    # Set Python path to include current directory
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
    
    Write-Host "📍 Directory: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray
    Write-Host "🐍 Python path configured" -ForegroundColor Gray
    
    # Install dependencies if needed
    Write-Host "📦 Ensuring dependencies are installed..." -ForegroundColor Gray
    pip install -q pydantic-settings grpcio grpcio-tools structlog deepeval openai
    
    # Start the service
    Write-Host "🚀 Starting DeepEval gRPC server..." -ForegroundColor Yellow
    python main.py
    
} catch {
    Write-Host "❌ Error starting DeepEval service: " -ForegroundColor Red
    Write-Host "💡 Try installing dependencies manually: pip install pydantic-settings grpcio grpcio-tools" -ForegroundColor Yellow
} finally {
    Pop-Location
}
