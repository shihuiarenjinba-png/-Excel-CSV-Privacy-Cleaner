from __future__ import annotations

import csv
import hashlib
import io
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Canvas, Checkbutton, Entry, Frame, IntVar, Label, Listbox, Scrollbar, StringVar, Tk, filedialog, messagebox
from tkinter import ttk

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


def csv_formula_risk(value: object) -> bool:
    """Conservatively block spreadsheet-formula-like CSV cells before export.

    CSV can become executable formulas when opened by spreadsheet software.
    This checks the actual output values; it does not mutate unselected cells.
    """
    if value is None:
        return False
    content = str(value).lstrip(" \\t\\r\\n")
    if not content:
        return False
    if content[0] in ("=", "+", "@"):
        return True
    if content.startswith("-"):
        return not bool(re.fullmatch(r"-[0-9]+(?:[.][0-9]+)?", content))
    return False


def clean_csv(src: Path, out: Path, columns: set[str], mode: str, salt: str) -> dict:
    ensure_distinct_paths(src, out)
    if mode not in MODES:
        raise ValueError("Mode must be mask, pseudonymize, or drop.")

    decoded = decode_text(src.read_bytes())
    # csv.DictReader must receive a newline-aware stream. splitlines() removes
    # embedded newlines from quoted fields and silently changes unselected data.
    reader = csv.DictReader(io.StringIO(decoded, newline=""))
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

    transformed_rows = []
    for row_index, row in enumerate(rows, start=2):
        out_row = dict(row)
        for col in selected:
            if mode == "drop":
                out_row.pop(col, None)
            elif mode == "pseudonymize":
                out_row[col] = pseudonym(out_row.get(col, ""), salt)
            else:
                out_row[col] = mask_value(out_row.get(col, ""))
        for column in out_headers:
            if csv_formula_risk(out_row.get(column)):
                raise ValueError(
                    f"Possible spreadsheet formula in output row {row_index}, column '{column}'. "
                    "Select and pseudonymize/drop that column or remove the risky value. "
                    "No file was exported."
                )
        transformed_rows.append({k: out_row.get(k, "") for k in out_headers})
    created = False
    try:
        with out.open("x", encoding="utf-8-sig", newline="") as fh:
            created = True
            writer = csv.DictWriter(fh, fieldnames=out_headers)
            writer.writeheader()
            for out_row in transformed_rows:
                writer.writerow(out_row)
    except BaseException:
        if created:
            out.unlink(missing_ok=True)
        raise
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
    sheet_results: list[dict] = []

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

        requested = columns or set(headers.keys())
        selected = requested & set(headers.keys())
        missing = sorted(requested - set(headers.keys())) if columns else []
        sheet_result = {
            "sheet": ws.title,
            "status": "processed" if selected else "skipped_no_matching_columns",
            "processed_columns": sorted(selected),
            "missing_requested_columns": missing,
            "rows": max(0, ws.max_row - 1),
        }

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
        sheet_results.append(sheet_result)

    if not wb.worksheets:
        raise ValueError("All worksheets would be removed. Keep at least one visible sheet.")
    created = False
    try:
        with out.open("xb") as handle:
            created = True
            wb.save(handle)
    except BaseException:
        if created:
            out.unlink(missing_ok=True)
        raise
    return {
        "sheets": len(wb.worksheets),
        "removed_hidden_sheets": removed_sheets,
        "removed_external_formulas": removed_external_formulas,
        "removed_external_hyperlinks": removed_external_hyperlinks,
        "sheet_results": sheet_results,
    }


def available_columns(path: Path) -> list[str]:
    """Read only headers for the selection UI; never alter the input."""
    ext = path.suffix.lower()
    if ext == ".csv":
        sample = decode_text(path.read_bytes())
        reader = csv.reader(io.StringIO(sample, newline=""))
        return validate_headers(next(reader, []), label="CSV")
    if ext == ".xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True, keep_links=False)
        try:
            names = []
            seen = set()
            for ws in wb.worksheets:
                if ws.sheet_state != "visible":
                    continue
                first = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), [])
                if not any(value not in (None, "") for value in first):
                    continue
                for name in validate_headers(list(first), label=f"worksheet '{ws.title}'"):
                    if name not in seen:
                        names.append(name)
                        seen.add(name)
            if not names:
                raise ValueError("No visible worksheet has a valid header row.")
            return names
        finally:
            wb.close()
    raise ValueError("Only CSV and XLSX inputs are supported.")


