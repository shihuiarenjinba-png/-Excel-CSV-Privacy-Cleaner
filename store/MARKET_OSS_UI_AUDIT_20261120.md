# Market / OSS reference audit — 2026-11-20

Product: **Excel / CSV Privacy Cleaner**

## References reviewed
- Microsoft Presidio: PII detection/anonymization framework for text, images and structured data; its documentation explicitly warns automated detection cannot guarantee finding all sensitive information.
  - https://github.com/microsoft/presidio
- Presidio Structured: identifies PII in structured/semi-structured datasets and supports cell/column redaction.
  - https://microsoft.github.io/presidio/

## Decisions for this product
- Keep deterministic user-selected column operations (mask / pseudonymize / remove) as the primary path.
- Do not claim automatic PII detection is complete; uncertain automated findings must remain reviewable.
- Preserve preview-before-export and non-destructive output-copy behavior.
- Keep pseudonymization strength/integrity checks and spreadsheet-formula edge cases as release blockers when they fail.
- Do not overwrite the original workbook/CSV.
- Treat this document as design evidence only; no third-party code was copied.

## Remaining release evidence
- Real Windows CSV/XLSX runs including formulas, duplicate keys, empty cells, large-ish files and invalid input.
- Open exported XLSX/CSV in a normal consumer workflow and confirm expected values/formulas.
- DPI/visual QA, exact Store version/assets, QA_UNSIGNED MSIX and manifest/hash evidence.
