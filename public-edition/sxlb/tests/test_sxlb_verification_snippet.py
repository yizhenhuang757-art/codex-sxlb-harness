import json
import subprocess
import sys
import unittest
from pathlib import Path

from sxlb_verification_snippet import should_generate_snippet, render_snippet


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_verification_snippet.py"


class SxlbVerificationSnippetTests(unittest.TestCase):
    def test_generation_condition_requires_bcd_completion_and_xingbu(self):
        self.assertTrue(should_generate_snippet({"task_class": "B", "phase": "completion", "office": "刑部"}))
        self.assertTrue(should_generate_snippet({"task_class": "D", "phase": "completion", "verification_output": "Ran 1 test OK"}))

        self.assertFalse(should_generate_snippet({"task_class": "A", "phase": "completion", "office": "刑部"}))
        self.assertFalse(should_generate_snippet({"task_class": "B", "phase": "startup", "office": "刑部"}))
        self.assertFalse(should_generate_snippet({"task_class": "B", "phase": "completion", "office": "礼部"}))

    def test_render_snippet_outputs_required_verification_fields(self):
        snippet = render_snippet(
            {
                "task_class": "B",
                "phase": "completion",
                "office": "刑部",
                "command": "python3 -m unittest",
                "result": "pass",
                "output": "Ran 170 tests in 1.131s OK",
                "target": "sxlb tests",
                "invariant": "all tests pass",
                "test_validity": "unittest fails on assertion or import errors",
            }
        )

        for field in ("验证目标", "受影响对象", "验证结论", "命令或动作", "结果", "行为断言/不变量", "测试有效性"):
            self.assertIn(f"- {field}：", snippet)
        self.assertIn("Ran 170 tests in 1.131s OK", snippet)

    def test_render_snippet_refuses_when_condition_not_met(self):
        with self.assertRaises(ValueError):
            render_snippet({"task_class": "A", "phase": "completion", "office": "刑部"})

    def test_cli_renders_json_input(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=json.dumps(
                {
                    "task_class": "B",
                    "phase": "completion",
                    "office": "刑部",
                    "command": "python3 -m unittest",
                    "result": "pass",
                    "output": "OK",
                },
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("- 验证结论：pass", result.stdout)


if __name__ == "__main__":
    unittest.main()
