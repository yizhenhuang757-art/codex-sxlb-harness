# Source Transparency and Skill Directory Design

## Purpose

Restore clear public attribution for the SXLB inspiration, explain the project's distinct design choices without overstating them, and make the skill system inspectable by office, lifecycle, and source relationship.

## Reader journey

The home page will state, before installation details, that SXLB is independently implemented and inspired by `cft0808/edict` and its task-dispatch architecture. It will link to a concise bilingual comparison page that distinguishes the projects and explains why SXLB defaults to a text-first harness with optional, reviewed delegation.

Readers who need operational detail will be able to open a bilingual directory by office. Each entry will state the role, skill, lifecycle, delivery status, source relationship, and a reference link when that link is publicly verified. Missing source metadata will be displayed as an explicit limitation rather than guessed.

## Source model

Each skill is classified as one of:

- public bundle maintained in this repository;
- optional host interface, with no claim that SXLB distributes its implementation;
- plugin-family capability supplied by the host environment;
- reference-derived skill or method with a verified upstream link;
- source URL not declared by the public package.

The public source registry will separately record project-level influences: Edict, its dispatch architecture, Agent-Reach, the English humanizer, humanizer-zh, and stop-slop. It will never infer a code lineage merely from a similar role or workflow.

## Bilingual content

English and Simplified Chinese pages will have corresponding sections, tables, claims, and links. Chinese prose will receive a `humanizer-zh` editing pass. English prose will receive a `blader/humanizer` editing pass. Both passes preserve factual claims and source labels; they remove inflated, formulaic, or vague language rather than adding personality to reference documentation.

## New pages

1. `why-sxlb.md` / `zh-CN/why-sxlb.md`: attribution, comparison, differences, and limits.
2. `skill-directory.md` / `zh-CN/skill-directory.md`: browsable office-by-office directory generated from a public metadata registry.
3. `sources.md` / `zh-CN/sources.md`: project-level source notes and direct links.

## Validation

- Extend the bilingual page-pair validator for the new pages.
- Validate that every directory record has a lifecycle and source relationship; require a URL only for entries that declare a verified external source.
- Run the public SXLB unit suite and the public-boundary scan.
- Fetch the deployed English and Chinese pages after publication and check their core attribution and directory content.
