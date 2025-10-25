# ClauseBot Full Stack Verification Script
# Verifies both backend (Render) and frontend (Vercel) deployments

param(
    [Parameter(Mandatory=$true)]
    [string]$FrontendUrl,
    
    [string]$BackendUrl = "https://clausebot-api.onrender.com"
)

Write-Host "`n=== ClauseBot Full Stack Verification ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "Backend: $BackendUrl" -ForegroundColor Gray
Write-Host "Frontend: $FrontendUrl`n" -ForegroundColor Gray

$results = @{
    Backend = @{}
    Frontend = @{}
    Integration = @{}
}

# ============================================
# BACKEND VERIFICATION
# ============================================
Write-Host "`n[1/3] Backend API Tests" -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod "$BackendUrl/health" -UseBasicParsing
    if ($health.ok -eq $true) {
        Write-Host "  ✅ /health: OK" -ForegroundColor Green
        $results.Backend.Health = "PASS"
    }
} catch {
    Write-Host "  ❌ /health: ERROR" -ForegroundColor Red
    $results.Backend.Health = "FAIL"
}

try {
    $buildinfo = Invoke-RestMethod "$BackendUrl/buildinfo" -UseBasicParsing
    if ($buildinfo.REPO) {
        Write-Host "  ✅ /buildinfo: $($buildinfo.REPO) @ $($buildinfo.SHA)" -ForegroundColor Green
        $results.Backend.BuildInfo = "PASS"
    }
} catch {
    Write-Host "  ❌ /buildinfo: ERROR" -ForegroundColor Red
    $results.Backend.BuildInfo = "FAIL"
}

try {
    $airtable = Invoke-RestMethod "$BackendUrl/health/airtable" -UseBasicParsing
    if ($airtable.status -eq "connected") {
        Write-Host "  ✅ /health/airtable: Connected" -ForegroundColor Green
        $results.Backend.Airtable = "PASS"
    }
} catch {
    Write-Host "  ❌ /health/airtable: ERROR" -ForegroundColor Red
    $results.Backend.Airtable = "FAIL"
}

try {
    $quiz = Invoke-RestMethod "$BackendUrl/health/quiz/baseline" -UseBasicParsing
    Write-Host "  ✅ /health/quiz/baseline: $($quiz.eligible_in_sample) eligible questions" -ForegroundColor Green
    $results.Backend.Quiz = "PASS"
} catch {
    Write-Host "  ❌ /health/quiz/baseline: ERROR" -ForegroundColor Red
    $results.Backend.Quiz = "FAIL"
}

# ============================================
# FRONTEND VERIFICATION
# ============================================
Write-Host "`n[2/3] Frontend Deployment Tests" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest $FrontendUrl -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Homepage loads: 200 OK" -ForegroundColor Green
        $results.Frontend.Homepage = "PASS"
        
        # Check for Vite build markers
        if ($response.Content -match "modulepreload|type=`"module`"") {
            Write-Host "  ✅ Vite build detected" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  ❌ Homepage load failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.Frontend.Homepage = "FAIL"
}

# Test /blank redirect
try {
    $null = Invoke-WebRequest "$FrontendUrl/blank" -MaximumRedirection 0 -ErrorAction Stop
    Write-Host "  ❌ /blank should redirect" -ForegroundColor Red
    $results.Frontend.BlankRedirect = "FAIL"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 308 -or $statusCode -eq 307) {
        Write-Host "  ✅ /blank redirects correctly ($statusCode)" -ForegroundColor Green
        $results.Frontend.BlankRedirect = "PASS"
    } else {
        Write-Host "  ⚠️  /blank status: $statusCode (expected 308)" -ForegroundColor Yellow
        $results.Frontend.BlankRedirect = "PARTIAL"
    }
}

# Test /module-1 redirect
try {
    $null = Invoke-WebRequest "$FrontendUrl/module-1" -MaximumRedirection 0 -ErrorAction Stop
    Write-Host "  ❌ /module-1 should redirect" -ForegroundColor Red
    $results.Frontend.ModuleRedirect = "FAIL"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 308 -or $statusCode -eq 301) {
        Write-Host "  ✅ /module-1 redirects correctly ($statusCode)" -ForegroundColor Green
        $results.Frontend.ModuleRedirect = "PASS"
    } else {
        Write-Host "  ⚠️  /module-1 status: $statusCode (expected 308/301)" -ForegroundColor Yellow
        $results.Frontend.ModuleRedirect = "PARTIAL"
    }
}

# ============================================
# INTEGRATION TESTS
# ============================================
Write-Host "`n[3/3] Integration Tests" -ForegroundColor Yellow

# Test CORS
try {
    $headers = @{
        "Origin" = $FrontendUrl
        "Access-Control-Request-Method" = "GET"
    }
    
    $corsResponse = Invoke-WebRequest "$BackendUrl/health" -Method OPTIONS -Headers $headers -UseBasicParsing
    $allowOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]
    
    if ($allowOrigin) {
        Write-Host "  ✅ CORS configured for: $allowOrigin" -ForegroundColor Green
        $results.Integration.CORS = "PASS"
    } else {
        Write-Host "  ⚠️  CORS headers present but origin not in response" -ForegroundColor Yellow
        $results.Integration.CORS = "PARTIAL"
    }
} catch {
    Write-Host "  ⚠️  CORS check inconclusive" -ForegroundColor Yellow
    $results.Integration.CORS = "UNKNOWN"
}

