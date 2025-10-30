$ErrorActionPreference = "Stop"
# Go to repo root
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here "..")
Set-Location $root

# 1) venv
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
  Write-Host "Creating venv..." -ForegroundColor Yellow
  python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
Write-Host "venv activated" -ForegroundColor Green

# 2) deps (idempotent + fast on warm cache)
python -m pip install --upgrade pip | Out-Null
python -m pip install -r .\requirements.txt | Out-Null
Write-Host "deps ok" -ForegroundColor Green

# 3) load .env if exists
if (Test-Path ".env") {
  Get-Content ".env" | ? { $_ -and ($_ -notmatch '^\s*#') } | % {
    $kv = $_ -split '=', 2
    if ($kv.Length -eq 2) { $name=$kv[0].Trim(); $val=$kv[1].Trim(); if (-not $env:$name) { $env:$name = $val } }
  }
  Write-Host ".env loaded (variables set if not already in shell)" -ForegroundColor Green
}

# 4) Preflight checks
.\scripts\preflight.ps1

# 5) PYTHONPATH
$env:PYTHONPATH = "$root;$root\clausebot_api"

# 6) Run API
Write-Host "Starting API on http://0.0.0.0:8081 ..." -ForegroundColor Cyan
python -m uvicorn clausebot_api.main:app --host 0.0.0.0 --port 8081 --reload
