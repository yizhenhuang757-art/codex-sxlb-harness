#!/usr/bin/env python3
"""Validate that an sxlb case package satisfies the minimum hard-framework rules."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
TASK_CLASS_RE = re.compile(r"- 任务类别：\s*([A-D])\b")
FIELD_VALUE_RE = re.compile(r"^- ([^：\n]+)：\s*(.+)$", re.MULTILINE)
FORBIDDEN_TOKENS = ("thin court", "province only", "direct handling")

BASE_REQUIRED_FILES = (
    "case.md",
    "dispatch-order.md",
    "menxia-review.md",
    "memorial-report.md",
    "event-ledger.md",
)

PLAN_REQUIRED_CLASSES = {"B", "C", "D"}
LEARNING_REQUIRED_CLASSES = {"B", "C", "D"}
READINESS_REQUIRED_CLASSES = {"B", "C", "D"}
LEARNING_REQUIRED_FIELDS = ("type", "scope", "source", "confidence", "summary", "promote_to", "stale_when")
VERIFICATION_REQUIRED_FIELDS = (
    "验证目标",
    "受影响对象",
    "验证结论",
    "命令或动作",
    "结果",
    "失败项",
    "复验",
    "未覆盖风险",
    "行为断言/不变量",
    "测试有效性",
)
VERIFICATION_OPTIONAL_FIELDS = ("浏览器证据", "覆盖率证据")
RECORDS_ROUTING_FIELDS = ("canonical", "report-only", "restart-update", "no-writeback")
DISPATCH_SCOPE_FIELDS = ("可写范围", "危险命令策略", "需额外批准动作")
REAL_SUBAGENT_DISPATCH_FIELDS = ("切片类型", "交互模式", "blocked-by", "验收标准")
LEGAL_DISPATCH_READINESS = {"ready-for-agent", "ready-for-human", "needs-info", "blocked", "n/a"}
ACTUAL_TOUCHED_FIELDS = ("真实触达清单", "真实触达文件", "touched-files")
EXTERNAL_EVIDENCE_REQUIRED_FIELDS = (
    "调研问题",
    "来源清单",
    "来源类型",
    "检查日期",
    "来源可靠性",
    "可用结论",
    "不确定性",
    "决策影响",
)
LEGAL_SOURCE_TYPES = {"official", "repo", "paper", "data", "article", "opinion"}
EXECUTION_OBSERVATION_REQUIRED_FIELDS = (
    "time",
    "office",
    "source",
    "event",
    "evidence",
    "candidate",
    "promote_to",
    "confidence",
)
EXECUTION_OBSERVATION_PROMOTION_TARGETS = {"none", "learning-candidates.jsonl"}
EVENT_STATE_ARTIFACTS = {
    "中书拟制": "zhongshu-plan.md",
    "门下审议": "menxia-review.md",
    "门下复核": "menxia-review.md",
    "尚书派发": "dispatch-order.md",
    "待回奏": "memorial-report.md",
}
CAIFENG_EVIDENCE_STATES = {"证据包待审", "已入方案"}
EVIDENCE_ARTIFACT_NAMES = (
    "external-evidence.md",
    "external-evidence-package.md",
    "caifeng-evidence.md",
    "evidence-package.md",
)
DANGEROUS_COMMAND_RE = re.compile(
    r"(?<![\w-])("
    r"rm\s+-[^\n;]*[rf][^\n;]*|"
    r"git\s+reset\s+--hard|"
    r"git\s+checkout\s+--|"
    r"git\s+clean\s+-[^\n;]*[fd][^\n;]*|"
    r"git\s+push\s+--force(?:-with-lease)?|"
    r"drop\s+table|"
    r"dd\s+if=|"
    r"sudo\s+|"
    r"chmod\s+-R|"
    r"chown\s+-R|"
    r"pkill\s+|"
    r"kill\s+-9"
    r")",
    re.IGNORECASE,
)

REQUIRED_FIELDS = {
    "case.md": (
        "任务",
        "用户目标",
        "约束",
        "风险级别",
        "能力召回",
        "任务类别",
        "最小合法链路",
        "当前建议链路",
        "首办官署",
        "下一站",
    ),
    "zhongshu-plan.md": (
        "目标",
        "不做什么",
        "成功标准",
        "主任务",
        "子任务",
        "风险与未知",
        "任务类别",
        "推荐链路",
        "主要官署",
        "能力召回",
    ),
    "dispatch-order.md": (
        "当前阶段",
        "拓扑",
        "执行方式",
        "真实派发",
        "能力召回",
        "delegation 可用性",
        "本线办理理由",
        "返回审议点",
    ),
    "menxia-review.md": (
        "来源",
        "审议类型",
        "当前阶段",
        "审议范围",
        "结论",
        "主要依据",
        "合法链路检查",
        "官署归属检查",
        "真实派发检查",
        "返回状态",
        "是否准许回奏",
    ),
    "memorial-report.md": (
        "任务",
        "使用链路",
        "当前结果",
        "停止时状态",
        "门下复核依据",
        "关键决策",
        "验证证据",
        "未完成/未验证项",
        "剩余风险",
        "案卷归档",
        "canonical 更新",
        "restart 更新",
    ),
}


@dataclass
class GuardResult:
    ok: bool
    errors: list[str]
    warnings: list[str]
    task_class: str | None


def read_file(case_dir: Path, name: str) -> str | None:
    path = case_dir / name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def parse_task_class(case_text: str | None) -> str | None:
    if not case_text:
        return None
    match = TASK_CLASS_RE.search(case_text)
    return match.group(1) if match else None


def parse_fields(text: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in FIELD_VALUE_RE.findall(text)}


def extract_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    remainder = text[start + len(marker) :]
    next_heading = remainder.find("\n## ")
    if next_heading == -1:
        return remainder.strip()
    return remainder[:next_heading].strip()


def parse_dispatch_assignments(dispatch_text: str) -> list[dict[str, str]]:
    office_section = extract_section(dispatch_text, "官署分派")
    blocks = re.split(r"\n\s*\n(?=- 官署：)", office_section.strip())
    assignments: list[dict[str, str]] = []
    for block in blocks:
        fields = parse_fields(block)
        if "官署" in fields:
            assignments.append(fields)
    return assignments


def required_files_for(task_class: str | None) -> list[str]:
    required = list(BASE_REQUIRED_FILES)
    if task_class in PLAN_REQUIRED_CLASSES:
        required.append("zhongshu-plan.md")
    if task_class in LEARNING_REQUIRED_CLASSES:
        required.append("learning-candidates.jsonl")
    if task_class in READINESS_REQUIRED_CLASSES:
        required.append("artifact-registry.md")
        required.append("verification.md")
        required.append("records-routing.md")
    return required


def is_filled(value: str | None) -> bool:
    if value is None:
        return False
    stripped = value.strip()
    if not stripped:
        return False
    if PLACEHOLDER_RE.search(stripped):
        return False
    return True


def validate_learning_candidates(text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"learning-candidates.jsonl line {index} is not valid JSON: {exc.msg}")
            continue
        if not isinstance(candidate, dict):
            errors.append(f"learning-candidates.jsonl line {index} must be a JSON object")
            continue
        for field in LEARNING_REQUIRED_FIELDS:
            if field not in candidate:
                errors.append(f"learning candidate line {index} is missing field: {field}")
            elif phase == "completion" and not str(candidate[field]).strip():
                errors.append(f"learning candidate line {index} has empty field: {field}")
        scope = str(candidate.get("scope", "")).strip()
        if scope and scope not in {"case", "project", "agent"}:
            errors.append(f"learning candidate line {index} has invalid scope: {scope}")
        promote_to = str(candidate.get("promote_to", "")).strip()
        if promote_to and promote_to not in {"none", "project", "agent", "canonical", "skill"}:
            errors.append(f"learning candidate line {index} has invalid promote_to: {promote_to}")
        try:
            confidence = int(candidate.get("confidence", 0))
        except (TypeError, ValueError):
            errors.append(f"learning candidate line {index} has non-integer confidence")
        else:
            if confidence < 1 or confidence > 10:
                errors.append(f"learning candidate line {index} confidence must be 1-10")
    return errors


def is_temporary_archive_path(value: str | None) -> bool:
    if not value:
        return False
    path = value.strip().strip("`")
    return path == "/tmp" or path.startswith("/tmp/") or path == "/private/tmp" or path.startswith("/private/tmp/")


def split_scope_items(value: str | None) -> list[str]:
    if not value:
        return []
    normalized = value.replace("；", ",").replace("，", ",").replace(";", ",")
    return [item.strip().strip("`") for item in normalized.split(",") if item.strip()]


def parse_touched_file_list(text: str) -> list[str]:
    touched: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        touched.extend(split_scope_items(line))
    return touched


def truthy_required(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in {"required", "yes", "true", "must", "必须", "需要"}


def first_actual_touched_ref(fields: dict[str, str]) -> str | None:
    for field in ACTUAL_TOUCHED_FIELDS:
        value = fields.get(field)
        if is_filled(value):
            return value.strip()
    return None


def is_pathlike_scope(value: str) -> bool:
    return "/" in value or value.startswith(".")


def path_matches_scope(path: str, scope: str) -> bool:
    clean_path = path.strip().strip("`")
    clean_scope = scope.strip().strip("`")
    if not clean_path or not clean_scope or not is_pathlike_scope(clean_scope):
        return False
    return clean_path == clean_scope or clean_path.startswith(clean_scope.rstrip("/") + "/")


def validate_touched_scope(case_dir: Path, assignment: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if assignment.get("分支执行") != "real-subagent":
        return errors
    branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
    return_ref = assignment.get("回传物", "").strip()
    if not return_ref:
        return errors
    return_text = read_file(case_dir, return_ref)
    if not return_text:
        return errors
    return_fields = parse_fields(return_text)
    actual_ref = first_actual_touched_ref(return_fields)
    if truthy_required(assignment.get("真实触达审计")) and not actual_ref:
        errors.append(f"real-subagent branch {branch_id} requires actual touched-files evidence")
    if actual_ref:
        actual_text = read_file(case_dir, actual_ref)
        if actual_text is None:
            errors.append(f"Referenced actual touched-files evidence is missing: {actual_ref}")
            touched = []
        else:
            touched = parse_touched_file_list(actual_text)
    else:
        touched = split_scope_items(return_fields.get("触达文件/产物"))
    writable = split_scope_items(assignment.get("可写范围") or assignment.get("所有权"))
    forbidden = split_scope_items(assignment.get("禁写范围"))
    for item in touched:
        if any(path_matches_scope(item, forbidden_scope) for forbidden_scope in forbidden):
            errors.append(f"real-subagent branch {branch_id} touches forbidden scope: {item}")
        writable_scopes = [scope for scope in writable if is_pathlike_scope(scope)]
        if writable_scopes and not any(path_matches_scope(item, scope) for scope in writable_scopes):
            errors.append(f"real-subagent branch {branch_id} touched file outside writable scope: {item}")
    return errors


def is_no_destructive_policy(policy: str | None) -> bool:
    if not policy:
        return False
    lowered = policy.strip().lower()
    return "no destructive" in lowered or "禁止危险" in lowered or "不得执行危险" in lowered


def is_approval_required_policy(policy: str | None) -> bool:
    if not policy:
        return False
    lowered = policy.strip().lower()
    return "approval required" in lowered or "requires approval" in lowered or "需批准" in lowered or "需要批准" in lowered


def has_extra_approval_requirement(value: str | None) -> bool:
    if not is_filled(value):
        return False
    return value.strip().lower() not in {"none", "n/a", "not required", "not-needed"}


def find_dangerous_command(text: str | None) -> str | None:
    if not text:
        return None
    match = DANGEROUS_COMMAND_RE.search(text)
    if not match:
        return None
    return match.group(1).strip()


def parse_approval_ledger_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 6:
            continue
        if cells[0] in {"branch", "none"}:
            continue
        rows.append(
            {
                "branch": cells[0],
                "office": cells[1],
                "command": cells[2].strip("`"),
                "approval_status": cells[3].lower(),
                "approval_evidence": cells[4],
                "return": cells[5],
            }
        )
    return rows


def validate_approval_ledger(case_dir: Path, assignments: list[dict[str, str]]) -> list[str]:
    dangerous: list[tuple[str, dict[str, str]]] = []
    for assignment in assignments:
        if assignment.get("分支执行") != "real-subagent":
            continue
        return_ref = assignment.get("回传物", "").strip()
        if not return_ref:
            continue
        return_text = read_file(case_dir, return_ref)
        if not return_text:
            continue
        return_fields = parse_fields(return_text)
        if find_dangerous_command(return_fields.get("关键命令或动作", "")):
            branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
            dangerous.append((branch_id, assignment))

    if not dangerous:
        return []

    ledger_text = read_file(case_dir, "approval-ledger.md")
    if not ledger_text:
        return ["approval-ledger.md is required when dangerous commands appear in real-subagent returns"]

    rows = parse_approval_ledger_rows(ledger_text)
    by_branch = {row["branch"]: row for row in rows}
    errors: list[str] = []
    for branch_id, assignment in dangerous:
        row = by_branch.get(branch_id)
        if not row:
            errors.append(f"approval-ledger.md is missing dangerous branch entry: {branch_id}")
            continue
        if (is_approval_required_policy(assignment.get("危险命令策略")) or has_extra_approval_requirement(assignment.get("需额外批准动作"))) and row.get("approval_status") != "present":
            errors.append(f"approval-ledger.md branch {branch_id} must mark approval_status=present for approval-gated dangerous command")
    return errors


def requires_objection_review(case_dir: Path, assignments: list[dict[str, str]]) -> bool:
    memorial_text = read_file(case_dir, "memorial-report.md") or ""
    memorial_fields = parse_fields(memorial_text)
    if not has_substantive_reason(memorial_fields.get("canonical 更新")):
        return False
    for assignment in assignments:
        if assignment.get("分支执行") != "real-subagent":
            continue
        return_ref = assignment.get("回传物", "").strip()
        if not return_ref:
            continue
        return_text = read_file(case_dir, return_ref)
        if not return_text:
            continue
        return_fields = parse_fields(return_text)
        if find_dangerous_command(return_fields.get("关键命令或动作", "")):
            return True
    return False


def validate_dangerous_command_policy(case_dir: Path, assignment: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if assignment.get("分支执行") != "real-subagent":
        return errors
    branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
    return_ref = assignment.get("回传物", "").strip()
    if not return_ref:
        return errors
    return_text = read_file(case_dir, return_ref)
    if not return_text:
        return errors
    return_fields = parse_fields(return_text)
    command_note = return_fields.get("关键命令或动作", "")
    dangerous_command = find_dangerous_command(command_note)
    if not dangerous_command:
        return errors

    policy = assignment.get("危险命令策略")
    if is_no_destructive_policy(policy):
        errors.append(f"real-subagent branch {branch_id} destructive command forbidden by policy: {dangerous_command}")
        return errors

    if is_approval_required_policy(policy) or has_extra_approval_requirement(assignment.get("需额外批准动作")):
        if not has_substantive_reason(return_fields.get("额外批准证据")):
            errors.append(f"real-subagent branch {branch_id} requires extra approval evidence for dangerous command: {dangerous_command}")
    return errors


def validate_verification_matrix(text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    fields = parse_fields(text)
    for field in VERIFICATION_REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"verification.md is missing field: {field}")
        elif phase == "completion" and not has_substantive_reason(fields[field]):
            if field not in {"失败项", "复验", "未覆盖风险"}:
                errors.append(f"verification.md has non-substantive field at completion: {field}")
    if fields.get("结果", "").strip().lower() not in {"pass", "passed", "ok", "success"}:
        errors.append("verification.md field 结果 must show a passing verification result at completion")
    for field in VERIFICATION_OPTIONAL_FIELDS:
        if field in fields and phase == "completion" and not is_filled(fields[field]):
            errors.append(f"verification.md has unfilled optional field at completion: {field}")
    return errors


def validate_artifact_registry(text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    required_artifacts = ("case.md", "dispatch-order.md", "menxia-review.md", "memorial-report.md", "event-ledger.md", "verification.md", "learning-candidates.jsonl", "records-routing.md")
    for artifact in required_artifacts:
        if artifact not in text:
            errors.append(f"artifact-registry.md does not reference required artifact: {artifact}")
    if phase == "completion" and "blocking" not in text:
        errors.append("artifact-registry.md must expose blocking status")
    return errors


def validate_records_routing(text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    fields = parse_fields(text)
    for field in RECORDS_ROUTING_FIELDS:
        if field not in fields:
            errors.append(f"records-routing.md is missing field: {field}")
        elif phase == "completion" and not is_filled(fields[field]):
            errors.append(f"records-routing.md has non-substantive field at completion: {field}")
    return errors


def has_substantive_reason(value: str | None) -> bool:
    if not is_filled(value):
        return False
    return value.strip().lower() not in {"n/a", "none", "<n/a>", "not-needed"}


def validate_external_evidence_package(name: str, text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    fields = parse_fields(text)
    for field in EXTERNAL_EVIDENCE_REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"{name} is missing external evidence field: {field}")
        elif phase == "completion" and field == "不确定性" and is_none_like(fields[field]):
            continue
        elif phase == "completion" and not has_substantive_reason(fields[field]):
            errors.append(f"{name} has non-substantive external evidence field at completion: {field}")

    source_types = split_scope_items(fields.get("来源类型"))
    for source_type in source_types:
        if source_type not in LEGAL_SOURCE_TYPES:
            errors.append(f"{name} has invalid 来源类型: {source_type}")
    return errors


def validate_execution_observations(text: str, *, phase: str = "completion") -> list[str]:
    errors: list[str] = []
    for index, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            observation = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"execution-observations.jsonl line {index} is not valid JSON: {exc.msg}")
            continue
        if not isinstance(observation, dict):
            errors.append(f"execution-observations.jsonl line {index} must be a JSON object")
            continue
        for field in EXECUTION_OBSERVATION_REQUIRED_FIELDS:
            if field not in observation:
                errors.append(f"execution observation line {index} is missing field: {field}")
            elif phase == "completion" and field != "evidence" and not str(observation[field]).strip():
                errors.append(f"execution observation line {index} has empty field: {field}")
        evidence = observation.get("evidence")
        if "evidence" in observation and not isinstance(evidence, dict):
            errors.append(f"execution observation line {index} evidence must be a JSON object")
        promote_to = str(observation.get("promote_to", "")).strip()
        if promote_to and promote_to not in EXECUTION_OBSERVATION_PROMOTION_TARGETS:
            errors.append(f"execution observation line {index} has invalid promote_to: {promote_to}")
    return errors


def has_external_evidence_reference(case_dir: Path, file_texts: dict[str, str]) -> bool:
    for name in EVIDENCE_ARTIFACT_NAMES:
        if (case_dir / name).exists():
            return True
    zhongshu_text = file_texts.get("zhongshu-plan.md") or read_file(case_dir, "zhongshu-plan.md") or ""
    evidence_markers = (
        "外部证据包：",
        "采风证据：",
        "证据包：",
        "external-evidence.md",
        "external-evidence-package.md",
        "caifeng-evidence.md",
        "evidence-package.md",
    )
    return any(marker in zhongshu_text for marker in evidence_markers)


def validate_event_artifact_consistency(case_dir: Path, file_texts: dict[str, str]) -> list[str]:
    ledger = file_texts.get("event-ledger.md") or read_file(case_dir, "event-ledger.md")
    if not ledger:
        return []

    errors: list[str] = []
    for state, artifact in EVENT_STATE_ARTIFACTS.items():
        if f"状态：{state}" in ledger and not (case_dir / artifact).exists():
            errors.append(f"event-ledger.md state {state} requires {artifact}")

    caifeng_states = re.findall(r"采风：\s*([^\n]+)", ledger)
    for raw_state in caifeng_states:
        state = raw_state.strip()
        if state in CAIFENG_EVIDENCE_STATES and not has_external_evidence_reference(case_dir, file_texts):
            errors.append(
                f"event-ledger.md caifeng state {state} requires zhongshu-plan.md evidence reference or an external evidence package"
            )
    return errors


def is_none_like(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"none", "n/a", "not-needed", "not required", "无"}


def validate_dispatch_readiness(dispatch_fields: dict[str, str], assignments: list[dict[str, str]], *, phase: str = "completion") -> list[str]:
    if phase != "completion":
        return []
    errors: list[str] = []
    readiness = dispatch_fields.get("派发就绪状态", "").strip().lower()
    real_assignments = [assignment for assignment in assignments if assignment.get("分支执行") == "real-subagent"]
    if real_assignments and not readiness:
        errors.append("dispatch-order.md real-subagent dispatch is missing 派发就绪状态")
    if readiness and readiness not in LEGAL_DISPATCH_READINESS:
        errors.append(f"dispatch-order.md has invalid 派发就绪状态: {readiness}")
    if readiness == "ready-for-agent":
        for assignment in real_assignments:
            blocked_by = assignment.get("blocked-by", "")
            if blocked_by and not is_none_like(blocked_by):
                branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
                errors.append(f"dispatch branch {branch_id} is blocked but dispatch is marked ready-for-agent")
    for assignment in real_assignments:
        branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
        for field in REAL_SUBAGENT_DISPATCH_FIELDS:
            value = assignment.get(field)
            if field == "blocked-by":
                if not is_filled(value):
                    errors.append(f"real-subagent branch {branch_id} missing {field}")
            elif not has_substantive_reason(value):
                errors.append(f"real-subagent branch {branch_id} missing substantive {field}")
        interaction_mode = assignment.get("交互模式", "").strip().lower()
        if interaction_mode.startswith("afk") and any(token in interaction_mode for token in ("hitl", "human", "user", "用户", "人工", "决策")):
            errors.append(f"real-subagent branch {branch_id} mixes AFK with a human decision point")
        if interaction_mode.startswith("hitl") and not any(token in interaction_mode for token in ("+", ":", "：", "decision", "用户", "人工", "确认", "审议")):
            errors.append(f"real-subagent branch {branch_id} HITL mode must name the decision point")
    return errors


def validate_case_dir(case_dir: Path, *, phase: str = "completion") -> GuardResult:
    errors: list[str] = []
    warnings: list[str] = []

    case_text = read_file(case_dir, "case.md")
    task_class = parse_task_class(case_text)
    required_files = required_files_for(task_class)

    for name in required_files:
        if not (case_dir / name).exists():
            errors.append(f"Missing required file: {name}")

    available_files = [name for name in required_files if (case_dir / name).exists()]
    file_texts = {name: read_file(case_dir, name) or "" for name in available_files}

    for name, text in file_texts.items():
        for token in FORBIDDEN_TOKENS:
            if token in text:
                errors.append(f"{name} contains forbidden legacy route token: {token}")

    for name, fields in REQUIRED_FIELDS.items():
        if name not in file_texts:
            continue
        parsed = parse_fields(file_texts[name])
        for field in fields:
            if field not in parsed:
                errors.append(f"{name} is missing field: {field}")
            elif phase == "completion" and not is_filled(parsed[field]):
                errors.append(f"{name} has unfilled field at completion: {field}")

    if phase == "completion":
        for name, text in file_texts.items():
            if PLACEHOLDER_RE.search(text):
                errors.append(f"{name} still contains template placeholders at completion")

    if "learning-candidates.jsonl" in file_texts:
        if phase == "completion" and task_class in LEARNING_REQUIRED_CLASSES and not file_texts["learning-candidates.jsonl"].strip():
            errors.append("learning-candidates.jsonl must contain a learning candidate or an explicit no-learning record at completion")
        errors.extend(validate_learning_candidates(file_texts["learning-candidates.jsonl"], phase=phase))
    if "verification.md" in file_texts:
        errors.extend(validate_verification_matrix(file_texts["verification.md"], phase=phase))
    if "artifact-registry.md" in file_texts:
        errors.extend(validate_artifact_registry(file_texts["artifact-registry.md"], phase=phase))
    if "records-routing.md" in file_texts:
        errors.extend(validate_records_routing(file_texts["records-routing.md"], phase=phase))
    for evidence_name in EVIDENCE_ARTIFACT_NAMES:
        evidence_text = read_file(case_dir, evidence_name)
        if evidence_text is not None:
            errors.extend(validate_external_evidence_package(evidence_name, evidence_text, phase=phase))
    observations_text = read_file(case_dir, "execution-observations.jsonl")
    if observations_text is not None:
        errors.extend(validate_execution_observations(observations_text, phase=phase))
    errors.extend(validate_event_artifact_consistency(case_dir, file_texts))

    if "case.md" in file_texts:
        case_fields = parse_fields(file_texts["case.md"])
        chain = case_fields.get("当前建议链路", "")
        if phase == "completion" and "门下复核" not in chain:
            errors.append("case.md current chain does not include 门下复核")
        if phase == "completion" and is_temporary_archive_path(case_fields.get("案卷路径")):
            errors.append("case.md 案卷路径 cannot remain in a temporary directory at completion")

    if "dispatch-order.md" in file_texts:
        dispatch_text = file_texts["dispatch-order.md"]
        dispatch_fields = parse_fields(dispatch_text)
        assignments = parse_dispatch_assignments(dispatch_text)
        topology = dispatch_fields.get("拓扑", "")
        real_dispatch = dispatch_fields.get("真实派发", "").lower()
        availability = dispatch_fields.get("delegation 可用性", "").lower()
        local_reason = dispatch_fields.get("本线办理理由", "")
        merge_summary = dispatch_fields.get("合流摘要", "")
        merge_required = dispatch_fields.get("合流要求", "").lower()

        if phase == "completion" and "parallel" in topology and availability == "available" and real_dispatch != "yes":
            if not has_substantive_reason(local_reason):
                errors.append("dispatch-order.md must explain why a delegable parallel branch stayed local")

        for assignment in assignments:
            branch_id = assignment.get("分支编号", "unknown").strip() or "unknown"
            for scope_field in DISPATCH_SCOPE_FIELDS:
                if phase == "completion" and not is_filled(assignment.get(scope_field)):
                    errors.append(f"dispatch branch {branch_id} missing {scope_field}")
            if phase == "completion":
                errors.extend(validate_touched_scope(case_dir, assignment))
                errors.extend(validate_dangerous_command_policy(case_dir, assignment))
        if phase == "completion":
            errors.extend(validate_approval_ledger(case_dir, assignments))
            if requires_objection_review(case_dir, assignments) and not (case_dir / "objection-review.md").exists():
                errors.append("objection-review.md is required for dangerous-command cases with canonical updates")
            errors.extend(validate_dispatch_readiness(dispatch_fields, assignments, phase=phase))

        real_assignments = [assignment for assignment in assignments if assignment.get("分支执行") == "real-subagent"]
        if real_dispatch == "yes":
            if not real_assignments:
                errors.append("dispatch-order.md claims real dispatch but has no real-subagent branch assignments")
            for assignment in real_assignments:
                branch_id = assignment.get("分支编号", "").strip()
                packet_ref = assignment.get("工作包", "").strip()
                return_ref = assignment.get("回传物", "").strip()
                if not branch_id:
                    errors.append("real-subagent branch is missing 分支编号")
                    continue
                if phase == "completion" and not is_filled(packet_ref):
                    errors.append(f"real-subagent branch {branch_id} is missing 工作包")
                if phase == "completion" and not is_filled(return_ref):
                    errors.append(f"real-subagent branch {branch_id} is missing 回传物")
                if packet_ref and not (case_dir / packet_ref).exists():
                    errors.append(f"Referenced subagent packet is missing: {packet_ref}")
                if phase == "completion" and return_ref and not (case_dir / return_ref).exists():
                    errors.append(f"Referenced subagent return is missing: {return_ref}")

            if merge_required in {"yes", "merge required", "required"} or len(real_assignments) > 1 or "parallel" in topology:
                if phase == "completion" and not is_filled(merge_summary):
                    errors.append("dispatch-order.md requires 合流摘要 for merge-dependent real dispatch")
                elif merge_summary and not (case_dir / merge_summary).exists():
                    errors.append(f"Referenced merge summary is missing: {merge_summary}")

    if "menxia-review.md" in file_texts:
        review_fields = parse_fields(file_texts["menxia-review.md"])
        if phase == "completion":
            if review_fields.get("审议类型") != "completion":
                errors.append("menxia-review.md must record a completion review before memorialization")
            if review_fields.get("是否准许回奏") != "yes":
                errors.append("menxia-review.md must explicitly allow memorialization before completion")
            if "dispatch-order.md" in file_texts:
                dispatch_fields = parse_fields(file_texts["dispatch-order.md"])
                if dispatch_fields.get("真实派发", "").lower() == "yes":
                    for field in ("工作包输入", "回传输入", "合流输入"):
                        if not is_filled(review_fields.get(field)):
                            errors.append(f"menxia-review.md must include {field} for real-subagent completion review")

    if "event-ledger.md" in file_texts and phase == "completion":
        ledger = file_texts["event-ledger.md"]
        needed_actions = ["intake", "dispatch", "memorial"]
        if task_class in PLAN_REQUIRED_CLASSES:
            needed_actions.extend(["plan", "review"])
        for action in needed_actions:
            if f"动作：{action}" not in ledger:
                errors.append(f"event-ledger.md is missing required action: {action}")

    if not task_class and phase == "completion":
        warnings.append("Could not determine task class from case.md; treating plan requirements conservatively.")

    return GuardResult(ok=not errors, errors=errors, warnings=warnings, task_class=task_class)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an sxlb case package.")
    parser.add_argument("case_dir", type=Path, help="Case/worklog directory to validate")
    parser.add_argument("--phase", choices=("startup", "completion"), default="completion")
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def format_result(result: GuardResult) -> str:
    lines = [f"ok: {str(result.ok).lower()}"]
    if result.task_class:
        lines.append(f"task_class: {result.task_class}")
    if result.errors:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in result.errors)
    if result.warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in result.warnings)
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    result = validate_case_dir(args.case_dir, phase=args.phase)
    if args.json_output:
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "task_class": result.task_class,
                    "errors": result.errors,
                    "warnings": result.warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(format_result(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
