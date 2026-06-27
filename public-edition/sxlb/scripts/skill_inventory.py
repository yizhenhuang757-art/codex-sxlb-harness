#!/usr/bin/env python3
"""Generate an audit inventory for local Codex skills.

The inventory is an evidence surface, not the daily routing surface. It records
concrete SKILL.md files and classifies nested vendor copies separately from
active skills so capability governance can stay family-level.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path


HOME = Path(os.environ.get("SXLB_PRIVATE_HOME", str(Path.home())))
SXLB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SXLB_ROOT / "skills" / "skill-inventory.generated.md"

AGENTS_SKILLS = HOME / ".agents" / "skills"
CODEX_SKILLS = HOME / ".codex" / "skills"
SUPERPOWERS_SKILLS = HOME / ".codex" / "superpowers" / "skills"
PLUGIN_CACHE = HOME / ".codex" / "plugins" / "cache"

PLUGIN_NAMESPACE_OVERRIDES = {
    "documents": "documents:documents",
    "presentations": "presentations:Presentations",
    "spreadsheets": "spreadsheets:Spreadsheets",
    "zotero": "zotero:Zotero",
}

PLUGIN_FAMILIES = {
    "browser",
    "canva",
    "chrome",
    "computer-use",
    "codex-security",
    "creative-production",
    "documents",
    "figma",
    "github",
    "outlook-email",
    "pdf",
    "presentations",
    "product-design",
    "spreadsheets",
    "zotero",
}

PREFIX_FAMILIES = (
    ("communication-", "communication"),
    ("gpt-record-", "gpt-record"),
    ("toefl-", "toefl"),
    ("wiki-", "wiki"),
)

NAMED_FAMILIES = {
    "best-minds": "reasoning-research",
    "chrome-devtools": "automation-integration",
    "csv-data-summarizer": "documents-media-data",
    "daily-review": "daily-planning",
    "defuddle": "obsidian",
    "docx": "documents-media-data",
    "docx-to-obsidian-md": "documents-media-data",
    "agent-reach": "automation-integration",
    "file-organizer": "automation-integration",
    "find-skills": "skill-governance",
    "frontend-design": "design-frontend",
    "guoshiguan-recall": "sxlb-governance",
    "humanizer-zh": "writing-polish",
    "imagegen": "creative-media",
    "internal-wiki-sync": "wiki",
    "json-canvas": "obsidian",
    "memory-gateway": "sxlb-governance",
    "mineru-ocr": "documents-media-data",
    "nano-pdf": "documents-media-data",
    "notebooklm": "reading-research",
    "object-scheduling": "daily-planning",
    "obsidian-bases": "obsidian",
    "obsidian-cli": "obsidian",
    "obsidian-markdown": "obsidian",
    "ontology": "reference-experimental",
    "openai-docs": "system",
    "pdf": "documents-media-data",
    "planning-with-files": "sxlb-governance",
    "plugin-creator": "skill-governance",
    "pptx": "documents-media-data",
    "quarkdown-export": "publishing-export",
    "reading-lab-knowledge-object": "reading-research",
    "reading-thinking-sync": "reading-research",
    "self-improving-agent": "skill-governance",
    "skill-creator": "skill-governance",
    "skill-installer": "skill-governance",
    "skill-onboarding": "skill-governance",
    "skills-index-sync": "skill-governance",
    "skills-manual-writer": "skill-governance",
    "spreadsheet": "documents-media-data",
    "sxlb": "sxlb-governance",
    "sxlb-agent-dispatch-check": "sxlb-governance",
    "ticktick-analytics": "daily-planning",
    "today-to-do": "daily-planning",
    "use-spark": "automation-integration",
    "weekly-review": "daily-planning",
    "wiki-calibration": "wiki",
    "workflow-orchestration-patterns": "automation-integration",
    "writing-sentence-building": "toefl",
    "zotero-chapter-workbench": "reading-research",
}

FAMILY_OFFICES = {
    "automation-integration": "兵部",
    "communication": "礼部 / 户部",
    "creative-media": "礼部",
    "daily-planning": "太子 / 户部",
    "design-frontend": "礼部 / 工部",
    "documents-media-data": "礼部 / 户部",
    "gpt-record": "礼部",
    "obsidian": "礼部 / 户部",
    "other": "吏部",
    "plugin/browser": "工部 / 刑部",
    "plugin/canva": "礼部",
    "plugin/chrome": "兵部",
    "plugin/codex-security": "刑部",
    "plugin/computer-use": "兵部 / 刑部 / 门下省",
    "plugin/creative-production": "礼部",
    "plugin/documents": "礼部",
    "plugin/figma": "礼部",
    "plugin/github": "兵部",
    "plugin/outlook-email": "兵部 / 礼部",
    "plugin/pdf": "礼部 / 户部",
    "plugin/presentations": "礼部",
    "plugin/product-design": "礼部 / 工部",
    "plugin/spreadsheets": "户部",
    "plugin/zotero": "户部",
    "publishing-export": "礼部",
    "reading-research": "户部",
    "reasoning-research": "中书省",
    "reference-experimental": "吏部",
    "skill-governance": "吏部",
    "superpowers": "host / 三省",
    "sxlb-governance": "吏部 / 太子",
    "system": "host",
    "toefl": "礼部 / 户部",
    "wiki": "礼部 / 吏部",
    "writing-polish": "礼部",
}


@dataclass(frozen=True)
class SkillRecord:
    skill_id: str
    family: str
    offices: str
    lifecycle: str
    source: str
    path: Path
    note: str


PUBLIC_RECORDS = (
    ("sxlb", "sxlb-governance", "吏部 / 太子", "active", "public-bundle", "$CODEX_SKILLS_HOME/sxlb/SKILL.md", "public bundled harness skill"),
    ("sxlb-agent-dispatch-check", "sxlb-governance", "吏部 / 太子", "active", "public-bundle", "$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check/SKILL.md", "optional companion dispatch gate"),
    ("planning-with-files", "sxlb-governance", "吏部 / 太子", "active", "optional-interface", "$CODEX_SKILLS_HOME/planning-with-files/SKILL.md", "optional interface; private implementations are not bundled"),
    ("memory-gateway", "sxlb-governance", "吏部 / 太子", "active", "optional-interface", "$CODEX_SKILLS_HOME/memory-gateway/SKILL.md", "optional interface; private memory stores are not bundled"),
    ("guoshiguan-recall", "sxlb-governance", "吏部 / 太子", "active", "optional-interface", "$CODEX_SKILLS_HOME/guoshiguan-recall/SKILL.md", "optional interface; private case history is not bundled"),
    ("find-skills", "skill-governance", "吏部", "active", "optional-interface", "$CODEX_SKILLS_HOME/find-skills/SKILL.md", "optional skill discovery interface"),
    ("plugin-creator", "skill-governance", "吏部", "active", "optional-interface", "$CODEX_SKILLS_HOME/plugin-creator/SKILL.md", "optional plugin creation interface"),
    ("skill-onboarding", "skill-governance", "吏部", "active", "optional-interface", "$CODEX_SKILLS_HOME/skill-onboarding/SKILL.md", "optional new-skill onboarding interface"),
    ("self-improving-agent", "skill-governance", "吏部", "active", "optional-interface", "$CODEX_SKILLS_HOME/self-improving-agent/SKILL.md", "optional retrospection interface"),
    ("agent-reach", "automation-integration", "兵部", "active", "optional-interface", "$CODEX_SKILLS_HOME/agent-reach/SKILL.md", "optional public research and platform routing interface"),
    ("workflow-orchestration-patterns", "automation-integration", "兵部", "active", "optional-interface", "$CODEX_SKILLS_HOME/workflow-orchestration-patterns/SKILL.md", "optional workflow design interface"),
    ("notebooklm", "reading-research", "户部", "active", "optional-interface", "$CODEX_SKILLS_HOME/notebooklm/SKILL.md", "optional research interface"),
    ("zotero-chapter-workbench", "reading-research", "户部", "active", "optional-interface", "$CODEX_SKILLS_HOME/zotero-chapter-workbench/SKILL.md", "optional citation workflow interface"),
    ("best-minds", "reasoning-research", "中书省", "active", "optional-interface", "$CODEX_SKILLS_HOME/best-minds/SKILL.md", "optional expert-framing interface"),
    ("superpowers:brainstorming", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/brainstorming/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:dispatching-parallel-agents", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/dispatching-parallel-agents/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:executing-plans", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/executing-plans/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:finishing-a-development-branch", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/finishing-a-development-branch/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:receiving-code-review", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/receiving-code-review/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:requesting-code-review", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/requesting-code-review/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:subagent-driven-development", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/subagent-driven-development/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:systematic-debugging", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/systematic-debugging/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:test-driven-development", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/test-driven-development/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:using-git-worktrees", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/using-git-worktrees/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:using-superpowers", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/using-superpowers/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:verification-before-completion", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/verification-before-completion/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:writing-plans", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/writing-plans/SKILL.md", "optional host workflow skill; not bundled"),
    ("superpowers:writing-skills", "superpowers", "host / 三省", "active", "optional-interface", "$CODEX_SUPERPOWERS_HOME/writing-skills/SKILL.md", "optional host workflow skill; not bundled"),
    ("frontend-design", "design-frontend", "礼部 / 工部", "active", "optional-interface", "$CODEX_SKILLS_HOME/frontend-design/SKILL.md", "optional frontend design interface"),
    ("docx", "documents-media-data", "礼部 / 户部", "active", "optional-interface", "$CODEX_SKILLS_HOME/docx/SKILL.md", "optional document artifact interface"),
    ("humanizer-zh", "writing-polish", "礼部", "active", "optional-interface", "$CODEX_SKILLS_HOME/humanizer-zh/SKILL.md", "optional writing polish interface"),
    ("toefl-reading-review", "toefl", "礼部 / 户部", "active", "optional-interface", "$CODEX_SKILLS_HOME/toefl-reading-review/SKILL.md", "optional learning workflow interface"),
    ("browser:control-in-app-browser", "plugin/browser", "工部 / 刑部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/browser/skills/control-in-app-browser/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("chrome:control-chrome", "plugin/chrome", "兵部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/chrome/skills/control-chrome/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("computer-use:computer-use", "plugin/computer-use", "兵部 / 刑部 / 门下省", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/computer-use/skills/computer-use/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("codex-security:security-scan", "plugin/codex-security", "刑部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/codex-security/skills/security-scan/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("codex-security:deep-security-scan", "plugin/codex-security", "刑部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/codex-security/skills/deep-security-scan/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("figma:figma-use", "plugin/figma", "礼部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/figma/skills/figma-use/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("figma:figma-generate-diagram", "plugin/figma", "礼部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/figma/skills/figma-generate-diagram/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("product-design:get-context", "plugin/product-design", "礼部 / 工部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/product-design/skills/get-context/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("product-design:image-to-code", "plugin/product-design", "礼部 / 工部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/product-design/skills/image-to-code/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("product-design:url-to-code", "plugin/product-design", "礼部 / 工部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/product-design/skills/url-to-code/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("product-design:prototype", "plugin/product-design", "礼部 / 工部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/product-design/skills/prototype/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("product-design:design-qa", "plugin/product-design", "礼部 / 工部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/product-design/skills/design-qa/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("presentations:Presentations", "plugin/presentations", "礼部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/presentations/skills/presentations/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("spreadsheets:Spreadsheets", "plugin/spreadsheets", "户部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/spreadsheets/skills/spreadsheets/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("outlook-email:outlook-email", "plugin/outlook-email", "兵部 / 礼部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/outlook-email/skills/outlook-email/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("zotero:Zotero", "plugin/zotero", "户部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/zotero/skills/zotero/SKILL.md", "concrete plugin skill; route through plugin family"),
    ("pdf:pdf", "plugin/pdf", "礼部 / 户部", "active-via-family", "plugin-cache", "$CODEX_PLUGIN_CACHE/pdf/skills/pdf/SKILL.md", "concrete plugin skill; route through plugin family"),
)


def parse_frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"')
    return None


def plugin_name_for(path: Path) -> str | None:
    try:
        parts = path.parts
        index = parts.index("cache")
        return parts[index + 2]
    except (ValueError, IndexError):
        return None


def plugin_skill_id(path: Path) -> str:
    plugin = plugin_name_for(path) or "plugin"
    if plugin in PLUGIN_NAMESPACE_OVERRIDES:
        return PLUGIN_NAMESPACE_OVERRIDES[plugin]
    return f"{plugin}:{path.parent.name}"


def is_nested_vendor(path: Path) -> bool:
    canonical = AGENTS_SKILLS / "planning-with-files" / "SKILL.md"
    return path.is_relative_to(AGENTS_SKILLS / "planning-with-files") and path != canonical


def family_for_name(name: str) -> str:
    for prefix, family in PREFIX_FAMILIES:
        if name.startswith(prefix):
            return family
    return NAMED_FAMILIES.get(name, "other")


def classify(path: Path) -> SkillRecord:
    if path.is_relative_to(PLUGIN_CACHE):
        plugin = plugin_name_for(path) or "plugin"
        family = f"plugin/{plugin}"
        return SkillRecord(
            skill_id=plugin_skill_id(path),
            family=family,
            offices=FAMILY_OFFICES.get(family, "吏部"),
            lifecycle="active-via-family",
            source="plugin-cache",
            path=path,
            note="concrete plugin skill; route through plugin family",
        )

    raw_name = parse_frontmatter_name(path) or path.parent.name
    name = raw_name.strip().strip('"')

    if path.is_relative_to(SUPERPOWERS_SKILLS):
        return SkillRecord(
            skill_id=f"superpowers:{name}",
            family="superpowers",
            offices=FAMILY_OFFICES["superpowers"],
            lifecycle="active",
            source="superpowers",
            path=path,
            note="host workflow skill",
        )

    if is_nested_vendor(path):
        return SkillRecord(
            skill_id=name,
            family="sxlb-governance",
            offices=FAMILY_OFFICES["sxlb-governance"],
            lifecycle="reference-only",
            source="nested-vendor",
            path=path,
            note="nested platform copy; excluded from active skill counts",
        )

    source = "agents" if path.is_relative_to(AGENTS_SKILLS) else "codex"
    if path.is_relative_to(CODEX_SKILLS / ".system"):
        source = "codex-system"
    family = family_for_name(name)

    return SkillRecord(
        skill_id=name,
        family=family,
        offices=FAMILY_OFFICES.get(family, "吏部"),
        lifecycle="active",
        source=source,
        path=path,
        note="canonical active skill",
    )


def collect_records() -> list[SkillRecord]:
    if os.environ.get("SXLB_SCAN_LOCAL_SKILLS") != "1":
        return sorted(
            [
                SkillRecord(
                    skill_id=skill_id,
                    family=family,
                    offices=offices,
                    lifecycle=lifecycle,
                    source=source,
                    path=Path(path),
                    note=note,
                )
                for skill_id, family, offices, lifecycle, source, path, note in PUBLIC_RECORDS
            ],
            key=lambda r: (r.family, r.lifecycle, r.skill_id, str(r.path)),
        )

    roots = [AGENTS_SKILLS, CODEX_SKILLS, SUPERPOWERS_SKILLS, PLUGIN_CACHE]
    records: list[SkillRecord] = []
    for root in roots:
        if root.exists():
            for path in sorted(root.glob("**/SKILL.md")):
                records.append(classify(path))
    return sorted(records, key=lambda r: (r.family, r.lifecycle, r.skill_id, str(r.path)))


def plugin_skill_count() -> int:
    if os.environ.get("SXLB_SCAN_LOCAL_SKILLS") != "1":
        return sum(1 for record in collect_records() if record.source == "plugin-cache")
    if not PLUGIN_CACHE.exists():
        return 0
    return sum(1 for _ in PLUGIN_CACHE.glob("**/SKILL.md"))


def render(records: list[SkillRecord]) -> str:
    active = [r for r in records if r.lifecycle in {"active", "active-via-family"}]
    reference = [r for r in records if r.lifecycle == "reference-only"]
    families = sorted({r.family for r in records})

    lines = [
        "# Skill Inventory (Generated)",
        "",
        "> Generated by `scripts/skill_inventory.py`. Do not edit by hand.",
        "",
        "## Summary",
        "",
        f"- total records: {len(records)}",
        f"- active records: {len(active)}",
        f"- reference-only records: {len(reference)}",
        f"- families: {len(families)}",
        "",
        "## Records",
        "",
        "| lifecycle | family | sxlb offices | skill | source | path | note |",
        "|---|---|---|---|---|---|---|",
    ]
    for record in records:
        rel_path = str(record.path)
        lines.append(
            f"| {record.lifecycle} | {record.family} | {record.offices} | `{record.skill_id}` | "
            f"{record.source} | `{rel_path}` | {record.note} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SXLB skill inventory.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if output is stale.")
    args = parser.parse_args()

    content = render(collect_records())
    if args.check:
        existing = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if existing != content:
            print(f"stale inventory: {args.output}")
            return 1
        return 0

    args.output.write_text(content, encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
