#!/usr/bin/env python3
"""Route tiny explicit sxlb events to before/at-step script gates."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

from sxlb_arrival_hooks import recommend_hooks as recommend_arrival_hooks

PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
FIELD_RE = re.compile(r"^- ([^：\n]+)：\s*(.+)$", re.MULTILINE)
PLAN_READY_FIELDS = (
    "目标",
    "不做什么",
    "成功标准",
    "主任务",
    "子任务",
    "验证方式",
    "任务类别",
    "推荐链路",
    "主要官署",
    "能力召回",
)


def parse_event_text(text: str) -> dict[str, Any]:
    """Parse a low-token event line such as `zhongshu.plan_ready case=/tmp/case`."""
    tokens = shlex.split(text.strip())
    if not tokens:
        return {}
    data: dict[str, Any] = {"event": tokens[0]}
    for token in tokens[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def build_event_packet(raw: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(raw, dict):
        return dict(raw)
    stripped = raw.strip()
    if not stripped:
        return {}
    if stripped.startswith("{"):
        return json.loads(stripped)
    return parse_event_text(stripped)


def _hook(
    name: str,
    office: str,
    timing: str,
    reason: str,
    command_hint: str,
    *,
    blocking: bool = True,
) -> dict[str, Any]:
    return {
        "hook": name,
        "office": office,
        "timing": timing,
        "blocking": blocking,
        "reason": reason,
        "command_hint": command_hint,
    }


def _semantic_bridge_hook(office: str, phase: str) -> dict[str, Any]:
    return _hook(
        "capability-semantic-bridge",
        f"{office}/吏部",
        "at-ready",
        "agent must spend a small amount of reasoning to translate user intent into normalized capability keywords before deterministic clan-first capability recall",
        f"derive semantic_keywords=[...] then pass them as repeatable --semantic-keyword values to recall_capabilities.py --phase {phase} --office {office}",
        blocking=False,
    )


def _arrival_payload(data: dict[str, Any]) -> dict[str, Any]:
    payload = dict(data)
    payload.setdefault("phase", "completion")
    payload.setdefault("state", "门下复核")
    return payload


def _parse_fields(text: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in FIELD_RE.findall(text)}


def _filled(value: str | None) -> bool:
    if value is None:
        return False
    stripped = value.strip()
    return bool(stripped) and not PLACEHOLDER_RE.search(stripped)


def check_plan_ready(case_dir: Path) -> dict[str, Any]:
    """Check the 中书方案 at the at-ready boundary before review/dispatch."""
    plan_path = case_dir / "zhongshu-plan.md"
    result: dict[str, Any] = {
        "policy": "explicit-event",
        "event": "zhongshu.plan_ready",
        "hook": "plan-precheck",
        "timing": "at-ready",
        "blocking": True,
        "case": str(case_dir),
        "artifact": "zhongshu-plan.md",
        "ok": False,
        "errors": [],
    }
    if not plan_path.exists():
        result["errors"].append("missing zhongshu-plan.md")
        return result

    text = plan_path.read_text(encoding="utf-8")
    fields = _parse_fields(text)
    for field in PLAN_READY_FIELDS:
        if not _filled(fields.get(field)):
            result["errors"].append(f"missing or placeholder field: {field}")
    result["ok"] = not result["errors"]
    return result


def route_event(data: dict[str, Any]) -> dict[str, Any]:
    """Map an explicit model event to mandatory hook scripts.

    Events are state gates, not post-hoc logs. They fire before entering a station
    or exactly when an office declares an artifact ready.
    """
    event = str(data.get("event", "")).strip()
    packet: dict[str, Any] = {
        "policy": "explicit-event",
        "event": event,
        "case": data.get("case", ""),
        "timing": "none",
        "hooks": [],
    }

    if event == "reply.substantive":
        packet["timing"] = "before-emit"
        packet["hooks"] = [
            _hook(
                "reply-generation",
                "吏部",
                "before-emit",
                "ordinary substantive sxlb replies must be generated or checked before the user sees them",
                "sxlb_reply.py --body <回奏 body>  # use --json when arrival_hooks are needed",
            )
        ]
        return packet

    if event in {"taizi.intake", "taizi.intake_ready"}:
        packet["event"] = "taizi.intake"
        packet["timing"] = "at-ready"
        packet["hooks"] = [
            _semantic_bridge_hook("太子", "intake"),
            _hook(
                "capability-recall",
                "太子/吏部",
                "at-ready",
                "intake should surface 0-3 likely skill families without granting execution authority",
                "recall_capabilities.py --text <user-text> --semantic-keyword <keyword> --phase intake --office 太子 --json",
                blocking=False,
            )
        ]
        return packet

    if event == "menxia.review_ready":
        packet["timing"] = "at-ready"
        arrival = _arrival_payload(data)
        arrival["phase"] = "review"
        packet["hooks"] = recommend_arrival_hooks(arrival)
        for hook in packet["hooks"]:
            hook["timing"] = "at-ready"
            hook["blocking"] = False
        return packet

    if event == "zhongshu.plan_ready":
        packet["timing"] = "at-ready"
        packet["hooks"] = [
            _semantic_bridge_hook("中书省", "planning"),
            _hook(
                "capability-recall",
                "中书省/吏部",
                "at-ready",
                "planning should record candidate skill clans and families before office/skill mapping",
                "recall_capabilities.py --text <user-text> --semantic-keyword <keyword> --phase planning --office 中书省 --json",
                blocking=False,
            ),
            _hook(
                "plan-precheck",
                "中书省/门下省",
                "at-ready",
                "a declared 中书方案 must expose plan shape before review or dispatch",
                "sxlb_event_router.py --check-plan-ready <case-dir> --json",
            )
        ]
        return packet

    if event == "shangshu.dispatch_ready":
        packet["timing"] = "at-ready"
        packet["hooks"] = [
            _semantic_bridge_hook("尚书省", "dispatch"),
            _hook(
                "capability-recall",
                "尚书省/吏部",
                "at-ready",
                "dispatch should retain recalled clan/family candidates while 六部 execution remains allowlist-bound",
                "recall_capabilities.py --text <user-text> --semantic-keyword <keyword> --phase dispatch --office 尚书省 --json",
                blocking=False,
            ),
            _hook(
                "dispatch-precheck",
                "尚书省/门下省",
                "at-ready",
                "a declared dispatch plan must be checked before execution begins",
                "shangshu_dispatch.py <case-dir> --json",
            )
        ]
        return packet

    if event == "menxia.completion_ready":
        packet["timing"] = "at-ready"
        packet["hooks"] = recommend_arrival_hooks(_arrival_payload(data))
        for hook in packet["hooks"]:
            hook["timing"] = "at-ready"
            hook["blocking"] = True
        return packet

    if event == "case.pre_compact":
        packet["timing"] = "before-compact"
        packet["hooks"] = [
            _hook(
                "state-packet",
                "礼部/吏部",
                "before-compact",
                "context compaction should preserve a compact resume packet so the next run reads a small state surface before long case artifacts",
                "sxlb_state_packet.py <case-dir> --write <case-dir>/state-packet.md",
                blocking=False,
            )
        ]
        return packet

    if event == "case.close":
        packet["timing"] = "at-close"
        packet["hooks"] = [
            _hook(
                "completion-and-records-check",
                "门下省/礼部/吏部",
                "at-close",
                "case close should include completion review, verification evidence, records routing, and restart/catalog disposition",
                "harness_hooks.py completion <case-dir> plus records-routing/restart checks",
            )
        ]
        return packet

    packet["unknown_event"] = event
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Route tiny explicit sxlb events to mandatory hook scripts.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--check-plan-ready", metavar="CASE_DIR", help="Run the 中书 at-ready plan precheck.")
    args = parser.parse_args()

    if args.check_plan_ready:
        result = check_plan_ready(Path(args.check_plan_ready))
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"ok: {str(result['ok']).lower()}")
            for error in result["errors"]:
                print(f"- {error}")
        return 0 if result["ok"] else 1

    packet = route_event(build_event_packet(sys.stdin.read()))
    if args.json_output:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(f"event: {packet.get('event', '')}")
        print(f"timing: {packet.get('timing', '')}")
        if not packet.get("hooks"):
            print("hooks: none")
        for hook in packet.get("hooks", []):
            print(f"- {hook['hook']} ({hook['timing']}): {hook['command_hint']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
