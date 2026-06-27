# Script Index

## Purpose

Provide the detailed script index for `sxlb`. Load this file only when implementing, debugging, or auditing scripted support; ordinary governed reasoning should use `harness.md` plus the relevant office protocol.

## Reply Generation Hard Gate

For ordinary substantive `sxlb` replies, `sxlb_reply.py` is the runtime entrypoint. The model provides lifecycle state and the intended `回奏` body; the script renders `朝堂状态`, validates the board shape through `status_board.py`, and returns department-owned `arrival_hooks` when JSON output is requested.

Use a state/body packet with `sxlb_reply.py --body-stdin` as the single generated-reply outlet for ordinary replies; do not draft `朝堂状态` directly. Manual board drafting is only a declared degraded fallback after the generator is unavailable, and the draft should still be checked with `response_board_check.py`.

Do not hand-roll `朝堂状态` field order or intervention lists in normal operation. If `sxlb_reply.py` cannot be run, explicitly mark the response as a degraded manual fallback and run `response_board_check.py` against the draft whenever possible.

```bash
printf '{"state":{"task":"<task>","state":"六部执行","runtime":"active","route":"太子 -> 中书省 -> 门下省 -> 尚书省 -> 吏部","case_status":"案卷 <case-name>","case":"<case path>","caifeng":"n/a","pending":"none"},"body":"<回奏 body>"}' \
  | python3 $SXLB_HOME/scripts/sxlb_reply.py --body-stdin

printf '{"state":{"task":"<task>","state":"门下复核","runtime":"active","case_status":"无","task_class":"B","office":"刑部","target":"completion","pending":"none"},"body":"<回奏 body>"}' \
  | python3 $SXLB_HOME/scripts/sxlb_reply.py --body-stdin --json
```

Prefer `--body-stdin` for ordinary replies. It avoids temporary body files and shell-escaping large multilingual reply text. `--body` and `--body-file` remain compatibility paths.

## Arrival Hooks

- `sxlb_arrival_hooks.py`: index-only router for department-owned arrival hooks.
- `menxia_arrival_hooks.py`: `门下省` completion precheck.
- `xingbu_arrival_hooks.py`: `刑部` verification snippets and touched-files evidence.
- `libu_arrival_hooks.py`: `礼部` records-routing and `起居郎` candidates.
- `hubu_arrival_hooks.py`: `户部` external-evidence package candidates.

Arrival checks run at transition surfaces, not just startup:

- scripted transitions: `sxlb_flow.py` and `sxlb_autoflow.py` return `arrival_hooks` after deriving state.
- reply generation: `sxlb_reply.py --json` returns `reply + arrival_hooks` from declared state/phase.

## Explicit Event Router

`sxlb_event_router.py` is the thin middleware entrypoint for low-token event packets emitted at governed boundaries. It is a trigger surface, not a protocol loader and not a monitor of private reasoning.

## Capability Recall

`recall_capabilities.py` reads `skills/skill-clans.json`, `skills/family-trigger-index.json`, and `skills/skill-inventory.generated.md`. It scores clans first from the user text plus agent-derived `semantic_keywords`, then scores 0-3 `family_candidates` inside the selected clans, and finally expands bounded candidate-only concrete skills into `skill_candidates` and phase-scoped `skill_bundles`. This is an advisory recall layer for `太子`, `中书省`, and `尚书省`; it does not grant tool or plugin execution authority.

The semantic bridge is agent-owned: before deterministic registry matching, the recalling office should spend a small amount of visible reasoning to translate user intent into normalized `semantic_keywords`. The script accepts those keywords through repeatable `--semantic-keyword` arguments and records them in JSON output for review. The script does not perform semantic interpretation by itself. Clan recall reduces the search space before family recall; family remains the execution boundary; concrete skill expansion is a loading shortlist, not activation.

```bash
python3 $SXLB_HOME/scripts/recall_capabilities.py \
  --text "<user task>" \
  --semantic-keyword browser \
  --semantic-keyword screenshot \
  --phase planning --office 中书省 --skill-limit 3 --json
```

The registry is authoritative for trigger matching. Human-readable Markdown may explain the registry, but should not become the source of truth.

Events fire before entering the next station or exactly when an office declares readiness:

