"""Shared predicates for sxlb arrival-only department helpers."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable


BCD_CLASSES = {"B", "C", "D"}
COMPLETION_STATES = {"门下复核", "待回奏", "退朝清算"}
REVIEW_STATES = {"门下审议", "门下复核", "待回奏", "退朝清算"}
RETURN_STATES = {"分支回传", "subagent-return", "回传审查"}
HUMAN_FACING_TARGETS = {
    "skill-manual",
    "manual",
    "readme",
    "project-page",
    "ai-report",
    "vault-doc",
    "usage-note",
    "human-facing",
}


def text(data: dict[str, Any], key: str, default: str = "") -> str:
    return str(data.get(key, default) or "").strip()


def lower(data: dict[str, Any], key: str) -> str:
    return text(data, key).lower()


def truthy(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "yes", "true", "required", "must", "需要", "必须"}


def at_completion_station(data: dict[str, Any]) -> bool:
    return lower(data, "phase") in {"completion", "close", "exit"} or text(data, "state") in COMPLETION_STATES


def at_review_station(data: dict[str, Any]) -> bool:
    return lower(data, "phase") in {"review", "completion", "close", "exit"} or text(data, "state") in REVIEW_STATES


def at_return_station(data: dict[str, Any]) -> bool:
    return lower(data, "phase") in {"subagent-return", "return", "completion", "close", "exit"} or text(data, "state") in RETURN_STATES


def hook(name: str, office: str, reason: str, command_hint: str, writes: str, owner_script: str) -> dict[str, str]:
    return {
        "hook": name,
        "office": office,
        "reason": reason,
        "arrival_policy": "runs only at the existing workflow station; does not create a new station",
        "command_hint": command_hint,
        "writes": writes,
        "owner_script": owner_script,
        "router_role": "index-only",
    }


Renderer = Callable[[dict[str, Any]], str]
Recommender = Callable[[dict[str, Any]], list[dict[str, str]]]


def run_department_cli(
    *,
    description: str,
    office: str,
    recommend_hooks: Recommender,
    renderers: dict[str, Renderer] | None = None,
) -> int:
    """Run the standard JSON/stdin CLI for one department-owned arrival helper."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--json", action="store_true", dest="json_output")
    if renderers:
        parser.add_argument("--render", choices=tuple(renderers))
    args = parser.parse_args()
    data = json.loads(sys.stdin.read() or "{}")
    if renderers and args.render:
        print(renderers[args.render](data))
        return 0

    result = {"policy": "arrival-only", "office": office, "hooks": recommend_hooks(data)}
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"office: {result['office']}")
        if not result["hooks"]:
            print("hooks: none")
        for item in result["hooks"]:
            print(f"- {item['hook']}: {item['reason']}")
    return 0
