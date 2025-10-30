# ClauseBot Exa.ai Setup Script
Write-Host "🚀 ClauseBot Exa.ai Integration Setup" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✅ Found existing .env file" -ForegroundColor Green
} else {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# Prompt for Exa API key
Write-Host ""
Write-Host "🔑 Please enter your Exa API key from https://dashboard.exa.ai/api-keys" -ForegroundColor Cyan
$exaKey = Read-Host "Exa API Key"

if ([string]::IsNullOrWhiteSpace($exaKey)) {
    Write-Host "❌ No API key provided. Exiting..." -ForegroundColor Red
    exit 1
}

# Update .env file
$envContent = Get-Content ".env" -Raw
if ($envContent -match "EXA_API_KEY=.*") {
    $envContent = $envContent -replace "EXA_API_KEY=.*", "EXA_API_KEY=$exaKey"
} else {
    $envContent += "`nEXA_API_KEY=$exaKey"
}

# Write updated content
$envContent | Out-File -FilePath ".env" -Encoding utf8 -NoNewline

Write-Host ""
Write-Host "✅ Exa API key configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🧪 Testing API endpoints..." -ForegroundColor Yellow

# Start the server in background for testing
Write-Host "Starting ClauseBot API server..." -ForegroundColor Cyan
$serverProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Hidden

# Wait for server to start
Start-Sleep -Seconds 5

try {
    # Test health endpoint
    Write-Host "Testing health endpoint..." -ForegroundColor Cyan
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8080/v1/healthz" -Method Get
    Write-Host "✅ Health check: $($healthResponse.status)" -ForegroundColor Green

    # Test websets list (requires auth)
    Write-Host "Testing websets endpoint..." -ForegroundColor Cyan
    $headers = @{ "Authorization" = "Bearer dev_read" }
    $websetsResponse = Invoke-RestMethod -Uri "http://localhost:8080/v1/websets" -Method Get -Headers $headers
    Write-Host "✅ Found $($websetsResponse.total) websets available" -ForegroundColor Green

    Write-Host ""
    Write-Host "🎉 ClauseBot API with Exa integration is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Available endpoints:" -ForegroundColor Cyan
    Write-Host "  • Health: http://localhost:8080/v1/healthz" -ForegroundColor White
    Write-Host "  • Websets: http://localhost:8080/v1/websets" -ForegroundColor White
    Write-Host "  • Search: http://localhost:8080/v1/websets/search?q=welding" -ForegroundColor White
    Write-Host "  • Multi-search: http://localhost:8080/v1/websets/multi-search?q=AWS" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Integration ready for Lovable frontend!" -ForegroundColor Green

} catch {
    Write-Host "❌ API test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Check that your Exa API key is valid and has sufficient credits." -ForegroundColor Yellow
} finally {
    # Stop the test server
    if ($serverProcess -and !$serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force
        Write-Host "Server stopped." -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "To start the server manually: npm run dev" -ForegroundColor Cyan
