#!/usr/bin/env python3
"""Semi-automatic Shangshu dispatcher for preparing governed execution."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from subagent_dispatch import create_dispatch_bundle, load_case_context


SUMMARY_NAME = "shangshu-dispatch-summary.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_dispatch_event(case_dir: Path, *, summary_name: str = SUMMARY_NAME) -> Path:
    ledger_path = case_dir / "event-ledger.md"
    if not ledger_path.exists():
        raise FileNotFoundError(f"Missing event ledger: {ledger_path}")

    existing = read_text(ledger_path).rstrip()
    entry = "\n".join(
        [
            "",
            f"- 时间：{now_iso()}",
            "  状态：尚书派发",
            "  动作：dispatch",
            "  发起：尚书省",
            "  摘要：Semi-automatic dispatch preparation completed",
            f"  证据：dispatch-order.md, {summary_name}",
            "",
        ]
    )
    write_text(ledger_path, existing + entry)
    return ledger_path


def render_dispatch_summary(case_dir: Path, context: Any, *, real_packet_count: int) -> str:
    local_branches = [assignment for assignment in context.assignments if assignment.execution != "real-subagent"]
    real_branches = [assignment for assignment in context.assignments if assignment.execution == "real-subagent"]
    lines = [
        "# 尚书派发摘要",
        "",
        "## 派发总览",
        "",
        f"- 案卷：{case_dir}",
        f"- 当前阶段：{context.dispatch_stage}",
        f"- 拓扑：{context.topology}",
        f"- 执行方式：{context.execution_mode}",
        f"- 真实派发分支：{real_packet_count}",
        f"- 能力召回：{context.capability_recall or 'none'}",
        f"- 本线办理理由：{context.local_reason if context.execution_mode == 'local-office' else 'n/a'}",
        f"- 返回审议点：{context.review_return_point}",
        "",
        "## 分支概览",
        "",
    ]
    for assignment in context.assignments:
        branch_id = assignment.branch_id or "n/a"
        lines.extend(
            [
                f"- {assignment.office} / {branch_id} / {assignment.execution}",
                f"  任务：{assignment.task}",
                f"  所有权：{assignment.ownership}",
            ]
        )

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- 真实派发分支：{', '.join((assignment.branch_id or assignment.office) for assignment in real_branches) or 'none'}",
            f"- 本线分支：{', '.join((assignment.branch_id or assignment.office) for assignment in local_branches) or 'none'}",
            "- 推荐动作：" + ("开始真实分支执行并等待回传" if real_branches else "按本线方案继续办理"),
        ]
    )
    return "\n".join(lines) + "\n"


def prepare_dispatch(case_dir: Path, *, force: bool = False) -> dict[str, Any]:
    context = load_case_context(case_dir)
    if context.dispatch_stage != "尚书派发":
        raise ValueError(f"dispatch-order.md is not in 尚书派发 stage: {context.dispatch_stage}")

    created_paths: list[str] = []
    real_packet_count = 0
    if context.execution_mode == "real-subagent":
        created = create_dispatch_bundle(case_dir, force=force)
        created_paths.extend(str(path) for path in created)
        real_packet_count = sum(1 for assignment in context.assignments if assignment.execution == "real-subagent")

    summary_path = case_dir / SUMMARY_NAME
    write_text(summary_path, render_dispatch_summary(case_dir, context, real_packet_count=real_packet_count))
    created_paths.append(str(summary_path))

    ledger_path = append_dispatch_event(case_dir)
    created_paths.append(str(ledger_path))

    result = {
        "case_dir": str(case_dir),
        "stage": context.dispatch_stage,
        "mode": context.execution_mode,
        "topology": context.topology,
        "real_packet_count": real_packet_count,
        "created": created_paths,
        "summary": str(summary_path),
        "ledger": str(ledger_path),
    }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare Shangshu dispatch artifacts for an sxlb case.")
    parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    parser.add_argument("--force", action="store_true", help="Overwrite generated artifacts when supported")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = prepare_dispatch(args.case_dir, force=args.force)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"mode: {result['mode']}")
        print(f"real_packet_count: {result['real_packet_count']}")
        print(f"summary: {result['summary']}")
        print(f"ledger: {result['ledger']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
