# ClauseBot Smoke Tests
# Run after deployment to verify both backend and frontend

Write-Host "`n=== ClauseBot Smoke Tests ===" -ForegroundColor Cyan

# Backend health checks
Write-Host "`n[Backend] Testing API..." -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod "https://clausebot-api.onrender.com/health" -UseBasicParsing
    if ($health.ok) {
        Write-Host "  ✅ /health - OK (version: $($health.version))" -ForegroundColor Green
    } else {
        Write-Host "  ❌ /health - FAILED" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ /health - ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

try {
    $airtable = Invoke-RestMethod "https://clausebot-api.onrender.com/health/airtable" -UseBasicParsing
    if ($airtable.status -eq "connected") {
        Write-Host "  ✅ /health/airtable - Connected" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  /health/airtable - Status: $($airtable.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ /health/airtable - ERROR" -ForegroundColor Red
}

try {
    $quiz = Invoke-RestMethod "https://clausebot-api.onrender.com/v1/quiz?count=2" -UseBasicParsing
    if ($quiz.source -eq "airtable") {
        Write-Host "  ✅ /v1/quiz - OK (source: airtable, count: $($quiz.count))" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  /v1/quiz - Source: $($quiz.source)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠️  /v1/quiz - $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
}

# Frontend health check
Write-Host "`n[Frontend] Testing site..." -ForegroundColor Yellow

try {
    $frontend = Invoke-WebRequest "https://clausebot.miltmonndt.com" -UseBasicParsing -TimeoutSec 10
    if ($frontend.StatusCode -eq 200) {
        Write-Host "  ✅ Frontend - OK" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Frontend - ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Smoke Tests Complete ===" -ForegroundColor Cyan
Write-Host ""

