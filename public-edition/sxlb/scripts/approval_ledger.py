#!/usr/bin/env python3
"""Generate an approval ledger for dangerous real-subagent actions."""

from __future__ import annotations

import argparse
from pathlib import Path

from sxlb_guard import find_dangerous_command, parse_dispatch_assignments, parse_fields, read_file


LEDGER_NAME = "approval-ledger.md"


def collect_approval_entries(case_dir: Path) -> list[dict[str, str]]:
    dispatch_text = read_file(case_dir, "dispatch-order.md") or ""
    entries: list[dict[str, str]] = []
    for assignment in parse_dispatch_assignments(dispatch_text):
        if assignment.get("分支执行") != "real-subagent":
            continue
        return_ref = assignment.get("回传物", "").strip()
        if not return_ref:
            continue
        return_text = read_file(case_dir, return_ref)
        if not return_text:
            continue
        return_fields = parse_fields(return_text)
        command = find_dangerous_command(return_fields.get("关键命令或动作", ""))
        if not command:
            continue
        approval_evidence = return_fields.get("额外批准证据", "").strip()
        entries.append(
            {
                "branch": assignment.get("分支编号", "unknown").strip() or "unknown",
                "office": assignment.get("官署", "unknown").strip() or "unknown",
                "command": command,
                "approval_status": "present" if approval_evidence and approval_evidence.lower() not in {"n/a", "none"} else "missing",
                "approval_evidence": approval_evidence or "missing",
                "return": return_ref,
            }
        )
    return entries


def render_approval_ledger(entries: list[dict[str, str]]) -> str:
    lines = [
        "# Approval Ledger",
        "",
        "| branch | office | command | approval_status | approval_evidence | return |",
        "|---|---|---|---|---|---|",
    ]
    if entries:
        for entry in entries:
            lines.append(
                "| {branch} | {office} | `{command}` | {approval_status} | {approval_evidence} | {return} |".format(
                    **entry
                )
            )
    else:
        lines.append("| none | none | none | none | none | none |")
    return "\n".join(lines) + "\n"


def write_approval_ledger(case_dir: Path) -> Path:
    path = case_dir / LEDGER_NAME
    path.write_text(render_approval_ledger(collect_approval_entries(case_dir)), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate approval-ledger.md for an sxlb case.")
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()
    print(write_approval_ledger(args.case_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
