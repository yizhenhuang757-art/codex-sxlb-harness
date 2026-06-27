#!/usr/bin/env python3
"""Scan external skill/prompt material for dangerous or overreaching instructions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

from sxlb_guard import find_dangerous_command


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("instruction-override", re.compile(r"\b(ignore|disregard|override)\b.{0,80}\b(previous|prior|system|developer|higher-priority)\b", re.I)),
    ("instruction-override", re.compile(r"(忽略|覆盖|无视).{0,40}(系统|开发者|上级|高优先级|之前)", re.I)),
    ("credential-or-browser-state", re.compile(r"\b(cookie|cookies|token|tokens|credential|credentials|secret|secrets|browser profile|login state)\b", re.I)),
    ("credential-or-browser-state", re.compile(r"(读取|导出|窃取|复制).{0,40}(cookie|token|密钥|凭证|登录态|浏览器)", re.I)),
    ("safeguard-disable", re.compile(r"\b(disable|bypass|turn off)\b.{0,80}\b(safety|guardrail|approval|review|checks?)\b", re.I)),
    ("unauthorized-external-action", re.compile(r"\b(auto|automatically)\b.{0,60}\b(push|post|comment|purchase|buy|book|submit|upload)\b", re.I)),
    ("unauthorized-config-mutation", re.compile(r"\b(modify|rewrite|change)\b.{0,80}\b(MCP config|github permissions|agent reach config|browser settings)\b", re.I)),
)


def iter_files(paths: list[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    yield child
        elif path.is_file():
            yield path


def line_col(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    return line, offset - line_start + 1


def scan_text(text: str, path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    dangerous = find_dangerous_command(text)
    if dangerous:
        index = text.lower().find(dangerous.lower())
        line, column = line_col(text, max(index, 0))
        findings.append(
            {
                "file": str(path),
                "line": line,
                "column": column,
                "category": "destructive-command",
                "match": dangerous,
                "status": "block",
            }
        )
    for category, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line, column = line_col(text, match.start())
            findings.append(
                {
                    "file": str(path),
                    "line": line,
                    "column": column,
                    "category": category,
                    "match": match.group(0),
                    "status": "warn",
                }
            )
    return findings


def scan_paths(paths: list[Path]) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    errors: list[str] = []
    scanned = 0
    for path in iter_files(paths):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{path}: not valid utf-8: {exc}")
            continue
        except OSError as exc:
            errors.append(f"{path}: {exc}")
            continue
        scanned += 1
        findings.extend(scan_text(text, path))
    return {"ok": not findings and not errors, "files_scanned": scanned, "findings": findings, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan external skill/prompt material for dangerous instructions.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--warn-only", action="store_true")
    args = parser.parse_args()

    result = scan_paths([Path(item) for item in args.paths])
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        for finding in result["findings"]:
            print(f"- {finding['file']}:{finding['line']}:{finding['column']} {finding['category']}: {finding['match']}")
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    if args.warn_only:
        return 0
    return 1 if result["findings"] or result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
