# Case Package Protocol

## Purpose

Define the minimum artifact package that makes an `sxlb` case inspectable by both humans and the `sxlb_guard`.

The case package is the durable state for the `sxlb` coding-agent harness. The visible `朝堂状态` board projects high-level state, but the package carries the auditable facts, evidence, and completion claims.

`能力召回` is a required case-package field for `case.md`, `zhongshu-plan.md`, and `dispatch-order.md`. It records semantic bridge keywords, 0-2 candidate skill clans, 0-3 candidate skill families, and any retained phase-scoped skill bundles from `scripts/recall_capabilities.py`, or `none`. When the user wording is implicit, the field should preserve the semantic bridge keywords used to make deterministic registry matching possible. This field is recall evidence only: clan is context, family is the execution boundary, and concrete skill candidates remain candidate-only until 六部 ownership, `skills/allowlist.md`, `skills/mapping.md`, and each concrete skill's own trigger/prerequisite rules all match.

## Case Package Weights

Every governed case needs a durable case record, but not every case needs the full heavy evidence bundle.

`volatile-record.md` is the exception for pre-case or low-value session traces. It is not a case package and must not be treated as durable evidence. Use it only when `sxlb` needs a short thread-local trace before deciding whether a real case package is justified.

For `A` fast lane, `volatile-record.md` is the normal lightweight record unless the task is immediately routed to a durable case record. It should be deleted at `退朝清算` when it has no durable route.

During `退朝清算`, an unrouted volatile record must be deleted automatically after closure checks pass. Preserve it only when it has been routed to at least one durable surface: case records, canonical docs, progress/current-state notes, `restart`, `国史馆`, or `起居郎候补`.

Use a `lightweight` package for `A` cases and low-risk vault maintenance where the verification conclusion can be stated inline in `menxia-review.md` and `memorial-report.md`.
Use a `full` package for `B`, `C`, and `D` cases, file-editing work with nontrivial risk, protocol changes, automation changes, real dispatch, or any case that needs separate verification evidence.

Temporary directories such as `/tmp` and `/private/tmp` may be used for experiments only. A case may not close while `case.md` still declares a temporary `案卷路径`.

For vault/UI maintenance, choose the package weight by observed behavior rather than by the first request:

- Start `lightweight` when the task is a bounded, reversible adjustment.
- Migrate to a durable worklog under `$SXLB_CASE_ROOT/` as soon as the task changes vault files and needs later replay.
- Upgrade to `full` if the case has repeated user-visible regressions, screenshot/runtime evidence, batch edits, reusable template changes, or a rule that should affect future vault work.

## Verification Weight Policy

Verification is mandatory as a conclusion, not always mandatory as a standalone `verification.md`.

- `inline`: for one-step `A` tasks and low-risk vault/UI maintenance. Record the check directly in `menxia-review.md` and `memorial-report.md`.
- `lightweight`: for small file edits where the user may later need to know what was checked. Inline is still acceptable if it names the changed object, the check, the result, and the remaining risk.
- `full`: for `B`, `C`, and `D` cases, protocol changes, automation, batch edits, real dispatch, or any work where evidence must be reviewed separately. Requires `verification.md`.
- `runtime`: for UI, browser, Markdown vault, app, or other live-path work. Record code-level checks separately from live-path, screenshot, or user-confirmed evidence. If live evidence failed or was unavailable, mark it as unverified rather than passing.

Minimum inline verification shape:

- `验证对象`: file, note, UI path, or behavior checked
- `验证动作`: command, manual check, screenshot, user-path attempt, or reason no runtime check was possible
- `结果`: pass, partial, fail, or user-confirmed
- `未覆盖风险`: none, or the concrete thing not yet verified

## Required Artifacts

Every governed case package should contain the base record:

- `case.md`
- `dispatch-order.md`
- `menxia-review.md`
- `memorial-report.md`
- `event-ledger.md`

Additional requirements:

