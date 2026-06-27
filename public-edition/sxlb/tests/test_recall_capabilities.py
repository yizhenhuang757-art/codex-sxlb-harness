import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SXLB_ROOT / "scripts" / "recall_capabilities.py"
REGISTRY_PATH = SXLB_ROOT / "skills" / "family-trigger-index.json"
CLAN_REGISTRY_PATH = SXLB_ROOT / "skills" / "skill-clans.json"


def load_recall_module():
    spec = importlib.util.spec_from_file_location("recall_capabilities", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def documented_families() -> set[str]:
    text = (SXLB_ROOT / "skills" / "skill-families.md").read_text(encoding="utf-8")
    return set(re.findall(r"`(family:[^`]+)`", text))


def allowlisted_families() -> set[str]:
    text = (SXLB_ROOT / "skills" / "allowlist.md").read_text(encoding="utf-8")
    return set(re.findall(r"`(family:[^`]+)`", text))


class RecallCapabilitiesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_recall_module()
        self.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.clan_registry = json.loads(CLAN_REGISTRY_PATH.read_text(encoding="utf-8"))

    def families_in_registry(self) -> set[str]:
        return {entry["family"] for entry in self.registry["families"]}

    def recall_families(self, text: str, *, phase: str = "planning", office: str = "中书省") -> list[str]:
        result = self.module.recall_capabilities(text, phase=phase, office=office)
        return [candidate["family"] for candidate in result["candidates"]]

    def test_registry_families_exist_in_skill_families_doc(self) -> None:
        self.assertEqual(self.families_in_registry() - documented_families(), set())

    def test_registry_families_exist_in_allowlist(self) -> None:
        self.assertEqual(self.families_in_registry() - allowlisted_families(), set())

    def test_registry_families_have_clan_mapping(self) -> None:
        clans = self.clan_registry["clans"]
        self.assertLessEqual(len(clans), self.clan_registry["max_clans"])
        mapped: set[str] = set()
        for clan in clans:
            self.assertTrue(clan["clan"].startswith("clan:"))
            self.assertIn("does not grant execution authority", clan["boundary"])
            self.assertIn("use_when", clan)
            mapped.update(clan["families"])
        self.assertEqual(self.families_in_registry() - mapped, set())

    def test_registry_does_not_reference_concrete_plugin_skills(self) -> None:
        concrete_plugin_refs: list[str] = []
        for entry in self.registry["families"]:
            serialized = json.dumps(entry, ensure_ascii=False)
            for match in re.findall(r"\b[a-z][a-z0-9-]+:[a-z][a-z0-9-]+\b", serialized):
                if not match.startswith("family:"):
                    concrete_plugin_refs.append(match)

        self.assertEqual(concrete_plugin_refs, [])

    def test_sample_requests_recall_typical_families(self) -> None:
        samples = {
            "open localhost in a browser, click through the UI, and take a screenshot": "family:plugin/browser",
            "use my logged-in Chrome profile and an existing tab to upload a file": "family:plugin/chrome",
            "turn this product design mockup into a responsive prototype": "family:plugin/product-design",
            "triage my Outlook inbox and draft replies from the email thread": "family:plugin/outlook-email",
            "search Zotero for citation metadata and export BibTeX": "family:plugin/zotero",
            "score this TOEFL speaking response and update the study evidence": "family:toefl",
            "control a local Mac desktop app with no API through GUI clicks": "family:plugin/computer-use",
        }

        for text, expected in samples.items():
            with self.subTest(expected=expected):
                self.assertIn(expected, self.recall_families(text))

    def test_recall_returns_zero_to_three_candidates_with_required_fields(self) -> None:
        result = self.module.recall_capabilities(
            "Need UI prototype, browser screenshot, and logged-in Chrome upload",
            phase="dispatch",
            office="尚书省",
        )

        self.assertGreaterEqual(len(result["clan_candidates"]), 1)
        self.assertLessEqual(len(result["clan_candidates"]), 2)
        self.assertGreaterEqual(len(result["family_candidates"]), 1)
        self.assertLessEqual(len(result["family_candidates"]), 3)
        selected_clans = {candidate["clan"] for candidate in result["clan_candidates"]}
        for candidate in result["clan_candidates"]:
            for field in ("clan", "title", "confidence", "reason", "recall_owner", "execution_boundary", "families"):
                self.assertIn(field, candidate)
            self.assertTrue(candidate["clan"].startswith("clan:"))
            self.assertIn("family-bound", candidate["execution_boundary"])
        for candidate in result["family_candidates"]:
            for field in ("family", "clan", "confidence", "reason", "recall_owner", "execution_owner", "boundary"):
                self.assertIn(field, candidate)
            self.assertTrue(candidate["family"].startswith("family:"))
            self.assertTrue(candidate["clan"].startswith("clan:"))
            self.assertIn(candidate["clan"], selected_clans)
        self.assertEqual(result["candidates"], result["family_candidates"])
        self.assertIn("clan recall is context only", result["policy"]["authority"])

    def test_semantic_keywords_bridge_implicit_request_to_registry_triggers(self) -> None:
        implicit_text = "帮我看看这个界面有没有明显问题"
        without_bridge = self.module.recall_capabilities(implicit_text, phase="planning", office="中书省")
        with_bridge = self.module.recall_capabilities(
            implicit_text,
            phase="planning",
            office="中书省",
            semantic_keywords=["ui", "browser", "screenshot", "visual smoke"],
        )

        self.assertNotIn("family:plugin/browser", [candidate["family"] for candidate in without_bridge["family_candidates"]])
        families = [candidate["family"] for candidate in with_bridge["family_candidates"]]
        self.assertIn("family:plugin/browser", families)
        browser = [candidate for candidate in with_bridge["family_candidates"] if candidate["family"] == "family:plugin/browser"][0]
        self.assertIn("clan:browser-automation-dev", [candidate["clan"] for candidate in with_bridge["clan_candidates"]])
        self.assertIn("semantic_keywords=ui, browser, screenshot, visual smoke", browser["reason"])
        self.assertEqual(with_bridge["input"]["semantic_keywords"], ["ui", "browser", "screenshot", "visual smoke"])

    def test_semantic_keywords_select_clan_before_family_matching(self) -> None:
        result = self.module.recall_capabilities(
            "帮我判断该走哪套机制",
            phase="planning",
            office="中书省",
            semantic_keywords=["governance"],
        )

        self.assertIn("clan:governance-process", [candidate["clan"] for candidate in result["clan_candidates"]])
        self.assertGreaterEqual(len(result["family_candidates"]), 1)
        self.assertTrue(
            all(candidate["clan"] == "clan:governance-process" for candidate in result["family_candidates"]),
            result["family_candidates"],
        )
        governance_clan = result["clan_candidates"][0]
        self.assertIn("matched clan signals", governance_clan["reason"])

    def test_recall_expands_selected_families_to_concrete_skill_candidates(self) -> None:
        result = self.module.recall_capabilities(
            "sxlb，检查一下你调用 skill 的机制",
            phase="planning",
            office="中书省",
            semantic_keywords=["skill", "governance", "sxlb"],
        )

        self.assertIn("skill_candidates", result)
        self.assertGreaterEqual(len(result["skill_candidates"]), 1)
        selected_families = {candidate["family"] for candidate in result["family_candidates"]}
        skill_families = {candidate["family"] for candidate in result["skill_candidates"]}
        self.assertTrue(skill_families <= selected_families)
        skill_names = {candidate["skill"] for candidate in result["skill_candidates"]}
        self.assertIn("sxlb", skill_names)
        for candidate in result["skill_candidates"]:
            for field in ("skill", "family", "clan", "path", "lifecycle", "reason", "activation"):
                self.assertIn(field, candidate)
            self.assertEqual(candidate["activation"], "candidate-only")

    def test_recall_returns_phase_scoped_skill_bundles(self) -> None:
        result = self.module.recall_capabilities(
            "Build a responsive product prototype, verify it in the browser, then prepare handoff notes",
            phase="dispatch",
            office="尚书省",
            semantic_keywords=["product design", "frontend", "browser", "documentation"],
        )

        self.assertIn("skill_bundles", result)
        self.assertGreaterEqual(len(result["skill_bundles"]), 1)
        for bundle in result["skill_bundles"]:
            for field in ("phase", "clan", "family", "execution_owner", "candidate_skills", "boundary", "exit_rule"):
                self.assertIn(field, bundle)
            self.assertEqual(bundle["phase"], "dispatch")
            self.assertLessEqual(len(bundle["candidate_skills"]), result["input"]["skill_limit"])
            self.assertIn("Load concrete SKILL.md only when the current phase needs it", bundle["exit_rule"])

    def test_skill_onboarding_request_prioritizes_skill_onboarding_candidate(self) -> None:
        result = self.module.recall_capabilities(
            "安装一个 new skill 后请跑 skill onboarding",
            phase="dispatch",
            office="尚书省",
            semantic_keywords=["skill onboarding", "new skill", "installed skill"],
        )

        self.assertIn("clan:governance-process", [candidate["clan"] for candidate in result["clan_candidates"]])
        self.assertIn("family:skill-governance", [candidate["family"] for candidate in result["family_candidates"]])
        governance_bundle = [
            bundle for bundle in result["skill_bundles"] if bundle["family"] == "family:skill-governance"
        ][0]
        self.assertIn("skill-onboarding", governance_bundle["candidate_skills"])

    def test_cli_reads_stdin_and_outputs_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--phase",
                "intake",
                "--office",
                "太子",
                "--semantic-keyword",
                "toefl",
                "--json",
            ],
            input="帮我看看这道题",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertIn("clan:learning-research", [candidate["clan"] for candidate in payload["clan_candidates"]])
        self.assertIn("family:toefl", [candidate["family"] for candidate in payload["family_candidates"]])
        self.assertEqual(payload["input"]["semantic_keywords"], ["toefl"])


if __name__ == "__main__":
    unittest.main()
