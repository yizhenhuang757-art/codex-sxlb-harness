# Intake Protocol

## Purpose

Define how `太子` opens a case in `sxlb` mode and decides the legal governed path for the case.

## Inputs

- explicit `sxlb` activation
- user task
- current thread context
- urgency, risk, and ambiguity signals

## Outputs

- `立案单`
- initial task class: `A`, `B`, `C`, or `D`
- next office in the chain
- case record anchor
- minimum legal chain

## Intake Rules

- Only enter the protocol when the user explicitly says `sxlb`.
- Record the user's goal, constraints, and desired outcome in a short `立案单`.
- Create or identify the case record anchor before deeper work begins.
- Once `sxlb` is active, do not thin the framework by skipping legal checkpoints.
- Small tasks may shrink to single-office ownership, but still require `太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏`.
- For `A` classification, run or satisfy the route-admission hook:

```bash
python3 $SXLB_HOME/scripts/harness_hooks.py route-admission <case-dir>
```

- `A` fast lane must use `太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏`, a named single office, and a lightweight `volatile-record.md` unless it is immediately routed to a durable case record.
- `A` fast lane must not use `direct handling`, real subagents, `中书省` planning, or full B/C/D artifacts by default.
- Escalate to a higher task class when uncertainty, multi-step execution, or cross-office coordination is real.
- Low-risk vault maintenance may start as `A` with a lightweight case package when the likely change is limited to one note, one template, one CSS snippet, or one local Markdown vault setting.
- Upgrade vault maintenance from `A` to at least `B` when it becomes batch editing, touches protected folders, changes reusable templates, affects Markdown vault UI/runtime behavior, or receives more than one user-visible correction loop.
- If the user explicitly asks to use `planning-with-files` during an active `sxlb` case, treat that as a `太子`-level request for case-record support unless the user clearly says otherwise.
- `restart` may be named as a future re-entry target, but it is never the primary case record.
- On later re-entry, read `restart` first; if it points to a project `retrospective.md`, treat that as the first case-record file to open.

## Task Classes

- `A`: single-office governed task
- `B`: province-reviewed and dispatched task
- `C`: full court task
- `D`: research plus engineering dual-track task
