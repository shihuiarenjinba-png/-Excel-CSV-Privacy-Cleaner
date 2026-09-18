from __future__ import annotations

import csv
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Checkbutton, Entry, Frame, IntVar, Label, Listbox, StringVar, Tk, filedialog, messagebox

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?81[- ]?)?0?\d{1,4}[- ]?\d{1,4}[- ]?\d{3,4}(?!\d)")
EXTERNAL_FORMULA_RE = re.compile(r"\[[^\]]+\.(?:xls|xlsx|xlsm|xlsb|csv)\]", re.I)
TEXT_ENCODINGS = ("utf-8-sig", "utf-8", "cp932", "utf-16")
MODES = {"mask", "pseudonymize", "drop"}
METADATA_EPOCH = datetime(1980, 1, 1, tzinfo=timezone.utc)


def pseudonym(value: object, salt: str) -> str:
    raw = f"{salt}|{value}".encode("utf-8", errors="strict")
    return "USER-" + hashlib.sha256(raw).hexdigest()[:10].upper()


def mask_value(value: object) -> str:
    text = "" if value is None else str(value)
    if EMAIL_RE.fullmatch(text):
        return "[REDACTED_EMAIL]"
    if PHONE_RE.fullmatch(text):
        return "[REDACTED_PHONE]"
    if len(text) <= 2:
        return "*" * len(text)
    return text[:1] + "*" * max(1, len(text) - 2) + text[-1:]


def parse_columns(text: str) -> set[str]:
    return {c.strip() for c in text.split(",") if c.strip()}


def validate_decoded_text(text: str) -> str:
    if "\x00" in text:
        raise UnicodeError("Decoded text contains NUL bytes and appears binary.")
    if text:
        controls = sum(ord(ch) < 32 and ch not in "\t\n\r\f" for ch in text)
        if controls / len(text) > 0.01:
            raise UnicodeError("Decoded text contains too many control characters and appears binary.")
    return text


def decode_text(raw: bytes) -> str:
    last_error: UnicodeError | None = None
    for enc in TEXT_ENCODINGS:
        try:
            return validate_decoded_text(raw.decode(enc))
        except UnicodeError as exc:
            last_error = exc
    raise UnicodeError(f"Unsupported or undecodable CSV encoding; supported encodings: {', '.join(TEXT_ENCODINGS)}") from last_error


def ensure_distinct_paths(src: Path, out: Path) -> None:
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = src.absolute() == out.absolute()
    if same:
        raise ValueError("Refusing to overwrite the original file.")


def validate_headers(raw_headers: list[object], *, label: str) -> list[str]:
    headers = ["" if value is None else str(value).strip() for value in raw_headers]
    if not headers or not any(headers):
        raise ValueError(f"{label} header row is missing or could not be parsed.")
    if any(not header for header in headers):
        raise ValueError(f"{label} contains a blank header. Every processed column must have a unique name.")
    seen: set[str] = set()
    duplicates: list[str] = []
    for header in headers:
        if header in seen and header not in duplicates:
            duplicates.append(header)
        seen.add(header)
    if duplicates:
        raise ValueError(f"Duplicate {label} header(s): " + ", ".join(duplicates))
    return headers


def clean_csv(src: Path, out: Path, columns: set[str], mode: str, salt: str) -> dict:
    ensure_distinct_paths(src, out)
    if mode not in MODES:
        raise ValueError("Mode must be mask, pseudonymize, or drop.")

    decoded = decode_text(src.read_bytes())
    reader = csv.DictReader(decoded.splitlines())
    headers = validate_headers(list(reader.fieldnames or []), label="CSV")
    rows: list[dict] = []
    for line_no, row in enumerate(reader, start=2):
        if None in row:
            raise ValueError(f"CSV row has more fields than the header at line {line_no}.")
        rows.append(row)

    selected = columns or set(headers)
    unknown = sorted(selected - set(headers))
    if columns and unknown:
        raise ValueError("Requested column(s) not found: " + ", ".join(unknown))

    if mode == "drop":
        out_headers = [h for h in headers if h not in selected]
        if not out_headers:
            raise ValueError("Refusing to drop every CSV column.")
    else:
        out_headers = headers

    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            out_row = dict(row)
            for col in selected:
                if mode == "drop":
                    out_row.pop(col, None)
                elif mode == "pseudonymize":
                    out_row[col] = pseudonym(out_row.get(col, ""), salt)
                else:
                    out_row[col] = mask_value(out_row.get(col, ""))
            writer.writerow({k: out_row.get(k, "") for k in out_headers})
    return {"rows": len(rows), "columns": len(headers)}


