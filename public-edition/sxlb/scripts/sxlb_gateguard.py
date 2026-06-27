#!/usr/bin/env python3
"""GateGuard preflight for protected SXLB edits and dangerous commands."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from sxlb_guard import find_dangerous_command


SXLB_ROOT = Path(__file__).resolve().parents[1]
PROTECTED_NAMES = {"SKILL.md", "MODE.md"}
PROTECTED_DIRS = {"protocols", "templates", "scripts"}
REQUIRED_FACTS = ("caller", "affected_states_offices_scripts", "user_instruction", "rollback_plan")
REVIEW_ONLY_RE = re.compile(r"git\s+clean\s+-[^\n;]*f|git\s+push\s+--force(?:-with-lease)?", re.I)


def load_event() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("GateGuard input must be a JSON object")
    return data


def protected_path(path_value: str) -> bool:
    path = Path(path_value).expanduser()
    try:
        rel = path.resolve().relative_to(SXLB_ROOT.resolve())
    except (ValueError, OSError):
        return False
    if str(rel) in PROTECTED_NAMES:
        return True
    return bool(rel.parts and rel.parts[0] in PROTECTED_DIRS)


def missing_facts(fact_package: dict[str, Any] | None) -> list[str]:
    facts = fact_package if isinstance(fact_package, dict) else {}
    missing: list[str] = []
    for field in REQUIRED_FACTS:
        value = facts.get(field)
        if value is None or str(value).strip().lower() in {"", "none", "n/a"}:
            missing.append(field)
    return missing


def command_findings(command: str | None) -> list[dict[str, str]]:
    if not command:
        return []
    dangerous = find_dangerous_command(command)
    if not dangerous:
        return []
    status = "require-review" if REVIEW_ONLY_RE.search(dangerous) else "block"
    return [{"category": "destructive-command", "match": dangerous, "status": status}]


def evaluate(event: dict[str, Any]) -> dict[str, Any]:
    paths = [str(item) for item in event.get("paths", [])]
    findings = command_findings(str(event.get("command") or ""))
    protected = [path for path in paths if protected_path(path)]
    missing = missing_facts(event.get("fact_package")) if protected else []

    status = "pass"
    reasons: list[str] = []
    if protected and missing:
        status = "require-review"
        reasons.append("protected SXLB edit requires a complete fact package")
    if findings:
        if any(item["status"] == "block" for item in findings):
            status = "block"
        elif status == "pass":
            status = "require-review"
        reasons.append("dangerous command requires GateGuard handling")

    return {
        "ok": status == "pass",
        "status": status,
        "protected_paths": protected,
        "missing_facts": missing,
        "findings": findings,
        "reasons": reasons,
    }


def exit_code(status: str) -> int:
    if status == "pass":
        return 0
    if status == "warn":
        return 1
    if status == "require-review":
        return 2
    if status == "block":
        return 3
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SXLB GateGuard preflight.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = evaluate(load_event())
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
        for reason in result["reasons"]:
            print(f"- {reason}")
    return exit_code(str(result["status"]))


if __name__ == "__main__":
    raise SystemExit(main())
