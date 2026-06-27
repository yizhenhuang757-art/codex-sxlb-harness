import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
SCRIPT = SCRIPTS / "sxlb_action_dispatcher.py"


class SxlbActionDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-action-dispatcher-"))
        (self.temp_dir / "state-packet.md").write_text(
            "# SXLB State Packet\n\n- Goal: keep resume tiny\n- Next Step: 门下复核\n",
            encoding="utf-8",
        )
        (self.temp_dir / "dispatch-order.md").write_text(
            """# 派令

## 官署分派

- 官署：工部
- 分支编号：local-implementation
- 可写范围：src
- 禁写范围：secrets
- 危险命令策略：approval-required
""",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_dispatcher(self, payload, *, profile="standard"):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        env["SXLB_PROFILE"] = profile
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_pre_action_runs_gateguard_and_write_scope_checks(self):
        payload = {
            "event": "pre_action",
            "case": str(self.temp_dir),
            "office": "工部",
            "command": "echo ok",
            "write_paths": ["src/app.py"],
        }

        result = self.run_dispatcher(payload)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["event"], "pre_action")
        steps = {step["id"]: step for step in data["steps"]}
        self.assertIn("gateguard", steps)
        self.assertIn("pre-action-scope", steps)
        self.assertTrue(steps["pre-action-scope"]["ok"])

    def test_completion_ready_minimal_suggests_quality_gate_without_running_heavy_guard(self):
        payload = {"event": "completion_ready", "case": str(self.temp_dir), "task_class": "A"}

        result = self.run_dispatcher(payload, profile="minimal")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        steps = {step["id"]: step for step in data["steps"]}
        self.assertEqual(steps["completion-quality-gate"]["status"], "skipped")
        self.assertEqual(steps["completion-quality-gate"]["reason"], "minimal profile")

    def test_case_resume_reads_state_packet_as_reference_only(self):
        payload = {"event": "case.resume", "case": str(self.temp_dir)}

        result = self.run_dispatcher(payload)

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        steps = {step["id"]: step for step in data["steps"]}
        self.assertTrue(steps["resume-packet"]["ok"])
        self.assertEqual(steps["resume-packet"]["data"]["instruction_policy"], "historical-reference-only")
        self.assertIn("state-packet.md", steps["resume-packet"]["data"]["read_first"])


if __name__ == "__main__":
    unittest.main()