def is_external_formula(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("="):
        return False
    lower = value.lower()
    return bool(EXTERNAL_FORMULA_RE.search(value) or "http://" in lower or "https://" in lower or "\\\\" in value)


def scrub_core_properties(wb) -> None:
    props = wb.properties
    # openpyxl requires valid datetimes when serializing core created/modified
    # properties. A fixed UTC epoch removes source timestamps without making the
    # generated XLSX unsaveable on current supported openpyxl versions. Current
    # openpyxl rewrites `modified` to the save time, which also prevents the
    # source document's value from persisting.
    for attr in ("created", "modified"):
        if hasattr(props, attr):
            setattr(props, attr, METADATA_EPOCH)
    for attr in (
        "creator", "lastModifiedBy", "title", "subject", "description", "keywords",
        "category", "contentStatus", "identifier", "language", "version", "revision",
        "lastPrinted"
    ):
        if hasattr(props, attr):
            setattr(props, attr, None)


def clean_xlsx(src: Path, out: Path, columns: set[str], mode: str, salt: str, remove_hidden: bool, remove_comments: bool) -> dict:
    from openpyxl import load_workbook

    ensure_distinct_paths(src, out)
    if mode not in MODES:
        raise ValueError("Mode must be mask, pseudonymize, or drop.")

    wb = load_workbook(src, keep_links=False)
    scrub_core_properties(wb)
    removed_sheets = 0
    removed_external_formulas = 0
    removed_external_hyperlinks = 0

    for ws in list(wb.worksheets):
        if remove_hidden and ws.sheet_state != "visible":
            wb.remove(ws)
            removed_sheets += 1
            continue

        raw_headers = [cell.value for cell in ws[1]]
        if any(value not in (None, "") for value in raw_headers):
            header_names = validate_headers(raw_headers, label=f"worksheet '{ws.title}'")
            headers = {name: index + 1 for index, name in enumerate(header_names)}
        else:
            headers = {}

        selected = columns or set(headers.keys())
        unknown = sorted(selected - set(headers.keys()))
        if columns and unknown:
            raise ValueError(f"Sheet '{ws.title}' is missing requested column(s): " + ", ".join(unknown))

        if mode == "drop":
            indices = sorted([headers[c] for c in selected if c in headers], reverse=True)
            if indices and len(indices) >= ws.max_column:
                raise ValueError(f"Refusing to drop every column from sheet '{ws.title}'.")
            for idx in indices:
                ws.delete_cols(idx, 1)
        else:
            for col in selected:
                idx = headers.get(col)
                if not idx:
                    continue
                for row in range(2, ws.max_row + 1):
                    cell = ws.cell(row=row, column=idx)
                    if cell.value in (None, ""):
                        continue
                    cell.value = pseudonym(cell.value, salt) if mode == "pseudonymize" else mask_value(cell.value)

        for row in ws.iter_rows():
            for cell in row:
                if remove_comments and cell.comment is not None:
                    cell.comment = None
                if is_external_formula(cell.value):
                    cell.value = "[REMOVED_EXTERNAL_FORMULA]"
                    removed_external_formulas += 1
                if cell.hyperlink is not None:
                    target = getattr(cell.hyperlink, "target", None)
                    if target and not str(target).startswith("#"):
                        cell.hyperlink = None
                        removed_external_hyperlinks += 1

    if not wb.worksheets:
        raise ValueError("All worksheets would be removed. Keep at least one visible sheet.")
    wb.save(out)
    return {
        "sheets": len(wb.worksheets),
        "removed_hidden_sheets": removed_sheets,
        "removed_external_formulas": removed_external_formulas,
        "removed_external_hyperlinks": removed_external_hyperlinks,
    }


class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Excel / CSV Privacy Cleaner — Windows")
        self.root.geometry("920x650")
        self.file: Path | None = None
        self.columns = StringVar()
        self.mode = StringVar(value="mask")
        self.salt = StringVar(value="local-default")
        self.remove_hidden = IntVar(value=1)
        self.remove_comments = IntVar(value=1)

        head = Frame(root, padx=12, pady=12)
        head.pack(fill="x")
        Label(head, text="Excel / CSV Privacy Cleaner", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(head, text="Create a safer copy locally. Original files are never overwritten.").pack(anchor="w")

        controls = Frame(root, padx=12)
        controls.pack(fill="x")
        Button(controls, text="Choose CSV/XLSX", width=18, command=self.choose).pack(side=LEFT)
        Button(controls, text="Export safer copy", width=18, command=self.export).pack(side=LEFT, padx=8)

        opts = Frame(root, padx=12, pady=10)
        opts.pack(fill="x")
        Label(opts, text="Columns to process (comma separated; blank = all columns):").pack(anchor="w")
        Entry(opts, textvariable=self.columns).pack(fill="x", pady=(2, 8))
        Label(opts, text="Mode: mask / pseudonymize / drop").pack(anchor="w")
        Entry(opts, textvariable=self.mode).pack(fill="x", pady=(2, 8))
        Label(opts, text="Pseudonym salt (keep stable if you need consistent IDs):").pack(anchor="w")
        Entry(opts, textvariable=self.salt).pack(fill="x", pady=(2, 8))
        Checkbutton(opts, text="Remove hidden worksheets (XLSX)", variable=self.remove_hidden).pack(anchor="w")
        Checkbutton(opts, text="Remove cell comments (XLSX)", variable=self.remove_comments).pack(anchor="w")

        self.listbox = Listbox(root, font=("Consolas", 10))
        self.listbox.pack(fill=BOTH, expand=True, padx=12, pady=12)

    def choose(self):
        p = filedialog.askopenfilename(title="Choose CSV or XLSX", filetypes=[("Data files", "*.csv *.xlsx"), ("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if not p:
            return
        self.file = Path(p)
        self.listbox.delete(0, END)
        self.listbox.insert(END, str(self.file))

    def export(self):
        if not self.file:
            return messagebox.showinfo("Privacy Cleaner", "Choose a file first.")
        mode = self.mode.get().strip().lower()
        if mode not in MODES:
            return messagebox.showerror("Privacy Cleaner", "Mode must be mask, pseudonymize, or drop.")
        ext = self.file.suffix.lower()
        if ext not in {".csv", ".xlsx"}:
            return messagebox.showerror("Privacy Cleaner", "Only CSV and XLSX are supported.")
        out = filedialog.asksaveasfilename(defaultextension=ext, initialfile=f"{self.file.stem}_safe{ext}", filetypes=[("Output", f"*{ext}")])
        if not out:
            return
        try:
            cols = parse_columns(self.columns.get())
            if ext == ".csv":
                stats = clean_csv(self.file, Path(out), cols, mode, self.salt.get())
            else:
                stats = clean_xlsx(self.file, Path(out), cols, mode, self.salt.get(), bool(self.remove_hidden.get()), bool(self.remove_comments.get()))
            self.listbox.insert(END, f"SAVED {out} | {stats}")
            messagebox.showinfo("Privacy Cleaner", f"Safer copy saved:\n{out}")
        except Exception as exc:
            messagebox.showerror("Privacy Cleaner", str(exc))


def main():
    from i18n import install_bilingual_ui

    root = Tk()
    App(root)
    install_bilingual_ui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
