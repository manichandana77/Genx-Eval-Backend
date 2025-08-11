# QUICK START - Evaluator Service
Write-Host "⚡ QUICK START: Evaluator Service" -ForegroundColor Green

try {
    Write-Host "📦 Installing final dependencies..." -ForegroundColor Yellow
    python -m pip install motor pymongo httpx --quiet --disable-pip-version-check 2>

    Push-Location "microservices\evaluator\src"
    
    # Set environment for testing
     = "C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation;"
     = "INFO"
     = "false"
     = "8000"
    
    # Use mock MongoDB for testing (won't require actual MongoDB)
     = "mongodb://localhost:27017/evaluation_test_db"
    
    Write-Host "🌍 Environment configured" -ForegroundColor Gray
    Write-Host "📍 Starting from: C:\Users\Chandu gorla\Desktop\Genx-Evaluation-Backend\GEN-X\MEGAservices\evaluation" -ForegroundColor Gray
    
    Write-Host "
🚀 Starting Evaluator API Server..." -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "🌐 API will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan  
    Write-Host "🏥 Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host "📊 Available endpoints:" -ForegroundColor Cyan
    Write-Host "  • GET  /health - Service health status" -ForegroundColor White
    Write-Host "  • POST /api/v1/evaluations/evaluate - Start evaluation" -ForegroundColor White
    Write-Host "  • GET  /api/v1/evaluations/metrics - Available metrics" -ForegroundColor White
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
    
    python main.py
    
} catch {
    Write-Host "❌ Error: " -ForegroundColor Red
    Write-Host "
💡 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check you're in the evaluation directory" -ForegroundColor White
    Write-Host "  2. Try: cd microservices\evaluator\src" -ForegroundColor White
    Write-Host "  3. Then: python main.py" -ForegroundColor White
} finally {
    Pop-Location
}
