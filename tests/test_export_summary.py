"""Customer-readable export summary must show unchanged XLSX sheets."""
import unittest
from pathlib import Path
from windows_app import format_export_summary


class ExportSummaryTests(unittest.TestCase):
    def test_csv_summary_is_simple_and_readable(self):
        lines = format_export_summary(Path("private-safe.csv"), {"rows": 3}, {"email"})
        self.assertTrue(any("CSV rows processed: 3" in row for row in lines))
        self.assertFalse(any(row.startswith("{") for row in lines))
        self.assertTrue(any("Review every output file" in row for row in lines))

    def test_xlsx_status_distinguishes_changed_and_unmatched_sheets(self):
        payload = {
            "removed_hidden_sheets": 1,
            "sheet_results": [
                {"sheet": "People", "status": "processed", "processed_columns": ["email"]},
                {"sheet": "Orders", "status": "skipped_no_matching_columns", "processed_columns": []},
            ],
        }
        lines = format_export_summary(Path("safer.xlsx"), payload, {"email"})
        self.assertTrue(any("Worksheets changed: 1; not changed: 1" in x for x in lines))
        self.assertTrue(any("Changed sheet: People" in x for x in lines))
        self.assertTrue(any("Unchanged sheet (no matching columns): Orders" in x for x in lines))
        self.assertTrue(any("Hidden worksheets removed: 1" in x for x in lines))
        self.assertTrue(any("Review every output file" in x for x in lines))


if __name__ == "__main__":
    unittest.main()
