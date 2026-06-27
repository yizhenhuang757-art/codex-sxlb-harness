import shutil
import tempfile
import unittest
from pathlib import Path

from sxlb_case_status import close_case, transition_case
from test_sxlb_guard import make_valid_case_package


class CaseStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-case-status-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_transition_records_luan_and_refreshes_registry(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "artifact-registry.md").write_text(
            """# 产物注册表

| 产物 | 生成官署 | 状态 | 下游消费 | blocking |
|---|---|---|---|---|
| case.md | 太子 | draft | 中书省 | yes |
""",
            encoding="utf-8",
        )

        result = transition_case(
            self.temp_dir,
            to_state="待分流",
            office="礼部",
            summary="Records routing refreshed",
            evidence="records-routing.md",
        )

        self.assertEqual(result["state"], "待分流")
        ledger = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("状态：待分流", ledger)
        self.assertIn("动作：录案", ledger)
        registry = (self.temp_dir / "artifact-registry.md").read_text(encoding="utf-8")
        self.assertIn("learning-candidates.jsonl", registry)
        self.assertNotIn("draft", registry)

    def test_close_case_refreshes_registry_and_runs_guard(self) -> None:
        make_valid_case_package(self.temp_dir)
        (self.temp_dir / "artifact-registry.md").write_text(
            "# 产物注册表\n\n| 产物 | 生成官署 | 状态 | 下游消费 | blocking |\n",
            encoding="utf-8",
        )

        result = close_case(self.temp_dir)

        self.assertTrue(result["guard"]["ok"], result["guard"])
        self.assertEqual(result["state"], "已回奏")
        ledger = (self.temp_dir / "event-ledger.md").read_text(encoding="utf-8")
        self.assertIn("状态：已回奏", ledger)
        self.assertIn("动作：录案", ledger)
        registry = (self.temp_dir / "artifact-registry.md").read_text(encoding="utf-8")
        self.assertIn("memorial-report.md", registry)
        self.assertIn("records-routing.md", registry)

    def test_close_case_deletes_unrouted_volatile_record(self) -> None:
        make_valid_case_package(self.temp_dir)
        volatile_record = self.temp_dir / "volatile-record.md"
        volatile_record.write_text(
            "# Volatile Record\n\n"
            "- 记录类型：volatile\n"
            "- 持久出口：none\n"
            "- 清理策略：delete-on-退朝\n",
            encoding="utf-8",
        )

        result = close_case(self.temp_dir)

        self.assertFalse(volatile_record.exists())
        self.assertEqual(result["volatile_record"]["state"], "deleted")

    def test_close_case_preserves_routed_volatile_record(self) -> None:
        make_valid_case_package(self.temp_dir)
        volatile_record = self.temp_dir / "volatile-record.md"
        volatile_record.write_text(
            "# Volatile Record\n\n"
            "- 记录类型：volatile\n"
            "- 持久出口：case, restart\n"
            "- 清理策略：delete-on-退朝\n",
            encoding="utf-8",
        )

        result = close_case(self.temp_dir)

        self.assertTrue(volatile_record.exists())
        self.assertEqual(result["volatile_record"]["state"], "preserved")

    def test_close_case_runs_harness_completion_advisories(self) -> None:
        make_valid_case_package(self.temp_dir)
        ledger = (self.temp_dir / "event-ledger.md")
        ledger.write_text(
            ledger.read_text(encoding="utf-8").rstrip()
            + "\n\n"
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

        result = close_case(self.temp_dir)

        self.assertTrue(result["guard"]["ok"], result["guard"])
        self.assertIn("harness_hooks", result)
        self.assertIn("workflow graduation candidate", result["harness_hooks"]["warnings"][0])


if __name__ == "__main__":
    unittest.main()
