import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SXLB_ROOT / "scripts" / "skill_inventory.py"


def load_inventory_module():
    spec = importlib.util.spec_from_file_location("skill_inventory", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillInventoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = load_inventory_module()
        self.records = self.inventory.collect_records()

    def test_generated_inventory_is_current(self) -> None:
        generated = (SXLB_ROOT / "skills" / "skill-inventory.generated.md").read_text(encoding="utf-8")
        self.assertEqual(generated, self.inventory.render(self.records))

    def test_plugin_cache_skills_are_active_via_family(self) -> None:
        plugin_records = [record for record in self.records if record.source == "plugin-cache"]
        self.assertEqual(len(plugin_records), self.inventory.plugin_skill_count())
        self.assertTrue(all(record.lifecycle == "active-via-family" for record in plugin_records))
        self.assertIn("plugin/product-design", {record.family for record in plugin_records})
        self.assertIn("product-design:url-to-code", {record.skill_id for record in plugin_records})
        self.assertIn("plugin/computer-use", {record.family for record in plugin_records})
        self.assertIn("computer-use:computer-use", {record.skill_id for record in plugin_records})
        self.assertIn("plugin/pdf", {record.family for record in plugin_records})
        self.assertIn("pdf:pdf", {record.skill_id for record in plugin_records})
        computer_use = [record for record in plugin_records if record.skill_id == "computer-use:computer-use"][0]
        self.assertEqual(computer_use.offices, "兵部 / 刑部 / 门下省")

    def test_agent_reach_routes_through_automation_integration(self) -> None:
        records_by_id = {record.skill_id: record for record in self.records}

        self.assertEqual(records_by_id["agent-reach"].family, "automation-integration")
        self.assertEqual(records_by_id["agent-reach"].offices, "兵部")

    def test_public_inventory_exposes_host_workflow_skill_interfaces(self) -> None:
        records_by_id = {record.skill_id: record for record in self.records}

        self.assertEqual(records_by_id["best-minds"].source, "optional-interface")
        expected_superpowers = {
            "superpowers:brainstorming",
            "superpowers:dispatching-parallel-agents",
            "superpowers:executing-plans",
            "superpowers:finishing-a-development-branch",
            "superpowers:receiving-code-review",
            "superpowers:requesting-code-review",
            "superpowers:subagent-driven-development",
            "superpowers:systematic-debugging",
            "superpowers:test-driven-development",
            "superpowers:using-git-worktrees",
            "superpowers:using-superpowers",
            "superpowers:verification-before-completion",
            "superpowers:writing-plans",
            "superpowers:writing-skills",
        }
        self.assertLessEqual(expected_superpowers, set(records_by_id))
        for skill_id in expected_superpowers:
            record = records_by_id[skill_id]
            self.assertEqual(record.family, "superpowers")
            self.assertEqual(record.source, "optional-interface")
            self.assertEqual(record.offices, "host / 三省")
            self.assertIn("$CODEX_SUPERPOWERS_HOME", str(record.path))
            self.assertIn("not bundled", record.note)

    def test_public_inventory_uses_placeholders_not_personal_paths(self) -> None:
        rendered = self.inventory.render(self.records)
        self.assertNotIn("/Users/", rendered)
        self.assertIn("$CODEX_SKILLS_HOME", rendered)
        self.assertIn("$CODEX_PLUGIN_CACHE", rendered)

    def test_allowlist_uses_families_not_plugin_cache_flattening(self) -> None:
        allowlist = (SXLB_ROOT / "skills" / "allowlist.md").read_text(encoding="utf-8")
        self.assertIn("family:plugin/product-design", allowlist)
        self.assertIn("family:plugin/codex-security", allowlist)
        self.assertIn("family:plugin/computer-use", allowlist)
        self.assertNotIn("product-design:get-context", allowlist)
        self.assertNotIn("codex-security:deep-security-scan", allowlist)
        self.assertNotIn("computer-use:computer-use", allowlist)

    def test_inventory_exposes_sxlb_office_positioning(self) -> None:
        generated = (SXLB_ROOT / "skills" / "skill-inventory.generated.md").read_text(encoding="utf-8")
        self.assertIn("| lifecycle | family | sxlb offices | skill | source | path | note |", generated)
        self.assertIn("| active-via-family | plugin/computer-use | 兵部 / 刑部 / 门下省 | `computer-use:computer-use`", generated)

    def test_inventory_families_are_documented_and_allowlisted(self) -> None:
        inventory_families = {record.family for record in self.records}
        family_text = (SXLB_ROOT / "skills" / "skill-families.md").read_text(encoding="utf-8")
        allowlist_text = (SXLB_ROOT / "skills" / "allowlist.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"`family:([^`]+)`", family_text))
        allowlisted = set(re.findall(r"`family:([^`]+)`", allowlist_text))

        self.assertEqual(inventory_families - documented, set())
        self.assertEqual(inventory_families - allowlisted, set())

    def test_inventory_families_have_clan_overlay(self) -> None:
        inventory_families = {f"family:{record.family}" for record in self.records}
        payload = json.loads((SXLB_ROOT / "skills" / "skill-clans.json").read_text(encoding="utf-8"))
        self.assertLessEqual(len(payload["clans"]), payload["max_clans"])
        mapped: set[str] = set()
        for clan in payload["clans"]:
            self.assertTrue(clan["clan"].startswith("clan:"))
            self.assertIn("does not grant execution authority", clan["boundary"])
            mapped.update(clan["families"])
        self.assertEqual(inventory_families - mapped, set())

    def test_research_tools_route_through_reading_research_family(self) -> None:
        records_by_id = {record.skill_id: record for record in self.records}
        self.assertEqual(records_by_id["notebooklm"].family, "reading-research")
        self.assertEqual(records_by_id["zotero-chapter-workbench"].family, "reading-research")


if __name__ == "__main__":
    unittest.main()
