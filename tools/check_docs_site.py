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


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path("docs")
    errors = validate(root)
    if errors:
        print("\n".join(errors))
        return 1
    print("Documentation site structure: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
