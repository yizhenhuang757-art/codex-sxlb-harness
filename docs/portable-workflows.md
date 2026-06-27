# Portable Workflows

The public edition should feel like the same governance harness, but with the user's private evidence stores replaced by empty, user-owned locations.

## Include As Workflow

These systems are public-edition features:

| System | What ships | What does not ship |
| --- | --- | --- |
| 案卷体系 | case templates, event ledgers, artifact registries, dispatch records, verification records, review gates | private cases and worklogs |
| 国史馆 | catalog protocol, index template, refresh rule, restart pointer pattern | private history, personal catalog entries, internal wiki contents |
| 起居郎 | documentation writeback protocol, candidate format, non-redundancy rules | private vault documents and personal project pages |
| 翰林院 | reference-pool structure, admission flow, source/license/evaluation manifest | downloaded third-party projects, private experiments, plugin caches |
| Multi-agent conversion path | optional path for turning reviewed agents, skills, prompts, and patterns into appointed capabilities when needed | unreviewed external agents installed as active authority |
| 强制面板 | status-board renderer, reply wrapper, response-board validator | private runtime transcripts |
| 严格吸收 | external reference screening, dangerous-instruction scans, review-only admission | unreviewed external prompts installed as active skills |

## Multi-Agent Conversion Model

The original 三省六部 inspiration is a multi-agent framework. The public edition here is a harness: it runs as a governed, text-first control layer by default, and keeps a controlled conversion path into multi-agent or multi-skill orchestration when the task calls for it.

The conversion path is:

```text
翰林院 reference pool
  -> 吏部 admission and appointment review
  -> 尚书省 dispatch packet
  -> bounded agent/skill execution
  -> merge summary
  -> 门下复核
```

This lets the harness make use of outside agents, skills, prompts, and orchestration patterns while preserving the governance chain. It should not blindly install market agents into active authority; it should first admit them as reference material, evaluate them, rewrite or wrap the useful parts, and dispatch them only when the work genuinely benefits from parallel or specialized execution.

## Exclude As Data

The public edition must not include personal domain data or account-bound stores:

- TOEFL records
- TickTick archives
- Zotero library contents
- communication/email/WeChat history
- internal wiki source material
- private `国史馆` entries
- browser profiles, plugin caches, credentials, or local MCP config

## Public Runtime Model

Use environment variables and empty local folders instead of hard-coded personal paths:

```bash
export SXLB_HOME="$CODEX_SKILLS_HOME/sxlb"
export SXLB_CASE_ROOT="$HOME/sxlb-cases"
export SXLB_GUOSHIGUAN_INDEX="$HOME/sxlb-cases/guoshiguan/index.md"
export SXLB_REFERENCE_POOL="$HOME/sxlb-reference-pool"
```

The harness may work without all variables set, but public docs should teach these as the portable baseline.

## Compatibility Rule

If a workflow has private content, publish the protocol, template, and adapter boundary. Do not publish the content.

If a workflow requires a plugin or account, publish the compatibility surface. Do not publish plugin cache, credentials, or account data.
