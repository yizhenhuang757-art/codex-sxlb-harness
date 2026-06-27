import shutil
import tempfile
import unittest
from pathlib import Path

from artifact_registry import build_registry, write_registry


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ArtifactRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-artifacts-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_build_registry_marks_required_artifacts_present_and_missing(self) -> None:
        write(self.temp_dir / "case.md", "- 任务类别：C\n")
        write(self.temp_dir / "dispatch-order.md", "# 派令\n")
        rows = build_registry(self.temp_dir)
        by_name = {row["artifact"]: row for row in rows}
        self.assertEqual(by_name["case.md"]["status"], "present")
        self.assertEqual(by_name["dispatch-order.md"]["status"], "present")
        self.assertEqual(by_name["verification.md"]["status"], "missing")
        self.assertEqual(by_name["verification.md"]["blocking"], "yes")

    def test_write_registry_creates_markdown_table(self) -> None:
        write(self.temp_dir / "case.md", "- 任务类别：C\n")
        path = write_registry(self.temp_dir)
        text = path.read_text(encoding="utf-8")
        self.assertIn("| artifact | required | status | consumer | blocking |", text)
        self.assertIn("| verification.md | yes | missing | 门下省 | yes |", text)

    def test_build_registry_includes_present_optional_approval_ledger(self) -> None:
        write(self.temp_dir / "case.md", "- 任务类别：C\n")
        write(self.temp_dir / "approval-ledger.md", "# Approval Ledger\n")
        rows = build_registry(self.temp_dir)
        by_name = {row["artifact"]: row for row in rows}
        self.assertEqual(by_name["approval-ledger.md"]["required"], "no")
        self.assertEqual(by_name["approval-ledger.md"]["status"], "present")
        self.assertEqual(by_name["approval-ledger.md"]["consumer"], "门下省")

    def test_build_registry_includes_present_optional_learning_ledger(self) -> None:
        write(self.temp_dir / "case.md", "- 任务类别：C\n")
        write(self.temp_dir / "learning-ledger.jsonl", '{"type":"pattern"}\n')
        rows = build_registry(self.temp_dir)
        by_name = {row["artifact"]: row for row in rows}
        self.assertEqual(by_name["learning-ledger.jsonl"]["required"], "no")
        self.assertEqual(by_name["learning-ledger.jsonl"]["status"], "present")


if __name__ == "__main__":
    unittest.main()
