param(
  [string]$BaseId = $env:AIRTABLE_BASE_ID,
  [string]$Table  = $env:AIRTABLE_TABLE,
  [string]$View   = $env:AIRTABLE_VIEW
)

$ErrorActionPreference = "Stop"
function ok($m){ Write-Host "✔ $m" -ForegroundColor Green }
function warn($m){ Write-Host "• $m" -ForegroundColor Yellow }
function fail($m){ Write-Host "✖ $m" -ForegroundColor Red }

# 1) Git sanity
try {
  $top = git rev-parse --show-toplevel 2>$null
  if (-not $top) { fail "Not inside a git repo"; exit 1 }
  Push-Location $top
  $branch = git rev-parse --abbrev-ref HEAD
  ok "Git repo: $top (branch: $branch)"
  # Clear stray git env that causes PIPETRACK/.git noise
  Remove-Item Env:GIT_DIR -ErrorAction SilentlyContinue
  Remove-Item Env:GIT_WORK_TREE -ErrorAction SilentlyContinue
  git fetch origin | Out-Null
  $ahead = git rev-list --left-right --count origin/$branch...$branch 2>$null
  if ($LASTEXITCODE -eq 0) {
    $parts = $ahead -split "\s+"
    if ($parts.Length -ge 2) {
      if ([int]$parts[1] -gt 0) { warn "Local ahead by $($parts[1]) commit(s)" }
      if ([int]$parts[0] -gt 0) { warn "Local behind by $($parts[0]) commit(s) — consider pull --rebase" }
    }
  }
} catch { fail "Git check failed: $_"; exit 1 }

# 2) Python & venv
try {
  $py = (Get-Command python -ErrorAction Stop).Source
  ok "Python: $py"
} catch { fail "Python not found on PATH"; exit 1 }

# 3) Package entrypoint exists
if ((Test-Path "$top\clausebot_api\main.py" -PathType Leaf) -and
    (Test-Path "$top\clausebot_api\airtable_data_source.py" -PathType Leaf)) {
  ok "Entrypoints present: clausebot_api/main.py and airtable_data_source.py"
} else {
  fail "Missing clausebot_api/*.py entry files"; exit 1
}

# 4) Required env
$need = @("AIRTABLE_API_KEY","AIRTABLE_BASE_ID","AIRTABLE_TABLE","AIRTABLE_VIEW")
$missing = @()
foreach($n in $need){ if ([string]::IsNullOrWhiteSpace((Get-Item Env:$n -ErrorAction SilentlyContinue).Value)) { $missing += $n } }
if ($missing.Count -gt 0) {
  fail ("Missing env: " + ($missing -join ", "))
  Write-Host "Hint: put them in .env (local) and Render (prod)" -ForegroundColor DarkGray
  exit 1
} else { ok "Env present: $($need -join ', ')" }

# 5) Airtable direct probe (proves PAT/base/table)
try {
  $encTable = [uri]::EscapeDataString($env:AIRTABLE_TABLE)
  $uri = "https://api.airtable.com/v0/$($env:AIRTABLE_BASE_ID)/$encTable?maxRecords=1&view=$([uri]::EscapeDataString($env:AIRTABLE_VIEW))"
  $resp = Invoke-WebRequest -UseBasicParsing -Uri $uri -Headers @{ Authorization = "Bearer $($env:AIRTABLE_API_KEY)" } -Method GET
  if ($resp.StatusCode -eq 200) { ok "Airtable reachable (200). Body length: $($resp.Content.Length)" }
  else { fail "Airtable unexpected status: $($resp.StatusCode)"; exit 1 }
} catch {
  $msg = if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
  fail "Airtable probe failed: $($msg -replace '\s+',' ')"
  exit 1
}

# 6) Dependency import quick test
try {
  $pyCode = @"
import sys
import fastapi, uvicorn, httpx, pydantic
print("fastapi", fastapi.__version__)
print("pydantic", pydantic.__version__)
"@
  $pyCode | python -
  if ($LASTEXITCODE -eq 0) { ok "Python deps import fine" } else { fail "Python deps import failed"; exit 1 }
} catch { fail "Python deps import errored: $_"; exit 1 }

# 7) Port availability (8081)
try {
  $port = 8081
  $tcp = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ? { $_.LocalPort -eq $port }
  if ($tcp) { warn "Port $port already in use (PID $($tcp.OwningProcess)). You might want to kill it." }
  else { ok "Port $port free" }
} catch { warn "Port check skipped: $_" }

Pop-Location
ok "Preflight complete."
