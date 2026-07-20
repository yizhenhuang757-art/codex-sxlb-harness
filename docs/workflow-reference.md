---
layout: default
title: Workflow reference
lang: en
alternate: /zh-CN/workflow-reference/
description: Follow the SXLB sequence from intake through review, execution, verification, and closure.
---

# Workflow reference

SXLB turns a substantive request into a visible, reviewable route. Not every case needs every artifact at the same weight, but a case should never lose clarity about who owns the next decision or what evidence supports it.

## The default route

```text
Intake → Proposal → Review → Dispatch → Execution → Completion review → Report
太子   → 中书省 → 门下省 → 尚书省 → 六部 → 门下复核     → 回奏
```

For a very small task, SXLB can use a lighter route: `太子 → 尚书省 → one office → 门下复核 → 回奏`. A substantive task involving planning, multiple tools, file changes, verification, or a meaningful risk normally uses the full route.

## 1. Intake — 太子

Intake files the request as a case, classifies its scale, identifies the desired outcome and constraints, and routes it to the appropriate path. It does not quietly perform planning or split work across offices on its own.

**Useful output:** a concise case statement, task class, scope, known risks, and the next responsible office.

## 2. Proposal — 中书省

The proposal stage turns the case into an actionable plan. It names the problem, intended result, non-goals, evidence, acceptance criteria, dependencies, and questions that need review. Uncertainty belongs in the proposal; it should not be hidden inside execution.

**Useful output:** a 中书方案 with alternatives and explicit review questions.

## 3. Review — 门下省

Review checks whether the proposed route is safe, proportionate, supported by evidence, and actually ready to execute. It can approve, return a proposal for revision, ask for more evidence, or escalate a meaningful disagreement to a bounded 会审 deliberation.

**Useful output:** an explicit verdict and the conditions for proceeding.

## 4. Dispatch — 尚书省

After approval, dispatch assigns a bounded piece of work to the responsible office or to a real subagent when that has been explicitly justified. The packet states the owner, write scope, deliverable, verification method, return format, and integration responsibility.

**Useful output:** a dispatch record, not merely an instruction hidden in conversation.

## 5. Execution — 六部

The six functional offices carry out bounded work. SXLB uses them as modern service boundaries: 工部 for implementation, 刑部 for testing and verification, 礼部 for user-facing documentation, 户部 for data and analysis, 兵部 for integration and automation, and 吏部 for skill governance and framework maintenance.

They do not replace proposal, review, or dispatch authority. A work return records what was done, what evidence exists, and which limitations remain.

## 6. Completion review — 门下复核

Completion is a separate checkpoint. The review examines the execution return, verification evidence, unresolved risks, and required records. A failed or incomplete result returns to dispatch or execution; it is not presented as complete by default.

**Useful output:** a review record that says whether closure is justified and, if not, what must happen next.

## 7. Report and closure — 回奏 / 退朝

The final report gives the result, evidence, remaining risk, and any next action. Closure routes durable records to their appropriate public or user-owned surfaces and keeps project-local learning separate from automatic system-wide changes.

## When multi-agent work is appropriate

Multi-agent execution is optional, not the default. Use it when branches are genuinely independent, specialized, and costly enough that parallel work has a clear benefit. Before dispatch, evaluate the candidate capability, define a narrow packet, and require a written return that can be reviewed and integrated.

For the conceptual basis of this sequence, see [the historical model]({{ '/three-departments-six-ministries/' | relative_url }}). For the careful modern mapping, see [SXLB mapping and design rationale]({{ '/sxlb-mapping/' | relative_url }}).
