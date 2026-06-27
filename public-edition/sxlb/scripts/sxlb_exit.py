#!/usr/bin/env python3
"""退朝清算 wrapper around existing sxlb close mechanics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sxlb_case_status import close_case


def run_exit(
    case_dir: Path,
    *,
    phase: str = "completion",
    refresh_catalog: bool = True,
) -> dict:
    """Run the existing close path and classify the next user-visible action."""
    result = close_case(case_dir, phase=phase, refresh_catalog_after=refresh_catalog)
    guard_ok = bool(result.get("guard", {}).get("ok"))
    result["next_action"] = "exit-confirmation" if guard_ok else "repair-before-exit"
    result["exit_allowed"] = guard_ok
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run sxlb 退朝清算 close checks.")
    parser.add_argument("case_dir", type=Path)
    parser.add_argument("--phase", choices=("startup", "completion"), default="completion")
    catalog_group = parser.add_mutually_exclusive_group()
    catalog_group.add_argument("--refresh-catalog", dest="refresh_catalog", action="store_true", default=True)
    catalog_group.add_argument("--no-refresh-catalog", dest="refresh_catalog", action="store_false")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    result = run_exit(args.case_dir, phase=args.phase, refresh_catalog=args.refresh_catalog)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"state: {result['state']}")
        print(f"exit_allowed: {str(result['exit_allowed']).lower()}")
        print(f"next_action: {result['next_action']}")
    return 0 if result["exit_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
