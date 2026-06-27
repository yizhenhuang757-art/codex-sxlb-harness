# Guoshiguan Execution Memory

## Purpose

Define how `sxlb` cases turn execution logs, worker returns, verification evidence, and learning candidates into durable case memory without bloating `国史馆/总目.md`.

## Core Rule

`国史馆/总目.md` is an index, not a process log.

Detailed evidence stays inside each case package. The catalog should point to the best re-entry file and status, while the case files preserve what happened.

## Memory Layers

Use four layers:

1. Catalog: `国史馆/总目.md` lists cases, status, restart, entry file, next step, and grouping notes.
2. Case evidence: `event-ledger.md`, `verification.md`, `artifact-registry.md`, branch returns, merge summaries, and optional execution observations.
3. Learning handoff: `learning-candidates.jsonl` contains filtered candidates or an explicit `no-learning` record; it is not canonical memory.
4. Canonical docs: stable rules promoted after review, such as protocols, skills, or restart pointers.

## Execution Observations

When a case has meaningful runtime evidence that is too granular for `event-ledger.md` but may be useful later, write `execution-observations.jsonl` in the case folder.

Each line should be one JSON object with:

- `time`
- `office`
- `source`
- `event`
- `evidence`
- `candidate`
- `promote_to`
- `confidence`

Use this file for raw observations such as tool failures, repeated integration friction, worker behavior patterns, or useful runtime traces.

Do not put private, irrelevant, or noisy transcript material there.
`promote_to` may only be `none` or `learning-candidates.jsonl`; raw observations cannot jump directly to canonical docs, agent rules, or skill changes.

## No-Learning Records

For `B`, `C`, and `D` cases, an empty `learning-candidates.jsonl` is not a sufficient closure signal.
If no reusable learning is justified, write one explicit JSONL record:

```json
{"type":"no-learning","scope":"case","source":"menxia-review","confidence":6,"summary":"No reusable project or agent learning justified for this case","promote_to":"none","stale_when":"new evidence appears"}
```

This keeps the self-improvement loop honest: either there is a candidate to review, or `门下省` has explicitly decided that the case should not teach a broader rule.

For vault/UI cases, repeated user-visible corrections are usually learning evidence, not mere noise. When the user reports the same class of failure more than once in one case, such as visual overlap, wrong runtime mode, missing generated links, or failed screenshot evidence, `门下省` should require either:

- a concrete `learning-candidates.jsonl` record naming the reusable workflow lesson, or
- an explicit `no-learning` record explaining why the issue is too local to promote.

## Promotion Path

Runtime observations must move through gates:

1. raw event in `event-ledger.md` or `execution-observations.jsonl`
2. filtered candidate in `learning-candidates.jsonl`
3. `self-improving-agent` or `吏部` review
4. canonical update only after explicit promotion

No observation should jump directly from a worker log into a skill rule.

## OMX-Style Logging Boundary

OMX-style systems are useful as reference patterns for:

- append-only event traces
- durable worker state
- explicit lifecycle transitions
- evidence-backed verification records
- memory candidates separated from canonical rules

Do not copy:

- always-on runtime logs into every case
- opaque memory updates
- agent self-claims without evidence
- dashboard-only status that cannot be reconstructed from files

## Guoshiguan Refresh Rule

After a case is created, moved, completed, or grouped under an umbrella, refresh `国史馆/总目.md`.

The refresh should update index metadata only. It should not rewrite case evidence or promote learning candidates.

## Review Rule

`门下省` should reject closure when:

- the catalog claims a case is complete but the case package lacks review or verification evidence
- the case claims completion while its declared archive path remains under `/tmp` or `/private/tmp`
- B/C/D `learning-candidates.jsonl` is empty instead of containing candidates or an explicit `no-learning` record
- `learning-candidates.jsonl` contains rules without a promotion gate
- `restart.md` contains detailed process logs instead of minimal re-entry state
- `国史馆/总目.md` is used as a dumping ground for worker logs
