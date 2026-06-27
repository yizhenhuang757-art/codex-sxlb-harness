# Intervention Protocol

## Purpose

Define how the user can intervene in `sxlb` mode without losing the governed workflow.

## Supported Commands

- `继续`
- `暂停`
- `恢复`
- `会审`
- `重审`
- `追因：...`
- `诊断：...`
- `录案`
- `召回 <某部>`
- `并行 <某部> <某部>`
- `恢复普通模式`
- `退朝`

## Intervention Rules

- `继续` advances from the current valid checkpoint using the active route already chosen.
- `暂停` freezes further dispatch until resumed.
- `恢复` restarts from the latest valid state.
- `会审` opens a temporary full-court deliberation hosted inside `门下审议`; `太子`, `中书省`, `门下省`, `尚书省`, and the relevant `六部` each state their position, debate for two rounds by default, and then `太子` must give a clear recommendation.
- `重审` routes the active item back to `门下省`.
- `追因：...` or `诊断：...` opens the dissatisfaction diagnostics path. It does not hide the status board or create a new permanent mode; when a case directory exists, first generate a diagnostic draft with `harness_hooks.py diagnose-dissatisfaction`, then ask `门下省` to compare the complaint with the original promise, evidence, failed guard, and smallest repair route.
- `录案` synchronizes the current case progress through `sxlb_case_status.py`: append a `录案` event, refresh `artifact-registry.md`, run `sxlb_guard.py`, and optionally refresh the 国史馆 catalog. It does not change dispatch ownership by itself.
- `召回 <某部>` stops that office's active assignment and returns control to `尚书省`.
- `并行 <某部> <某部>` requests parallel dispatch and can only be applied if ownership does not overlap.
- `恢复普通模式` closes the governed workflow with a final `回奏` and then continues outside `sxlb` while preserving current context.
- `退朝` initiates `退朝清算`; it does not immediately end `sxlb`.
- During `退朝清算`, `太子`, `吏部`, and `门下省` remain active for closure checks, records routing, and retrospective handling.
- During `退朝清算`, `吏部` also runs volatile-record cleanup: delete `volatile-record.md` only when it is explicitly marked volatile, has `清理策略：delete-on-退朝`, and has no durable route such as case records, canonical docs, progress/current-state notes, `restart`, `国史馆`, or `起居郎候补`.
- Actual exit from `sxlb` occurs only after the closure checklist is complete, the closing `回奏` is delivered, and any skipped closure item is explicitly reported.
- If `太子` used `planning-with-files` for the active case, or the user explicitly requested `planning-with-files` in `sxlb` and it was therefore treated as a `太子` trigger, and a project worklog exists, `退朝清算` must trigger a `吏部项目复盘` before exit confirmation.
- `吏部项目复盘` is project-local only: it reviews the current project's planning, routing, execution, and review quality, writes the result to the case worklog, and does not modify agent-wide skills or canonical rules by default.
- If the retrospective cannot be written, the closing `回奏` must explicitly state `吏部项目复盘：未执行` and give the reason, such as no active worklog, no `planning-with-files` use, user-requested immediate exit, or an access error.

## Control Points

- after `中书省` planning
- before `尚书省` dispatch
- after department reports
- before final `回奏`
- after an unsatisfactory result when the user asks for `追因` or `诊断`

## High-Cost Deliberation

- The primary trigger for `会审` is the explicit user command `会审`.
- `门下省` and `尚书省` may also request `会审` when they judge the active proposal too complex for ordinary review, but they do not thereby turn `会审` into a default review step.
- `会审` is for contested proposals, ambiguous tradeoffs, routing disputes, or cases where the user explicitly wants to hear multiple offices argue their positions.
- `会审` does not create a new top-level state and it is not a lasting thread mode; it is a temporary structured sub-protocol that runs while the case is visibly in `门下审议`.
- `会审` should usually produce:
  - one `会审录`
  - one updated `审议单` or revised `中书方案`
- `会审` defaults to two rebuttal rounds; a third round requires explicit `门下省` approval.
- `太子` must end `会审` with a recommended route, one backup route, and the cost of not adopting the recommendation.
- Every `会审` output must visibly include:
  - one `会审录`
  - one explicit closing sentence from `太子`
  - one explicit return sentence stating that the thread has exited `会审` and returned to ordinary `sxlb` flow
- `会审` may be invoked from planning review, pre-dispatch review, merge review, or final completion review when a single-line verdict would hide important disagreement.
