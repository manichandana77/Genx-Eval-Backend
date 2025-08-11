# Start Both Services
Write-Host "🚀 Starting Both Services..." -ForegroundColor Green

# Start DeepEval service in background
Write-Host "🧠 Starting DeepEval service..." -ForegroundColor Yellow
Start-Process PowerShell -ArgumentList "-File", "start-deepeval.ps1" -WindowStyle Normal

# Wait a moment for DeepEval to start
Start-Sleep -Seconds 3

# Start Evaluator service
Write-Host "⚙️ Starting Evaluator service..." -ForegroundColor Yellow
Start-Process PowerShell -ArgumentList "-File", "start-evaluator.ps1" -WindowStyle Normal

Write-Host "✅ Both services started!" -ForegroundColor Green
Write-Host "🌐 Access points:" -ForegroundColor Cyan
Write-Host "   - Evaluator API: http://localhost:8000" -ForegroundColor White
Write-Host "   - DeepEval gRPC: localhost:50051" -ForegroundColor White
Write-Host "   - API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - Health Check: http://localhost:8000/health" -ForegroundColor White
