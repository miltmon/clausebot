# ClauseBot API Smoke Test - One-Command Validation
# MiltmonNDTGPT's tight, no-fluff go-live validation

param(
    [string]$ApiUrl = "https://clausebot-api.onrender.com",
    [string]$WebUrl = "https://clausebot.miltmonndt.com"
)

Write-Host "🌊 ClauseBot API Smoke Test" -ForegroundColor Blue
Write-Host "===========================" -ForegroundColor Blue
Write-Host "API: $ApiUrl" -ForegroundColor Gray
Write-Host "Web: $WebUrl" -ForegroundColor Gray
Write-Host ""

$results = @()

Write-Host "🌐 API checks" -ForegroundColor Cyan
$endpoints = @("/", "/health", "/docs", "/api/ping", "/api/welding/test")

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri ($ApiUrl + $endpoint) -TimeoutSec 10
        Write-Host "  ✅ $endpoint" -ForegroundColor Green
        $results += @{ endpoint = $endpoint; status = "pass"; response = $response }
    } catch {
        Write-Host "  ❌ $endpoint -> $($_.Exception.Message)" -ForegroundColor Red
        $results += @{ endpoint = $endpoint; status = "fail"; error = $_.Exception.Message }
    }
}

Write-Host ""
Write-Host "🖥️  Frontend check" -ForegroundColor Cyan
try {
    $frontendResponse = Invoke-WebRequest -Uri $WebUrl -TimeoutSec 15
    Write-Host "  ✅ $WebUrl -> $($frontendResponse.StatusCode)" -ForegroundColor Green
    $results += @{ endpoint = "frontend"; status = "pass"; statusCode = $frontendResponse.StatusCode }
} catch {
    Write-Host "  ❌ $WebUrl -> $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ endpoint = "frontend"; status = "fail"; error = $_.Exception.Message }
}

Write-Host ""
Write-Host "🔗 CORS spot-check" -ForegroundColor Cyan
try {
    $headers = @{ 
        Origin = $WebUrl
        'Access-Control-Request-Method' = 'GET'
    }
    $preflightResponse = Invoke-WebRequest -Uri ($ApiUrl + "/health") -Method OPTIONS -Headers $headers -TimeoutSec 10 -ErrorAction SilentlyContinue
    
    if ($preflightResponse.Headers.'Access-Control-Allow-Origin') {
        Write-Host "  ✅ CORS allows $WebUrl" -ForegroundColor Green
        $results += @{ endpoint = "cors"; status = "pass"; message = "CORS configured correctly" }
    } else {
        Write-Host "  ⚠️  CORS header not visible (may still be fine in browser)" -ForegroundColor Yellow
        $results += @{ endpoint = "cors"; status = "warn"; message = "CORS header not visible in PowerShell test" }
    }
} catch {
    Write-Host "  ⚠️  Could not simulate preflight" -ForegroundColor Yellow
    $results += @{ endpoint = "cors"; status = "warn"; error = $_.Exception.Message }
}

# Summary
Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta

$passed = ($results | Where-Object { $_.status -eq "pass" }).Count
$failed = ($results | Where-Object { $_.status -eq "fail" }).Count
$warnings = ($results | Where-Object { $_.status -eq "warn" }).Count

Write-Host "Results: $passed passed, $failed failed, $warnings warnings" -ForegroundColor White

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "🎯 All critical tests passed! API and frontend are operational." -ForegroundColor Green
    Write-Host "Ready for production traffic." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Review errors above before going live." -ForegroundColor Yellow
}

# Save results for monitoring
$testReport = @{
    timestamp = (Get-Date).ToString("o")
    api_url = $ApiUrl
    web_url = $WebUrl
    results = $results
    summary = @{
        passed = $passed
        failed = $failed
        warnings = $warnings
        overall_status = if ($failed -eq 0) { "healthy" } else { "degraded" }
    }
}

$reportPath = "smoke_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$testReport | ConvertTo-Json -Depth 4 | Set-Content -Path $reportPath -Encoding UTF8
Write-Host ""
Write-Host "📄 Test report saved: $reportPath" -ForegroundColor Gray

Write-Host ""
Write-Host "🌊 Smoke test complete!" -ForegroundColor Blue
