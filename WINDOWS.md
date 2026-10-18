# Excel / CSV Privacy Cleaner — Simplified Windows Candidate

## User experience
- Select CSV/XLSX, and **check only the columns** to process; none selected by default.
- Pick `mask` (partial masking), `pseudonymize` (repeatable keyed SHA256-derived identifier) or `drop` (remove a column).
- Preview a small in-memory example of before and after. Preview is illustrative and not a privacy guarantee; other sheets and metadata are not fully shown.
- Export to a **new filename** only; existing files and originals cannot be overwritten by normal output paths.
- The pseudonymization key is random per application launch. Retain it securely if consistent mapping across runs is required. Advanced settings contain key, hidden worksheet and comment options.
- XLSX worksheets may have different column schemas. Selected names are applied only to sheets containing the column. Missing requested columns are listed per sheet in processing statistics.

## Safety boundaries
- CSV export refuses formula-like values in both headers and output cells (including unselected columns). This is a conservative check, not a guarantee against every spreadsheet injection trick. Japanese encodings and quoted newlines still need real Windows regression proof.
- XLSX formula links, complex Excel objects, macros, charts, embedded images and other hidden content are **not** guaranteed removed. Dropping columns may affect dependent formulas. Test with an independent Excel reader before external sharing.
- Hash-derived pseudonyms are deterministic, not encryption or irreversible anonymization. Predictable or exposed keys allow linkage; keep keys private.
- Changing the values of selected columns is not equivalent to certifying the workbook free of personal data.
- A limited preview is not a complete audit.

- Input caps: CSV up to 25 MiB, XLSX compressed up to 15 MiB and expanded ZIP content up to 160 MiB, at most 100,000 data rows/sheet. Larger inputs are refused before writing; these thresholds limit resource exhaustion but do not certify safety.
- Formula cells in selected XLSX columns are blocked for partial masking; explicit pseudonymize/drop may be used, with dependent spreadsheet formulas requiring separate review. XLSX macro payloads are rejected.

## Execute and test on Windows
```powershell
py -3 -m pip install "openpyxl>=3.1,<4"
py -3 -m compileall -q windows_app.py i18n.py smoke_test.py tests
py -3 .\smoke_test.py
py -3 -m unittest discover -s tests -v
py -3 .\bilingual_smoke_test.py
py -3 .\windows_app.py
```

When hosted CI never starts, run `store/run-windows-qa.ps1` on a clean Windows checkout to capture actual synthetic test results, commit SHA and log digest. **Running this script is still not real human GUI/MSIX certification.**

`build-windows-portable.ps1` creates a portable development EXE. This is **not** Microsoft Store MSIX.

## Store release gate — HOLD
Pending executed regression tests, CSV large-file and Excel complex-format fixtures, real Windows GUI/DPI acceptance, memory/performance tests, clean install and removal, formal MSIX identity, MSIX package and Store certification, commercial license and dependency notices, privacy terms, screenshots and final product pricing.
