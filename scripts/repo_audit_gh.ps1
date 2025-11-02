#!/usr/bin/env pwsh
# Repo audit script using GitHub CLI (gh api)
# Uses authenticated gh CLI instead of PAT tokens

$ErrorActionPreference = "Stop"

# Repository list - all repos to audit
$REPOS = @(
    "miltmon/clausebot-api",
    "miltmon/clausebotai", 
    "miltmon/clausebot",
    "miltmon/gemini-2-0-flash-image-generation-and-editing",
    "miltmon/wix-classes-subscriptions",
    "miltmon/nextjs-commerce",
    "miltmon/nextjs-ai-chatbot",
    "miltmon/clausebot.ai-answer-engine-generative-ui",
    "miltmon/awsbokphoneapp",
    "miltmon/idletime-herb-vault",
    "miltmon/table-id-helper",
    "miltmon/WeldMap-",
    "miltmon/456-three-dice",
    "miltmon/rgs-family-connect"
)

# External service configuration
$SUPABASE_URL = $env:SUPABASE_URL
if (-not $SUPABASE_URL) { $SUPABASE_URL = "https://hqhughgdraokwmreronk.supabase.co" }
$AIRTABLE_API_KEY = $env:AIRTABLE_API_KEY

# Output setup
$OUTDIR = "repo_audit_output"
if (-not (Test-Path $OUTDIR)) { New-Item -ItemType Directory -Path $OUTDIR | Out-Null }

$timestamp = (Get-Date -Format "yyyyMMddTHHmmssZ" -AsUTC)
$report_file = "$OUTDIR/repo-audit-$timestamp.json"

Write-Host "🔍 Starting repository audit at $timestamp" -ForegroundColor Cyan
Write-Host "   Scanning $($REPOS.Count) repositories..." -ForegroundColor Gray

# Initialize JSON report
$report = @{
    generated_at = $timestamp
    audit_version = "1.0.0"
    external_services = @{}
    repos = @{}
}

################################################################################
# External Service Checks
################################################################################

Write-Host "📡 Checking external services..." -ForegroundColor Cyan

# Supabase health check
$supabase_status = 0
$supabase_response_time = 0
if ($SUPABASE_URL) {
    $start_time = Get-Date
    try {
        $response = Invoke-WebRequest -Uri "$SUPABASE_URL/rest/v1/" -TimeoutSec 10 -UseBasicParsing
        $supabase_status = $response.StatusCode
        $end_time = Get-Date
        $supabase_response_time = [int](($end_time - $start_time).TotalMilliseconds)
        Write-Host "   ✅ Supabase: reachable ($supabase_response_time ms)" -ForegroundColor Green
    } catch {
        $supabase_status = 0
        Write-Host "   ⚠️  Supabase: unreachable or timeout" -ForegroundColor Yellow
    }
}

$report.external_services.supabase = @{
    url = $SUPABASE_URL
    status = $supabase_status
    response_time_ms = $supabase_response_time
}

# Airtable API check
$airtable_status = 0
$airtable_response_time = 0
$start_time = Get-Date
if ($AIRTABLE_API_KEY) {
    try {
        $headers = @{ Authorization = "Bearer $AIRTABLE_API_KEY" }
        $response = Invoke-WebRequest -Uri "https://api.airtable.com/v0/meta/bases" -Headers $headers -TimeoutSec 10 -UseBasicParsing
        $airtable_status = $response.StatusCode
        $end_time = Get-Date
        $airtable_response_time = [int](($end_time - $start_time).TotalMilliseconds)
        Write-Host "   ✅ Airtable: authenticated & reachable ($airtable_response_time ms)" -ForegroundColor Green
    } catch {
        $airtable_status = 401
        Write-Host "   ⚠️  Airtable: auth failed or unreachable" -ForegroundColor Yellow
    }
} else {
    try {
        $response = Invoke-WebRequest -Uri "https://api.airtable.com" -TimeoutSec 10 -UseBasicParsing
        $airtable_status = $response.StatusCode
        $end_time = Get-Date
        $airtable_response_time = [int](($end_time - $start_time).TotalMilliseconds)
        Write-Host "   ✅ Airtable: reachable (unauthenticated ping, $airtable_response_time ms)" -ForegroundColor Green
    } catch {
        $airtable_status = 0
        Write-Host "   ⚠️  Airtable: unreachable" -ForegroundColor Yellow
    }
}

$report.external_services.airtable = @{
    url = "https://api.airtable.com"
    authenticated = ($null -ne $AIRTABLE_API_KEY)
    status = $airtable_status
    response_time_ms = $airtable_response_time
}

################################################################################
# Repository Checks
################################################################################

Write-Host "" 
Write-Host "📚 Scanning repositories..." -ForegroundColor Cyan

foreach ($repo in $REPOS) {
    Write-Host "   Scanning: $repo" -ForegroundColor Gray
    
    $repo_data = @{}
    
    # 1. Collaborators & permissions
    try {
        $collab_json = gh api "/repos/$repo/collaborators" --jq '.' | ConvertFrom-Json
        $repo_data.collaborators = $collab_json
    } catch {
        $repo_data.collaborators = @()
    }
    
    # 2. Webhooks
    try {
        $hooks_json = gh api "/repos/$repo/hooks" --jq '.' | ConvertFrom-Json
        $repo_data.webhooks = $hooks_json
    } catch {
        $repo_data.webhooks = @()
    }
    
    # 3. Actions secrets (list names only)
    try {
        $secrets_json = gh api "/repos/$repo/actions/secrets" --jq '.' | ConvertFrom-Json
        $repo_data.actions_secrets = $secrets_json
    } catch {
        $repo_data.actions_secrets = @{ secrets = @() }
    }
    
    # 4. Latest workflow run
    try {
        $runs_json = gh api "/repos/$repo/actions/runs?per_page=1" --jq '.' | ConvertFrom-Json
        $repo_data.latest_workflow_run = $runs_json
    } catch {
        $repo_data.latest_workflow_run = @{ workflow_runs = @() }
    }
    
    $report.repos[$repo] = $repo_data
}

################################################################################
# Write Report
################################################################################

$json_output = $report | ConvertTo-Json -Depth 10
$json_output | Out-File -FilePath $report_file -Encoding UTF8

Write-Host ""
Write-Host "✅ Audit complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📄 Report written to: $report_file" -ForegroundColor Cyan
Get-ChildItem $report_file | Format-Table Name, Length, LastWriteTime
Write-Host ""
Write-Host "💡 Query examples:" -ForegroundColor Yellow
Write-Host "   Get-Content '$report_file' | ConvertFrom-Json | Select-Object -ExpandProperty external_services"
Write-Host "   Get-Content '$report_file' | ConvertFrom-Json | Select-Object -ExpandProperty repos | Get-Member"

exit 0
