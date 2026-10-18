"""Regression: normalized CSV headings, preflight-before-output, limited memory."""
import csv
import tempfile
from unittest.mock import patch
import windows_app
import unittest
from pathlib import Path

from windows_app import available_columns, clean_csv, preview_changes


class CsvIntegrityTests(unittest.TestCase):
    def test_heading_with_spaces_preserves_selected_and_unselected_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "顧客.csv"
            output = root / "out.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as file:
                csv.writer(file).writerows([
                    [" id ", " email ", " 顧客メモ "],
                    ["001", "alice@example.com", "KEEP EXACTLY"],
                    ["002", "bob@example.com", "行\n改行"],
                ])
            original = source.read_bytes()
            self.assertEqual(available_columns(source), ["id", "email", "顧客メモ"])
            preview = preview_changes(source, {"email"}, "mask", "key")
            self.assertTrue(any("[REDACTED_EMAIL]" in x for x in preview))
            stats = clean_csv(source, output, {"email"}, "mask", "key")
            self.assertEqual(stats["rows"], 2)
            with output.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(list(rows[0]), ["id", "email", "顧客メモ"])
            self.assertEqual(rows[0]["id"], "001")
            self.assertEqual(rows[0]["email"], "[REDACTED_EMAIL]")
            self.assertEqual(rows[0]["顧客メモ"], "KEEP EXACTLY")
            self.assertEqual(rows[1]["顧客メモ"], "行\n改行")
            self.assertEqual(source.read_bytes(), original)

    def test_late_formula_blocks_export_without_partial_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            src = root / "large.csv"
            out = root / "output.csv"
            with src.open("w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["email", "comment"])
                for i in range(2200):
                    writer.writerow([f"user{i}@example.com", "safe"])
                writer.writerow(["end@example.com", "=SUM(1,2)"])
            original = src.read_bytes()
            with self.assertRaisesRegex(ValueError, "Possible spreadsheet formula"):
                clean_csv(src, out, {"email"}, "mask", "key")
            self.assertFalse(out.exists())
            self.assertEqual(src.read_bytes(), original)

    def test_pseudonymization_preserves_missing_and_empty_values(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            output = root / "output.csv"
            source.write_text("email,notes\nalice@example.com,present\n,empty\n", encoding="utf-8")
            clean_csv(source, output, {"email"}, "pseudonymize", "secret-key")
            with output.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertTrue(rows[0]["email"].startswith("USER-"))
            self.assertEqual(rows[1]["email"], "")
            self.assertEqual(rows[1]["notes"], "empty")

    def test_empty_pseudonym_key_refused_even_without_gui(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            out = root / "out.csv"
            source.write_text("name\nAlice\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonempty"):
                clean_csv(source, out, {"name"}, "pseudonymize", " ")
            self.assertFalse(out.exists())


    def test_output_reopen_detects_corrupt_writer_and_removes_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            output = root / "out.csv"
            source.write_text("email,notes\na@example.com,unchanged\n", encoding="utf-8")

            class CorruptingWriter(csv.DictWriter):
                def writerow(self, rowdict):
                    modified = dict(rowdict)
                    if modified.get("email") not in ("email", None):
                        modified["notes"] = "incorrect"
                    return super().writerow(modified)

            with patch.object(windows_app.csv, "DictWriter", CorruptingWriter):
                with self.assertRaisesRegex(ValueError, "CSV output verification failed"):
                    clean_csv(source, output, {"email"}, "mask", "salt")
            self.assertFalse(output.exists())
            self.assertEqual(source.read_text(encoding="utf-8"),
                             "email,notes\na@example.com,unchanged\n")

    def test_missing_csv_field_exports_empty_value_without_losing_other_columns(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.csv"
            output = root / "output.csv"
            source.write_text("email,notes,extra\na@example.com,unchanged\n", encoding="utf-8")
            clean_csv(source, output, {"email"}, "mask", "key")
            with output.open(encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(rows[0]["notes"], "unchanged")
            self.assertEqual(rows[0]["extra"], "")


if __name__ == "__main__":
    unittest.main()
