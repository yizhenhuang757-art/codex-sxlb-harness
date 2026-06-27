# Review Protocol

## Purpose

Define how `门下省` reviews plans and major execution claims before work proceeds.

In the `sxlb` harness, review is a completion and guardrail surface. It should identify which guard passed or failed rather than relying on intention or general confidence.

## Inputs

- `中书方案`
- execution evidence
- verification output
- prior review findings

## Outputs

- `审议单`
- optional `会审录`
- verdict:
  - `通过`
  - `封驳`
  - `补证后再审`

## Mandatory Review Checkpoints

- after `中书省` completes a plan for any `B`, `C`, or `D` task
- before `尚书省` dispatches any subagent or office split
- after `D` track outputs are merged back into one decision package
- before final completion claims on `C` and `D` tasks
- before any visible claim that a file-editing or verification-bearing task is complete

## Scripted Support

Scripts can supply completion prechecks, guard results, and review packages; see `protocols/harness.md` for the script index. `门下省` still owns the verdict, exception handling, and whether a failure is missing evidence, weak verification, bad routing, or unresolved risk.

## Review Rules

- Review evidence, not intention.
- Check scope fit, verification quality, routing quality, and skill fit.
- Apply a lightweight four-gate review before approval:
  - 假设检查：material assumptions are stated or explicitly marked unknown.
  - 复杂度检查：the plan or completion claim does not add avoidable offices, artifacts, abstractions, or dependencies.
  - 边界检查：the work stayed inside the declared scope and write boundary.
  - 验证标准检查：success criteria and verification evidence are concrete enough to support the next checkpoint.
- For PRD-shaped plans, check that `领域语言`, ADR relevance, decision-tree closure, and testing decisions are present or explicitly `n/a`.
- For `采风` packages, check that the `外部证据包` answers the question tree, labels source type and 来源可靠性, and marks unknown or weak evidence before it influences the plan.
- Check `预算与停止条件` on `B`, `C`, and `D` plans: missing budgets, unbounded repair loops, or unclear escalation points require `补证后再审`.
- Apply `冲突取舍检查` when source files, AGENTS rules, skills, tests, or prior decisions disagree: the review must name the chosen source of truth rather than averaging conflicting instructions.
- For dispatch packages, check that real-subagent branches do not hide HITL decisions inside AFK work, blocked branches are not labeled `ready-for-agent`, and acceptance criteria are concrete.
- Check records routing quality: process detail must stay in case records, while stable rules must be promoted deliberately.
- For dissatisfaction diagnostics, compare the user's stated dissatisfaction with the original success criteria, locate the failure in intake / planning / execution / verification / reporting / preference capture, name the evidence chain, and propose the smallest repair route.
- When the issue is a harness gap rather than a one-off execution error, record a learning candidate, guardrail candidate, or workflow-graduation candidate instead of only fixing the immediate output.
- Match verification weight to risk:
  - `A` and low-risk maintenance cases may use inline verification in `menxia-review.md` and `memorial-report.md`.
  - Inline verification must still name `验证对象`, `验证动作`, `结果`, and `未覆盖风险`.
  - `B`, `C`, and `D` cases require `verification.md`.
  - `verification.md` should name a concrete `行为断言/不变量` and `测试有效性`, so green tests show behavior instead of ceremony.
  - UI/runtime cases must distinguish code-level evidence from live user-path or screenshot evidence; do not treat failed or wrong-window screenshots as passing evidence.
  - When a task starts as `A` but accumulates repeated user-visible regressions, failed runtime checks, or more than one corrective loop, upgrade the verification weight to `lightweight` or `full`.
- Apply `失败显性化检查` before completion: skipped, partial, failed, or unverified work must appear in verification evidence or the memorial instead of being collapsed into a passing claim.
- For completion review, prefer a semi-automatic `门下复核` pass that:
  - runs the case validator
  - runs the harness completion hook or uses `sxlb_case_status.py close`, which includes harness advisories
  - checks fresh return / merge / verification evidence
  - rejects completion when the declared `案卷路径` is still under `/tmp` or `/private/tmp`
  - checks that B/C/D `learning-candidates.jsonl` is non-empty or explicitly records `no-learning`
  - writes one explicit `门下复核单`
  - appends the review event into the ledger
- Route technical debugging or test execution back to `刑部`; do not absorb it.
- Require rework when material ambiguity or unsupported claims remain.
- `补证后再审` keeps the task in the review lane while missing evidence is gathered.
- A compliant review must be visible in the transcript as `门下审议`; silent internal review is not enough.
- When disagreement across offices is materially useful to expose, `门下省` may host a `会审` round before issuing the final review verdict.
