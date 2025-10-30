# ClauseBot Production Readiness Test
# Comprehensive validation for deployment readiness

param(
    [string]$ApiBase = "http://127.0.0.1:8000",
    [switch]$Verbose = $false,
    [switch]$SkipCredentialTests = $false
)

$ErrorActionPreference = "Continue"

Write-Host "🚀 ClauseBot Production Readiness Test" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
Write-Host "API Base: $ApiBase" -ForegroundColor Gray
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$testResults = @()
$criticalIssues = @()
$warnings = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method = "GET",
        [string]$Endpoint,
        [hashtable]$Body = @{},
        [string]$Category = "General",
        [bool]$Critical = $false
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
        
        Write-Host "   ✅ PASS - $Name" -ForegroundColor Green
        if ($Verbose) {
            Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
        }
        
        $script:testResults += @{
            Test = $Name
            Category = $Category
            Status = "PASS"
            Response = $response
            Critical = $Critical
        }
        
        return $response
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-Host "   ❌ FAIL - $Name" -ForegroundColor Red
        Write-Host "   Error: $errorMsg" -ForegroundColor Red
        
        if ($Critical) {
            $script:criticalIssues += "$Name - $errorMsg"
        } else {
            $script:warnings += "$Name - $errorMsg"
        }
        
        $script:testResults += @{
            Test = $Name
            Category = $Category
            Status = "FAIL"
            Error = $errorMsg
            Critical = $Critical
        }
        
        return $null
    }
}

# ===== 1. CORE API FUNCTIONALITY =====
Write-Host "1️⃣  CORE API FUNCTIONALITY" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

$rootResponse = Test-Endpoint "Root Endpoint" "GET" "/" @{} "Core" $true
$healthResponse = Test-Endpoint "Basic Health Check" "GET" "/health" @{} "Core" $true
$detailedHealthResponse = Test-Endpoint "Detailed Health Check" "GET" "/health/detailed" @{} "Core" $false

# ===== 2. SUPERPOWER ENDPOINTS =====
Write-Host ""
Write-Host "2️⃣  SUPERPOWER ENDPOINTS" -ForegroundColor Magenta
Write-Host "========================" -ForegroundColor Magenta

Test-Endpoint "AI Provider Config" "GET" "/api/config/provider" @{} "AI" $false
Test-Endpoint "Cost Model Pricing" "GET" "/api/costs/models" @{} "Cost" $false
Test-Endpoint "Metrics Snapshot" "GET" "/api/metrics/snapshot" @{} "Metrics" $false
Test-Endpoint "Model Whoami" "GET" "/whoami/model" @{} "AI" $false

# ===== 3. DATABASE CONNECTIVITY =====
Write-Host ""
Write-Host "3️⃣  DATABASE CONNECTIVITY" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

if (-not $SkipCredentialTests) {
    Test-Endpoint "List Incidents (Supabase)" "GET" "/api/incidents?limit=1" @{} "Database" $false
    Test-Endpoint "List Airtable Records" "GET" "/api/airtable" @{} "Database" $false
    Test-Endpoint "Search Functionality" "GET" "/api/search?q=test" @{} "Database" $false
} else {
    Write-Host "   ⚠️  SKIPPED - Database tests (credentials not configured)" -ForegroundColor Yellow
}

# ===== 4. AI FUNCTIONALITY =====
Write-Host ""
Write-Host "4️⃣  AI FUNCTIONALITY" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

if (-not $SkipCredentialTests) {
    $aiRequest = @{
        prompt = "What is AWS D1.1?"
        temperature = 0.1
        max_tokens = 100
    }
    Test-Endpoint "AI Assistant" "POST" "/api/assist" $aiRequest "AI" $false
    
    $costRequest = @{
        provider_model = "gpt-4"
        monthly_calls = 1000
        avg_input_tokens = 100
        avg_output_tokens = 200
    }
    Test-Endpoint "Cost Estimation" "POST" "/api/costs/estimate" $costRequest "Cost" $false
} else {
    Write-Host "   ⚠️  SKIPPED - AI tests (API keys not configured)" -ForegroundColor Yellow
}

