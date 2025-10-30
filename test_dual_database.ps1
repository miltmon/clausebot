# ClauseBot Dual-Database API Test Suite
# Comprehensive validation for Supabase + Airtable integration

param(
    [string]$ApiBase = "http://127.0.0.1:8000",
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Continue"

Write-Host "🧪 ClauseBot Dual-Database API Test Suite" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
Write-Host "API Base: $ApiBase" -ForegroundColor Gray
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$testResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method = "GET",
        [string]$Endpoint,
        [hashtable]$Body = @{},
        [string]$ExpectedStatus = "200"
    )
    
    Write-Host "🔍 Testing: $Name" -ForegroundColor Cyan
    
    try {
        $uri = "$ApiBase$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            TimeoutSec = 10
        }
        
        if ($Body.Count -gt 0) {
            $params.Body = ($Body | ConvertTo-Json -Depth 4)
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "   ✅ SUCCESS - $Name" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
        }
        
        $script:testResults += @{
            Test = $Name
            Status = "PASS"
            Response = $response
            Error = $null
        }
        
        return $response
    }
    catch {
        Write-Host "   ❌ FAILED - $Name" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        
        $script:testResults += @{
            Test = $Name
            Status = "FAIL"
            Response = $null
            Error = $_.Exception.Message
        }
        
        return $null
    }
}

# ===== BASIC HEALTH CHECKS =====
Write-Host "1️⃣  BASIC HEALTH CHECKS" -ForegroundColor Magenta
Write-Host "======================" -ForegroundColor Magenta

Test-Endpoint "Root Endpoint" "GET" "/"
Test-Endpoint "Health Check" "GET" "/health"
Test-Endpoint "Detailed Health" "GET" "/health/detailed"

# ===== LEGACY ENDPOINTS =====
Write-Host ""
Write-Host "2️⃣  LEGACY ENDPOINTS" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

Test-Endpoint "Ping Endpoint" "GET" "/api/ping"
Test-Endpoint "Welding Test" "GET" "/api/welding/test"

# ===== READ OPERATIONS =====
Write-Host ""
Write-Host "3️⃣  READ OPERATIONS" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta

Test-Endpoint "List Incidents (Supabase)" "GET" "/api/incidents"
Test-Endpoint "List Airtable Records" "GET" "/api/airtable"
Test-Endpoint "Search Test" "GET" "/api/search?q=test"

# ===== WRITE OPERATIONS =====
Write-Host ""
Write-Host "4️⃣  WRITE OPERATIONS" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

# Test basic incident creation
$testIncident = @{
    source = "manual"
    title = "Test Incident - $(Get-Date -Format 'HH:mm:ss')"
    description = "Local API test incident"
    severity = "low"
    confidence = 0.95
    payload = @{
        test_run = $true
        timestamp = (Get-Date).ToString("o")
        local_test = $true
    }
}

$createResult = Test-Endpoint "Create Test Incident" "POST" "/api/ingest/incident" $testIncident

# Test CURSOR incident integration
if ($createResult) {
    Write-Host ""
    Write-Host "5️⃣  CURSOR INTEGRATION" -ForegroundColor Magenta
    Write-Host "=====================" -ForegroundColor Magenta
    
    $cursorIncident = @{
        incident_type = "chrome_hang_test"
        severity = "medium"
        confidence = 0.77
        system_context = @{
            os = "Windows 11"
            ram_gb = 16
            gpu = "Intel Ultra 7 155H"
            test_mode = $true
        }
        gpu_info = @{
            driver_version = "31.0.101.4826"
            hardware_acceleration = $true
        }
        chrome_config = @{
            version = "118.0.5993.88"
            angle_backend = "D3D11"
        }
    }
    
    Test-Endpoint "CURSOR Incident Report" "POST" "/api/cursor/incident" $cursorIncident
}

# ===== SUMMARY =====
Write-Host ""
Write-Host "📊 TEST SUMMARY" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta

$totalTests = $testResults.Count
$passedTests = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failedTests = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count

Write-Host ""
Write-Host "Results: $passedTests passed, $failedTests failed (of $totalTests total)" -ForegroundColor White

if ($failedTests -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED! Dual-database API is working correctly." -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Check the errors above." -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "Failed Tests:" -ForegroundColor Red
    $testResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "   ❌ $($_.Test): $($_.Error)" -ForegroundColor Red
    }
}

# Save results
$reportPath = "test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report = @{
    timestamp = (Get-Date).ToString("o")
    api_base = $ApiBase
    total_tests = $totalTests
    passed = $passedTests
    failed = $failedTests
    results = $testResults
}

try {
    $report | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host ""
    Write-Host "📄 Test report saved: $reportPath" -ForegroundColor Gray
} catch {
    Write-Host ""
    Write-Host "⚠️  Could not save test report: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🧪 Testing complete!" -ForegroundColor Blue

# Exit with appropriate code
if ($failedTests -eq 0) {
    exit 0
} else {
    exit 1
}
