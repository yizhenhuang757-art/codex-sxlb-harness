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


class SxlbSystemHealthBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-system-health-"))
        (self.temp_dir / "state-packet.md").write_text("# SXLB State Packet\n", encoding="utf-8")
        (self.temp_dir / "dispatch-order.md").write_text(
            """# 派令

## 官署分派

- 官署：吏部
- 分支编号：system-health
- 可写范围：$SXLB_HOME
- 禁写范围：$SXLB_HOME/MODE.md
- 危险命令策略：approval-required
""",
            encoding="utf-8",
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def run_script(self, name, payload=None, *args, profile=None):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        if profile:
            env["SXLB_PROFILE"] = profile
        return subprocess.run(
            [sys.executable, str(SCRIPTS / name), *args],
            input=json.dumps(payload or {}),
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_risk_scorer_recommends_strict_for_sxlb_canonical_edits(self):
        payload = {
            "event": "pre_action",
            "write_paths": [str(SXLB_ROOT / "MODE.md")],
            "command": "echo ok",
        }

        result = self.run_script("sxlb_risk_scorer.py", payload, "--json")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["recommended_profile"], "strict")
        self.assertIn("canonical-or-protected-path", data["reasons"])

    def test_config_protection_requires_change_plan_for_protected_config(self):
        payload = {
            "paths": [str(SXLB_ROOT / "MODE.md")],
            "fact_package": {
                "caller": "test",
                "affected_states_offices_scripts": "MODE",
                "user_instruction": "protect config",
                "rollback_plan": "restore MODE",
            },
        }

        result = self.run_script("sxlb_config_protection.py", payload, "--json")

        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "require-review")
        self.assertIn("missing-change-plan", {item["category"] for item in data["findings"]})

    def test_config_protection_requires_change_plan_for_script_surface(self):
        payload = {
            "paths": [str(SXLB_ROOT / "scripts" / "sxlb_action_dispatcher.py")],
            "fact_package": {
                "caller": "test",
                "affected_states_offices_scripts": "dispatcher",
                "user_instruction": "protect script runtime",
                "rollback_plan": "restore dispatcher",
            },
        }

        result = self.run_script("sxlb_config_protection.py", payload, "--json")

        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "require-review")
        self.assertIn(str(SXLB_ROOT / "scripts" / "sxlb_action_dispatcher.py"), data["protected_paths"])

    def test_change_plan_check_allows_matching_protected_path(self):
        plan_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "sxlb_change_plan.py"),
                "plan",
                "--case",
                str(self.temp_dir),
                "--title",
                "protect mode change",
                "--path",
                str(SXLB_ROOT / "MODE.md"),
                "--rollback",
                "restore MODE.md",
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS)},
        )
        self.assertEqual(plan_result.returncode, 0, plan_result.stderr + plan_result.stdout)
        plan_id = json.loads(plan_result.stdout)["plan_id"]

        check_payload = {"case": str(self.temp_dir), "change_plan_id": plan_id, "paths": [str(SXLB_ROOT / "MODE.md")]}
        check_result = self.run_script("sxlb_change_plan.py", check_payload, "check", "--json")

        self.assertEqual(check_result.returncode, 0, check_result.stderr + check_result.stdout)
        data = json.loads(check_result.stdout)
        self.assertTrue(data["ok"])

    def test_dispatcher_auto_profile_and_metrics_with_case(self):
        payload = {
            "event": "case.resume",
            "case": str(self.temp_dir),
            "write_paths": [str(SXLB_ROOT / "scripts" / "sxlb_action_dispatcher.py")],
        }

        result = self.run_script("sxlb_action_dispatcher.py", payload, "--json", profile="auto")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["profile"], "strict")
        self.assertEqual(data["risk"]["recommended_profile"], "strict")
        self.assertEqual(data["metrics"]["status"], "written")
        self.assertTrue((self.temp_dir / "runtime-metrics.jsonl").exists())

    def test_dispatcher_skips_metrics_without_case(self):
        payload = {"event": "completion_ready", "task_class": "A"}

        result = self.run_script("sxlb_action_dispatcher.py", payload, "--json", profile="minimal")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["metrics"]["status"], "skipped")
        self.assertEqual(data["metrics"]["reason"], "no case")

    def test_quality_gate_plan_maps_touched_files_to_validation_commands(self):
        payload = {
            "event": "completion_ready",
            "case": str(self.temp_dir),
            "touched_files": [
                str(SXLB_ROOT / "hooks" / "sxlb-hooks.json"),
                str(SXLB_ROOT / "scripts" / "sxlb_action_dispatcher.py"),
            ],
        }

        result = self.run_script("sxlb_action_dispatcher.py", payload, "--json", profile="minimal")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        data = json.loads(result.stdout)
        commands = " ".join(item["command"] for item in data["quality_plan"]["commands"])
        self.assertIn("validate_sxlb_hooks.py", commands)
        self.assertIn("unittest", commands)


if __name__ == "__main__":
    unittest.main()
