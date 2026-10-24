# Build a Store-submission MSIX candidate only from a real Partner Center identity.
# Does not self-certify, sign for sideloading, publish, or replace an existing artifact.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$IdentityName,
    [Parameter(Mandatory=$true)][string]$Publisher,
    [Parameter(Mandatory=$true)][string]$PublisherDisplayName,
    [Parameter(Mandatory=$true)][string]$DisplayName,
    [Parameter(Mandatory=$true)][string]$AssetsDirectory,
    [Parameter(Mandatory=$true)][string]$ExePath,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+\.0$')][string]$Version
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ExpectedBranch = "codex/store-p1-excel-csv-privacy-20261023"
function Invoke-GitText {
    param([string[]]$GitArguments)
    $Output = & git @GitArguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Git command failed (exit $LASTEXITCODE): git $($GitArguments -join ' '); output: $Output" }
    return ($Output | Out-String).Trim()
}
Set-Location -LiteralPath $Root
$RemoteUrl = Invoke-GitText -GitArguments @("remote","get-url","origin")
if ($RemoteUrl -notmatch '(?i)github[.]com[:/]shihuiarenjinba-png/-Excel-CSV-Privacy-Cleaner(?:[.]git)?$') { throw "Wrong origin repository." }
Invoke-GitText -GitArguments @("fetch","origin") | Out-Null
$Branch = Invoke-GitText -GitArguments @("branch","--show-current")
$SourceSha = Invoke-GitText -GitArguments @("rev-parse","HEAD")
$RemoteSha = Invoke-GitText -GitArguments @("rev-parse",("origin/" + $ExpectedBranch))
$DirtyState = Invoke-GitText -GitArguments @("status","--porcelain","--untracked-files=all")
if ($Branch -cne $ExpectedBranch) { throw "Wrong working branch: $Branch" }
if ($SourceSha -notmatch '^[0-9a-f]{40}$' -or $RemoteSha -cne $SourceSha) { throw "Local and remote HEAD must be identical." }
if ($DirtyState) { throw "Uncommitted or untracked changes exist; stopped before packaging." }

if ($IdentityName -notmatch '^[A-Za-z0-9][A-Za-z0-9_.-]{1,48}$' -or
    $IdentityName -match '(?i)(example|placeholder|testidentity|yourname)') {
    throw "Provide the exact Partner Center package identity (not a sample or test identity)."
}
if ($Publisher -notmatch '^CN=.+$' -or $Publisher -match '(?i)(example|placeholder|testidentity|yourname)' -or
    $PublisherDisplayName.Trim().Length -eq 0 -or $DisplayName.Trim().Length -eq 0) {
    throw "Provide exact real Store Publisher, PublisherDisplayName and DisplayName."
}
$parts = $Version.Split('.')
if ($parts.Count -ne 4 -or [int]$parts[0] -lt 1 -or
    ($parts | Where-Object { [long]$_ -gt 65535 }).Count -gt 0) {
    throw "MSIX Store version must be 1..65535 for major, <=65535 for minor/build, and fourth field 0."
}
if (-not (Test-Path -LiteralPath $ExePath -PathType Leaf)) { throw "Built EXE not found: $ExePath" }
if (-not (Test-Path -LiteralPath $AssetsDirectory -PathType Container)) {
    throw "Provide real store logo PNG assets, not generated placeholders."
}
if (-not (Get-Command MakeAppx.exe -ErrorAction SilentlyContinue)) {
    throw "Windows SDK MakeAppx.exe not on PATH. Install Windows SDK and add its x64 bin directory."
}

