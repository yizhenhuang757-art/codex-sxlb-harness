#!/usr/bin/env python3
"""Plan/check/record SXLB canonical changes without applying edits."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-").lower()
    return slug or "change-plan"


def plan_dir(case_dir: Path) -> Path:
    return case_dir / "change-plans"


def plan_path(case_dir: Path, plan_id: str) -> Path:
    return plan_dir(case_dir) / f"{plan_id}.json"


def load_stdin_json() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("change plan input must be a JSON object")
    return data


def create_plan(case_dir: Path, *, title: str, paths: list[str], rollback: str) -> dict[str, Any]:
    plan_id = f"{now_stamp()}-{slugify(title)}"
    payload = {
        "version": 1,
        "plan_id": plan_id,
        "title": title,
        "case": str(case_dir),
        "paths": paths,
        "rollback": rollback,
        "status": "planned",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    plan_dir(case_dir).mkdir(parents=True, exist_ok=True)
    plan_path(case_dir, plan_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "plan_id": plan_id, "path": str(plan_path(case_dir, plan_id)), "plan": payload}


def check_plan(case_dir: Path, *, plan_id: str, paths: list[str]) -> dict[str, Any]:
    path = plan_path(case_dir, plan_id)
    if not path.exists():
        return {"ok": False, "status": "missing", "errors": [f"change plan not found: {plan_id}"]}
    plan = json.loads(path.read_text(encoding="utf-8"))
    planned = {str(item) for item in plan.get("paths", [])}
    missing = [item for item in paths if str(item) not in planned]
    errors = [f"path not covered by change plan: {item}" for item in missing]
    if not str(plan.get("rollback", "")).strip():
        errors.append("change plan missing rollback")
    return {"ok": not errors, "status": "pass" if not errors else "block", "errors": errors, "plan": plan}


def record_plan(case_dir: Path, *, plan_id: str, status: str) -> dict[str, Any]:
    path = plan_path(case_dir, plan_id)
    if not path.exists():
        return {"ok": False, "status": "missing", "errors": [f"change plan not found: {plan_id}"]}
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["status"] = status
    plan["recorded_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "status": status, "plan_id": plan_id, "path": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan/check/record SXLB canonical changes.")
    sub = parser.add_subparsers(dest="command", required=True)

    plan_cmd = sub.add_parser("plan")
    plan_cmd.add_argument("--case", required=True, type=Path)
    plan_cmd.add_argument("--title", required=True)
    plan_cmd.add_argument("--path", action="append", dest="paths", default=[])
    plan_cmd.add_argument("--rollback", required=True)
    plan_cmd.add_argument("--json", action="store_true", dest="json_output")

    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("--json", action="store_true", dest="json_output")

    record_cmd = sub.add_parser("record")
    record_cmd.add_argument("--case", required=True, type=Path)
    record_cmd.add_argument("--plan-id", required=True)
    record_cmd.add_argument("--status", default="applied")
    record_cmd.add_argument("--json", action="store_true", dest="json_output")

    args = parser.parse_args()
    if args.command == "plan":
        result = create_plan(args.case, title=args.title, paths=args.paths, rollback=args.rollback)
    elif args.command == "check":
        payload = load_stdin_json()
        result = check_plan(
            Path(str(payload.get("case", ""))),
            plan_id=str(payload.get("change_plan_id", "")),
            paths=[str(item) for item in payload.get("paths", [])],
        )
    else:
        result = record_plan(args.case, plan_id=args.plan_id, status=args.status)

    if getattr(args, "json_output", False):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result.get('ok')).lower()}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
