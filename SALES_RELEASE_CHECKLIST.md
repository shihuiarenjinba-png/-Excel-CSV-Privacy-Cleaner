# Excel / CSV Privacy Cleaner — Paid launch gate (2026-10-18)

**CURRENT STATUS: HOLD.** None of the following checks is satisfied merely by committing code or drafting listings.

## Before creating a Partner Center product frame
- [ ] Run actual Windows code, GUI, hostile-file, egress and dependency-license checks; record immutable SHA256 evidence
- [ ] Use `store/release_gate.py --stage registration --evidence <file>` with the exact checked commit SHA and inspect its output
- [ ] Confirm paid customer use case, free competitors, price hypothesis and Microsoft Store name rights; then manually authorize product-name reservation
- [ ] Do not reserve the name only because source code or test definitions exist. Current registration **HOLD**.

## Product and customer acceptance
- [x] Short path: choose a file → select columns via checkboxes → choose transform → preview → export another file
- [x] Existing source and export files protected by exclusive-create logic
- [x] Dangerous spreadsheet-formula-shaped CSV values rejected before an export is created (unit test added; execution pending)
- [x] JA/EN labels and local first-use instructions updated (visual review pending)
- [ ] 5 first-time testers finish 3 realistic synthetic tasks without guidance, no severe errors
- [ ] Japanese/English UI at 100%, 125%, 150% scaling; keyboard and accessible navigation, Windows 10 and 11

## Safety and regression
- [ ] GitHub Actions or Windows local tests executed and passed (current hosted runners never start job steps)
- [ ] CSV encoding, quoted multiline, long Unicode, bad headers and formula injection tests
- [ ] XLSX hidden sheets, comments, formulas, hyperlinks, large-file and complex workbook limitations
- [ ] Source/output immutability under errors and restarts
- [ ] Actual runtime network/telemetry/egress check
- [ ] Dependencies, Python/openpyxl licensing and NOTICE approved by legal/release owner

## Microsoft Store submission
- [ ] Reserved product name and real Partner Center identity supplied and verified
- [ ] True product package identity and semantic version as required by Store
- [ ] Store assets: authentic screenshots, 44/150 icons, 50px Store logo, other required sizes verified
- [ ] Generated **real-identity** MSIX; SHA256 and unpacked EXE hash checked
- [ ] Actual MSIX install → launch → update → settings persistence → uninstall on Windows
- [ ] Windows App Certification Kit and real Partner Center certification
- [ ] Support/privacy URLs live and reviewed, age rating and accurate Store copy
- [ ] Actual paid price tier + target markets in Partner Center, refund/tax/support policy
- [ ] Sales-owner GO recorded after review of immutable per-commit evidence manifest

## Signing nuance
**Microsoft Store distribution of MSIX:** Store signs accepted packages. No commercial CA code-signing purchase required solely for Store-submitted MSIX. **Separate EXE/MSI distribution:** Authenticode sign yourself. Test/dev self-signed packages are not launch artifacts.

## Business gate
- [x] Competing free PDF/EXIF utilities factored into first-product choice
- [x] Buy-once price hypotheses (¥980 initial; ¥1,480 comparison) and gross/net scenarios documented
- [ ] Actual Store price confirmed (not presumed supported in exact yen amount)
- [ ] Real purchase-intent interviews or beta validation
- [ ] Store listing impression → conversion → refund/support metrics after public release

Use `store/release_gate.py` for evidence inspection. Neither an empty JSON template nor a successful pack command makes a sale-ready product.