- `taizi.intake`: `at-ready`, routes to semantic bridge and capability recall before filing the `能力召回` field. `taizi.intake_ready` is retained as a compatibility alias.
- `reply.substantive`: `before-emit`, routes to the reply-generation hard gate.
- `zhongshu.plan_ready`: `at-ready`, routes to semantic bridge, capability recall, and `sxlb_event_router.py --check-plan-ready <case-dir> --json` before review or dispatch.
- `shangshu.dispatch_ready`: `at-ready`, routes to semantic bridge, capability recall, and `shangshu_dispatch.py <case-dir> --json` before execution begins.
- `menxia.review_ready`: `at-ready`, reuses department-owned arrival hooks as non-blocking review advisories.
- `menxia.completion_ready`: `at-ready`, reuses department-owned arrival hooks before completion claims.
- `case.pre_compact`: `before-compact`, surfaces the minimum restart packet expectation.
- `case.close`: `at-close`, surfaces completion, records-routing, restart, and catalog disposition checks.

Example:

```bash
printf 'zhongshu.plan_ready case=<case-dir> task_class=B' \
  | python3 $SXLB_HOME/scripts/sxlb_event_router.py --json

python3 $SXLB_HOME/scripts/sxlb_event_router.py --check-plan-ready <case-dir> --json
```

Keep event packets as sidecar state, not visible board content. The board remains the compact human projection; the event router only binds already-required workflow stations to their scriptable checks.

## Hook Graph Runner

`hooks/sxlb-hooks.json` is the structured hook graph, and `hooks/sxlb-hooks.schema.json` is its local schema. Validate it with:

```bash
python3 $SXLB_HOME/scripts/validate_sxlb_hooks.py --json
```

Run an event through the optional unified runner with:

```bash
printf '{"event":"zhongshu.plan_ready","case":"<case-dir>","task_class":"B"}' \
  | SXLB_PROFILE=standard python3 $SXLB_HOME/scripts/sxlb_hook_runner.py --dry-run --json
```

The runner supports `SXLB_PROFILE=minimal|standard|strict`, `SXLB_DISABLED_HOOKS`, dry-run, input truncation metadata, script path validation, per-hook timeout, and structured `pass` / `warn` / `block` / `error` results. It is a boundary-check caller over existing stations, not a new workflow station.

## Runtime Efficiency

`sxlb_action_dispatcher.py` is the low-token hot-path dispatcher. It accepts one JSON event packet and routes only the relevant checks for that event/profile:

```bash
printf '{"event":"case.resume","case":"<case-dir>"}' \
  | SXLB_PROFILE=standard python3 $SXLB_HOME/scripts/sxlb_action_dispatcher.py --json

printf '{"event":"completion_ready","case":"<case-dir>","task_class":"A"}' \
  | SXLB_PROFILE=minimal python3 $SXLB_HOME/scripts/sxlb_action_dispatcher.py --json

printf '{"event":"case.resume","case":"<case-dir>","write_paths":["$SXLB_HOME/scripts/sxlb_action_dispatcher.py"]}' \
  | SXLB_PROFILE=auto python3 $SXLB_HOME/scripts/sxlb_action_dispatcher.py --json
```

Current dispatcher events:

- `pre_action`: runs GateGuard and pre-action write/command scope checks.
- `completion_ready` / `menxia.completion_ready`: runs or skips the completion quality gate according to profile.
- `case.resume`: reads `state-packet.md` as historical-reference-only context.

Profiles:

- `minimal`: skip heavier quality gates where the event route allows it.
- `standard`: default governed checks.
- `strict`: high-risk checks; used for protected SXLB edits, destructive commands, real dispatch, and external account/config surfaces.
- `auto`: asks `sxlb_risk_scorer.py` to recommend `minimal` / `standard` / `strict` from the event packet.

Dispatcher JSON includes:

- `risk`: `sxlb_risk_scorer.py` output with `recommended_profile`, `recommended_task_class`, and reason tags.
- `quality_plan`: recommended verification commands derived from touched/write paths; it is an evidence plan, not automatic command execution.
- `metrics`: result from `sxlb_case_metrics.py`. Metrics are case-local only. With a valid `case`, the dispatcher appends `<case-dir>/runtime-metrics.jsonl`; without a case, it returns `status: skipped` and creates no global state.

Supporting system-health scripts:

- `sxlb_risk_scorer.py`: scores one event packet and recommends profile/task class.
- `sxlb_change_plan.py`: creates/checks/records planned protected SXLB changes under `<case-dir>/change-plans/`; it never applies edits.
- `sxlb_config_protection.py`: requires a matching change plan before protected SXLB config/canonical edits, including `SKILL.md`, `MODE.md`, `hooks/`, `protocols/`, `scripts/`, `skills/`, and `templates/`.
- `sxlb_case_metrics.py`: appends compact runtime metrics inside an existing case package only.