# ===== 5. INCIDENT MANAGEMENT =====
Write-Host ""
Write-Host "5️⃣  INCIDENT MANAGEMENT" -ForegroundColor Magenta
Write-Host "======================" -ForegroundColor Magenta

if (-not $SkipCredentialTests) {
    $testIncident = @{
        source = "manual"
        title = "Production Readiness Test - $(Get-Date -Format 'HH:mm:ss')"
        description = "Automated test incident for production validation"
        severity = "low"
        confidence = 0.99
        payload = @{
            test_type = "production_readiness"
            timestamp = (Get-Date).ToString("o")
        }
    }
    Test-Endpoint "Create Test Incident" "POST" "/api/ingest/incident" $testIncident "Incident" $false
    
    $cursorIncident = @{
        incident_type = "production_test"
        severity = "low"
        confidence = 0.95
        system_context = @{
            test_mode = $true
            os = "Windows 11"
            validation = "production_readiness"
        }
    }
    Test-Endpoint "CURSOR Incident Integration" "POST" "/api/cursor/incident" $cursorIncident "Incident" $false
} else {
    Write-Host "   ⚠️  SKIPPED - Incident tests (database not configured)" -ForegroundColor Yellow
}

# ===== 6. CONFIGURATION VALIDATION =====
Write-Host ""
Write-Host "6️⃣  CONFIGURATION VALIDATION" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Magenta

# Check environment variables
$envVars = @(
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY", 
    "AIRTABLE_API_KEY",
    "AIRTABLE_BASE_ID",
    "MODEL_PROVIDER",
    "MODEL_NAME"
)

$configuredVars = 0
$totalVars = $envVars.Count

foreach ($var in $envVars) {
    $value = [System.Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "   ✅ ${var}: Configured" -ForegroundColor Green
        $configuredVars++
    } else {
        Write-Host "   ❌ ${var}: Not configured" -ForegroundColor Red
        $script:warnings += "Environment variable $var not configured"
    }
}

Write-Host "   📊 Configuration: $configuredVars/$totalVars environment variables set" -ForegroundColor White

# ===== 7. SECURITY & PERFORMANCE =====
Write-Host ""
Write-Host "7️⃣  SECURITY & PERFORMANCE" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

