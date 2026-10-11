# Sales release checklist / 販売直前チェック

## Code gates / コード側
- [x] CSV/XLSX privacy transformation remains independent from UI-language state
- [x] Packaged build enters through `desktop_entry.py`
- [x] Explicit **`言語 / Language`** selector with persisted `日本語 / English`
- [x] Existing product-specific i18n and bilingual smoke infrastructure remains available

## Real Windows / fixture gates / 実機確認
- [ ] Windows 10 / Windows 11 smoke tests
- [ ] 日本語 → English → 日本語 switching and restart persistence
- [ ] 100%, 125%, 150% display scaling
- [ ] Run bilingual_smoke_test.py and smoke_test.py after the language-entry change
- [ ] Test CSV encodings documented by the product and XLSX fixtures
- [ ] Verify masking, pseudonymization, and drop modes on controlled data
- [ ] Verify hidden worksheets and comments are removed when enabled
- [ ] Verify external links/formulas and metadata handling with controlled fixtures
- [ ] Verify duplicate/blank headers and malformed files fail safely
- [ ] Verify original input is never silently overwritten
- [ ] Verify runtime network egress matches the documented local-first boundary
- [ ] Build one-file EXE from a path with spaces/non-ASCII characters
- [ ] Windows Defender/AV scan; record SHA-256
- [ ] Prepare LICENSE/NOTICE/SBOM; lock openpyxl/Python dependencies
- [ ] Authenticode-sign final commercial artifact

Do not mark sales-ready until all applicable unchecked items are complete.
未チェック項目が残っている間は販売完成扱いにしません。
