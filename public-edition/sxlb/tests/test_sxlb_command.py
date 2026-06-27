import json
import subprocess
import sys
import unittest
from pathlib import Path

from sxlb_command import route_command


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_command.py"


class SxlbCommandTests(unittest.TestCase):
    def test_routes_clear_global_commands(self):
        cases = {
            "继续": "continue",
            "暂停": "pause",
            "恢复": "resume",
            "退朝": "exit_court",
            "录案": "record_case",
            "事件簿": "show_ledger",
            "重审": "review_again",
            "会审": "deliberation",
            "国史馆": "guoshiguan",
            "起居郎": "qijulang",
            "体检": "doctor",
            "健康检查": "doctor",
            "doctor": "doctor",
            "帮助": "help",
            "help": "help",
            "怎么用": "help",
        }

        for text, action in cases.items():
            with self.subTest(text=text):
                result = route_command(text, state="六部执行")
                self.assertEqual(result["action"], action)
                self.assertEqual(result["confidence"], "high")

    def test_routes_shijiang_question(self):
        result = route_command("侍讲官 这个边界是什么意思？", state="六部执行")

        self.assertEqual(result["action"], "ask_officer")
        self.assertEqual(result["target"], "侍讲官")
        self.assertEqual(result["payload"], "这个边界是什么意思？")

    def test_routes_tuixia_by_state_without_misfiring_shijiang(self):
        self.assertEqual(route_command("退下", state="侍讲官")["action"], "shijiang_exit")
        self.assertEqual(route_command("侍讲官退下", state="侍讲官")["action"], "shijiang_exit")

        non_shijiang = route_command("退下", state="六部执行")
        self.assertEqual(non_shijiang["action"], "dismiss_current")
        self.assertEqual(non_shijiang["target"], "六部执行")

        named = route_command("侍讲官退下", state="六部执行")
        self.assertEqual(named["action"], "unknown")

    def test_cli_routes_command(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--state", "六部执行", "--json"],
            input="退下",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "dismiss_current")
        self.assertEqual(payload["target"], "六部执行")


if __name__ == "__main__":
    unittest.main()
