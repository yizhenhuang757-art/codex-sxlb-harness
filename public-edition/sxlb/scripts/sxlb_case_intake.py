#!/usr/bin/env python3
"""Advise whether to reuse an sxlb worklog before creating a new case."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


RECALL_SCRIPT = Path("$CODEX_SKILLS_HOME/guoshiguan-recall/scripts/recall.py")


def parse_recall_json(text: str) -> dict[str, Any]:
    payload = json.loads(text)
    if "matches" not in payload or not isinstance(payload["matches"], list):
        raise ValueError("recall payload must contain a matches list")
    return payload


def _best_match(recall_payload: dict[str, Any]) -> dict[str, Any] | None:
    matches = recall_payload.get("matches") or []
    if not matches:
        return None
    return matches[0]


def _strong_reuse_match(match: dict[str, Any] | None) -> bool:
    if not match:
        return False
    return match.get("confidence") == "high" and int(match.get("score") or 0) >= 18


def advise_case_action(
    query: str,
    *,
    current_case: str | None = None,
    recall_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Advise `use_current`, `reuse`, or `create` without making the final judgment."""
    if current_case:
        return {
            "action": "use_current",
            "case": current_case,
            "first_read": None,
            "recall_required": False,
            "reason": "current case is already active",
        }
    if recall_payload is None:
        raise ValueError("recall payload is required when no current case is active")

    match = _best_match(recall_payload)
    if _strong_reuse_match(match):
        return {
            "action": "reuse",
            "case": match.get("project"),
            "first_read": match.get("first_read"),
            "recall_required": True,
            "reason": "high-confidence Guoshiguan match found before case creation",
        }
    return {
        "action": "create",
        "case": None,
        "first_read": None,
        "recall_required": True,
        "reason": "no high-confidence Guoshiguan match found",
    }


def run_recall(query: str, *, limit: int = 5) -> dict[str, Any]:
    completed = subprocess.run(
        ["python3", str(RECALL_SCRIPT), query, "--limit", str(limit), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "recall failed")
    return parse_recall_json(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Guoshiguan recall before creating an sxlb case.")
    parser.add_argument("--query", required=True, help="Current task or user request.")
    parser.add_argument("--current-case", help="Existing active case path, if any.")
    parser.add_argument("--recall-json-file", type=Path, help="Use a precomputed recall JSON payload.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    try:
        recall_payload = None
        if not args.current_case:
            if args.recall_json_file:
                recall_payload = parse_recall_json(args.recall_json_file.read_text(encoding="utf-8"))
            else:
                recall_payload = run_recall(args.query, limit=args.limit)
        result = advise_case_action(args.query, current_case=args.current_case, recall_payload=recall_payload)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"action: {result['action']}")
            print(f"case: {result['case'] or 'n/a'}")
            print(f"reason: {result['reason']}")
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
