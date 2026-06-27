#!/usr/bin/env python3
"""Recommend the minimum sxlb task class and case profile from mechanical signals."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def _truthy(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "yes", "true", "y", "是", "有"}
    return bool(value)


def _int_value(data: dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(data.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def recommend_profile(signals: dict[str, Any]) -> dict[str, Any]:
    """Return a conservative recommendation, not a final governance decision."""
    reasons: list[str] = []
    task_class = "A"
    profile = "lightweight"

    if _truthy(signals, "real_subagent") or _truthy(signals, "parallel"):
        task_class = "D"
        profile = "full"
        reasons.append("real subagent or parallel topology needs D route")
    elif _truthy(signals, "multi_branch") or _truthy(signals, "research"):
        task_class = "C"
        profile = "full"
        reasons.append("multi-branch or research task needs C route")
    elif (
        _truthy(signals, "file_edit")
        or _truthy(signals, "verification")
        or _int_value(signals, "tool_actions") > 1
    ):
        task_class = "B"
        profile = "full"
        reasons.append("file edit or verification requires B route")

    if _truthy(signals, "protocol_change") or _truthy(signals, "automation"):
        if task_class == "A":
            task_class = "B"
        profile = "full"
        reasons.append("protocol or automation change needs full evidence")

    if _truthy(signals, "high_risk") or str(signals.get("risk", "")).strip().lower() in {"high", "medium"}:
        if task_class == "A":
            task_class = "B"
        profile = "full"
        reasons.append("non-low risk needs reviewed case evidence")

    if not reasons:
        reasons.append("single substantive action")

    return {
        "task_class": task_class,
        "profile": profile,
        "route_minimum": (
            "太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏"
            if task_class == "A"
            else "太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏"
        ),
        "reasons": reasons,
        "advisory": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend minimum sxlb task class and case profile.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    try:
        signals = json.load(sys.stdin)
        result = recommend_profile(signals)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"task_class: {result['task_class']}")
        print(f"profile: {result['profile']}")
        print(f"route_minimum: {result['route_minimum']}")
        for reason in result["reasons"]:
            print(f"- {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
