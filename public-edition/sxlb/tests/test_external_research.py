import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]


class ExternalResearchProtocolTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (SXLB_ROOT / relative_path).read_text(encoding="utf-8")

    def test_caifeng_protocol_exists_as_evidence_package_not_department(self) -> None:
        text = self.read("protocols/external-research.md")
        self.assertIn("采风", text)
        self.assertIn("外部证据包", text)
        self.assertIn("不是新部门", text)
        self.assertIn("不替中书省拍板", text)

    def test_protocol_sets_lightweight_research_bounds_and_source_types(self) -> None:
        text = self.read("protocols/external-research.md")
        self.assertIn("2-5", text)
        self.assertIn("2-4", text)
        self.assertIn("official", text)
        self.assertIn("repo", text)
        self.assertIn("paper", text)
        self.assertIn("opinion", text)

    def test_core_offices_reference_caifeng_boundaries(self) -> None:
        combined = "\n".join(
            [
                self.read("roles/zhongshu.md"),
                self.read("roles/shangshu.md"),
                self.read("roles/menxia.md"),
                self.read("roles/libu_hr.md"),
                self.read("roles/gongbu.md"),
                self.read("roles/xingbu.md"),
                self.read("roles/hubu.md"),
            ]
        )
        self.assertIn("采风", combined)
        self.assertIn("外部证据包", combined)
        self.assertIn("来源可靠性", combined)

    def test_readme_links_external_research_protocol(self) -> None:
        text = self.read("README.md")
        self.assertIn("protocols/external-research.md", text)
        self.assertIn("采风", text)


if __name__ == "__main__":
    unittest.main()
