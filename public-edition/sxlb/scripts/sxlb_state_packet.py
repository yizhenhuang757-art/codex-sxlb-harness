#!/usr/bin/env python3
"""Generate a compact resume/state packet for an SXLB case."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MAX_ITEMS = 5
MAX_VALUE_CHARS = 280


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def clip(value: str, limit: int = MAX_VALUE_CHARS) -> str:
    clean = re.sub(r"\s+", " ", value).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def first_field(text: str, names: list[str]) -> str:
    for name in names:
        match = re.search(rf"^- {re.escape(name)}[：:]\s*(.+)$", text, re.MULTILINE)
        if match:
            return clip(match.group(1))
    return ""


def bullet_values(text: str, *, patterns: list[str], limit: int = MAX_ITEMS, newest_first: bool = False) -> list[str]:
    values: list[str] = []
    lines = text.splitlines()
    if newest_first:
        lines = list(reversed(lines))
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        body = stripped[2:].strip()
        if any(re.search(pattern, body, re.I) for pattern in patterns):
            values.append(clip(body))
        if len(values) >= limit:
            break
    if newest_first:
        values.reverse()
    return values


def markdown_files(case_dir: Path) -> list[str]:
    return sorted(path.name for path in case_dir.glob("*.md") if path.is_file())


def latest_section(text: str) -> str:
    matches = list(re.finditer(r"^#{2,6}\s+.+$", text, re.MULTILINE))
    if not matches:
        return text
    return text[matches[-1].start() :]


def collect_packet(case_dir: Path) -> dict[str, Any]:
    case_text = read_text(case_dir / "case.md")
    restart_text = read_text(case_dir / "restart.md")
    verification_text = read_text(case_dir / "verification.md")
    implementation_text = read_text(case_dir / "implementation-notes.md")
    event_text = read_text(case_dir / "event-ledger.md")

    goal = first_field(case_text, ["用户目标", "目标", "任务"]) or first_field(restart_text, ["Current Goal"])
    state = first_field(case_text, ["当前状态", "下一站", "当前建议链路"]) or first_field(restart_text, ["Current Phase"])
    next_step = first_field(case_text, ["下一站"]) or first_field(restart_text, ["Next Legal Move", "下一步"])
    if not next_step:
        next_candidates = bullet_values(restart_text, patterns=[r"下一步", r"next", r"太子", r"中书", r"门下"], limit=2)
        next_step = next_candidates[0] if next_candidates else ""

    latest_verification = latest_section(verification_text)
    latest_implementation = latest_section(implementation_text)
    verification = bullet_values(
        latest_verification,
        patterns=[r"OK", r"Ran \d+ tests", r"验证", r"全量", r"绿灯", r"pass"],
        newest_first=True,
    )
    files_changed = bullet_values(
        latest_implementation,
        patterns=[r"`[^`]+`", r"新增", r"更新", r"修复", r"重新生成"],
        newest_first=True,
    )
    if not files_changed:
        files_changed = markdown_files(case_dir)[:MAX_ITEMS]

    open_risks = bullet_values(
        "\n".join([restart_text, latest_verification, event_text]),
        patterns=[r"当前提示项", r"未完成", r"未验证", r"unknown", r"WARN", r"待决"],
        newest_first=True,
    )

    packet = {
        "version": 1,
        "case": str(case_dir),
        "goal": goal or "unknown",
        "state": state or "unknown",
        "next_step": next_step or "unknown",
        "verification": verification[:MAX_ITEMS],
        "files_changed": files_changed[:MAX_ITEMS],
        "open_risks": open_risks[:MAX_ITEMS],
        "read_first": [name for name in ["state-packet.md", "restart.md", "verification.md", "implementation-notes.md"] if (case_dir / name).exists() or name == "state-packet.md"],
    }
    packet["budget"] = {"packet_chars": len(json.dumps(packet, ensure_ascii=False))}
    return packet


def render_markdown(packet: dict[str, Any]) -> str:
    def lines_for(items: list[str]) -> list[str]:
        return [f"- {item}" for item in items] if items else ["- none"]

    lines = [
        "# SXLB State Packet",
        "",
        f"- Case: `{packet['case']}`",
        f"- Goal: {packet['goal']}",
        f"- State: {packet['state']}",
        f"- Next Step: {packet['next_step']}",
        "",
        "## Verification",
        *lines_for(packet["verification"]),
        "",
        "## Files Changed",
        *lines_for(packet["files_changed"]),
        "",
        "## Open Risks",
        *lines_for(packet["open_risks"]),
        "",
        "## Read First",
        *[f"- `{item}`" for item in packet["read_first"]],
        "",
        f"_packet_chars: {packet['budget']['packet_chars']}_",
        "",
    ]
    return "\n".join(lines)


def case_dir_from_stdin() -> Path | None:
    text = sys.stdin.read().strip()
    if not text:
        return None
    if text.startswith("{"):
        data = json.loads(text)
        if not isinstance(data, dict):
            return None
        value = data.get("case") or data.get("case_dir")
        return Path(str(value)) if value else None
    for token in text.split():
        if token.startswith("case="):
            return Path(token.split("=", 1)[1])
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compact SXLB state/resume packet.")
    parser.add_argument("case_dir", type=Path, nargs="?")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--write", type=Path, help="Write markdown packet to this path.")
    parser.add_argument("--write-default", action="store_true", help="Write <case_dir>/state-packet.md.")
    args = parser.parse_args()

    case_dir = args.case_dir or case_dir_from_stdin()
    if not case_dir:
        print("missing case_dir", file=sys.stderr)
        return 1

    packet = collect_packet(case_dir)
    write_path = args.write
    if args.write_default:
        write_path = case_dir / "state-packet.md"
    if write_path:
        write_path.write_text(render_markdown(packet), encoding="utf-8")
        print(str(write_path))
    elif args.json_output:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
