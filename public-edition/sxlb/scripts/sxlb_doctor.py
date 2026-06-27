#!/usr/bin/env python3
"""Human-facing SXLB health check.

This is a read-only convenience wrapper over existing validators. It does not
install tools, read cookies/tokens, or mutate external configuration.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

from external_capability_health import health_report
from validate_sxlb_hooks import validate_graph


SXLB_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SXLB_ROOT / "scripts"
SKILL_INVENTORY = SCRIPTS / "skill_inventory.py"
CRITICAL_SCRIPTS = [
    "sxlb_reply.py",
    "sxlb_event_router.py",
    "sxlb_hook_runner.py",
    "sxlb_gateguard.py",
    "sxlb_guard.py",
    "validate_sxlb_hooks.py",
]
BAD_STATUSES = {"block", "error"}


def check(
    check_id: str,
    label: str,
    status: str,
    detail: str,
    *,
    evidence: Any | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "detail": detail,
        "evidence": evidence if evidence is not None else {},
        "next_actions": next_actions or [],
    }


def hook_graph_check() -> dict[str, Any]:
    try:
        result = validate_graph()
    except Exception as exc:  # pragma: no cover - defensive wrapper
        return check(
            "hook_graph",
            "Hook Graph",
            "error",
            f"hook graph validation crashed: {exc}",
            next_actions=["修复 validate_sxlb_hooks.py 或 hook graph 后重跑 doctor"],
        )
    if result["ok"]:
        return check(
            "hook_graph",
            "Hook Graph",
            "ok",
            f"{result['hook_count']} hooks cover {len(result['events'])} events",
            evidence={"events": result["events"], "graph": result["graph"]},
        )
    return check(
        "hook_graph",
        "Hook Graph",
        "block",
        f"{len(result['errors'])} validation error(s)",
        evidence={"errors": result["errors"]},
        next_actions=["先修复 hooks/sxlb-hooks.json 或 schema，再启用 hook runner"],
    )


def skill_inventory_check() -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(SKILL_INVENTORY), "--check"],
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    if result.returncode == 0:
        return check("skill_inventory", "Skill Inventory", "ok", "skill inventory is current")
    detail = (result.stdout + result.stderr).strip() or f"exit code {result.returncode}"
    return check(
        "skill_inventory",
        "Skill Inventory",
        "warn",
        detail,
        next_actions=["运行 scripts/skill_inventory.py 刷新 skill-inventory.generated.md"],
    )


def external_capabilities_check() -> dict[str, Any]:
    try:
        report = health_report()
    except Exception as exc:  # pragma: no cover - defensive wrapper
        return check(
            "external_capabilities",
            "外部能力",
            "error",
            f"external capability health crashed: {exc}",
            next_actions=["检查 external_capability_health.py"],
        )
    capabilities = list(report.get("capabilities", []))
    statuses: dict[str, int] = {}
    for item in capabilities:
        status = str(item.get("status", "unknown"))
        statuses[status] = statuses.get(status, 0) + 1
    attention = [item for item in capabilities if item.get("status") != "ok"]
    if attention:
        detail = ", ".join(f"{key}={value}" for key, value in sorted(statuses.items()))
        actions = [
            f"{item['capability']}: {item['recommended_fallback']}; {item['user_action']}"
            for item in attention[:5]
        ]
        return check(
            "external_capabilities",
            "外部能力",
            "warn",
            detail,
            evidence={"capabilities": capabilities},
            next_actions=actions,
        )
    return check(
        "external_capabilities",
        "外部能力",
        "ok",
        f"{len(capabilities)} capabilities are available",
        evidence={"capabilities": capabilities},
    )


def critical_scripts_check() -> dict[str, Any]:
    missing: list[str] = []
    compile_errors: list[str] = []
    for name in CRITICAL_SCRIPTS:
        path = SCRIPTS / name
        if not path.exists():
            missing.append(name)
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            compile_errors.append(f"{name}: {exc.msg}")
    if missing or compile_errors:
        return check(
            "critical_scripts",
            "关键脚本",
            "block",
            f"missing={len(missing)}, compile_errors={len(compile_errors)}",
            evidence={"missing": missing, "compile_errors": compile_errors},
            next_actions=["修复缺失或无法编译的 SXLB 关键脚本"],
        )
    return check(
        "critical_scripts",
        "关键脚本",
        "ok",
        f"{len(CRITICAL_SCRIPTS)} scripts exist and compile",
        evidence={"scripts": CRITICAL_SCRIPTS},
    )


def build_report() -> dict[str, Any]:
    checks = [
        hook_graph_check(),
        skill_inventory_check(),
        external_capabilities_check(),
        critical_scripts_check(),
    ]
    status_counts: dict[str, int] = {}
    for item in checks:
        status = str(item["status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    ok = not any(item["status"] in BAD_STATUSES for item in checks)
    next_actions = [
        action
        for item in checks
        for action in item.get("next_actions", [])
    ]
    if not next_actions:
        next_actions = ["无阻断项；继续按 sxlb 流程使用，遇到外部工具问题时再重跑体检。"]
    summary = "可用" if ok else "需要先处理阻断项"
    if ok and status_counts.get("warn"):
        summary = "可用，但有提示项"
    return {
        "ok": ok,
        "summary": summary,
        "checks": checks,
        "status_counts": status_counts,
        "next_actions": next_actions,
    }


def render_human(report: dict[str, Any]) -> str:
    lines = [
        "SXLB 健康检查",
        f"总体：{report['summary']}",
        "",
    ]
    for item in report["checks"]:
        marker = {
            "ok": "OK",
            "warn": "WARN",
            "block": "BLOCK",
            "error": "ERROR",
        }.get(str(item["status"]), str(item["status"]).upper())
        lines.append(f"- {item['label']}: {marker} - {item['detail']}")
    lines.extend(["", "下一步："])
    for action in report["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a read-only SXLB health check.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    report = build_report()
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
