"""Validate the required bilingual GitHub Pages documentation structure."""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_PAIRS = (
    ("index.md", "zh-CN/index.md"),
    ("quickstart.md", "zh-CN/quickstart.md"),
    ("features.md", "zh-CN/features.md"),
    ("workflow-reference.md", "zh-CN/workflow-reference.md"),
    ("three-departments-six-ministries.md", "zh-CN/three-departments-six-ministries.md"),
    ("sxlb-mapping.md", "zh-CN/sxlb-mapping.md"),
    ("why-sxlb.md", "zh-CN/why-sxlb.md"),
    ("skill-directory.md", "zh-CN/skill-directory.md"),
    ("sources.md", "zh-CN/sources.md"),
)

EDITORIAL_PROCESS_LANGUAGE = (
    "Editorial methods used for this revision",
    "本次修订使用的编辑方法",
)


def validate(root: Path) -> list[str]:
    """Return structure errors for the bilingual documentation pages."""
    errors: list[str] = []
    for english_path, chinese_path in REQUIRED_PAIRS:
        for relative_path in (english_path, chinese_path):
            page = root / relative_path
            if not page.is_file():
                errors.append(f"Missing required page: {relative_path}")
            elif not page.read_text(encoding="utf-8").strip():
                errors.append(f"Required page is empty: {relative_path}")
    return errors


def validate_public_page_language(root: Path) -> list[str]:
    """Reject public copy that describes how the documentation was edited."""
    errors: list[str] = []
    for relative_path in ("sources.md", "zh-CN/sources.md"):
        page = root / relative_path
        if not page.is_file():
            continue
        content = page.read_text(encoding="utf-8")
        if any(phrase in content for phrase in EDITORIAL_PROCESS_LANGUAGE):
            errors.append(f"Public page explains its editorial process: {relative_path}")
    return errors


def validate_source_records(records: list[dict[str, object]]) -> list[str]:
    """Return errors for source claims used in public skill documentation."""
    errors: list[str] = []
    for record in records:
        skill_id = str(record.get("skill_id", "<unknown>"))
        relation = record.get("source_relation")
        source_url = record.get("source_url")
        source_note = str(record.get("source_note", "")).strip()
        if relation in {"external-reference", "upstream-project"}:
            if not isinstance(source_url, str) or not source_url.startswith("https://"):
                errors.append(f"External source requires HTTPS URL: {skill_id}")
        elif not source_url and not source_note:
            errors.append(f"Source relation requires note or URL: {skill_id}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("docs")
    errors = validate(root) + validate_public_page_language(root)
    if errors:
        print("\n".join(errors))
        return 1
    print("Documentation site structure: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
