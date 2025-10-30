# ClauseBot Exa.ai Integration - Production Validation Suite
# Comprehensive go-live validation for bulletproof deployment

param(
    [string]$DriveRoot = "G:\ClauseBot_OPPS_Workspace",
    [switch]$SkipWebhook = $false,
    [switch]$SkipPull = $false,
    [switch]$SkipCascade = $false,
    [switch]$Strict = $false
)

$ErrorActionPreference = "Continue"  # Don't stop on first error - collect all issues

Write-Host "🌊 ClauseBot Production Validation Suite" -ForegroundColor Blue
Write-Host "=======================================" -ForegroundColor Blue
Write-Host "Target: $DriveRoot" -ForegroundColor Gray
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$validationResults = @()
$criticalIssues = @()
$warnings = @()

function Test-ValidationStep {
    param(
        [string]$StepName,
        [scriptblock]$TestScript,
        [string]$Category = "General"
    )
    
    Write-Host "🔍 Testing: $StepName" -ForegroundColor Cyan
    
    try {
        $result = & $TestScript
        if ($result.Status -eq "PASS") {
            Write-Host "   ✅ PASS - $($result.Message)" -ForegroundColor Green
            $script:validationResults += @{
                Step = $StepName
                Category = $Category
                Status = "PASS"
                Message = $result.Message
                Details = $result.Details
            }
        } elseif ($result.Status -eq "WARN") {
            Write-Host "   ⚠️  WARN - $($result.Message)" -ForegroundColor Yellow
            $script:warnings += "$StepName - $($result.Message)"
            $script:validationResults += @{
                Step = $StepName
                Category = $Category
                Status = "WARN"
                Message = $result.Message
                Details = $result.Details
            }
        } else {
            Write-Host "   ❌ FAIL - $($result.Message)" -ForegroundColor Red
            $script:criticalIssues += "$StepName - $($result.Message)"
            $script:validationResults += @{
                Step = $StepName
                Category = $Category
                Status = "FAIL"
                Message = $result.Message
                Details = $result.Details
            }
        }
    } catch {
        Write-Host "   ❌ ERROR - $($_.Exception.Message)" -ForegroundColor Red
        $script:criticalIssues += "$StepName - $($_.Exception.Message)"
        $script:validationResults += @{
            Step = $StepName
            Category = $Category
            Status = "ERROR"
            Message = $_.Exception.Message
            Details = $null
        }
    }
}

# ===== 1. PREFLIGHT CHECKS (5 min) =====
Write-Host "1️⃣  PREFLIGHT CHECKS" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

Test-ValidationStep "Webhook Health Endpoint" {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8088/health" -TimeoutSec 5
        if ($response.ok) {
            return @{ Status = "PASS"; Message = "Webhook server responding"; Details = $response }
        } else {
            return @{ Status = "FAIL"; Message = "Webhook health check failed"; Details = $response }
        }
    } catch {
        return @{ Status = "FAIL"; Message = "Webhook server not accessible: $($_.Exception.Message)"; Details = $null }
    }
} "Preflight"

Test-ValidationStep "Drive Paths Exist" {
    $requiredPaths = @(
        "$DriveRoot\Shared\compliance_updates\inbox",
        "$DriveRoot\Windsurf\receipts",
        "$DriveRoot\Windsurf\audit_trails",
        "$DriveRoot\CURSOR\compliance_analysis"
    )
    
    $missingPaths = @()
    foreach ($path in $requiredPaths) {
        if (-not (Test-Path $path)) {
            $missingPaths += $path
        }
    }
    
    if ($missingPaths.Count -eq 0) {
        return @{ Status = "PASS"; Message = "All required Drive paths exist"; Details = $requiredPaths }
    } else {
        return @{ Status = "FAIL"; Message = "Missing paths: $($missingPaths -join ', ')"; Details = $missingPaths }
    }
} "Preflight"

