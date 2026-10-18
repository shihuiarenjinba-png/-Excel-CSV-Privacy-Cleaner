"""Guard headers, compressed containers and size limits before saving."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED

from openpyxl import Workbook
import windows_app
from windows_app import available_columns, clean_csv, clean_xlsx, validate_input_size


class InputPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_formula_header_not_written_to_output(self):
        src = self.root / "danger.csv"
        out = self.root / "out.csv"
        src.write_text("=HYPERLINK(\"\"https://example.invalid\"\"),customer\nx,Alice\n", encoding="utf-8")
        before = src.read_bytes()
        with self.assertRaisesRegex(ValueError, "column header"):
            clean_csv(src, out, {"customer"}, "pseudonymize", "key")
        self.assertFalse(out.exists())
        self.assertEqual(src.read_bytes(), before)

    def test_csv_size_limit(self):
        src = self.root / "large.csv"
        src.write_text("name\nAlice\n", encoding="utf-8")
        with patch.object(windows_app, "MAX_CSV_BYTES", 3):
            with self.assertRaisesRegex(ValueError, "Input file must be"):
                available_columns(src)
            with self.assertRaisesRegex(ValueError, "Input file must be"):
                clean_csv(src, self.root / "out.csv", {"name"}, "mask", "key")
        self.assertFalse((self.root / "out.csv").exists())

    def test_xlsx_zip_bomb_budget_rejected(self):
        src = self.root / "too-big.xlsx"
        with ZipFile(src, "w", ZIP_DEFLATED) as z:
            z.writestr("xl/worksheets/sheet1.xml", "X" * 15000)
        with patch.object(windows_app, "MAX_XLSX_UNCOMPRESSED", 100):
            with self.assertRaisesRegex(ValueError, "Expanded workbook"):
                validate_input_size(src)

    def test_macro_payload_hidden_inside_xlsx_rejected(self):
        src = self.root / "macro.xlsx"
        with ZipFile(src, "w") as z:
            z.writestr("xl/vbaProject.bin", b"not a real macro")
        with self.assertRaisesRegex(ValueError, "Macro-containing"):
            validate_input_size(src)

    def test_regular_small_workbook_accepted(self):
        src = self.root / "ordinary.xlsx"
        wb = Workbook()
        wb.active.append(["person", "email"])
        wb.active.append(["Alice", "alice@example.invalid"])
        wb.save(src)
        self.assertEqual(available_columns(src), ["person", "email"])
        out = self.root / "out.xlsx"
        clean_xlsx(src, out, {"email"}, "pseudonymize", "key", True, True)
        self.assertTrue(out.is_file())

    def test_csv_data_row_limit(self):
        src = self.root / "many.csv"
        src.write_text("x\nAlice\nBob\n", encoding="utf-8")
        with patch.object(windows_app, "MAX_SPREADSHEET_ROWS", 1):
            with self.assertRaisesRegex(ValueError, "100,000 rows"):
                clean_csv(src, self.root / "out.csv", {"x"}, "mask", "key")
        self.assertFalse((self.root / "out.csv").exists())


if __name__ == "__main__":
    unittest.main()
