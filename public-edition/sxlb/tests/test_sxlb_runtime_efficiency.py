import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from sxlb_event_router import route_event


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"


class SxlbRuntimeEfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-runtime-efficiency-"))
        (self.temp_dir / "case.md").write_text(
            "# Case\n\n- 用户目标：make sxlb faster\n- 当前状态：六部执行\n",
            encoding="utf-8",
        )
        (self.temp_dir / "verification.md").write_text(
            "# 验证记录\n\n"
            "## Parent\n\n"
            "### Old\n\n"
            "- 路由红灯结果：`体检` 返回 `unknown`。\n\n"
            "### Latest\n\n"
            "- 全量测试：Ran 244 tests ... OK\n"
            "- 当前提示项：mcp 为 unknown，不阻断普通使用。\n",
            encoding="utf-8",
        )
        (self.temp_dir / "implementation-notes.md").write_text(
            "# Implementation Notes\n\n"
            "## Early\n\n"
            "- 新增 old-script.py\n\n"
            "## Latest\n\n"
            "- 新增 scripts/sxlb_state_packet.py\n",
            encoding="utf-8",
        )
        (self.temp_dir / "restart.md").write_text(
            "# Restart\n\n- 下一步：wire pre_compact hook\n",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_script(self, script_name, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script_name), *args],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_state_packet_json_is_small_and_resume_ready(self):
        result = self.run_script("sxlb_state_packet.py", str(self.temp_dir), "--json")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["case"], str(self.temp_dir))
        self.assertLess(payload["budget"]["packet_chars"], 2500)
        self.assertIn("goal", payload)
        self.assertIn("state", payload)
        self.assertIn("next_step", payload)
        self.assertIn("verification", payload)
        self.assertIn("files_changed", payload)
        self.assertTrue(any("244 tests" in item for item in payload["verification"]))
        self.assertTrue(any("sxlb_state_packet.py" in item for item in payload["files_changed"]))
        self.assertFalse(any("old-script.py" in item for item in payload["files_changed"]))
        self.assertTrue(any("mcp" in item for item in payload["open_risks"]))
        self.assertFalse(any("红灯结果" in item for item in payload["open_risks"]))

    def test_state_packet_markdown_can_write_resume_packet(self):
        output = self.temp_dir / "state-packet.md"
        result = self.run_script("sxlb_state_packet.py", str(self.temp_dir), "--write", str(output))

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        text = output.read_text(encoding="utf-8")
        self.assertIn("# SXLB State Packet", text)
        self.assertIn("Next Step", text)
        self.assertLess(len(text), 2500)

    def test_pre_compact_event_routes_to_state_packet_generator(self):
        packet = route_event({"event": "case.pre_compact", "case": str(self.temp_dir)})

        self.assertEqual(packet["timing"], "before-compact")
        hooks = {hook["hook"]: hook for hook in packet["hooks"]}
        self.assertIn("state-packet", hooks)
        self.assertIn("sxlb_state_packet.py", hooks["state-packet"]["command_hint"])
        self.assertFalse(hooks["state-packet"]["blocking"])

    def test_harness_audit_reports_redundancy_candidates(self):
        result = self.run_script("sxlb_harness_audit.py", "--json")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("candidates", payload)
        self.assertGreaterEqual(len(payload["candidates"]), 1)
        self.assertTrue(
            any(item["recommendation"] in {"defer", "compress", "keep-on-demand"} for item in payload["candidates"])
        )


if __name__ == "__main__":
    unittest.main()
