from pathlib import Path
import unittest


SXLB_ROOT = Path(__file__).resolve().parents[1]


class StatusBoardTemplateTests(unittest.TestCase):
    def test_status_board_lists_shijiang_officer_command(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")

        self.assertIn("`侍讲官 <问题>`", template)
        self.assertIn("templates/status-board.md", mode)

    def test_status_board_lists_event_ledger_command(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        status_machine = (SXLB_ROOT / "protocols" / "status-machine.md").read_text(encoding="utf-8")

        self.assertIn("`事件簿`", template)
        self.assertIn("templates/status-board.md", mode)
        self.assertIn("`事件簿`", status_machine)

    def test_status_board_defaults_to_compact_with_caifeng_line(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")

        self.assertIn("默认显示紧凑版", template)
        self.assertIn("默认显示紧凑版", mode)
        self.assertIn("采风：<n/a|待采证|采证中|证据包待审|已入方案>", template)
        self.assertIn("干预：`继续` `暂停` `会审` `重审` `录案` `事件簿` `侍讲官 <问题>` `国史馆` `翰林院` `起居郎` `退朝`", template)
        self.assertNotIn("`改派`", template)

    def test_status_board_lists_specialist_intervention_commands_without_hints(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")

        self.assertNotIn("提示：", template)
        for command in ("`国史馆`", "`翰林院`", "`起居郎`"):
            self.assertIn(command, template)

    def test_six_hats_only_appears_in_deliberation_hint(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        status_machine = (SXLB_ROOT / "protocols" / "status-machine.md").read_text(encoding="utf-8")

        compact_section = template.split("## 太子面板", 1)[0]
        self.assertNotIn("六帽", compact_section)
        self.assertIn("会审干预：`六帽`", template)
        self.assertIn("`六帽`", mode)
        self.assertIn("`六帽`", status_machine)

    def test_status_board_documents_full_board_triggers(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")

        for trigger in ("首次进入", "正式方案", "正式审议", "正式派发", "真实 subagent", "退朝清算"):
            self.assertIn(trigger, template)
        self.assertIn("formal plan/review/dispatch", mode)
        self.assertIn("退朝清算", mode)

    def test_status_board_has_stage_specific_compact_panels(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")

        for panel in ("太子面板", "中书面板", "门下面板", "尚书面板"):
            self.assertIn(f"## {panel}", template)
            self.assertIn(panel, mode)

        self.assertIn("scripts/status_board.py", template)
        self.assertIn("scripts/status_board.py", mode)
        self.assertIn("六部执行使用默认紧凑版", template)
        self.assertIn("六部执行使用默认紧凑版", mode)

    def test_mode_requires_reply_generator_for_substantive_replies(self):
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        script_index = (SXLB_ROOT / "protocols" / "script-index.md").read_text(encoding="utf-8")

        self.assertIn("Before composing any ordinary substantive `sxlb` reply, call `scripts/sxlb_reply.py`", mode)
        self.assertIn("Do not hand-roll `朝堂状态` field order or intervention lists", mode)
        self.assertIn("If the script cannot be run, state that explicitly in `回奏`", mode)
        self.assertIn("Reply Generation Hard Gate", script_index)

    def test_mode_requires_state_body_packet_as_single_reply_outlet(self):
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        script_index = (SXLB_ROOT / "protocols" / "script-index.md").read_text(encoding="utf-8")

        for text in (mode, script_index):
            self.assertIn("state/body packet", text)
            self.assertIn("single generated-reply outlet", text)
            self.assertIn("do not draft `朝堂状态` directly", text)

    def test_mode_bars_uncanonical_court_offices(self):
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")

        for text in (mode, template):
            self.assertIn("Do not introduce unlisted historical court offices", text)
            self.assertIn("unknown office-like fields fail board validation", text)

    def test_mode_binds_low_token_events_without_board_bloat(self):
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")
        script_index = (SXLB_ROOT / "protocols" / "script-index.md").read_text(encoding="utf-8")
        harness = (SXLB_ROOT / "protocols" / "harness.md").read_text(encoding="utf-8")

        self.assertIn("explicit low-token event packets", mode)
        self.assertIn("before entering the next station", mode)
        self.assertIn("exactly when an office declares readiness", mode)
        self.assertIn("must not read private reasoning", mode)
        self.assertIn("sxlb_event_router.py", script_index)
        self.assertIn("zhongshu.plan_ready", script_index)
        self.assertIn("--check-plan-ready", script_index)
        self.assertIn("not visible board content", script_index)
        self.assertIn("sidecar trigger", harness)

    def test_status_board_cannot_be_the_only_record_source(self):
        template = (SXLB_ROOT / "templates" / "status-board.md").read_text(encoding="utf-8")
        mode = (SXLB_ROOT / "MODE.md").read_text(encoding="utf-8")

        self.assertIn("面板不得作为唯一记录源", template)
        self.assertIn("面板不得作为唯一记录源", mode)
        for artifact in ("case.md", "zhongshu-plan.md", "menxia-review.md", "dispatch-order.md"):
            self.assertIn(artifact, template)


if __name__ == "__main__":
    unittest.main()
