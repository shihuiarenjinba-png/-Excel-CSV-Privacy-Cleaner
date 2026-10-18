"""Synthetic Tk GUI workflow regression; requires Windows interactive desktop.

Programmatic widget commands are not a replacement for a human visual/DPI check.
"""
from pathlib import Path
import csv
import tempfile
from tkinter import Tk
from unittest.mock import patch

from windows_app import App, filedialog, messagebox


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="excel_gui_synthetic_") as temporary:
        folder = Path(temporary)
        source = folder / "日本語_sample.csv"
        dest = folder / "previewed.csv"
        with source.open("w", encoding="utf-8-sig", newline="") as handle:
            csv.writer(handle).writerows([
                ["名前", "email", "部署"],
                ["Alice", "alice@example.com", "開発"],
                ["Bob", "bob@example.com", "営業"],
            ])
        original = source.read_bytes()
        root = Tk()
        try:
            root.withdraw()
            app = App(root)
            root.update_idletasks()
            with patch.object(filedialog, "askopenfilename", return_value=str(source)):
                app.choose()
            assert set(app.column_vars) == {"名前", "email", "部署"}
            assert app.selected_columns() == set(), "No columns may be preselected"
            app.column_vars["email"].set(1)
            assert app.selected_columns() == {"email"}
            with patch.object(messagebox, "showerror", side_effect=AssertionError):
                app.preview()
            preview = "\n".join(app.listbox.get(0, "end"))
            assert "[REDACTED_EMAIL]" in preview and "alice@example.com" in preview
            with patch.object(messagebox, "askokcancel", return_value=True), \
                 patch.object(filedialog, "asksaveasfilename", return_value=str(dest)), \
                 patch.object(messagebox, "showinfo") as info, \
                 patch.object(messagebox, "showerror", side_effect=AssertionError):
                app.export()
            assert info.called, "GUI must confirm a successful operation"
            assert source.read_bytes() == original, "Never modify the input"
            with dest.open("r", encoding="utf-8-sig", newline="") as result:
                output = list(csv.DictReader(result))
            assert output[0]["email"] == "[REDACTED_EMAIL]"
            assert output[0]["名前"] == "Alice"
            assert output[1]["部署"] == "営業"
            previous = dest.read_bytes()
            with patch.object(messagebox, "askokcancel", return_value=True), \
                 patch.object(filedialog, "asksaveasfilename", return_value=str(dest)), \
                 patch.object(messagebox, "showerror") as error:
                app.export()
            assert error.called, "Overwriting the previous export must be rejected"
            assert dest.read_bytes() == previous
            # A rejected replacement must clear the old export target and checked columns.
            invalid_source = folder / "broken.csv"
            invalid_source.write_bytes(b"\x00\x01\x02")
            with patch.object(filedialog, "askopenfilename", return_value=str(invalid_source)), \
                 patch.object(messagebox, "showerror") as invalid_error:
                app.choose()
            assert invalid_error.called
            assert app.file is None and app.selected_columns() == set()
            with patch.object(messagebox, "showinfo") as missing_file:
                app.export()
            assert missing_file.called
            assert source.read_bytes() == original
            assert dest.read_bytes() == previous
            print("GUI_SYNTHETIC_E2E_OK: choose, checkbox, preview, export, no-overwrite, stale-state reset")
            print("HUMAN_VISUAL_ACCEPTANCE_NOT_TESTED")
        finally:
            root.destroy()


if __name__ == "__main__":
    main()