`sxlb_state_packet.py` generates a compact resume packet from an existing case package. Use it before compaction or at resume so the next run reads `state-packet.md` before long case artifacts.

```bash
python3 $SXLB_HOME/scripts/sxlb_state_packet.py <case-dir> --write <case-dir>/state-packet.md
printf '{"event":"case.pre_compact","case":"<case-dir>"}' \
  | SXLB_PROFILE=standard python3 $SXLB_HOME/scripts/sxlb_hook_runner.py --json
```

`case.pre_compact` in `hooks/sxlb-hooks.json` now calls `sxlb_state_packet.py --write-default`. The packet is a hot-path summary, not a replacement for durable case records.

`sxlb_harness_audit.py` reports advisory redundancy/overhead candidates:

```bash
python3 $SXLB_HOME/scripts/sxlb_harness_audit.py --json
```

## SXLB Help

`sxlb_help.py` is a compact user-facing command guide. It answers "what can I say next, when should I use it, and what will happen" without changing lifecycle state.

```bash
python3 $SXLB_HOME/scripts/sxlb_help.py
python3 $SXLB_HOME/scripts/sxlb_help.py --json
```

The explicit commands `帮助`, `help`, and `怎么用` route to this guide through `sxlb_command.py`.

## SXLB Doctor

`sxlb_doctor.py` is a read-only human-facing health check over existing validators and low-risk capability checks. It summarizes hook graph validity, skill inventory freshness, external capability status, and critical script availability without reading cookies, exporting tokens, mutating MCP/Chrome/GitHub/OpenCLI config, or adding a daemon.

```bash
python3 $SXLB_HOME/scripts/sxlb_doctor.py
python3 $SXLB_HOME/scripts/sxlb_doctor.py --json
```

The explicit commands `体检`, `健康检查`, and `doctor` route to this check through `sxlb_command.py`; they are convenience commands, not new SXLB states or offices.

## Harness Hooks

```bash
printf '{"phase":"completion","task_class":"B","office":"刑部"}' | python3 $SXLB_HOME/scripts/sxlb_arrival_hooks.py --json
printf '{"phase":"completion","task_class":"B","office":"刑部"}' | python3 $SXLB_HOME/scripts/xingbu_arrival_hooks.py --json
python3 $SXLB_HOME/scripts/harness_hooks.py pre-action <case-dir> --branch-id <branch> --command "<command>" --write-path <path>
python3 $SXLB_HOME/scripts/harness_hooks.py post-action <case-dir> --state <state> --office <office> --summary "<summary>" --evidence <artifact> --touched-file <path>
python3 $SXLB_HOME/scripts/harness_hooks.py route-admission <case-dir>
python3 $SXLB_HOME/scripts/harness_hooks.py subagent-return <case-dir> --branch-id <branch>
python3 $SXLB_HOME/scripts/harness_hooks.py workflow-graduation <case-dir>
python3 $SXLB_HOME/scripts/harness_hooks.py completion <case-dir>
python3 $SXLB_HOME/scripts/harness_hooks.py diagnose-dissatisfaction <case-dir> --complaint "追因：..." --output dissatisfaction-diagnostic.md
python3 $SXLB_HOME/scripts/scan_external_skill_unicode.py <path> --json
python3 $SXLB_HOME/scripts/scan_dangerous_instructions.py <path> --json
python3 $SXLB_HOME/scripts/sxlb_gateguard.py --json
python3 $SXLB_HOME/scripts/external_capability_health.py --json
```

## Coverage

- `arrival-hooks`: recommend or render candidates only after their existing workflow station is reached.
- `pre-action`: checks declared write paths and dangerous-command approval.
- `post-action`: appends hook events and structured observations.
- `route-admission`: enforces A-class fast lane boundaries.
- `subagent-return`: checks packet return, scope, touched-files, and dangerous-command evidence.
- `workflow-graduation`: warns when repeated stable work may deserve a script/checklist/template/workflow.
- `completion`: runs `sxlb_guard.py` plus harness advisories.
- `diagnose-dissatisfaction`: drafts diagnostic evidence for `门下省` review.
- `unicode-scan` / `dangerous-instruction-scan`: 刑部 validators for external skill/prompt intake.
- `gateguard`: 门下/刑部 pre-action fact-package and dangerous-command guard for protected SXLB edits.
- `external-capability-health`: 兵部/吏部 low-risk capability status check; it must not read cookies, export tokens, or mutate external configs.
