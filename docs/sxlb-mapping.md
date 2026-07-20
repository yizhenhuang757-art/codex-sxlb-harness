---
layout: default
title: SXLB mapping and design rationale
lang: en
alternate: /zh-CN/sxlb-mapping/
description: Learn how SXLB translates the Three Departments and Six Ministries into a modern, text-first governance harness.
---

# SXLB mapping and design rationale

SXLB is inspired by the governance logic of the Three Departments and Six Ministries; it is not a historical simulation. The names give a memorable vocabulary for differentiated responsibility, but the operating goal is contemporary: make knowledge work easier to inspect, challenge, coordinate, verify, and resume.

## The central translation

| Historical model | SXLB role or mechanism | What is carried forward | What is not claimed |
| --- | --- | --- | --- |
| 中书省 | Planning and synthesis | A proposal is explicit before action | A literal reproduction of imperial document drafting |
| 门下省 | Independent review, objections, and completion review | A plan and a completion claim can be challenged | Historical veto powers or court rank |
| 尚书省 | Dispatch, coordination, and reassignment | Approved work gets a named owner and bounded packet | A real bureaucracy controlling people |
| 六部 | Functional service boundaries | Specialized responsibilities are separated and visible | Fixed historical portfolios or a claim of equivalence |
| 史官式留痕 | Case records, event ledgers, status boards, and bounded documentation routing | Decisions can be revisited with evidence | An imperial archive or automatic publication of personal data |

The translation begins with a sequence, not a title: **proposal → independent review → accountable execution → verification → recordkeeping**. When a task needs only a small route, SXLB reduces the weight of its artifacts; it does not erase the distinction between deciding, doing, and accepting.

## The role of 太子

太子 is a modern orchestration role rather than a direct element of the three-department model. It receives a request, opens and routes the case, keeps the visible state coherent, and consolidates closure. It must not become a second planning office or directly dispatch a departmental split that belongs to 尚书省.

This role solves a practical problem in agent work: the conversation needs a legible entrance and exit, not only specialist stages in the middle.

## The three departments in SXLB

### 中书省: plan before irreversible action

中书省 converts a filed case into a proposal with outcome, evidence, constraints, non-goals, alternatives, acceptance criteria, budget, and stopping conditions. The important design choice is that uncertainty becomes reviewable text. A plan is allowed to be revised; hidden assumptions are not treated as execution authority.

### 门下省: make objection and acceptance distinct

门下省 reviews plans before material execution and reviews completion claims after work returns. It can approve, require more evidence, return a proposal for revision, or convene a bounded 会审 when ordinary review would conceal an important disagreement. This makes review a real decision surface rather than an after-the-fact compliment.

### 尚书省: dispatch is a contract, not a label

尚书省 turns an approved plan into bounded work. A dispatch identifies the owner, write scope, deliverable, verification method, return format, and integrator. It may recall or reassign work when evidence changes. Naming an office without a packet does not count as dispatch.

## The six ministries as modern service boundaries

| SXLB office | Modern responsibility | Historical inspiration used carefully |
| --- | --- | --- |
| 吏部 | Skill governance, capability evaluation, framework maintenance | Personnel appointment and fitness for responsibility |
| 户部 | Data work and analysis | Resource, account, and evidence stewardship |
| 礼部 | Documentation, user-facing clarity, and 起居郎 writeback | Formal communication, learning, and institutional presentation |
| 兵部 | Integration and automation | Coordinated movement and operational support |
| 刑部 | Testing, debugging, verification, and technical findings | Standards, procedure, accountability, and reviewable findings |
| 工部 | Implementation and refactoring | Technical construction and material execution |

These are purpose-built service boundaries for an agent harness. They are not translations of historical ministerial authority. A task may use one office, several offices, or no split at all; the test is whether the distinction reduces ambiguity and improves review.

## Why the public edition is text-first

SXLB treats readable records as the common interface between people, tools, and agents. A status board, proposal, review verdict, dispatch packet, and verification record let a future reader reconstruct the decision without relying on hidden model state.

Text-first does not mean manual-only. Scripts can prepare inventories, render status, validate boundaries, and surface checks. They do not silently create authority, convert an unreviewed external capability into an approved one, or replace a review verdict.

## The optional multi-agent conversion path

The original inspiration can support multi-agent work, but SXLB does not make delegation its default. The controlled route is:

```text
翰林院 reference pool
  → 吏部 evaluation and appointment review
  → 尚书省 dispatch packet
  → bounded agent or skill execution
  → merge summary and verification
  → 门下省 review
```

An external agent, skill, prompt, or pattern begins as reference material. It is evaluated for fit, safety, license, tools, and failure modes before it becomes a candidate for active work. Real dispatch needs a positive coordination judgment, independent branches, a clear owner, and an integrable written return. Otherwise SXLB keeps the work local or serial.

## Boundaries and limitations

- The user remains the authority for goals, scope, approvals, and external commitments.
- A role name never grants tool permission, access to private data, or permission to change external systems.
- The framework favors proportionate governance: more structure for consequential work, less for a small bounded task.
- Historical language is a design vocabulary and source of questions, not evidence that a modern agent system recreates imperial institutions.
- Public documentation publishes protocols and empty templates, never a maintainer's private cases, memory stores, credentials, or operating history.

This is the intended innovation of SXLB: historical institutional reasoning becomes a practical, inspectable control layer for modern work without pretending that metaphor is identity.
