#!/usr/bin/env python3
"""Update and validate an sxlb case's visible progress records."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from artifact_registry import write_registry
from sxlb_guard import GuardResult, parse_fields, validate_case_dir


DEFAULT_CATALOG_SCRIPT = Path("$CODEX_SKILLS_HOME/planning-with-files/scripts/update-guoshiguan-catalog.py")
VOLATILE_RECORD_NAME = "volatile-record.md"
VOLATILE_DELETE_POLICIES = {"delete-on-退朝", "delete-on-exit"}
NO_DURABLE_ROUTE_VALUES = {"", "none", "n/a", "no", "false", "无", "否", "未记录", "不记录"}
DURABLE_ROUTE_FIELDS = (
    "案卷归档",
    "case",
    "canonical 更新",
    "canonical",
    "progress 更新",
    "progress",
    "restart 更新",
    "restart",
    "国史馆 更新",
    "guoshiguan",
    "起居郎候补",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def guard_to_dict(result: GuardResult) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "task_class": result.task_class,
        "errors": result.errors,
        "warnings": result.warnings,
    }


def normalize_route_value(value: str) -> str:
    return value.strip().lower()


def has_durable_route_value(value: str) -> bool:
    normalized = normalize_route_value(value)
    if normalized in NO_DURABLE_ROUTE_VALUES:
        return False
    parts = [
        normalize_route_value(part)
        for part in normalized.replace("，", ",").replace("；", ",").replace(";", ",").split(",")
    ]
    parts = [part for part in parts if part]
    if not parts:
        return False
    return any(part not in NO_DURABLE_ROUTE_VALUES for part in parts)


def cleanup_volatile_record(case_dir: Path) -> dict[str, Any]:
    record_path = case_dir / VOLATILE_RECORD_NAME
    if not record_path.exists():
        return {"state": "absent", "path": str(record_path), "reason": "no volatile record"}

    text = record_path.read_text(encoding="utf-8")
    fields = parse_fields(text)
    record_type = normalize_route_value(fields.get("记录类型", ""))
    if record_type != "volatile":
        return {"state": "preserved", "path": str(record_path), "reason": "record is not marked volatile"}

    cleanup_policy = normalize_route_value(fields.get("清理策略", ""))
    if cleanup_policy not in VOLATILE_DELETE_POLICIES:
        return {"state": "preserved", "path": str(record_path), "reason": "cleanup policy is not delete-on-exit"}

    durable_route = fields.get("持久出口", "")
    routed = has_durable_route_value(durable_route)
    for field_name in DURABLE_ROUTE_FIELDS:
        if has_durable_route_value(fields.get(field_name, "")):
            routed = True
            break

    if routed:
        return {"state": "preserved", "path": str(record_path), "reason": "record has a durable route"}

    record_path.unlink()
    return {"state": "deleted", "path": str(record_path), "reason": "unrouted volatile record removed on exit"}


def append_event(case_dir: Path, *, state: str, action: str, office: str, summary: str, evidence: str) -> Path:
    ledger_path = case_dir / "event-ledger.md"
    if ledger_path.exists():
        existing = ledger_path.read_text(encoding="utf-8").rstrip()
    else:
        existing = "# 事件簿"
    entry = "\n".join(
        [
            "",
            f"- 时间：{now_iso()}",
            f"  状态：{state}",
            f"  动作：{action}",
            f"  发起：{office}",
            f"  摘要：{summary}",
            f"  证据：{evidence}",
            "",
        ]
    )
    write_text(ledger_path, existing + entry)
    return ledger_path


def refresh_registry(case_dir: Path) -> Path:
    return write_registry(case_dir)


def check_case(case_dir: Path, *, phase: str = "completion", refresh: bool = False) -> dict[str, Any]:
    registry_path: Path | None = refresh_registry(case_dir) if refresh else None
    guard = validate_case_dir(case_dir, phase=phase)
    return {
        "state": "validated" if guard.ok else "blocked",
        "registry": str(registry_path) if registry_path else None,
        "guard": guard_to_dict(guard),
    }


def transition_case(
    case_dir: Path,
    *,
    to_state: str,
    office: str = "太子",
    summary: str = "Case progress synchronized",
    evidence: str = "event-ledger.md",
    phase: str = "completion",
) -> dict[str, Any]:
    event_path = append_event(
        case_dir,
        state=to_state,
        action="录案",
        office=office,
        summary=summary,
        evidence=evidence,
    )
    registry_path = refresh_registry(case_dir)
    guard = validate_case_dir(case_dir, phase=phase)
    return {
        "state": to_state,
        "event": str(event_path),
        "registry": str(registry_path),
        "guard": guard_to_dict(guard),
    }


def refresh_catalog(script: Path = DEFAULT_CATALOG_SCRIPT) -> dict[str, Any]:
    if not script.exists():
        return {"ok": False, "script": str(script), "error": "catalog script not found"}
    completed = subprocess.run(
        ["python3", str(script)],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "ok": completed.returncode == 0,
        "script": str(script),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def close_case(
    case_dir: Path,
    *,
    phase: str = "completion",
    refresh_catalog_after: bool = False,
    catalog_script: Path = DEFAULT_CATALOG_SCRIPT,
) -> dict[str, Any]:
    registry_path = refresh_registry(case_dir)
    guard = validate_case_dir(case_dir, phase=phase)
    if guard.ok:
        state = "已回奏"
        summary = "Case status closed after guard passed"
    else:
        state = "待分流"
        summary = "Case status sync found guard blockers"
    event_path = append_event(
        case_dir,
        state=state,
        action="录案",
        office="门下省",
        summary=summary,
        evidence="sxlb_case_status.py",
    )
    if guard.ok:
        volatile_record = cleanup_volatile_record(case_dir)
    else:
        volatile_record = {
            "state": "preserved",
            "path": str(case_dir / VOLATILE_RECORD_NAME),
            "reason": "guard blocked closure",
        }
    from harness_hooks import check_completion

    harness_hooks = check_completion(case_dir, phase=phase).to_dict()
    catalog = refresh_catalog(catalog_script) if refresh_catalog_after and guard.ok else None
    return {
        "state": state,
        "event": str(event_path),
        "registry": str(registry_path),
        "guard": guard_to_dict(guard),
        "harness_hooks": harness_hooks,
        "volatile_record": volatile_record,
        "catalog": catalog,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Synchronize an sxlb case's ledger, registry, guard status, and optional catalog.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Validate a case, optionally refreshing artifact-registry.md first.")
    check_parser.add_argument("case_dir", type=Path)
    check_parser.add_argument("--phase", choices=("startup", "completion"), default="completion")
    check_parser.add_argument("--refresh-registry", action="store_true")
    check_parser.add_argument("--json", action="store_true", dest="json_output")

    transition_parser = subparsers.add_parser("transition", help="Append a 录案 event, refresh registry, and run guard.")
    transition_parser.add_argument("case_dir", type=Path)
    transition_parser.add_argument("--to", required=True, dest="to_state")
    transition_parser.add_argument("--office", default="太子")
    transition_parser.add_argument("--summary", default="Case progress synchronized")
    transition_parser.add_argument("--evidence", default="event-ledger.md")
    transition_parser.add_argument("--phase", choices=("startup", "completion"), default="completion")
    transition_parser.add_argument("--json", action="store_true", dest="json_output")

    close_parser = subparsers.add_parser("close", help="Refresh registry, run guard, append final 录案 status, and optionally refresh 国史馆.")
    close_parser.add_argument("case_dir", type=Path)
    close_parser.add_argument("--phase", choices=("startup", "completion"), default="completion")
    catalog_group = close_parser.add_mutually_exclusive_group()
    catalog_group.add_argument("--refresh-catalog", dest="refresh_catalog", action="store_true", default=True)
    catalog_group.add_argument("--no-refresh-catalog", dest="refresh_catalog", action="store_false")
    close_parser.add_argument("--catalog-script", type=Path, default=DEFAULT_CATALOG_SCRIPT)
    close_parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def format_result(result: dict[str, Any]) -> str:
    guard = result.get("guard", {})
    lines = [
        f"state: {result.get('state')}",
        f"guard_ok: {str(guard.get('ok')).lower()}",
    ]
    if result.get("event"):
        lines.append(f"event: {result['event']}")
    if result.get("registry"):
        lines.append(f"registry: {result['registry']}")
    volatile_record = result.get("volatile_record")
    if volatile_record is not None:
        lines.append(f"volatile_record: {volatile_record.get('state')} ({volatile_record.get('reason')})")
    harness_hooks = result.get("harness_hooks")
    if harness_hooks is not None:
        lines.append(f"harness_hooks_ok: {str(harness_hooks.get('ok')).lower()}")
        for warning in harness_hooks.get("warnings", []):
            lines.append(f"harness_warning: {warning}")
        for error in harness_hooks.get("errors", []):
            lines.append(f"harness_error: {error}")
    for error in guard.get("errors", []):
        lines.append(f"error: {error}")
    for warning in guard.get("warnings", []):
        lines.append(f"warning: {warning}")
    catalog = result.get("catalog")
    if catalog is not None:
        lines.append(f"catalog_ok: {str(catalog.get('ok')).lower()}")
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "check":
        result = check_case(args.case_dir, phase=args.phase, refresh=args.refresh_registry)
    elif args.command == "transition":
        result = transition_case(
            args.case_dir,
            to_state=args.to_state,
            office=args.office,
            summary=args.summary,
            evidence=args.evidence,
            phase=args.phase,
        )
    elif args.command == "close":
        result = close_case(
            args.case_dir,
            phase=args.phase,
            refresh_catalog_after=args.refresh_catalog,
            catalog_script=args.catalog_script,
        )
    else:
        raise ValueError(f"Unknown command: {args.command}")

    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))
    return 0 if result["guard"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