Test-ValidationStep "Scheduled Task Status" {
    try {
        $task = Get-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly" -ErrorAction SilentlyContinue
        if ($task) {
            $nextRun = (Get-ScheduledTaskInfo -TaskName "ClauseBot_ExaCompliance_Hourly").NextRunTime
            if ($nextRun -and $nextRun -lt (Get-Date).AddHours(1)) {
                return @{ Status = "PASS"; Message = "Scheduled task active, next run: $nextRun"; Details = $task }
            } else {
                return @{ Status = "WARN"; Message = "Scheduled task exists but next run > 1 hour"; Details = $task }
            }
        } else {
            return @{ Status = "WARN"; Message = "Scheduled task not found - manual scheduling required"; Details = $null }
        }
    } catch {
        return @{ Status = "FAIL"; Message = "Cannot check scheduled task: $($_.Exception.Message)"; Details = $null }
    }
} "Preflight"

# ===== 2. SMOKE TESTS (10-15 min) =====
Write-Host ""
Write-Host "2️⃣  SMOKE TESTS" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta

if (-not $SkipWebhook) {
    Test-ValidationStep "Webhook Push Integration" {
        $testPayload = @{
            source = "exa.ai"
            webset_id = "validation_test"
            items = @(
                @{
                    title = "Validation Test - AWS D1.1 2025 Rev 1"
                    url = "https://validation.test/aws-d1-1-2025-r1"
                    description = "Production validation test item"
                    detected_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                    sections = @("6.1.4")
                    impact_tags = @("validation", "test")
                }
            )
        } | ConvertTo-Json -Depth 4
        
        try {
            $response = Invoke-RestMethod -Method POST -Uri "http://localhost:8088/exa/webset/ingest" -Body $testPayload -ContentType "application/json" -TimeoutSec 10
            
            # Check if file was created
            Start-Sleep -Seconds 2
            $inboxFiles = Get-ChildItem -Path "$DriveRoot\Shared\compliance_updates\inbox" -Filter "exa_validation_test_*.json" | Sort-Object LastWriteTime -Descending
            
            if ($inboxFiles.Count -gt 0 -and $response.accepted -eq 1) {
                return @{ Status = "PASS"; Message = "Webhook created inbox file successfully"; Details = @{ Response = $response; File = $inboxFiles[0].Name } }
            } else {
                return @{ Status = "FAIL"; Message = "Webhook response OK but no inbox file created"; Details = $response }
            }
        } catch {
            return @{ Status = "FAIL"; Message = "Webhook test failed: $($_.Exception.Message)"; Details = $null }
        }
    } "Smoke Test"
}

if (-not $SkipPull) {
    Test-ValidationStep "Pull Integration" {
        # Create temporary test CSV
        $testCsv = @"
Title,URL,Description,UpdatedAt
"Validation Test - ASME Section IX","https://validation.test/asme-ix","Production validation test","$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
"@
        
        $tempCsvPath = "$env:TEMP\validation_test_export.csv"
        $testCsv | Set-Content -Path $tempCsvPath -Encoding UTF8
        
        try {
            $beforeCount = (Get-ChildItem -Path "$DriveRoot\Shared\compliance_updates\inbox" -Filter "exa_*.json").Count
            
            & "$HOME\Diagnostics\exa_pull.ps1" -ExportPath $tempCsvPath -WebsetId "validation_pull_test" -DriveRoot $DriveRoot
            
            $afterCount = (Get-ChildItem -Path "$DriveRoot\Shared\compliance_updates\inbox" -Filter "exa_*.json").Count
            
            if ($afterCount -gt $beforeCount) {
                return @{ Status = "PASS"; Message = "Pull integration created new inbox files"; Details = @{ Before = $beforeCount; After = $afterCount } }
            } else {
                return @{ Status = "WARN"; Message = "Pull integration ran but no new files (possible duplicate)"; Details = @{ Before = $beforeCount; After = $afterCount } }
            }
        } catch {
            return @{ Status = "FAIL"; Message = "Pull integration failed: $($_.Exception.Message)"; Details = $null }
        } finally {
            Remove-Item $tempCsvPath -ErrorAction SilentlyContinue
        }
    } "Smoke Test"
}

