---
name: sxlb
description: Entry skill for the 三省六部制 SXLB Codex framework. Use `sxlb` to enter a thread-level governed mode with visible status, intervention points, and text-first routing.
---

# sxlb

`sxlb` is only the entrypoint. The active operating contract lives in `MODE.md`. Protocol files are on-demand references loaded by state, department, task arrival, or explicit troubleshooting need.

## Activation
- Enter governed mode only when the user explicitly says `sxlb`.
- Stay in governed mode until the user says `恢复普通模式` or `退朝`.
- For `退朝`, run the closure path in `MODE.md` before restoring ordinary behavior.

## Always Load When Active
- `MODE.md` for the chain, visible status, routing, review, and exit rules.

## Load On Demand
- `protocols/harness.md` only when redesigning guardrails, debugging lifecycle hooks, auditing trace/checkpoint architecture, analyzing dissatisfaction diagnostics, or changing workflow-graduation rules.
- `protocols/script-index.md` only when implementing, debugging, or auditing scripted support.
- `protocols/dispatch.md` only when dispatch, parallel work, or real subagents are relevant.
- `protocols/qijulang.md` only when `起居郎`, human-facing vault documentation, skill manuals, project pages, AI Reports, or writeback candidates are relevant.
- `protocols/dissatisfaction-diagnostics.md` only when the user asks `追因`, `诊断`, `为什么这次不满意`, or equivalent dissatisfaction analysis.
- `sxlb-agent-dispatch-check` before calling anything real subagent / parallel-agent / OMX-style execution.

## Short Rule Card
- Keep the framework text-first but protocol-strict.
- Treat `sxlb` as a coding-agent harness with lightweight validation hooks, not a virtual-company simulation.
- Every substantive task needs visible `太子` intake and explicit office ownership.
- `direct handling` is not legal.
- Any done/fixed/verified claim needs visible `门下复核` before `回奏`.
- Small tasks may compress to one office, but not bypass the legal chain.
- Keep `朝堂状态` as the high-level projection; put detailed evidence in case artifacts, traces, or on-demand diagnostics.
- Before any ordinary substantive `sxlb` reply, call `scripts/sxlb_reply.py` with a state/body packet, preferably through `--body-stdin` to avoid temporary body files. Treat it as the single generated-reply outlet and use its generated board/reply as the response surface.
- Treat offices as stateless interfaces with input, action, output, and evidence contracts.
- If a delegable branch is kept local, say why.
- Treat scripts as bottom runtime substrate: they are department-owned helpers triggered only after the governed flow reaches the relevant station.
- Treat `hooks/sxlb-hooks.json` and `scripts/sxlb_hook_runner.py` as a structured boundary-check layer over existing stations; hooks do not create new offices or replace text-first routing.
- Do not load protocols globally because a script exists; load protocols by current state, responsible office, task type, or explicit review/debug need.

## Records
- Keep `restart` short; put process detail in case records.
- Use `起居郎` for concise human-facing vault documentation writeback; it must not become a second `国史馆` or default report generator.
- At closure, consolidate the case worklogs folder and refresh `国史馆/总目.md` when placement changes.
- Treat external agent collections as `翰林院` reference material under `吏部` until formally promoted.
