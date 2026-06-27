# Migration Completeness Audit

Date: 2026-06-28

## Executive Finding

The public edition contains the complete non-bytecode `sxlb` harness file set from the private source, plus two public-only blank templates for portable operation.

It does not contain every related private skill implementation. That is intentional. The public edition bundles the reusable governance substrate and publishes private-data-dependent skills as optional interfaces.

## Core Harness File Parity

Comparison:

```text
private source: $PRIVATE_SXLB_SOURCE
public copy:    public-edition/sxlb
excluded:       __pycache__, *.pyc, *.pyo
```

Result:

```text
private non-bytecode files: 156
public non-bytecode files: 158
missing from public:        0
public-only additions:      2
```

Public-only additions:

- `templates/guoshiguan-index.md`
- `templates/hanlinyuan-manifest.md`

These additions are blank operating templates, not private data.

## Bundled Skills

Bundled:

- `sxlb`
- `sxlb-agent-dispatch-check`

The companion skill is included under:

```text
public-edition/companion-skills/sxlb-agent-dispatch-check
```

## Preserved Workflow Systems

The following reusable systems ship as protocols, templates, scripts, tests, or companion skill behavior:

- 案卷体系
- 国史馆 catalog pattern
- 起居郎 documentation writeback
- 翰林院 reference-pool admission
- 强制状态面板
- 严格外部项目筛查
- 门下复核 and verification gates
- 多 agent dispatch admission checks
- 翰林院-backed conversion path into multi-agent / multi-skill orchestration

## Multi-Agent Conversion Capacity

The original 三省六部 inspiration is a multi-agent framework. The public edition here is a harness: it preserves governed control, records, review, and intervention surfaces, while keeping a path to convert selected work into multi-agent or multi-skill orchestration when useful.

- `翰林院` holds reserve agents, skills, prompts, and orchestration patterns.
- `吏部` evaluates and appoints candidates.
- `尚书省` turns appointed capabilities into bounded dispatch packets.
- `sxlb-agent-dispatch-check` prevents unnecessary real-subagent overhead.
- `门下省` reviews returns, merge summaries, and verification evidence.

This means the harness can, in principle, absorb and coordinate market agents and skill ecosystems. The public edition deliberately ships the admission and review mechanism rather than bundling unreviewed external agents or claiming default always-on multi-agent execution.

## Intervention Surface

The public edition preserves the key user intervention controls:

- `会审`: full-court deliberation sub-protocol under `门下审议`.
- `侍讲官 <问题>`: bounded explanatory mode that answers a current-case or protocol question without changing lifecycle state.
- `重审`: routes the current item back to `门下省`.
- `录案`: synchronizes case status, evidence, artifact registry, and guard checks.
- `事件簿`: exposes or refreshes the case event ledger.
- `国史馆`, `翰林院`, `起居郎`: route catalog, reference-pool, and human-facing documentation actions.
- `退朝`: starts closure and records-routing checks before exiting governed mode.

Evidence in the public copy:

- `protocols/intervention.md`
- `protocols/deliberation.md`
- `protocols/status-machine.md`
- `templates/court-deliberation.md`
- `templates/status-board.md`
- `scripts/sxlb_command.py`
- `scripts/sxlb_reply.py`
- `scripts/status_board.py`
- `tests/test_sxlb_command.py`
- `tests/test_sxlb_reply.py`
- `tests/test_status_board_template.py`
- `tests/test_response_board_check.py`

## Optional Interfaces, Not Bundled Implementations

These skills are documented as optional interfaces rather than bundled full implementations:

- `planning-with-files`
- `memory-gateway`
- `guoshiguan-recall`
- `agent-reach`
- `self-improving-agent`
- `find-skills`
- `skill-onboarding`
- `plugin-creator`
- `workflow-orchestration-patterns`
- `best-minds`
- `superpowers:*` host workflow interfaces, including planning, TDD, debugging, code review, worktrees, dispatch, and verification process skills
- `frontend-design`
- `docx`
- `humanizer-zh`
- selected plugin families such as GitHub, Chrome, Documents, Spreadsheets, Presentations, Zotero, and Codex Security

Reason: their full local versions may rely on private stores, account state, plugin caches, vault paths, or personal workflow history. A downloader can install or connect their own equivalents, but should not receive the maintainer's private data.

## What A Downloader Gets

A downloader gets:

- the complete `sxlb` harness mechanics;
- the public companion dispatch gate;
- blank portable storage templates;
- public-safe skill inventory placeholders;
- tests and scanner scripts;
- documentation for optional integrations.

## Install Smoke Test

Verified by copying:

- `public-edition/sxlb` to a temporary `$CODEX_SKILLS_HOME/sxlb`
- `public-edition/companion-skills/sxlb-agent-dispatch-check` to a temporary `$CODEX_SKILLS_HOME/sxlb-agent-dispatch-check`

Checks:

- `sxlb/SKILL.md` exists
- `sxlb/MODE.md` exists
- `sxlb-agent-dispatch-check/SKILL.md` exists
- public `sxlb` unit tests run from the temporary install

Result:

```text
Ran 263 tests
OK
```

A downloader does not automatically get:

- the maintainer's private memory, 国史馆 entries, internal wiki, or case history;
- account-bound plugin access or browser/GitHub/Zotero/login state;
- TOEFL, TickTick, Zotero, communication, or wiki personal data;
- active CI until `docs/ci/test-workflow.yml` is installed under `.github/workflows/` with GitHub `workflow` scope.

## Remaining Improvements

- Add a sample case generated from `templates/case.md` to show first-run operation without private worklogs.
- Add adapter examples for user-owned `SXLB_CASE_ROOT`, `SXLB_GUOSHIGUAN_INDEX`, and `SXLB_REFERENCE_POOL`.
- Activate GitHub Actions after authenticating with a token that has `workflow` scope.
- Publish under the exact target namespace `HYZ/codex-sxlb-harness` only after that namespace is confirmed under maintainer control.
