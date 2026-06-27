# Records Routing Protocol

## Purpose

Define how governed outputs are split so `restart` stays minimal while process evidence and stable conclusions remain durable.

## Routing Surfaces

- case records: worklog files, evidence, trial-and-error, intermediate plans
- volatile session records: short thread-local traces that are deleted at exit unless routed to a durable surface
- learning handoff: project-scoped or agent-scoped learning candidates that are not yet canonical rules
- canonical docs: stable rules, manuals, constitutions, and lasting workflow conclusions
- `restart`: current goal, stable current state, first files to read, and likely next adjustments
- `国史馆/总目.md`: cross-case index only, not a process log or memory store
- `起居郎`: human-facing vault documentation writeback, such as manuals, project pages, skill indexes, AI Reports, README files, and usage notes

## Scripted Support

Scripts can prepare artifact inventories, close checks, learning entries, and `礼部` candidates; see `protocols/harness.md` for the script index. They do not promote case-local facts into durable surfaces, and routing conflicts are resolved by this protocol plus `门下省`/`礼部` review.

## Routing Rules

- Default all detailed process material to case records.
- Use `volatile-record.md` only for non-durable traces that help the current `sxlb` run but do not yet deserve a case package, canonical update, progress note, restart pointer, or catalog entry.
- During `退朝清算`, delete any `volatile-record.md` that declares `记录类型：volatile`, `清理策略：delete-on-退朝`, and no durable `持久出口`.
- If a volatile record is routed to case records, canonical docs, progress/current-state notes, `restart`, `国史馆`, or `起居郎候补`, preserve it until the target durable record has captured the relevant content.
- Keep OMX-style runtime logs, branch traces, and execution observations inside the case package.
- Use `国史馆/总目.md` only to index cases and re-entry pointers; do not append worker logs, observations, or memory candidates to the catalog.
- Promote only stable and reusable conclusions to canonical docs.
- Keep `restart` short and overwrite stale state instead of appending mini-history.
- Before closure, run one lightweight case worklogs consolidation pass so the case folder is grouped under the right umbrella when it clearly belongs to an existing family (for example: `zotero`, `sxlb`, `internal-wiki`, `toefl`).
- Temporary case folders under `/tmp` or `/private/tmp` are allowed only for scratch experiments. If the case changes vault files, runs through more than one feedback loop, or reaches completion review, move or recreate the case under `$SXLB_CASE_ROOT/` before closure.
- This consolidation pass should prefer low-risk folder moves and should not rewrite case content semantics.
- Use `file-organizer` for this pass when available; if not available, apply the same rule manually and record that fallback in the closing note.
- After consolidation, refresh `国史馆/总目.md` so entry paths and statuses reflect the new folder layout.
- If a fact is only useful for reconstructing one case, it does not belong in `restart`.
- If a conclusion would still matter after this case is forgotten, consider canonical promotion.
- If a conclusion changes how the user should find, understand, use, or continue a project or skill, add a small `起居郎候补` item rather than forcing a broad vault scan.
- `起居郎` writeback should read only user-named targets, candidate items, known outputs, and narrow target-document fragments unless the user confirms a broader scope.
- Context packets, when used, are case-record extracts only. They must not become independent process logs, restart content, or canonical evidence unless their underlying core artifact is promoted through review.
- When `退朝` triggers `吏部项目复盘`, write that retrospective to `<worklog>/retrospective.md`.
- A `退朝`-triggered retrospective is a case record, not a canonical rule change by default.
- For `B`, `C`, and `D` cases, closure should leave `learning-candidates.jsonl` in the case package. It must contain either real candidates for `self-improving-agent` or one explicit `no-learning` record. Silence is not evidence; an empty file usually means the learning handoff was skipped.
- If a case produces raw runtime observations, write them to `execution-observations.jsonl` first; only filtered and review-worthy items should become `learning-candidates.jsonl`.
- Learning candidates must declare `promote_to`; promotion requires a later gate and may target `none`, `project`, `agent`, `canonical`, or `skill`.
- `退朝` must not bypass records routing. It first enters `退朝清算`, and mode exit is allowed only after the retrospective and closure checklist have been handled or explicitly marked as skipped/failed.
- `restart` remains the first re-entry document even when a project retrospective exists.
- If `<worklog>/retrospective.md` exists, `restart` should list it as the first case-record file to read, ahead of `task_plan.md`, `progress.md`, and `findings.md`.

## Required Check At Closure

Before a task leaves governed mode, confirm:

1. case records capture the process trail
2. canonical docs capture any new stable rule
3. `restart` only keeps the minimum re-entry pointers
4. `起居郎候补` is either empty, marked `none`, or routed to bounded human-facing writeback when the case changed future-facing usage
5. B/C/D case packages include `learning-candidates.jsonl` with either candidates or an explicit `no-learning` record, and every line has a promotion gate
6. if `planning-with-files` was used, including a user-explicit `sxlb` request treated as a `太子` trigger, the worklog includes a short project retrospective in `retrospective.md`
7. if that retrospective exists, `restart` points to it as the first worklog file to read on re-entry
8. if any required retrospective or restart update was skipped or failed, the closing `回奏` states the reason explicitly
9. the case has passed a lightweight case worklogs consolidation check (grouped or explicitly marked "no grouping needed")
10. `国史馆/总目.md` has been refreshed after any grouping move
11. unrouted `volatile-record.md` has been deleted, or any preserved volatile record names its durable route
