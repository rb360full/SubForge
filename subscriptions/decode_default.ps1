Param(
    [string]$Input = "Telegram-List1.txt",
    [string]$Output = $null
)

if (-not $Output) {
    $Output = [System.IO.Path]::GetFileNameWithoutExtension($Input) + ".decoded.txt"
}

$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

if (-not (Test-Path $Input)) {
    Write-Error "Input file '$Input' not found"
    exit 2
}

$b64 = Get-Content $Input -Raw
[System.IO.File]::WriteAllBytes($Output, [System.Convert]::FromBase64String($b64))
Write-Host "Wrote decoded subscription lines to $Output"