def preview_changes(path: Path, columns: set[str], mode: str, salt: str, limit: int = 4) -> list[str]:
    """Short in-memory illustrative before/after preview; not a security audit."""
    if not columns:
        return ["Select at least one column to preview."]
    rows = []
    if path.suffix.lower() == ".csv":
        decoded = decode_text(path.read_bytes())
        reader = csv.DictReader(io.StringIO(decoded, newline=""))
        validate_headers(list(reader.fieldnames or []), label="CSV")
        for row in reader:
            if None in row:
                raise ValueError("CSV data has more fields than headers.")
            rows.append(("CSV", row))
            if len(rows) >= limit:
                break
    else:
        from openpyxl import load_workbook
        wb = load_workbook(path, read_only=True, keep_links=False, data_only=False)
        try:
            for ws in wb.worksheets:
                if ws.sheet_state != "visible":
                    continue
                values = ws.iter_rows(values_only=True)
                header = next(values, ())
                if not any(value not in (None, "") for value in header):
                    continue
                names = validate_headers(list(header), label=ws.title)
                if not (set(names) & columns):
                    continue
                for values_row in values:
                    rows.append((ws.title, dict(zip(names, values_row))))
                    if len(rows) >= limit:
                        break
                if len(rows) >= limit:
                    break
        finally:
            wb.close()
    lines = ["Preview only: other sheets, metadata and formulas are not shown here."]
    for sheet, row in rows:
        for col in sorted(columns & row.keys()):
            before = "" if row.get(col) is None else str(row[col])
            after = "(column removed)" if mode == "drop" else (
                pseudonym(row[col], salt) if mode == "pseudonymize" else mask_value(row[col])
            )
            lines.append(f"[{sheet}] {col}: {before[:65]!r}  →  {after[:65]!r}")
    if len(lines) == 1:
        lines.append("No matching data rows in the preview sample.")
    return lines


