"""Immutable approval for a local CSV/XLSX privacy export.

Only a successful preview of the exact source bytes, columns and options
approves a later export. This module never writes to the source.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def export_revision(path: Path, columns: set[str], mode: str, salt: str,
                    remove_hidden: bool, remove_comments: bool) -> str:
    if not columns:
        raise ValueError("処理対象の列を1つ以上選んでください。")
    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("元ファイルが見つからないか、リンクになっています。")
    digest = hashlib.sha256()
    with source.open("rb") as reader:
        for block in iter(lambda: reader.read(1024 * 1024), b""):
            digest.update(block)
    snapshot = {
        "source": str(source.resolve()),
        "sha256": digest.hexdigest(),
        "columns": sorted(columns),
        "mode": mode,
        "private_key": salt if mode == "pseudonymize" else "",
        "remove_hidden": bool(remove_hidden),
        "remove_comments": bool(remove_comments),
    }
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()
