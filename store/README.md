# Commercial release preparation (NOT approved for sale)

This directory contains **drafts and locally executable validation tools**, not a completed Store submission or a real MSIX.

## Business decision
Primary first-sale candidate: Excel / CSV Privacy Cleaner. Proposed Japanese buy-once test price **¥980** initial experiment (compare with **¥1,480**; Partner Center market price *not set*). Audience: small-office operators preparing selected CSV/XLSX columns for sharing. Paid value is a simple, explicit, local workflow, not guaranteed anonymization. See `monetization_plan.md` and `listing_ja.md` / `listing_en.md`.

## Current safety and size restrictions

CSV supports up to 25 MiB and 100,000 rows. XLSX accepts up to 15 MiB compressed, 160 MiB expanded and 100,000 rows per sheet. These caps must be shown to prospective customers; they are not a claim that the product processes unlimited datasets. Formula-shaped CSV cells or headers can block export. This is deliberately conservative: never silently change unselected cells.

## Local Windows proof when hosted runners fail

Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\store\run-windows-qa.ps1` from a clean checked-out `improve/simple-column-ui-20261018` branch. It creates unique QA logs and a result JSON under `Documents\ExcelCSVPrivacyCleaner-QA`; it never marks GUI/MSIX/Store certification as passed. If `python` or pinned dependencies cannot run, the evidence records HOLD. The generated report is not customer-facing and should not include personal data.

## Product-frame readiness gate (before reserving a name)

See [PHASE1_REGISTRATION_READINESS.md](PHASE1_REGISTRATION_READINESS.md). Once test/GUI/privacy/license evidence exists for the exact commit, run `py -3 .\store\release_gate.py --stage registration --evidence .\store\actual-evidence.json`. This checks five pre-registration quality gates **without requiring a Partner Center identity or MSIX**. Passing the evidence check is not automatic permission to publish or reserve a name; verify name rights, timing and customer value manually. Current registration decision: **HOLD**.

## Sequence to create a Store candidate
1. Complete automated and real-user GUI tests on a clean Windows 10 and Windows 11 PC; record evidence outside any source-data folder.
2. Supply only **actual Partner Center** package IdentityName, Publisher CN, and PublisherDisplayName, plus real 50/44/150 PNG assets and final product name. Do not use synthetic/test identity for sale.
3. Run the existing portable EXE build from this branch: `build-windows-portable.ps1` and validate its hash.
4. With Windows SDK MakeAppx.exe on PATH, run the packager with the same publisher/name as Partner Center:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\store\build-store-msix.ps1 `
  -IdentityName 'ACTUAL.NAME.FROM.PARTNER.CENTER' `
  -Publisher 'CN=ACTUAL PUBLISHER FROM PARTNER CENTER' `
  -PublisherDisplayName 'ACTUAL DISPLAY NAME' `
  -DisplayName 'Excel / CSV Privacy Cleaner' `
  -AssetsDirectory 'C:\real-store-assets' `
  -ExePath '.\dist\ExcelCSVPrivacyCleaner.exe' `
  -Version '1.0.0.0'
```

Values above are **instructions, not real identity values** and will be rejected as placeholders. Output is an unsigned MSIX **candidate**, not a Store acceptance result. This script checks the exe hash after packing/unpacking but does not install it or prove GUI operation.

5. Test installation/update/uninstall, settings persistence, full-trust activation, Store preflight, malicious input fixtures, Windows App Certification Kit and asset correctness.
6. Confirm Store listing screenshots, working support and privacy URLs, real target price, age rating, third-party license audit, and product identity matches exact manifest fields.
7. Store MSIX distributions are signed by Microsoft after successful certification. A separately distributed EXE/MSI needs its own trusted signing. Do **not** apply outdated claims that a CA certificate must be purchased for Store MSIX. Official docs: https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/package-version-numbering and https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-started-with-the-microsoft-store
8. Preserve every proof file and its SHA256. Copy `evidence.template.json` to an actual evidence manifest, update the exact **release commit SHA**, and run:

```powershell
py -3 .\store\release_gate.py --evidence .\store\actual-evidence.json
```

The release gate starts in HOLD, verifies referenced file checksums, and **does not approve submission or certification** even if proofs are present. Review results manually; do not fabricate or infer test passes from failed GitHub Actions.

## Current blocker — GitHub-hosted runners

Across several independent repos, both `windows-latest` and `ubuntu-latest` jobs have failed before their first step. Jobs show empty runner names and no step logs. This is **not proof of broken test code**. Review Actions quota/billing/runner availability, account permissions, possible provider incident and retry after correcting the environment. In the meantime use real Windows commands on an independent machine, preserve console output and source SHA. No result should be marked PASS until it actually runs.

**Launch gate: HOLD. No package, identity, Store price, certification, or customer payment is asserted to exist.**
