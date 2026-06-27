# Capability Scouting Protocol

## Purpose

Define how `吏部` should use `find-skills` and related governance judgment to scout external skills without weakening the `sxlb` framework.

## When to Trigger

`吏部` should open a capability-scouting pass only when at least one of these is true:

- an office has a repeated workflow gap that local skills do not cover well
- `尚书省` cannot cleanly dispatch a branch because the needed skill layer is missing
- `门下省` keeps finding the same evidence-quality or process-quality weakness across cases
- the user explicitly asks whether a market skill exists for a known office need

Do not trigger capability scouting just because a new skill looks interesting.

## Inputs

- the current workflow gap
- affected office or offices
- repeated failure or friction evidence when available
- current allowlist and mapping state
- representative external skill candidates
- current local installation state for the relevant skill names

Before looking outward, `吏部` should first audit these local sources:

- `$CODEX_SKILLS_HOME`
- `$CODEX_HOME/skills`
- `$CODEX_SUPERPOWERS_HOME`
- plugin-provided skill caches relevant to enabled plugins

## Required Output

`吏部` should produce one capability-scouting memo or equivalent judgment containing:

- target office
- workflow gap
- why current local skills are insufficient or costly
- candidate external skill or pattern
- whether the needed capability is already installed locally, only governed on paper, or entirely absent
- local fit assessment
- installation recommendation or non-install recommendation
- governance classification: `可用` / `需用` / `急用`
- whether the result should remain a reference pattern or become a framework change

## Classification Rules

### 可用

Use `可用` when:

- the skill appears helpful
- the gap is real but not currently blocking
- the skill may be worth borrowing as a pattern before installation

### 需用

Use `需用` when:

- the same gap is recurring
- one office has a stable ownership need
- current local handling is possible but clearly inefficient or fragile

### 急用

Use `急用` when:

- a current governed workflow is materially blocked
- repeated failures show the gap is no longer optional
- no adequate local substitute exists inside the current framework

## Adoption Rule

- `吏部` may recommend a skill after scouting.
- `吏部` may not treat discovery itself as approval.
- Installing, allowlisting, or canonizing a new skill still requires an explicit framework update.
- If the external skill is useful mainly as an idea source, record it as a reference pattern rather than adding it to the framework.
- If the needed capability already exists locally under another source tree or namespace, prefer documenting the provenance over importing an external duplicate.

## Dispatch Interaction

- `尚书省` may request a capability-scouting pass before dispatch when a branch lacks a clean legal skill path.
- Offices should not self-expand by importing external skills ad hoc.
- If a current case is time-sensitive, `尚书省` may continue with local bounded handling while `吏部` scouts in parallel, but the reason must be stated.
