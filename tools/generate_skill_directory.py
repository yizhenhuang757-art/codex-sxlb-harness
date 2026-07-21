"""Generate public bilingual skill-directory pages from the audited inventory."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
INVENTORY_DIR = REPO_ROOT / "public-edition" / "sxlb" / "scripts"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(INVENTORY_DIR))

import check_docs_site
import skill_inventory


REGISTRY_PATH = REPO_ROOT / "docs" / "data" / "skill-source-registry.json"
OUTPUTS = {
    "en": REPO_ROOT / "docs" / "skill-directory.md",
    "zh-CN": REPO_ROOT / "docs" / "zh-CN" / "skill-directory.md",
}

RELATION_LABELS = {
    "en": {
        "external-reference": "External reference",
        "public-bundle": "Public bundle",
        "host-interface": "Host interface",
        "plugin-family": "Plugin family",
    },
    "zh-CN": {
        "external-reference": "外部参考",
        "public-bundle": "公共包",
        "host-interface": "宿主接口",
        "plugin-family": "插件能力族",
    },
}


def inventory_records() -> list[dict[str, str]]:
    return [
        {
            "skill_id": skill_id,
            "family": family,
            "offices": offices,
            "lifecycle": lifecycle,
            "source": source,
            "note": note,
        }
        for skill_id, family, offices, lifecycle, source, _path, note in skill_inventory.PUBLIC_RECORDS
    ]


def default_source(record: dict[str, str]) -> dict[str, object]:
    if record["source"] == "public-bundle":
        return {
            "source_relation": "public-bundle",
            "source_url": None,
            "source_note": "Bundled and maintained in this public repository.",
        }
    if record["source"] == "plugin-cache":
        return {
            "source_relation": "plugin-family",
            "source_url": None,
            "source_note": "Supplied by an installed host plugin family; no upstream URL is declared in the public inventory.",
        }
    return {
        "source_relation": "host-interface",
        "source_url": None,
        "source_note": "Optional interface supplied by a host environment; the public inventory does not declare an upstream URL.",
    }


def normalize_records(records: list[dict[str, str]], overrides: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for record in records:
        source = default_source(record)
        source.update(overrides.get(record["skill_id"], {}))
        rows.append({**record, **source})
    errors = check_docs_site.validate_source_records(rows)
    if errors:
        raise ValueError(errors[0])
    return sorted(rows, key=lambda row: (str(row["offices"]), str(row["skill_id"])))


def source_cell(row: dict[str, object], language: str) -> str:
    relation = RELATION_LABELS[language][str(row["source_relation"])]
    note = str(row["source_note"])
    url = row["source_url"]
    if isinstance(url, str) and url:
        return f'{html.escape(relation)}: <a href="{html.escape(url, quote=True)}">{html.escape(note)}</a>'
    return f"{html.escape(relation)}: {html.escape(note)}"


def render_page(rows: list[dict[str, object]], language: str) -> str:
    chinese = language == "zh-CN"
    title = "部门与技能目录" if chinese else "Office and skill directory"
    alternate = "/skill-directory/" if chinese else "/zh-CN/skill-directory/"
    description = (
        "按部门、生命周期和来源关系检索 SXLB 公共版技能目录。"
        if chinese
        else "Search the SXLB public skill directory by office, lifecycle, and source relationship."
    )
    intro = (
        "目录列出公共清单中的全部技能记录。来源关系说明该技能是否随公共包交付、由宿主环境提供，或有可验证的外部参考。没有公开来源链接的条目会直接说明这一点。"
        if chinese
        else "This directory lists every skill record in the public inventory. The source relation states whether SXLB bundles it, a host supplies it, or a verified external reference exists. Entries without a public upstream URL say so directly."
    )
    headers = ("部门", "技能", "生命周期", "交付状态", "来源关系", "使用说明") if chinese else ("Office", "Skill", "Lifecycle", "Delivery", "Source relationship", "Use note")
    table_rows: list[str] = []
    for row in rows:
        search_text = " ".join(str(row.get(key, "")) for key in ("offices", "skill_id", "family", "lifecycle", "note", "source_relation", "source_note")).lower()
        table_rows.append(
            f'<tr data-search="{html.escape(search_text, quote=True)}"><td>{html.escape(str(row["offices"]))}</td><td><code>{html.escape(str(row["skill_id"]))}</code></td><td>{html.escape(str(row["lifecycle"]))}</td><td>{html.escape(str(row["source"]))}</td><td>{source_cell(row, language)}</td><td>{html.escape(str(row["note"]))}</td></tr>'
        )
    return "\n".join(
        [
            "---",
            "layout: default",
            f"title: {title}",
            f"lang: {language}",
            f"alternate: {alternate}",
            "directory_filter: true",
            f"description: {description}",
            "---",
            "",
            f"# {title}",
            "",
            intro,
            "",
            ("查看[来源说明]({{ '/zh-CN/sources/' | relative_url }})，了解项目、方法和接口之间的区别。" if chinese else "Read the [source notes]({{ '/sources/' | relative_url }}) for the distinction between projects, methods, and interfaces."),
            "",
            '<label class="directory-filter-label" for="directory-filter">' + ("筛选目录" if chinese else "Filter directory") + '</label>',
            '<input id="directory-filter" data-directory-filter type="search" placeholder="' + ("输入部门、技能或来源" if chinese else "Type an office, skill, or source") + '">',
            '<p id="directory-count" aria-live="polite"></p>',
            "",
            '<div class="directory-table-wrap">',
            '<table data-directory-table>',
            '<thead><tr>' + "".join(f"<th>{html.escape(header)}</th>" for header in headers) + '</tr></thead>',
            '<tbody>',
            *table_rows,
            '</tbody></table></div>',
        ]
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    rows = normalize_records(inventory_records(), registry["skill_overrides"])
    stale: list[Path] = []
    for language, output in OUTPUTS.items():
        content = render_page(rows, language)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != content:
                stale.append(output)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(content, encoding="utf-8")
    if stale:
        print("Generated directory is stale: " + ", ".join(str(path.relative_to(REPO_ROOT)) for path in stale))
        return 1
    print("Skill directory: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
