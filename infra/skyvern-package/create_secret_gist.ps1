Param(
  [Parameter(Mandatory=$true)]
  [string]$ZipPath,
  [string]$Description = "Skyvern OpenAI + Aurora + S3 package",
  [switch]$UseGh  # set this switch to use GitHub CLI instead of curl+token
)

# 1) Prep temp directory
$Tmp = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "skyvern_gist_" + [guid]::NewGuid().ToString()))
Write-Host "Temp dir: $Tmp"
Expand-Archive -Path $ZipPath -DestinationPath $Tmp -Force

# Normalize to the root of the unzipped content (if zip has a root folder)
$entries = Get-ChildItem -Path $Tmp
if ($entries.Count -eq 1 -and $entries[0].PSIsContainer) {
  $Root = $entries[0].FullName
} else {
  $Root = $Tmp
}
Write-Host "Unzipped root: $Root"

if ($UseGh) {
  # 2a) Use GitHub CLI (recommended)
  # Requires: gh auth login (account with gist scope)
  Write-Host "Using GitHub CLI to create a private Gist..."
  Push-Location $Root
  # GH versions differ on gist flags; this works on newer gh:
  $res = gh gist create . --private --description "$Description" 2>&1
  Pop-Location
  if ($LASTEXITCODE -ne 0) {
    Write-Error "gh gist create failed: $res"
    exit 1
  }
  Write-Host "Gist URL:"
  Write-Output $res
  exit 0
}

# 2b) Use curl + GITHUB_TOKEN to call the GitHub API
# Requires env var: $env:GITHUB_TOKEN with gist scope
if (-not $env:GITHUB_TOKEN) {
  Write-Error "GITHUB_TOKEN environment variable not set. Provide a token with 'gist' scope or use -UseGh."
  exit 1
}

# Build the 'files' object payload for GitHub Gist API
$files = @{ }
Get-ChildItem -Recurse -File -Path $Root | ForEach-Object {
  $rel = Resolve-Path $_.FullName -Relative -RelativeBasePath $Root 2>$null
  if (-not $rel) {
    $rel = $_.FullName.Substring($Root.Length).TrimStart('\','/')
  }
  $content = Get-Content -Raw -LiteralPath $_.FullName
  $files[$rel -replace '\\','/'] = @{ content = $content }
}

$payload = @{
  description = $Description
  public = $false
  files = $files
} | ConvertTo-Json -Depth 100

# Write payload to a temp file
$payloadPath = Join-Path $Tmp "gist_payload.json"
$payload | Set-Content -LiteralPath $payloadPath -Encoding UTF8

# Create the Gist
Write-Host "Creating secret gist via API..."
$apiUrl = "https://api.github.com/gists"
# Use curl if present; fallback to Invoke-RestMethod
if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
  $result = & curl.exe -s -H "Authorization: token $($env:GITHUB_TOKEN)" -H "Content-Type: application/json" -d "@$payloadPath" $apiUrl
  # Try to parse URL
  try {
    $obj = $result | ConvertFrom-Json
    if ($obj.html_url) {
      Write-Host "Gist URL:"
      Write-Output $obj.html_url
      exit 0
    }
  } catch {}
  Write-Host $result
  exit 0
} else {
  $resp = Invoke-RestMethod -Method Post -Uri $apiUrl -Headers @{ Authorization = "token $($env:GITHUB_TOKEN)"; "Content-Type" = "application/json" } -Body (Get-Content -Raw $payloadPath)
  Write-Host "Gist URL:"
  Write-Output $resp.html_url
}
