"""Local evidence gate for a prospective Microsoft Store release.

This is a blocking checklist, not an automated certification or a license grant.
Never substitutes for actual Windows acceptance, Partner Center or Microsoft review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

GATES = {
    "functional_tests": "Complete existing and added CSV/XLSX tests",
    "human_gui": "Human Windows 10/11 GUI, JA/EN, 100/125/150% DPI and keyboard review",
    "hostile_fixtures": "Corrupt, large, formula-injection, hidden-sheet and overwrite fixtures",
    "privacy_egress": "Runtime offline/egress verification and truthful privacy disclosures",
    "dependencies_license": "Product license, openpyxl/Python/other dependency licenses and notices",
    "store_identity": "Real Partner Center package identity and publisher equality",
    "msix_package": "MSIX version, structure, SHA256 and actual intended contents",
    "installation_lifecycle": "Install, launch, update, preserve settings and clean uninstall",
    "windows_certification": "Windows App Certification Kit and Microsoft Store certification",
    "store_listing": "Final JA/EN product text, screenshots, icon and support/privacy URLs",
    "commerce": "Paid app tier, target markets, expected net receipts and refund/support policy",
}


# These are gates to reserve a product name, not to build or submit a Store MSIX.
REGISTRATION_GATES = (
    "functional_tests", "human_gui", "hostile_fixtures",
    "privacy_egress", "dependencies_license",
)


def file_digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            sha.update(chunk)
    return sha.hexdigest()


def check_evidence(root: Path, payload: dict, actual_commit: str, *, required_gates=None) -> list[str]:
    """Returns exact missing/invalid gate IDs. Never assumes a gate has passed."""
    faults = []
    required_gates = tuple(GATES) if required_gates is None else tuple(required_gates)
    if payload.get("schema_version") != 1:
        faults.append("schema_version")
    if payload.get("commit_sha") != actual_commit or not re.fullmatch(r"[0-9a-f]{40}", actual_commit):
        faults.append("commit_sha")
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        return sorted(set(faults + list(required_gates)))
    base = root.resolve(strict=True)
    for key in required_gates:
        record = gates.get(key)
        if not isinstance(record, dict) or record.get("status") != "PASS":
            faults.append(key)
            continue
        relative = record.get("evidence_file")
        declared_sha = record.get("sha256")
        if not isinstance(relative, str) or not isinstance(declared_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", declared_sha):
            faults.append(key)
            continue
        try:
            location = (base / relative).resolve(strict=True)
            if not location.is_relative_to(base) or not location.is_file() or location.is_symlink():
                faults.append(key)
                continue
            if file_digest(location) != declared_sha:
                faults.append(key)
        except (OSError, RuntimeError, ValueError):
            faults.append(key)
    return sorted(set(faults))


def main() -> int:
    parser = argparse.ArgumentParser(description="Local candidate release evidence check; always fail closed.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--stage", choices=("registration", "sale"), default="sale",
                        help="registration checks quality before creating a Store product frame")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL, timeout=8,
        ).strip()
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        if not isinstance(evidence, dict):
            raise ValueError("Evidence must be a JSON object.")
        faults = check_evidence(root, evidence, commit,
                                required_gates=(REGISTRATION_GATES if args.stage == "registration" else None))
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print("HOLD: evidence could not be verified: " + str(error))
        return 2
    if faults:
        print("HOLD: release conditions not evidenced: " + ", ".join(faults))
        return 2
    if args.stage == "registration":
        print("REGISTRATION_EVIDENCE_COMPLETE_FOR_MANUAL_REVIEW_ONLY")
        print("Check product differentiation, name rights and release timing manually.")
        print("This does NOT approve MSIX upload or commercial sale.")
    else:
        print("EVIDENCE_COMPLETE_FOR_MANUAL_REVIEW_ONLY")
        print("No Store submission or commercial release is approved by this tool.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
