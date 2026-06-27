#!/usr/bin/env python3
"""Conservative autoflow wrapper: advance only low-risk sxlb states."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from sxlb_flow import advance_case
from sxlb_guard import parse_fields, read_file


ALLOWED_STAGES = {"尚书派发", "门下复核"}


def run_autoflow(case_dir: Path) -> dict[str, Any]:
    dispatch_text = read_file(case_dir, "dispatch-order.md")
    if not dispatch_text:
        raise FileNotFoundError(f"Missing dispatch-order.md in {case_dir}")
    dispatch = parse_fields(dispatch_text)
    stage = dispatch.get("当前阶段", "").strip()
    if stage not in ALLOWED_STAGES:
        return {
            "ok": False,
            "reason": f"autoflow blocked: stage `{stage}` not in conservative allowlist",
            "state": "blocked",
            "actions": [],
        }
    result = advance_case(case_dir, force=False)
    return {
        "ok": True,
        "reason": "advanced conservatively",
        "state": result["state"],
        "actions": result["actions"],
        "next_step": result["next_step"],
        "arrival_hooks": result["arrival_hooks"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run conservative sxlb autoflow.")
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = run_autoflow(args.case_dir)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        print(f"state: {result['state']}")
        print(f"reason: {result['reason']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
