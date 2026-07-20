from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import check_docs_site


class DocumentationSiteStructureTests(unittest.TestCase):
    def test_reports_missing_language_counterpart(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "index.md").write_text("# SXLB\n", encoding="utf-8")

            errors = check_docs_site.validate(root)

        self.assertIn("Missing required page: zh-CN/index.md", errors)

    def test_accepts_complete_nonempty_language_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for english_path, chinese_path in check_docs_site.REQUIRED_PAIRS:
                for relative_path in (english_path, chinese_path):
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text("# Documentation\n", encoding="utf-8")

            errors = check_docs_site.validate(root)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
