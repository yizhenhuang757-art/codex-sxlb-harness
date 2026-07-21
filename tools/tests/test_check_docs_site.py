from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import check_docs_site


class DocumentationSiteStructureTests(unittest.TestCase):
    def test_requires_new_bilingual_source_transparency_pages(self) -> None:
        self.assertIn(("why-sxlb.md", "zh-CN/why-sxlb.md"), check_docs_site.REQUIRED_PAIRS)
        self.assertIn(("skill-directory.md", "zh-CN/skill-directory.md"), check_docs_site.REQUIRED_PAIRS)
        self.assertIn(("sources.md", "zh-CN/sources.md"), check_docs_site.REQUIRED_PAIRS)

    def test_validates_declared_source_relationships(self) -> None:
        errors = check_docs_site.validate_source_records(
            [
                {
                    "skill_id": "humanizer-zh",
                    "source_relation": "external-reference",
                    "source_url": "https://github.com/op7418/Humanizer-zh",
                    "source_note": "Chinese editorial skill",
                },
                {
                    "skill_id": "plugin/example",
                    "source_relation": "plugin-family",
                    "source_url": None,
                    "source_note": "Supplied by the host environment.",
                },
                {
                    "skill_id": "missing-link",
                    "source_relation": "external-reference",
                    "source_url": None,
                    "source_note": "",
                },
            ]
        )

        self.assertEqual(
            ["External source requires HTTPS URL: missing-link"],
            errors,
        )

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

    def test_reports_empty_required_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for english_path, chinese_path in check_docs_site.REQUIRED_PAIRS:
                for relative_path in (english_path, chinese_path):
                    page = root / relative_path
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text("# Documentation\n", encoding="utf-8")
            (root / "zh-CN/sxlb-mapping.md").write_text("\n", encoding="utf-8")

            errors = check_docs_site.validate(root)

        self.assertIn("Required page is empty: zh-CN/sxlb-mapping.md", errors)


if __name__ == "__main__":
    unittest.main()
