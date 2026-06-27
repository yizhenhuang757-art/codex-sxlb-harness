import shutil
import tempfile
import unittest
from pathlib import Path

from init_case import DEFAULT_TEMPLATES, LIGHTWEIGHT_TEMPLATES, scaffold_case


class InitCaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-init-case-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_scaffold_creates_full_case_package(self) -> None:
        created = scaffold_case(self.temp_dir)
        self.assertEqual(set(created), set(DEFAULT_TEMPLATES))
        for name in DEFAULT_TEMPLATES:
            self.assertTrue((self.temp_dir / name).exists(), name)

    def test_scaffold_skips_existing_without_force(self) -> None:
        scaffold_case(self.temp_dir)
        created = scaffold_case(self.temp_dir)
        self.assertEqual(created, [])

    def test_learning_candidates_template_starts_empty(self) -> None:
        scaffold_case(self.temp_dir)
        learning_path = self.temp_dir / "learning-candidates.jsonl"
        ledger_path = self.temp_dir / "learning-ledger.jsonl"
        self.assertTrue(learning_path.exists())
        self.assertTrue(ledger_path.exists())
        self.assertEqual(learning_path.read_text(encoding="utf-8"), "")
        self.assertEqual(ledger_path.read_text(encoding="utf-8").strip(), "")

    def test_scaffold_creates_p0_stage2_artifacts(self) -> None:
        scaffold_case(self.temp_dir)
        for name in ("artifact-registry.md", "verification.md", "menxia-readiness.md", "records-routing.md"):
            self.assertTrue((self.temp_dir / name).exists(), name)

    def test_scaffold_does_not_create_context_packets_by_default(self) -> None:
        scaffold_case(self.temp_dir)
        for name in ("intake-context.md", "dispatch-packet.md", "review-grill.md"):
            self.assertFalse((self.temp_dir / name).exists(), name)

    def test_scaffold_can_create_lightweight_case_package(self) -> None:
        created = scaffold_case(self.temp_dir, profile="lightweight")
        self.assertEqual(set(created), set(LIGHTWEIGHT_TEMPLATES))
        for name in LIGHTWEIGHT_TEMPLATES:
            self.assertTrue((self.temp_dir / name).exists(), name)
        self.assertFalse((self.temp_dir / "verification.md").exists())
        self.assertFalse((self.temp_dir / "artifact-registry.md").exists())


if __name__ == "__main__":
    unittest.main()
