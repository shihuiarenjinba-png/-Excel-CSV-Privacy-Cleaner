"""Release evidence is deliberately incomplete until actual Windows validation."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "store" / "release_gate.py"
spec = importlib.util.spec_from_file_location("store_release_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gate)

COMMIT = "a" * 40


class StoreGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "evidence").mkdir()
        self.proof = self.root / "evidence" / "sample.txt"
        self.proof.write_text("synthetic evidence for unit test only", encoding="utf-8")
        self.entry = {
            "status": "PASS", "evidence_file": "evidence/sample.txt",
            "sha256": hashlib.sha256(self.proof.read_bytes()).hexdigest(),
        }

    def test_empty_template_is_not_release_ready(self):
        payload = {"schema_version": 1, "commit_sha": COMMIT,
                   "gates": {name: {"status": "TODO"} for name in gate.GATES}}
        self.assertEqual(set(gate.check_evidence(self.root, payload, COMMIT)), set(gate.GATES))

    def test_correct_hash_is_necessary_but_not_store_approval(self):
        payload = {"schema_version": 1, "commit_sha": COMMIT,
                   "gates": {name: dict(self.entry) for name in gate.GATES}}
        self.assertEqual(gate.check_evidence(self.root, payload, COMMIT), [])
        self.proof.write_text("changed!", encoding="utf-8")
        self.assertEqual(set(gate.check_evidence(self.root, payload, COMMIT)), set(gate.GATES))

    def test_wrong_commit_blocks_all_release(self):
        payload = {"schema_version": 1, "commit_sha": "b" * 40,
                   "gates": {name: dict(self.entry) for name in gate.GATES}}
        self.assertIn("commit_sha", gate.check_evidence(self.root, payload, COMMIT))

    def test_path_traversal_is_rejected(self):
        outside = self.root.parent / "private-file.txt"
        # Never create a file outside our private temp tree; the path is missing.
        payload = {"schema_version": 1, "commit_sha": COMMIT,
                   "gates": {name: dict(self.entry) for name in gate.GATES}}
        payload["gates"]["msix_package"]["evidence_file"] = "../private-file.txt"
        self.assertIn("msix_package", gate.check_evidence(self.root, payload, COMMIT))


if __name__ == "__main__":
    unittest.main()
