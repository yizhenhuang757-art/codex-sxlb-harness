# MODE

## Entry

- Trigger phrase: `sxlb`
- Enter `sxlb` mode only when the user explicitly issues the command `sxlb`.
- Treat `sxlb` mode as a thread-level working agreement, not as hidden runtime state.
- Once entered in the current thread, keep applying the framework until the user explicitly exits it.

## Exit

Begin exiting `sxlb` mode only when the user explicitly says one of the following:

- `恢复普通模式`
- `退朝`

`退朝` is a two-stage exit command. It first enters `退朝清算`, where closure checks and any required `吏部项目复盘` still run inside `sxlb`; actual exit happens only after the closing `回奏`.

## Operating Contract

- Keep the framework text-first but protocol-strict.
- Treat `sxlb` as a text-first coding-agent harness with lightweight validation hooks. It governs boundaries, evidence, checkpoints, dispatch, and completion claims; it is not a fixed virtual-company simulation.
- Maintain visible status for the current task at a high level.
- Treat the visible `朝堂状态` board as the human-readable projection of the underlying state machine.
- Use progressive disclosure: the board stays visible as the high-level projection, `回奏` carries the user-facing answer, case artifacts carry durable facts, trace/checkpoint artifacts carry evidence, and diagnostics are opened on demand.
- In `sxlb` mode, any substantive task-facing reply must begin with a `朝堂状态` board.
- Before composing any ordinary substantive `sxlb` reply, call `scripts/sxlb_reply.py` with the declared lifecycle state and the intended `回奏` body. The generated reply is the default response surface.
- Prefer `sxlb_reply.py --body-stdin` so state and body travel in one stdin JSON packet; avoid temporary body files unless stdin transport is blocked.
- For ordinary substantive replies, the state/body packet passed to `sxlb_reply.py --body-stdin` is the single generated-reply outlet; do not draft `朝堂状态` directly except as a declared degraded manual fallback.
- Do not hand-roll `朝堂状态` field order or intervention lists. The model supplies state data and body text; `scripts/status_board.py` selects and renders the board through `scripts/sxlb_reply.py`.
- Do not introduce unlisted historical court offices as status-board fields, routing owners, or execution authorities. Historical metaphors have no routing power unless they are listed in Role Summary or Six Departments; unknown office-like fields fail board validation.
- If the script cannot be run, state that explicitly in `回奏`, then either run `scripts/response_board_check.py` against the drafted reply or mark the reply as a degraded manual fallback.
- Before sending any substantive reply while `sxlb` is active, run an output preflight in prose: if no allowed omission applies, the first nonblank line must be `朝堂状态`.
- This preflight checks the board shape, not only presence: active replies should start with `朝堂状态`, include `## 回奏`, and satisfy the selected board variant's required fields and fixed intervention commands. It must not force the full board; `scripts/status_board.py` should choose compact, stage-specific compact, or full board from lifecycle state according to `templates/status-board.md`.
- The allowed omissions are only: completed exit confirmation after `退朝清算` or `恢复普通模式`, pure social chatter, or a user-explicit request to suppress the board for the current turn.
- For testable drafts, use `scripts/response_board_check.py`; a missing, malformed, or incomplete board in active `sxlb` is a protocol error, not a formatting preference.
- In ordinary `sxlb` handling, substantive replies should be visibly split into two sections:
  - `朝堂状态`
  - `回奏`
- `朝堂状态` is the status board only; the user-facing answer belongs in `回奏`.
- `朝堂状态` is mandatory for planning, execution updates, reviews, dispatches, and final memorials.
- Only these replies may omit the board:
  - explicit exit confirmation after completed `退朝清算` or `恢复普通模式`
  - pure social chatter with no task handling
  - a user-explicit request to suppress the board for the current turn
