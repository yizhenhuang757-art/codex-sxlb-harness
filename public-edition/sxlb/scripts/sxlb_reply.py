#!/usr/bin/env python3
"""Generate complete sxlb replies from state data and a reply body."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from sxlb_arrival_hooks import recommend_hooks
from status_board import render_board, validate_board_text


SHIJIANG_STATES = {"侍讲官", "shijiang", "shijiangguan"}
SHIJIANG_EXIT_TEXTS = {"退下", "侍讲官退下"}


def normalize_user_command(text: str) -> str:
    """Normalize a short user command for script-level command detection."""
    normalized = text.strip()
    normalized = re.sub(r"\s+", "", normalized)
    normalized = normalized.strip("。.!！?？；;，,、")
    return normalized


def is_shijiang_state(data: dict[str, Any]) -> bool:
    value = str(data.get("state") or data.get("mode") or data.get("variant") or "")
    return value.strip().lower() in SHIJIANG_STATES or value.strip() in SHIJIANG_STATES


def is_shijiang_exit(text: str, state: dict[str, Any] | str | None = None) -> bool:
    """Return true only when an exit command is issued inside 侍讲官 state."""
    if state is None:
        return False
    state_data = {"state": state} if isinstance(state, str) else state
    if not is_shijiang_state(state_data):
        return False
    return normalize_user_command(text) in SHIJIANG_EXIT_TEXTS


def _clean_body(body: str) -> str:
    return body.strip()


def build_reply(data: dict[str, Any], body: str, *, variant: str | None = None) -> str:
    """Build a full user-facing reply from state data and body text."""
    clean_body = _clean_body(body)
    if is_shijiang_state(data):
        reply = f"侍讲官回奏\n\n{clean_body}\n"
        return reply

    board = render_board(data, variant=variant)
    reply = f"{board}\n## 回奏\n\n{clean_body}\n"
    ok, errors = validate_board_text(reply, variant=variant)
    if not ok:
        raise ValueError("; ".join(errors))
    return reply


def build_reply_packet(data: dict[str, Any], body: str, *, variant: str | None = None) -> dict[str, Any]:
    """Build a reply plus department-owned arrival hooks for the declared state."""
    reply = build_reply(data, body, variant=variant)
    hooks = [] if is_shijiang_state(data) else recommend_hooks(data)
    return {"reply": reply, "arrival_hooks": hooks}


def _read_body(args: argparse.Namespace, stdin_packet: dict[str, Any] | None = None) -> str:
    if args.body_stdin:
        if stdin_packet is None:
            raise ValueError("--body-stdin requires stdin JSON with `state` and `body` fields")
        return str(stdin_packet.get("body", ""))
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    if args.body is not None:
        return args.body
    return ""


def _read_state(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any] | None]:
    packet = json.load(sys.stdin)
    if args.body_stdin:
        if not isinstance(packet, dict) or "state" not in packet:
            raise ValueError("--body-stdin stdin JSON must be an object with `state` and `body` fields")
        state = packet.get("state")
        if not isinstance(state, dict):
            raise ValueError("--body-stdin `state` must be an object")
        return state, packet
    if not isinstance(packet, dict):
        raise ValueError("stdin JSON state must be an object")
    return packet, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sxlb replies from JSON state and body text.")
    parser.add_argument("--body", help="Reply body text. Use --body-file or --body-stdin for multiline bodies.")
    parser.add_argument("--body-file", help="Path to a UTF-8 Markdown body file.")
    parser.add_argument(
        "--body-stdin",
        action="store_true",
        help="Read stdin as JSON object with `state` and `body`, avoiding temporary body files.",
    )
    parser.add_argument("--state", help="Current lifecycle state for command detection.")
    parser.add_argument("--variant", help="Force a status board variant for ordinary replies.")
    parser.add_argument(
        "--detect-shijiang-exit",
        action="store_true",
        help="Read user input from stdin and report whether it exits 侍讲官.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON for detection or errors.")
    args = parser.parse_args()

    if args.detect_shijiang_exit:
        result = {"exit": is_shijiang_exit(sys.stdin.read(), args.state)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    try:
        data, stdin_packet = _read_state(args)
        body = _read_body(args, stdin_packet)
        if args.json:
            print(json.dumps(build_reply_packet(data, body, variant=args.variant), ensure_ascii=False, indent=2))
        else:
            print(build_reply(data, body, variant=args.variant), end="")
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
