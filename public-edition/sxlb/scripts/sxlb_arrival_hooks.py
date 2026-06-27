#!/usr/bin/env python3
"""Index department-owned sxlb arrival-only helper hooks."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from hubu_arrival_hooks import recommend_hooks as recommend_hubu_hooks
from hubu_arrival_hooks import render_external_evidence_candidate
from libu_arrival_hooks import recommend_hooks as recommend_libu_hooks
from libu_arrival_hooks import render_qijulang_candidate, render_records_routing_candidate
from menxia_arrival_hooks import recommend_hooks as recommend_menxia_hooks
from xingbu_arrival_hooks import recommend_hooks as recommend_xingbu_hooks


DEPARTMENT_RECOMMENDERS = (
    recommend_menxia_hooks,
    recommend_xingbu_hooks,
    recommend_libu_hooks,
    recommend_hubu_hooks,
)


def recommend_hooks(data: dict[str, Any]) -> list[dict[str, str]]:
    """Return department-owned hooks; this router owns no substantive hook."""
    hooks: list[dict[str, str]] = []
    for recommend in DEPARTMENT_RECOMMENDERS:
        hooks.extend(recommend(data))
    return hooks


def render_candidate(hook_name: str, data: dict[str, Any]) -> str:
    if hook_name == "records-routing-candidate":
        return render_records_routing_candidate(data)
    if hook_name == "qijulang-candidate":
        return render_qijulang_candidate(data)
    if hook_name == "external-evidence-package":
        return render_external_evidence_candidate(data)
    raise ValueError(f"No renderable candidate for hook: {hook_name}")


def build_result(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy": "arrival-only",
        "router_role": "index-only",
        "non_expansion_rule": "helper hooks may run only when the governed flow has already reached their department station",
        "hooks": recommend_hooks(data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Index conservative department-owned sxlb arrival hooks.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--render", choices=("records-routing-candidate", "qijulang-candidate", "external-evidence-package"))
    args = parser.parse_args()
    data = json.loads(sys.stdin.read() or "{}")
    if args.render:
        print(render_candidate(args.render, data))
        return 0
    result = build_result(data)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"policy: {result['policy']}")
        print(f"router_role: {result['router_role']}")
        if not result["hooks"]:
            print("hooks: none")
        for hook_item in result["hooks"]:
            print(f"- {hook_item['hook']} ({hook_item['office']} via {hook_item['owner_script']}): {hook_item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
