# sxlb

`sxlb` is a local Codex skill scaffold for the 三省六部制 SXLB Codex framework.

This mode is text-first but no longer soft by default once active. It introduces a thread-level governed mode with visible status, intervention points, a legal governance chain for routing work, and an explicit records discipline.

`朝堂状态` remains the human-readable surface. The status-machine protocol defines the legal state and transition rules behind that surface, and governed task-facing turns are expected to show that board explicitly rather than treat it as optional flavor.

In ordinary use, governed replies are expected to be visibly split into two parts:

- `朝堂状态` for the board
- `回奏` for the actual answer to the user

This keeps status projection and user-facing judgment separate rather than blending them into one block.

In practice, `sxlb` is a thread-level working contract entered with the explicit command `sxlb` and exited with an explicit exit command.
Once active, substantive turns stay governed even when the task itself is small; the simplification happens through single-office dispatch, not by skipping intake, dispatch, review, or memorial steps.

It does not replace Codex's native instruction hierarchy or local skills. Instead, it routes work through a 三省六部 governance layer while composing with the existing skill ecosystem.
It is not a hidden backend auto-runner, but it is an explicit orchestration shell: when the work truly splits into independent branches and delegation is available, `尚书省` should treat those branches as real dispatch candidates rather than decorative labels.
That candidacy is gated, not automatic: `sxlb-agent-dispatch-check` is the lightweight admission skill for deciding whether real subagents are worth their cost.
In the hardened form, real subagent orchestration is document-backed rather than implied: a branch should have a work packet, a return artifact, and a merge path before it counts as a true delegated branch.
When a real dispatch becomes high-cost or multi-branch, the Heavy Dispatch Layer can be cold-started to add isolation decisions, durable branch state, verify/fix loops, and explicit shutdown without making daily `sxlb` heavier.

For contested plans or major tradeoff calls, the framework may also open a text-first collective deliberation through the explicit intervention command `会审`, which defaults to two rebuttal rounds and ends with a clear recommendation from `太子`.

The framework now separates governed records into three destinations:

- case records in task-specific worklogs
- stable conclusions in canonical docs
- minimal re-entry pointers in `restart` notes

For coding and framework-maintenance cases, `sxlb` treats external agent advice as useful only when it can become a checkable local control. The current lightweight controls are: `预算与停止条件`, `冲突取舍检查`, `行为断言/不变量` plus `测试有效性`, and explicit `未完成/未验证项`. These stop agent drift without importing a long external rules list.

Human-facing vault documentation is a separate projection surface handled by `起居郎`, a standing officer under `礼部`. It updates manuals, project pages, skill indexes, AI Reports, README files, and usage notes only when a stable change needs to be visible to a future human reader. It is delta-based by default and must not become a second `国史馆` or a default report generator.

`国史馆/总目.md` is the cross-case index for those worklogs. It should stay lightweight: case evidence, OMX-style runtime observations, branch traces, and learning candidates belong inside each case package, not in the catalog.

At closure, the framework also runs one lightweight maintenance action:

- group the finished case under an existing `case worklogs` umbrella when relation is clear (for example `zotero`, `sxlb`, `internal-wiki`, `toefl`)
- prefer `file-organizer` for this grouping pass
- refresh `国史馆/总目.md` after grouping so re-entry links stay valid

On re-entry, `restart` stays first. If it points to `<worklog>/retrospective.md`, read that before `task_plan.md`, `progress.md`, or `findings.md`.

Within an active `sxlb` case, an explicit user request to use `planning-with-files` is treated as `太子` invoking case-record support unless the user clearly assigns that responsibility elsewhere.
Within the same case, every substantive tool action must remain attributable to one named office, even if the controller executes locally without spawning a separate worker.

Host-required process skills still remain in force across the framework. Office mappings govern office-selected skills, not mandatory environment-level constraints such as `superpowers:using-superpowers`.

The office-to-skill mapping and allowlist rules live under:

- [skills/mapping.md](./skills/mapping.md)
- [skills/allowlist.md](./skills/allowlist.md)

Framework map:

- [MODE.md](./MODE.md) for runtime behavior, status shape, and entry/exit semantics
- [roles/](./roles) for office constitutions
- [protocols/](./protocols) for lifecycle and intervention rules
- [protocols/case-package.md](./protocols/case-package.md) for the minimum auditable case artifact set
- [protocols/subagent-orchestration.md](./protocols/subagent-orchestration.md) for the real subagent work-packet, return, and merge contract
- [protocols/heavy-dispatch-layer.md](./protocols/heavy-dispatch-layer.md) for cold-start real multi-agent execution, isolation, state, verify/fix, and shutdown rules
- [protocols/guoshiguan-execution-memory.md](./protocols/guoshiguan-execution-memory.md) for case-level execution logs, observations, learning candidates, and catalog boundaries
- [protocols/qijulang.md](./protocols/qijulang.md) for lightweight human-facing vault documentation writeback
- [protocols/hanlinyuan-reference-pool.md](./protocols/hanlinyuan-reference-pool.md) for `吏部` management of external agent/prompt/skill reference material
- `sxlb-agent-dispatch-check` for the real-subagent admission gate before OMX-style or parallel-agent execution
- [protocols/external-research.md](./protocols/external-research.md) for lightweight `采风` external research and `外部证据包` handling
- [protocols/capability-scouting.md](./protocols/capability-scouting.md) for how `吏部` scouts external skills and classifies office-level capability gaps
- [protocols/deliberation.md](./protocols/deliberation.md) for full-court collective deliberation
- [protocols/capability-boundaries.md](./protocols/capability-boundaries.md) for office-level read/write and canonical boundaries
- [templates/](./templates) for visible session artifacts
- [examples/](./examples) for worked examples
- [examples/session-dry-run.md](./examples/session-dry-run.md) for a full transcript-style walkthrough

