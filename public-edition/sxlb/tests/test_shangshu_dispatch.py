import json
import shutil
import tempfile
import unittest
from pathlib import Path

from shangshu_dispatch import prepare_dispatch


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_real_dispatch_case(root: Path) -> None:
    write(
        root / "case.md",
        """# 立案单

## 基本信息

- 任务：Prepare real dispatch
- 用户目标：Create real subagent work packets
- 约束：Keep scope bounded
- 风险级别：medium
- 案卷路径：$SXLB_CASE_ROOT/sxlb/test-dispatch-case
- restart 目标：n/a
- 能力召回：family:sxlb-governance, family:automation-integration

## 任务分类

- 任务类别：C
- 最小合法链路：太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏
- 当前建议链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏
- 首办官署：尚书省
- 下一站：尚书省

## 立案备注

- 关键未知：none
- 需要用户确认：no
- 可能更新的 canonical：none
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
- 能力召回：family:sxlb-governance, family:automation-integration
- delegation 可用性：available
- 本线办理理由：not-needed
- 返回审议点：门下复核
- 合流要求：merge required
- 合流摘要：subagents/merge-summary.md

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Implement scripts
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：protocols/
- 可写范围：scripts/, tests/
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：boundary conflict

- 官署：刑部
- 分支编号：office-02
- 任务：Verify scripts
- 所有权：tests/
- 共享只读：scripts/
- 禁写范围：protocols/
- 可写范围：scripts/, tests/
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python, unittest
- 禁止越权：do not edit protocols
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-02.md
- 回传物：subagents/returns/subagent-return-office-02.md
- 升级条件：verification ambiguity

## 双轨附记

- 文线：n/a
- 武线：工部与刑部并行
- 合流点：门下复核
- 合流负责：工部
""",
    )
    write(root / "event-ledger.md", "# 事件簿\n")


def make_local_dispatch_case(root: Path) -> None:
    make_real_dispatch_case(root)
    write(
        root / "dispatch-order.md",
        """# 派令

## 派发信息

- 当前阶段：尚书派发
- 拓扑：serial
- 执行方式：local-office
- 真实派发：no
- 能力召回：family:sxlb-governance
- delegation 可用性：available
- 本线办理理由：high coupling across a single file
- 返回审议点：门下复核
- 合流要求：not required
- 合流摘要：n/a

## 官署分派

- 官署：工部
- 分支编号：office-local-gongbu
- 任务：Implement scripts locally
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：protocols/
- 可写范围：scripts/, tests/
- 危险命令策略：no destructive commands
- 需额外批准动作：none
- 整合者：工部
- 允许技能：python
- 禁止越权：do not edit protocols
- 分支执行：local-office
- 工作包：n/a
- 回传物：local notes
- 升级条件：if file boundary becomes unclear

## 双轨附记

- 文线：n/a
- 武线：n/a
- 合流点：门下复核
- 合流负责：工部
""",
    )


class ShangshuDispatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-shangshu-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_prepare_real_dispatch_creates_packets_summary_and_ledger_entry(self) -> None:
        make_real_dispatch_case(self.temp_dir)
        result = prepare_dispatch(self.temp_dir, force=True)
        self.assertEqual(result["mode"], "real-subagent")
        self.assertEqual(result["real_packet_count"], 2)
        self.assertTrue((self.temp_dir / "subagents" / "subagent-work-packet-office-01.md").exists())
        summary_path = self.temp_dir / "shangshu-dispatch-summary.md"
        self.assertTrue(summary_path.exists())
        self.assertIn("真实派发分支：2", summary_path.read_text(encoding="utf-8"))
        self.assertIn("能力召回：family:sxlb-governance, family:automation-integration", summary_path.read_text(encoding="utf-8"))
        ledger_text = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("动作：dispatch", ledger_text)
        self.assertIn("证据：dispatch-order.md, shangshu-dispatch-summary.md", ledger_text)

    def test_prepare_local_dispatch_skips_packets_but_still_writes_summary(self) -> None:
        make_local_dispatch_case(self.temp_dir)
        result = prepare_dispatch(self.temp_dir, force=True)
        self.assertEqual(result["mode"], "local-office")
        self.assertEqual(result["real_packet_count"], 0)
        self.assertFalse((self.temp_dir / "subagents" / "manifest.json").exists())
        summary_text = (self.temp_dir / "shangshu-dispatch-summary.md").read_text(encoding="utf-8")
        self.assertIn("执行方式：local-office", summary_text)
        self.assertIn("本线办理理由：high coupling across a single file", summary_text)

    def test_prepare_rejects_non_dispatch_stage(self) -> None:
        make_real_dispatch_case(self.temp_dir)
        dispatch_path = self.temp_dir / "dispatch-order.md"
        dispatch_path.write_text(
            dispatch_path.read_text(encoding="utf-8").replace("当前阶段：尚书派发", "当前阶段：门下审议"),
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            prepare_dispatch(self.temp_dir, force=True)


if __name__ == "__main__":
    unittest.main()
