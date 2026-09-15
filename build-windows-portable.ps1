$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw "Python launcher 'py' is required." }
$Venv = Join-Path $Root ".venv-build"
if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
py -3 -m venv $Venv
$Python = Join-Path $Venv "Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install pyinstaller "openpyxl>=3.1,<4"
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name "ExcelCSVPrivacyCleaner" --collect-all openpyxl windows_app.py
Write-Host "Built: $Root\dist\ExcelCSVPrivacyCleaner.exe"
Write-Host "Before sale: hidden-sheet/comment/external-link fixtures, metadata checks, runtime egress verification, malware scan, Authenticode signing, SHA256."
