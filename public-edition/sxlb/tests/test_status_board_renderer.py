import unittest

from status_board import (
    INTERVENTIONS,
    render_board,
    select_variant,
    validate_board_text,
)


class StatusBoardRendererTests(unittest.TestCase):
    def test_selects_stage_specific_compact_variants_from_state(self):
        cases = {
            "待立案": "taizi",
            "中书拟制": "zhongshu",
            "门下审议": "menxia",
            "门下复核": "menxia",
            "尚书派发": "shangshu",
            "六部执行": "default",
        }

        for state, expected in cases.items():
            with self.subTest(state=state):
                self.assertEqual(select_variant(state), expected)

    def test_selects_full_for_boundary_events_and_risks(self):
        self.assertEqual(select_variant("退朝清算"), "full")
        self.assertEqual(select_variant("中书拟制", event="formal-plan"), "full")
        self.assertEqual(select_variant("六部执行", risk=True), "full")
        self.assertEqual(select_variant("六部执行", blocked=True), "full")
        self.assertEqual(select_variant("尚书派发", real_subagent=True), "full")

    def test_rendered_compact_board_has_fixed_interventions(self):
        board = render_board(
            {
                "task": "脚本化面板",
                "state": "六部执行",
                "runtime": "active",
                "route": "太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部",
                "case_status": "案卷 case/path",
                "case": "case/path",
                "caifeng": "n/a",
                "pending": "none",
            }
        )

        self.assertTrue(board.startswith("朝堂状态\n"))
        self.assertIn("案卷状态：案卷 case/path", board)
        for command in INTERVENTIONS:
            self.assertIn(f"`{command}`", board)

    def test_rendered_zhongshu_variant_has_required_fields(self):
        board = render_board(
            {
                "task": "脚本化面板",
                "state": "中书拟制",
                "runtime": "active",
                "plan": "草拟中",
                "decision_tree": "open",
                "case_status": "无",
                "caifeng": "n/a",
                "pending": "none",
            }
        )

        for label in ("任务：", "中书：", "方案：", "决策树：", "案卷状态：", "采风：", "产物：", "待决：", "干预："):
            self.assertIn(label, board)
        self.assertNotIn("## 当前链路", board)

    def test_validate_rejects_missing_required_compact_fields(self):
        ok, errors = validate_board_text(
            """朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none

## 回奏

正文。""",
            variant="default",
        )

        self.assertFalse(ok)
        self.assertIn("missing required board field: 干预", errors)

    def test_validate_rejects_missing_fixed_intervention(self):
        ok, errors = validate_board_text(
            """朝堂状态
任务：脚本化面板
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `退朝`

## 回奏

正文。""",
            variant="default",
        )

        self.assertFalse(ok)
        self.assertIn("missing intervention command: 起居郎", errors)

    def test_validate_rejects_unknown_court_office_field(self):
        ok, errors = validate_board_text(
            """朝堂状态
任务：脚本化面板
枢密院：接续已接受计划，从现有改动往前推进。
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 工部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 回奏

正文。""",
            variant="default",
        )

        self.assertFalse(ok)
        self.assertIn("unknown status board field: 枢密院", errors)

    def test_validate_distinguishes_canonical_office_from_unknown_field(self):
        ok, errors = validate_board_text(
            """朝堂状态
任务：脚本化面板
工部：先修当前 RED 的编辑器单 occurrence 问题。
状态：六部执行 / active
链路：太子 -> 中书省 -> 门下省 -> 尚书省 -> 工部
案卷状态：案卷 case/path
采风：n/a
待决：none
干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`

## 回奏

正文。""",
            variant="default",
        )

        self.assertFalse(ok)
        self.assertIn("non-template status board field: 工部", errors)
        self.assertNotIn("unknown status board field: 工部", errors)

    def test_case_status_defaults_to_short_case_name_and_hooks(self):
        board = render_board(
            {
                "task": "脚本化面板",
                "state": "六部执行",
                "runtime": "active",
                "route": "太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部",
                "case": "$SXLB_CASE_ROOT/example-case",
                "hooks": ["起居郎", "国史馆"],
                "caifeng": "n/a",
                "pending": "none",
            }
        )

        self.assertIn("案卷状态：案卷 example-case；钩子 起居郎,国史馆", board)

    def test_menxia_status_shows_review_outcomes(self):
        cases = [
            ({"state": "门下审议", "runtime": "active", "verdict": "待审", "target": "方案"}, "门下：审议中"),
            ({"state": "门下审议", "runtime": "done", "verdict": "通过", "target": "方案"}, "门下：通过"),
            ({"state": "门下审议", "runtime": "blocked", "verdict": "封驳", "target": "派令"}, "门下：封驳"),
            ({"state": "门下审议", "runtime": "review", "verdict": "补证后再审", "target": "证据包"}, "门下：补证"),
            ({"state": "门下复核", "runtime": "done", "verdict": "通过", "target": "完成包"}, "门下：复核通过"),
            ({"state": "门下复核", "runtime": "blocked", "verdict": "封驳", "target": "完成包"}, "门下：复核封驳"),
            ({"state": "门下复核", "runtime": "review", "verdict": "补证后再审", "target": "完成包"}, "门下：复核补证"),
        ]

        for data, expected in cases:
            with self.subTest(expected=expected):
                board = render_board({"task": "门下状态", "case_status": "无", "pending": "none", **data})
                self.assertIn(expected, board)

    def test_menxia_status_can_be_explicit_count(self):
        board = render_board(
            {
                "task": "门下状态",
                "state": "门下复核",
                "menxia_status": "done×2",
                "target": "完成包",
                "verdict": "通过",
                "case_status": "无",
                "pending": "none",
            }
        )

        self.assertIn("门下：done×2", board)


if __name__ == "__main__":
    unittest.main()
