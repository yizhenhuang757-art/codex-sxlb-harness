#!/usr/bin/env python3
"""Generate objection-review.md for high-risk completion cases."""

from __future__ import annotations

import argparse
from pathlib import Path

from approval_ledger import collect_approval_entries
from sxlb_guard import has_substantive_reason, parse_fields, read_file


OUTPUT_NAME = "objection-review.md"


def requires_objection_review(case_dir: Path) -> bool:
    memorial_text = read_file(case_dir, "memorial-report.md") or ""
    memorial_fields = parse_fields(memorial_text)
    canonical_update = memorial_fields.get("canonical 更新", "")
    if not has_substantive_reason(canonical_update):
        return False
    return bool(collect_approval_entries(case_dir))


def render_objection_review(case_dir: Path) -> str:
    entries = collect_approval_entries(case_dir)
    blocking = "yes" if any(entry.get("approval_status") != "present" for entry in entries) else "no"
    trigger = "dangerous command + canonical update"
    return "\n".join(
        [
            "# 异议复核单",
            "",
            "## 触发背景",
            "",
            f"- 触发原因：{trigger}",
            "- 输入材料：menxia-review.md, memorial-report.md, approval-ledger.md",
            "",
            "## 复核摘要",
            "",
            "- 重合问题：none",
            "- 独有问题：none",
            "- 误报：none",
            f"- 是否阻断：{blocking}",
            "",
        ]
    )


def write_objection_review(case_dir: Path) -> Path:
    path = case_dir / OUTPUT_NAME
    path.write_text(render_objection_review(case_dir), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate objection-review.md when case risk requires it.")
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()
    if not requires_objection_review(args.case_dir):
        print("not-required")
        return 0
    print(write_objection_review(args.case_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
