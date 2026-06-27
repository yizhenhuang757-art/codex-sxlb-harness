#!/usr/bin/env python3
"""Low-token action dispatcher for SXLB hot-path checks."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from harness_hooks import check_completion, check_pre_action
from sxlb_risk_scorer import score_event


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
LEGAL_PROFILES = {"minimal", "standard", "strict", "auto"}


def current_profile() -> str:
    profile = os.environ.get("SXLB_PROFILE", "standard").strip().lower() or "standard"
    return profile if profile in LEGAL_PROFILES else "standard"


def load_event() -> dict[str, Any]:
    text = sys.stdin.read().strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("dispatcher input must be a JSON object")
    return data


def step(step_id: str, ok: bool, status: str, *, reason: str = "", data: Any | None = None) -> dict[str, Any]:
    return {
        "id": step_id,
        "ok": ok,
        "status": status,
        "reason": reason,
        "data": data if data is not None else {},
    }


def run_gateguard(event: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "action": event.get("action", event.get("event", "pre_action")),
        "paths": event.get("paths") or event.get("write_paths") or [],
        "command": event.get("command", ""),
        "fact_package": event.get("fact_package", {}),
    }
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "sxlb_gateguard.py"), "--json"],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    ok = data.get("status") in {"pass", "warn"} or data.get("ok") is True
    status = str(data.get("status") or ("pass" if ok else "block"))
    return step("gateguard", ok, status, data=data)


def run_config_protection(event: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "case": event.get("case", ""),
        "paths": event.get("paths") or event.get("write_paths") or [],
        "fact_package": event.get("fact_package", {}),
        "change_plan_id": event.get("change_plan_id", ""),
    }
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "sxlb_config_protection.py"), "--json"],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        data = {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    ok = data.get("status") in {"pass", "warn"} or data.get("ok") is True
    status = str(data.get("status") or ("pass" if ok else "block"))
    return step("config-protection", ok, status, data=data)


def dispatch_pre_action(event: dict[str, Any]) -> list[dict[str, Any]]:
    case_dir = Path(str(event.get("case", "")))
    steps = [run_gateguard(event), run_config_protection(event)]
    if case_dir.exists():
        result = check_pre_action(
            case_dir,
            office=event.get("office"),
            branch_id=event.get("branch_id"),
            command=event.get("command"),
            write_paths=list(event.get("write_paths") or []),
            approval_evidence=event.get("approval_evidence"),
        ).to_dict()
        steps.append(step("pre-action-scope", bool(result["ok"]), "pass" if result["ok"] else "block", data=result))
    else:
        steps.append(step("pre-action-scope", True, "skipped", reason="case missing or not provided"))
    return steps


def quality_gate_plan(event: dict[str, Any]) -> dict[str, Any]:
    touched = [str(item) for item in event.get("touched_files") or event.get("write_paths") or []]
    commands: list[dict[str, str]] = []
    if any("sxlb-hooks" in path or "/hooks/" in path for path in touched):
        commands.append({
            "reason": "hook graph changed",
            "command": "python3 $SXLB_HOME/scripts/validate_sxlb_hooks.py --json",
        })
    if any(path.endswith(".py") and "/scripts/" in path for path in touched):
        commands.append({
            "reason": "SXLB script changed",
            "command": "PYTHONPATH=$SXLB_HOME/scripts:$SXLB_HOME/tests python3 -m unittest discover -s $SXLB_HOME/tests",
        })
    if any("skill-inventory" in path or "skill-clans" in path or "allowlist.md" in path for path in touched):
        commands.append({
            "reason": "skill governance changed",
            "command": "PYTHONPATH=$SXLB_HOME/scripts:$SXLB_HOME/tests python3 $SXLB_HOME/tests/test_skill_inventory.py",
        })
    if not commands:
        commands.append({"reason": "default completion check", "command": "python3 $SXLB_HOME/scripts/sxlb_doctor.py"})
    return {"commands": commands, "touched_files": touched}


def dispatch_completion_ready(event: dict[str, Any], profile: str) -> list[dict[str, Any]]:
    if profile == "minimal":
        return [
            step(
                "completion-quality-gate",
                True,
                "skipped",
                reason="minimal profile",
                data={"suggested_next": "run standard profile if files changed or completion claim is high-risk"},
            )
        ]
    case_dir = Path(str(event.get("case", "")))
    if not case_dir.exists():
        return [step("completion-quality-gate", False, "error", reason="case missing")]
    result = check_completion(case_dir, phase=str(event.get("phase", "completion"))).to_dict()
    return [step("completion-quality-gate", bool(result["ok"]), "pass" if result["ok"] else "block", data=result)]


def dispatch_case_resume(event: dict[str, Any]) -> list[dict[str, Any]]:
    case_dir = Path(str(event.get("case", "")))
    packet = case_dir / "state-packet.md"
    if not packet.exists():
        return [
            step(
                "resume-packet",
                False,
                "warn",
                reason="state-packet.md missing",
                data={
                    "instruction_policy": "historical-reference-only",
                    "read_first": ["restart.md", "verification.md", "implementation-notes.md"],
                },
            )
        ]
    text = packet.read_text(encoding="utf-8")
    return [
        step(
            "resume-packet",
            True,
            "pass",
            data={
                "instruction_policy": "historical-reference-only",
                "read_first": ["state-packet.md", "restart.md", "verification.md", "implementation-notes.md"],
                "packet_chars": len(text),
                "preview": text[:800],
            },
        )
    ]


def dispatch(event: dict[str, Any], profile: str | None = None) -> dict[str, Any]:
    requested_profile = profile or current_profile()
    risk = score_event(event)
    active_profile = risk["recommended_profile"] if requested_profile == "auto" else requested_profile
    event_name = str(event.get("event", "")).strip()
    if event_name == "pre_action":
        steps = dispatch_pre_action(event)
    elif event_name in {"completion_ready", "menxia.completion_ready"}:
        steps = dispatch_completion_ready(event, active_profile)
    elif event_name == "case.resume":
        steps = dispatch_case_resume(event)
    else:
        steps = [step("unknown-event", True, "skipped", reason=f"no dispatcher route for {event_name}")]

    quality_plan = quality_gate_plan(event) if event_name in {"completion_ready", "menxia.completion_ready"} else {"commands": []}
    ok = not any(item["status"] in {"block", "error"} or item["ok"] is False and item["status"] != "warn" for item in steps)
    result = {
        "ok": ok,
        "event": event_name,
        "profile": active_profile,
        "risk": risk,
        "quality_plan": quality_plan,
        "steps": steps,
    }
    result["metrics"] = append_metrics_if_case(event, result)
    return result


def append_metrics_if_case(event: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "case": event.get("case", ""),
        "event": result.get("event", ""),
        "profile": result.get("profile", ""),
        "risk": result.get("risk", {}),
        "steps": result.get("steps", []),
        "quality_plan": result.get("quality_plan", {}),
    }
    case_value = str(payload["case"]).strip()
    if case_value:
        packet = Path(case_value) / "state-packet.md"
        if packet.exists():
            payload["state_packet_chars"] = len(packet.read_text(encoding="utf-8"))
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS / "sxlb_case_metrics.py"), "append", "--json"],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "status": "error", "reason": completed.stderr or completed.stdout}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch one low-token SXLB action event to hot-path checks.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()
    result = dispatch(load_event())
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"ok: {str(result['ok']).lower()}")
        for item in result["steps"]:
            print(f"- {item['id']}: {item['status']}")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
