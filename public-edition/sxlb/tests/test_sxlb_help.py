import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
SCRIPT = SCRIPTS / "sxlb_help.py"


class SxlbHelpTests(unittest.TestCase):
    def run_help(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SCRIPTS)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_human_help_lists_common_commands_and_effects(self):
        result = self.run_help()

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SXLB 常用命令", result.stdout)
        self.assertIn("体检", result.stdout)
        self.assertIn("继续", result.stdout)
        self.assertIn("退朝", result.stdout)
        self.assertIn("什么时候用", result.stdout)

    def test_json_help_is_machine_readable(self):
        result = self.run_help("--json")

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertIn("commands", payload)
        commands = {item["command"]: item for item in payload["commands"]}
        self.assertIn("体检", commands)
        self.assertEqual(commands["体检"]["action"], "doctor")
        self.assertIn("use_when", commands["继续"])


if __name__ == "__main__":
    unittest.main()
