from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Checkbutton, Entry, Frame, IntVar, Label, Listbox, StringVar, Tk, filedialog, messagebox

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?81[- ]?)?0?\d{1,4}[- ]?\d{1,4}[- ]?\d{3,4}(?!\d)")
EXTERNAL_FORMULA_RE = re.compile(r"\[[^\]]+\.(?:xls|xlsx|xlsm|xlsb|csv)\]", re.I)


def pseudonym(value: object, salt: str) -> str:
    raw = f"{salt}|{value}".encode("utf-8", errors="ignore")
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


def clean_csv(src: Path, out: Path, columns: set[str], mode: str, salt: str) -> dict:
    raw = src.read_bytes()
    decoded = None
    for enc in ("utf-8-sig", "utf-8", "cp932", "utf-16"):
        try:
            decoded = raw.decode(enc)
            break
        except UnicodeDecodeError:
            pass
    if decoded is None:
        decoded = raw.decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(decoded.splitlines()))
    headers = list(rows[0].keys()) if rows else []
    selected = columns or set(headers)
    if mode == "drop":
        out_headers = [h for h in headers if h not in selected]
    else:
        out_headers = headers
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_headers)
        writer.writeheader()
        for row in rows:
            out_row = dict(row)
            for col in selected:
                if col not in out_row:
                    continue
                if mode == "drop":
                    out_row.pop(col, None)
                elif mode == "pseudonymize":
                    out_row[col] = pseudonym(out_row[col], salt)
                else:
                    out_row[col] = mask_value(out_row[col])
            writer.writerow({k: out_row.get(k, "") for k in out_headers})
    return {"rows": len(rows), "columns": len(headers)}


def is_external_formula(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("="):
        return False
    lower = value.lower()
    return bool(EXTERNAL_FORMULA_RE.search(value) or "http://" in lower or "https://" in lower or "\\\\" in value)


def scrub_core_properties(wb) -> None:
    props = wb.properties
    for attr in (
        "creator", "lastModifiedBy", "title", "subject", "description", "keywords",
        "category", "contentStatus", "identifier", "language", "version", "revision",
        "created", "modified", "lastPrinted"
    ):
        if hasattr(props, attr):
            setattr(props, attr, None)


def clean_xlsx(src: Path, out: Path, columns: set[str], mode: str, salt: str, remove_hidden: bool, remove_comments: bool) -> dict:
    from openpyxl import load_workbook

    # keep_links=False is the supported openpyxl path for dropping cached external-workbook links.
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

        headers = {str(cell.value).strip(): cell.column for cell in ws[1] if cell.value is not None}
        selected = columns or set(headers.keys())
        if mode == "drop":
            indices = sorted([headers[c] for c in selected if c in headers], reverse=True)
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
        if mode not in {"mask", "pseudonymize", "drop"}:
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
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
