import shutil
import tempfile
import unittest
from pathlib import Path

from context_packets import (
    PACKET_TEMPLATES,
    find_duplicate_context_records,
    scaffold_context_packets,
    validate_context_packet,
    validate_context_packets,
)


class ContextPacketsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-context-packets-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_scaffold_creates_all_context_packet_files(self) -> None:
        created = scaffold_context_packets(self.temp_dir)
        self.assertEqual(set(created), set(PACKET_TEMPLATES))
        for name in PACKET_TEMPLATES:
            self.assertTrue((self.temp_dir / name).exists(), name)

    def test_intake_context_rejects_taizi_planning_overreach(self) -> None:
        path = self.temp_dir / "intake-context.md"
        path.write_text(
            """# 太子上下文入口

## 必填字段

- 案由：Build context packets
- 用户目标：Reduce token waste
- 约束：Keep taizi small
- 上下文入口：case.md
- 下一站：中书省
- 关键未知：none
- 不做什么：do not implement yet

## 太子边界

- PRD：太子直接写完整方案
- canonical 决策：promote now
""",
            encoding="utf-8",
        )

        issues = validate_context_packet(path, "intake-context.md")

        self.assertTrue(any("太子越权" in issue for issue in issues))

    def test_packet_rejects_empty_or_placeholder_values(self) -> None:
        path = self.temp_dir / "dispatch-packet.md"
        path.write_text(
            """# 尚书上下文包

## 分支

- 官署：<office>
- 任务：
- readiness：ready-for-agent
- 共享只读：case.md
- 可写范围：scripts/
- 禁写范围：none
- 回传物：verification.md
""",
            encoding="utf-8",
        )

        issues = validate_context_packet(path, "dispatch-packet.md")

        self.assertIn("empty or placeholder field: 官署", issues)
        self.assertIn("empty or placeholder field: 任务", issues)

    def test_dispatch_packet_requires_context_boundaries(self) -> None:
        path = self.temp_dir / "dispatch-packet.md"
        path.write_text(
            """# 尚书上下文包

## 分支

- 官署：工部
- 任务：Implement script
- readiness：ready-for-agent
- 回传物：verification.md
""",
            encoding="utf-8",
        )

        issues = validate_context_packet(path, "dispatch-packet.md")

        self.assertIn("missing required field: 共享只读", issues)
        self.assertIn("missing required field: 可写范围", issues)
        self.assertIn("missing required field: 禁写范围", issues)

    def test_review_grill_requires_four_gate_checks(self) -> None:
        path = self.temp_dir / "review-grill.md"
        path.write_text(
            """# 门下 Grill 清单

## 审议对象

- 来源：zhongshu-plan.md

## 检查

- 假设检查：pass
- 边界检查：pass
""",
            encoding="utf-8",
        )

        issues = validate_context_packet(path, "review-grill.md")

        self.assertIn("missing required field: 复杂度检查", issues)
        self.assertIn("missing required field: 验证标准检查", issues)

    def test_duplicate_context_records_warn_when_packet_repeats_core_fields(self) -> None:
        (self.temp_dir / "case.md").write_text(
            """# 立案单

## 基本信息

- 用户目标：Reduce token waste without adding a new mandatory case layer
- 约束：Keep packets on-demand only
- 上下文入口：case.md, dispatch-order.md, menxia-review.md
""",
            encoding="utf-8",
        )
        (self.temp_dir / "intake-context.md").write_text(
            """# 太子上下文入口

## 必填字段

- 案由：Context packets
- 用户目标：Reduce token waste without adding a new mandatory case layer
- 约束：Use short pointers
- 上下文入口：case.md, dispatch-order.md, menxia-review.md
- 下一站：中书省
- 关键未知：none
- 不做什么：do not make packets default
""",
            encoding="utf-8",
        )

        warnings = find_duplicate_context_records(self.temp_dir)

        self.assertTrue(any("intake-context.md duplicates case.md field 用户目标" in warning for warning in warnings))
        self.assertTrue(any("intake-context.md duplicates case.md field 上下文入口" in warning for warning in warnings))

    def test_duplicate_context_records_are_optional_validate_checks(self) -> None:
        (self.temp_dir / "case.md").write_text(
            """# 立案单

- 用户目标：Reduce token waste without adding a new mandatory case layer
""",
            encoding="utf-8",
        )
        (self.temp_dir / "intake-context.md").write_text(
            """# 太子上下文入口

## 必填字段

- 案由：Context packets
- 用户目标：Reduce token waste without adding a new mandatory case layer
- 约束：none
- 上下文入口：case.md
- 下一站：中书省
- 关键未知：none
- 不做什么：none
""",
            encoding="utf-8",
        )

        default_issues = validate_context_packets(self.temp_dir, templates=("intake-context.md",))
        duplicate_issues = validate_context_packets(
            self.temp_dir,
            templates=("intake-context.md",),
            check_duplicates=True,
        )

        self.assertEqual(default_issues, [])
        self.assertTrue(any("duplicate core record" in issue for issue in duplicate_issues))


if __name__ == "__main__":
    unittest.main()
