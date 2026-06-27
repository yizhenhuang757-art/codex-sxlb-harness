#!/usr/bin/env python3
"""Manage learning-ledger.jsonl entries for sxlb cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("type", "scope", "source", "confidence", "summary", "promote_to", "stale_when")
VALID_SCOPES = {"case", "project", "agent"}


def _validate_entry(entry: dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in entry or not str(entry[field]).strip():
            raise ValueError(f"learning entry missing field: {field}")
    if str(entry["scope"]).strip() not in VALID_SCOPES:
        raise ValueError(f"invalid scope: {entry['scope']}")
    try:
        confidence = int(entry["confidence"])
    except (TypeError, ValueError) as exc:
        raise ValueError("confidence must be integer 1-10") from exc
    if confidence < 1 or confidence > 10:
        raise ValueError("confidence must be integer 1-10")


def _read_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        item = json.loads(text)
        if isinstance(item, dict):
            entries.append(item)
    return entries


def _write_entries(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(entry, ensure_ascii=False) for entry in entries]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def add_entry(path: Path, entry: dict[str, Any]) -> dict[str, Any]:
    _validate_entry(entry)
    normalized = dict(entry)
    normalized["confidence"] = int(normalized["confidence"])
    normalized.setdefault("status", "active")
    entries = _read_entries(path)
    entries.append(normalized)
    _write_entries(path, entries)
    return normalized


def query_entries(path: Path, *, learning_type: str | None = None, scope: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    entries = _read_entries(path)
    result: list[dict[str, Any]] = []
    for entry in entries:
        if learning_type and str(entry.get("type", "")).strip() != learning_type:
            continue
        if scope and str(entry.get("scope", "")).strip() != scope:
            continue
        if status and str(entry.get("status", "active")).strip() != status:
            continue
        result.append(entry)
    return result


def mark_stale(path: Path, *, learning_type: str | None = None, scope: str | None = None, reason: str = "stale") -> int:
    entries = _read_entries(path)
    updated = 0
    for entry in entries:
        if learning_type and str(entry.get("type", "")).strip() != learning_type:
            continue
        if scope and str(entry.get("scope", "")).strip() != scope:
            continue
        entry["status"] = "stale"
        entry["stale_reason"] = reason
        updated += 1
    _write_entries(path, entries)
    return updated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage learning-ledger.jsonl entries.")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add one learning entry")
    add.add_argument("path", type=Path)
    add.add_argument("--entry", required=True, help="JSON object string for one entry")

    query = sub.add_parser("query", help="Query learning entries")
    query.add_argument("path", type=Path)
    query.add_argument("--type", dest="learning_type")
    query.add_argument("--scope")
    query.add_argument("--status")

    stale = sub.add_parser("stale", help="Mark matching entries as stale")
    stale.add_argument("path", type=Path)
    stale.add_argument("--type", dest="learning_type")
    stale.add_argument("--scope")
    stale.add_argument("--reason", default="stale")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "add":
        added = add_entry(args.path, json.loads(args.entry))
        print(json.dumps(added, ensure_ascii=False))
        return 0
    if args.command == "query":
        rows = query_entries(args.path, learning_type=args.learning_type, scope=args.scope, status=args.status)
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if args.command == "stale":
        count = mark_stale(args.path, learning_type=args.learning_type, scope=args.scope, reason=args.reason)
        print(count)
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
