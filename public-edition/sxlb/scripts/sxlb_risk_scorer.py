#!/usr/bin/env python3
"""Score SXLB event risk and recommend task class/profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from sxlb_guard import find_dangerous_command


SXLB_ROOT = Path(__file__).resolve().parents[1]
STRICT_NAMES = {"SKILL.md", "MODE.md"}
STRICT_DIRS = {"hooks", "protocols", "scripts", "skills", "templates"}
EXTERNAL_CONFIG_HINTS = ("mcp", "chrome", "cookie", "token", "github", "opencli", "agent-reach")


def load_event() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("risk scorer input must be a JSON object")
    return data


def is_sxlb_protected(path_value: str) -> bool:
    path = Path(path_value).expanduser()
    try:
        rel = path.resolve().relative_to(SXLB_ROOT.resolve())
    except (ValueError, OSError):
        return False
    return str(rel) in STRICT_NAMES or bool(rel.parts and rel.parts[0] in STRICT_DIRS)


def score_event(event: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    paths = [str(item) for item in event.get("write_paths") or event.get("paths") or event.get("touched_files") or []]
    command = str(event.get("command") or "")
    event_name = str(event.get("event") or "")

    if any(is_sxlb_protected(path) for path in paths):
        reasons.append("canonical-or-protected-path")
    if find_dangerous_command(command):
        reasons.append("dangerous-command")
    if str(event.get("real_dispatch", "")).lower() in {"yes", "true", "real-subagent"}:
        reasons.append("real-dispatch")
    lowered = " ".join(paths + [command, event_name]).lower()
    if any(hint in lowered for hint in EXTERNAL_CONFIG_HINTS):
        reasons.append("external-config-or-account")
    if event_name in {"completion_ready", "menxia.completion_ready"} and paths:
        reasons.append("files-changed-completion")

    if any(reason in reasons for reason in ("canonical-or-protected-path", "dangerous-command", "real-dispatch", "external-config-or-account")):
        profile = "strict"
        task_class = "C"
    elif paths or event_name in {"pre_action", "completion_ready", "menxia.completion_ready"}:
        profile = "standard"
        task_class = "B"
    else:
        profile = "minimal"
        task_class = "A"
        reasons.append("low-risk-no-write")

    return {
        "ok": True,
        "event": event_name,
        "recommended_profile": profile,
        "recommended_task_class": task_class,
        "reasons": sorted(set(reasons)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend SXLB profile/task class from one event packet.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = score_event(load_event())
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"profile: {result['recommended_profile']}")
        print(f"task_class: {result['recommended_task_class']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
