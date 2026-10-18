# Local Windows validation fallback. Does not authorize Store release.
[CmdletBinding()]
param(
    [string]$EvidenceParent = (Join-Path $env:USERPROFILE "Documents\ExcelCSVPrivacyCleaner-QA"),
    [string]$ExpectedBranch = "improve/simple-column-ui-20261018"
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$id = [guid]::NewGuid().ToString("N")
$dir = Join-Path $EvidenceParent ("evidence-" + $id)
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$log = Join-Path $dir "tests.log"
$reportFile = Join-Path $dir "qa-result.json"
$branch = ""
$sha = ""
$results = @()
$overallPass = $false
$venv = Join-Path $env:TEMP ("ExcelCSV-QA-" + $id)
try {
    $sha = (& git -C $Root rev-parse HEAD 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $sha -notmatch '^[a-f0-9]{40}$') {
        throw "A real Git checkout with commit SHA is required."
    }
    $branch = (& git -C $Root branch --show-current 2>&1 | Out-String).Trim()
    if (-not $ExpectedBranch.Trim() -or $branch -ne $ExpectedBranch) {
        throw "Wrong branch: $branch (expected $ExpectedBranch). Specify -ExpectedBranch for a derived QA branch."
    }
    $dirty = & git -C $Root status --porcelain --untracked-files=no
    if ($LASTEXITCODE -ne 0 -or $dirty) {
        throw "Tracked worktree must be clean. Do not test uncommitted changes."
    }
    function Record([string]$label, [string]$executable, [string[]]$arguments) {
        ("==== " + $label + " ====") | Out-File -LiteralPath $log -Append -Encoding utf8
        # Windows PowerShell 5.1 may promote a native tool's harmless stderr
        # into a terminating NativeCommandError when ErrorActionPreference=Stop.
        # Preserve stderr in the log and trust the real process exit code.
        $oldPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            $output = & $executable @arguments 2>&1 | Out-String
            $exit = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $oldPreference
        }
        $output | Out-File -LiteralPath $log -Append -Encoding utf8
        $script:results += [ordered]@{name=$label;exit_code=$exit}
        if ($exit -ne 0) { throw "$label failed ($exit). See $log" }
    }
    . (Join-Path $Root "build_python.ps1")
    $BasePython = Resolve-BuildPython
    Record "Isolated environment" $BasePython @("-m","venv",$venv)
    $python = Join-Path $venv "Scripts\python.exe"
    Record "Pinned packages" $python @("-m","pip","install","-r",(Join-Path $Root "requirements-windows.lock.txt"))
    Record "Python compile" $python @("-m","compileall","-q",(Join-Path $Root "windows_app.py"),(Join-Path $Root "i18n.py"),(Join-Path $Root "tests"))
    Push-Location $Root
    try {
        Record "Existing smoke" $python @("smoke_test.py")
        Record "Regression suite" $python @("-m","unittest","discover","-s","tests","-p","test_*.py","-v")
        Record "Synthetic Tk GUI flow" $python @("gui_smoke_test.py")
        Record "Bilingual smoke" $python @("bilingual_smoke_test.py")
        Record "Language standard" $python @("language_standard_smoke_test.py")
        Record "Dialog parents" $python @("dialog_parent_smoke_test.py")
    } finally { Pop-Location }
    $overallPass = $true
} catch {
    ($_ | Out-String) | Out-File -LiteralPath $log -Append -Encoding utf8
} finally {
    if (Test-Path -LiteralPath $venv) {
        try { Remove-Item -LiteralPath $venv -Recurse -Force -ErrorAction Stop }
        catch { ("Disposable environment cleanup failed: " + $_) | Out-File -LiteralPath $log -Append -Encoding utf8 }
    }
    $hash = if (Test-Path -LiteralPath $log) {
        (Get-FileHash -LiteralPath $log -Algorithm SHA256).Hash.ToLowerInvariant()
    } else { "" }
    [ordered]@{
        schema_version=1; product="ExcelCSVPrivacyCleaner"; source_sha=$sha; branch=$branch
        automated_local_tests_pass=$overallPass; human_gui_pass=$false
        msix_install_pass=$false; store_certification_pass=$false
        test_steps=$results; log_sha256=$hash
        created_utc=(Get-Date).ToUniversalTime().ToString("o")
        scope="Synthetic tests only; no Store release approval."
    } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportFile -Encoding UTF8
    Write-Host "QA report: $reportFile"
    if (-not $overallPass) { throw "HOLD: local tests were not all successful. See $log" }
    Write-Host "LOCAL TESTS PASS ONLY; HUMAN GUI/MSIX/STORE STILL HOLD."
}
