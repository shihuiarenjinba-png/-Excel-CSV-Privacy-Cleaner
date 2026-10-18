# Read-only inspection of a previously generated portable EXE candidate.
# Does not run unknown binaries, install packages, update files, or approve Store release.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$SourceSha,
    [string]$CandidateParent = (Join-Path $env:USERPROFILE 'Documents\ExcelCSVPrivacyCleaner-Candidates')
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not (Test-Path -LiteralPath $CandidateParent -PathType Container)) {
    throw "Candidate folder not found: $CandidateParent"
}

$found = @(
    Get-ChildItem -LiteralPath $CandidateParent -Directory |
    Where-Object {
        $_.Name.StartsWith($SourceSha.Substring(0,12), [StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath (Join-Path $_.FullName 'candidate-manifest.json') -PathType Leaf)
    }
)
if ($found.Count -ne 1) {
    throw "Expected exactly one candidate folder for the requested source commit, found $($found.Count). Specify -CandidateParent to narrow the directory; never guess a candidate."
}
$folder = $found[0].FullName
$manifestPath = Join-Path $folder 'candidate-manifest.json'
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($null -eq $manifest -or $manifest.product -ne 'ExcelCSVPrivacyCleaner') {
    throw 'Invalid product declaration in candidate manifest.'
}
if ($manifest.source_sha -ine $SourceSha) {
    throw "Source SHA mismatch: requested $SourceSha, manifest says $($manifest.source_sha)"
}
if ($manifest.exe_name -ne 'ExcelCSVPrivacyCleaner.exe') {
    throw 'Unexpected EXE name in candidate manifest.'
}
if ($manifest.is_msix -ne $false -or $manifest.store_certified -ne $false) {
    throw 'Manifest has unexpected MSIX or certification flags; candidate requires manual review.'
}
$exe = Join-Path $folder 'ExcelCSVPrivacyCleaner.exe'
if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
    throw "Built EXE is missing: $exe"
}
$hash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
if ($hash -ne $manifest.exe_sha256.ToLowerInvariant()) {
    throw "EXE SHA256 differs from its immutable build manifest! No further use allowed."
}
$signature = Get-AuthenticodeSignature -LiteralPath $exe
$size = (Get-Item -LiteralPath $exe).Length

Write-Host 'PORTABLE EXE INTEGRITY: PASS (hash matches original build manifest).'
Write-Host "Source commit: $SourceSha"
Write-Host "Candidate directory: $folder"
Write-Host "EXE SHA256: $hash"
Write-Host "EXE bytes: $size"
Write-Host "Authenticode status (informational): $($signature.Status)"
Write-Host 'NOT TESTED HERE: actual GUI, malware scan, internet connections, LICENSE/NOTICE, MSIX installation, Microsoft Store certification.'
Write-Host 'This is only a read-only integrity review. Product registration and sale remain HOLD.'
