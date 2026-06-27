#!/usr/bin/env python3
"""Validate that an active sxlb reply starts with a visible status board."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from status_board import starts_with_board, validate_board_text


ALLOWED_OMISSIONS = {"exit-confirmation", "social", "user-suppressed"}


def first_nonblank_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def validate_response_board(
    text: str,
    *,
    active: bool = True,
    omission_reason: str | None = None,
) -> tuple[bool, list[str]]:
    """Return whether a drafted reply satisfies the active-sxlb board rule."""
    errors: list[str] = []
    if not active:
        return True, errors

    if omission_reason:
        if omission_reason in ALLOWED_OMISSIONS:
            return True, errors
        errors.append(f"unknown omission reason: {omission_reason}")
        return False, errors

    ok, board_errors = validate_board_text(text)
    if not ok:
        errors.extend(board_errors)

    return not errors, errors


def _read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check active-sxlb reply board preflight.")
    parser.add_argument("path", nargs="?", help="Draft reply path. Reads stdin when omitted.")
    parser.add_argument("--inactive", action="store_true", help="Treat the reply as outside active sxlb mode.")
    parser.add_argument(
        "--allow-omission",
        choices=sorted(ALLOWED_OMISSIONS),
        help="Allowed reason to omit the board.",
    )
    parser.add_argument("--json", action="store_true", help="Print a JSON result.")
    args = parser.parse_args()

    ok, errors = validate_response_board(
        _read_input(args.path),
        active=not args.inactive,
        omission_reason=args.allow_omission,
    )
    if args.json:
        print(json.dumps({"ok": ok, "errors": errors}, ensure_ascii=False, indent=2))
    elif not ok:
        for error in errors:
            print(error, file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