Operational helpers:

- 2026-06-22 起，`sxlb` 有一层 ECC-inspired 但本地重写的 runtime automation。它不是 ECC 安装，也不是后台 daemon；它只是把已存在的状态边界接到可审计脚本上，减少重复读案卷和手工判断：
  - `hooks/sxlb-hooks.json` + `scripts/sxlb_hook_runner.py`：结构化 hook graph 和统一 runner，用于 `taizi.intake`、`zhongshu.plan_ready`、`menxia.completion_ready`、`case.pre_compact`、`case.close` 等边界。
  - `scripts/sxlb_action_dispatcher.py`：低 token event dispatcher；配合 `SXLB_PROFILE=minimal|standard|strict|auto`，只跑当前事件需要的检查。
  - `scripts/sxlb_state_packet.py`：从案卷生成短 `state-packet.md`，供 resume / pre-compact 先读，避免每次重翻长案卷。
  - `scripts/sxlb_config_protection.py`、`scripts/sxlb_change_plan.py`、`scripts/sxlb_gateguard.py`：保护 SXLB 自身规则、协议、脚本和模板的修改，要求事实包或 change plan。
  - `scripts/scan_external_skill_unicode.py`、`scripts/scan_dangerous_instructions.py`、`scripts/external_capability_health.py`：外部 skill/prompt 入藏前扫描，以及只读外部能力健康检查。
  - `scripts/sxlb_case_metrics.py`：只在案卷存在时写入案卷内 runtime metrics；没有案卷则跳过，不创建全局指标。
- 这些 hooks 只是在已有站点的抵达检查，不新增官署，不替代 `朝堂状态 + 回奏`，也不跳过 `太子 -> 中书省 -> 门下省 -> 尚书省 -> 六部 -> 门下复核 -> 回奏`。
- ECC 本身只以 reference-only 形式记录在 `$SXLB_REFERENCE_POOL/ecc/`；未安装、未执行、未复制源码。后续若要吸收具体外部 agent/skill，应另走翰林院 plan/apply/state/doctor 和刑部审查。
- `scripts/sxlb_help.py` prints a compact command guide. Use it when you are unsure what to say next:
  - `python3 $SXLB_HOME/scripts/sxlb_help.py`
  - `python3 $SXLB_HOME/scripts/sxlb_help.py --json`
- `scripts/sxlb_doctor.py` runs a read-only health check for the current SXLB setup. Use it when SXLB feels confusing or after framework edits:
  - `python3 $SXLB_HOME/scripts/sxlb_doctor.py`
  - `python3 $SXLB_HOME/scripts/sxlb_doctor.py --json`
- `scripts/validate_sxlb_hooks.py --json` validates the hook graph after changing hook definitions.
- `scripts/sxlb_action_dispatcher.py --json` is the preferred scripted hot path for resume, pre-action, completion-ready, and case metrics events; see `protocols/script-index.md` for packet examples.
- `scripts/init_case.py` scaffolds a governed case package into a worklog folder. Use `--profile lightweight` for low-risk `A` cases where inline verification is enough; use the default `full` profile for `B/C/D`, protocol, automation, or real-dispatch cases.
- Low-risk vault maintenance should usually start with `--profile lightweight`; upgrade to a full case when the work becomes batch editing, reusable template/protocol work, repeated UI regression handling, screenshot/runtime validation, or anything that must teach future runs.
- `scripts/sxlb_guard.py` validates whether a case package satisfies the minimum hard-framework rules
- `scripts/shangshu_dispatch.py` turns a reviewed dispatch order into prepared execution artifacts and a ledger-backed dispatch summary
- `scripts/subagent_dispatch.py` creates real-subagent packets, records branch returns, and builds merge summaries
- `scripts/menxia_review.py` turns a completion package into a formal review decision and blocks memorialization when evidence is still missing
- `scripts/sxlb_case_status.py close` refreshes closure records and deletes `volatile-record.md` when it is explicitly marked as a delete-on-退朝 record with no durable route
- `scripts/sxlb_flow.py` conservatively advances a case through dispatch preparation, merge refresh, and completion review while reporting the next legal step
- `tests/` contains the first verification coverage for those helpers

Capability growth stays governed:

- `吏部` owns `find-skills`, but only as a scouting and governance tool
- external skill discovery does not equal automatic adoption
- repeated office gaps should be classified as `可用 / 需用 / 急用` before the framework changes

Recommended orchestration records when delegation is real:

- `subagent-work-packet-<branch>.md` limits branch scope and context
- `subagent-return-<branch>.md` standardizes return evidence and exception reporting
- `heavy-dispatch-state.md` or `subagents/manifest.json` tracks branch status when the Heavy Dispatch Layer is active
- `merge-summary.md` gives `门下省` one reviewable integration surface
