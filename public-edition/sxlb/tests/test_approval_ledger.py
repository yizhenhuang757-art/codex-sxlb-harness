import shutil
import tempfile
import unittest
from pathlib import Path

from approval_ledger import collect_approval_entries, write_approval_ledger


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_approval_case(root: Path) -> None:
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
- 返回审议点：门下复核
- 合流要求：not required
- 合流摘要：n/a

## 官署分派

- 官署：工部
- 分支编号：office-01
- 任务：Perform approved cleanup
- 所有权：scripts/
- 共享只读：tests/
- 禁写范围：docs/
- 可写范围：scripts/
- 真实触达审计：not required
- 危险命令策略：approval required
- 需额外批准动作：destructive commands
- 整合者：工部
- 允许技能：python
- 禁止越权：do not touch docs
- 分支执行：real-subagent
- 工作包：subagents/subagent-work-packet-office-01.md
- 回传物：subagents/returns/subagent-return-office-01.md
- 升级条件：approval missing
""",
    )
    write(
        root / "subagents" / "returns" / "subagent-return-office-01.md",
        """# 子代理回传物

## 基本信息

- 分支编号：office-01
- 回传状态：complete

## 证据与产物

- 触达文件/产物：scripts/cache
- 新增证据：manual verification passed
- 额外批准证据：user approved cleanup in current thread
- 关键命令或动作：rm -rf scripts/cache
""",
    )


class ApprovalLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-approval-ledger-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_collect_approval_entries_from_real_subagent_returns(self) -> None:
        make_approval_case(self.temp_dir)

        entries = collect_approval_entries(self.temp_dir)

        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["branch"], "office-01")
        self.assertEqual(entry["office"], "工部")
        self.assertEqual(entry["command"], "rm -rf scripts/cache")
        self.assertEqual(entry["approval_status"], "present")
        self.assertEqual(entry["approval_evidence"], "user approved cleanup in current thread")

    def test_write_approval_ledger_creates_markdown_table(self) -> None:
        make_approval_case(self.temp_dir)

        path = write_approval_ledger(self.temp_dir)

        text = path.read_text(encoding="utf-8")
        self.assertIn("| branch | office | command | approval_status | approval_evidence | return |", text)
        self.assertIn("| office-01 | 工部 | `rm -rf scripts/cache` | present | user approved cleanup in current thread | subagents/returns/subagent-return-office-01.md |", text)


if __name__ == "__main__":
    unittest.main()
