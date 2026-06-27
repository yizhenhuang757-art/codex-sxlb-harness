# Hanlinyuan Reference Pool

## Purpose

Define how `吏部` stores external agents, prompts, skills, and multi-agent patterns as reference talent without making them active `sxlb` authority.

`翰林院` is the reserve layer that lets the `sxlb` harness convert into multi-agent or multi-skill orchestration when needed. It can hold candidate agents, skills, prompts, workflows, and orchestration patterns from the wider market, but those candidates remain reference material until admitted, evaluated, and appointed through governance.

## Name

Use `翰林院` for the reference pool.

This is a talent and pattern reserve, not an arsenal. It belongs to `吏部` because it concerns evaluation, appointment, and promotion of agent capabilities.

When conversion into multi-agent work is justified:

- `翰林院` stores candidates.
- `吏部` evaluates capability, license, safety, and fit.
- `尚书省` dispatches appointed capabilities only when ownership and return contracts are clear.
- `门下省` reviews merges and blocks unsafe or unverified promotion.

## Location

Default local path:

```text
$SXLB_REFERENCE_POOL/
```

Suggested structure:

```text
$SXLB_REFERENCE_POOL/
  README.md
  omx/
    manifest.md
    upstream/
    extracted/
    evaluations/
```

## Status Boundary

Material in `翰林院` is reference-only.

It is not:

- an installed skill
- an active office allowlist entry
- permission to call external tools
- permission to bypass `吏部` capability scouting

## Admission Flow

External agents enter in four steps:

1. 入院: download or copy into `翰林院` as reference material.
2. 清点: record source, license, files, and intended use in a manifest.
3. 评议: classify as `可参考`, `可改写`, `需隔离`, or `不采用`.
4. 任用: only after `吏部` review may a pattern be rewritten as a local skill, protocol, or allowlist update.

## Multi-Agent Conversion Path

Reference material may become active capability only through this path:

1. `翰林院` stores the external agent/skill/pattern with source and license notes.
2. `吏部` classifies its usable role, safety boundary, required tools, and expected failure modes.
3. `刑部` or the responsible office runs dangerous-instruction, data-boundary, and license checks when needed.
4. `尚书省` may include the capability in a dispatch packet only with a clear owner, write scope, deliverable, verification method, and integrator.
5. `门下省` reviews the return and merge before any canonical rule, allowlist, or bundled skill changes.

This keeps the `sxlb` harness open to market agents and skill ecosystems while preventing unreviewed external behavior from becoming active authority.

## OMX Handling

OMX agents and prompts should first enter:

```text
$SXLB_REFERENCE_POOL/omx/
```

They should remain reference material until evaluated against local Codex Desktop tools and `sxlb` governance.

Do not install OMX agents directly into `$CODEX_SKILLS_HOME/` without a separate `吏部` promotion decision.
