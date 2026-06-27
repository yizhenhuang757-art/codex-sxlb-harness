#!/usr/bin/env python3
"""Create and manage real subagent dispatch artifacts for an sxlb case package."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from touched_files import write_touched_files


FIELD_VALUE_RE = re.compile(r"^- ([^：\n]+)：\s*(.+)$", re.MULTILINE)

SUBAGENTS_DIRNAME = "subagents"
RETURNS_DIRNAME = "returns"
MANIFEST_NAME = "manifest.json"
MERGE_SUMMARY_NAME = "merge-summary.md"
HEAVY_DISPATCH_STATE_NAME = "heavy-dispatch-state.md"
EXECUTION_OBSERVATIONS_NAME = "execution-observations.jsonl"


@dataclass
class OfficeAssignment:
    branch_id: str
    office: str
    task: str
    slice_type: str
    interaction_mode: str
    blocked_by: str
    acceptance_criteria: str
    ownership: str
    shared_readonly: str
    forbidden_scope: str
    writable_scope: str
    actual_touched_audit: str
    dangerous_policy: str
    extra_approvals: str
    integrator: str
    allowed_skills: str
    boundary: str
    execution: str


@dataclass
class CaseContext:
    task: str
    goal: str
    constraints: str
    task_class: str
    chain: str
    review_return_point: str
    dispatch_stage: str
    topology: str
    execution_mode: str
    real_dispatch: str
    capability_recall: str
    admission_result: str
    cost_judgment: str
    delegation_availability: str
    local_reason: str
    merge_checkpoint: str
    merge_owner: str
    assignments: list[OfficeAssignment]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def parse_assignments(dispatch_text: str) -> list[OfficeAssignment]:
    office_section = extract_section(dispatch_text, "官署分派")
    assignments: list[OfficeAssignment] = []
    blocks = re.split(r"\n\s*\n(?=- 官署：)", office_section.strip())
    for block in blocks:
        fields = parse_fields(block)
        if "官署" not in fields:
            continue
        assignments.append(
            OfficeAssignment(
                branch_id=fields.get("分支编号", "").strip(),
                office=fields.get("官署", "").strip(),
                task=fields.get("任务", "").strip(),
                slice_type=fields.get("切片类型", "").strip(),
                interaction_mode=fields.get("交互模式", "").strip(),
                blocked_by=fields.get("blocked-by", "").strip(),
                acceptance_criteria=fields.get("验收标准", "").strip(),
                ownership=fields.get("所有权", "").strip(),
                shared_readonly=fields.get("共享只读", "").strip(),
                forbidden_scope=fields.get("禁写范围", "").strip(),
                writable_scope=fields.get("可写范围", "").strip(),
                actual_touched_audit=fields.get("真实触达审计", "").strip(),
                dangerous_policy=fields.get("危险命令策略", "").strip(),
                extra_approvals=fields.get("需额外批准动作", "").strip(),
                integrator=fields.get("整合者", "").strip(),
                allowed_skills=fields.get("允许技能", "").strip(),
                boundary=fields.get("禁止越权", "").strip(),
                execution=fields.get("分支执行", "").strip(),
            )
        )
    return assignments


def load_case_context(case_dir: Path) -> CaseContext:
    case_path = case_dir / "case.md"
    dispatch_path = case_dir / "dispatch-order.md"
    if not case_path.exists():
        raise FileNotFoundError(f"Missing case file: {case_path}")
    if not dispatch_path.exists():
        raise FileNotFoundError(f"Missing dispatch file: {dispatch_path}")

    case_fields = parse_fields(read_text(case_path))
    dispatch_text = read_text(dispatch_path)
    dispatch_fields = parse_fields(dispatch_text)
    assignments = parse_assignments(dispatch_text)

    if not assignments:
        raise ValueError("dispatch-order.md does not contain any office assignments")

    return CaseContext(
        task=case_fields.get("任务", ""),
        goal=case_fields.get("用户目标", ""),
        constraints=case_fields.get("约束", ""),
        task_class=case_fields.get("任务类别", ""),
        chain=case_fields.get("当前建议链路", ""),
        review_return_point=dispatch_fields.get("返回审议点", ""),
        dispatch_stage=dispatch_fields.get("当前阶段", ""),
        topology=dispatch_fields.get("拓扑", ""),
        execution_mode=dispatch_fields.get("执行方式", ""),
        real_dispatch=dispatch_fields.get("真实派发", ""),
        capability_recall=dispatch_fields.get("能力召回", ""),
        admission_result=dispatch_fields.get("多 agent 准入", ""),
        cost_judgment=dispatch_fields.get("成本判断", ""),
        delegation_availability=dispatch_fields.get("delegation 可用性", ""),
        local_reason=dispatch_fields.get("本线办理理由", ""),
        merge_checkpoint=dispatch_fields.get("合流点", ""),
        merge_owner=dispatch_fields.get("合流负责", ""),
        assignments=assignments,
    )


def load_manifest(case_dir: Path) -> dict[str, Any]:
    manifest_path = case_dir / SUBAGENTS_DIRNAME / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest_path}")
    return json.loads(read_text(manifest_path))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_branch_id(raw: str | None, fallback_index: int) -> str:
    if raw:
        return raw.strip()
    return f"office-{fallback_index:02d}"


def render_packet(case_dir: Path, packet_id: str, context: CaseContext, assignment: OfficeAssignment) -> str:
    case_id = case_dir.name
    writable_scope = assignment.writable_scope or assignment.ownership
    forbidden_scope = assignment.forbidden_scope or f"除 `{writable_scope}` 之外的文件、产物与决策范围"
    actual_touched_audit = assignment.actual_touched_audit or "not required"
    slice_type = assignment.slice_type or "unspecified"
    interaction_mode = assignment.interaction_mode or "unspecified"
    blocked_by = assignment.blocked_by or "none"
    acceptance_criteria = assignment.acceptance_criteria or f"在 `{context.review_return_point}` 前交付可复核回传物"
    touched_command = (
        "python3 $SXLB_HOME/scripts/touched_files.py "
        f"--repo <repo> --output <case-dir>/subagents/returns/touched-files-{packet_id}.txt"
    )
    return "\n".join(
        [
            "# 子代理工作包",
            "",
            "## 工作包信息",
            "",
            f"- 案件编号：{case_id}",
            f"- 分支编号：{packet_id}",
            f"- 所属官署：{assignment.office}",
            "- 执行方式：real-subagent",
            "- 派发来源：dispatch-order.md",
            f"- 返回物：subagent-return-{packet_id}.md",
            "",
            "## 任务目标",
            "",
            f"- 目标：{assignment.task}",
            f"- 切片类型：{slice_type}",
            f"- 交互模式：{interaction_mode}",
            f"- blocked-by：{blocked_by}",
            f"- 成功标准：在 `{context.review_return_point}` 前交付可复核回传物",
            f"- 验收标准：{acceptance_criteria}",
            f"- 不做什么：越出 `{assignment.ownership}` 的写入边界；忽略 `{assignment.boundary}`",
            "",
            "## 边界",
            "",
            f"- 可写范围：{writable_scope}",
            f"- 共享只读：{assignment.shared_readonly}",
            f"- 禁写范围：{forbidden_scope}",
            f"- 真实触达审计：{actual_touched_audit}",
            f"- 危险命令策略：{assignment.dangerous_policy or 'not specified'}",
            f"- 需额外批准动作：{assignment.extra_approvals or 'not specified'}",
            f"- 禁止越权：{assignment.boundary}",
            "",
            "## 允许方法",
            "",
            f"- 允许技能：{assignment.allowed_skills}",
            "- 允许工具：按宿主环境与本分支需要执行",
            "- 强制方法：边界不清时先回传，不自行扩权",
            "",
            "## 回传要求",
            "",
            "- 必交内容：summary / evidence / touched files / risks / next step / boundary statement",
            f"- 真实触达清单生成：{touched_command if actual_touched_audit.lower() == 'required' else 'not required'}",
            f"- 回传时机：完成本分支目标，或在 `{context.merge_checkpoint or context.review_return_point}` 前需要升级时",
            "- 升级条件：遇到边界冲突、共享写冲突、证据不足、或需调整派发",
            f"- 需要谁来合流：{context.merge_owner or assignment.integrator}",
            "",
            "## 最小上下文包",
            "",
            "- 必读材料：case.md, dispatch-order.md",
            f"- 背景摘要：任务 `{context.task}`；目标 `{context.goal}`；约束 `{context.constraints}`；链路 `{context.chain}`",
        ]
    )


def _merge_existing_packet_state(
    existing_packets: list[dict[str, Any]],
    packets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    existing_by_id = {packet["packet_id"]: packet for packet in existing_packets}
    merged: list[dict[str, Any]] = []
    for packet in packets:
        previous = existing_by_id.get(packet["packet_id"], {})
        merged_packet = dict(packet)
        for key in ("return_status", "return_summary", "return_file", "last_updated"):
            if key in previous and key not in merged_packet:
                merged_packet[key] = previous[key]
        merged.append(merged_packet)
    return merged


def should_write_heavy_state(context: CaseContext) -> bool:
    return (
        context.admission_result.strip().lower() == "pass"
        and context.real_dispatch.strip().lower() == "yes"
    )


def _branch_runtime_status(packet: dict[str, Any]) -> str:
    status = packet.get("return_status", "pending")
    if status in {"completed", "complete", "done", "returned"}:
        return "returned"
    if status in {"blocked", "running", "recalled", "closed", "merged"}:
        return status
    return "queued"


def _branch_verification_status(packet: dict[str, Any]) -> str:
    status = packet.get("return_status", "pending")
    verification = packet.get("verification", "")
    if status in {"completed", "complete", "done", "returned"}:
        return "pass" if verification and verification != "not provided" else "pending"
    if status == "failed":
        return "fail"
    return "pending"


def render_heavy_dispatch_state(manifest: dict[str, Any], *, timestamp: str) -> str:
    lines = [
        "# Heavy Dispatch State",
        "",
        "## State Header",
        "",
        f"- 案件编号：{Path(manifest.get('case_dir', '')).name or 'n/a'}",
        "- heavy layer：active",
        f"- 启动依据：多 agent 准入：{manifest.get('admission_result', '')}; 真实派发：{manifest.get('real_dispatch', '')}",
        "- 状态来源：subagents/manifest.json",
        f"- 合流负责：{manifest.get('merge_owner', '') or 'n/a'}",
        f"- 最后更新：{timestamp}",
        "",
        "## Branches",
        "",
    ]
    for packet in manifest.get("packets", []):
        return_file = packet.get("return_file", "pending")
        lines.extend(
            [
                f"- 分支编号：{packet['packet_id']}",
                f"- 官署：{packet['office']}",
                "- 执行环境：shared-repo",
                f"- 可写范围：{packet.get('writable_scope') or packet.get('ownership') or 'n/a'}",
                f"- 状态：{_branch_runtime_status(packet)}",
                f"- 工作包：{packet['packet_file']}",
                f"- 回传物：{return_file}",
                f"- 验证状态：{_branch_verification_status(packet)}",
                "- 合流状态：pending",
                f"- 最后实质更新：{packet.get('last_updated', timestamp)}",
                "",
            ]
        )
    unclosed = [
        packet["packet_id"]
        for packet in manifest.get("packets", [])
        if _branch_runtime_status(packet) not in {"returned", "merged", "closed", "recalled"}
    ]
    lines.extend(
        [
            "## Shutdown",
            "",
            "- 关闭状态：not-started",
            f"- 未闭合分支：{', '.join(unclosed) if unclosed else 'none'}",
            "- 门下复核输入：dispatch + packets + returns + merge + verification",
            "",
        ]
    )
    return "\n".join(lines)


def write_heavy_dispatch_state(case_dir: Path, manifest: dict[str, Any], timestamp: str) -> Path:
    state_path = case_dir / HEAVY_DISPATCH_STATE_NAME
    write_text(state_path, render_heavy_dispatch_state(manifest, timestamp=timestamp))
    return state_path


def append_execution_observation(case_dir: Path, observation: dict[str, Any]) -> Path:
    observations_path = case_dir / EXECUTION_OBSERVATIONS_NAME
    observations_path.parent.mkdir(parents=True, exist_ok=True)
    with observations_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(observation, ensure_ascii=False, sort_keys=True) + "\n")
    return observations_path


def create_dispatch_bundle(case_dir: Path, *, force: bool = False) -> list[Path]:
    context = load_case_context(case_dir)
    real_assignments = [assignment for assignment in context.assignments if assignment.execution == "real-subagent"]
    if not real_assignments:
        raise ValueError("dispatch-order.md does not mark any office as real-subagent")

    subagents_dir = case_dir / SUBAGENTS_DIRNAME
    returns_dir = subagents_dir / RETURNS_DIRNAME
    subagents_dir.mkdir(parents=True, exist_ok=True)
    returns_dir.mkdir(parents=True, exist_ok=True)

    existing_manifest: dict[str, Any] | None = None
    manifest_path = subagents_dir / MANIFEST_NAME
    if manifest_path.exists():
        existing_manifest = json.loads(read_text(manifest_path))

    created: list[Path] = []
    packets: list[dict[str, Any]] = []
    for index, assignment in enumerate(real_assignments, start=1):
        packet_id = normalize_branch_id(assignment.branch_id, index)
        packet_filename = f"subagent-work-packet-{packet_id}.md"
        packet_path = subagents_dir / packet_filename
        packets.append(
            {
                "packet_id": packet_id,
                "packet_file": f"{SUBAGENTS_DIRNAME}/{packet_filename}",
                "office": assignment.office,
                "task": assignment.task,
                "slice_type": assignment.slice_type,
                "interaction_mode": assignment.interaction_mode,
                "blocked_by": assignment.blocked_by,
                "acceptance_criteria": assignment.acceptance_criteria,
                "ownership": assignment.ownership,
                "shared_readonly": assignment.shared_readonly,
                "forbidden_scope": assignment.forbidden_scope,
                "writable_scope": assignment.writable_scope,
                "actual_touched_audit": assignment.actual_touched_audit,
                "dangerous_policy": assignment.dangerous_policy,
                "extra_approvals": assignment.extra_approvals,
                "integrator": assignment.integrator,
                "allowed_skills": assignment.allowed_skills,
                "boundary": assignment.boundary,
                "execution": assignment.execution,
            }
        )
        if packet_path.exists() and not force:
            continue
        write_text(packet_path, render_packet(case_dir, packet_id, context, assignment))
        created.append(packet_path)

    packet_entries = packets
    if existing_manifest and not force:
        packet_entries = _merge_existing_packet_state(existing_manifest.get("packets", []), packets)

    manifest = {
        "case_dir": str(case_dir),
        "generated_at": now_iso(),
        "task": context.task,
        "goal": context.goal,
        "task_class": context.task_class,
        "chain": context.chain,
        "dispatch_stage": context.dispatch_stage,
        "topology": context.topology,
        "execution_mode": context.execution_mode,
        "real_dispatch": context.real_dispatch,
        "admission_result": context.admission_result,
        "cost_judgment": context.cost_judgment,
        "delegation_availability": context.delegation_availability,
        "review_return_point": context.review_return_point,
        "merge_checkpoint": context.merge_checkpoint,
        "merge_owner": context.merge_owner,
        "packets": packet_entries,
    }
    write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if manifest_path not in created:
        created.append(manifest_path)
    if should_write_heavy_state(context):
        state_path = write_heavy_dispatch_state(case_dir, manifest, manifest["generated_at"])
        if state_path not in created:
            created.append(state_path)
    return created


def find_packet(manifest: dict[str, Any], packet_id: str) -> dict[str, Any]:
    for packet in manifest.get("packets", []):
        if packet.get("packet_id") == packet_id:
            return packet
    raise KeyError(f"Unknown packet_id: {packet_id}")


def render_return(
    packet: dict[str, Any],
    *,
    status: str,
    summary: str,
    touched_artifacts: list[str],
    actual_touched_file: str | None,
    verification: str,
    approval_evidence: str,
    risks: str,
    next_step: str,
) -> str:
    lines = [
        "# 子代理回传物",
        "",
        "## 基本信息",
        "",
        f"- 案件编号：n/a",
        f"- 分支编号：{packet['packet_id']}",
        f"- 所属官署：{packet['office']}",
        f"- 工作包引用：subagent-work-packet-{packet['packet_id']}.md",
        f"- 回传状态：{status}",
        "",
        "## 结果摘要",
        "",
        f"- 已完成内容：{summary}",
        "- 未完成内容：none",
        f"- 关键判断：{next_step}",
        "",
        "## 证据与产物",
        "",
        f"- 触达文件/产物：{', '.join(touched_artifacts) if touched_artifacts else 'none'}",
        f"- 真实触达清单：{actual_touched_file or 'n/a'}",
        f"- 新增证据：{verification}",
        f"- 额外批准证据：{approval_evidence}",
        f"- 关键命令或动作：recorded via subagent_dispatch.py at {now_iso()}",
        "",
        "## 边界声明",
        "",
        "- 是否越权：no",
        "- 边界异常：none",
        "- 需要召回或调整派发：no",
        "",
        "## 合流输入",
        "",
        "- 对其他分支的依赖：none",
        "- 已知冲突：none",
        f"- 建议下一步：{next_step}",
        f"- 剩余风险：{risks}",
        "",
        "## 涉及产物明细",
        "",
    ]
    if touched_artifacts:
        lines.extend(f"- {artifact}" for artifact in touched_artifacts)
    else:
        lines.append("- none")
    return "\n".join(lines)


def record_subagent_return(
    case_dir: Path,
    *,
    packet_id: str,
    status: str,
    summary: str,
    touched_artifacts: list[str] | None = None,
    touched_files_repo: Path | None = None,
    verification: str = "not provided",
    approval_evidence: str = "n/a",
    risks: str = "none",
    next_step: str = "n/a",
) -> Path:
    manifest = load_manifest(case_dir)
    packet = find_packet(manifest, packet_id)
    touched = touched_artifacts or []
    returns_dir = case_dir / SUBAGENTS_DIRNAME / RETURNS_DIRNAME
    actual_touched_file: str | None = None
    if touched_files_repo is not None:
        touched_path = returns_dir / f"touched-files-{packet_id}.txt"
        write_touched_files(touched_files_repo, touched_path)
        try:
            actual_touched_file = touched_path.relative_to(case_dir).as_posix()
        except ValueError:
            actual_touched_file = str(touched_path)
    return_path = returns_dir / f"subagent-return-{packet_id}.md"
    write_text(
        return_path,
        render_return(
            packet,
            status=status,
            summary=summary,
            touched_artifacts=touched,
            actual_touched_file=actual_touched_file,
            verification=verification,
            approval_evidence=approval_evidence,
            risks=risks,
            next_step=next_step,
        ),
    )

    for entry in manifest.get("packets", []):
        if entry.get("packet_id") == packet_id:
            entry["return_status"] = status
            entry["return_summary"] = summary
            entry["return_file"] = f"{SUBAGENTS_DIRNAME}/{RETURNS_DIRNAME}/{return_path.name}"
            if approval_evidence != "n/a":
                entry["approval_evidence"] = approval_evidence
            if actual_touched_file:
                entry["actual_touched_file"] = actual_touched_file
            entry["verification"] = verification
            entry["last_updated"] = now_iso()
            break

    manifest["generated_at"] = now_iso()
    write_text(case_dir / SUBAGENTS_DIRNAME / MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    state_path = case_dir / HEAVY_DISPATCH_STATE_NAME
    if state_path.exists() or (
        manifest.get("admission_result", "").strip().lower() == "pass"
        and manifest.get("real_dispatch", "").strip().lower() == "yes"
    ):
        write_heavy_dispatch_state(case_dir, manifest, manifest["generated_at"])
    append_execution_observation(
        case_dir,
        {
            "time": manifest["generated_at"],
            "office": packet.get("office", ""),
            "source": "subagent_dispatch.record",
            "event": "subagent-return-recorded",
            "evidence": {
                "packet_id": packet_id,
                "status": status,
                "summary": summary,
                "return_file": f"{SUBAGENTS_DIRNAME}/{RETURNS_DIRNAME}/{return_path.name}",
                "verification": verification,
                "touched_artifacts": touched,
                "actual_touched_file": actual_touched_file or "n/a",
            },
            "candidate": "Worker return captured as case-level execution evidence.",
            "promote_to": "learning-candidates.jsonl",
            "confidence": "medium",
        },
    )
    return return_path


def build_merge_summary(case_dir: Path, *, force: bool = False) -> Path:
    manifest = load_manifest(case_dir)
    summary_path = case_dir / SUBAGENTS_DIRNAME / MERGE_SUMMARY_NAME
    if summary_path.exists() and not force:
        return summary_path

    completed = 0
    pending: list[dict[str, Any]] = []
    lines = [
        "# 子代理合流摘要",
        "",
        "## 合流总览",
        "",
        f"- 案卷：{manifest.get('case_dir', case_dir)}",
        f"- 派发阶段：{manifest.get('dispatch_stage', '')}",
        f"- 拓扑：{manifest.get('topology', '')}",
        f"- 合流点：{manifest.get('merge_checkpoint', '') or manifest.get('review_return_point', '')}",
        f"- 合流负责：{manifest.get('merge_owner', '') or 'n/a'}",
        "",
        "## 分支状态",
        "",
    ]

    for packet in manifest.get("packets", []):
        status = packet.get("return_status", "pending")
        if status != "pending":
            completed += 1
        else:
            pending.append(packet)
        lines.extend(
            [
                f"### {packet['packet_id']} {packet['office']}",
                f"- 状态：{status}",
                f"- 任务：{packet['task']}",
                f"- 摘要：{packet.get('return_summary', 'pending')}",
                f"- 回传文件：{packet.get('return_file', 'pending')}",
                "",
            ]
        )

    lines.extend(
        [
            "## 合流判断",
            "",
            f"- 已回传分支：{completed}/{len(manifest.get('packets', []))}",
            f"- 是否可进入门下复核：{'yes' if not pending else 'no'}",
        ]
    )
    if pending:
        lines.append("- 待补分支：" + ", ".join(packet["packet_id"] for packet in pending))
    else:
        lines.append("- 待补分支：none")

    lines.extend(
        [
            "",
            "## 下一步建议",
            "",
            "- 建议动作：" + ("进入门下复核" if not pending else "继续催办未回传分支"),
        ]
    )

    write_text(summary_path, "\n".join(lines) + "\n")
    return summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage real subagent dispatch artifacts for an sxlb case package.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create packet files and manifest for real-subagent assignments")
    create_parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    create_parser.add_argument("--force", action="store_true", help="Overwrite packet files and manifest")

    record_parser = subparsers.add_parser("record", help="Record a subagent return for a packet")
    record_parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    record_parser.add_argument("--packet-id", required=True, help="Packet id from subagents/manifest.json")
    record_parser.add_argument("--status", default="completed", help="Return status")
    record_parser.add_argument("--summary", required=True, help="Short summary of the branch result")
    record_parser.add_argument("--artifact", action="append", dest="artifacts", default=[], help="Touched artifact path")
    record_parser.add_argument("--touched-files-repo", type=Path, help="Git repo to scan for an actual touched-files list")
    record_parser.add_argument("--verification", default="not provided", help="Verification note")
    record_parser.add_argument("--approval-evidence", default="n/a", help="Evidence for any extra approval required by dispatch")
    record_parser.add_argument("--risks", default="none", help="Residual risk note")
    record_parser.add_argument("--next-step", default="n/a", help="Suggested next step")

    merge_parser = subparsers.add_parser("merge", help="Generate a merge summary from current returns")
    merge_parser.add_argument("case_dir", type=Path, help="Case/worklog directory")
    merge_parser.add_argument("--force", action="store_true", help="Overwrite an existing merge summary")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "create":
        created = create_dispatch_bundle(args.case_dir, force=args.force)
        print("Created:")
        for path in created:
            print(f"- {path}")
        return 0

    if args.command == "record":
        path = record_subagent_return(
            args.case_dir,
            packet_id=args.packet_id,
            status=args.status,
            summary=args.summary,
            touched_artifacts=args.artifacts,
            touched_files_repo=args.touched_files_repo,
            verification=args.verification,
            approval_evidence=args.approval_evidence,
            risks=args.risks,
            next_step=args.next_step,
        )
        print(path)
        return 0

    if args.command == "merge":
        path = build_merge_summary(args.case_dir, force=args.force)
        print(path)
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
