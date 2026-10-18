"""Commercial integrity of stable keyed pseudonyms."""
import re
import unittest
from windows_app import pseudonym

class PseudonymTests(unittest.TestCase):
    def test_repeated_value_and_private_key_make_same_id(self):
        a = pseudonym("alice@example.com", "private-example-key")
        self.assertEqual(a, pseudonym("alice@example.com", "private-example-key"))
        self.assertRegex(a, r"^USER-[0-9A-F]{16}$")
        self.assertNotIn("alice", a)

    def test_other_key_or_value_changes_id(self):
        a = pseudonym("A", "private-example-key")
        self.assertNotEqual(a, pseudonym("A", "another-key"))
        self.assertNotEqual(a, pseudonym("B", "private-example-key"))

    def test_empty_key_rejected(self):
        for key in ("", "   "):
            with self.assertRaisesRegex(ValueError, "nonempty"):
                pseudonym("A", key)

    def test_short_sample_no_collisions(self):
        values = [pseudonym(f"customer{i}@example.com", "key") for i in range(10000)]
        self.assertEqual(len(set(values)), len(values))

if __name__ == "__main__":
    unittest.main()
