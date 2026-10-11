# Excel / CSV Privacy Cleaner — Windows MVP

## Implemented

- CSV and XLSX input
- Column-level `mask`, deterministic `pseudonymize`, or `drop`
- CSV quoted cells retain embedded newlines, commas, quotes, surrounding whitespace, and unselected values after round-trip processing
- Original file is never overwritten
- XLSX hidden-sheet removal
- XLSX cell-comment removal
- XLSX external-link collection cleared on output
- Heterogeneous XLSX worksheets are supported: only matching requested columns are transformed, while non-matching worksheets and non-target cells are preserved
- XLSX results include per-sheet processed/skipped status and missing requested columns
- Stable pseudonyms using a user-controlled salt

## Run

```powershell
py -3 -m pip install openpyxl
py -3 .\windows_app.py
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-portable.ps1
```

Output: `dist\ExcelCSVPrivacyCleaner.exe`

## Sales note

Formulas are preserved where openpyxl can preserve them, but complex Excel features/macros are outside this `.xlsx` MVP. `.xlsm` is not accepted. Before sale test hidden sheets, comments, external links, formulas, Japanese encodings, large CSVs, Windows 10/11, malware scan, signing and SHA256.