# Check if frontend can reach backend
Write-Host "  ℹ️  Note: Browser-side API connectivity should be tested manually" -ForegroundColor Gray

# ============================================
# SUMMARY
# ============================================
Write-Host "`n=== VERIFICATION SUMMARY ===" -ForegroundColor Cyan

$totalChecks = 0
$passedChecks = 0

foreach ($category in $results.Keys) {
    foreach ($check in $results[$category].Keys) {
        $totalChecks++
        if ($results[$category][$check] -eq "PASS") {
            $passedChecks++
        }
    }
}

$passRate = [math]::Round(($passedChecks / $totalChecks) * 100, 0)

Write-Host "`nResults: $passedChecks/$totalChecks checks passed ($passRate%)" -ForegroundColor $(
    if ($passRate -ge 90) { "Green" } 
    elseif ($passRate -ge 70) { "Yellow" } 
    else { "Red" }
)

Write-Host "`nBackend (Render):" -ForegroundColor White
foreach ($key in $results.Backend.Keys) {
    $status = $results.Backend[$key]
    $color = if ($status -eq "PASS") { "Green" } else { "Red" }
    Write-Host "  $key : $status" -ForegroundColor $color
}

Write-Host "`nFrontend (Vercel):" -ForegroundColor White
foreach ($key in $results.Frontend.Keys) {
    $status = $results.Frontend[$key]
    $color = if ($status -eq "PASS") { "Green" } elseif ($status -eq "PARTIAL") { "Yellow" } else { "Red" }
    Write-Host "  $key : $status" -ForegroundColor $color
}

Write-Host "`nIntegration:" -ForegroundColor White
foreach ($key in $results.Integration.Keys) {
    $status = $results.Integration[$key]
    $color = if ($status -eq "PASS") { "Green" } elseif ($status -eq "PARTIAL" -or $status -eq "UNKNOWN") { "Yellow" } else { "Red" }
    Write-Host "  $key : $status" -ForegroundColor $color
}

# Final verdict
if ($passRate -ge 90) {
    Write-Host "`n🎉 DEPLOYMENT SUCCESSFUL - ALL SYSTEMS OPERATIONAL!" -ForegroundColor Green
    Write-Host "🎊 Weekend debugging loop: CLOSED!" -ForegroundColor Green
    exit 0
} elseif ($passRate -ge 70) {
    Write-Host "`n⚠️  DEPLOYMENT MOSTLY SUCCESSFUL - REVIEW WARNINGS" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n❌ DEPLOYMENT VERIFICATION FAILED - REVIEW ERRORS" -ForegroundColor Red
    exit 1
}

