import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]


class KarpathyPrinciplesProtocolTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (SXLB_ROOT / relative_path).read_text(encoding="utf-8")

    def test_planning_protocol_requires_assumptions_simplicity_scope_and_verification(self) -> None:
        text = self.read("protocols/planning.md")
        self.assertIn("未声明假设", text)
        self.assertIn("不必要复杂度", text)
        self.assertIn("改动边界", text)
        self.assertIn("步骤 -> 验证方式", text)

    def test_review_protocol_checks_the_four_lightweight_gates(self) -> None:
        text = self.read("protocols/review.md")
        self.assertIn("假设检查", text)
        self.assertIn("复杂度检查", text)
        self.assertIn("边界检查", text)
        self.assertIn("验证标准检查", text)

    def test_templates_surface_the_gate_without_adding_external_dependency(self) -> None:
        plan_text = self.read("templates/zhongshu-plan.md")
        review_text = self.read("templates/menxia-review.md")
        combined = plan_text + "\n" + review_text
        self.assertIn("四问", combined)
        self.assertIn("假设", combined)
        self.assertIn("复杂度", combined)
        self.assertIn("改动边界", combined)
        self.assertIn("验证方式", combined)
        self.assertNotIn("andrej-karpathy-skills", combined)

    def test_agent_failure_upgrades_have_concrete_template_fields(self) -> None:
        plan_text = self.read("templates/zhongshu-plan.md")
        dispatch_text = self.read("templates/dispatch-order.md")
        review_text = self.read("templates/menxia-review.md")
        verification_text = self.read("templates/verification.md")
        memorial_text = self.read("templates/memorial-report.md")

        self.assertIn("预算与停止条件", plan_text)
        self.assertIn("执行预算", dispatch_text)
        self.assertIn("预算超限处理", dispatch_text)
        self.assertIn("冲突取舍检查", review_text)
        self.assertIn("失败显性化检查", review_text)
        self.assertIn("行为断言/不变量", verification_text)
        self.assertIn("测试有效性", verification_text)
        self.assertIn("未完成/未验证项", memorial_text)

    def test_review_protocol_rejects_hidden_budget_conflict_and_unverified_work(self) -> None:
        text = self.read("protocols/review.md")

        self.assertIn("预算与停止条件", text)
        self.assertIn("冲突取舍检查", text)
        self.assertIn("失败显性化检查", text)
        self.assertIn("测试有效性", text)


if __name__ == "__main__":
    unittest.main()
