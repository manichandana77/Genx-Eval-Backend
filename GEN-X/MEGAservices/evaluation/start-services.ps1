# Simple PowerShell script to start services
Write-Host "🚀 Starting Evaluation Backend..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "🐳 Starting services with Docker Compose..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "✅ Services started!" -ForegroundColor Green
Write-Host "🌐 Access points:" -ForegroundColor Cyan
Write-Host "   - Evaluator API: http://localhost:8000" -ForegroundColor White
Write-Host "   - MongoDB Admin: http://localhost:8081" -ForegroundColor White
Write-Host "   - DeepEval gRPC: localhost:50051" -ForegroundColor White

Write-Host "
📊 To view logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor White
