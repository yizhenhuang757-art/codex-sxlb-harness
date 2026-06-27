#!/usr/bin/env python3
"""Validate the structured SXLB hook graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SXLB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = SXLB_ROOT / "hooks" / "sxlb-hooks.json"
DEFAULT_SCHEMA = SXLB_ROOT / "hooks" / "sxlb-hooks.schema.json"
LEGAL_EVENTS = {
    "taizi.intake",
    "zhongshu.plan_ready",
    "shangshu.dispatch_ready",
    "menxia.review_ready",
    "menxia.completion_ready",
    "reply.substantive",
    "case.pre_compact",
    "case.close",
}
LEGAL_PROFILES = {"minimal", "standard", "strict"}
OFFICE_TOKENS = {"太子", "中书省", "门下省", "尚书省", "吏部", "户部", "礼部", "兵部", "刑部", "工部"}
REQUIRED_HOOK_FIELDS = {"id", "event", "office", "script", "blocking", "profiles", "timeout_seconds"}


def load_json(path: Path) -> tuple[Any | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"missing file: {path}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid json in {path}: {exc}"]


def script_path_error(script: str) -> str | None:
    path = Path(script)
    if path.is_absolute():
        return f"script path must be relative: {script}"
    if ".." in path.parts:
        return f"script path must not contain '..': {script}"
    resolved = (SXLB_ROOT / path).resolve()
    try:
        resolved.relative_to(SXLB_ROOT.resolve())
    except ValueError:
        return f"script path escapes SXLB root: {script}"
    if not resolved.exists():
        return f"script path does not exist: {script}"
    if not resolved.is_file():
        return f"script path is not a file: {script}"
    return None


def validate_hook(hook: dict[str, Any], seen_ids: set[str], index: int) -> list[str]:
    prefix = f"hooks[{index}]"
    errors: list[str] = []
    missing = sorted(REQUIRED_HOOK_FIELDS - set(hook))
    for field in missing:
        errors.append(f"{prefix} missing field: {field}")
    if missing:
        return errors

    hook_id = hook.get("id")
    if not isinstance(hook_id, str) or not hook_id.strip():
        errors.append(f"{prefix}.id must be a non-empty string")
    elif hook_id in seen_ids:
        errors.append(f"duplicate hook id: {hook_id}")
    else:
        seen_ids.add(hook_id)

    event = hook.get("event")
    if event not in LEGAL_EVENTS:
        errors.append(f"{prefix}.event is not legal: {event}")

    office = hook.get("office")
    if not isinstance(office, str) or not any(token in office for token in OFFICE_TOKENS):
        errors.append(f"{prefix}.office is not a recognized SXLB office: {office}")

    if not isinstance(hook.get("blocking"), bool):
        errors.append(f"{prefix}.blocking must be boolean")

    timeout = hook.get("timeout_seconds")
    if not isinstance(timeout, int) or timeout <= 0:
        errors.append(f"{prefix}.timeout_seconds must be a positive integer")

    profiles = hook.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append(f"{prefix}.profiles must be a non-empty list")
    else:
        illegal = sorted(set(profiles) - LEGAL_PROFILES)
        if illegal:
            errors.append(f"{prefix}.profiles contains illegal values: {', '.join(illegal)}")

    script = hook.get("script")
    if not isinstance(script, str) or not script.strip():
        errors.append(f"{prefix}.script must be a non-empty string")
    else:
        error = script_path_error(script)
        if error:
            errors.append(f"{prefix}.{error}")

    args = hook.get("args", [])
    if args is not None and (not isinstance(args, list) or not all(isinstance(item, str) for item in args)):
        errors.append(f"{prefix}.args must be a list of strings")

    return errors


def validate_graph(graph_path: Path = DEFAULT_GRAPH, schema_path: Path = DEFAULT_SCHEMA) -> dict[str, Any]:
    schema, schema_errors = load_json(schema_path)
    graph, graph_errors = load_json(graph_path)
    errors = schema_errors + graph_errors
    if schema is not None and not isinstance(schema, dict):
        errors.append("schema root must be an object")
    if graph is None:
        return {"ok": False, "errors": errors, "hook_count": 0, "events": []}
    if not isinstance(graph, dict):
        errors.append("hook graph root must be an object")
        return {"ok": False, "errors": errors, "hook_count": 0, "events": []}
    if graph.get("version") != 1:
        errors.append("hook graph version must be 1")
    hooks = graph.get("hooks")
    if not isinstance(hooks, list):
        errors.append("hook graph hooks must be a list")
        hooks = []

    seen_ids: set[str] = set()
    events: set[str] = set()
    for index, hook in enumerate(hooks):
        if not isinstance(hook, dict):
            errors.append(f"hooks[{index}] must be an object")
            continue
        events.add(str(hook.get("event", "")))
        errors.extend(validate_hook(hook, seen_ids, index))

    missing_events = sorted(LEGAL_EVENTS - events)
    for event in missing_events:
        errors.append(f"missing required event in hook graph: {event}")
    return {
        "ok": not errors,
        "errors": errors,
        "hook_count": len(hooks),
        "events": sorted(events),
        "graph": str(graph_path),
        "schema": str(schema_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the SXLB hook graph.")
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    result = validate_graph(Path(args.graph), Path(args.schema))
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
