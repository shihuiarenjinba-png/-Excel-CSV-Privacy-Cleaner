# Excel / CSV Privacy Cleaner — Simplified Windows Candidate

## User experience
- Select CSV/XLSX, and **check only the columns** to process; none selected by default.
- Pick `mask` (partial masking), `pseudonymize` (repeatable keyed SHA256-derived identifier) or `drop` (remove a column).
- Preview a small in-memory example of before and after. Preview is illustrative and not a privacy guarantee; other sheets and metadata are not fully shown.
- Export to a **new filename** only; existing files and originals cannot be overwritten by normal output paths.
- The pseudonymization key is random per application launch. Retain it securely if consistent mapping across runs is required. Advanced settings contain key, hidden worksheet and comment options.
- XLSX worksheets may have different column schemas. Selected names are applied only to sheets containing the column. Missing requested columns are listed per sheet in processing statistics.

## Safety boundaries
- CSV round-trip aims to preserve newlines, Japanese encodings and unselected values, but Excel formula injection in any data remains a user review concern.
- XLSX formula links, complex Excel objects, macros, charts, embedded images and other hidden content are **not** guaranteed removed. Dropping columns may affect dependent formulas. Test with an independent Excel reader before external sharing.
- Hash-derived pseudonyms are deterministic, not encryption or irreversible anonymization. Predictable or exposed keys allow linkage; keep keys private.
- Changing the values of selected columns is not equivalent to certifying the workbook free of personal data.
- A limited preview is not a complete audit.

## Execute and test on Windows
```powershell
py -3 -m pip install "openpyxl>=3.1,<4"
py -3 -m compileall -q windows_app.py i18n.py smoke_test.py tests
py -3 .\smoke_test.py
py -3 -m unittest discover -s tests -v
py -3 .\bilingual_smoke_test.py
py -3 .\windows_app.py
```

`build-windows-portable.ps1` creates a portable development EXE. This is **not** Microsoft Store MSIX.

## Store release gate — HOLD
Pending executed regression tests, CSV large-file and Excel complex-format fixtures, real Windows GUI/DPI acceptance, memory/performance tests, clean install and removal, formal MSIX identity, MSIX package and Store certification, commercial license and dependency notices, privacy terms, screenshots and final product pricing.