class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Excel / CSV Privacy Cleaner — Windows")
        self.root.geometry("940x720")
        self.file: Path | None = None
        self.mode = StringVar(value="mask")
        self.salt = StringVar(value=secrets.token_hex(16))
        self.remove_hidden = IntVar(value=1)
        self.remove_comments = IntVar(value=1)
        self.column_vars: dict[str, IntVar] = {}
        self.advanced_visible = False
        self.show_key = IntVar(value=0)
        self.key_entry = None

        head = Frame(root, padx=12, pady=12)
        head.pack(fill="x")
        Label(head, text="Excel / CSV Privacy Cleaner", font=("Segoe UI", 19, "bold")).pack(anchor="w")
        Label(head, text="Select file → check columns → choose method → preview → export a new copy.").pack(anchor="w")
        toolbar = Frame(root, padx=12)
        toolbar.pack(fill="x")
        Button(toolbar, text="1  Choose file", command=self.choose, width=17).pack(side=LEFT)
        Button(toolbar, text="4  Preview", command=self.preview, width=14).pack(side=LEFT, padx=8)
        Button(toolbar, text="5  Export copy", command=self.export, width=17).pack(side=LEFT)

        Label(root, text="2  Check the columns to process (none selected by default)", anchor="w").pack(fill="x", padx=12, pady=(12, 2))
        column_box = Frame(root, padx=12)
        column_box.pack(fill="x")
        self.canvas = Canvas(column_box, height=165, highlightthickness=1)
        scroll = Scrollbar(column_box, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side=LEFT, fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.check_area = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.check_area, anchor="nw")
        self.check_area.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        options = Frame(root, padx=12, pady=9)
        options.pack(fill="x")
        Label(options, text="3  Processing method:").pack(side=LEFT)
        ttk.Combobox(options, textvariable=self.mode,
                     values=("mask", "pseudonymize", "drop"), state="readonly", width=17).pack(side=LEFT, padx=10)
        Label(options, text="mask: partly hide | pseudonymize: ID | drop: remove").pack(side=LEFT)
        Button(options, text="Advanced options", command=self.toggle_advanced).pack(side=LEFT)
        self.advanced = Frame(root, padx=12)
        Label(self.advanced, text="Pseudonym key (keep private; use same key for consistent IDs):").pack(anchor="w")
        self.key_entry = Entry(self.advanced, textvariable=self.salt, show="•")
        self.key_entry.pack(fill="x")
        Checkbutton(self.advanced, text="Show pseudonym key", variable=self.show_key,
                    command=self.toggle_key_visibility).pack(anchor="w")
        Checkbutton(self.advanced, text="Remove hidden worksheets (XLSX)", variable=self.remove_hidden).pack(anchor="w")
        Checkbutton(self.advanced, text="Remove cell comments (XLSX)", variable=self.remove_comments).pack(anchor="w")

        Label(root, text="Preview and processing results (example rows; verify exported file yourself):").pack(anchor="w", padx=12, pady=(12, 2))
        self.listbox = Listbox(root, font=("Consolas", 10))
        self.listbox.pack(fill=BOTH, expand=True, padx=12, pady=(0, 12))
        self.listbox.insert(END, "Choose a CSV or XLSX file to begin.")

    def toggle_key_visibility(self):
        self.key_entry.configure(show="" if self.show_key.get() else "•")

    def toggle_advanced(self):
        self.advanced_visible = not self.advanced_visible
        if self.advanced_visible:
            self.advanced.pack(fill="x", before=self.listbox)
        else:
            self.advanced.pack_forget()

    def selected_columns(self) -> set[str]:
        return {name for name, flag in self.column_vars.items() if flag.get()}

    def choose(self):
        p = filedialog.askopenfilename(
            parent=self.root, title="Choose CSV or XLSX",
            filetypes=[("Data files", "*.csv *.xlsx"), ("CSV", "*.csv"), ("Excel", "*.xlsx")],
        )
        if not p:
            return
        candidate = Path(p)
        try:
            names = available_columns(candidate)
            if len(names) > 250:
                raise ValueError("Over 250 distinct columns: use a smaller input or split it before processing.")
        except Exception as exc:
            messagebox.showerror("Cannot read columns", str(exc))
            return
        self.file = candidate
        for widget in self.check_area.winfo_children():
            widget.destroy()
        self.column_vars = {}
        for name in names:
            state = IntVar(value=0)
            self.column_vars[name] = state
            Checkbutton(self.check_area, text=name, variable=state, anchor="w").pack(anchor="w")
        self.listbox.delete(0, END)
        self.listbox.insert(END, f"Selected: {self.file}")
        self.listbox.insert(END, f"Loaded {len(names)} column labels. Check only those you intend to change.")

    def preview(self):
        if self.file is None:
            return messagebox.showinfo("Choose file first", "Select an input file.")
        selected = self.selected_columns()
        if not selected:
            return messagebox.showwarning("No columns selected", "Check one or more column names.")
        try:
            lines = preview_changes(self.file, selected, self.mode.get(), self.salt.get())
            self.listbox.delete(0, END)
            for line in lines:
                self.listbox.insert(END, line)
        except Exception as exc:
            messagebox.showerror("Preview failed", str(exc))

    def export(self):
        if self.file is None:
            return messagebox.showinfo("Choose file first", "Select an input file.")
        selected = self.selected_columns()
        if not selected:
            return messagebox.showwarning("No columns selected", "Check one or more column names.")
        mode = self.mode.get()
        if mode not in MODES:
            return messagebox.showerror("Invalid method", "Choose mask, pseudonymize or drop.")
        if mode == "pseudonymize" and not self.salt.get().strip():
            return messagebox.showerror("Missing key", "Pseudonymization needs a nonempty private key.")
        if not messagebox.askokcancel(
            "Review export",
            f"{len(selected)} selected column(s): {', '.join(sorted(selected)[:8])}"
            "\nOther columns and workbook content may still contain personal data."
            "\nWorkbook formulas and hidden structures are not comprehensively certified."
            "\nContinue to choose a NEW output file?",
        ):
            return
        ext = self.file.suffix.lower()
        out = filedialog.asksaveasfilename(
            parent=self.root, defaultextension=ext,
            initialfile=f"{self.file.stem}_safe{ext}", filetypes=[("Output", f"*{ext}")],
        )
        if not out:
            return
        destination = Path(out)
        if destination.exists() or destination.is_symlink():
            return messagebox.showerror("File exists", "Choose a new output filename; existing files are never replaced.")
        try:
            if ext == ".csv":
                stats = clean_csv(self.file, destination, selected, mode, self.salt.get())
            else:
                stats = clean_xlsx(self.file, destination, selected, mode, self.salt.get(),
                                   bool(self.remove_hidden.get()), bool(self.remove_comments.get()))
            if destination.stat().st_size <= 0:
                raise ValueError("Generated file is empty; do not share.")
            self.listbox.insert(END, f"CREATED {destination.name} | {stats}")
            messagebox.showinfo("Export complete", "New copy created. Check the final output before sharing.")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))


def main():
    from i18n import install_bilingual_ui

    root = Tk()
    App(root)
    install_bilingual_ui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
