Param(
  [Parameter(Mandatory=$true)]
  [string]$ZipPath,
  [string]$Description = "Skyvern OpenAI + Aurora + S3 package",
  [switch]$UseGh  # if set, no token prompt; uses gh CLI instead
)

if ($UseGh) {
  & "$PSScriptRoot\create_secret_gist.ps1" -ZipPath $ZipPath -Description $Description -UseGh
  exit $LASTEXITCODE
}

# Prompt for token securely
$sec = Read-Host "Enter GitHub token (gist scope)" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try {
  $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
  # Set token only for this process
  $env:GITHUB_TOKEN = $plain
  # Invoke the main script (API path)
  & "$PSScriptRoot\create_secret_gist.ps1" -ZipPath $ZipPath -Description $Description
  $code = $LASTEXITCODE
} finally {
  if ($ptr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
  # Clear variables to minimize in-memory lifetime
  Remove-Variable sec, plain, ptr -ErrorAction SilentlyContinue
  # Unset env variable
  Remove-Item Env:\GITHUB_TOKEN -ErrorAction SilentlyContinue
}
exit $code
