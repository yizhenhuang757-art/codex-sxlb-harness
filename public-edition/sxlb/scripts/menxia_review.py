#!/usr/bin/env python3
"""Semi-automatic Menxia completion review gate for sxlb."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from approval_ledger import collect_approval_entries, write_approval_ledger
from objection_review import requires_objection_review, write_objection_review
from sxlb_guard import (
    extract_section,
    has_substantive_reason,
    parse_dispatch_assignments,
    parse_fields,
    read_file,
    validate_case_dir,
)


REVIEW_FILE = "menxia-review.md"
READINESS_FILE = "menxia-readiness.md"
SELF_GENERATED_REVIEW_ISSUES = {
    "Missing required file: menxia-review.md",
    "event-ledger.md state 门下审议 requires menxia-review.md",
    "event-ledger.md state 门下复核 requires menxia-review.md",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_review_event(case_dir: Path) -> Path:
    ledger_path = case_dir / "event-ledger.md"
    existing = ledger_path.read_text(encoding="utf-8").rstrip()
    entry = "\n".join(
        [
            "",
            f"- 时间：{now_iso()}",
            "  状态：门下复核",
            "  动作：review",
            "  发起：门下省",
            "  摘要：Completion review executed",
            "  证据：menxia-review.md",
            "",
        ]
    )
    write_text(ledger_path, existing + entry)
    return ledger_path


def collect_review_inputs(case_dir: Path) -> dict[str, str]:
    dispatch_text = read_file(case_dir, "dispatch-order.md") or ""
    dispatch_fields = parse_fields(dispatch_text)
    assignments = parse_dispatch_assignments(dispatch_text)
    real_assignments = [assignment for assignment in assignments if assignment.get("分支执行") == "real-subagent"]
    packet_inputs = ", ".join(
        assignment.get("工作包", "").strip()
        for assignment in real_assignments
        if assignment.get("工作包", "").strip()
    ) or "n/a"
    return_inputs = ", ".join(
        assignment.get("回传物", "").strip()
        for assignment in real_assignments
        if assignment.get("回传物", "").strip()
    ) or "n/a"
    merge_input = dispatch_fields.get("合流摘要", "n/a").strip() or "n/a"
    return {
        "dispatch_ref": "dispatch-order.md",
        "packet_inputs": packet_inputs,
        "return_inputs": return_inputs,
        "merge_input": merge_input,
        "real_dispatch": dispatch_fields.get("真实派发", "").lower(),
        "case_dir": str(case_dir),
    }


def collect_verification_issues(case_dir: Path) -> list[str]:
    issues: list[str] = []
    memorial_text = read_file(case_dir, "memorial-report.md") or ""
    memorial_fields = parse_fields(memorial_text)
    verification_evidence = memorial_fields.get("验证证据", "")
    if not has_substantive_reason(verification_evidence):
        issues.append("Verification evidence is missing or non-substantive in memorial-report.md")

    dispatch_text = read_file(case_dir, "dispatch-order.md") or ""
    dispatch_fields = parse_fields(dispatch_text)
    if dispatch_fields.get("真实派发", "").lower() == "yes":
        assignments = parse_dispatch_assignments(dispatch_text)
        for assignment in assignments:
            if assignment.get("分支执行") != "real-subagent":
                continue
            return_ref = assignment.get("回传物", "").strip()
            if not return_ref:
                issues.append(f"Real-subagent branch {assignment.get('分支编号', 'unknown')} has no return reference")
                continue
            return_text = read_file(case_dir, return_ref)
            if not return_text:
                issues.append(f"Missing referenced return artifact: {return_ref}")
                continue
            return_fields = parse_fields(return_text)
            if not has_substantive_reason(return_fields.get("新增证据", "")):
                issues.append(f"Branch return {return_ref} lacks substantive verification evidence")
    return issues


def render_readiness_dashboard(*, issues: list[str], review_inputs: dict[str, str], approval_entries: list[dict[str, str]]) -> str:
    issue_text = "\n".join(issues)
    verification_fields = parse_fields(read_file(Path(review_inputs["case_dir"]), "verification.md") or "")
    browser_coverage_status = "n/a"
    if has_substantive_reason(verification_fields.get("浏览器证据")) or has_substantive_reason(verification_fields.get("覆盖率证据")):
        browser_coverage_status = "pass"
    test_quality_status = (
        "pass"
        if has_substantive_reason(verification_fields.get("行为断言/不变量"))
        and has_substantive_reason(verification_fields.get("测试有效性"))
        else "pending"
    )

    def status_for(gate: str, evidence: str) -> str:
        if gate == "验证证据":
            return "fail" if "verification" in issue_text.lower() else "pass"
        if evidence != "n/a":
            return "pass"
        return "pending"

    rows = [
        ("中书方案", "yes", status_for("中书方案", "zhongshu-plan.md"), "zhongshu-plan.md"),
        ("派令", "yes", status_for("派令", review_inputs["dispatch_ref"]), review_inputs["dispatch_ref"]),
        ("产物注册表", "yes", status_for("产物注册表", "artifact-registry.md"), "artifact-registry.md"),
        ("验证证据", "yes", status_for("验证证据", "verification.md"), "verification.md"),
        ("测试有效性", "yes", test_quality_status, "verification.md"),
        ("浏览器/覆盖率证据", "conditional", browser_coverage_status, "verification.md"),
        ("记录分流", "yes", status_for("记录分流", "records-routing.md"), "records-routing.md"),
        ("learning handoff", "yes", status_for("learning handoff", "learning-candidates.jsonl"), "learning-candidates.jsonl"),
        ("分支回传", "conditional", "pass" if review_inputs["return_inputs"] != "n/a" or review_inputs["real_dispatch"] != "yes" else "pending", review_inputs["return_inputs"]),
        ("合流摘要", "conditional", "pass" if review_inputs["merge_input"] != "n/a" or review_inputs["real_dispatch"] != "yes" else "pending", review_inputs["merge_input"]),
    ]
    if approval_entries:
        approval_ok = all(entry.get("approval_status") == "present" for entry in approval_entries)
        rows.append(("审批台账", "conditional", "pass" if approval_ok else "fail", "approval-ledger.md"))
    else:
        rows.append(("审批台账", "conditional", "n/a", "n/a"))
    lines = [
        "# 门下 readiness dashboard",
        "",
        "| Gate | Required | Status | Evidence |",
        "|---|---:|---|---|",
    ]
    for gate, required, status, evidence in rows:
        lines.append(f"| {gate} | {required} | {status} | {evidence} |")
    return "\n".join(lines) + "\n"


def render_review(
    *,
    verdict: str,
    allow_memorial: bool,
    issues: list[str],
    review_inputs: dict[str, str],
    approval_entries: list[dict[str, str]],
) -> str:
    legal_check = "pass" if not any("legacy" in issue.lower() or "missing required file" in issue.lower() for issue in issues) else "fail"
    verification_check = "pass" if not any("verification" in issue.lower() for issue in issues) else "fail"
    merge_check = "pass" if not any("merge" in issue.lower() for issue in issues) else "fail"
    packet_check = "pass" if not any("packet" in issue.lower() for issue in issues) else "fail"
    return_check = "pass" if not any("return" in issue.lower() for issue in issues) else "fail"
    route_check = "pass" if not any("dispatch" in issue.lower() for issue in issues) else "fail"
    issue_text = "\n".join(issues).lower()
    prd_language_check = "manual"
    dispatch_slice_check = "fail" if any(token in issue_text for token in ("切片类型", "验收标准", "acceptance")) else ("pass" if review_inputs["real_dispatch"] == "yes" else "n/a")
    hitl_afk_check = "fail" if any(token in issue_text for token in ("hitl", "afk", "交互模式", "human decision")) else ("pass" if review_inputs["real_dispatch"] == "yes" else "n/a")
    readiness_check = "fail" if any(token in issue_text for token in ("ready-for-agent", "blocked", "派发就绪状态")) else ("pass" if review_inputs["real_dispatch"] == "yes" else "n/a")
    budget_check = "fail" if any(token in issue_text for token in ("预算", "budget", "修复循环", "执行预算")) else "manual"
    conflict_choice_check = "fail" if any(token in issue_text for token in ("conflict", "冲突", "source of truth")) else "manual"
    failure_visibility_check = "pass" if not issues else "fail"
    approval_check = "n/a"
    approval_input = "n/a"
    if approval_entries:
        approval_input = "approval-ledger.md"
        approval_check = "pass" if all(entry.get("approval_status") == "present" for entry in approval_entries) else "fail"

    evidence_line = "completion package is valid and verification evidence is present" if not issues else "; ".join(issues)
    supplement = "none" if not issues else "; ".join(issues)
    return_state = "待回奏" if allow_memorial else "门下复核"
    return_office = "礼部" if allow_memorial else "尚书省"

    return "\n".join(
        [
            "# 门下复核单",
            "",
            "## 审议对象",
            "",
            "- 来源：completion claim",
            "- 审议类型：completion",
            "- 当前阶段：门下复核",
            "- 审议范围：completion package",
            f"- 派令引用：{review_inputs['dispatch_ref']}",
            f"- 工作包输入：{review_inputs['packet_inputs']}",
            f"- 回传输入：{review_inputs['return_inputs']}",
            f"- 合流输入：{review_inputs['merge_input']}",
            f"- 审批台账输入：{approval_input}",
            "",
            "## 审议结论",
            "",
            f"- 结论：{verdict}",
            f"- 主要依据：{evidence_line}",
            "",
            "## 发现",
            "",
            f"- 合法链路检查：{legal_check}",
            "- 官署归属检查：pass",
            "- 四问-假设检查：manual",
            "- 四问-复杂度检查：manual",
            "- 四问-改动边界检查：manual",
            f"- 四问-验证方式检查：{verification_check}",
            f"- PRD/领域语言检查：{prd_language_check}",
            f"- 预算与停止条件检查：{budget_check}",
            f"- 冲突取舍检查：{conflict_choice_check}",
            f"- 派发切片检查：{dispatch_slice_check}",
            f"- HITL/AFK 检查：{hitl_afk_check}",
            f"- blocked-by/ready-for-agent 检查：{readiness_check}",
            f"- 真实派发检查：{'required' if review_inputs['real_dispatch'] == 'yes' else 'not-required'}",
            f"- 工作包边界检查：{packet_check}",
            f"- 回传完备检查：{return_check}",
            f"- 合流依据检查：{merge_check}",
            f"- 审批台账检查：{approval_check}",
            "- 范围问题：none" if not issues else f"- 范围问题：{supplement}",
            "- 分支冲突问题：none",
            f"- 验证问题：{verification_check if verification_check == 'pass' else supplement}",
            f"- 失败显性化检查：{failure_visibility_check}",
            "- 技能匹配问题：none",
            f"- 路由问题：{route_check}",
            "",
            "## 下一步",
            "",
            f"- 返回状态：{return_state}",
            f"- 返回官署：{return_office}",
            f"- 是否准许回奏：{'yes' if allow_memorial else 'no'}",
            f"- 补充要求：{supplement}",
            "",
        ]
    )


def run_completion_review(case_dir: Path, *, force: bool = False) -> dict[str, Any]:
    approval_ledger_path = write_approval_ledger(case_dir)
    objection_review_path: str | None = None
    if requires_objection_review(case_dir):
        objection_review_path = str(write_objection_review(case_dir))
    approval_entries = collect_approval_entries(case_dir)
    guard_result = validate_case_dir(case_dir, phase="completion")
    issues = [issue for issue in guard_result.errors if issue not in SELF_GENERATED_REVIEW_ISSUES]
    issues.extend(collect_verification_issues(case_dir))
    review_inputs = collect_review_inputs(case_dir)

    allow_memorial = not issues
    verdict = "通过" if allow_memorial else "补证后再审"
    review_text = render_review(
        verdict=verdict,
        allow_memorial=allow_memorial,
        issues=issues,
        review_inputs=review_inputs,
        approval_entries=approval_entries,
    )

    readiness_path = case_dir / READINESS_FILE
    write_text(readiness_path, render_readiness_dashboard(issues=issues, review_inputs=review_inputs, approval_entries=approval_entries))

    review_path = case_dir / REVIEW_FILE
    if review_path.exists() and not force:
        raise FileExistsError(f"Review file already exists: {review_path}")
    write_text(review_path, review_text)
    ledger_path = append_review_event(case_dir)

    return {
        "case_dir": str(case_dir),
        "verdict": verdict,
        "allow_memorial": allow_memorial,
        "issues": issues,
        "approval_ledger_path": str(approval_ledger_path),
        "objection_review_path": objection_review_path,
        "review_path": str(review_path),
        "readiness_path": str(readiness_path),
        "ledger_path": str(ledger_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a semi-automatic Menxia completion review.")
    parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    parser.add_argument("--force", action="store_true", help="Overwrite menxia-review.md if it already exists")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON result")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_completion_review(args.case_dir, force=args.force)
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"verdict: {result['verdict']}")
        print(f"allow_memorial: {str(result['allow_memorial']).lower()}")
        if result["issues"]:
            print("issues:")
            for issue in result["issues"]:
                print(f"- {issue}")
    return 0 if result["allow_memorial"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
