import json
import subprocess
import sys
import unittest
from pathlib import Path

from hubu_arrival_hooks import recommend_hooks as recommend_hubu_hooks
from libu_arrival_hooks import render_qijulang_candidate, render_records_routing_candidate
from menxia_arrival_hooks import recommend_hooks as recommend_menxia_hooks
from sxlb_arrival_hooks import recommend_hooks, render_candidate
from xingbu_arrival_hooks import recommend_hooks as recommend_xingbu_hooks


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SXLB_ROOT / "scripts" / "sxlb_arrival_hooks.py"


class SxlbArrivalHooksTests(unittest.TestCase):
    def hook_names(self, data):
        return [hook["hook"] for hook in recommend_hooks(data)]

    def test_no_hooks_before_arrival_even_when_mechanical_signals_exist(self):
        hooks = self.hook_names(
            {
                "phase": "execution",
                "state": "六部执行",
                "task_class": "B",
                "office": "刑部",
                "file_edit": True,
                "canonical_changed": True,
                "human_facing_change": True,
                "external_sources_used": True,
                "conclusion_depends_on_external": True,
                "actual_touched_audit": "required",
            }
        )

        self.assertEqual(hooks, [])

    def test_router_only_indexes_department_owned_hooks(self):
        hooks = recommend_hooks(
            {
                "phase": "completion",
                "task_class": "B",
                "office": "刑部",
                "human_facing_change": True,
            }
        )

        self.assertEqual(
            {hook["owner_script"] for hook in hooks},
            {
                "menxia_arrival_hooks.py",
                "xingbu_arrival_hooks.py",
                "libu_arrival_hooks.py",
            },
        )
        self.assertTrue(all(hook["router_role"] == "index-only" for hook in hooks))

    def test_department_scripts_own_their_local_hooks(self):
        data = {"phase": "completion", "task_class": "B", "office": "刑部"}

        self.assertEqual([hook["hook"] for hook in recommend_menxia_hooks(data)], ["completion-precheck"])
        self.assertEqual([hook["hook"] for hook in recommend_xingbu_hooks(data)], ["verification-snippet"])
        self.assertEqual([hook["hook"] for hook in recommend_hubu_hooks(data)], [])

    def test_verification_hook_is_completion_arrival_only(self):
        self.assertIn(
            "completion-precheck",
            self.hook_names({"phase": "completion", "task_class": "B"}),
        )
        self.assertIn(
            "verification-snippet",
            self.hook_names({"phase": "completion", "task_class": "B", "office": "刑部"}),
        )
        self.assertNotIn(
            "verification-snippet",
            self.hook_names({"phase": "execution", "task_class": "B", "office": "刑部"}),
        )
        self.assertNotIn(
            "completion-precheck",
            self.hook_names({"phase": "execution", "task_class": "B"}),
        )

    def test_records_routing_is_only_for_required_completion_packages(self):
        self.assertIn(
            "records-routing-candidate",
            self.hook_names({"phase": "completion", "task_class": "C"}),
        )
        self.assertNotIn(
            "records-routing-candidate",
            self.hook_names({"phase": "execution", "task_class": "C", "canonical_changed": True}),
        )

    def test_qijulang_candidate_is_attached_to_records_routing_not_standalone(self):
        self.assertIn(
            "qijulang-candidate",
            self.hook_names({"phase": "completion", "task_class": "B", "human_facing_change": True}),
        )
        self.assertNotIn(
            "qijulang-candidate",
            self.hook_names({"phase": "completion", "task_class": "A", "human_facing_change": True}),
        )

    def test_touched_files_hook_waits_for_return_or_completion_station(self):
        self.assertIn(
            "touched-files-evidence",
            self.hook_names(
                {
                    "phase": "subagent-return",
                    "file_edit": True,
                    "actual_touched_audit": "required",
                }
            ),
        )
        self.assertNotIn(
            "touched-files-evidence",
            self.hook_names(
                {
                    "phase": "execution",
                    "file_edit": True,
                    "actual_touched_audit": "required",
                }
            ),
        )

    def test_external_evidence_hook_requires_source_dependent_review_or_completion(self):
        self.assertIn(
            "external-evidence-package",
            self.hook_names(
                {
                    "phase": "review",
                    "external_sources_used": True,
                    "conclusion_depends_on_external": True,
                }
            ),
        )
        self.assertNotIn(
            "external-evidence-package",
            self.hook_names(
                {
                    "phase": "review",
                    "external_sources_used": True,
                    "conclusion_depends_on_external": False,
                }
            ),
        )

    def test_cli_reads_json_stdin(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            input=json.dumps(
                {
                    "phase": "completion",
                    "task_class": "B",
                    "office": "刑部",
                    "human_facing_change": True,
                },
                ensure_ascii=False,
            ),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["policy"], "arrival-only")
        self.assertIn("verification-snippet", [hook["hook"] for hook in payload["hooks"]])
        self.assertIn("records-routing-candidate", [hook["hook"] for hook in payload["hooks"]])

    def test_department_clis_emit_department_owned_json(self):
        cases = [
            ("menxia_arrival_hooks.py", {"phase": "completion"}, "门下省", "completion-precheck"),
            ("xingbu_arrival_hooks.py", {"phase": "completion", "task_class": "B", "office": "刑部"}, "刑部", "verification-snippet"),
            ("libu_arrival_hooks.py", {"phase": "completion", "task_class": "B"}, "礼部", "records-routing-candidate"),
            (
                "hubu_arrival_hooks.py",
                {"phase": "review", "external_sources_used": True, "conclusion_depends_on_external": True},
                "户部/门下省",
                "external-evidence-package",
            ),
        ]
        for script_name, payload, office, expected_hook in cases:
            with self.subTest(script=script_name):
                result = subprocess.run(
                    [sys.executable, str(SXLB_ROOT / "scripts" / script_name), "--json"],
                    input=json.dumps(payload, ensure_ascii=False),
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0)
                output = json.loads(result.stdout)
                self.assertEqual(output["policy"], "arrival-only")
                self.assertEqual(output["office"], office)
                self.assertIn(expected_hook, [hook["hook"] for hook in output["hooks"]])

    def test_render_records_routing_candidate_has_required_fields(self):
        text = render_records_routing_candidate(
            {
                "phase": "completion",
                "task_class": "B",
                "canonical_changed": True,
                "restart_changed": True,
            },
        )

        for field in ("canonical", "report-only", "restart-update", "no-writeback"):
            self.assertIn(f"- {field}：", text)

    def test_render_qijulang_candidate_requires_attached_hook(self):
        text = render_qijulang_candidate(
            {
                "phase": "completion",
                "task_class": "B",
                "human_facing_change": True,
                "target": "skill manual",
            },
        )

        self.assertIn("- 起居郎候补：yes", text)
        self.assertIn("attached to records-routing", text)

        with self.assertRaises(ValueError):
            render_qijulang_candidate(
                {"phase": "completion", "task_class": "A", "human_facing_change": True},
            )

    def test_render_external_evidence_candidate_has_source_boundary_fields(self):
        text = render_candidate(
            "external-evidence-package",
            {
                "phase": "review",
                "external_sources_used": True,
                "conclusion_depends_on_external": True,
                "question": "latest rule",
            },
        )

        for field in ("调研问题", "来源清单", "来源类型", "检查日期", "来源可靠性", "决策影响"):
            self.assertIn(f"- {field}：", text)


if __name__ == "__main__":
    unittest.main()
