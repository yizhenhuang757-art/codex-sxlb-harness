#!/usr/bin/env python3
"""Protect SXLB configuration/canonical surfaces from silent weakening."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
PROTECTED_NAMES = {"SKILL.md", "MODE.md"}
PROTECTED_PREFIXES = {
    "hooks",
    "protocols",
    "scripts",
    "skills",
    "templates",
}
PROTECTED_FILE_NAMES = {
    "allowlist.md",
    "mapping.md",
    "skill-clans.json",
    "skill-inventory.generated.md",
    "sxlb-hooks.json",
    "sxlb-hooks.schema.json",
}
EXTERNAL_CONFIG_HINTS = ("mcp", "chrome", "cookie", "token", "github", "opencli", "agent-reach")


def load_event() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("config protection input must be a JSON object")
    return data


def protected_path(path_value: str) -> bool:
    path = Path(path_value).expanduser()
    lowered = str(path).lower()
    if any(hint in lowered for hint in EXTERNAL_CONFIG_HINTS):
        return True
    try:
        rel = path.resolve().relative_to(SXLB_ROOT.resolve())
    except (ValueError, OSError):
        return False
    if str(rel) in PROTECTED_NAMES or rel.name in PROTECTED_FILE_NAMES:
        return True
    return bool(rel.parts and rel.parts[0] in PROTECTED_PREFIXES)


def check_change_plan(event: dict[str, Any], paths: list[str]) -> dict[str, Any] | None:
    plan_id = str(event.get("change_plan_id", "")).strip()
    case = str(event.get("case", "")).strip()
    if not plan_id or not case:
        return None
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "sxlb_change_plan.py"), "check", "--json"],
        input=json.dumps({"case": case, "change_plan_id": plan_id, "paths": paths}, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "errors": [result.stderr or result.stdout or "change plan check failed"]}


def evaluate(event: dict[str, Any]) -> dict[str, Any]:
    paths = [str(item) for item in event.get("paths") or event.get("write_paths") or []]
    protected = [path for path in paths if protected_path(path)]
    findings: list[dict[str, str]] = []
    status = "pass"
    reasons: list[str] = []
    plan_result = None

    if protected:
        plan_result = check_change_plan(event, protected)
        if not plan_result or not plan_result.get("ok"):
            status = "require-review"
            reasons.append("protected config/canonical edits require a matching change plan")
            findings.append({"category": "missing-change-plan", "status": "require-review"})

    return {
        "ok": status == "pass",
        "status": status,
        "protected_paths": protected,
        "findings": findings,
        "reasons": reasons,
        "change_plan": plan_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Protect SXLB config/canonical surfaces.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = evaluate(load_event())
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
