param(
  [string]$ApiBase = "https://clausebot-api.onrender.com",
  [string]$Cat1 = "Fundamentals",
  [int]$Count = 5
)

$ErrorActionPreference = "Stop"
function show($name,$uri){
  try{
    $r = Invoke-WebRequest -Uri $uri -UseBasicParsing -MaximumRedirection 0 -ErrorAction Stop
    Write-Host "✔ $name ($($r.StatusCode))" -ForegroundColor Green
    ($r.Content | Select-Object -First 1)
  } catch {
    $status = $_.Exception.Response.StatusCode.value__ 2>$null
    Write-Host "✖ $name ($status)" -ForegroundColor Red
    try {
      $stream = $_.Exception.Response.GetResponseStream()
      if ($stream) {
        $body = (New-Object IO.StreamReader($stream)).ReadToEnd()
        Write-Host ($body.Substring(0,[Math]::Min(500,$body.Length)))
      }
    } catch { }
  }
}

show "Health"            "$ApiBase/health"
show "Airtable health"   "$ApiBase/health/airtable"
show "Quiz ($Cat1 x$Count)" "$ApiBase/v1/quiz?count=$Count&category=$([Uri]::EscapeDataString($Cat1))"
show "Quiz (stress 50)"  "$ApiBase/v1/quiz?count=50&category=$([Uri]::EscapeDataString($Cat1))"