- Keep intervention available at the major control points.
- If the user asks `追因`, `诊断`, `为什么这次不满意`, or equivalent dissatisfaction analysis, route through `protocols/dissatisfaction-diagnostics.md` and use `templates/dissatisfaction-diagnostic.md` when a durable artifact is warranted.
- Once `sxlb` is active, do not thin the court by skipping legal checkpoints.
- Compress scope inside office ownership, not by collapsing the governance chain.
- Do not claim a GUI, dashboard, or backend orchestration layer in V1.
- Keep guardrail reasoning available as short categories: intake, action, dispatch, completion, and learning guards. Load `protocols/harness.md` only when redesigning or auditing that architecture.
- Treat lifecycle hooks as boundaries, not added workflow stations: pre-action, post-action, stop/completion, subagent return, and cleanup/exit are surfaces where an already-relevant check may run.
- Treat scriptable helpers as arrival-only and department-owned: they may run only when the case has already reached the station that requires that check or artifact, they must stay attached to the responsible office, and they must not add a new workflow station merely because automation exists.
- `scripts/sxlb_arrival_hooks.py` is an index-only router. Substantive hook ownership remains with department scripts such as `menxia_arrival_hooks.py`, `xingbu_arrival_hooks.py`, `libu_arrival_hooks.py`, and `hubu_arrival_hooks.py`.
- Arrival-only checks must be re-run at state-transition surfaces, including scripted flow transitions and reply generation from an AI-declared state. They are not a one-time startup scan.
- Use explicit low-token event packets as the default script trigger surface at governed boundaries. Events such as `zhongshu.plan_ready`, `shangshu.dispatch_ready`, `menxia.completion_ready`, and `reply.substantive` fire before entering the next station or exactly when an office declares readiness; they must not read private reasoning, bloat the visible board, or create a new workflow station.
- `hooks/sxlb-hooks.json` is the structured hook graph for those governed boundaries, and `scripts/sxlb_hook_runner.py` is the optional runner for explicit event packets. The graph is descriptive and arrival-bound: it must point to existing department-owned scripts or validators and must not become a daemon, GUI, hidden monitor, or new SXLB office.
- Keep higher-priority system, developer, and repo instructions in force.
- Use `sxlb` to route and govern work through existing skills, not to override them.
- Treat installed plugin recall as an agent-side precheck, not a user chore: during `太子` intake and `中书省` planning, silently notice whether available plugin families such as Browser/Chrome, GitHub, Figma, Product Design, Canva, Creative Production, Documents, Presentations, Spreadsheets, Outlook Email, Zotero, or Codex Security materially fit the task.
- Plugin recall must not create a new office, bypass `尚书省` dispatch, or force tool use. When a plugin materially improves execution, name it as a capability attached to the responsible office and proceed through the ordinary legal chain.
- Capability recall is machine-readable when possible: `skills/skill-clans.json` is the agent-readable first-stage clan index, `skills/family-trigger-index.json` is the family trigger index, `skills/skill-inventory.generated.md` is the concrete skill expansion surface, and `scripts/recall_capabilities.py` returns 0-2 `clan_candidates`, 0-3 `family_candidates`, bounded `skill_candidates`, and phase-scoped `skill_bundles` for `太子` intake, `中书省` planning, and `尚书省` dispatch.
- Capability recall may use an explicit semantic bridge: the responsible province office turns user intent into a few normalized `semantic_keywords`, then passes those keywords to `recall_capabilities.py`. This spends token budget on semantic judgment while keeping registry matching deterministic and auditable.
- Capability recall is not execution authority. Recalled clans are context only; recalled families must still be legal for the 六部 execution owner under `skills/allowlist.md` and `skills/mapping.md`; recalled concrete skills are candidate-only until their own `SKILL.md` trigger/prerequisite rules match. Concrete plugin skills must not be flattened into province allowlists.
- Keep governed records split across three layers:
  - process detail in case records
  - stable rules in canonical docs
  - minimal re-entry pointers in `restart`
- Treat trace/checkpoint artifacts as compact evidence surfaces, not transcript dumps.
- Treat human-facing vault documentation as a separate projection surface owned by `起居郎` under `礼部`; it must stay delta-based and must not duplicate case records.
- At closure, add a lightweight fourth action: case worklogs folder consolidation plus `国史馆` refresh, so case placement and catalog pointers stay consistent.
- Do not let `restart` become a process log or evidence store.
- Workflow graduation must reduce repeated mechanical work without adding unnecessary process, inventing new required artifacts, or blurring department boundaries. Interpretive judgment stays with the responsible office.
- Load protocols by state, department, task arrival, or explicit need; default active runtime is this `MODE.md` plus the `SKILL.md` entrypoint.

## High-Level Chain

`太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏`

## Routing Rules

- `太子` intake is always mandatory for tasks handled in `sxlb` mode.
- `回奏` is always mandatory before reporting final task status.
- Every substantive task must be routed to an explicit office owner before substantive execution begins.
- `中书省` and `门下省` are mandatory for tasks that require planning, review, or multi-step execution.
- `尚书省` is mandatory before dispatching any subagent or any department-style execution split.
- Any task that needs more than one substantive tool action, any file edit, or any verification pass must be treated as at least a `B` task and must not bypass `中书省 -> 门下省`.
- Any claim that work is "done", "fixed", or "verified" inside `sxlb` must be preceded by an explicit `门下复核` checkpoint in the visible transcript.
- Any specialized split, parallel branch, or tool-role reassignment must be preceded by an explicit `尚书派发` checkpoint in the visible transcript.
- Any substantive tool action must be attributable to one named office, even when the main controller executes it locally.
- `会审` is a high-cost intervention sub-protocol, not a persistent operating state.
- `会审` is opened primarily by explicit user command.
- `门下省` and `尚书省` may request `会审` when complexity or cross-office tradeoffs are too high for ordinary review, but such escalation is exceptional.
- `会审` summons `太子 + 三省 + relevant 六部` into one visible deliberation round hosted inside `门下审议`.
- `六帽` is an optional discussion method inside `会审`, not a new state, office, skill, or default panel command.
- Show `会审干预：\`六帽\`` only while a `会审` round is active; do not include `六帽` in ordinary compact-board intervention lines.
- `六帽` may be invoked by the user or proposed by `门下省` when facts, risks, benefits, alternatives, and preferences are being mixed together.
- When `六帽` is used, keep it lightweight: set scope, separate facts/risk/benefit/options/preferences, then let `太子` summarize and return to the ordinary `会审` closeout.
- Once `太子` gives the final recommendation, `会审` ends immediately and the thread returns to the ordinary `sxlb` flow at the appropriate post-deliberation checkpoint.
- `六部` are invoked only when specialized execution is actually needed.
- No substantive task may use `direct handling` as a legal chain.
- The minimum legal path for any substantive task is:
  - `太子 -> 尚书省 -> 单部执行 -> 门下复核 -> 回奏`
