import json
import shutil
import tempfile
import unittest
from pathlib import Path

from subagent_dispatch import create_dispatch_bundle


SXLB_ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_slice_dispatch_case(root: Path) -> None:
    write(
        root / "case.md",
        """# 立案单

## 基本信息

- 任务：Upgrade dispatch slices
- 用户目标：Make dispatch ready for agent execution
- 约束：Keep scope narrow
- 风险级别：medium
- 案卷路径：/tmp/example
- restart 目标：n/a

## 任务分类

- 任务类别：C
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 首办官署：尚书省
- 下一站：尚书省
""",
    )
    write(
        root / "dispatch-order.md",
        """# 派令

## 派发信息

- 当前阶段：尚书派发
- 拓扑：parallel
- 执行方式：real-subagent
- 真实派发：yes
- delegation 可用性：available
- 本线办理理由：not-needed
- 派发就绪状态：ready-for-agent
- 返回审议点：门下复核
- 合流要求：merge required
- 合流摘要：subagents/merge-summary.md

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Deliver a thin executable slice
- 切片类型：vertical slice
- 交互模式：AFK
- blocked-by：none
- 验收标准：unit test passes and return artifact names touched files
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：protocols/
- 可写范围：scripts/
- 真实触达审计：required
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：boundary conflict

## 双轨附记

- 文线：n/a
- 武线：n/a
- 合流点：门下复核
- 合流负责：工部
""",
    )


class MattPocockUpgradeTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (SXLB_ROOT / relative_path).read_text(encoding="utf-8")

    def test_zhongshu_protocol_and_template_gain_prd_decision_tree_language(self) -> None:
        combined = self.read("protocols/planning.md") + "\n" + self.read("templates/zhongshu-plan.md")
        self.assertIn("决策树", combined)
        self.assertIn("领域语言", combined)
        self.assertIn("ADR", combined)
        self.assertIn("PRD", combined)
        self.assertIn("测试决策", combined)

    def test_shangshu_dispatch_gains_slice_and_handoff_governance(self) -> None:
        combined = self.read("protocols/dispatch.md") + "\n" + self.read("templates/dispatch-order.md")
        self.assertIn("vertical slice", combined)
        self.assertIn("HITL", combined)
        self.assertIn("AFK", combined)
        self.assertIn("blocked-by", combined)
        self.assertIn("ready-for-agent", combined)
        self.assertIn("验收标准", combined)

    def test_department_roles_gain_cross_office_reference_patterns(self) -> None:
        combined = "\n".join(
            [
                self.read("roles/zhongshu.md"),
                self.read("roles/shangshu.md"),
                self.read("roles/gongbu.md"),
                self.read("roles/xingbu.md"),
                self.read("roles/bingbu.md"),
                self.read("roles/libu.md"),
                self.read("roles/libu_hr.md"),
            ]
        )
        self.assertIn("PRD", combined)
        self.assertIn("vertical slice", combined)
        self.assertIn("深模块", combined)
        self.assertIn("RED-GREEN-REFACTOR", combined)
        self.assertIn("guardrails", combined)
        self.assertIn("参考模式", combined)

    def test_bug_qa_template_requires_reproduction_and_root_cause_fields(self) -> None:
        combined = self.read("templates/verification.md") + "\n" + self.read("roles/xingbu.md")
        self.assertIn("复现步骤", combined)
        self.assertIn("期望行为", combined)
        self.assertIn("实际行为", combined)
        self.assertIn("根因假设", combined)

    def test_architecture_changes_require_real_friction_before_deepening(self) -> None:
        combined = self.read("protocols/planning.md") + "\n" + self.read("roles/gongbu.md")
        self.assertIn("真实摩擦", combined)
        self.assertIn("架构改造", combined)
        self.assertIn("深模块", combined)

    def test_reference_patterns_do_not_expand_skill_allowlist(self) -> None:
        combined = self.read("skills/mapping.md") + "\n" + self.read("skills/allowlist.md")
        self.assertIn("参考模式", combined)
        self.assertIn("not a callable skill", combined)
        self.assertIn("do not count as allowlisted skills", combined)
        self.assertNotIn("mattpocock/skills", combined)

    def test_subagent_orchestration_docs_match_dispatch_readiness_contract(self) -> None:
        combined = self.read("protocols/subagent-orchestration.md") + "\n" + self.read("protocols/case-package.md")
        self.assertIn("端到端薄切片", combined)
        self.assertIn("interaction mode", combined)
        self.assertIn("blocked-by", combined)
        self.assertIn("acceptance criteria", combined)
        self.assertIn("real-subagent dispatch has readiness", combined)

    def test_subagent_packet_carries_slice_readiness_and_acceptance_criteria(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-slice-"))
        try:
            make_slice_dispatch_case(temp_dir)
            result = create_dispatch_bundle(temp_dir, force=True)
            self.assertEqual(len(result), 2)
            packet_text = (temp_dir / "subagents" / "subagent-work-packet-office-01.md").read_text(encoding="utf-8")
            self.assertIn("切片类型：vertical slice", packet_text)
            self.assertIn("交互模式：AFK", packet_text)
            self.assertIn("blocked-by：none", packet_text)
            self.assertIn("验收标准：unit test passes", packet_text)

            manifest = json.loads((temp_dir / "subagents" / "manifest.json").read_text(encoding="utf-8"))
            packet = manifest["packets"][0]
            self.assertEqual(packet["slice_type"], "vertical slice")
            self.assertEqual(packet["interaction_mode"], "AFK")
            self.assertEqual(packet["blocked_by"], "none")
            self.assertIn("unit test passes", packet["acceptance_criteria"])
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
