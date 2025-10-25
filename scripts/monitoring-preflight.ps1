# ClauseBot Monitoring Pre-Flight Check
# Run this before setting up UptimeRobot monitors (Nov 2, 2025)

Write-Host "`n=== ClauseBot Monitoring Pre-Flight Checks ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "Purpose: Verify all endpoints before UptimeRobot setup`n" -ForegroundColor Gray

$results = @()

# Define endpoints to check
$endpoints = @(
    @{
        Name = "API Health"
        URL = "https://clausebot-api.onrender.com/health"
        ExpectedStatus = 200
        ExpectedKeyword = "ok"
        Critical = $true
    },
    @{
        Name = "Frontend"
        URL = "https://clausebot.vercel.app/"
        ExpectedStatus = 200
        ExpectedKeyword = "ClauseBot"
        Critical = $true
    },
    @{
        Name = "Quiz API"
        URL = "https://clausebot-api.onrender.com/v1/quiz/fundamentals"
        ExpectedStatus = 200
        ExpectedKeyword = "questions"
        Critical = $false
    },
    @{
        Name = "Crosswalk API"
        URL = "https://clausebot-api.onrender.com/v1/crosswalk/stats"
        ExpectedStatus = 200
        ExpectedKeyword = "total"
        Critical = $false
    },
    @{
        Name = "Buildinfo"
        URL = "https://clausebot-api.onrender.com/buildinfo"
        ExpectedStatus = 200
        ExpectedKeyword = "REPO"
        Critical = $false
    }
)

# Test each endpoint
foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $($endpoint.Name)..." -ForegroundColor Yellow
    
    $result = @{
        Name = $endpoint.Name
        URL = $endpoint.URL
        Status = "UNKNOWN"
        StatusCode = 0
        ResponseTime = 0
        KeywordFound = $false
        Critical = $endpoint.Critical
    }
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest $endpoint.URL -UseBasicParsing -TimeoutSec 30
        $stopwatch.Stop()
        
        $result.StatusCode = $response.StatusCode
        $result.ResponseTime = $stopwatch.ElapsedMilliseconds
        
        # Check for expected keyword
        if ($response.Content -match $endpoint.ExpectedKeyword) {
            $result.KeywordFound = $true
        }
        
        # Determine overall status
        if ($response.StatusCode -eq $endpoint.ExpectedStatus -and $result.KeywordFound) {
            $result.Status = "PASS"
            Write-Host "  ✅ Status: $($result.StatusCode) | Response: $($result.ResponseTime)ms | Keyword: Found" -ForegroundColor Green
        } elseif ($response.StatusCode -eq $endpoint.ExpectedStatus) {
            $result.Status = "WARN"
            Write-Host "  ⚠️  Status: $($result.StatusCode) | Response: $($result.ResponseTime)ms | Keyword: NOT Found" -ForegroundColor Yellow
        } else {
            $result.Status = "FAIL"
            Write-Host "  ❌ Status: $($result.StatusCode) (expected $($endpoint.ExpectedStatus))" -ForegroundColor Red
        }
        
    } catch {
        $result.Status = "FAIL"
        Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $results += $result
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan

$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$warnTests = ($results | Where-Object { $_.Status -eq "WARN" }).Count
$failedTests = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$criticalFailed = ($results | Where-Object { $_.Critical -and $_.Status -eq "FAIL" }).Count

Write-Host "`nTest Results: $passedTests PASS | $warnTests WARN | $failedTests FAIL (of $totalTests total)" -ForegroundColor White

if ($criticalFailed -gt 0) {
    Write-Host "`n⚠️  CRITICAL: $criticalFailed critical endpoints failed!" -ForegroundColor Red
    Write-Host "   Do NOT proceed with UptimeRobot setup until these are fixed." -ForegroundColor Red
} elseif ($failedTests -gt 0) {
    Write-Host "`n⚠️  $failedTests non-critical endpoints failed" -ForegroundColor Yellow
    Write-Host "   You can proceed with UptimeRobot setup, but investigate these issues." -ForegroundColor Yellow
} elseif ($warnTests -gt 0) {
    Write-Host "`n✅ All endpoints responding, but $warnTests have keyword warnings" -ForegroundColor Yellow
    Write-Host "   Safe to proceed with UptimeRobot setup." -ForegroundColor Yellow
} else {
    Write-Host "`n✅ ALL CHECKS PASSED - READY FOR UPTIMEROBOT SETUP!" -ForegroundColor Green
}

# Detailed Results Table
Write-Host "`n=== DETAILED RESULTS ===" -ForegroundColor Cyan
$results | Format-Table Name, Status, StatusCode, ResponseTime, KeywordFound -AutoSize

# Response Time Analysis
Write-Host "`n=== RESPONSE TIME ANALYSIS ===" -ForegroundColor Cyan
$avgResponseTime = ($results | Measure-Object -Property ResponseTime -Average).Average
Write-Host "Average Response Time: $([math]::Round($avgResponseTime, 0))ms" -ForegroundColor White

$slowEndpoints = $results | Where-Object { $_.ResponseTime -gt 1000 }
if ($slowEndpoints) {
    Write-Host "`n⚠️  Slow endpoints (>1000ms):" -ForegroundColor Yellow
    $slowEndpoints | ForEach-Object {
        Write-Host "   - $($_.Name): $($_.ResponseTime)ms" -ForegroundColor Yellow
    }
}

# Final Recommendation
Write-Host "`n=== RECOMMENDATION ===" -ForegroundColor Cyan

if ($criticalFailed -gt 0) {
    Write-Host "❌ DO NOT PROCEED - Fix critical failures first" -ForegroundColor Red
    exit 1
} elseif ($passedTests -eq $totalTests) {
    Write-Host "✅ PROCEED WITH UPTIMEROBOT SETUP" -ForegroundColor Green
    Write-Host "   All endpoints are healthy and ready for monitoring.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  PROCEED WITH CAUTION" -ForegroundColor Yellow
    Write-Host "   Some non-critical endpoints have issues. Document these." -ForegroundColor Yellow
    Write-Host "   Safe to set up monitors, but investigate failures after setup.`n" -ForegroundColor Yellow
    exit 0
}

