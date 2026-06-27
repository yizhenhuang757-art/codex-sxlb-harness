# HYZ / codex-sxlb-harness

Public-edition staging workspace for the `sxlb` Codex harness.

This directory is not the live private skill directory. It is a clean workspace for preparing a GitHub-ready package of the text-first 三省六部 governance harness, companion skill boundaries, public documentation, and verification checks.

Architecturally, the original 三省六部 inspiration is a multi-agent framework. This public edition is different in emphasis: `sxlb` is a harness. It keeps a governed, text-first control layer by default, while `翰林院` preserves the option to convert selected work into multi-agent or multi-skill orchestration when that is actually useful.

## Current Status

- Stage: planning and public workspace scaffold
- Source migration: completed into `public-edition/sxlb`
- Companion skill: `sxlb-agent-dispatch-check` bundled under `public-edition/companion-skills`
- CI: GitHub Actions workflow drafted at `docs/ci/test-workflow.yml`; activation requires a GitHub token with `workflow` scope
- License: MIT draft added under `HYZ`
- Target GitHub path: `HYZ/codex-sxlb-harness`
- Publication: prepared for public visibility after final verification

## Intended Repository Shape

```text
public-edition/
  sxlb/                       # sanitized harness skill package
  companion-skills/           # publishable companion skills or stubs
docs/
  audits/
  attribution.md
  install.md
  prompts/agent-install-companion-skills.md
  privacy.md
  skill-compatibility.md
  plans/
tools/
docs/ci/test-workflow.yml
LICENSE
```

## Packaging Principle

Publish the reusable governance system, not the private operating environment.

The public edition should include:

- `sxlb` runtime contract: `SKILL.md`, `MODE.md`, roles, protocols, templates, hooks, scripts, tests, and examples after sanitization
- portable workflow mechanisms: case packages, required status boards, `国史馆`-style execution memory, `起居郎` documentation writeback, `翰林院` reference-pool admission, and review/verification gates
- a conversion path into multi-agent execution when needed: `翰林院` stores reserve agents/skills/patterns, `吏部` evaluates and appoints them, `尚书省` dispatches them only when the coordination cost is justified, and `门下省` reviews their returns
- empty templates and environment-variable conventions so a user can create their own case root, catalog, and reference pool
- `sxlb-agent-dispatch-check` as a bundled companion skill for deciding when real subagents are worth the overhead
- docs explaining optional integration with GitHub, Browser/Chrome, Figma, Documents, Spreadsheets, Outlook, Zotero, and Codex Security plugin families

The public edition should not include:

- private vault paths
- private case/worklog history
- private `国史馆`, internal wiki, memory-gateway stores, or other personal knowledge contents
- full local skill inventory or personal skill paths
- plugin caches
- email, TickTick, Zotero library content
- credentials, browser profiles, or local MCP config

## Portable Workflow Scope

The public edition is intended to preserve the reusable systems, with empty storage and public-safe adapters:

| Workflow | Public edition stance |
| --- | --- |
| 案卷体系 | Bundled as templates, hooks, tests, and completion gates |
| 国史馆 | Bundled as an index pattern and template; no private history |
| 起居郎 | Bundled as a protocol for bounded human-facing documentation writeback |
| 翰林院 | Bundled as a reference-pool admission workflow for external projects |
| Multi-agent conversion path | Bundled as an optional path from reference pool -> admission -> dispatch -> merge -> review |
| Strict external screening | Bundled through review protocols and scanner scripts |
| Forced status panels | Bundled through `sxlb_reply.py`, `status_board.py`, and response-board checks |
| Intervention surface | Bundled for `会审`, `侍讲官 <问题>`, `重审`, `录案`, `事件簿`, `国史馆`, `翰林院`, `起居郎`, and `退朝` |
| Personal domains | Excluded or documented as optional integrations only |

## Attribution Draft

Inspired by the 三省六部 multi-agent orchestration pattern popularized by [cft0808/edict](https://github.com/cft0808/edict) and its [task dispatch architecture](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md). This repository is an independent Codex skill harness and does not vendor or fork Edict/OpenClaw source code.

## Verification Snapshot

- Public copy tests: `Ran 263 tests`, `OK`
- Private path scan: no matches for the private-path pattern set used in `docs/privacy.md`
- Migration audit: `docs/audits/migration-completeness.md`
- Duplicate staging directory: quarantined outside the public workspace
- CI draft: staged under `docs/ci/test-workflow.yml`; not active yet because current GitHub token cannot write workflow files
- Bytecode cleanup: `__pycache__` and `*.pyc` removed after test run
- GitHub remote: created and pushed
- License: MIT draft added
- Publication: pending final visibility switch

## Next Step

Switch the repository to public only after the target GitHub namespace `HYZ/codex-sxlb-harness` is available under an account or organization controlled by the maintainer. Enable CI later by copying `docs/ci/test-workflow.yml` to `.github/workflows/test.yml` with a GitHub token that has `workflow` scope.

For assisted local setup, copy the prompt in `docs/prompts/agent-install-companion-skills.md` into the installing Agent. It installs the bundled skills and safely discovers optional companion workflow skills without importing private data by default.
