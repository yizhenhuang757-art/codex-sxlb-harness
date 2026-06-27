#!/usr/bin/env python3
"""State-aware command routing for explicit sxlb control phrases."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from sxlb_reply import is_shijiang_exit, normalize_user_command


COMMANDS = {
    "继续": ("continue", None),
    "暂停": ("pause", None),
    "恢复": ("resume", None),
    "退朝": ("exit_court", None),
    "录案": ("record_case", None),
    "事件簿": ("show_ledger", None),
    "重审": ("review_again", None),
    "会审": ("deliberation", None),
    "国史馆": ("guoshiguan", "国史馆"),
    "起居郎": ("qijulang", "起居郎"),
    "翰林院": ("hanlinyuan", "翰林院"),
    "体检": ("doctor", "sxlb_doctor"),
    "健康检查": ("doctor", "sxlb_doctor"),
    "doctor": ("doctor", "sxlb_doctor"),
    "帮助": ("help", "sxlb_help"),
    "help": ("help", "sxlb_help"),
    "怎么用": ("help", "sxlb_help"),
}


def _unknown(text: str, *, state: str | None) -> dict[str, Any]:
    return {
        "action": "unknown",
        "target": None,
        "payload": text.strip(),
        "state": state,
        "confidence": "low",
    }


def route_command(text: str, *, state: str | None = None) -> dict[str, Any]:
    """Route only explicit control commands; leave complex intent to the model."""
    normalized = normalize_user_command(text)
    if not normalized:
        return _unknown(text, state=state)

    if is_shijiang_exit(text, state):
        return {
            "action": "shijiang_exit",
            "target": "侍讲官",
            "payload": "",
            "state": state,
            "confidence": "high",
        }

    if normalized == "退下":
        return {
            "action": "dismiss_current",
            "target": state or "current",
            "payload": "",
            "state": state,
            "confidence": "high" if state else "medium",
        }

    if normalized == "侍讲官退下":
        return _unknown(text, state=state)

    if normalized in COMMANDS:
        action, target = COMMANDS[normalized]
        return {
            "action": action,
            "target": target,
            "payload": "",
            "state": state,
            "confidence": "high",
        }

    match = re.match(r"^侍讲官\s*(.+)$", text.strip())
    if match and match.group(1).strip():
        return {
            "action": "ask_officer",
            "target": "侍讲官",
            "payload": match.group(1).strip(),
            "state": state,
            "confidence": "high",
        }

    return _unknown(text, state=state)


def main() -> int:
    parser = argparse.ArgumentParser(description="Route explicit sxlb control commands.")
    parser.add_argument("--state", help="Current sxlb lifecycle state or special mode.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    result = route_command(sys.stdin.read(), state=args.state)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"action: {result['action']}")
        print(f"target: {result['target'] or 'n/a'}")
        if result["payload"]:
            print(f"payload: {result['payload']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
