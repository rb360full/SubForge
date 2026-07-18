Param(
    [string]$Input = "default.txt",
    [string]$Output = "default.decoded.txt"
)

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

if (-not (Test-Path $Input)) {
    Write-Error "Input file '$Input' not found in $repo\subscriptions"
    exit 2
}

$b64 = Get-Content $Input -Raw
[System.IO.File]::WriteAllBytes($Output, [System.Convert]::FromBase64String($b64))
Write-Host "Wrote decoded subscription lines to $Output"
