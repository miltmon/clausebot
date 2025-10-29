#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ClauseBot Vercel Cache Audit & Validation Script
.DESCRIPTION
    Validates cache headers, monitors cache performance, and generates compliance reports
    for ClauseBot's Vercel deployment.
.PARAMETER Url
    Base URL to audit (default: https://clausebot.vercel.app)
.PARAMETER GenerateReport
    Generate detailed compliance report
.PARAMETER CheckCompliance
    Run full compliance validation
.EXAMPLE
    .\cache-audit.ps1
    .\cache-audit.ps1 -Url https://clausebot.vercel.app -GenerateReport
    .\cache-audit.ps1 -CheckCompliance
#>

param(
    [string]$Url = "https://clausebot.vercel.app",
    [switch]$GenerateReport,
    [switch]$CheckCompliance
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ANSI Colors
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

Write-Host "${Blue}╔════════════════════════════════════════════════════════════╗${Reset}"
Write-Host "${Blue}║   ClauseBot Vercel Cache Audit & Compliance Validator     ║${Reset}"
Write-Host "${Blue}╚════════════════════════════════════════════════════════════╝${Reset}"
Write-Host ""

# Test endpoints with expected cache behavior
$testEndpoints = @(
    @{
        Path = "/"
        ExpectedCacheControl = "public, max-age=0, must-revalidate"
        ExpectedCDN = $null
        Description = "Root HTML"
        ShouldCache = $false
    },
    @{
        Path = "/health"
        ExpectedCacheControl = "public, max-age=30, stale-while-revalidate=30"
        ExpectedCDN = "public, max-age=30, stale-while-revalidate=30"
        Description = "Health endpoint"
        ShouldCache = $true
    },
    @{
        Path = "/buildinfo"
        ExpectedCacheControl = "public, max-age=60, stale-while-revalidate=60"
        ExpectedCDN = "public, max-age=60, stale-while-revalidate=60"
        Description = "Build info endpoint"
        ShouldCache = $true
    },
    @{
        Path = "/assets/clausebot-badge.png"
        ExpectedCacheControl = "public, max-age=31536000, immutable"
        ExpectedCDN = "public, max-age=31536000, immutable"
        Description = "Static asset"
        ShouldCache = $true
    }
)

$results = @()
$passCount = 0
$failCount = 0
$warnings = @()

Write-Host "${Yellow}🔍 Testing cache headers for $($testEndpoints.Count) endpoints...${Reset}`n"

foreach ($endpoint in $testEndpoints) {
    $fullUrl = "$Url$($endpoint.Path)"
    Write-Host "Testing: ${Blue}$($endpoint.Path)${Reset} - $($endpoint.Description)"
    
    try {
        $response = Invoke-WebRequest -Uri $fullUrl -Method HEAD -UseBasicParsing -ErrorAction SilentlyContinue
        
        $cacheControl = $response.Headers['Cache-Control'] -join ', '
        $cdnCacheControl = $response.Headers['CDN-Cache-Control'] -join ', '
        $vercelCdnCacheControl = $response.Headers['Vercel-CDN-Cache-Control'] -join ', '
        $xVercelCache = $response.Headers['x-vercel-cache'] -join ', '
        
        $result = @{
            Path = $endpoint.Path
            Description = $endpoint.Description
            StatusCode = $response.StatusCode
            CacheControl = $cacheControl
            CDNCacheControl = $cdnCacheControl
            VercelCDNCacheControl = $vercelCdnCacheControl
            XVercelCache = $xVercelCache
            ExpectedCacheControl = $endpoint.ExpectedCacheControl
            ExpectedCDN = $endpoint.ExpectedCDN
            Pass = $true
            Issues = @()
        }
        
        # Validate Cache-Control
        if ($endpoint.ExpectedCacheControl -and $cacheControl -ne $endpoint.ExpectedCacheControl) {
            $result.Pass = $false
            $result.Issues += "Cache-Control mismatch: Expected '$($endpoint.ExpectedCacheControl)', Got '$cacheControl'"
        }
        
        # Validate CDN-Cache-Control
        if ($endpoint.ExpectedCDN -and $cdnCacheControl -ne $endpoint.ExpectedCDN) {
            $result.Pass = $false
            $result.Issues += "CDN-Cache-Control mismatch: Expected '$($endpoint.ExpectedCDN)', Got '$cdnCacheControl'"
        }
        
        # Check for cache status
        if ($xVercelCache) {
            Write-Host "  ${Green}✓${Reset} Cache Status: ${Blue}$xVercelCache${Reset}"
        } else {
            Write-Host "  ${Yellow}⚠${Reset} No x-vercel-cache header (may be normal for first request)"
        }
        
        if ($result.Pass) {
            Write-Host "  ${Green}✓ PASS${Reset} - Headers correct"
            $passCount++
        } else {
            Write-Host "  ${Red}✗ FAIL${Reset} - Issues found:"
            foreach ($issue in $result.Issues) {
                Write-Host "    ${Red}•${Reset} $issue"
            }
            $failCount++
        }
        
        $results += $result
    }
    catch {
        Write-Host "  ${Red}✗ ERROR${Reset} - $($_.Exception.Message)"
        $failCount++
        $results += @{
            Path = $endpoint.Path
            Description = $endpoint.Description
            StatusCode = 0
            Pass = $false
            Issues = @("Request failed: $($_.Exception.Message)")
        }
    }
    
    Write-Host ""
}

# Security Headers Check
Write-Host "${Yellow}🔒 Validating security headers...${Reset}`n"

try {
    $response = Invoke-WebRequest -Uri $Url -Method HEAD -UseBasicParsing
    
    $securityHeaders = @{
        'X-Content-Type-Options' = 'nosniff'
        'X-Frame-Options' = 'DENY'
        'X-XSS-Protection' = '1; mode=block'
        'Content-Security-Policy' = $true  # Just check it exists
    }
    
    foreach ($header in $securityHeaders.Keys) {
        $value = $response.Headers[$header] -join ', '
        if ($value) {
            if ($securityHeaders[$header] -is [bool]) {
                Write-Host "  ${Green}✓${Reset} $header present"
            } elseif ($value -eq $securityHeaders[$header]) {
                Write-Host "  ${Green}✓${Reset} $header = $value"
            } else {
                Write-Host "  ${Yellow}⚠${Reset} $header = $value (expected: $($securityHeaders[$header]))"
                $warnings += "$header mismatch"
            }
        } else {
            Write-Host "  ${Red}✗${Reset} $header MISSING"
            $warnings += "$header missing"
        }
    }
    
    # Check CSP for WebSocket support
    $csp = $response.Headers['Content-Security-Policy'] -join ', '
    if ($csp -match 'wss://') {
        Write-Host "  ${Green}✓${Reset} WebSocket (wss://) allowed in CSP"
    } else {
        Write-Host "  ${Yellow}⚠${Reset} WebSocket (wss://) not found in CSP (may be added later)"
        $warnings += "WebSocket not in CSP"
    }
}
catch {
    Write-Host "  ${Red}✗ ERROR${Reset} - Failed to check security headers: $($_.Exception.Message)"
}

Write-Host ""

# Summary
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host "${Blue}  AUDIT SUMMARY${Reset}"
Write-Host "${Blue}═══════════════════════════════════════════════════════${Reset}"
Write-Host "  Passed:  ${Green}$passCount${Reset}"
Write-Host "  Failed:  ${Red}$failCount${Reset}"
Write-Host "  Warnings: ${Yellow}$($warnings.Count)${Reset}"

if ($warnings.Count -gt 0) {
    Write-Host "`n${Yellow}⚠ Warnings:${Reset}"
    foreach ($warning in $warnings) {
        Write-Host "  • $warning"
    }
}

# Compliance Check
if ($CheckCompliance) {
    Write-Host "`n${Yellow}📋 Running compliance validation...${Reset}`n"
    
    $complianceChecks = @{
        'Cache Policy Documented' = Test-Path "docs\VERCEL_CACHE_STRATEGY_SOP.md"
        'vercel.json Configured' = Test-Path "frontend\vercel.json"
        'All Tests Pass' = ($failCount -eq 0)
        'Security Headers Present' = ($warnings.Count -eq 0)
    }
    
    foreach ($check in $complianceChecks.Keys) {
        if ($complianceChecks[$check]) {
            Write-Host "  ${Green}✓${Reset} $check"
        } else {
            Write-Host "  ${Red}✗${Reset} $check"
        }
    }
    
    if ($complianceChecks.Values -notcontains $false) {
        Write-Host "`n${Green}✓ COMPLIANCE: PASSED${Reset}"
    } else {
        Write-Host "`n${Red}✗ COMPLIANCE: FAILED${Reset}"
    }
}

# Generate Report
if ($GenerateReport) {
    Write-Host "`n${Yellow}📊 Generating compliance report...${Reset}"
    
    $reportPath = "cache-audit-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report = @{
        timestamp = (Get-Date).ToString('o')
        url = $Url
        summary = @{
            total_tests = $testEndpoints.Count
            passed = $passCount
            failed = $failCount
            warnings = $warnings.Count
        }
        results = $results
        warnings = $warnings
        compliance_status = if ($failCount -eq 0 -and $warnings.Count -eq 0) { 'PASS' } else { 'FAIL' }
    }
    
    $report | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding utf8
    Write-Host "${Green}✓${Reset} Report saved to: $reportPath"
}

Write-Host ""

# Exit code
if ($failCount -gt 0) {
    Write-Host "${Red}❌ Audit FAILED - Fix issues before deploying${Reset}"
    exit 1
} elseif ($warnings.Count -gt 0) {
    Write-Host "${Yellow}⚠ Audit PASSED with warnings - Review before production${Reset}"
    exit 0
} else {
    Write-Host "${Green}✅ Audit PASSED - All cache headers correct${Reset}"
    exit 0
}

