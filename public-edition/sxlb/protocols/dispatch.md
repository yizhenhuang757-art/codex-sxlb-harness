# Dispatch Protocol

## Purpose
Define how `尚书省` turns an approved plan into local office execution or real subagent execution.

Dispatch treats offices and real subagents as stateless interfaces: bounded inputs, allowed actions, forbidden actions, return artifacts, and review checkpoints. It should reduce controller load without smuggling hidden context or unclear ownership into execution.

## Canonical Companions
- `templates/dispatch-order.md`: dispatch order shape.
- `protocols/subagent-orchestration.md`: work packets, returns, merge inputs, touched-file audit, dangerous-command evidence.
- `protocols/heavy-dispatch-layer.md`: optional high-cost multi-agent state, isolation, verify/fix, and shutdown rules.
- `sxlb-agent-dispatch-check`: lightweight admission gate before real subagent execution.

## Dispatch Rules
- Dispatch only after required review has passed.
- Name one owner for every branch and one integrator for shared writes.
- For A-class fast lane, use one named local-office owner and avoid real subagents, full branch packets, and `direct handling`.
- Parallel work is allowed only for non-overlapping ownership or explicit integration.
- Mark each branch as `local-office` or `real-subagent`.
- Use `n/a` for slice/readiness fields only when work is simple local execution.
- Before marking any branch `real-subagent`, apply `sxlb-agent-dispatch-check`.
- If admission is `fail` or `uncertain`, stay local unless the user explicitly overrides the cost judgment.
- If a delegable branch is kept local, state the reason.
- If ownership cannot be stated cleanly, stay serial.
- If a branch can be expressed as a deterministic, repeated, stable operation, prefer proposing a script/workflow graduation path over repeated real-subagent improvisation.
- Dispatch orders for nontrivial branches should include `执行预算`, `修复循环上限`, and `预算超限处理` so repeated agent correction loops return to coordination or review instead of drifting.
- Before risky execution, `尚书省` may require the pre-action hook:

```bash
python3 $SXLB_HOME/scripts/harness_hooks.py pre-action <case-dir> --branch-id <branch> --command "<command>" --write-path <path>
```

## Branch Contract
Each substantive branch should declare:
- slice type: `端到端薄切片 (vertical slice)`, support slice, research slice, verification slice, coordination slice, or `n/a`
- interaction mode: `AFK`, `HITL + decision point`, or `n/a`
- `blocked-by`
- `验收标准`
- write scope, shared read scope, forbidden scope
- return artifact and review return point
- per-branch stop/escalation conditions when budget, evidence, or scope boundaries fail

Use `ready-for-agent`, `ready-for-human`, `needs-info`, `blocked`, or `n/a` as the single readiness status.

## Real Subagent Minimum
When a branch is `real-subagent`, the minimum chain is:

1. `派令` names branch, owner, boundary, readiness, and integrator.
2. `尚书派发摘要` is issued and the dispatch event is recorded.
3. `subagent-work-packet-<branch>.md` is issued.
4. The worker executes only inside packet scope.
5. `subagent-return-<branch>.md` is written.
6. `merge-summary.md` is written when branch outputs must be reconciled.
7. `门下省` reviews dispatch, packets, returns, merge, and verification before `回奏`.

## Review Rules
- `门下省` reviews dispatch packages as evidence bundles, not final claims.
- Reject packages that hide a `HITL` choice inside `AFK`, mark blocked work as `ready-for-agent`, lack concrete `验收标准`, or miss required packets/returns.
- Return to review after material milestones, not only at the end.

## Dual-Track Rule
For `D` tasks, issue one merged dispatch order with `文线`, `武线`, merge point, and merge owner. Both tracks must return branch artifacts before final review.
