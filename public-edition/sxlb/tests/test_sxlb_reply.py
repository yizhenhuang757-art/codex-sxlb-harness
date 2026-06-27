import json
import subprocess
import sys
import unittest
from pathlib import Path

from sxlb_reply import build_reply, build_reply_packet, is_shijiang_exit


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_reply.py"


class SxlbReplyTests(unittest.TestCase):
    def test_build_reply_generates_board_and_memorial(self):
        reply = build_reply(
            {
                "task": "统一回复生成器",
                "state": "中书拟制",
                "runtime": "active",
                "plan": "草拟中",
                "decision_tree": "open",
                "caifeng": "n/a",
                "pending": "none",
            },
            "正文。",
        )

        self.assertTrue(reply.startswith("朝堂状态\n"))
        self.assertIn("中书：拟制 / active", reply)
        self.assertIn("## 回奏\n\n正文。", reply)
        self.assertIn("`起居郎`", reply)

    def test_reply_packet_includes_arrival_hooks_from_declared_state(self):
        packet = build_reply_packet(
            {
                "task": "手动声明门下复核",
                "state": "门下复核",
                "runtime": "active",
                "task_class": "B",
                "office": "刑部",
                "target": "completion",
                "result": "pending",
                "issues": "none",
                "artifact": "menxia-review.md",
                "pending": "none",
            },
            "正文。",
        )

        self.assertIn("## 回奏\n\n正文。", packet["reply"])
        hooks = packet["arrival_hooks"]
        self.assertIn("completion-precheck", [hook["hook"] for hook in hooks])
        self.assertIn("verification-snippet", [hook["hook"] for hook in hooks])
        self.assertTrue(all(hook["router_role"] == "index-only" for hook in hooks))

    def test_build_reply_generates_single_line_shijiang_panel(self):
        reply = build_reply({"state": "侍讲官"}, "这是解释。")

        self.assertTrue(reply.startswith("侍讲官回奏\n\n"))
        self.assertNotIn("朝堂状态", reply)
        self.assertNotIn("## 回奏", reply)
        self.assertTrue(reply.endswith("这是解释。\n"))

    def test_shijiang_exit_detection(self):
        for text in ("退下", " 退下。", "侍讲官退下", "侍讲官退下。"):
            with self.subTest(text=text):
                self.assertTrue(is_shijiang_exit(text, {"state": "侍讲官"}))

        for text in ("退朝", "继续", "请侍讲官解释一下"):
            with self.subTest(text=text):
                self.assertFalse(is_shijiang_exit(text, {"state": "侍讲官"}))

    def test_shijiang_exit_detection_is_state_scoped(self):
        self.assertFalse(is_shijiang_exit("退下"))
        self.assertFalse(is_shijiang_exit("退下", {"state": "中书拟制"}))
        self.assertFalse(is_shijiang_exit("侍讲官退下", {"state": "六部执行"}))

    def test_cli_generates_reply_from_json_stdin(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--body", "正文。"],
            input=json.dumps(
                {
                    "task": "统一回复生成器",
                    "state": "六部执行",
                    "runtime": "active",
                    "route": "太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部",
                    "case": "case/path",
                    "caifeng": "n/a",
                    "pending": "none",
                },
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("朝堂状态\n"))
        self.assertIn("## 回奏\n\n正文。", result.stdout)

    def test_cli_generates_reply_from_body_stdin_packet(self):
        packet = {
            "state": {
                "task": "统一回复生成器",
                "state": "六部执行",
                "runtime": "active",
                "route": "太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部",
                "case": "case/path",
                "caifeng": "n/a",
                "pending": "none",
            },
            "body": "第一行。\n\n第二行。",
        }
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--body-stdin"],
            input=json.dumps(packet, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith("朝堂状态\n"))
        self.assertIn("## 回奏\n\n第一行。\n\n第二行。", result.stdout)

    def test_cli_json_generates_reply_from_body_stdin_packet(self):
        packet = {
            "state": {
                "task": "手动声明门下复核",
                "state": "门下复核",
                "runtime": "active",
                "task_class": "B",
                "office": "刑部",
                "target": "completion",
                "result": "pending",
                "issues": "none",
                "artifact": "menxia-review.md",
                "pending": "none",
            },
            "body": "正文。",
        }
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--body-stdin", "--json"],
            input=json.dumps(packet, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn("## 回奏\n\n正文。", payload["reply"])
        self.assertIn("completion-precheck", [hook["hook"] for hook in payload["arrival_hooks"]])

    def test_cli_json_includes_reply_and_arrival_hooks(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--body", "正文。", "--json"],
            input=json.dumps(
                {
                    "task": "手动声明门下复核",
                    "state": "门下复核",
                    "runtime": "active",
                    "task_class": "B",
                    "office": "刑部",
                    "target": "completion",
                    "result": "pending",
                    "issues": "none",
                    "artifact": "menxia-review.md",
                    "pending": "none",
                },
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn("## 回奏\n\n正文。", payload["reply"])
        self.assertIn("verification-snippet", [hook["hook"] for hook in payload["arrival_hooks"]])

    def test_cli_detects_shijiang_exit(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--detect-shijiang-exit", "--state", "侍讲官"],
            input="侍讲官退下",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('"exit": true', result.stdout)

    def test_cli_does_not_detect_shijiang_exit_outside_shijiang_state(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--detect-shijiang-exit", "--state", "六部执行"],
            input="退下",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('"exit": false', result.stdout)


if __name__ == "__main__":
    unittest.main()
