import json
import subprocess
import sys
import unittest
from pathlib import Path

from sxlb_case_intake import advise_case_action, parse_recall_json


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_case_intake.py"


class SxlbCaseIntakeTests(unittest.TestCase):
    def test_recommends_reuse_for_high_confidence_match_when_no_current_case(self):
        packet = {
            "matches": [
                {
                    "project": "sxlb/status-board-renderer",
                    "confidence": "high",
                    "score": 24,
                    "first_read": "/tmp/case/memorial-report.md",
                }
            ]
        }

        result = advise_case_action("面板脚本化", current_case=None, recall_payload=packet)

        self.assertEqual(result["action"], "reuse")
        self.assertEqual(result["case"], "sxlb/status-board-renderer")
        self.assertTrue(result["recall_required"])

    def test_recommends_create_when_no_recall_match(self):
        result = advise_case_action("全新任务", current_case=None, recall_payload={"matches": []})

        self.assertEqual(result["action"], "create")
        self.assertTrue(result["recall_required"])

    def test_current_case_short_circuits_recall_requirement(self):
        result = advise_case_action("继续当前任务", current_case="/tmp/case", recall_payload={"matches": []})

        self.assertEqual(result["action"], "use_current")
        self.assertFalse(result["recall_required"])
        self.assertEqual(result["case"], "/tmp/case")

    def test_parse_recall_json_accepts_json_text(self):
        parsed = parse_recall_json(json.dumps({"matches": [{"project": "x"}]}))

        self.assertEqual(parsed["matches"][0]["project"], "x")

    def test_cli_can_advise_from_recall_json_file(self):
        path = Path("/tmp/sxlb_case_intake_recall.json")
        path.write_text(json.dumps({"matches": []}), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--query", "全新任务", "--recall-json-file", str(path), "--json"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "create")


if __name__ == "__main__":
    unittest.main()
