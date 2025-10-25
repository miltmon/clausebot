# ClauseBot Monorepo Deployment Verification Script
# Date: October 25, 2025
# Purpose: Verify Render backend + Vercel frontend deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$VercelUrl,
    
    [string]$RenderUrl = "https://clausebot-api.onrender.com"
)

Write-Host "`n=== ClauseBot Monorepo Deployment Verification ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

$results = @{
    Backend = @{}
    Frontend = @{}
    Integration = @{}
}

# ============================================
# BACKEND VERIFICATION
# ============================================
Write-Host "`n[1/4] Backend Health Checks" -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod "$RenderUrl/health" -UseBasicParsing
    if ($health.ok -eq $true) {
        Write-Host "  ✅ /health endpoint: OK" -ForegroundColor Green
        $results.Backend.Health = "PASS"
    } else {
        Write-Host "  ❌ /health endpoint: Failed" -ForegroundColor Red
        $results.Backend.Health = "FAIL"
    }
} catch {
    Write-Host "  ❌ /health endpoint: Error - $($_.Exception.Message)" -ForegroundColor Red
    $results.Backend.Health = "ERROR"
}

try {
    $airtable = Invoke-RestMethod "$RenderUrl/health/airtable" -UseBasicParsing
    if ($airtable.ok -eq $true) {
        Write-Host "  ✅ /health/airtable endpoint: OK" -ForegroundColor Green
        $results.Backend.Airtable = "PASS"
    } else {
        Write-Host "  ❌ /health/airtable endpoint: Failed" -ForegroundColor Red
        $results.Backend.Airtable = "FAIL"
    }
} catch {
    Write-Host "  ❌ /health/airtable endpoint: Error - $($_.Exception.Message)" -ForegroundColor Red
    $results.Backend.Airtable = "ERROR"
}

try {
    $quiz = Invoke-RestMethod "$RenderUrl/health/quiz/baseline" -UseBasicParsing
    Write-Host "  ✅ /health/quiz/baseline: OK (Total: $($quiz.total_records), Eligible: $($quiz.eligible_count))" -ForegroundColor Green
    $results.Backend.Quiz = "PASS"
} catch {
    Write-Host "  ❌ /health/quiz/baseline: Error - $($_.Exception.Message)" -ForegroundColor Red
    $results.Backend.Quiz = "ERROR"
}

# ============================================
# FRONTEND VERIFICATION
# ============================================
Write-Host "`n[2/4] Frontend Health Checks" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest $VercelUrl -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ Frontend loads: 200 OK" -ForegroundColor Green
        $results.Frontend.Load = "PASS"
        
        # Check for build artifacts
        if ($response.Content -match "vite") {
            Write-Host "  ✅ Vite build detected" -ForegroundColor Green
        }
        
        # Check for GA4 script
        if ($response.Content -match "gtag|analytics") {
            Write-Host "  ✅ Analytics script detected" -ForegroundColor Green
            $results.Frontend.GA4 = "DETECTED"
        } else {
            Write-Host "  ⚠️  Analytics script not found in HTML" -ForegroundColor Yellow
            $results.Frontend.GA4 = "NOT_DETECTED"
        }
    }
} catch {
    Write-Host "  ❌ Frontend load failed: $($_.Exception.Message)" -ForegroundColor Red
    $results.Frontend.Load = "FAIL"
}

# ============================================
# REDIRECT VERIFICATION
# ============================================
Write-Host "`n[3/4] Vercel Redirect Checks" -ForegroundColor Yellow

# Test /blank redirect
try {
    $null = Invoke-WebRequest "$VercelUrl/blank" -MaximumRedirection 0 -ErrorAction Stop
    Write-Host "  ❌ /blank should redirect (expected 308)" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 308 -or $statusCode -eq 307) {
        Write-Host "  ✅ /blank redirects correctly ($statusCode)" -ForegroundColor Green
        $results.Frontend.BlankRedirect = "PASS"
    } else {
        Write-Host "  ❌ /blank unexpected status: $statusCode" -ForegroundColor Red
        $results.Frontend.BlankRedirect = "FAIL"
    }
}

