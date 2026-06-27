#!/usr/bin/env python3
"""户部 arrival-only external-evidence helper hooks."""

from __future__ import annotations

from datetime import date
from typing import Any

from arrival_common import at_review_station, hook, run_department_cli, text, truthy


OWNER_SCRIPT = "hubu_arrival_hooks.py"


def needs_external_evidence_package(data: dict[str, Any]) -> bool:
    return at_review_station(data) and truthy(data, "external_sources_used") and truthy(data, "conclusion_depends_on_external")


def recommend_hooks(data: dict[str, Any]) -> list[dict[str, str]]:
    if not needs_external_evidence_package(data):
        return []
    return [
        hook(
            "external-evidence-package",
            "户部/门下省",
            "review/completion already depends on external sources, so source boundary evidence is required",
            "hubu_arrival_hooks.py --render external-evidence-package",
            "external-evidence.md candidate",
            OWNER_SCRIPT,
        )
    ]


def render_external_evidence_candidate(data: dict[str, Any]) -> str:
    if not needs_external_evidence_package(data):
        raise ValueError("external-evidence-package is not allowed before its existing 户部/门下 station is reached")
    return "\n".join(
        [
            "# External evidence package candidate",
            "",
            f"- 调研问题：{text(data, 'question', text(data, 'task', 'n/a'))}",
            f"- 来源清单：{text(data, 'sources', 'to-be-filled from already-used sources')}",
            f"- 来源类型：{text(data, 'source_types', 'official')}",
            f"- 检查日期：{text(data, 'checked_date', date.today().isoformat())}",
            f"- 来源可靠性：{text(data, 'source_reliability', 'to be assessed by 门下省')}",
            f"- 可用结论：{text(data, 'usable_conclusion', 'to be filled from reviewed evidence')}",
            f"- 不确定性：{text(data, 'uncertainty', 'none stated yet')}",
            f"- 决策影响：{text(data, 'decision_impact', 'external evidence supports a user-facing conclusion')}",
            "- 触发条件：review/completion already relies on external sources",
            "",
        ]
    )


def main() -> int:
    return run_department_cli(
        description="Run 户部 arrival-only external-evidence helper hooks.",
        office="户部/门下省",
        recommend_hooks=recommend_hooks,
        renderers={"external-evidence-package": render_external_evidence_candidate},
    )


if __name__ == "__main__":
    raise SystemExit(main())
