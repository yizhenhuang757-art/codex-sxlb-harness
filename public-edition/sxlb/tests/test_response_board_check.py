import subprocess
import sys
import unittest
from pathlib import Path

from response_board_check import starts_with_board, validate_response_board


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "response_board_check.py"


class ResponseBoardCheckTests(unittest.TestCase):
    def test_active_sxlb_reply_without_board_fails(self):
        ok, errors = validate_response_board("回奏\n\n已完成。")

        self.assertFalse(ok)
        self.assertIn("active sxlb reply must begin with 朝堂状态", errors)

    def test_active_sxlb_reply_with_plain_board_passes(self):
        ok, errors = validate_response_board(
            """朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 回奏

已完成。"""
        )

        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_active_sxlb_reply_with_markdown_heading_board_passes(self):
        self.assertTrue(starts_with_board("# 朝堂状态\n状态：门下复核"))

    def test_stage_specific_compact_board_passes(self):
        draft = """朝堂状态
任务：修正输出前检查
中书：拟制 / active
方案：草拟中
决策树：open
案卷状态：无
采风：n/a
产物：`zhongshu-plan.md`
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 回奏

这里只用了中书专用紧凑面板，不是完整版。"""

        ok, errors = validate_response_board(draft)

        self.assertTrue(ok)
        self.assertEqual(errors, [])
        self.assertNotIn("当前链路", draft)

    def test_inactive_reply_without_board_passes(self):
        ok, errors = validate_response_board("普通回答。", active=False)

        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_allowed_omission_reason_passes(self):
        ok, errors = validate_response_board("已退出 sxlb。", omission_reason="exit-confirmation")

        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_cli_rejects_missing_board(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="回奏\n无面板。",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("active sxlb reply must begin with 朝堂状态", result.stderr)

    def test_cli_accepts_board(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            input="""朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 回奏

有面板。""",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('"ok": true', result.stdout)

    def test_active_sxlb_reply_without_memorial_section_fails(self):
        ok, errors = validate_response_board(
            """朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

正文。"""
        )

        self.assertFalse(ok)
        self.assertIn("active sxlb reply must include ## 回奏", errors)

    def test_active_sxlb_reply_missing_intervention_fails(self):
        ok, errors = validate_response_board(
            """朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `退朝`

## 回奏

正文。"""
        )

        self.assertFalse(ok)
        self.assertIn("missing intervention command: 起居郎", errors)

    def test_shijiang_reply_panel_passes_without_standard_board(self):
        ok, errors = validate_response_board("侍讲官回奏\n\n这是解释。")

        self.assertTrue(ok)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
