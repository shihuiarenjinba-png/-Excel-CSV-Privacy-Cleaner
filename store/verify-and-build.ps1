# One command for test -> immutable-source portable EXE candidate.
# Does NOT reserve Microsoft Store product name or produce an MSIX.
[CmdletBinding()]
param(
    [string]$ExpectedBranch = 'improve/simple-column-ui-20261018'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Qa = Join-Path $PSScriptRoot 'run-windows-qa.ps1'
$Build = Join-Path $PSScriptRoot 'build-portable-candidate.ps1'
if (-not (Test-Path -LiteralPath $Qa -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Build -PathType Leaf)) {
    throw 'Required local QA/candidate-build script is missing.'
}
Write-Host 'STAGE 1: Run real local Python + synthetic GUI tests.'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Qa -ExpectedBranch $ExpectedBranch
if ($LASTEXITCODE -ne 0) {
    throw 'HOLD: actual regression execution failed; packaging was not started.'
}
Write-Host 'STAGE 2: Create a portable candidate from exact committed source.'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Build -ExpectedBranch $ExpectedBranch
if ($LASTEXITCODE -ne 0) {
    throw 'HOLD: portable candidate build failed. Do not claim a package was created.'
}
Write-Host 'PORTABLE CANDIDATE COMPLETE FOR QA. NOT A STORE MSIX OR SALE APPROVAL.'
