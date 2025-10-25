# ClauseBot OpenAPI Validation & Security Scan
# Comprehensive API quality gate with audit trail integration
# Validates spec conformance, quality, and dynamic security testing

param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$OutDir = ".\docs",
  [string]$AuditDir = "G:\ClauseBot_OPPS_Workspace\Windsurf\audit_trails",
  [int]$HardFailScore = 1,  # fail pipeline if ≥1 critical error found
  [switch]$SkipDynamic = $false,  # skip schemathesis for faster runs
  [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 ClauseBot OpenAPI Validation & Security Scan" -ForegroundColor Blue
Write-Host "===============================================" -ForegroundColor Blue
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host "Output Dir: $OutDir" -ForegroundColor Gray
Write-Host "Audit Dir: $AuditDir" -ForegroundColor Gray
Write-Host ""

# Create directories
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $AuditDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$specJson = Join-Path $OutDir "openapi_$stamp.json"
$specYaml = Join-Path $OutDir "openapi_$stamp.yaml"
$auditJson = Join-Path $AuditDir "openapi_audit_$stamp.json"

function Write-VerboseLog($Message) {
    if ($Verbose) {
        Write-Host "   $Message" -ForegroundColor Gray
    }
}

# Step 1: Fetch OpenAPI spec
Write-Host "📥 Fetching OpenAPI spec from $BaseUrl/openapi.json" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/openapi.json" -TimeoutSec 10
    $response | ConvertTo-Json -Depth 20 | Out-File $specJson -Encoding UTF8
    Write-VerboseLog "Spec saved to $specJson"
} catch {
    Write-Host "❌ Failed to fetch OpenAPI spec: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Convert JSON to YAML (optional, for better readability)
Write-Host "🔄 Converting JSON to YAML format" -ForegroundColor Cyan
$py = @"
import sys, json, yaml
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    print("✅ YAML conversion successful")
except Exception as e:
    print(f"⚠️  YAML conversion failed: {e}")
    sys.exit(0)  # Non-fatal
"@
$pyFile = Join-Path $OutDir "json2yaml_$stamp.py"
$py | Out-File $pyFile -Encoding UTF8

try {
    python "$pyFile" "$specJson" "$specYaml"
    Write-VerboseLog "YAML spec saved to $specYaml"
} catch {
    Write-Host "⚠️  YAML conversion failed (non-fatal): $($_.Exception.Message)" -ForegroundColor Yellow
    $specYaml = $specJson  # Fallback to JSON
}

# Step 3: Ensure validation tools are installed
Write-Host "🔧 Ensuring validation tools are installed" -ForegroundColor Cyan
Write-VerboseLog "Installing Python packages..."
try {
    pip install --quiet openapi-spec-validator schemathesis pyyaml 2>$null
} catch {
    Write-Host "⚠️  Some Python packages may not be available" -ForegroundColor Yellow
}

Write-VerboseLog "Checking Spectral CLI..."
try {
    npm list -g @stoplight/spectral-cli 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-VerboseLog "Installing Spectral CLI..."
        npm install -g @stoplight/spectral-cli | Out-Null
    } else {
        Write-VerboseLog "Spectral CLI already installed"
    }
} catch {
    Write-Host "⚠️  Spectral CLI installation may have failed" -ForegroundColor Yellow
}

# Step 4: Static Audit - Conformance & Quality
Write-Host "📋 Static audit via Spectral and OpenAPI Spec Validator" -ForegroundColor Cyan
$spectralOut = Join-Path $OutDir "spectral_$stamp.txt"
$spectralJson = Join-Path $OutDir "spectral_$stamp.json"

# Run Spectral
try {
    Write-VerboseLog "Running Spectral linter..."
    spectral lint "$specYaml" --format json --output "$spectralJson" 2>$null
    spectral lint "$specYaml" | Tee-Object -FilePath $spectralOut
    
    # Parse Spectral results
    if (Test-Path $spectralJson) {
        $spectralResults = Get-Content $spectralJson | ConvertFrom-Json
        $errors = ($spectralResults | Where-Object { $_.severity -eq 0 }).Count
        $warns = ($spectralResults | Where-Object { $_.severity -eq 1 }).Count
        $infos = ($spectralResults | Where-Object { $_.severity -eq 2 }).Count
    } else {
        # Fallback: parse text output
        $errors = (Select-String -Path $spectralOut -Pattern "\berror\b" -ErrorAction SilentlyContinue).Count
        $warns = (Select-String -Path $spectralOut -Pattern "\bwarn\b" -ErrorAction SilentlyContinue).Count
        $infos = (Select-String -Path $spectralOut -Pattern "\binfo\b" -ErrorAction SilentlyContinue).Count
    }
} catch {
    Write-Host "⚠️  Spectral analysis failed: $($_.Exception.Message)" -ForegroundColor Yellow
    $errors = 999
    $warns = 0
    $infos = 0
}

# Run OpenAPI Spec Validator
$specValidateOk = $true
try {
    Write-VerboseLog "Running OpenAPI Spec Validator..."
    python -c "from openapi_spec_validator import validate_spec;import json,sys;validate_spec(json.load(open('$specJson','r',encoding='utf-8')))"
    Write-VerboseLog "✅ OpenAPI spec validation passed"
} catch {
    $specValidateOk = $false
    Write-VerboseLog "❌ OpenAPI spec validation failed"
}

# Step 5: Dynamic Scan - Conformance & Security (optional)
$stExit = 0
$stOut = Join-Path $OutDir "schemathesis_$stamp.txt"