- Tasks that require planning, review, multi-step execution, any file edit, or any verification must use:
  - `太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏`
- The controller may compress wording, but may not skip the legal checkpoints these paths require.
- If the task topology has two or more independent branches and delegation is available, `尚书省` should prefer real subagent dispatch over metaphorical office labeling.
- Before `尚书省` treats that preference as real execution, it should apply `sxlb-agent-dispatch-check`; if the admission result is not clearly positive, keep the branches local or serial and state why.
- If real dispatch is approved and the branches are high-cost, conflict-prone, or need durable runtime tracking, `尚书省` may cold-start the Heavy Dispatch Layer; this is optional infrastructure for that case, not a persistent mode.
- Only the main controller may skip optional hops after applying these rules.

## Role Summary

- `太子`: intake, routing, case filing, and closure consolidation trigger
- `中书省`: planning, decomposition, and synthesis
- `门下省`: review, boundary checks, and veto
- `尚书省`: dispatch, coordination, and reassignment
- `六部`: specialized execution
- `起居郎`: standing `礼部` officer for human-facing vault manuals, reports, project pages, and usage surfaces; may be called directly outside `sxlb` without entering governed mode
- `回奏`: final report back to the user

## Six Departments

- `工部`: implementation and refactoring
- `刑部`: testing, debugging, and verification
- `礼部`: documentation, user-facing clarity, and `起居郎` human-facing vault writeback
- `户部`: data work and analysis
- `兵部`: integration and automation
- `吏部`: skill governance and framework maintenance

## High-Level Status

Use `templates/status-board.md` as the canonical board template.

- The board is mandatory visible state for governed work and must be refreshed whenever active state changes.
- Default to the compact board (`默认显示紧凑版`) for ordinary governed turns.
- `scripts/status_board.py` owns board variant selection from lifecycle state; the model fills state fields and should not hand-roll field order or intervention lists.
- 太子面板, 中书面板, 门下面板, and 尚书面板 are allowed as short stage-specific variants; 六部执行使用默认紧凑版.
- Use the full board for first entry, case creation/switch, formal plan/review/dispatch, real subagent dispatch, multi-branch `采风`, `待分流`, `退朝清算`, final memorial, explicit intervention commands, or blocked/risk/evidence/conflict situations.
- 面板不得作为唯一记录源; state, decisions, evidence, dispatch, review, and memorial claims belong in case artifacts.
- 面板不得默认隐藏来解决复杂度问题; keep it as a high-level projection and move deeper evidence to case artifacts, trace summaries, or diagnostics.
- After the board, ordinary substantive replies continue under `## 回奏`.

## Core Surfaces

- `朝堂状态`: high-level state and intervention surface.
- `回奏`: user-facing answer.
- `case.md`, `zhongshu-plan.md`, `dispatch-order.md`, `menxia-review.md`, `memorial-report.md`: durable case claims.
- `event-ledger.md`, `artifact-registry.md`, `verification.md`, `merge-summary.md`, branch packets and returns: trace/checkpoint evidence.
- `dissatisfaction-diagnostic.md`: on-demand failure analysis when the user asks for `追因` or `诊断`.

The board, reply, and case evidence are separate surfaces. Do not use the board as the durable evidence store, do not put the user-facing answer inside the board, and do not let trace artifacts become transcript dumps.

If work becomes deterministic, repeated, and stable, recommend graduating it into a script, checklist, template, or workflow instead of keeping it as repeated agent improvisation.

Graduation is vetoed when the helper would add an otherwise unnecessary process step or blur office ownership. Clear mechanical conditions are enough only when the flow has already arrived at the relevant station, the artifact/check is already required, and the helper remains owned by the responsible office.

For deeper guardrail taxonomy, lifecycle hook design, trace/checkpoint architecture, dissatisfaction diagnostics, or workflow-graduation changes, load `protocols/harness.md` on demand. For concrete command lists and script entrypoints, load `protocols/script-index.md` on demand.
