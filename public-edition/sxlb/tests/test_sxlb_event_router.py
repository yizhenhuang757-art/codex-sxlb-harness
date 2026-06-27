import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sxlb_event_router import build_event_packet, check_plan_ready, parse_event_text, route_event


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_event_router.py"


class SxlbEventRouterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-event-router-"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_parse_low_token_event_text(self):
        event = parse_event_text("zhongshu.plan_ready case=/tmp/case task_class=B")

        self.assertEqual(event["event"], "zhongshu.plan_ready")
        self.assertEqual(event["case"], "/tmp/case")
        self.assertEqual(event["task_class"], "B")

    def test_zhongshu_plan_ready_is_at_ready_gate_not_after_complete(self):
        packet = route_event({"event": "zhongshu.plan_ready", "case": "/tmp/case"})

        self.assertEqual(packet["timing"], "at-ready")
        self.assertEqual(packet["policy"], "explicit-event")
        self.assertIn("plan-precheck", [hook["hook"] for hook in packet["hooks"]])
        plan_hook = [hook for hook in packet["hooks"] if hook["hook"] == "plan-precheck"][0]
        self.assertTrue(plan_hook["blocking"])
        self.assertIn("--check-plan-ready", plan_hook["command_hint"])
        self.assertNotEqual(packet["timing"], "after-complete")

    def test_check_plan_ready_blocks_missing_required_fields(self):
        (self.temp_dir / "zhongshu-plan.md").write_text(
            """# 中书方案

## 目标与边界

- 目标：<goal>
- 不做什么：none
- 成功标准：tests pass
""",
            encoding="utf-8",
        )

        result = check_plan_ready(self.temp_dir)

        self.assertFalse(result["ok"])
        self.assertEqual(result["timing"], "at-ready")
        self.assertIn("missing or placeholder field: 目标", result["errors"])
        self.assertIn("missing or placeholder field: 主任务", result["errors"])

    def test_check_plan_ready_passes_filled_plan_shape(self):
        (self.temp_dir / "zhongshu-plan.md").write_text(
            """# 中书方案

## 目标与边界

- 目标：make explicit events trigger scripts at governed boundaries
- 不做什么：do not read private reasoning or load all protocols
- 成功标准：router tests and docs bind before-enter / at-ready semantics

## 任务拆解

- 主任务：implement thin event router
- 子任务：document minimal contract and verify hooks

## 四问校准

- 验证方式：unit tests and guard

## 路由建议

- 任务类别：B
- 推荐链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏

## 技能与官署映射

- 主要官署：吏部, 兵部, 刑部
- 能力召回：family:sxlb-governance, family:automation-integration
""",
            encoding="utf-8",
        )

        result = check_plan_ready(self.temp_dir)

        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])

    def test_cli_check_plan_ready_returns_nonzero_when_blocked(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--check-plan-ready", str(self.temp_dir), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("missing zhongshu-plan.md", payload["errors"])

    def test_shangshu_dispatch_ready_requires_dispatch_precheck(self):
        packet = route_event({"event": "shangshu.dispatch_ready", "case": "/tmp/case"})

        hooks = [hook["hook"] for hook in packet["hooks"]]
        self.assertEqual(packet["timing"], "at-ready")
        self.assertIn("capability-semantic-bridge", hooks)
        self.assertIn("capability-recall", hooks)
        self.assertIn("dispatch-precheck", hooks)
        dispatch_hook = [hook for hook in packet["hooks"] if hook["hook"] == "dispatch-precheck"][0]
        self.assertIn("shangshu_dispatch.py", dispatch_hook["command_hint"])
        recall_hook = [hook for hook in packet["hooks"] if hook["hook"] == "capability-recall"][0]
        self.assertFalse(recall_hook["blocking"])
        self.assertIn("--semantic-keyword", recall_hook["command_hint"])
        self.assertIn("recall_capabilities.py", recall_hook["command_hint"])

    def test_taizi_intake_ready_recommends_capability_recall_without_blocking(self):
        packet = route_event({"event": "taizi.intake_ready", "case": "/tmp/case"})

        self.assertEqual(packet["timing"], "at-ready")
        self.assertEqual([hook["hook"] for hook in packet["hooks"]], ["capability-semantic-bridge", "capability-recall"])
        self.assertFalse(packet["hooks"][0]["blocking"])
        self.assertFalse(packet["hooks"][1]["blocking"])
        self.assertIn("semantic_keywords", packet["hooks"][0]["command_hint"])
        self.assertIn("--phase intake", packet["hooks"][1]["command_hint"])

    def test_zhongshu_plan_ready_recommends_capability_recall_before_plan_precheck(self):
        packet = route_event({"event": "zhongshu.plan_ready", "case": "/tmp/case"})

        hooks = [hook["hook"] for hook in packet["hooks"]]
        self.assertEqual(hooks, ["capability-semantic-bridge", "capability-recall", "plan-precheck"])
        self.assertFalse(packet["hooks"][0]["blocking"])
        self.assertFalse(packet["hooks"][1]["blocking"])
        self.assertTrue(packet["hooks"][2]["blocking"])

    def test_menxia_completion_ready_reuses_arrival_hooks_at_ready(self):
        packet = route_event(
            {
                "event": "menxia.completion_ready",
                "case": "/tmp/case",
                "task_class": "B",
                "office": "刑部",
                "human_facing_change": True,
            }
        )

        hooks = [hook["hook"] for hook in packet["hooks"]]
        self.assertEqual(packet["timing"], "at-ready")
        self.assertIn("completion-precheck", hooks)
        self.assertIn("verification-snippet", hooks)
        self.assertIn("records-routing-candidate", hooks)
        self.assertIn("qijulang-candidate", hooks)

    def test_reply_substantive_is_before_emit_gate(self):
        packet = route_event({"event": "reply.substantive", "case": "/tmp/case"})

        self.assertEqual(packet["timing"], "before-emit")
        self.assertEqual(packet["hooks"][0]["hook"], "reply-generation")
        self.assertIn("sxlb_reply.py", packet["hooks"][0]["command_hint"])

    def test_unknown_event_is_non_expanding(self):
        packet = route_event({"event": "unknown.event", "case": "/tmp/case"})

        self.assertEqual(packet["hooks"], [])
        self.assertEqual(packet["unknown_event"], "unknown.event")
        self.assertEqual(packet["policy"], "explicit-event")

    def test_build_event_packet_from_json_or_text(self):
        self.assertEqual(build_event_packet({"event": "reply.substantive"})["event"], "reply.substantive")
        self.assertEqual(build_event_packet("reply.substantive case=/tmp/case")["case"], "/tmp/case")

    def test_cli_reads_text_event_and_outputs_json(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            input="reply.substantive case=/tmp/case",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["event"], "reply.substantive")
        self.assertIn("sxlb_reply.py", payload["hooks"][0]["command_hint"])


if __name__ == "__main__":
    unittest.main()