# Test /module-1 redirect
try {
    $null = Invoke-WebRequest "$VercelUrl/module-1" -MaximumRedirection 0 -ErrorAction Stop
    Write-Host "  ❌ /module-1 should redirect (expected 308)" -ForegroundColor Red
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 308 -or $statusCode -eq 301) {
        Write-Host "  ✅ /module-1 redirects correctly ($statusCode)" -ForegroundColor Green
        $results.Frontend.ModuleRedirect = "PASS"
    } else {
        Write-Host "  ❌ /module-1 unexpected status: $statusCode" -ForegroundColor Red
        $results.Frontend.ModuleRedirect = "FAIL"
    }
}

# ============================================
# CORS VERIFICATION
# ============================================
Write-Host "`n[4/4] CORS Configuration Check" -ForegroundColor Yellow

try {
    $headers = @{
        "Origin" = $VercelUrl
        "Access-Control-Request-Method" = "GET"
        "Access-Control-Request-Headers" = "Content-Type"
    }
    
    $corsResponse = Invoke-WebRequest "$RenderUrl/health" -Method OPTIONS -Headers $headers -UseBasicParsing
    
    $allowOrigin = $corsResponse.Headers["Access-Control-Allow-Origin"]
    if ($allowOrigin) {
        Write-Host "  ✅ CORS configured: $allowOrigin" -ForegroundColor Green
        $results.Integration.CORS = "PASS"
    } else {
        Write-Host "  ⚠️  CORS headers present but origin not in response" -ForegroundColor Yellow
        $results.Integration.CORS = "PARTIAL"
    }
} catch {
    Write-Host "  ⚠️  CORS preflight check inconclusive: $($_.Exception.Message)" -ForegroundColor Yellow
    $results.Integration.CORS = "UNKNOWN"
}

# ============================================
# SUMMARY
# ============================================
Write-Host "`n=== DEPLOYMENT VERIFICATION SUMMARY ===" -ForegroundColor Cyan

$totalChecks = 0
$passedChecks = 0

foreach ($category in $results.Keys) {
    foreach ($check in $results[$category].Keys) {
        $totalChecks++
        if ($results[$category][$check] -eq "PASS" -or $results[$category][$check] -eq "DETECTED") {
            $passedChecks++
        }
    }
}

Write-Host "`nResults: $passedChecks/$totalChecks checks passed" -ForegroundColor $(if ($passedChecks -eq $totalChecks) { "Green" } else { "Yellow" })

Write-Host "`nBackend (Render):" -ForegroundColor White
Write-Host "  Health: $($results.Backend.Health)" -ForegroundColor $(if ($results.Backend.Health -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Airtable: $($results.Backend.Airtable)" -ForegroundColor $(if ($results.Backend.Airtable -eq "PASS") { "Green" } else { "Red" })
Write-Host "  Quiz: $($results.Backend.Quiz)" -ForegroundColor $(if ($results.Backend.Quiz -eq "PASS") { "Green" } else { "Red" })

Write-Host "`nFrontend (Vercel):" -ForegroundColor White
Write-Host "  Load: $($results.Frontend.Load)" -ForegroundColor $(if ($results.Frontend.Load -eq "PASS") { "Green" } else { "Red" })
Write-Host "  GA4: $($results.Frontend.GA4)" -ForegroundColor $(if ($results.Frontend.GA4 -eq "DETECTED") { "Green" } else { "Yellow" })
Write-Host "  /blank redirect: $($results.Frontend.BlankRedirect)" -ForegroundColor $(if ($results.Frontend.BlankRedirect -eq "PASS") { "Green" } else { "Red" })
Write-Host "  /module-1 redirect: $($results.Frontend.ModuleRedirect)" -ForegroundColor $(if ($results.Frontend.ModuleRedirect -eq "PASS") { "Green" } else { "Red" })

Write-Host "`nIntegration:" -ForegroundColor White
Write-Host "  CORS: $($results.Integration.CORS)" -ForegroundColor $(if ($results.Integration.CORS -eq "PASS") { "Green" } elseif ($results.Integration.CORS -eq "PARTIAL") { "Yellow" } else { "Gray" })

if ($passedChecks -eq $totalChecks) {
    Write-Host "`n🎉 ALL CHECKS PASSED - DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    exit 0
} elseif ($passedChecks -ge ($totalChecks * 0.8)) {
    Write-Host "`n⚠️  DEPLOYMENT PARTIALLY SUCCESSFUL - REVIEW WARNINGS" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n❌ DEPLOYMENT VERIFICATION FAILED - REVIEW ERRORS ABOVE" -ForegroundColor Red
    exit 1
}

