---
name: sxlb-agent-dispatch-check
description: Use when an active sxlb case may dispatch real subagents, parallel agents, multi-agent work, OMX-style execution, or several independent branches through 尚书省.
---

# SXLB Agent Dispatch Check

## Purpose

Use this as the lightweight gate before `尚书省` turns office labels into real subagent execution.

This skill does not make `sxlb` a multi-agent framework by default. It decides whether a specific dispatch is worth paying the coordination cost.

## Owner

- Framework maintenance: `吏部`
- Runtime user: `尚书省`
- Review consumer: `门下省`

## Default Rule

Default to local office execution.

Use real subagents only when the dispatch clearly earns its overhead. When doubtful, stay local and state the reason in the dispatch order.

## Admission Check

Real subagent dispatch should pass all four gates:

1. Parallel branches: at least two branches can make progress independently.
2. Ownership: each branch has a clear write boundary, read bundle, forbidden scope, and integrator.
3. Return contract: each branch has a concrete deliverable and verification method.
4. Cost benefit: expected time or cognitive-load savings are clearly larger than setup, supervision, merge, and review cost.

If any gate fails, use `local-office`, `serial`, or `parallel local-office` execution instead of real subagents.

If all gates pass and the dispatch is high-cost, conflict-prone, or has multiple real branches, use `$SXLB_HOME/protocols/heavy-dispatch-layer.md` as the cold-start execution layer.

## Dispatch Record

When real subagents are considered, `派令` should include:

```text
多 agent 准入：<pass|fail|n/a>
准入理由：<one-line judgment>
成本判断：<clearly worth it|not worth it|uncertain>
```

For each branch, include:

```text
owner:
write scope:
shared read:
forbidden scope:
deliverable:
verification:
integrator:
failure handling:
```

## OMX Reference Boundary

OMX-style patterns are reference material for the execution layer only:

- worker isolation
- ownership and work packets
- durable branch state
- structured returns
- verify and fix loops
- merge before review

Do not import OMX identity, role names, UI assumptions, or always-on team mode into `sxlb`.

## Review Rule

`门下省` should reject a real-subagent dispatch package when:

- admission is missing or marked `fail`
- branch ownership overlaps without a named integrator
- verification is vague
- returns are absent
- merge is skipped when branch outputs interact
