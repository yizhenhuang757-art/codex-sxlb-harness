#!/usr/bin/env python3
"""Render verification.md snippets for B/C/D completion checks owned by Xingbu."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


BCD_CLASSES = {"B", "C", "D"}


def _value(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key)
    if value is None or value == "":
        return default
    return str(value)


def should_generate_snippet(data: dict[str, Any]) -> bool:
    """True only for B/C/D completion checks with Xingbu or concrete verification output."""
    task_class = str(data.get("task_class", "")).strip().upper()
    phase = str(data.get("phase", "")).strip().lower()
    office = str(data.get("office", "")).strip()
    has_output = bool(str(data.get("verification_output") or data.get("output") or "").strip())
    return task_class in BCD_CLASSES and phase == "completion" and (office == "刑部" or has_output)


def render_snippet(data: dict[str, Any]) -> str:
    if not should_generate_snippet(data):
        raise ValueError("verification snippet requires B/C/D + completion + 刑部 or verification output")

    result = _value(data, "result", "pass").strip().lower()
    conclusion = "pass" if result in {"pass", "passed", "ok", "success"} else result
    output = _value(data, "output", _value(data, "verification_output", "n/a"))

    return "\n".join(
        [
            "- 验证目标："
            + _value(data, "goal", f"确认 {_value(data, 'target', 'completion package')} 的行为符合完成标准。"),
            f"- 受影响对象：{_value(data, 'target', 'n/a')}",
            f"- 验证结论：{conclusion}",
            "- 验证重量：" + _value(data, "weight", "full"),
            "- 验收标准覆盖：" + _value(data, "coverage", "all"),
            "- RED-GREEN-REFACTOR 证据：" + _value(data, "tdd_evidence", "n/a"),
            "- 行为断言/不变量：" + _value(data, "invariant", "command completed with expected result"),
            "- 测试有效性：" + _value(data, "test_validity", "command would fail on test or runtime error"),
            "",
            f"- 命令或动作：{_value(data, 'command', 'n/a')}",
            f"- 结果：{conclusion}",
            "- 失败项：" + _value(data, "failures", "none"),
            f"- 复验：{output}",
            "- 未覆盖风险：" + _value(data, "remaining_risk", "none"),
            "- 浏览器证据：" + _value(data, "browser_evidence", "n/a"),
            "- 覆盖率证据：" + _value(data, "coverage_evidence", "n/a"),
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a verification.md snippet from JSON stdin.")
    parser.add_argument("--json", action="store_true", help="Print JSON wrapper with snippet.")
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
        snippet = render_snippet(data)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"ok": True, "snippet": snippet}, ensure_ascii=False, indent=2))
    else:
        print(snippet, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
