#!/usr/bin/env python3
"""Report likely redundancy/overhead candidates in the SXLB harness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SXLB_ROOT = Path(__file__).resolve().parents[1]


def candidate(
    area: str,
    symptom: str,
    recommendation: str,
    rationale: str,
    path: str,
) -> dict[str, str]:
    return {
        "area": area,
        "symptom": symptom,
        "recommendation": recommendation,
        "rationale": rationale,
        "path": path,
    }


def audit() -> dict[str, Any]:
    candidates = [
        candidate(
            "user-facing help layer",
            "帮助/怎么用 is useful for onboarding but not on the hot path for the owner",
            "defer",
            "Keep as optional command; do not expand it into more beginner-facing docs during runtime-efficiency work.",
            "scripts/sxlb_help.py",
        ),
        candidate(
            "verbose status explanations",
            "朝堂状态 can invite repeated prose explanation when a compact packet would do",
            "compress",
            "Prefer sxlb_state_packet.py for resume/compact surfaces and keep visible board high-level.",
            "MODE.md",
        ),
        candidate(
            "harness protocol loading",
            "protocols/harness.md is long and should not be loaded for ordinary turns",
            "keep-on-demand",
            "The file already says on-demand; enforce this by using event packets and script-index for concrete commands.",
            "protocols/harness.md",
        ),
        candidate(
            "strict capability health at intake",
            "external-capability-health can cost subprocess time and is only needed when external tools matter",
            "keep-on-demand",
            "Keep it strict-profile only; doctor remains the explicit human-triggered check.",
            "hooks/sxlb-hooks.json",
        ),
        candidate(
            "case artifacts",
            "large case records are durable but expensive to reread after compaction",
            "compress",
            "Generate state-packet.md before compaction and read it before long artifacts on resume.",
            "scripts/sxlb_state_packet.py",
        ),
    ]
    return {
        "ok": True,
        "policy": "advisory-only",
        "summary": "Do not delete governance; move non-hot-path material behind profiles, event packets, and compact state packets.",
        "candidates": candidates,
    }


def render_human(report: dict[str, Any]) -> str:
    lines = [
        "SXLB Harness Redundancy Audit",
        report["summary"],
        "",
    ]
    for item in report["candidates"]:
        lines.append(f"- {item['area']}: {item['recommendation']}")
        lines.append(f"  symptom: {item['symptom']}")
        lines.append(f"  rationale: {item['rationale']}")
        lines.append(f"  path: {item['path']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SXLB harness overhead candidates.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    report = audit()
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
