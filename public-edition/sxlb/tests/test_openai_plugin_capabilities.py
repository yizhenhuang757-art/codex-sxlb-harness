import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]


class OpenAIPluginCapabilitiesTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (SXLB_ROOT / relative_path).read_text(encoding="utf-8")

    def test_chrome_plugin_is_bingbu_login_state_browser_execution(self) -> None:
        combined = "\n".join(
            [
                self.read("skills/allowlist.md"),
                self.read("skills/mapping.md"),
                self.read("skills/skill-families.md"),
                self.read("skills/skill-inventory.generated.md"),
                self.read("roles/bingbu.md"),
            ]
        )
        self.assertIn("family:plugin/chrome", combined)
        self.assertIn("chrome:control-chrome", combined)
        self.assertIn("family:plugin/computer-use", combined)
        self.assertIn("computer-use:computer-use", combined)
        self.assertIn("Computer Use confirmation policy", combined)
        self.assertIn("真实 Chrome 登录态", combined)
        self.assertIn("已打开标签页", combined)
        self.assertIn("网页表单", combined)
        self.assertIn("不要替代 Chrome DevTools 的诊断职责", combined)

    def test_zotero_plugin_is_hubu_literature_and_citation_data_execution(self) -> None:
        combined = "\n".join(
            [
                self.read("skills/allowlist.md"),
                self.read("skills/mapping.md"),
                self.read("skills/skill-families.md"),
                self.read("skills/skill-inventory.generated.md"),
                self.read("roles/hubu.md"),
            ]
        )
        self.assertIn("family:plugin/zotero", combined)
        self.assertIn("zotero:Zotero", combined)
        self.assertIn("文献库", combined)
        self.assertIn("BibTeX", combined)
        self.assertIn("引用数据", combined)
        self.assertIn("写入 Zotero 库前必须确认", combined)

    def test_libu_owns_plugin_capability_promotion_boundaries(self) -> None:
        combined = "\n".join(
            [
                self.read("skills/mapping.md"),
                self.read("skills/skill-families.md"),
                self.read("roles/libu_hr.md"),
            ]
        )
        self.assertIn("OpenAI 插件", combined)
        self.assertIn("插件能力晋升", combined)
        self.assertIn("可用 / 需用 / 急用", combined)
        self.assertIn("family", combined)

    def test_zero_burden_plugin_recall_uses_families_and_inventory(self) -> None:
        combined = "\n".join(
            [
                self.read("MODE.md"),
                self.read("skills/allowlist.md"),
                self.read("skills/mapping.md"),
                self.read("skills/skill-families.md"),
                self.read("skills/skill-inventory.generated.md"),
            ]
        )
        self.assertIn("agent-side precheck", combined)
        for family in (
            "family:plugin/browser",
            "family:plugin/figma",
            "family:plugin/product-design",
            "family:plugin/computer-use",
            "family:plugin/presentations",
            "family:plugin/spreadsheets",
            "family:plugin/outlook-email",
            "family:plugin/codex-security",
        ):
            self.assertIn(family, combined)
        for concrete_skill in (
            "browser:control-in-app-browser",
            "computer-use:computer-use",
            "figma:figma-use",
            "figma:figma-generate-diagram",
            "product-design:get-context",
            "product-design:image-to-code",
            "product-design:url-to-code",
            "product-design:prototype",
            "product-design:design-qa",
            "presentations:Presentations",
            "spreadsheets:Spreadsheets",
            "outlook-email:outlook-email",
            "codex-security:security-scan",
            "codex-security:deep-security-scan",
        ):
            self.assertIn(concrete_skill, combined)


if __name__ == "__main__":
    unittest.main()
