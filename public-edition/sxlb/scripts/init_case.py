#!/usr/bin/env python3
"""Scaffold the minimum auditable case package for an sxlb worklog."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

DEFAULT_TEMPLATES = (
    "case.md",
    "zhongshu-plan.md",
    "dispatch-order.md",
    "menxia-review.md",
    "memorial-report.md",
    "event-ledger.md",
    "status-board.md",
    "retrospective.md",
    "learning-candidates.jsonl",
    "learning-ledger.jsonl",
    "menxia-readiness.md",
    "verification.md",
    "artifact-registry.md",
    "records-routing.md",
)

LIGHTWEIGHT_TEMPLATES = (
    "case.md",
    "dispatch-order.md",
    "menxia-review.md",
    "memorial-report.md",
    "event-ledger.md",
    "status-board.md",
    "records-routing.md",
)

PROFILES = {
    "full": DEFAULT_TEMPLATES,
    "lightweight": LIGHTWEIGHT_TEMPLATES,
}


def scaffold_case(
    case_dir: Path,
    *,
    force: bool = False,
    templates: Iterable[str] | None = None,
    profile: str = "full",
) -> list[str]:
    """Create the standard sxlb case-package files."""
    case_dir.mkdir(parents=True, exist_ok=True)
    if templates is None:
        try:
            templates = PROFILES[profile]
        except KeyError as exc:
            raise ValueError(f"Unknown sxlb case profile: {profile}") from exc
    created: list[str] = []

    for name in templates:
        src = TEMPLATES_DIR / name
        dst = case_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing template: {src}")
        if dst.exists() and not force:
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        created.append(name)

    return created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold an sxlb case package in a worklog folder.")
    parser.add_argument("case_dir", type=Path, help="Target worklog/case directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing case files")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="full", help="Case package weight to scaffold")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    created = scaffold_case(args.case_dir, force=args.force, profile=args.profile)
    if created:
        print("Created:")
        for name in created:
            print(f"- {name}")
    else:
        print("No files created; case package already existed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
