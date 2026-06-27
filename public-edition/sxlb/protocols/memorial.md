# Memorial Protocol

## Purpose

Define how work returns to the user as a structured `回奏`.

## Inputs

- completed office outputs
- review outcomes
- verification evidence
- open risks or follow-up items
- event ledger
- case record summary

## Outputs

- `回奏`
- records split summary
- learning handoff summary
- retrospective summary

## Memorial Rules

- Every `sxlb` task closes with a `回奏`, including downgrade and cancellation paths.
- State the final chain path used.
- Separate confirmed outcomes from remaining risks.
- Include the current status if work is paused or partially complete.
- Do not claim completion without fresh verification evidence. For `A` and low-risk maintenance cases this may be an inline verification conclusion; for `B/C/D` cases it must cite `verification.md`.
- Inline verification in a memorial should be short, but it must still say what object/path was checked, what action was used, what the result was, and what remains unverified.
- If the user exits `sxlb` or downgrades to ordinary mode, produce a closing `回奏` that summarizes the current governed state before leaving the framework.
- For `退朝`, do not treat the command itself as the exit point. First enter `退朝清算`, complete closure checks, and only then leave `sxlb` after the closing `回奏`.
- If the task is cancelled or abandoned, produce a cancellation memorial that records why the governed workflow stopped.
- Route detailed process history to case records, not to `restart`.
- Route stable, reusable conclusions to canonical docs, not to case-only logs.
- Update `restart` only with the minimum re-entry pointers needed for the next session.
- `restart` remains the re-entry surface, but when `<worklog>/retrospective.md` exists it should name that file as the first worklog file to read before `task_plan.md`, `progress.md`, or `findings.md`.
- Every governed run should end with a short retrospective summary in the memorial.
- If `太子` used `planning-with-files`, or the user explicitly requested `planning-with-files` in `sxlb` and it was therefore treated as a `太子` trigger, and the active case has a project worklog, `退朝` must also trigger a `吏部项目复盘` written to `<worklog>/retrospective.md`.
- `吏部项目复盘` is scoped to the project worklog. It may recommend future upgrades, but it does not change agent-wide skills or canonical docs unless the user later asks for promotion.
- The memorial must cite whether a project retrospective was written. If it was skipped or failed, cite the reason instead of silently omitting it.
- The memorial may cite that a project retrospective was written, but should not inline the full worklog retrospective.
- For B/C/D cases, cite `learning-candidates.jsonl` in the memorial. It must contain either reusable candidates or an explicit `no-learning` record; candidates require `self-improving-agent` promotion before becoming project or agent rules.

## Minimum Memorial Shape

- task summary
- chain used
- key decisions
- verification evidence
- open risks
- next recommended move
- records routing:
  - case records
  - canonical targets
  - restart target
  - learning handoff target
- retrospective:
  - smooth point
  - stuck point
  - rework point
  - next project improvement candidate
- exit closure:
  - `退朝清算` status if applicable
  - whether `<worklog>/retrospective.md` was written, skipped, or failed
  - whether `restart` now points to the retrospective when required
- if applicable, how `文线` and `武线` were merged
