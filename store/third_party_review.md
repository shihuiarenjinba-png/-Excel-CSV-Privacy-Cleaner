# Third-party attribution and release rights review (PENDING)

Source of truth: `requirements-windows.lock.txt` in the exact release commit. This is an inventory to be reviewed, **not a declaration that every license is cleared**.

## Core runtime
- CPython: verify redistribution of interpreter/runtime with PyInstaller and carry required notices
- openpyxl 3.1.5, et_xmlfile 2.0.0: verify upstream license text and attribution/NOTICE obligations
- PyInstaller 6.22.3, pyinstaller-hooks-contrib 2026.8, altgraph 0.17.5, packaging 26.3, pefile 2024.8.26, pywin32-ctypes 0.2.3, setuptools 84.0.0, pip 26.2.1: verify actual inclusion and licenses
- Windows packaging / icons / fonts: only use assets with a documented commercial license; no borrowed logos or screenshots
- No claim of included license files unless they exist inside the final distributable

## To mark this PASS
1. Extract exact license and version list for **locked, installed** dependencies from final build environment; detect transitive bundled runtime files and DLLs.
2. Create the actual bundled LICENSE/NOTICE and verify its presence after MSIX roundtrip unpacking.
3. Record copyright notices and license constraints, including current build tooling and source code redistribution.
4. Confirm own product end-user license, refund/support policy, registered publisher/brand usage and legal review.
5. Record a SHA256 proof in the release-evidence manifest, reflecting only the final release commit.

**Gate: HOLD. No blanket assertion of license compliance.**
