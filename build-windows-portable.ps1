$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw "Python launcher 'py' is required." }
$Venv = Join-Path $Root ".venv-build"
if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
py -3 -m venv $Venv
$Python = Join-Path $Venv "Scripts\python.exe"
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }
& $Python -m pip install pyinstaller "openpyxl>=3.1,<4"
if ($LASTEXITCODE -ne 0) { throw "dependency installation failed." }
& $Python .\bilingual_smoke_test.py
if ($LASTEXITCODE -ne 0) { throw "bilingual_smoke_test.py failed." }
& $Python .\language_standard_smoke_test.py
if ($LASTEXITCODE -ne 0) { throw "language_standard_smoke_test.py failed." }
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name "ExcelCSVPrivacyCleaner" --collect-all openpyxl desktop_entry.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }
Write-Host "Built: $Root\dist\ExcelCSVPrivacyCleaner.exe"
Write-Host "Before sale: run SALES_RELEASE_CHECKLIST.md, hidden-sheet/comment/external-link fixtures, metadata checks, JA/EN UI smoke, runtime egress verification, malware scan, Authenticode signing, SHA256."
