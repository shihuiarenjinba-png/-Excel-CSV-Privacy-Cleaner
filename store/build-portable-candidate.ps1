# Builds a versioned pre-Store Windows EXE from an immutable git snapshot.
# NO signing, MSIX, publishing or Microsoft certification is asserted.
[CmdletBinding()]
param(
    [string]$CandidateParent = (Join-Path $env:USERPROFILE 'Documents\ExcelCSVPrivacyCleaner-Candidates'),
    [string]$ExpectedBranch = 'improve/simple-column-ui-20261018'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Sha = (& git -C $Root rev-parse HEAD | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $Sha -notmatch '^[0-9a-f]{40}$') {
    throw 'A valid git checkout and exact commit SHA are required.'
}
$ActualBranch = (& git -C $Root branch --show-current | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $ActualBranch -ne $ExpectedBranch) {
    throw "Wrong branch: $ActualBranch (expected $ExpectedBranch)"
}
$Dirty = & git -C $Root status --porcelain --untracked-files=no
if ($LASTEXITCODE -ne 0 -or $Dirty) { throw 'Tracked checkout is dirty; commit changes before building.' }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is required.' }
if (-not (Get-Command powershell.exe -ErrorAction SilentlyContinue)) { throw 'Windows PowerShell is required.' }

$id = [guid]::NewGuid().ToString('N')
$Stage = Join-Path $env:TEMP ('ExcelCSV-build-' + $id)
$Archive = Join-Path $Stage 'snapshot.zip'
$Worktree = Join-Path $Stage 'source'
$Candidate = Join-Path $CandidateParent ($Sha.Substring(0,12) + '-' + $id)
$Succeeded = $false
try {
    New-Item -ItemType Directory -Path $Stage -Force | Out-Null
    & git -C $Root archive --format=zip --output=$Archive HEAD
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Archive -PathType Leaf)) {
        throw 'Could not create a source-only git archive.'
    }
    Expand-Archive -LiteralPath $Archive -DestinationPath $Worktree -ErrorAction Stop
    $Builder = Join-Path $Worktree 'build-windows-portable.ps1'
    if (-not (Test-Path -LiteralPath $Builder -PathType Leaf)) {
        throw 'Original Windows builder is missing from git snapshot.'
    }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Builder
    if ($LASTEXITCODE -ne 0) { throw "Windows build failed (exit $LASTEXITCODE)." }
    $Built = Join-Path $Worktree 'dist\ExcelCSVPrivacyCleaner.exe'
    if (-not (Test-Path -LiteralPath $Built -PathType Leaf)) {
        throw 'Build reported success but no ExcelCSVPrivacyCleaner.exe was generated.'
    }
    if (Test-Path -LiteralPath $Candidate) {
        throw "Refusing to replace existing candidate folder: $Candidate"
    }
    New-Item -ItemType Directory -Path $CandidateParent -Force -ErrorAction Stop | Out-Null
    New-Item -ItemType Directory -Path $Candidate -ErrorAction Stop | Out-Null
    Copy-Item -LiteralPath $Built -Destination (Join-Path $Candidate 'ExcelCSVPrivacyCleaner.exe') -ErrorAction Stop
    $Guide = Join-Path $Worktree 'START_HERE.html'
    if (Test-Path -LiteralPath $Guide -PathType Leaf) {
        Copy-Item -LiteralPath $Guide -Destination (Join-Path $Candidate 'START_HERE.html') -ErrorAction Stop
    }
    $Hash = (Get-FileHash -LiteralPath (Join-Path $Candidate 'ExcelCSVPrivacyCleaner.exe') -Algorithm SHA256).Hash.ToLowerInvariant()
    $Manifest = [ordered]@{
        product='ExcelCSVPrivacyCleaner'
        source_branch=$ActualBranch
        source_sha=$Sha
        exe_sha256=$Hash
        exe_name='ExcelCSVPrivacyCleaner.exe'
        created_utc=(Get-Date).ToUniversalTime().ToString('o')
        is_msix=$false
        store_certified=$false
        human_gui_accepted=$false
        scope='Unsigned portable Windows candidate for synthetic QA only, not a commercial deliverable.'
    }
    $Manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $Candidate 'candidate-manifest.json') -Encoding UTF8
    $Succeeded = $true
    Write-Host "PORTABLE QA CANDIDATE (NOT STORE MSIX): $Candidate"
    Write-Host "SOURCE SHA: $Sha"
    Write-Host "EXE SHA256: $Hash"
    Write-Host 'Required next: run binary on Windows, visual/DPI review, license NOTICE, privacy egress, Partner Center Identity, Store MSIX install and certification.'
} finally {
    if (Test-Path -LiteralPath $Stage) {
        Remove-Item -LiteralPath $Stage -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (-not $Succeeded -and (Test-Path -LiteralPath $Candidate)) {
        # This path is a newly generated GUID-only output, never an existing product.
        Remove-Item -LiteralPath $Candidate -Recurse -Force -ErrorAction SilentlyContinue
    }
}
