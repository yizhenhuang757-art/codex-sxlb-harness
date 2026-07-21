---
layout: default
title: Why SXLB exists
lang: en
alternate: /zh-CN/why-sxlb/
description: How SXLB relates to the Edict project, where it differs, and what it does not claim.
---

# Why SXLB exists

SXLB is an independent implementation for Codex. It is inspired by [cft0808/edict](https://github.com/cft0808/edict), especially its use of 三省六部 to separate agent responsibilities and its [task dispatch architecture](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md). SXLB does not vendor or fork Edict or OpenClaw code.

The shared question is simple: when several capabilities may act on a task, how do you make planning, review, execution, and responsibility visible? The two projects answer it in different environments.

## What SXLB takes from Edict

Edict made the 三省六部 model useful for thinking about agent roles. SXLB keeps that vocabulary because it gives a task more than one point of view. A proposal can be reviewed before it is acted on. A dispatch can name an owner. A return can be checked before it becomes a final answer.

The influence is conceptual and documented. It is not a claim of shared code, a fork relationship, or the same runtime architecture.

## Where the projects differ

| Question | Edict | SXLB |
| --- | --- | --- |
| Primary form | Multi-agent orchestration system | Codex skill harness |
| Default operating mode | Specialized agents coordinate work | A text-first governed route runs in one conversation; delegation is optional |
| Control surface | Agent orchestration, dashboard, configuration, and audit-oriented operations | Case records, visible proposal and review checkpoints, dispatch packets, status boards, and portable templates |
| Delegation | A core orchestration concern | A reviewed choice: the case must justify specialization, a bounded packet, and an integrable return |
| Public package | Project runtime | Sanitized protocols, skills, templates, scripts, tests, and documentation without a maintainer's private operating history |

These differences do not establish a ranking. They describe different trade-offs.

## Why SXLB uses this shape

Codex work often begins as one conversation with a human who needs to see what is being proposed and why. SXLB therefore starts with a lightweight route: intake, proposal when needed, review, bounded execution, completion review, and report. It can bring in agents or specialist skills when the work has independent branches and the coordination cost makes sense.

This keeps three things separate that otherwise blur together: deciding what to do, doing it, and accepting the result. It also keeps private history and credentials out of the public package.

## What SXLB improves for its setting

- It makes entry, review, completion, and re-entry explicit through a case and status record.
- It treats external agents, skills, and prompts as reference material before they become active authority.
- It requires a named scope, deliverable, verification method, and return for real delegation.
- It offers a public package that can be installed without importing a maintainer's personal data or local configuration.

Those are design choices for a Codex skill harness. They are not claims that the historical offices, Edict, or any other system should behave the same way.

## Read the details

Use the [office and skill directory]({{ '/skill-directory/' | relative_url }}) to see every public inventory record and its source relationship. Read [sources and relationships]({{ '/sources/' | relative_url }}) for the full attribution boundary.
