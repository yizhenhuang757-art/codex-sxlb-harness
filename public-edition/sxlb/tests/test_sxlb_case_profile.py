import json
import subprocess
import sys
import unittest
from pathlib import Path

from sxlb_case_profile import recommend_profile


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_case_profile.py"


class SxlbCaseProfileTests(unittest.TestCase):
    def test_simple_single_office_task_can_be_lightweight_a(self):
        result = recommend_profile({"tool_actions": 1})

        self.assertEqual(result["task_class"], "A")
        self.assertEqual(result["profile"], "lightweight")
        self.assertIn("single substantive action", result["reasons"])

    def test_file_edit_or_verification_upgrades_to_b_full(self):
        result = recommend_profile({"file_edit": True, "verification": True})

        self.assertEqual(result["task_class"], "B")
        self.assertEqual(result["profile"], "full")
        self.assertIn("file edit or verification requires B route", result["reasons"])

    def test_protocol_change_or_automation_uses_full_case(self):
        result = recommend_profile({"protocol_change": True, "automation": True})

        self.assertEqual(result["task_class"], "B")
        self.assertEqual(result["profile"], "full")
        self.assertIn("protocol or automation change needs full evidence", result["reasons"])

    def test_real_subagent_or_parallel_upgrades_to_d(self):
        result = recommend_profile({"real_subagent": True, "parallel": True})

        self.assertEqual(result["task_class"], "D")
        self.assertEqual(result["profile"], "full")
        self.assertIn("real subagent or parallel topology needs D route", result["reasons"])

    def test_cli_reads_json_stdin(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            input=json.dumps({"file_edit": True}, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["task_class"], "B")
        self.assertEqual(payload["profile"], "full")


if __name__ == "__main__":
    unittest.main()
