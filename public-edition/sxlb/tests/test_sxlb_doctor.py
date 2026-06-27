import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
SCRIPT = SCRIPTS / "sxlb_doctor.py"


class SxlbDoctorTests(unittest.TestCase):
    def run_doctor(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_json_report_has_human_summary_and_core_checks(self):
        result = self.run_doctor("--json")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("ok", payload)
        self.assertIn("summary", payload)
        self.assertIn("next_actions", payload)
        checks = {check["id"]: check for check in payload["checks"]}
        self.assertEqual(
            set(checks),
            {"hook_graph", "skill_inventory", "external_capabilities", "critical_scripts"},
        )
        for check in checks.values():
            self.assertIn(check["status"], {"ok", "warn", "block", "error"})
            self.assertTrue(check["label"])
            self.assertTrue(check["detail"])

    def test_human_report_is_concise_chinese_health_check(self):
        result = self.run_doctor()

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SXLB 健康检查", result.stdout)
        self.assertIn("Hook Graph", result.stdout)
        self.assertIn("外部能力", result.stdout)
        self.assertIn("下一步", result.stdout)


if __name__ == "__main__":
    unittest.main()
