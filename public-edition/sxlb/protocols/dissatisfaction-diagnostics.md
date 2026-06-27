# Dissatisfaction Diagnostics Protocol

## Purpose

Provide an on-demand path for diagnosing unsatisfactory `sxlb` results without making the user inspect the whole process by default.

This protocol is a diagnostic surface, not a default panel replacement and not an apology template.

## Triggers

Use this protocol when the user says, or clearly means:

- `追因：...`
- `诊断：...`
- `为什么这次不满意`
- `哪里失败了`
- `复盘这次为什么没做好`
- equivalent dissatisfaction or failure-analysis language

If the user only wants the work fixed immediately, do the smallest necessary diagnosis inside `门下复核` and proceed to the repair route.

## Required Inputs

- the user's dissatisfaction point, quoted or restated briefly
- original request and constraints
- stated or inferred success criteria
- relevant `朝堂状态` transitions, if available
- case artifacts: plan, dispatch order, review, verification, memorial, ledger, and branch returns as applicable
- tool or test evidence where the failure concerns implementation behavior

If required inputs are missing, mark them as missing evidence instead of inventing intent.

## Diagnostic Output

Use `templates/dissatisfaction-diagnostic.md` when a durable artifact is warranted. For small cases, the same headings may be answered inline.

When a case directory exists, prefer generating the first diagnostic draft with:

```bash
python3 $SXLB_HOME/scripts/harness_hooks.py diagnose-dissatisfaction <case-dir> --complaint "追因：..." --output dissatisfaction-diagnostic.md
```

The generated file is a draft evidence surface. `门下省` still owns the final judgment, attribution, and repair route.

The diagnostic must include:

- 不满意点复述
- 原始承诺/成功标准对照
- 失败位置判断: intake / planning / execution / verification / reporting / preference capture
- 证据链
- 归责: agent failure / harness gap / unclear requirement / insufficient verification / task uncertainty
- 最小修复路线

## Failure Location Guide

- intake: the task goal, boundary, risk, or success criteria were not captured.
- planning: the plan selected the wrong slice, ignored constraints, or failed to surface tradeoffs.
- execution: the work did not implement the approved plan or crossed scope.
- verification: checks were missing, too weak, stale, or treated partial evidence as passing.
- reporting: the `回奏` hid uncertainty, overstated completion, or omitted important evidence.
- preference capture: the work missed a stable user preference that was stated or should have been carried from the case.

Multiple locations may be named, but the diagnostic should identify the primary failure if the evidence supports one.

## Repair Route

After diagnosis:

1. State the smallest repair that could satisfy the original success criteria.
2. Name the guard or hook that would prevent recurrence.
3. Route the repair through the current legal `sxlb` checkpoint.
4. If the issue is stable and repeated, add a learning candidate or workflow-graduation candidate instead of silently relying on future memory.

## Limits

- Do not use diagnosis as a way to relitigate every step when the user asked for a direct fix.
- Do not call the panel the source of truth; use artifacts and evidence.
- Do not convert dissatisfaction into a new permanent mode.
- Do not promote a one-off preference into canonical behavior without review.
