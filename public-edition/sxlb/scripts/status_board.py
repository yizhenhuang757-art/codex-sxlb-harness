#!/usr/bin/env python3
"""Render and validate sxlb status boards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import PurePath
from typing import Any


INTERVENTIONS = (
    "继续",
    "暂停",
    "会审",
    "重审",
    "录案",
    "事件簿",
    "侍讲官 <问题>",
    "国史馆",
    "翰林院",
    "起居郎",
    "退朝",
)

FULL_INTERVENTIONS = (
    "继续",
    "暂停",
    "恢复",
    "会审",
    "重审",
    "追因",
    "诊断",
    "录案",
    "召回 <某部>",
    "并行 <某部> <某部>",
    "事件簿",
    "侍讲官 <问题>",
    "国史馆",
    "翰林院",
    "起居郎",
    "退朝",
)

FULL_EVENTS = {
    "entry",
    "case-open",
    "case-switch",
    "formal-plan",
    "formal-review",
    "formal-dispatch",
    "real-subagent",
    "multi-branch-evidence",
    "records-routing",
    "closure",
    "final-report",
    "event-ledger",
    "re-review",
    "deliberation",
    "record-sync",
}

FULL_STATES = {"退朝清算", "待分流", "待回奏", "已回奏", "已中止"}

STATE_VARIANTS = {
    "待立案": "taizi",
    "中书拟制": "zhongshu",
    "门下审议": "menxia",
    "门下复核": "menxia",
    "尚书派发": "shangshu",
    "六部执行": "default",
}

REQUIRED_FIELDS = {
    "default": ("任务", "状态", "链路", "案卷状态", "采风", "待决", "干预"),
    "taizi": ("任务", "太子", "分类", "首办", "案卷状态", "待决", "干预"),
    "zhongshu": ("任务", "中书", "方案", "决策树", "案卷状态", "采风", "产物", "待决", "干预"),
    "menxia": ("任务", "门下", "对象", "结论", "问题", "案卷状态", "产物", "待决", "干预"),
    "shangshu": ("任务", "尚书", "拓扑", "派发", "readiness", "合流", "案卷状态", "产物", "待决", "干预"),
    "full": ("任务", "模式", "当前状态", "运行态", "案卷状态", "案卷", "事件簿", "分流状态", "采风"),
}

KNOWN_BOARD_FIELDS = {
    field
    for fields in REQUIRED_FIELDS.values()
    for field in fields
} | {
    "能力召回",
    "会审干预",
}

CANONICAL_OFFICE_FIELDS = {
    "太子",
    "中书省",
    "门下省",
    "尚书省",
    "六部",
    "工部",
    "刑部",
    "礼部",
    "户部",
    "兵部",
    "吏部",
    "起居郎",
    "回奏",
}

COURT_OFFICE_SUFFIXES = ("省", "部", "院", "郎", "官", "处", "台", "寺", "监")
BOARD_RE = re.compile(r"^\s*(?:#{1,6}\s*)?朝堂状态\b")
SHIJIANG_BOARD_RE = re.compile(r"^\s*(?:#{1,6}\s*)?侍讲官回奏\b")
FIELD_RE = re.compile(r"^([^：:\n]+)[：:]")


def select_variant(
    state: str,
    *,
    event: str | None = None,
    risk: bool = False,
    blocked: bool = False,
    real_subagent: bool = False,
    force: str | None = None,
) -> str:
    """Select the board variant from lifecycle state and boundary events."""
    if force:
        if force not in REQUIRED_FIELDS:
            raise ValueError(f"unknown board variant: {force}")
        return force
    if event in FULL_EVENTS or risk or blocked or real_subagent or state in FULL_STATES:
        return "full"
    return STATE_VARIANTS.get(state, "default")


def intervention_line(commands: tuple[str, ...] = INTERVENTIONS) -> str:
    return "干预：" + " ".join(f"`{command}`" for command in commands)


def _value(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if value is None or value == "":
        return default
    return str(value)


def _case_status(data: dict[str, Any]) -> str:
    explicit = data.get("case_status")
    if explicit:
        status = str(explicit)
    else:
        case = str(data.get("case") or "").strip()
        if case and case.lower() not in {"n/a", "none", "null"}:
            status = f"案卷 {_short_name(case)}"
        else:
            status = "无"

    hooks = _hooks_status(data)
    if hooks:
        return f"{status}；钩子 {hooks}"
    return status


def _short_name(value: str) -> str:
    if "/" not in value:
        return value
    return PurePath(value).name or value


def _hooks_status(data: dict[str, Any]) -> str:
    hooks = data.get("hooks") or data.get("record_hooks") or data.get("arrival_hooks")
    if not hooks:
        return ""
    if isinstance(hooks, str):
        return hooks
    if isinstance(hooks, (list, tuple)):
        names: list[str] = []
        for hook in hooks:
            if isinstance(hook, dict):
                names.append(str(hook.get("name") or hook.get("office") or hook.get("id") or hook))
            else:
                names.append(str(hook))
        return ",".join(name for name in names if name)
    return str(hooks)


def _menxia_status(data: dict[str, Any]) -> str:
    explicit = data.get("menxia_status")
    if explicit:
        return str(explicit)

    state = str(data.get("state") or "")
    runtime = str(data.get("runtime") or "").lower()
    verdict = str(data.get("verdict") or "").strip()
    target = str(data.get("target") or "").strip()
    is_review = "复核" in state or target == "完成包"

    if verdict in {"通过", "封驳"}:
        return f"复核{verdict}" if is_review else verdict
    if verdict in {"补证", "补证后再审"}:
        return "复核补证" if is_review else "补证"
    if verdict == "待审":
        return "复核中" if is_review else "审议中"
    if runtime in {"blocked", "驳回"}:
        return "复核封驳" if is_review else "封驳"
    if runtime in {"done", "complete", "completed"}:
        return "复核通过" if is_review else "通过"
    if runtime in {"review", "active"}:
        return "复核中" if is_review else "审议中"
    return "none"


def _default_lines(data: dict[str, Any]) -> list[str]:
    return [
        "朝堂状态",
        f"任务：{_value(data, 'task', '<task title>')}",
        f"状态：{_value(data, 'state', '<当前状态>')} / {_value(data, 'runtime', '<运行态>')}",
        f"链路：{_value(data, 'route', '<太子 -> 中书省 -> 门下省 -> 当前六部或 n/a>')}",
        f"案卷状态：{_case_status(data)}",
        f"采风：{_value(data, 'caifeng', 'n/a')}",
        f"待决：{_value(data, 'pending', 'none')}",
        intervention_line(),
    ]


def _taizi_lines(data: dict[str, Any]) -> list[str]:
    return [
        "朝堂状态",
        f"任务：{_value(data, 'task', '<task title>')}",
        f"太子：{_value(data, 'taizi', '立案')} / {_value(data, 'runtime', 'active')}",
        f"分类：{_value(data, 'task_class', '<A|B|C|D|待定>')}",
        f"首办：{_value(data, 'first_office', 'n/a')}",
        f"能力召回：{_value(data, 'capability_recall', 'none')}",
        f"案卷状态：{_case_status(data)}",
        f"待决：{_value(data, 'pending', 'none')}",
        intervention_line(),
    ]


def _zhongshu_lines(data: dict[str, Any]) -> list[str]:
    return [
        "朝堂状态",
        f"任务：{_value(data, 'task', '<task title>')}",
        f"中书：拟制 / {_value(data, 'runtime', 'active')}",
        f"方案：{_value(data, 'plan', '草拟中')}",
        f"决策树：{_value(data, 'decision_tree', 'open')}",
        f"能力召回：{_value(data, 'capability_recall', 'none')}",
        f"案卷状态：{_case_status(data)}",
        f"采风：{_value(data, 'caifeng', 'n/a')}",
        "产物：`zhongshu-plan.md`",
        f"待决：{_value(data, 'pending', 'none')}",
        intervention_line(),
    ]


def _menxia_lines(data: dict[str, Any]) -> list[str]:
    return [
        "朝堂状态",
        f"任务：{_value(data, 'task', '<task title>')}",
        f"门下：{_menxia_status(data)}",
        f"对象：{_value(data, 'target', '方案')}",
        f"结论：{_value(data, 'verdict', '待审')}",
        f"问题：{_value(data, 'issue', 'none')}",
        f"案卷状态：{_case_status(data)}",
        "产物：`menxia-review.md`",
        f"待决：{_value(data, 'pending', 'none')}",
        intervention_line(),
    ]


def _shangshu_lines(data: dict[str, Any]) -> list[str]:
    return [
        "朝堂状态",
        f"任务：{_value(data, 'task', '<task title>')}",
        f"尚书：派发 / {_value(data, 'runtime', 'active')}",
        f"拓扑：{_value(data, 'topology', 'single-thread')}",
        f"派发：{_value(data, 'dispatch', 'local-office')}",
        f"能力召回：{_value(data, 'capability_recall', 'none')}",
        f"readiness：{_value(data, 'readiness', 'ready-for-agent')}",
        f"合流：{_value(data, 'merge', 'n/a')}",
        f"案卷状态：{_case_status(data)}",
        "产物：`dispatch-order.md`",
        f"待决：{_value(data, 'pending', 'none')}",
        intervention_line(),
    ]


def _full_lines(data: dict[str, Any]) -> list[str]:
    offices = data.get("offices") or {}
    assigned = data.get("assigned") or []
    records = data.get("records") or {}
    return [
        "朝堂状态",
        "",
        f"任务：{_value(data, 'task', '<task title>')}",
        "模式：SXLB",
        f"当前状态：{_value(data, 'state', '<当前状态>')}",
        f"运行态：{_value(data, 'runtime', 'active')}",
        f"案卷状态：{_case_status(data)}",
        f"案卷：{_value(data, 'case', 'n/a')}",
        f"事件簿：{_value(data, 'ledger', 'n/a')}",
        f"分流状态：{_value(data, 'routing_state', '未开始')}",
        f"采风：{_value(data, 'caifeng', 'n/a')}",
        f"能力召回：{_value(data, 'capability_recall', 'none')}",
        "",
        "## 当前链路",
        "",
        f"- 太子：{offices.get('taizi', 'n/a')}",
        f"- 中书省：{offices.get('zhongshu', 'n/a')}",
        f"- 门下省：{offices.get('menxia', 'n/a')}",
        f"- 尚书省：{offices.get('shangshu', 'n/a')}",
        f"- 六部：{offices.get('liubu', 'n/a')}",
        "",
        "## 已派发",
        "",
        *(f"- {item}" for item in (assigned or ["none"])),
        "",
        "## 记录去向",
        "",
        f"- 案卷：{records.get('case', 'none')}",
        f"- canonical：{records.get('canonical', 'none')}",
        f"- restart：{records.get('restart', 'none')}",
        "",
        "## 待决问题",
        "",
        f"- {_value(data, 'pending', 'none')}",
        "",
        "## 可干预命令",
        "",
        *(f"- `{command}`" for command in FULL_INTERVENTIONS),
    ]


RENDERERS = {
    "default": _default_lines,
    "taizi": _taizi_lines,
    "zhongshu": _zhongshu_lines,
    "menxia": _menxia_lines,
    "shangshu": _shangshu_lines,
    "full": _full_lines,
}


def render_board(data: dict[str, Any], variant: str | None = None) -> str:
    """Render a status board without the user-facing reply body."""
    selected = variant or select_variant(
        _value(data, "state", ""),
        event=data.get("event"),
        risk=bool(data.get("risk")),
        blocked=bool(data.get("blocked")),
        real_subagent=bool(data.get("real_subagent")),
        force=data.get("force_variant"),
    )
    try:
        lines = RENDERERS[selected](data)
    except KeyError as exc:
        raise ValueError(f"unknown board variant: {selected}") from exc
    return "\n".join(lines).rstrip() + "\n"


def first_nonblank_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def starts_with_board(text: str) -> bool:
    first = first_nonblank_line(text)
    return bool(BOARD_RE.match(first) or SHIJIANG_BOARD_RE.match(first))


def starts_with_shijiang_board(text: str) -> bool:
    return bool(SHIJIANG_BOARD_RE.match(first_nonblank_line(text)))


def has_memorial_section(text: str) -> bool:
    return any(line.strip() == "## 回奏" for line in text.splitlines())


def _board_text_only(text: str) -> str:
    parts = re.split(r"(?m)^## 回奏\s*$", text, maxsplit=1)
    return parts[0]


def infer_variant(text: str) -> str:
    board = _board_text_only(text)
    if "## 当前链路" in board or re.search(r"(?m)^模式：SXLB\s*$", board):
        return "full"
    field_names = set()
    for line in board.splitlines():
        match = FIELD_RE.match(line.strip())
        if match:
            field_names.add(match.group(1).strip())
    if "太子" in field_names and "分类" in field_names:
        return "taizi"
    if "中书" in field_names:
        return "zhongshu"
    if "门下" in field_names:
        return "menxia"
    if "尚书" in field_names:
        return "shangshu"
    return "default"


def court_office_field_errors(text: str) -> list[str]:
    """Find hand-rolled office-like board fields outside the canonical templates."""
    board = _board_text_only(text)
    errors: list[str] = []
    for line in board.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-"):
            continue
        match = FIELD_RE.match(stripped)
        if not match:
            continue
        field = match.group(1).strip()
        if field in KNOWN_BOARD_FIELDS:
            continue
        if field.endswith(COURT_OFFICE_SUFFIXES):
            if field in CANONICAL_OFFICE_FIELDS:
                errors.append(f"non-template status board field: {field}")
            else:
                errors.append(f"unknown status board field: {field}")
    return errors


def validate_board_text(text: str, *, variant: str | None = None, require_reply: bool = True) -> tuple[bool, list[str]]:
    """Validate board structure and fixed intervention commands."""
    errors: list[str] = []
    if starts_with_shijiang_board(text):
        return True, errors
    if not starts_with_board(text):
        errors.append("active sxlb reply must begin with 朝堂状态")
        return False, errors
    if require_reply and not has_memorial_section(text):
        errors.append("active sxlb reply must include ## 回奏")

    selected = variant or infer_variant(text)
    board = _board_text_only(text)
    errors.extend(court_office_field_errors(text))

    for field in REQUIRED_FIELDS[selected]:
        if not re.search(rf"(?m)^{re.escape(field)}[：:]", board):
            errors.append(f"missing required board field: {field}")

    if selected == "full":
        for section in ("## 当前链路", "## 已派发", "## 记录去向", "## 待决问题", "## 可干预命令"):
            if section not in board:
                errors.append(f"missing required full board section: {section}")
    elif "六帽" in board:
        errors.append("六帽 is only allowed in 会审提示, not ordinary compact boards")

    for command in INTERVENTIONS:
        if f"`{command}`" not in board:
            errors.append(f"missing intervention command: {command}")

    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or validate sxlb status boards.")
    parser.add_argument("--render", action="store_true", help="Render a board from JSON stdin")
    parser.add_argument("--validate", action="store_true", help="Validate a reply from stdin")
    parser.add_argument("--variant", choices=sorted(REQUIRED_FIELDS), help="Force or validate a specific variant")
    parser.add_argument("--json", action="store_true", help="Print JSON output for validation")
    args = parser.parse_args()

    if args.render:
        data = json.load(sys.stdin)
        print(render_board(data, variant=args.variant), end="")
        return 0

    ok, errors = validate_board_text(sys.stdin.read(), variant=args.variant)
    if args.json:
        print(json.dumps({"ok": ok, "errors": errors}, ensure_ascii=False, indent=2))
    elif not ok:
        for error in errors:
            print(error, file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
