# Status Machine

## Purpose

Define the stable state model for `sxlb` work so protocols, templates, and examples share one lifecycle.

## Task Classes

- `A`: single-office governed task
- `B`: province-reviewed and dispatched task
- `C`: full court task
- `D`: research plus engineering dual-track task

## States

- `待立案`
- `中书拟制`
- `门下审议`
- `尚书派发`
- `六部执行`
- `门下复核`
- `待回奏`
- `待分流`
- `退朝清算`
- `已回奏`
- `已暂停`
- `已中止`

## Transition Rules

- `待立案 -> 尚书派发` for `A` tasks after intake
- `待立案 -> 中书拟制` for `B`, `C`, and `D` tasks after intake
- `中书拟制 -> 门下审议` when planning output is ready
- `门下审议 -> 中书拟制` when the verdict is `封驳`
- `门下审议 -> 门下审议` when the verdict is `补证后再审` and more evidence is being gathered
- `门下审议 -> 尚书派发` for approved `B`, `C`, and `D` tasks
- `尚书派发 -> 六部执行` when dispatch is issued
- `尚书派发 -> 尚书派发` when `召回 <某部>` or `并行 <某部> <某部>` changes the current dispatch order
- `六部执行 -> 门下审议` when a major review return point is reached
- `六部执行 -> 尚书派发` when `召回 <某部>` changes active assignments
- `六部执行 -> 门下复核` when the execution package is ready for completion review
- `门下复核 -> 尚书派发` when completion review requires reroute or reassignment
- `门下复核 -> 六部执行` when more execution is required before completion
- `门下复核 -> 待回奏` when completion review passes
- `待回奏 -> 待分流` when the memorial draft and evidence package are ready
- `待分流 -> 已回奏` when process records, canonical updates, and restart updates have been routed
- any active state -> `退朝清算` on `退朝`
- `退朝清算 -> 待回奏` after the closure checklist has been completed or its skipped items have been explicitly recorded
- `待回奏 -> 已中止` when a cancellation memorial is delivered for an abandoned task
- any active state -> `已暂停` on `暂停`
- `已暂停 -> previous active state` on `恢复`
- any active state -> `待回奏` on `恢复普通模式`
- any active state -> `待回奏` on explicit task cancellation or abandonment

## Visibility Rules

- Every transition into a new active state must be reflected by a refreshed visible `朝堂状态` board in the next substantive reply.
- `中书拟制`, `门下审议`, `尚书派发`, `门下复核`, and `待回奏` may not be implicit; each must appear as an explicit visible checkpoint when used.
- If execution spans multiple turns, the board must be refreshed at least once per turn while the task remains in `六部执行`.
- A completion claim is invalid if the transcript does not show the immediately preceding required review state.

## Review Checkpoints

- planning review for `B`, `C`, and `D`
- pre-dispatch review for `B`, `C`, and `D`
- merge review for `D` after `文线` and `武线` rejoin
- final completion review for any substantive governed task
- records split checkpoint before closure for any governed task that produced durable artifacts
- exit-closure checkpoint in `退朝清算` before governed mode actually ends

## Scripted Support

Scripts may render boards, route explicit commands, and surface arrival hooks at transition points; see `protocols/harness.md` for the script index. They do not create new lifecycle states or make `会审`, `门下复核`, `待分流`, or `退朝清算` optional.

## Command Mapping

- `继续`: proceed from the current valid checkpoint
- `会审`: stay in or return to `门下审议` and open the collective deliberation sub-protocol
- `六帽`: when already in `会审`, keep the state at `门下审议` and structure the deliberation with the six-hats discussion method
- `重审`: route the active item to `门下审议`
- `录案`: keep the current lifecycle state while synchronizing `event-ledger.md`, `artifact-registry.md`, `sxlb_guard.py`, and optional catalog status through `sxlb_case_status.py`
- `召回 <某部>`: route active department work back to `尚书派发`
- `并行 <某部> <某部>`: stay in `尚书派发` until a valid parallel dispatch order is issued
- `事件簿`: show or summarize the current case event ledger without changing state
- `侍讲官 <问题>`: answer a bounded explanatory question about the current case or protocol without changing lifecycle state
- `国史馆`: show the relevant worklog/catalog pointer or refresh requirement without turning the catalog into a process log
- `翰林院`: surface or route reference material as reference-only input under `吏部`
- `起居郎`: route bounded human-facing documentation writeback through `礼部` without duplicating the case record or `国史馆`
- `退朝`: enter `退朝清算`; do not exit `sxlb` until closure checks, retrospective routing, and the closing memorial are complete

## Notes

- Only the main controller can move work between states.
- Thin-court handling is not a legal path inside active `sxlb`.
- `退朝` is a two-stage command: it initiates closure while `太子`, `吏部`, and `门下省` remain active; actual exit happens only after the closing `回奏`.
- `D` tasks may execute in parallel tracks during `六部执行`, but must merge before final review and final memorialization.
- No task should close directly from evidence gathering into `已回奏`; records must be split first.
- `朝堂状态` is still the user-facing board, but it should now reflect this state machine instead of acting as free-form commentary only.
- If the board is omitted where required, that turn is protocol-defective and the next turn should restore state visibility before new work proceeds.
- `会审` is intentionally modeled as a sub-protocol under `门下审议` rather than a separate top-level state, to preserve a lean lifecycle while still allowing structured debate.
- `会审` may be opened by explicit user command, or exceptionally at the request of `门下省` or `尚书省` when complexity makes ordinary review decision-poor.
- `六帽` is only a `会审`-local intervention prompt. It must not appear in the ordinary compact board and must not create a separate lifecycle state.
- Use `六帽` to separate facts, risks, benefits, alternatives, preferences, and process control when deliberation is mixing them together.
- A `六帽` round should end with `太子` summarizing the recommendation and returning to the normal `会审` closeout.
- Once `太子` delivers the final deliberation recommendation, `会审` must terminate explicitly and the transcript must return to the ordinary `sxlb` route without treating `会审` as a continuing state.
