# Real Subagent Orchestration Protocol

## Purpose

Define the document contract for real subagent execution inside `sxlb`, so delegation reduces controller overload without causing context drift, ownership blur, or silent overreach.

## Core Principle

`尚书省` may not call a branch `real-subagent` unless that branch is governed by a written work packet and a written return artifact.

Real orchestration in `sxlb` therefore means:

- branch-scoped context instead of transcript dumping
- named ownership instead of implied freedom
- explicit return artifacts instead of controller paraphrase
- merge before review instead of skipping straight to `回奏`
- stateless branch interfaces: each worker receives the smallest sufficient packet and returns evidence in the required shape

## Required Documents

For each real-subagent branch:

- one `subagent-work-packet-<branch>.md`
- one `subagent-return-<branch>.md`

For high-cost or multi-branch real-subagent cases where `尚书省` activates the Heavy Dispatch Layer:

- one `heavy-dispatch-state.md`, or an equivalent `subagents/manifest.json` produced by `subagent_dispatch.py`

For any case with more than one execution branch, or any case where branch outputs must be reconciled before review:

- one `merge-summary.md`

## Work Packet Rules

A valid work packet should define:

- case identifier
- branch identifier
- owning office
- task objective
- slice type, such as `端到端薄切片 (vertical slice)`, support slice, research slice, verification slice, or coordination slice
- interaction mode, either `AFK` or `HITL` with the decision point named
- `blocked-by` dependency status
- observable acceptance criteria
- write scope
- shared read bundle
- forbidden scope
- actual touched-files audit requirement
- dangerous command policy
- actions requiring extra approval
- allowed skills or required methods
- expected return artifact
- escalation triggers
- completion standard

The packet should be small enough for a worker to stay on task and strong enough for `门下省` to later judge whether the worker crossed the line.

For simple local office work these slice/readiness fields may be `n/a` in the dispatch order, but once a branch is marked `real-subagent` they are part of the auditable contract.

## Return Rules

A valid branch return should report:

- packet reference
- branch result
- files or artifacts touched
- independent touched-files list when required
- evidence produced
- extra approval evidence when the dispatch order requires approval for dangerous actions
- unresolved risks
- explicit boundary statement
- requested next step

If the worker had to stop because of ambiguity, blocked access, or conflict with another branch, the return should say so rather than improvising ownership.

## Merge Rules

The merge owner is responsible for:

- collecting all branch returns
- identifying overlap or contradiction
- integrating non-overlapping outputs
- naming unresolved conflicts
- producing one merge summary for `门下省`

The merge owner may integrate shared conclusions, but may not rewrite branch evidence into an untraceable single voice.

## Review Input Rules

`门下省` should review the following bundle together:

- `dispatch-order.md`
- `heavy-dispatch-state.md` or `subagents/manifest.json` when the Heavy Dispatch Layer was activated
- all relevant `subagent-work-packet-*.md`
- all relevant `subagent-return-*.md`
- `merge-summary.md` when required
- any fresh verification evidence referenced by the returns

If any of these are absent while the case claims real subagent execution, `门下省` should treat the package as incomplete.

After every real-subagent return, treat the return as a lifecycle hook point: check packet scope, touched-files evidence, dangerous-command evidence, unresolved risks, and merge requirements before allowing completion review.

For deterministic checks, run:

```bash
python3 $SXLB_HOME/scripts/harness_hooks.py subagent-return <case-dir> --branch-id <branch>
```

## Risk Reduction Intent

This protocol exists to reduce two recurrent subagent weaknesses:

- context fracture: workers receive only their owned bundle and return in a standardized shape
- overreach: workers are judged against explicit boundaries rather than broad thread memory


## Scope Audit

Real-subagent returns should expose `触达文件/产物`. During completion review, `sxlb_guard.py` compares those touched files with the branch `可写范围` and `禁写范围` from `dispatch-order.md`.

The first implementation is path/prefix based. It is intended to catch clear overreach, not to interpret vague natural-language ownership claims.

For higher-risk branches, `dispatch-order.md` may set `真实触达审计：required`. In that case the branch return must include `真实触达清单`, pointing to an independent touched-files evidence file such as `git diff --name-only` output or an equivalent tool-generated list. When this file is present, `sxlb_guard.py` treats it as the stronger evidence source and audits those paths instead of trusting the return's self-reported `触达文件/产物`.

This is still a completion-time evidence check, not a live filesystem monitor. It does not infer untracked changes unless the independent touched-files list includes them.

`sxlb` provides `scripts/touched_files.py` to generate that independent list from a git working tree. The helper records unstaged, staged, and untracked paths:

```bash
python3 $SXLB_HOME/scripts/touched_files.py --repo <repo> --output <case-dir>/subagents/returns/touched-files-<branch>.txt
```

The generated file can be referenced directly from `真实触达清单`.

`subagent_dispatch.py create` carries the relevant dispatch scope fields into each work packet. If the branch says `真实触达审计：required`, the generated packet includes the `touched_files.py` command the worker should run before returning. `subagent_dispatch.py record --touched-files-repo <repo>` can then generate the list and write its relative path into the return artifact automatically.

`subagent_dispatch.py create` also carries `切片类型`, `交互模式`, `blocked-by`, and `验收标准` from `dispatch-order.md` into the packet and manifest. `sxlb_guard.py` treats missing or contradictory values in these fields as completion blockers for real-subagent dispatch.

## Dangerous Command Policy

`危险命令策略` is not just prose. During completion review, `sxlb_guard.py` scans real-subagent return `关键命令或动作` for destructive command patterns such as `rm -rf`, `git reset --hard`, `git clean -fd`, `git checkout --`, recursive permission/ownership changes, `sudo`, and process-kill commands.

- If the branch policy says `no destructive commands`, the return fails review when such a command is reported.
- If the branch policy or `需额外批准动作` requires approval, the return must include `额外批准证据`.
- `subagent_dispatch.py record --approval-evidence <evidence>` writes that evidence into the return artifact and manifest.
