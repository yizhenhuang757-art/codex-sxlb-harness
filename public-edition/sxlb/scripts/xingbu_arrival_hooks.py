#!/usr/bin/env python3
"""刑部 arrival-only verification and touched-files helper hooks."""

from __future__ import annotations

from typing import Any

from arrival_common import BCD_CLASSES, at_completion_station, at_return_station, hook, lower, run_department_cli, text, truthy


OWNER_SCRIPT = "xingbu_arrival_hooks.py"


def needs_verification_snippet(data: dict[str, Any]) -> bool:
    task_class = text(data, "task_class").upper()
    office = text(data, "office")
    has_output = bool(text(data, "verification_output") or text(data, "output"))
    return at_completion_station(data) and task_class in BCD_CLASSES and (office == "刑部" or has_output)


def needs_touched_files_evidence(data: dict[str, Any]) -> bool:
    audit_required = lower(data, "actual_touched_audit") == "required" or truthy(data, "actual_touched_audit")
    return at_return_station(data) and truthy(data, "file_edit") and audit_required


def recommend_hooks(data: dict[str, Any]) -> list[dict[str, str]]:
    hooks: list[dict[str, str]] = []
    if needs_verification_snippet(data):
        hooks.append(
            hook(
                "verification-snippet",
                "刑部",
                "B/C/D completion with 刑部 or concrete verification output already requires verification evidence",
                "sxlb_verification_snippet.py",
                "verification.md snippet",
                OWNER_SCRIPT,
            )
        )
    if needs_touched_files_evidence(data):
        hooks.append(
            hook(
                "touched-files-evidence",
                "刑部",
                "branch return or completion station already requires actual touched-files audit",
                "touched_files.py --repo <repo> --output <case-dir>/subagents/returns/touched-files-<branch>.txt",
                "touched-files evidence",
                OWNER_SCRIPT,
            )
        )
    return hooks


def main() -> int:
    return run_department_cli(
        description="Run 刑部 arrival-only verification helper hooks.",
        office="刑部",
        recommend_hooks=recommend_hooks,
    )


if __name__ == "__main__":
    raise SystemExit(main())
