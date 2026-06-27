#!/usr/bin/env python3
"""Generate artifact-registry.md for an sxlb case package."""

from __future__ import annotations

import argparse
from pathlib import Path

from sxlb_guard import parse_task_class, read_file, required_files_for


CONSUMERS = {
    "case.md": "中书省",
    "zhongshu-plan.md": "尚书省",
    "dispatch-order.md": "门下省",
    "menxia-review.md": "礼部",
    "memorial-report.md": "回奏",
    "event-ledger.md": "门下省",
    "verification.md": "门下省",
    "learning-candidates.jsonl": "self-improving-agent",
    "artifact-registry.md": "门下省",
    "menxia-readiness.md": "门下复核",
    "records-routing.md": "待分流",
    "approval-ledger.md": "门下省",
    "objection-review.md": "门下省",
}

OPTIONAL_TRACKED_ARTIFACTS = ("approval-ledger.md", "learning-ledger.jsonl", "objection-review.md")


def build_registry(case_dir: Path) -> list[dict[str, str]]:
    case_text = read_file(case_dir, "case.md")
    task_class = parse_task_class(case_text)
    required = set(required_files_for(task_class))
    required.add("menxia-readiness.md")
    required.add("artifact-registry.md")
    required.add("records-routing.md")
    optional_present = {name for name in OPTIONAL_TRACKED_ARTIFACTS if (case_dir / name).exists()}
    artifacts = sorted(required | optional_present)
    rows: list[dict[str, str]] = []
    for artifact in artifacts:
        present = (case_dir / artifact).exists()
        rows.append(
            {
                "artifact": artifact,
                "required": "yes" if artifact in required else "no",
                "status": "present" if present else "missing",
                "consumer": CONSUMERS.get(artifact, "门下省"),
                "blocking": "yes" if artifact in required else "no",
            }
        )
    return rows


def render_registry(rows: list[dict[str, str]]) -> str:
    lines = [
        "# 产物注册表",
        "",
        "| artifact | required | status | consumer | blocking |",
        "|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['artifact']} | {row['required']} | {row['status']} | {row['consumer']} | {row['blocking']} |"
        )
    return "\n".join(lines) + "\n"


def write_registry(case_dir: Path) -> Path:
    path = case_dir / "artifact-registry.md"
    path.write_text(render_registry(build_registry(case_dir)), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate artifact-registry.md for an sxlb case.")
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()
    print(write_registry(args.case_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
