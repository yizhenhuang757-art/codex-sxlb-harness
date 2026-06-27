#!/usr/bin/env python3
"""门下省 arrival-only completion helper hooks."""

from __future__ import annotations

from typing import Any

from arrival_common import at_completion_station, hook, run_department_cli


OWNER_SCRIPT = "menxia_arrival_hooks.py"


def needs_completion_precheck(data: dict[str, Any]) -> bool:
    return at_completion_station(data)


def recommend_hooks(data: dict[str, Any]) -> list[dict[str, str]]:
    if not needs_completion_precheck(data):
        return []
    return [
        hook(
            "completion-precheck",
            "门下省",
            "completion/close station already requires guard review before final claims",
            "harness_hooks.py completion <case-dir>",
            "guard advisories",
            OWNER_SCRIPT,
        )
    ]


def main() -> int:
    return run_department_cli(
        description="Run 门下省 arrival-only completion helper hooks.",
        office="门下省",
        recommend_hooks=recommend_hooks,
    )


if __name__ == "__main__":
    raise SystemExit(main())
