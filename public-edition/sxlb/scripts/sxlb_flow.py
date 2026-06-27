#!/usr/bin/env python3
"""Conservative flow orchestrator for advancing an sxlb case package."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from menxia_review import REVIEW_FILE, run_completion_review
from shangshu_dispatch import SUMMARY_NAME as DISPATCH_SUMMARY_NAME
from shangshu_dispatch import prepare_dispatch
from subagent_dispatch import MANIFEST_NAME, SUBAGENTS_DIRNAME, build_merge_summary
from sxlb_arrival_hooks import recommend_hooks
from sxlb_guard import parse_dispatch_assignments, parse_fields, read_file


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_event(case_dir: Path, *, state: str, action: str, office: str, summary: str, evidence: str) -> Path:
    ledger_path = case_dir / "event-ledger.md"
    existing = ledger_path.read_text(encoding="utf-8").rstrip()
    entry = "\n".join(
        [
            "",
            f"- 时间：{now_iso()}",
            f"  状态：{state}",
            f"  动作：{action}",
            f"  发起：{office}",
            f"  摘要：{summary}",
            f"  证据：{evidence}",
            "",
        ]
    )
    write_text(ledger_path, existing + entry)
    return ledger_path


def load_dispatch(case_dir: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    dispatch_text = read_file(case_dir, "dispatch-order.md")
    if not dispatch_text:
        raise FileNotFoundError(f"Missing dispatch-order.md in {case_dir}")
    return parse_fields(dispatch_text), parse_dispatch_assignments(dispatch_text)


def real_assignments(assignments: list[dict[str, str]]) -> list[dict[str, str]]:
    return [assignment for assignment in assignments if assignment.get("分支执行") == "real-subagent"]


def merge_required(dispatch_fields: dict[str, str], assignments: list[dict[str, str]]) -> bool:
    merge_flag = dispatch_fields.get("合流要求", "").strip().lower()
    topology = dispatch_fields.get("拓扑", "").strip().lower()
    return merge_flag in {"yes", "required", "merge required"} or len(real_assignments(assignments)) > 1 or "parallel" in topology


def dispatch_preparation_needed(case_dir: Path, dispatch_fields: dict[str, str], assignments: list[dict[str, str]]) -> bool:
    if not (case_dir / DISPATCH_SUMMARY_NAME).exists():
        return True
    if dispatch_fields.get("执行方式") != "real-subagent":
        return False
    manifest_path = case_dir / SUBAGENTS_DIRNAME / MANIFEST_NAME
    if not manifest_path.exists():
        return True
    for assignment in real_assignments(assignments):
        packet_ref = assignment.get("工作包", "").strip()
        if packet_ref and not (case_dir / packet_ref).exists():
            return True
    return False


def collect_missing_returns(case_dir: Path, assignments: list[dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for assignment in real_assignments(assignments):
        branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
        return_ref = assignment.get("回传物", "").strip()
        if not return_ref:
            missing.append(f"{branch_id}: missing return reference")
            continue
        if not (case_dir / return_ref).exists():
            missing.append(f"{branch_id}: {return_ref}")
    return missing


def derive_state(*, review_result: dict[str, Any] | None, memorial_exists: bool, missing_returns: list[str], merge_missing: bool) -> tuple[str, str]:
    if review_result:
        if review_result["allow_memorial"]:
            return "reviewed-pass", "礼部可据 `menxia-review.md` 回奏，不需再人工判断结案合法性。"
        return "reviewed-blocked", "门下省已拦下当前结案，请先补证后再审。"
    if missing_returns:
        return "awaiting-returns", "真实分支仍有未回传项，当前不应进入结案复核。"
    if merge_missing:
        return "awaiting-merge", "回传已齐，但尚缺合流摘要，先完成合流再议结案。"
    if memorial_exists:
        return "ready-for-review", "结案材料已到位，可进入门下复核。"
    return "ready-for-memorial", "执行证据已齐，但尚未形成回奏材料。"


def load_existing_review(case_dir: Path) -> dict[str, Any] | None:
    review_text = read_file(case_dir, REVIEW_FILE)
    if not review_text:
        return None
    fields = parse_fields(review_text)
    verdict = fields.get("结论", "")
    allow_memorial = fields.get("是否准许回奏") == "yes"
    return {"verdict": verdict, "allow_memorial": allow_memorial}


def parse_task_class(case_dir: Path) -> str:
    fields = parse_fields(read_file(case_dir, "case.md") or "")
    return fields.get("任务类别", "").strip()


def phase_for_state(state: str) -> str:
    if state in {"reviewed-pass", "reviewed-blocked", "ready-for-review"}:
        return "completion"
    if state == "awaiting-returns":
        return "execution"
    if state == "awaiting-merge":
        return "review"
    if state == "ready-for-memorial":
        return "completion"
    return state


def arrival_context(case_dir: Path, *, state: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    verification_text = read_file(case_dir, "verification.md") or ""
    return {
        "phase": phase_for_state(state),
        "state": state,
        "task_class": parse_task_class(case_dir),
        "office": "刑部" if verification_text else "",
        "verification_output": verification_text,
        "records_routing_required": (case_dir / "records-routing.md").exists(),
        "canonical_changed": "canonical 更新：" in (read_file(case_dir, "memorial-report.md") or ""),
        "actions": [action["action"] for action in actions],
    }


def advance_case(case_dir: Path, *, force: bool = False) -> dict[str, Any]:
    dispatch_fields, assignments = load_dispatch(case_dir)
    actions: list[dict[str, Any]] = []
    dispatch_stage = dispatch_fields.get("当前阶段", "").strip()

    if dispatch_stage == "尚书派发" and (force or dispatch_preparation_needed(case_dir, dispatch_fields, assignments)):
        dispatch_result = prepare_dispatch(case_dir, force=force)
        actions.append(
            {
                "action": "dispatch",
                "office": "尚书省",
                "result": {
                    "summary": dispatch_result["summary"],
                    "real_packet_count": dispatch_result["real_packet_count"],
                },
            }
        )

    dispatch_fields, assignments = load_dispatch(case_dir)
    missing_returns = collect_missing_returns(case_dir, assignments)

    merge_path_str = dispatch_fields.get("合流摘要", "").strip()
    merge_path = case_dir / merge_path_str if merge_path_str and merge_path_str not in {"n/a", "none"} else None
    needs_merge = dispatch_fields.get("执行方式") == "real-subagent" and merge_required(dispatch_fields, assignments)
    merge_missing = bool(needs_merge and merge_path and not merge_path.exists())

    if (force or merge_missing) and needs_merge and not missing_returns:
        summary_path = build_merge_summary(case_dir, force=force)
        append_event(
            case_dir,
            state=dispatch_fields.get("返回审议点", "门下复核"),
            action="merge",
            office=dispatch_fields.get("合流负责", "尚书省") or "尚书省",
            summary="Merge summary refreshed from current branch returns",
            evidence=str(summary_path.relative_to(case_dir)),
        )
        actions.append(
            {
                "action": "merge",
                "office": dispatch_fields.get("合流负责", "尚书省") or "尚书省",
                "result": {"summary": str(summary_path)},
            }
        )
        merge_missing = False

    memorial_exists = (case_dir / "memorial-report.md").exists()
    review_exists = (case_dir / REVIEW_FILE).exists()
    review_result: dict[str, Any] | None = load_existing_review(case_dir) if review_exists and not force else None

    if memorial_exists and (force or not review_exists) and not missing_returns and not merge_missing:
        review_result = run_completion_review(case_dir, force=force)
        actions.append(
            {
                "action": "review",
                "office": "门下省",
                "result": {
                    "verdict": review_result["verdict"],
                    "allow_memorial": review_result["allow_memorial"],
                },
            }
        )

    state, next_step = derive_state(
        review_result=review_result,
        memorial_exists=memorial_exists,
        missing_returns=missing_returns,
        merge_missing=merge_missing,
    )
    arrival_hooks = recommend_hooks(arrival_context(case_dir, state=state, actions=actions))

    return {
        "case_dir": str(case_dir),
        "state": state,
        "next_step": next_step,
        "missing_returns": missing_returns,
        "merge_missing": merge_missing,
        "memorial_exists": memorial_exists,
        "review_exists": review_exists or review_result is not None,
        "actions": actions,
        "arrival_hooks": arrival_hooks,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Advance an sxlb case through dispatch, merge, and review.")
    parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    parser.add_argument("--force", action="store_true", help="Refresh generated artifacts when supported")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = advance_case(args.case_dir, force=args.force)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"state: {result['state']}")
        print(f"next_step: {result['next_step']}")
        if result["missing_returns"]:
            print("missing_returns:")
            for item in result["missing_returns"]:
                print(f"- {item}")
        for action in result["actions"]:
            print(f"action: {action['action']} ({action['office']})")
        if result["arrival_hooks"]:
            print("arrival_hooks:")
            for hook in result["arrival_hooks"]:
                print(f"- {hook['hook']} ({hook['office']} via {hook['owner_script']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