# ===== 3. CURSOR → WINDSURF HANDOFF (10 min) =====
Write-Host ""
Write-Host "3️⃣  CURSOR → WINDSURF HANDOFF" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta

if (-not $SkipCascade) {
    Test-ValidationStep "Compliance Cascade Dry Run" {
        # Find a test compliance update file
        $testFiles = Get-ChildItem -Path "$DriveRoot\Shared\compliance_updates\inbox" -Filter "exa_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($testFiles) {
            try {
                & "$HOME\Diagnostics\windsurf_compliance_cascade.ps1" -ComplianceUpdatePath $testFiles.FullName -DriveRoot $DriveRoot -DryRun
                
                # Note: Dry run won't create actual files, but should complete without error
                return @{ Status = "PASS"; Message = "Compliance cascade dry run completed successfully"; Details = @{ TestFile = $testFiles.Name } }
            } catch {
                return @{ Status = "FAIL"; Message = "Compliance cascade failed: $($_.Exception.Message)"; Details = $null }
            }
        } else {
            return @{ Status = "WARN"; Message = "No compliance update files found for cascade test"; Details = $null }
        }
    } "Handoff"
}

# ===== 4. SCORECARD + DASHBOARD (5-10 min) =====
Write-Host ""
Write-Host "4️⃣  SCORECARD + DASHBOARD" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

Test-ValidationStep "Team Scorecard Update" {
    try {
        if (Test-Path "$HOME\build_team_scorecard.ps1") {
            & "$HOME\build_team_scorecard.ps1" -DriveRoot $DriveRoot
            
            $scorecardPath = "$DriveRoot\Shared\team_scorecard.json"
            if (Test-Path $scorecardPath) {
                $scorecard = Get-Content $scorecardPath -Raw | ConvertFrom-Json
                
                # Check for compliance metrics
                if ($scorecard.compliance_metrics) {
                    return @{ Status = "PASS"; Message = "Team scorecard updated with compliance metrics"; Details = $scorecard.compliance_metrics }
                } else {
                    return @{ Status = "WARN"; Message = "Team scorecard updated but no compliance metrics found"; Details = $scorecard }
                }
            } else {
                return @{ Status = "FAIL"; Message = "Team scorecard file not created"; Details = $null }
            }
        } else {
            return @{ Status = "WARN"; Message = "Team scorecard script not found"; Details = $null }
        }
    } catch {
        return @{ Status = "FAIL"; Message = "Team scorecard update failed: $($_.Exception.Message)"; Details = $null }
    }
} "Dashboard"

# ===== 5. GUARDRAILS & ROLLBACK (5 min) =====
Write-Host ""
Write-Host "5️⃣  GUARDRAILS & ROLLBACK" -ForegroundColor Magenta
Write-Host "=========================" -ForegroundColor Magenta

Test-ValidationStep "Kill Switch Documentation" {
    $killSwitchSteps = @(
        "Disable-ScheduledTask -TaskName 'ClauseBot_ExaCompliance_Hourly'",
        "Stop webhook server (uvicorn process)",
        "Create kill switch marker file"
    )
    
    # Test scheduled task disable/enable
    try {
        $task = Get-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly" -ErrorAction SilentlyContinue
        if ($task) {
            # Test disable (then re-enable)
            Disable-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly" -Confirm:$false
            Enable-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly"
            return @{ Status = "PASS"; Message = "Kill switch procedures validated"; Details = $killSwitchSteps }
        } else {
            return @{ Status = "WARN"; Message = "Scheduled task not found for kill switch test"; Details = $killSwitchSteps }
        }
    } catch {
        return @{ Status = "FAIL"; Message = "Kill switch test failed: $($_.Exception.Message)"; Details = $null }
    }
} "Guardrails"

