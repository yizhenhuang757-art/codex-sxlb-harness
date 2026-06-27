#!/usr/bin/env python3
"""礼部 arrival-only records-routing and 起居郎 helper hooks."""

from __future__ import annotations

from typing import Any

from arrival_common import BCD_CLASSES, HUMAN_FACING_TARGETS, at_completion_station, hook, lower, run_department_cli, text, truthy


OWNER_SCRIPT = "libu_arrival_hooks.py"


def needs_records_routing(data: dict[str, Any]) -> bool:
    task_class = text(data, "task_class").upper()
    has_routing_trigger = any(
        truthy(data, key)
        for key in (
            "records_routing_required",
            "canonical_changed",
            "restart_changed",
            "writeback_changed",
            "protocol_change",
            "automation",
        )
    )
    return at_completion_station(data) and (task_class in BCD_CLASSES or has_routing_trigger)


def needs_qijulang_candidate(data: dict[str, Any]) -> bool:
    target = lower(data, "target_kind")
    human_facing = truthy(data, "human_facing_change") or target in HUMAN_FACING_TARGETS
    return needs_records_routing(data) and human_facing


def recommend_hooks(data: dict[str, Any]) -> list[dict[str, str]]:
    hooks: list[dict[str, str]] = []
    if needs_records_routing(data):
        hooks.append(
            hook(
                "records-routing-candidate",
                "礼部",
                "completion package already requires records routing or has a concrete writeback trigger",
                "libu_arrival_hooks.py --render records-routing-candidate",
                "records-routing.md candidate",
                OWNER_SCRIPT,
            )
        )
    if needs_qijulang_candidate(data):
        hooks.append(
            hook(
                "qijulang-candidate",
                "礼部/起居郎",
                "human-facing writeback is attached to records routing and is not a standalone workflow",
                "libu_arrival_hooks.py --render qijulang-candidate",
                "起居郎候补 candidate",
                OWNER_SCRIPT,
            )
        )
    return hooks


def _require_hook(data: dict[str, Any], hook_name: str) -> None:
    if hook_name not in {item["hook"] for item in recommend_hooks(data)}:
        raise ValueError(f"{hook_name} is not allowed before its existing 礼部 station is reached")


def render_records_routing_candidate(data: dict[str, Any]) -> str:
    _require_hook(data, "records-routing-candidate")
    canonical = text(data, "canonical") or ("updated canonical/protocol/script surface" if truthy(data, "canonical_changed") else "not-needed")
    restart = text(data, "restart_update") or ("update restart pointer if phase changed" if truthy(data, "restart_changed") else "not-needed")
    report_only = text(data, "report_only") or "case-local evidence remains in the worklog"
    no_writeback = text(data, "no_writeback") or "no unrelated vault or canonical writeback"
    return "\n".join(
        [
            "# Records routing candidate",
            "",
            f"- canonical：{canonical}",
            f"- report-only：{report_only}",
            f"- restart-update：{restart}",
            f"- no-writeback：{no_writeback}",
            "- 触发条件：arrival-only 礼部 completion/writeback gate",
            "",
        ]
    )


def render_qijulang_candidate(data: dict[str, Any]) -> str:
    _require_hook(data, "qijulang-candidate")
    target = text(data, "target") or text(data, "target_kind") or "human-facing surface"
    return "\n".join(
        [
            "# 起居郎候补",
            "",
            "- 起居郎候补：yes",
            f"- 目标：{target}",
            "- 依附关系：attached to records-routing; not a standalone workflow",
            f"- 理由：{text(data, 'reason', 'human-facing change needs a concise user-facing projection')}",
            "- 写入方式：delta-only after 门下复核 or explicit user request",
            "",
        ]
    )


def main() -> int:
    return run_department_cli(
        description="Run 礼部 arrival-only helper hooks.",
        office="礼部",
        recommend_hooks=recommend_hooks,
        renderers={
            "records-routing-candidate": render_records_routing_candidate,
            "qijulang-candidate": render_qijulang_candidate,
        },
    )


if __name__ == "__main__":
    raise SystemExit(main())