if (-not $SkipDynamic) {
    Write-Host "🔍 Dynamic scan via Schemathesis (testing live API)" -ForegroundColor Cyan
    $schemaUrl = "$BaseUrl/openapi.json"
    
    try {
        Write-VerboseLog "Running Schemathesis against $schemaUrl..."
        # Run with timeout and limited checks for faster execution
        schemathesis run "$schemaUrl" --base-url "$BaseUrl" --checks=all --hypothesis-seed=1 `
            --validate-schema --max-examples=10 --hypothesis-deadline=5000 > "$stOut" 2>&1
        $stExit = $LASTEXITCODE
        Write-VerboseLog "Schemathesis completed with exit code: $stExit"
    } catch {
        Write-Host "⚠️  Schemathesis scan failed: $($_.Exception.Message)" -ForegroundColor Yellow
        $stExit = 1
    }
} else {
    Write-Host "⏭️  Skipping dynamic scan (--SkipDynamic specified)" -ForegroundColor Yellow
    "Dynamic scan skipped by user request" | Out-File $stOut -Encoding UTF8
}

# Step 6: Generate comprehensive audit report
Write-Host "📊 Generating audit report" -ForegroundColor Cyan

$result = [ordered]@{
    metadata = @{
        timestamp = (Get-Date).ToString("o")
        clausebot_version = "1.0.0"
        audit_type = "openapi_validation"
        base_url = $BaseUrl
        validator_version = "1.0"
    }
    files = @{
        spec_json = (Resolve-Path $specJson -ErrorAction SilentlyContinue)?.Path
        spec_yaml = if (Test-Path $specYaml) { (Resolve-Path $specYaml).Path } else { $null }
        spectral_output = (Resolve-Path $spectralOut -ErrorAction SilentlyContinue)?.Path
        schemathesis_output = (Resolve-Path $stOut -ErrorAction SilentlyContinue)?.Path
    }
    static_audit = @{
        spectral = @{
            errors = $errors
            warnings = $warns
            infos = $infos
            total_issues = $errors + $warns + $infos
        }
        openapi_spec_validator = @{
            passed = $specValidateOk
            status = if ($specValidateOk) { "PASS" } else { "FAIL" }
        }
    }
    dynamic_scan = @{
        enabled = -not $SkipDynamic
        tool = "schemathesis"
        exit_code = $stExit
        status = if ($stExit -eq 0) { "PASS" } else { "FAIL" }
    }
    overall_assessment = @{
        status = "PASS"
        score = 0
        critical_issues = 0
        reason = ""
        recommendations = @()
    }
}

# Calculate overall status
$criticalIssues = 0
$recommendations = @()

if (-not $specValidateOk) { 
    $criticalIssues += 1
    $recommendations += "Fix OpenAPI spec validation errors"
}
if ($errors -ge $HardFailScore) { 
    $criticalIssues += 1 
    $recommendations += "Resolve Spectral errors (found: $errors)"
}
if ($stExit -ne 0 -and -not $SkipDynamic) { 
    $criticalIssues += 1
    $recommendations += "Fix dynamic scan failures"
}

$result.overall_assessment.critical_issues = $criticalIssues
$result.overall_assessment.recommendations = $recommendations

if ($criticalIssues -gt 0) {
    $result.overall_assessment.status = "FAIL"
    $result.overall_assessment.reason = "Critical issues found requiring attention"
    $result.overall_assessment.score = [math]::Max(0, 100 - ($criticalIssues * 25))
} else {
    $result.overall_assessment.status = "PASS"
    $result.overall_assessment.reason = "All validation checks passed"
    $result.overall_assessment.score = [math]::Max(75, 100 - ($warns * 2) - ($infos * 1))
}

# Save audit report
($result | ConvertTo-Json -Depth 10) | Out-File $auditJson -Encoding UTF8

# Step 7: Display summary
Write-Host ""
Write-Host "📊 ClauseBot OpenAPI Audit Summary" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow
Write-Host "Static Analysis:" -ForegroundColor White
Write-Host "  Spectral: $errors errors, $warns warnings, $infos infos" -ForegroundColor White
Write-Host "  Spec Validator: $(if ($specValidateOk) { '✅ PASS' } else { '❌ FAIL' })" -ForegroundColor White
Write-Host "Dynamic Scan:" -ForegroundColor White
Write-Host "  Schemathesis: $(if ($SkipDynamic) { 'SKIPPED' } elseif ($stExit -eq 0) { '✅ PASS' } else { '❌ FAIL' })" -ForegroundColor White
Write-Host ""
Write-Host "Overall Status: $($result.overall_assessment.status)" -ForegroundColor $(if ($result.overall_assessment.status -eq "PASS") { "Green" } else { "Red" })
Write-Host "Quality Score: $($result.overall_assessment.score)/100" -ForegroundColor White
Write-Host "Critical Issues: $criticalIssues" -ForegroundColor White

if ($recommendations.Count -gt 0) {
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Yellow
    foreach ($rec in $recommendations) {
        Write-Host "  • $rec" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Audit Report: $auditJson" -ForegroundColor Cyan
Write-Host "Spec Files: $specJson" -ForegroundColor Cyan
Write-Host ""

# Exit with appropriate code
if ($result.overall_assessment.status -ne "PASS") { 
    Write-Host "🚨 Validation failed - see issues above" -ForegroundColor Red
    exit 2 
} else {
    Write-Host "✅ All validations passed!" -ForegroundColor Green
    exit 0
}
