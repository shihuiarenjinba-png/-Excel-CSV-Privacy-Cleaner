# Read-only Windows app-control triage for the already-built candidate.
# Never changes policy, creates an allow-list, unblocks a file, or executes the EXE.
[CmdletBinding()]
param(
    [string]$CandidateDirectory = (Join-Path $env:USERPROFILE 'Documents\ExcelCSVPrivacyCleaner-Candidates\5a11d5e50eed-020cfef374dc4936af630455b985a0b3'),
    [int]$HoursBack = 24
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if ($HoursBack -lt 1 -or $HoursBack -gt 168) {
    throw 'HoursBack must be between 1 and 168.'
}
$ExePath = Join-Path $CandidateDirectory 'ExcelCSVPrivacyCleaner.exe'
if (-not (Test-Path -LiteralPath $ExePath -PathType Leaf)) {
    throw "Candidate EXE not found: $ExePath"
}
$ExpectedHash = '9a81e3a7deb5d8048cde49b164bf0596344469644a1e12c57a06281fc6010962'
$ActualHash = (Get-FileHash -LiteralPath $ExePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ActualHash -ne $ExpectedHash) {
    throw 'SHA256 mismatch: this is not the previously verified candidate. Stop and investigate.'
}
$signature = Get-AuthenticodeSignature -LiteralPath $ExePath
Write-Host 'SOURCE CANDIDATE SHA: 5a11d5e50eed856a8948966a9e0886248b58c615'
Write-Host "EXE SHA256 PASS: $ActualHash"
Write-Host "Authenticode status: $($signature.Status)"
Write-Host 'This script does not attempt to start the EXE or modify Windows security policy.'

$start = (Get-Date).AddHours(-$HoursBack)
$eventSources = @(
    @{Log='Microsoft-Windows-CodeIntegrity/Operational'; Ids=@(3077,3033,3089); Label='App Control / Smart App Control / Code Integrity'},
    @{Log='Microsoft-Windows-AppLocker/EXE and DLL'; Ids=@(8004); Label='AppLocker executable blocking'},
    @{Log='Microsoft-Windows-Windows Defender/Operational'; Ids=@(1116,1121); Label='Microsoft Defender detection / ASR'}
)
$target = 'ExcelCSVPrivacyCleaner.exe'
$hits = 0
foreach ($entry in $eventSources) {
    Write-Host ""
    Write-Host ("=== " + $entry.Label + " ===")
    try {
        $events = @(Get-WinEvent -FilterHashtable @{
            LogName = $entry.Log
            Id = $entry.Ids
            StartTime = $start
        } -ErrorAction Stop | Where-Object {
            $_.Message -and $_.Message.IndexOf($target, [StringComparison]::OrdinalIgnoreCase) -ge 0
        } | Select-Object -First 8)
        if ($events.Count -eq 0) {
            Write-Host 'No matching events found in this readable log window; this does not prove there was no block.'
            continue
        }
        foreach ($event in $events) {
            $hits++
            Write-Host "Event ID $($event.Id) at $($event.TimeCreated)"
            Write-Host "Log: $($entry.Log)"
            Write-Host (($event.Message -replace "\r", '') -split "\n" | Select-Object -First 16 | Out-String).Trim()
            Write-Host '---'
        }
    } catch {
        Write-Host "Cannot read this log or no records exist: $($_.Exception.Message)"
    }
}
Write-Host ""
if ($hits -eq 0) {
    Write-Host 'No correlated block event was visible. Check Windows Security > App & browser control > Smart App Control, and Windows Security > Virus & threat protection > Protection history.'
} else {
    Write-Host 'Relevant events printed. Determine which actual product/policy rejected the file before making any release decision.'
}
Write-Host 'Do NOT disable security features, create broad exceptions, or call a blocked EXE release-ready.'
Write-Host 'Before sharing event text, redact usernames, device names, IDs, and unrelated file paths.'
