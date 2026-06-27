#!/usr/bin/env python3
"""Scan external skill/prompt material for deceptive Unicode controls."""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Iterable


BIDI_CONTROLS = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A))
ZERO_WIDTH = {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF}
TAG_CHARS = set(range(0xE0000, 0xE0080))
VARIATION_SELECTORS = set(range(0xFE00, 0xFE10)) | set(range(0xE0100, 0xE01F0))


def iter_files(paths: list[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    yield child
        elif path.is_file():
            yield path


def category_for(char: str) -> str | None:
    code = ord(char)
    if code in BIDI_CONTROLS:
        return "bidi-control"
    if code in ZERO_WIDTH:
        return "zero-width"
    if code in TAG_CHARS:
        return "tag-smuggling"
    if code in VARIATION_SELECTORS:
        return "variation-selector"
    return None


def scan_text(text: str, path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for column, char in enumerate(line, start=1):
            category = category_for(char)
            if not category:
                continue
            findings.append(
                {
                    "file": str(path),
                    "line": line_no,
                    "column": column,
                    "code_point": f"U+{ord(char):04X}",
                    "name": unicodedata.name(char, "UNKNOWN"),
                    "category": category,
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
    parser = argparse.ArgumentParser(description="Scan files for deceptive Unicode controls.")
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
            print(f"- {finding['file']}:{finding['line']}:{finding['column']} {finding['code_point']} {finding['category']}")
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    if args.warn_only:
        return 0
    return 1 if result["findings"] or result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
