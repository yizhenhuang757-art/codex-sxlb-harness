#!/usr/bin/env python3
"""Lightweight lifecycle hook checks for the sxlb coding-agent harness."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sxlb_case_status import append_event, now_iso
from sxlb_guard import (
    find_dangerous_command,
    has_substantive_reason,
    is_approval_required_policy,
    is_no_destructive_policy,
    parse_dispatch_assignments,
    parse_fields,
    read_file,
    validate_case_dir,
    validate_dangerous_command_policy,
    validate_touched_scope,
)


NONE_VALUES = {"", "none", "n/a", "not required", "not-needed", "no", "false", "无"}
SUMMARY_RE = re.compile(r"摘要：\s*(.+)")
A_FAST_LANE_ROUTE = "太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏"
A_HEAVY_ARTIFACTS = (
    "zhongshu-plan.md",
    "verification.md",
    "artifact-registry.md",
    "records-routing.md",
    "learning-candidates.jsonl",
)
FAILURE_LOCATION_KEYWORDS = (
    ("verification", ("验证", "测试", "复验", "没测", "未测", "test", "verify", "verification")),
    ("reporting", ("回奏", "报告", "说明", "没说", "未说明", "隐瞒", "夸大", "report")),
    ("execution", ("执行", "实现", "代码", "改错", "没改", "implementation", "execute")),
    ("planning", ("方案", "计划", "路线", "拆解", "planning", "plan")),
    ("intake", ("需求", "目标", "范围", "约束", "没理解", "intake", "scope")),
    ("preference capture", ("偏好", "习惯", "喜欢", "不喜欢", "preference")),
)


@dataclass
class HookResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "data": self.data,
        }


def split_items(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace("；", ",").replace("，", ",").replace(";", ",")
    return [item.strip().strip("`") for item in normalized.split(",") if item.strip()]


def meaningful(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in NONE_VALUES


def path_in_scope(path: str, scope: str) -> bool:
    clean_path = path.strip().strip("`")
    clean_scope = scope.strip().strip("`").rstrip("/")
    if not clean_path or not clean_scope:
        return False
    return clean_path == clean_scope or clean_path.startswith(clean_scope + "/")


def load_assignment(case_dir: Path, *, office: str | None = None, branch_id: str | None = None) -> dict[str, str] | None:
    dispatch_text = read_file(case_dir, "dispatch-order.md") or ""
    assignments = parse_dispatch_assignments(dispatch_text)
    for assignment in assignments:
        if branch_id and assignment.get("分支编号", "").strip() == branch_id:
            return assignment
        if office and assignment.get("官署", "").strip() == office:
            return assignment
    return None


def normalize_route(value: str | None) -> str:
    if not value:
        return ""
    return " -> ".join(part.strip() for part in value.replace("→", "->").split("->") if part.strip())


def case_fields(case_dir: Path) -> dict[str, str]:
    return parse_fields(read_file(case_dir, "case.md") or "")


def dispatch_fields(case_dir: Path) -> dict[str, str]:
    return parse_fields(read_file(case_dir, "dispatch-order.md") or "")


def has_volatile_record(case_dir: Path) -> bool:
    path = case_dir / "volatile-record.md"
    if not path.exists():
        return False
    fields = parse_fields(path.read_text(encoding="utf-8"))
    return fields.get("记录类型", "").strip().lower() == "volatile"


def check_route_admission(case_dir: Path) -> HookResult:
    """Check route admission, with hard boundaries for A-class fast lane."""
    fields = case_fields(case_dir)
    task_class = fields.get("任务类别", "").strip()
    route = normalize_route(fields.get("当前建议链路"))
    data = {"task_class": task_class or "unknown", "route": route}
    if task_class != "A":
        return HookResult(True, warnings=["route-admission currently enforces only A fast lane"], data=data)

    errors: list[str] = []
    warnings: list[str] = []
    if route != A_FAST_LANE_ROUTE:
        errors.append(f"A task must use fast lane route: {A_FAST_LANE_ROUTE}")
    if normalize_route(fields.get("最小合法链路")) != A_FAST_LANE_ROUTE:
        errors.append(f"A task minimum legal route must be: {A_FAST_LANE_ROUTE}")
    if not meaningful(fields.get("首办官署")):
        errors.append("A task requires a named 首办官署")
    if not has_volatile_record(case_dir):
        errors.append("A task volatile-record.md is required as the lightweight record")

    dispatch_text = read_file(case_dir, "dispatch-order.md") or ""
    dispatch = dispatch_fields(case_dir)
    if "direct handling" in dispatch_text.lower():
        errors.append("A task must not use direct handling; use named local-office ownership")
    if dispatch.get("真实派发", "").strip().lower() in {"yes", "true"}:
        errors.append("A task must not use real-subagent dispatch")
    if dispatch.get("执行方式", "").strip().lower() not in {"local-office", "single-office", "单部执行", "本地单部"}:
        errors.append("A task execution method must be local-office/single-office")

    assignments = parse_dispatch_assignments(dispatch_text)
    if not assignments:
        errors.append("A task requires one named office assignment")
    elif len(assignments) > 1:
        errors.append("A task should use one office assignment")
    else:
        office = assignments[0].get("官署", "")
        if not meaningful(office):
            errors.append("A task assignment requires a named 官署")
        if assignments[0].get("分支执行", "").strip().lower() == "real-subagent":
            errors.append("A task assignment must not be real-subagent")

    for artifact in A_HEAVY_ARTIFACTS:
        if (case_dir / artifact).exists():
            errors.append(f"A task should not require heavy artifact by default: {artifact}")

    risk = fields.get("风险级别", "").strip().lower()
    if risk and risk not in {"low", "低", "minor"}:
        warnings.append("A task has non-low risk; consider upgrading to B")

    return HookResult(not errors, errors=errors, warnings=warnings, data=data)


def check_write_scope(write_paths: list[str], assignment: dict[str, str]) -> list[str]:
    errors: list[str] = []
    writable = split_items(assignment.get("可写范围") or assignment.get("所有权"))
    forbidden = split_items(assignment.get("禁写范围"))
    branch = assignment.get("分支编号", "unknown").strip() or "unknown"
    for path in write_paths:
        if any(path_in_scope(path, forbidden_scope) for forbidden_scope in forbidden):
            errors.append(f"branch {branch} writes forbidden scope: {path}")
        if writable and not any(path_in_scope(path, writable_scope) for writable_scope in writable):
            errors.append(f"branch {branch} writes outside writable scope: {path}")
    return errors


def check_dangerous_pre_action(command: str | None, assignment: dict[str, str], approval_evidence: str | None) -> list[str]:
    if not command:
        return []
    dangerous = find_dangerous_command(command)
    if not dangerous:
        return []
    branch = assignment.get("分支编号", "unknown").strip() or "unknown"
    policy = assignment.get("危险命令策略")
    if is_no_destructive_policy(policy):
        return [f"branch {branch} destructive command forbidden by policy: {dangerous}"]
    if is_approval_required_policy(policy) or meaningful(assignment.get("需额外批准动作")):
        if not has_substantive_reason(approval_evidence):
            return [f"branch {branch} dangerous command requires approval evidence: {dangerous}"]
    return []


def check_pre_action(
    case_dir: Path,
    *,
    office: str | None = None,
    branch_id: str | None = None,
    command: str | None = None,
    write_paths: list[str] | None = None,
    approval_evidence: str | None = None,
) -> HookResult:
    """Run a pre-action guard for command and write-boundary risk."""
    assignment = load_assignment(case_dir, office=office, branch_id=branch_id)
    if assignment is None:
        target = branch_id or office or "unknown"
        return HookResult(False, errors=[f"dispatch assignment not found for: {target}"])

    errors: list[str] = []
    errors.extend(check_write_scope(write_paths or [], assignment))
    errors.extend(check_dangerous_pre_action(command, assignment, approval_evidence))
    return HookResult(not errors, errors=errors, data={"assignment": assignment})


def append_execution_observation(
    case_dir: Path,
    *,
    office: str,
    summary: str,
    evidence: str,
    touched_files: list[str],
) -> Path:
    path = case_dir / "execution-observations.jsonl"
    observation = {
        "time": now_iso(),
        "office": office,
        "source": "harness_hooks.py post-action",
        "event": summary,
        "evidence": {
            "artifact": evidence,
            "touched_files": touched_files,
        },
        "candidate": "none",
        "promote_to": "none",
        "confidence": 1,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(observation, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def record_post_action(
    case_dir: Path,
    *,
    state: str,
    office: str,
    summary: str,
    evidence: str,
    touched_files: list[str] | None = None,
) -> HookResult:
    """Record a post-action checkpoint in the ledger and observation trace."""
    touched = touched_files or []
    event_path = append_event(case_dir, state=state, action="hook-post-action", office=office, summary=summary, evidence=evidence)
    observation_path = append_execution_observation(
        case_dir,
        office=office,
        summary=summary,
        evidence=evidence,
        touched_files=touched,
    )
    return HookResult(
        True,
        data={
            "event": str(event_path),
            "execution_observations": str(observation_path),
            "touched_files": touched,
        },
    )


def check_subagent_return(case_dir: Path, *, branch_id: str) -> HookResult:
    """Run the subagent-return lifecycle guard for one real-subagent branch."""
    assignment = load_assignment(case_dir, branch_id=branch_id)
    if assignment is None:
        return HookResult(False, errors=[f"dispatch assignment not found for branch: {branch_id}"])
    if assignment.get("分支执行") != "real-subagent":
        return HookResult(True, warnings=[f"branch {branch_id} is not marked real-subagent"])

    return_ref = assignment.get("回传物", "").strip()
    if not return_ref or not (case_dir / return_ref).exists():
        return HookResult(False, errors=[f"real-subagent branch {branch_id} return artifact is missing: {return_ref or 'n/a'}"])

    return_text = read_file(case_dir, return_ref) or ""
    return_fields = parse_fields(return_text)
    required_fields = ("案件编号", "分支编号", "所属官署", "工作包引用", "回传状态")
    errors = [f"real-subagent branch {branch_id} return is missing field: {field}" for field in required_fields if not meaningful(return_fields.get(field))]
    errors.extend(validate_touched_scope(case_dir, assignment))
    errors.extend(validate_dangerous_command_policy(case_dir, assignment))
    return HookResult(not errors, errors=errors, data={"return": return_ref})


def extract_event_summaries(ledger_text: str) -> list[str]:
    return [match.group(1).strip() for match in SUMMARY_RE.finditer(ledger_text)]


def detect_workflow_graduation(case_dir: Path) -> HookResult:
    """Warn when the trace shows a repeated stable task that may deserve automation."""
    ledger_text = read_file(case_dir, "event-ledger.md") or ""
    summaries = extract_event_summaries(ledger_text)
    counts: dict[str, int] = {}
    for summary in summaries:
        normalized = summary.lower().strip()
        counts[normalized] = counts.get(normalized, 0) + 1

    warnings: list[str] = []
    for summary, count in sorted(counts.items()):
        has_signal = any(token in summary for token in ("repeated", "stable", "deterministic", "重复", "稳定", "固定"))
        if count >= 3 and has_signal:
            warnings.append(f"workflow graduation candidate: repeated stable action seen {count} times: {summary}")

    return HookResult(True, warnings=warnings, data={"summaries_checked": len(summaries)})


def check_completion(case_dir: Path, *, phase: str = "completion") -> HookResult:
    """Run the main guard plus harness-level completion advisories."""
    guard = validate_case_dir(case_dir, phase=phase)
    graduation = detect_workflow_graduation(case_dir)
    errors = list(guard.errors)
    warnings = list(guard.warnings) + graduation.warnings
    return HookResult(
        guard.ok and not errors,
        errors=errors,
        warnings=warnings,
        data={
            "task_class": guard.task_class,
            "graduation": graduation.data,
        },
    )


def strip_diagnostic_prefix(complaint: str) -> str:
    stripped = complaint.strip()
    for prefix in ("诊断：", "追因：", "诊断:", "追因:"):
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return stripped


def infer_failure_location(complaint: str) -> str:
    lowered = complaint.lower()
    for location, keywords in FAILURE_LOCATION_KEYWORDS:
        if any(keyword.lower() in lowered for keyword in keywords):
            return location
    return "needs-review"


def field_from_file(case_dir: Path, file_name: str, field: str) -> str:
    text = read_file(case_dir, file_name) or ""
    return parse_fields(text).get(field, "missing")


def artifact_status(case_dir: Path, file_name: str) -> str:
    return file_name if (case_dir / file_name).exists() else f"{file_name} missing"


def render_dissatisfaction_diagnostic(case_dir: Path, *, complaint: str, failure_location: str) -> str:
    restated = strip_diagnostic_prefix(complaint)
    user_goal = field_from_file(case_dir, "case.md", "用户目标")
    constraints = field_from_file(case_dir, "case.md", "约束")
    success_criteria = field_from_file(case_dir, "zhongshu-plan.md", "成功标准")
    verification_result = field_from_file(case_dir, "verification.md", "结果")
    verification_risk = field_from_file(case_dir, "verification.md", "未覆盖风险")
    review_verdict = field_from_file(case_dir, "menxia-review.md", "结论")
    memorial_risk = field_from_file(case_dir, "memorial-report.md", "剩余风险")
    repair_checkpoint = "门下复核" if failure_location in {"verification", "reporting"} else "中书省 -> 门下省"
    guard = {
        "intake": "intake guard",
        "planning": "intake/planning guard",
        "execution": "action guard",
        "verification": "completion guard",
        "reporting": "completion/reporting guard",
        "preference capture": "learning guard",
    }.get(failure_location, "门下 diagnostic review")

    return "\n".join(
        [
            "# 不满意诊断单",
            "",
            "## 触发",
            "",
            f"- 用户原话：{complaint}",
            "- 诊断范围：current case package",
            f"- 当前案卷：{case_dir}",
            "",
            "## 不满意点复述",
            "",
            f"- {restated}",
            "",
            "## 原始承诺 / 成功标准对照",
            "",
            f"- 用户目标：{user_goal}",
            f"- 约束：{constraints}",
            f"- 成功标准：{success_criteria}",
            f"- 实际结果：验证结果={verification_result}; 门下结论={review_verdict}",
            "- 差距：需要门下省按用户不满意点复核确认",
            "",
            "## 失败位置判断",
            "",
            f"- intake：{'candidate' if failure_location == 'intake' else 'not primary from complaint keywords'}",
            f"- planning：{'candidate' if failure_location == 'planning' else 'not primary from complaint keywords'}",
            f"- execution：{'candidate' if failure_location == 'execution' else 'not primary from complaint keywords'}",
            f"- verification：{'candidate' if failure_location == 'verification' else 'not primary from complaint keywords'}",
            f"- reporting：{'candidate' if failure_location == 'reporting' else 'not primary from complaint keywords'}",
            f"- preference capture：{'candidate' if failure_location == 'preference capture' else 'not primary from complaint keywords'}",
            f"- 主要失败位置：{failure_location}",
            "",
            "## 证据链",
            "",
            f"- 对话证据：{restated}",
            f"- 案卷证据：case.md; zhongshu-plan.md; menxia-review.md; memorial-report.md; {artifact_status(case_dir, 'event-ledger.md')}",
            f"- 工具/测试证据：{artifact_status(case_dir, 'verification.md')}; 结果={verification_result}; 未覆盖风险={verification_risk}",
            "- 缺失证据：需要人工补入具体对话片段或失败现场，如果案卷未记录",
            "",
            "## 归责",
            "",
            "- agent failure：需要门下省确认",
            "- harness gap：若现有 guard 未拦住该失败，则记录为候选",
            "- unclear requirement：若原始目标/成功标准缺失，则记录为候选",
            "- insufficient verification：若验证证据缺失、过弱或与声明不匹配，则记录为候选",
            "- task uncertainty：若外部条件或需求本身不确定，则记录为候选",
            "- 主要归责：needs-review",
            "",
            "## 最小修复路线",
            "",
            f"- 下一 checkpoint：{repair_checkpoint}",
            "- 修复动作：补齐证据链，对照原成功标准重审，并只修正与不满意点直接相关的最小范围",
            "- 需要补证：失败现场、相关工具输出、原回奏或完成声明",
            f"- 防复发 guard/hook：{guard}",
            f"- 当前剩余风险：{memorial_risk}",
            "- 是否形成 learning/workflow 候选：由门下复核后决定",
            "",
        ]
    )


def create_dissatisfaction_diagnostic(
    case_dir: Path,
    *,
    complaint: str,
    output_name: str = "dissatisfaction-diagnostic.md",
) -> HookResult:
    """Generate an on-demand dissatisfaction diagnostic artifact."""
    if not complaint.strip():
        return HookResult(False, errors=["complaint is required"])
    failure_location = infer_failure_location(complaint)
    output_path = case_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_dissatisfaction_diagnostic(case_dir, complaint=complaint, failure_location=failure_location),
        encoding="utf-8",
    )
    return HookResult(
        True,
        data={
            "output": str(output_path),
            "failure_location": failure_location,
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run lightweight sxlb harness lifecycle hooks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    route = subparsers.add_parser("route-admission", help="Check route admission, including A fast lane boundaries.")
    route.add_argument("case_dir", type=Path)

    pre = subparsers.add_parser("pre-action", help="Check command/write-boundary risk before an action.")
    pre.add_argument("case_dir", type=Path)
    pre.add_argument("--office")
    pre.add_argument("--branch-id")
    pre.add_argument("--command", dest="action_command")
    pre.add_argument("--write-path", action="append", default=[])
    pre.add_argument("--approval-evidence")

    post = subparsers.add_parser("post-action", help="Record a post-action ledger and observation event.")
    post.add_argument("case_dir", type=Path)
    post.add_argument("--state", required=True)
    post.add_argument("--office", required=True)
    post.add_argument("--summary", required=True)
    post.add_argument("--evidence", required=True)
    post.add_argument("--touched-file", action="append", default=[])

    subagent = subparsers.add_parser("subagent-return", help="Check one real-subagent return artifact.")
    subagent.add_argument("case_dir", type=Path)
    subagent.add_argument("--branch-id", required=True)

    graduation = subparsers.add_parser("workflow-graduation", help="Detect repeated stable work that should graduate.")
    graduation.add_argument("case_dir", type=Path)

    completion = subparsers.add_parser("completion", help="Run main guard plus harness completion advisories.")
    completion.add_argument("case_dir", type=Path)
    completion.add_argument("--phase", choices=("startup", "completion"), default="completion")

    diagnostic = subparsers.add_parser("diagnose-dissatisfaction", help="Generate an on-demand dissatisfaction diagnostic artifact.")
    diagnostic.add_argument("case_dir", type=Path)
    diagnostic.add_argument("--complaint", required=True)
    diagnostic.add_argument("--output", default="dissatisfaction-diagnostic.md")
    return parser


def dispatch_cli(args: argparse.Namespace) -> HookResult:
    if args.command == "route-admission":
        return check_route_admission(args.case_dir)
    if args.command == "pre-action":
        return check_pre_action(
            args.case_dir,
            office=args.office,
            branch_id=args.branch_id,
            command=args.action_command,
            write_paths=args.write_path,
            approval_evidence=args.approval_evidence,
        )
    if args.command == "post-action":
        return record_post_action(
            args.case_dir,
            state=args.state,
            office=args.office,
            summary=args.summary,
            evidence=args.evidence,
            touched_files=args.touched_file,
        )
    if args.command == "subagent-return":
        return check_subagent_return(args.case_dir, branch_id=args.branch_id)
    if args.command == "workflow-graduation":
        return detect_workflow_graduation(args.case_dir)
    if args.command == "completion":
        return check_completion(args.case_dir, phase=args.phase)
    if args.command == "diagnose-dissatisfaction":
        return create_dissatisfaction_diagnostic(args.case_dir, complaint=args.complaint, output_name=args.output)
    raise ValueError(f"Unknown command: {args.command}")


def main() -> int:
    result = dispatch_cli(build_parser().parse_args())
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
