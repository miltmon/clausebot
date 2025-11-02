Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$REPOS = @(
  "miltmon/clausebot-api","miltmon/clausebotai","miltmon/clausebot",
  "miltmon/gemini-2-0-flash-image-generation-and-editing",
  "miltmon/wix-classes-subscriptions","miltmon/nextjs-commerce",
  "miltmon/nextjs-ai-chatbot","miltmon/clausebot.ai-answer-engine-generative-ui",
  "miltmon/awsbokphoneapp","miltmon/idletime-herb-vault",
  "miltmon/table-id-helper","miltmon/WeldMap-","miltmon/456-three-dice",
  "miltmon/rgs-family-connect"
)
$OutDir = Join-Path -Path (Get-Location) -ChildPath "repo_audit_output"
if (-not (Test-Path $OutDir)) { New-Item -Path $OutDir -ItemType Directory | Out-Null }
$timestamp = (Get-Date).ToString("yyyyMMddTHHmmssZ")
$reportFile = Join-Path $OutDir ("repo-audit-$timestamp.json")
$SupabaseUrl = $env:SUPABASE_URL
if (-not $SupabaseUrl) { $SupabaseUrl = "https://hqhughgdraokwmreronk.supabase.co" }
$AirtableKey = $env:AIRTABLE_API_KEY
function Test-Head($uri) {
  try { $r = Invoke-WebRequest -Uri $uri -Method Head -TimeoutSec 10 -ErrorAction Stop; return @{ status = $r.StatusCode; ok = $true } }
  catch { return @{ status = 0; ok = $false; error = $_.Exception.Message } }
}
$external = @{}
$supRes = Test-Head -uri ("{0}/rest/v1/" -f $SupabaseUrl)
$external.supabase = @{ url = $SupabaseUrl; status = $supRes.status }
if ($AirtableKey) {
  try { $r = Invoke-RestMethod -Uri "https://api.airtable.com/v0/meta/bases" -Headers @{ Authorization = "Bearer $AirtableKey" } -Method Get -TimeoutSec 10 -ErrorAction Stop; $external.airtable = @{ url = "https://api.airtable.com"; authenticated = $true; status = 200 } }
  catch { $external.airtable = @{ url = "https://api.airtable.com"; authenticated = $false; status = 401; error = $_.Exception.Message } }
} else {
  $ping = Test-Head -uri "https://api.airtable.com"
  $external.airtable = @{ url = "https://api.airtable.com"; authenticated = $false; status = $ping.status }
}
if (-not $env:GITHUB_API_TOKEN) { Write-Error "GITHUB_API_TOKEN not set in this session."; exit 2 }
$headers = @{ Authorization = "token $env:GITHUB_API_TOKEN"; "User-Agent" = "repo-audit-ps" }
$reposObj = @{}
foreach ($repo in $REPOS) {
  Write-Host "Scanning $repo" -ForegroundColor Cyan
  $repoObj = @{}
  try { $collabUri = "https://api.github.com/repos/$repo/collaborators"; $collab = Invoke-RestMethod -Uri $collabUri -Headers $headers -Method Get -ErrorAction Stop; $repoObj.collaborators = $collab | ForEach-Object { @{ login = $_.login; id = $_.id } } } catch { $repoObj.collaborators = @(); $repoObj._collab_error = $_.Exception.Message }
  try { $hooksUri = "https://api.github.com/repos/$repo/hooks"; $hooks = Invoke-RestMethod -Uri $hooksUri -Headers $headers -Method Get -ErrorAction Stop; $repoObj.webhooks = $hooks | ForEach-Object { @{ id = $_.id; url = $_.config.url } } } catch { $repoObj.webhooks = @(); $repoObj._hooks_error = $_.Exception.Message }
  try { $secretsUri = "https://api.github.com/repos/$repo/actions/secrets"; $secrets = Invoke-RestMethod -Uri $secretsUri -Headers $headers -Method Get -ErrorAction Stop; $repoObj.actions_secrets = $secrets } catch { $repoObj.actions_secrets = @{ secrets = @() }; $repoObj._secrets_error = $_.Exception.Message }
  try { $runsUri = "https://api.github.com/repos/$repo/actions/runs?per_page=1"; $runs = Invoke-RestMethod -Uri $runsUri -Headers $headers -Method Get -ErrorAction Stop; $repoObj.latest_workflow_run = $runs } catch { $repoObj.latest_workflow_run = @{ workflow_runs = @() }; $repoObj._runs_error = $_.Exception.Message }
  $reposObj[$repo] = $repoObj
}
$final = @{ generated_at = (Get-Date).ToString("u"); audit_version = "1.0.0-ps"; external_services = $external; repos = $reposObj }
$final | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding utf8
Write-Host "✅ Audit complete. File written to: $reportFile" -ForegroundColor Green
