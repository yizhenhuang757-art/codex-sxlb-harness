# Harness Protocol

Reference-only / on-demand layer. Do not load this file as part of the default active `sxlb` runtime; the default runtime is `SKILL.md + MODE.md`. Load this file when redesigning guardrails, debugging lifecycle hooks, auditing trace/checkpoint architecture, analyzing dissatisfaction diagnostics, or changing workflow-graduation rules.

## Purpose

Define `sxlb` as a practical coding-agent harness: a text-first governance layer that constrains boundaries, evidence, checkpoints, dispatch, and completion claims without pretending to be a persistent virtual company or a hidden runtime.

## Core Model

`sxlb` should be treated as:

> a text-first coding-agent harness with lightweight validation hooks.

It should not be treated as:

> a fixed virtual-company multi-agent workflow.

The framework keeps the human-facing ritual because it helps the user see where work sits, but the durable state is the case package. The visible panel is a projection; it is not the full state store.

## Harness Layers

- `朝堂状态`: current high-level state projection and intervention surface.
- `回奏`: user-facing answer, decision, or completion report.
- case artifacts: durable facts, plans, dispatch contracts, evidence, verification, and records routing.
- trace/checkpoint surfaces: compact process history through `event-ledger.md`, `artifact-registry.md`, `verification.md`, `merge-summary.md`, and branch returns.
- diagnostic surfaces: on-demand failure analysis through `protocols/dissatisfaction-diagnostics.md` and `templates/dissatisfaction-diagnostic.md`.

Do not solve overload by hiding the board by default. Solve it by keeping the board high-level and routing deeper evidence to the right artifact.

## Runtime Efficiency

Keep the hot path small:

- prefer compact event packets over rereading long protocols
- prefer `state-packet.md` before `restart.md`, `verification.md`, or long case records on resume
- keep external capability checks in explicit doctor/strict-profile paths unless the task needs those tools
- keep beginner-facing help optional; do not expand it into the owner-facing runtime path
- load this harness protocol only for redesign, debugging, audit, or workflow-graduation questions

`scripts/sxlb_state_packet.py` is the default pre-compact/resume compression surface. It does not replace durable case artifacts; it points to the minimum next reads.

Use `scripts/sxlb_harness_audit.py` when checking for redundant ceremony, repeated prose, or checks that should move behind profile/event gates.

## Guardrail Taxonomy

- intake guard: goal, scope, constraints, ambiguity, risk, success criteria, and case anchor.
- action guard: tool use, write boundary, dangerous commands, approvals, and touched-files evidence.
- dispatch guard: real subagent admission, ownership, readiness, branch contract, HITL/AFK fit, and return contract.
- completion guard: verification evidence, unresolved risks, skipped work, records routing, and completion-claim quality.
- learning guard: what may become a learning candidate, what stays case-local, and what requires promotion before becoming canonical.

When a user asks why a result failed, prefer naming the guard that failed over giving a vague apology.

## Lifecycle Hook Targets

These hooks are policy targets. Some are already partly enforced by scripts; others remain protocol-level until a safe script implementation exists.

- pre-action: confirm scope, write boundary, dangerous command policy, and required approval before risky action.
- post-action: capture touched files, evidence, observations, and ledger entries after material work.
- stop/completion: require `门下复核`, verification evidence, records routing, and unresolved-risk disclosure before final `回奏`.
- subagent return: check packet scope, return artifact, touched-files evidence, dangerous-command evidence, and merge requirements before review.
- cleanup/exit: preserve routed records and delete only unrouted `volatile-record.md` according to the existing cleanup policy.

## Arrival-Only Automation

Scripted helpers must not create new workflow stations. A helper is eligible only when the governed flow has already reached the station where the artifact or check is required.

Use this veto before graduating any helper:

- arrival reached: the current phase/state is already at the relevant station
- no workflow expansion: the helper does not add a new review, document, or report that the case would not otherwise need
- inevitable artifact/check: under the stated condition, the artifact or check is already required
- low judgment loss: the helper handles shape, fields, missing items, or fixed routing, not substantive judgment
- blocking over fabrication: missing inputs block or warn; the helper must not invent completion evidence

Department scripts own these helpers. `scripts/sxlb_arrival_hooks.py` is only an index/router and must not become a cross-office execution office.

Arrival checks run at scripted transition surfaces and reply generation surfaces, not just once at startup. For the detailed script list and command examples, load `protocols/script-index.md` on demand.

When a boundary needs a script, prefer an explicit low-token event packet over expanding the visible board. The event is a sidecar trigger emitted from a declared state such as plan-ready, dispatch-ready, completion-ready, or reply-before-emit; it must not depend on private reasoning or create a new workflow station.

## Scripted Hook Surface

Use `scripts/harness_hooks.py` and department arrival hooks for lightweight, deterministic checks. Keep script details in `protocols/script-index.md`; this file states the governance boundaries.

`hooks/sxlb-hooks.json` may describe which governed-boundary event reaches which deterministic check, and `scripts/sxlb_hook_runner.py` may execute those entries for explicit event packets. The graph and runner remain below the text protocol: they are not a daemon, not a GUI, not a new office, and not permission to bypass the responsible station.

`scripts/sxlb_case_status.py close` runs the completion hook and includes its advisories in the close result. These checks are still lightweight and evidence-based; they do not claim live filesystem monitoring.

## Stateless Role Interfaces

Offices are low-context interfaces, not virtual employees. Each office should be reconstructable from the case package.

Each office should make clear:

- input required before it can act
- actions it may take
- actions it must not take
- output artifact or visible checkpoint
- evidence needed by the next office

If an office needs memory that is not in the thread or case package, it should ask for that context or create a bounded context packet instead of improvising.

## Trace And Checkpoint Surfaces

Use these artifacts as the compact trace:

- `event-ledger.md`: lifecycle events and material transitions
- `artifact-registry.md`: what artifacts exist and whether the package is inspectable
- `verification.md`: behavior claims, commands, results, skipped checks, and residual risk
- `dispatch-order.md`: branch ownership and readiness
- `subagent-return-*.md`: real branch returns
- `merge-summary.md`: reconciliation before review
- `dissatisfaction-diagnostic.md`: on-demand post-failure analysis

The trace is not a transcript dump. It should be short enough for a future run to inspect quickly.

## Workflow Graduation

When a task becomes deterministic, repeated, and stable, `sxlb` should recommend graduating it from agent improvisation into a script, checklist, template, or workflow.

Graduation candidates include:

- repeated case-package setup
- repeated validation or cleanup checks
- stable file migration or catalog refresh work
- recurring diagnostic or review forms

Graduation does not mean every task becomes automation. Interpretive, ambiguous, and preference-heavy work should remain agent-handled with clear evidence and review.