$OutputDir = Join-Path $Root "dist-store"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$Package = Join-Path $OutputDir ("ExcelCSVPrivacyCleaner_QA_UNSIGNED_" + $Version + "_x64.msix")
if (Test-Path -LiteralPath $Package) { throw "Candidate MSIX already exists: $Package" }
$Stage = Join-Path $env:TEMP ("ExcelCSVPrivacyCleaner-msix-" + [guid]::NewGuid().ToString("N"))
$Check = Join-Path $env:TEMP ("ExcelCSVPrivacyCleaner-check-" + [guid]::NewGuid().ToString("N"))
try {
    New-Item -ItemType Directory -Path (Join-Path $Stage "Assets") -Force | Out-Null
    Copy-Item -LiteralPath $ExePath -Destination (Join-Path $Stage "ExcelCSVPrivacyCleaner.exe") -ErrorAction Stop
    Set-Content -LiteralPath (Join-Path $Stage "SOURCE_GIT_COMMIT.txt") -Value $SourceSha -Encoding ASCII
    $ExpectedLogoDimensions = @{
        "StoreLogo.png" = @(50, 50)
        "Square44x44Logo.png" = @(44, 44)
        "Square150x150Logo.png" = @(150, 150)
    }
    foreach ($name in @("StoreLogo.png", "Square44x44Logo.png", "Square150x150Logo.png")) {
        $Source = Join-Path $AssetsDirectory $name
        if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) { throw "Missing real logo asset: $Source" }
        $bytes = [System.IO.File]::ReadAllBytes($Source)
        if ($bytes.Length -lt 24 -or $bytes[0] -ne 137 -or $bytes[1] -ne 80 -or
            $bytes[2] -ne 78 -or $bytes[3] -ne 71 -or $bytes[4] -ne 13 -or
            $bytes[5] -ne 10 -or $bytes[6] -ne 26 -or $bytes[7] -ne 10 -or
            $bytes[12] -ne 73 -or $bytes[13] -ne 72 -or $bytes[14] -ne 68 -or $bytes[15] -ne 82) {
            throw "Required logo is not a valid PNG/IHDR: $Source"
        }
        $width = 0; $height = 0
        for ($i = 16; $i -lt 20; $i++) { $width = ($width * 256) + [int]$bytes[$i] }
        for ($i = 20; $i -lt 24; $i++) { $height = ($height * 256) + [int]$bytes[$i] }
        $expected = $ExpectedLogoDimensions[$name]
        if ($width -ne [int]$expected[0] -or $height -ne [int]$expected[1]) {
            throw "Wrong PNG dimensions for $name : $width x $height"
        }
        Copy-Item -LiteralPath $Source -Destination (Join-Path (Join-Path $Stage "Assets") $name)
    }
    $SafeIdentity = [System.Security.SecurityElement]::Escape($IdentityName)
    $SafePublisher = [System.Security.SecurityElement]::Escape($Publisher)
    $SafePublisherName = [System.Security.SecurityElement]::Escape($PublisherDisplayName)
    $SafeDisplay = [System.Security.SecurityElement]::Escape($DisplayName)
    $Manifest = @"
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
         xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
         xmlns:uap10="http://schemas.microsoft.com/appx/manifest/uap/windows10/10"
         xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
         IgnorableNamespaces="uap uap10 rescap">
  <Identity Name="$SafeIdentity" Publisher="$SafePublisher" Version="$Version" ProcessorArchitecture="x64"/>
  <Properties>
    <DisplayName>$SafeDisplay</DisplayName>
    <PublisherDisplayName>$SafePublisherName</PublisherDisplayName>
    <Logo>Assets\StoreLogo.png</Logo>
  </Properties>
  <Resources><Resource Language="ja-JP"/><Resource Language="en-US"/></Resources>
  <Dependencies><TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.19041.0" MaxVersionTested="10.0.26100.0"/></Dependencies>
  <Applications>
    <Application Id="App" Executable="ExcelCSVPrivacyCleaner.exe"
                 uap10:RuntimeBehavior="packagedClassicApp"
                 uap10:TrustLevel="mediumIL">
      <uap:VisualElements DisplayName="$SafeDisplay"
          Description="Local CSV/XLSX column transformation"
          BackgroundColor="transparent"
          Square150x150Logo="Assets\Square150x150Logo.png"
          Square44x44Logo="Assets\Square44x44Logo.png"/>
    </Application>
  </Applications>
  <Capabilities><rescap:Capability Name="runFullTrust"/></Capabilities>