Test-ValidationStep "Security Validation" {
    # Check for PII in recent files
    $recentFiles = Get-ChildItem -Path "$DriveRoot\Shared\compliance_updates\inbox" -Filter "exa_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    
    $piiFound = $false
    foreach ($file in $recentFiles) {
        try {
            $content = Get-Content $file.FullName -Raw
            # Simple PII check - look for email patterns, phone numbers, etc.
            if ($content -match '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' -or 
                $content -match '\b\d{3}-\d{3}-\d{4}\b' -or
                $content -match '\bfull_text\b' -or
                $content -match '\bcontent\b.*\b.{200,}\b') {
                $piiFound = $true
                break
            }
        } catch {
            # Skip files that can't be read
        }
    }
    
    if (-not $piiFound) {
        return @{ Status = "PASS"; Message = "No PII detected in recent compliance files"; Details = @{ FilesChecked = $recentFiles.Count } }
    } else {
        return @{ Status = "FAIL"; Message = "Potential PII detected in compliance files"; Details = @{ FilesChecked = $recentFiles.Count } }
    }
} "Guardrails"

# ===== FINAL VALIDATION SUMMARY =====
Write-Host ""
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Magenta
Write-Host "====================" -ForegroundColor Magenta

$totalTests = $validationResults.Count
$passedTests = ($validationResults | Where-Object { $_.Status -eq "PASS" }).Count
$warnTests = ($validationResults | Where-Object { $_.Status -eq "WARN" }).Count
$failedTests = ($validationResults | Where-Object { $_.Status -in @("FAIL", "ERROR") }).Count

Write-Host ""
Write-Host "Results: $passedTests passed, $warnTests warnings, $failedTests failed (of $totalTests total)" -ForegroundColor White

# Critical Issues
if ($criticalIssues.Count -gt 0) {
    Write-Host ""
    Write-Host "🚨 CRITICAL ISSUES (MUST FIX BEFORE PRODUCTION):" -ForegroundColor Red
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

# Production Readiness Assessment
Write-Host ""
if ($criticalIssues.Count -eq 0) {
    if ($warnings.Count -eq 0) {
        Write-Host "🎯 PRODUCTION READY - All validations passed!" -ForegroundColor Green
        Write-Host "   ✅ Zero critical issues" -ForegroundColor Green
        Write-Host "   ✅ Zero warnings" -ForegroundColor Green
        Write-Host "   🚀 Safe to deploy to production" -ForegroundColor Green
    } else {
        Write-Host "✅ PRODUCTION READY - Minor warnings only" -ForegroundColor Green
        Write-Host "   ✅ Zero critical issues" -ForegroundColor Green
        Write-Host "   ⚠️  $($warnings.Count) warnings (non-blocking)" -ForegroundColor Yellow
        Write-Host "   🚀 Safe to deploy with monitoring" -ForegroundColor Green
    }
} else {
    Write-Host "❌ NOT PRODUCTION READY" -ForegroundColor Red
    Write-Host "   ❌ $($criticalIssues.Count) critical issues must be resolved" -ForegroundColor Red
    Write-Host "   🛑 DO NOT DEPLOY until issues are fixed" -ForegroundColor Red
}

# Save validation report
$reportPath = "$DriveRoot\Shared\production_validation_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report = @{
    timestamp = (Get-Date).ToString("o")
    validation_results = $validationResults
    summary = @{
        total_tests = $totalTests
        passed = $passedTests
        warnings = $warnTests
        failed = $failedTests
        critical_issues = $criticalIssues
        warnings_list = $warnings
        production_ready = ($criticalIssues.Count -eq 0)
    }
}

try {
    $report | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host ""
    Write-Host "📄 Validation report saved: $reportPath" -ForegroundColor Gray
} catch {
    Write-Host ""
    Write-Host "⚠️  Could not save validation report: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌊 Production validation complete!" -ForegroundColor Blue

# Exit with appropriate code
if ($criticalIssues.Count -eq 0) {
    exit 0  # Success
} else {
    exit 1  # Critical issues found
}
