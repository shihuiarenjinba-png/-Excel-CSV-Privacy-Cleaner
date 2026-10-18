"""Fail-closed check for spreadsheet formulas appearing after CSV export."""
import tempfile
import unittest
from pathlib import Path

from windows_app import clean_csv, csv_formula_risk


class CsvFormulaExportTests(unittest.TestCase):
    def test_spreadsheet_formula_prefixes(self):
        for value in ("=1+1", " +SUM(1,2)", "\t@SUM(1,2)", "-cmd|' /C calc'!A0",
                      "\r\n=HYPERLINK(\"https://x\", \"click\")"):
            with self.subTest(value=value):
                self.assertTrue(csv_formula_risk(value))
        for value in ("-150", "-1.25", "hello", "00124", "", None):
            self.assertFalse(csv_formula_risk(value))

    def test_unselected_formula_blocks_without_creating_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            dest = root / "safe.csv"
            source.write_text("email,note\nperson@example.org,=HYPERLINK(\"\"https://unsafe.example\"\")\n",
                              encoding="utf-8")
            untouched = source.read_bytes()
            with self.assertRaisesRegex(ValueError, "Possible spreadsheet formula"):
                clean_csv(source, dest, {"email"}, "mask", "salt")
            self.assertFalse(dest.exists())
            self.assertEqual(source.read_bytes(), untouched)

    def test_pseudonymized_formula_column_can_be_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            dest = root / "safe.csv"
            source.write_text("input,keep\n=1+1,ordinary\n", encoding="utf-8")
            clean_csv(source, dest, {"input"}, "pseudonymize", "private-salt")
            output = dest.read_text(encoding="utf-8-sig")
            self.assertNotIn("=1+1", output)
            self.assertIn("ordinary", output)

    def test_existing_output_stays_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            output = root / "existing.csv"
            source.write_text("input\nAlice\n", encoding="utf-8")
            output.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                clean_csv(source, output, {"input"}, "mask", "salt")
            self.assertEqual(output.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