</Package>
"@
    [xml]$Xml = $Manifest
    if ($Xml.Package.Identity.Publisher -ne $Publisher -or $Xml.Package.Identity.Name -ne $IdentityName) {
        throw "Store identity XML did not roundtrip."
    }
    [System.IO.File]::WriteAllText((Join-Path $Stage "AppxManifest.xml"), $Manifest,
                                  (New-Object System.Text.UTF8Encoding($false)))
    & MakeAppx.exe pack /d $Stage /p $Package
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Package -PathType Leaf)) {
        throw "MakeAppx pack failed"
    }
    New-Item -ItemType Directory -Path $Check | Out-Null
    & MakeAppx.exe unpack /p $Package /d $Check
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath (Join-Path $Check "ExcelCSVPrivacyCleaner.exe"))) {
        throw "MSIX roundtrip unpack or executable verification failed"
    }
    [xml]$RoundtripManifest = Get-Content -LiteralPath (Join-Path $Check "AppxManifest.xml") -Raw -Encoding UTF8
    $Ns = New-Object System.Xml.XmlNamespaceManager($RoundtripManifest.NameTable)
    $Ns.AddNamespace("f","http://schemas.microsoft.com/appx/manifest/foundation/windows10")
    $Ns.AddNamespace("uap","http://schemas.microsoft.com/appx/manifest/uap/windows10")
    $IdNode = $RoundtripManifest.SelectSingleNode("/f:Package/f:Identity",$Ns)
    $PropsNode = $RoundtripManifest.SelectSingleNode("/f:Package/f:Properties",$Ns)
    $VisualNode = $RoundtripManifest.SelectSingleNode("/f:Package/f:Applications/f:Application/uap:VisualElements",$Ns)
    $DisplayNode = if ($null -ne $PropsNode) { $PropsNode.SelectSingleNode("f:DisplayName",$Ns) } else { $null }
    $PublisherNode = if ($null -ne $PropsNode) { $PropsNode.SelectSingleNode("f:PublisherDisplayName",$Ns) } else { $null }
    if ($null -eq $IdNode -or $null -eq $DisplayNode -or $null -eq $PublisherNode -or $null -eq $VisualNode -or
        $IdNode.GetAttribute("Name") -cne $IdentityName -or $IdNode.GetAttribute("Publisher") -cne $Publisher -or
        $IdNode.GetAttribute("Version") -cne $Version -or $IdNode.GetAttribute("ProcessorArchitecture") -cne "x64" -or
        $DisplayNode.InnerText -cne $DisplayName -or $PublisherNode.InnerText -cne $PublisherDisplayName -or
        $VisualNode.GetAttribute("DisplayName") -cne $DisplayName) {
        throw "Unpacked MSIX manifest does not match the requested Store identity."
    }
    $EmbeddedSource = (Get-Content -LiteralPath (Join-Path $Check "SOURCE_GIT_COMMIT.txt") -Raw -Encoding ASCII).Trim()
    if ($EmbeddedSource -cne $SourceSha) { throw "Embedded source commit does not match build HEAD." }
    $OriginalHash = (Get-FileHash -LiteralPath $ExePath -Algorithm SHA256).Hash
    $PackedHash = (Get-FileHash -LiteralPath (Join-Path $Check "ExcelCSVPrivacyCleaner.exe") -Algorithm SHA256).Hash
    if ($OriginalHash -ne $PackedHash) { throw "Packaged executable SHA256 differs from input!" }
    $MsixHash = (Get-FileHash -LiteralPath $Package -Algorithm SHA256).Hash
    Write-Host "QA_UNSIGNED / NOT CERTIFIED: $Package"
    Write-Host "MSIX SHA256: $MsixHash"
    Write-Host "SOURCE SHA: $SourceSha"
    Write-Host "MANIFEST IDENTITY MATCH: PASS"
    Write-Host "Next: real install/update/uninstall, offline verification, WACK and Partner Center certification."
} catch {
    if (Test-Path -LiteralPath $Package) { Remove-Item -LiteralPath $Package -Force }
    throw
} finally {
    if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
    if (Test-Path -LiteralPath $Check) { Remove-Item -LiteralPath $Check -Recurse -Force }
}
