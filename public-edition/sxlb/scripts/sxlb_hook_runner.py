#!/usr/bin/env python3
"""Run SXLB hook graph entries for one explicit governed-boundary event."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from validate_sxlb_hooks import DEFAULT_GRAPH, SXLB_ROOT, validate_graph


LEGAL_PROFILES = {"minimal", "standard", "strict"}
DEFAULT_MAX_INPUT_BYTES = 65536


def read_input(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    if args.event:
        return args.event, {"truncated": False, "bytes_read": len(args.event.encode("utf-8")), "source": "--event"}
    limit = args.max_input_bytes
    raw = sys.stdin.buffer.read(limit + 1)
    truncated = len(raw) > limit
    if truncated:
        raw = raw[:limit]
    return raw.decode("utf-8", errors="replace"), {
        "truncated": truncated,
        "bytes_read": len(raw),
        "max_input_bytes": limit,
        "source": "stdin",
    }


def parse_event_packet(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        return {}
    if stripped.startswith("{"):
        data = json.loads(stripped)
        if not isinstance(data, dict):
            raise ValueError("event JSON must be an object")
        return data
    return {"event": stripped.split()[0], "raw": stripped}


def load_hooks(graph_path: Path) -> list[dict[str, Any]]:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    return list(graph.get("hooks", []))


def disabled_hooks() -> set[str]:
    raw = os.environ.get("SXLB_DISABLED_HOOKS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def current_profile() -> str:
    profile = os.environ.get("SXLB_PROFILE", "standard").strip().lower() or "standard"
    return profile if profile in LEGAL_PROFILES else "standard"


def script_command(hook: dict[str, Any]) -> list[str]:
    script = (SXLB_ROOT / hook["script"]).resolve()
    return [sys.executable, str(script), *hook.get("args", [])]


def select_hooks(hooks: list[dict[str, Any]], event: str, profile: str, disabled: set[str]) -> list[dict[str, Any]]:
    return [
        hook
        for hook in hooks
        if hook.get("event") == event and profile in hook.get("profiles", []) and hook.get("id") not in disabled
    ]


def run_hook(hook: dict[str, Any], event_text: str, *, dry_run: bool) -> dict[str, Any]:
    command = script_command(hook)
    base = {
        "id": hook["id"],
        "office": hook["office"],
        "blocking": hook["blocking"],
        "timeout_seconds": hook["timeout_seconds"],
        "script": hook["script"],
        "args": hook.get("args", []),
        "command": command,
        "executed": False,
    }
    if dry_run:
        return {**base, "status": "pass", "returncode": None, "stdout": "", "stderr": ""}
    try:
        result = subprocess.run(
            command,
            input=event_text,
            text=True,
            capture_output=True,
            check=False,
            timeout=hook["timeout_seconds"],
        )
    except subprocess.TimeoutExpired as exc:
        return {
            **base,
            "executed": True,
            "status": "error" if hook["blocking"] else "warn",
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": f"hook timeout after {hook['timeout_seconds']}s",
        }

    status = "pass"
    if result.returncode != 0:
        status = "block" if hook["blocking"] else "warn"
    parsed_status = None
    try:
        parsed = json.loads(result.stdout) if result.stdout.strip().startswith("{") else None
        if isinstance(parsed, dict):
            parsed_status = parsed.get("status")
    except json.JSONDecodeError:
        parsed_status = None
    if parsed_status == "block":
        status = "block"
    elif parsed_status == "require-review":
        status = "block" if hook["blocking"] else "warn"
    elif parsed_status in {"warn", "pass", "error"}:
        status = parsed_status

    return {
        **base,
        "executed": True,
        "status": status,
        "raw_status": parsed_status,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def build_result(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    validation = validate_graph(Path(args.graph))
    if not validation["ok"]:
        return {"ok": False, "status": "error", "errors": validation["errors"], "hooks": []}, 1

    event_text, input_meta = read_input(args)
    packet = parse_event_packet(event_text)
    event = str(packet.get("event", "")).strip()
    if not event:
        return {"ok": False, "status": "error", "errors": ["missing event"], "hooks": [], "input": input_meta}, 1

    profile = current_profile()
    disabled = disabled_hooks()
    hooks = select_hooks(load_hooks(Path(args.graph)), event, profile, disabled)
    hook_results = [run_hook(hook, event_text, dry_run=args.dry_run) for hook in hooks]
    statuses = {item["status"] for item in hook_results}
    ok = not (statuses & {"block", "error"})
    exit_code = 0 if ok else 2
    return {
        "ok": ok,
        "event": event,
        "profile": profile,
        "dry_run": args.dry_run,
        "disabled_hooks": sorted(disabled),
        "input": input_meta,
        "hooks": hook_results,
    }, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SXLB hook graph checks for one event.")
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--event", help="Event packet or event name. Defaults to stdin.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--max-input-bytes", type=int, default=DEFAULT_MAX_INPUT_BYTES)
    args = parser.parse_args()

    result, exit_code = build_result(args)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result.get('ok')).lower()}")
        for hook in result.get("hooks", []):
            print(f"- {hook['id']}: {hook['status']}")
        for error in result.get("errors", []):
            print(f"- {error}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