# Test CORS headers
try {
    $corsTest = Invoke-WebRequest -Uri "$ApiBase/health" -Method OPTIONS -TimeoutSec 5
    if ($corsTest.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "   ✅ CORS headers present" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  CORS headers missing" -ForegroundColor Yellow
        $script:warnings += "CORS headers not detected"
    }
} catch {
    Write-Host "   ⚠️  CORS test failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test response times
if ($detailedHealthResponse) {
    $avgLatency = 0
    $serviceCount = 0
    
    if ($detailedHealthResponse.services) {
        foreach ($service in $detailedHealthResponse.services.PSObject.Properties) {
            $latency = $service.Value.latency_ms
            if ($null -ne $latency) {
                $avgLatency += $latency
                $serviceCount++
            }
        }
        
        if ($serviceCount -gt 0) {
            $avgLatency = $avgLatency / $serviceCount
            if ($avgLatency -lt 500) {
                Write-Host "   ✅ Average response time: $([math]::Round($avgLatency, 2))ms (Good)" -ForegroundColor Green
            } elseif ($avgLatency -lt 1000) {
                Write-Host "   ⚠️  Average response time: $([math]::Round($avgLatency, 2))ms (Acceptable)" -ForegroundColor Yellow
            } else {
                Write-Host "   ❌ Average response time: $([math]::Round($avgLatency, 2))ms (Slow)" -ForegroundColor Red
                $script:warnings += "High response latency detected"
            }
        }
    }
}

# ===== PRODUCTION READINESS ASSESSMENT =====
Write-Host ""
Write-Host "📊 PRODUCTION READINESS ASSESSMENT" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta

$totalTests = $testResults.Count
$passedTests = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failedTests = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$criticalFailures = ($testResults | Where-Object { $_.Status -eq "FAIL" -and $_.Critical }).Count

Write-Host ""
Write-Host "Test Results: $passedTests passed, $failedTests failed (of $totalTests total)" -ForegroundColor White
Write-Host "Critical Failures: $criticalFailures" -ForegroundColor $(if ($criticalFailures -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $($warnings.Count)" -ForegroundColor $(if ($warnings.Count -eq 0) { "Green" } elseif ($warnings.Count -lt 5) { "Yellow" } else { "Red" })

# Production Readiness Verdict
Write-Host ""
if ($criticalFailures -eq 0 -and $failedTests -eq 0) {
    Write-Host "🎯 PRODUCTION READY - All tests passed!" -ForegroundColor Green
    Write-Host "   ✅ Core functionality working" -ForegroundColor Green
    Write-Host "   ✅ No critical failures" -ForegroundColor Green
    Write-Host "   🚀 Safe to deploy to production" -ForegroundColor Green
    $readinessStatus = "READY"
} elseif ($criticalFailures -eq 0) {
    Write-Host "⚠️  PRODUCTION READY WITH WARNINGS" -ForegroundColor Yellow
    Write-Host "   ✅ Core functionality working" -ForegroundColor Green
    Write-Host "   ⚠️  $failedTests non-critical test failures" -ForegroundColor Yellow
    Write-Host "   🚀 Safe to deploy with monitoring" -ForegroundColor Yellow
    $readinessStatus = "READY_WITH_WARNINGS"
} else {
    Write-Host "❌ NOT PRODUCTION READY" -ForegroundColor Red
    Write-Host "   ❌ $criticalFailures critical failures detected" -ForegroundColor Red
    Write-Host "   🛑 DO NOT DEPLOY until critical issues are resolved" -ForegroundColor Red
    $readinessStatus = "NOT_READY"
}

# Critical Issues
if ($criticalIssues.Count -gt 0) {
    Write-Host ""
    Write-Host "🚨 CRITICAL ISSUES (MUST FIX):" -ForegroundColor Red
    foreach ($issue in $criticalIssues) {
        Write-Host "   ❌ $issue" -ForegroundColor Red
    }
}

# Warnings
if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  WARNINGS (RECOMMENDED TO FIX):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "   ⚠️  $warning" -ForegroundColor Yellow
    }
}

# Recommendations
Write-Host ""
Write-Host "💡 RECOMMENDATIONS:" -ForegroundColor Cyan
if ($configuredVars -lt $totalVars) {
    Write-Host "   🔧 Configure missing environment variables for full functionality" -ForegroundColor Cyan
}
if ($SkipCredentialTests) {
    Write-Host "   🔑 Set up database and AI provider credentials for complete testing" -ForegroundColor Cyan
}
Write-Host "   📊 Monitor /health/detailed endpoint for service health" -ForegroundColor Cyan
Write-Host "   🔍 Use /api/metrics/snapshot for operational metrics" -ForegroundColor Cyan
Write-Host "   💰 Monitor /api/costs/actual for AI usage costs" -ForegroundColor Cyan

# Save results
$reportPath = "production_readiness_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report = @{
    timestamp = (Get-Date).ToString("o")
    api_base = $ApiBase
    readiness_status = $readinessStatus
    test_results = $testResults
    summary = @{
        total_tests = $totalTests
        passed = $passedTests
        failed = $failedTests
        critical_failures = $criticalFailures
        warnings_count = $warnings.Count
        configuration_score = "$configuredVars/$totalVars"
    }
    critical_issues = $criticalIssues
    warnings = $warnings
}

try {
    $report | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host ""
    Write-Host "📄 Production readiness report saved: $reportPath" -ForegroundColor Gray
} catch {
    Write-Host ""
    Write-Host "⚠️  Could not save report: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Production readiness test complete!" -ForegroundColor Blue

# Exit with appropriate code
if ($readinessStatus -eq "READY") {
    exit 0
} elseif ($readinessStatus -eq "READY_WITH_WARNINGS") {
    exit 1
} else {
    exit 2
}
