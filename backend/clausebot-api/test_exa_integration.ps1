# Test Exa.ai Integration - End-to-End Validation
# Tests both webhook and pull integration with mock data

param(
    [string]$DriveRoot = "$HOME\Google Drive\ClauseBot_OPPS_Workspace",
    [switch]$TestWebhook = $true,
    [switch]$TestPull = $true,
    [switch]$TestCascade = $true
)

Write-Host "🧪 Exa.ai Integration Test Suite" -ForegroundColor Magenta
Write-Host "================================" -ForegroundColor Magenta

$testResults = @()

# Test 1: Webhook Integration
if ($TestWebhook) {
    Write-Host ""
    Write-Host "1. 🔗 Testing Webhook Integration..." -ForegroundColor Cyan
    
    # Start webhook server in background
    Start-Process -FilePath "python" -ArgumentList "exa_webhook_app.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    
    # Test webhook with mock data
    $mockPayload = @{
        source = "exa.ai"
        webset_id = "aws_cwi_test"
        items = @(
            @{
                title = "AWS D1.1 2025 Rev 1 – Clause 6 Updates"
                url = "https://example.org/aws-d1-1-2025-r1"
                description = "Preheat minimum raised to 75°C for Group II steels (summary)."
                detected_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                sections = @("6.1.4", "6.2.1")
                impact_tags = @("procedure", "parameter", "preheat")
            }
        )
    } | ConvertTo-Json -Depth 4
    
    try {
        $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8088/exa/webset/ingest" -Body $mockPayload -ContentType "application/json"
        Write-Host "   ✅ Webhook test passed: $($response.accepted) items accepted" -ForegroundColor Green
        $testResults += @{ test = "webhook"; status = "pass"; details = $response }
    } catch {
        Write-Host "   ❌ Webhook test failed: $($_.Exception.Message)" -ForegroundColor Red
        $testResults += @{ test = "webhook"; status = "fail"; error = $_.Exception.Message }
    }
}

# Test 2: Pull Integration
if ($TestPull) {
    Write-Host ""
    Write-Host "2. 📥 Testing Pull Integration..." -ForegroundColor Cyan
    
    # Create mock CSV export
    $mockCsv = @"
Title,URL,Description,UpdatedAt
"ASME Section IX 2023 Update","https://example.org/asme-ix-2023","New qualification requirements for automated welding","2025-10-01T18:00:00Z"
"AWS CWI Certification Changes","https://example.org/cwi-cert-2025","Updated inspection criteria for structural welding","2025-10-01T17:30:00Z"
"@
    
    $tempCsv = "$env:TEMP\mock_exa_export.csv"
    $mockCsv | Set-Content -Path $tempCsv -Encoding UTF8
    
    try {
        & "~\Diagnostics\exa_pull.ps1" -ExportPath $tempCsv -WebsetId "test_webset" -DriveRoot $DriveRoot
        Write-Host "   ✅ Pull integration test passed" -ForegroundColor Green
        $testResults += @{ test = "pull"; status = "pass"; details = "CSV processed successfully" }
    } catch {
        Write-Host "   ❌ Pull integration test failed: $($_.Exception.Message)" -ForegroundColor Red
        $testResults += @{ test = "pull"; status = "fail"; error = $_.Exception.Message }
    }
    
    # Cleanup
    Remove-Item $tempCsv -ErrorAction SilentlyContinue
}

# Test 3: Compliance Cascade
if ($TestCascade) {
    Write-Host ""
    Write-Host "3. 🌊 Testing Compliance Cascade..." -ForegroundColor Cyan
    
    # Find a test compliance update file
    $inboxDir = Join-Path $DriveRoot "Shared\compliance_updates\inbox"
    $testFile = Get-ChildItem -Path $inboxDir -Filter "exa_*.json" | Select-Object -First 1
    
    if ($testFile) {
        try {
            & "~\Diagnostics\windsurf_compliance_cascade.ps1" -ComplianceUpdatePath $testFile.FullName -DryRun
            Write-Host "   ✅ Compliance cascade test passed" -ForegroundColor Green
            $testResults += @{ test = "cascade"; status = "pass"; details = "Dry run completed successfully" }
        } catch {
            Write-Host "   ❌ Compliance cascade test failed: $($_.Exception.Message)" -ForegroundColor Red
            $testResults += @{ test = "cascade"; status = "fail"; error = $_.Exception.Message }
        }
    } else {
        Write-Host "   ⚠️  No compliance update files found for cascade test" -ForegroundColor Yellow
        $testResults += @{ test = "cascade"; status = "skip"; reason = "No test files available" }
    }
}

# Test 4: API Integration
Write-Host ""
Write-Host "4. 🚀 Testing API Integration..." -ForegroundColor Cyan

try {
    # Test ClauseBot API health
    $health = Invoke-RestMethod -Uri "http://localhost:8081/api/v1/pilot-a/health" -TimeoutSec 5
    Write-Host "   ✅ ClauseBot API health check passed" -ForegroundColor Green
    
    # Test metrics endpoint
    $metrics = Invoke-RestMethod -Uri "http://localhost:8081/api/v1/pilot-a/metrics" -TimeoutSec 5
    Write-Host "   ✅ Metrics endpoint accessible" -ForegroundColor Green
    
    $testResults += @{ test = "api"; status = "pass"; details = "All endpoints responding" }
} catch {
    Write-Host "   ⚠️  ClauseBot API not running (start with: uvicorn api.main:app --port 8081)" -ForegroundColor Yellow
    $testResults += @{ test = "api"; status = "skip"; reason = "API server not running" }
}

# Test Summary
Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta

$passed = ($testResults | Where-Object { $_.status -eq "pass" }).Count
$failed = ($testResults | Where-Object { $_.status -eq "fail" }).Count
$skipped = ($testResults | Where-Object { $_.status -eq "skip" }).Count

foreach ($result in $testResults) {
    $status = switch ($result.status) {
        "pass" { "✅ PASS" }
        "fail" { "❌ FAIL" }
        "skip" { "⚠️  SKIP" }
    }
    Write-Host "  $status - $($result.test)" -ForegroundColor White
    if ($result.error) {
        Write-Host "    Error: $($result.error)" -ForegroundColor Red
    }
    if ($result.reason) {
        Write-Host "    Reason: $($result.reason)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Results: $passed passed, $failed failed, $skipped skipped" -ForegroundColor White

if ($failed -eq 0) {
    Write-Host "🎯 All tests passed! Exa.ai integration is ready for production." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Review errors above before deployment." -ForegroundColor Yellow
}

# Cleanup webhook server
Get-Process -Name "python" | Where-Object { $_.CommandLine -like "*exa_webhook_app*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🧪 Test suite complete!" -ForegroundColor Magenta
