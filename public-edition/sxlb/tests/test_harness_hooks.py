import json
import shutil
import tempfile
import unittest
from pathlib import Path

from harness_hooks import (
    build_parser,
    check_pre_action,
    check_route_admission,
    check_subagent_return,
    create_dissatisfaction_diagnostic,
    detect_workflow_graduation,
    dispatch_cli,
    record_post_action,
)
from test_sxlb_guard import make_valid_case_package


def make_a_fast_lane_package(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    (root / "case.md").write_text(
        """# 立案单

## 基本信息

- 任务：Fix one typo
- 用户目标：Make one bounded correction
- 约束：Keep A fast lane
- 风险级别：low

## 任务分类

- 任务类别：A
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 首办官署：礼部
- 下一站：尚书省
""",
        encoding="utf-8",
    )
    (root / "dispatch-order.md").write_text(
        """# 派令

## 派发信息

- 当前阶段：尚书派发
- 拓扑：single-thread
- 执行方式：local-office
- 真实派发：no
- delegation 可用性：not used
- 本线办理理由：A fast lane single-office task
- 返回审议点：门下复核

## 官署分派

- 官署：礼部
- 任务：Fix one typo
- 所有权：target note
- 可写范围：notes/
- 禁写范围：canonical docs
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 分支执行：local-office
""",
        encoding="utf-8",
    )
    (root / "volatile-record.md").write_text(
        """# Volatile Record

- 记录类型：volatile
- 持久出口：none
- 清理策略：delete-on-退朝
- 官署：礼部
- 摘要：A fast lane record
""",
        encoding="utf-8",
    )


class HarnessHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-harness-hooks-"))
        make_valid_case_package(self.temp_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_pre_action_blocks_forbidden_scope(self) -> None:
        result = check_pre_action(
            self.temp_dir,
            office="工部",
            branch_id="office-01",
            command="python3 scripts/tool.py",
            write_paths=["canonical docs/rule.md"],
        )

        self.assertFalse(result.ok)
        self.assertIn("writes forbidden scope", result.errors[0])

    def test_pre_action_requires_approval_for_approval_gated_dangerous_command(self) -> None:
        dispatch = (self.temp_dir / "dispatch-order.md").read_text(encoding="utf-8")
        dispatch = dispatch.replace("危险命令策略：no destructive commands", "危险命令策略：approval required")
        (self.temp_dir / "dispatch-order.md").write_text(dispatch, encoding="utf-8")

        result = check_pre_action(
            self.temp_dir,
            office="工部",
            branch_id="office-01",
            command="rm -rf build",
            write_paths=["scripts/generated.py"],
        )

        self.assertFalse(result.ok)
        self.assertIn("requires approval evidence", result.errors[0])

    def test_pre_action_allows_approval_gated_dangerous_command_with_evidence(self) -> None:
        dispatch = (self.temp_dir / "dispatch-order.md").read_text(encoding="utf-8")
        dispatch = dispatch.replace("危险命令策略：no destructive commands", "危险命令策略：approval required")
        (self.temp_dir / "dispatch-order.md").write_text(dispatch, encoding="utf-8")

        result = check_pre_action(
            self.temp_dir,
            office="工部",
            branch_id="office-01",
            command="rm -rf build",
            write_paths=["scripts/generated.py"],
            approval_evidence="user approved cleanup",
        )

        self.assertTrue(result.ok, result.errors)

    def test_post_action_records_event_and_execution_observation(self) -> None:
        result = record_post_action(
            self.temp_dir,
            state="六部执行",
            office="工部",
            summary="Generated harness hook",
            evidence="tests/test_harness_hooks.py",
            touched_files=["scripts/harness_hooks.py", "tests/test_harness_hooks.py"],
        )

        self.assertTrue(result.ok, result.errors)
        ledger = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("状态：六部执行", ledger)
        observations = (self.temp_dir / "execution-observations.jsonl").read_text(encoding="utf-8")
        observation = json.loads(observations.splitlines()[-1])
        self.assertEqual(observation["office"], "工部")
        self.assertEqual(observation["event"], "Generated harness hook")
        self.assertEqual(observation["evidence"]["touched_files"], ["scripts/harness_hooks.py", "tests/test_harness_hooks.py"])

    def test_subagent_return_flags_missing_return_artifact(self) -> None:
        return_path = self.temp_dir / "subagents" / "returns" / "subagent-return-office-01.md"
        return_path.unlink()

        result = check_subagent_return(self.temp_dir, branch_id="office-01")

        self.assertFalse(result.ok)
        self.assertIn("return artifact is missing", result.errors[0])

    def test_workflow_graduation_warns_on_repeated_stable_task_signal(self) -> None:
        (self.temp_dir / "event-ledger.md").write_text(
            "# 事件簿\n\n"
            "- 时间：2026-05-20T00:00:00+00:00\n"
            "  状态：六部执行\n"
            "  动作：录案\n"
            "  发起：工部\n"
            "  摘要：Repeated stable catalog refresh\n"
            "  证据：event-ledger.md\n\n"
            "- 时间：2026-05-20T00:01:00+00:00\n"
            "  状态：六部执行\n"
            "  动作：录案\n"
            "  发起：工部\n"
            "  摘要：Repeated stable catalog refresh\n"
            "  证据：event-ledger.md\n\n"
            "- 时间：2026-05-20T00:02:00+00:00\n"
            "  状态：六部执行\n"
            "  动作：录案\n"
            "  发起：工部\n"
            "  摘要：Repeated stable catalog refresh\n"
            "  证据：event-ledger.md\n",
            encoding="utf-8",
        )

        result = detect_workflow_graduation(self.temp_dir)

        self.assertTrue(result.ok, result.errors)
        self.assertIn("workflow graduation candidate", result.warnings[0])

    def test_pre_action_cli_preserves_subcommand_and_checked_command(self) -> None:
        dispatch = (self.temp_dir / "dispatch-order.md").read_text(encoding="utf-8")
        dispatch = dispatch.replace("危险命令策略：no destructive commands", "危险命令策略：approval required")
        (self.temp_dir / "dispatch-order.md").write_text(dispatch, encoding="utf-8")

        args = build_parser().parse_args(
            [
                "pre-action",
                str(self.temp_dir),
                "--branch-id",
                "office-01",
                "--command",
                "rm -rf build",
                "--write-path",
                "scripts/generated.py",
            ]
        )
        result = dispatch_cli(args)

        self.assertFalse(result.ok)
        self.assertIn("requires approval evidence", result.errors[0])

    def test_dissatisfaction_diagnostic_writes_required_sections_and_case_evidence(self) -> None:
        result = create_dissatisfaction_diagnostic(
            self.temp_dir,
            complaint="诊断：这次没有验证就说完成",
            output_name="dissatisfaction-diagnostic.md",
        )

        self.assertTrue(result.ok, result.errors)
        diagnostic = (self.temp_dir / "dissatisfaction-diagnostic.md").read_text(encoding="utf-8")
        self.assertIn("## 不满意点复述", diagnostic)
        self.assertIn("这次没有验证就说完成", diagnostic)
        self.assertIn("## 原始承诺 / 成功标准对照", diagnostic)
        self.assertIn("用户目标：Make sxlb enforceable", diagnostic)
        self.assertIn("成功标准：Validator and scaffolder work", diagnostic)
        self.assertIn("主要失败位置：verification", diagnostic)
        self.assertIn("## 证据链", diagnostic)
        self.assertIn("verification.md", diagnostic)
        self.assertIn("## 最小修复路线", diagnostic)

    def test_dissatisfaction_diagnostic_cli_writes_custom_output(self) -> None:
        args = build_parser().parse_args(
            [
                "diagnose-dissatisfaction",
                str(self.temp_dir),
                "--complaint",
                "追因：回奏没有说明剩余风险",
                "--output",
                "diagnostics/custom.md",
            ]
        )
        result = dispatch_cli(args)

        self.assertTrue(result.ok, result.errors)
        self.assertTrue((self.temp_dir / "diagnostics" / "custom.md").exists())
        self.assertEqual(result.data["failure_location"], "reporting")

    def test_route_admission_allows_a_fast_lane_with_volatile_record(self) -> None:
        make_a_fast_lane_package(self.temp_dir)

        result = check_route_admission(self.temp_dir)

        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.data["task_class"], "A")
        self.assertEqual(result.data["route"], "太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏")

    def test_route_admission_blocks_a_case_that_routes_through_zhongshu(self) -> None:
        make_a_fast_lane_package(self.temp_dir)
        case_path = self.temp_dir / "case.md"
        case_path.write_text(
            case_path.read_text(encoding="utf-8").replace(
                "当前建议链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏",
                "当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏",
            ),
            encoding="utf-8",
        )

        result = check_route_admission(self.temp_dir)

        self.assertFalse(result.ok)
        self.assertIn("A task must use fast lane route", result.errors[0])

    def test_route_admission_blocks_heavy_artifacts_for_a_case(self) -> None:
        make_a_fast_lane_package(self.temp_dir)
        (self.temp_dir / "zhongshu-plan.md").write_text("# 中书方案\n", encoding="utf-8")
        (self.temp_dir / "verification.md").write_text("# 验证\n", encoding="utf-8")

        result = check_route_admission(self.temp_dir)

        self.assertFalse(result.ok)
        self.assertTrue(any("heavy artifact" in error for error in result.errors))

    def test_route_admission_blocks_direct_handling_and_missing_record_for_a_case(self) -> None:
        make_a_fast_lane_package(self.temp_dir)
        (self.temp_dir / "volatile-record.md").unlink()
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace("执行方式：local-office", "执行方式：direct handling"),
            encoding="utf-8",
        )

        result = check_route_admission(self.temp_dir)

        self.assertFalse(result.ok)
        self.assertTrue(any("direct handling" in error for error in result.errors))
        self.assertTrue(any("volatile-record.md is required" in error for error in result.errors))

    def test_route_admission_cli_reports_a_fast_lane_result(self) -> None:
        make_a_fast_lane_package(self.temp_dir)
        args = build_parser().parse_args(["route-admission", str(self.temp_dir)])

        result = dispatch_cli(args)

        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.data["task_class"], "A")


if __name__ == "__main__":
    unittest.main()
