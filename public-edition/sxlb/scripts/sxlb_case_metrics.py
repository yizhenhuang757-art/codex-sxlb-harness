#!/usr/bin/env python3
"""Append SXLB runtime metrics inside a case package only."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


METRICS_FILE = "runtime-metrics.jsonl"


def load_event() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("metrics input must be a JSON object")
    return data


def append_metric(payload: dict[str, Any]) -> dict[str, Any]:
    case_value = str(payload.get("case", "")).strip()
    if not case_value:
        return {"ok": True, "status": "skipped", "reason": "no case"}
    case_dir = Path(case_value)
    if not case_dir.exists() or not case_dir.is_dir():
        return {"ok": True, "status": "skipped", "reason": "case missing", "case": case_value}

    entry = {
        "time": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "event": payload.get("event", ""),
        "profile": payload.get("profile", ""),
        "risk": payload.get("risk", {}),
        "steps": [
            {"id": item.get("id"), "status": item.get("status"), "ok": item.get("ok")}
            for item in payload.get("steps", [])
        ],
        "quality_plan": payload.get("quality_plan", {}),
        "state_packet_chars": payload.get("state_packet_chars"),
    }
    path = case_dir / METRICS_FILE
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return {"ok": True, "status": "written", "path": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Append runtime metrics inside an SXLB case package.")
    parser.add_argument("command", choices=("append",))
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = append_metric(load_event())
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
