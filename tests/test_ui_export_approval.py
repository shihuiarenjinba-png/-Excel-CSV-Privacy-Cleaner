"""UI safety regression: no export approval survives changed source/options."""
import tempfile
import unittest
from pathlib import Path

from ui_export_approval import export_revision


class PreviewApprovalTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "customer.csv"
        self.source.write_text("id,email\n00123,a@example.org\n", encoding="utf-8")

    def revision(self, **kwargs):
        opts = dict(path=self.source, columns={"email"}, mode="mask",
                    salt="private", remove_hidden=True, remove_comments=True)
        opts.update(kwargs)
        return export_revision(**opts)

    def test_same_selection_is_approved(self):
        self.assertEqual(self.revision(), self.revision())

    def test_same_size_source_change_invalidates_approval(self):
        previous = self.revision()
        self.source.write_text("id,email\n00123,b@example.org\n", encoding="utf-8")
        self.assertNotEqual(previous, self.revision())

    def test_mode_columns_and_options_invalidate_approval(self):
        base = self.revision()
        for change in ({"mode": "drop"}, {"columns": {"id"}},
                       {"remove_hidden": False}, {"remove_comments": False},
                       {"mode": "pseudonymize", "salt": "another"}):
            with self.subTest(change=change):
                self.assertNotEqual(base, self.revision(**change))

    def test_private_key_not_present_in_revision(self):
        result = self.revision(mode="pseudonymize")
        self.assertNotIn("private", result)
        self.assertEqual(len(result), 64)

    def test_missing_or_linked_source_is_not_approved(self):
        self.source.unlink()
        with self.assertRaises(ValueError):
            self.revision()


if __name__ == "__main__":
    unittest.main()