- `zhongshu-plan.md` is required for `B`, `C`, and `D` cases
- `artifact-registry.md`, `verification.md`, and `records-routing.md` are required for `B`, `C`, and `D` completion packages
- `learning-candidates.jsonl` is required for `B`, `C`, and `D` completion packages. It must contain at least one candidate or one explicit `no-learning` JSON object explaining why no reusable learning is justified. Every line must be a JSON object with `type`, `scope`, `source`, `confidence`, `summary`, `promote_to`, and `stale_when`.

Conditional requirement:

- `subagent-work-packet-<branch>.md` is required for every branch marked `real-subagent`
- `subagent-return-<branch>.md` is required for every branch marked `real-subagent`
- `heavy-dispatch-state.md` or `subagents/manifest.json` is required when the Heavy Dispatch Layer is activated
- `dissatisfaction-diagnostic.md` is required when a dissatisfaction diagnosis is durable case evidence rather than a small inline answer
- `merge-summary.md` is required whenever:
  - two or more execution branches must be reconciled
  - a `D` case uses `文线 / 武线`
  - branch returns, verification, or cross-branch conflicts must be presented to `门下省` as one package

Optional but recommended:

- `status-board.md`
- `dissatisfaction-diagnostic.md` for on-demand `追因` / `诊断` responses that may guide repair or future learning
- `retrospective.md`
- `execution-observations.jsonl` when runtime observations are too detailed for `event-ledger.md` but may later inform `learning-candidates.jsonl`

Volatile, delete-on-exit:

- `volatile-record.md` for a non-durable session trace. It must declare `记录类型：volatile`, `持久出口`, and `清理策略：delete-on-退朝`. `sxlb_case_status.py close` deletes it when closure passes and no durable route is declared.

## Scripted Support

Scripts scaffold, profile, inventory, validate, and close case packages; see `protocols/harness.md` for the script index. They do not decide the substantive route, and observed risk or `门下省` review can require a heavier package than a script recommends.

On-demand context compression:

- `intake-context.md`, `dispatch-packet.md`, and `review-grill.md` are not default case-package files.
- Use them only for `C`/`D` cases, real subagent dispatch, cross-case handoff, or long-thread compression where a smaller read surface is worth the extra artifact.
- Do not duplicate judgments already recorded in `case.md`, `dispatch-order.md`, or `menxia-review.md`; prefer adding the needed field to the core artifact.
- Context packets are working extracts for reducing token load, not new canonical records or a second案卷 layer.

## Enforcement Intent

- The case package is the minimum auditable surface for `sxlb`.
- If a material step is not reflected in the package, the guard should treat it as missing workflow evidence.
- A filled package is more important than a long package; concise but explicit artifacts are preferred.

## Guard Expectations

The validator should be able to inspect the package for:

- missing required files
- forbidden legacy routes such as `direct handling`
- placeholders left in completion-critical artifacts
- whether real subagent dispatch happened or was deliberately not used
- whether real-subagent dispatch has readiness, slice type, HITL/AFK, blocked-by, and acceptance-criteria evidence
- whether the event ledger shows the minimum legal lifecycle
- whether B/C/D completion packages include a project learning handoff file
- whether B/C/D learning handoff is non-empty or explicitly marked `no-learning`
- whether a completed case still points to a temporary archive path
- whether learning candidates have an explicit promotion gate instead of silently becoming canonical rules
- whether real-subagent claims are backed by packets and returns
- whether merge-dependent cases expose a merge summary for review
- whether detailed execution observations stay in the case package instead of polluting `国史馆/总目.md`
- whether on-demand dissatisfaction diagnostics identify failure location, evidence chain, attribution, and the smallest repair route when such diagnostics were requested
- whether `sxlb_case_status.py close` or `harness_hooks.py completion` surfaced harness advisories such as workflow-graduation candidates
- whether completed case packages expose `能力召回` in intake, planning, and dispatch artifacts instead of relying on hidden model memory
