# Skill Families

## Purpose

This is the family-level routing surface for SXLB skill governance. It groups concrete
skills into stable families so agents do not have to remember every individual
`SKILL.md`.

For human-facing navigation, use the clan overlay in `skill-clans.md` and
`skill-clans.json`. Clan is above family:

- clan: keeps the visible index small and human-usable;
- family: remains the machine-readable recall and allowlist/mapping boundary;
- concrete skill: remains the actual execution unit with its own `SKILL.md`.

Concrete skills remain separate. A family entry means:

- route at the family level during intake, planning, and dispatch;
- expand to a concrete skill only when the task needs it;
- obey the concrete skill's own `SKILL.md`, mandatory prerequisites, and tool boundaries;
- keep full coverage in `skill-inventory.generated.md`.

## Lifecycle Labels

- `active`: callable directly as a canonical skill.
- `active-via-family`: concrete skill is callable through a family route.
- `reference-only`: available as reference or vendor material, not an active route.
- `candidate-hanlinyuan`: should be moved or copied into `翰林院` before future use.
- `candidate-delete`: deletion candidate; requires migration evidence and user confirmation.
- `deprecated`: no longer routed, preserved only for history.

## Province And System Families

| Family | SXLB Positioning | Use When | Boundary |
|---|---|---|---|
| `family:system` | host | OpenAI/system skill creation, install, image generation, OpenAI docs | Host instructions still outrank SXLB |
| `family:superpowers` | host / 三省 | Engineering process methods such as TDD, debugging, verification, worktrees, plans | Use only when the user task matches the skill trigger |
| `family:sxlb-governance` | 吏部 / 太子 | SXLB mode, dispatch gate, restart/worklog recall, governed case support | Does not replace legal SXLB chain |
| `family:skill-governance` | 吏部 | Create, install, onboard, audit, improve, or document skills | Discovery is not approval to install or allowlist |

## Plugin Families

| Family | SXLB Positioning | Use When | Expansion Boundary |
|---|---|---|---|
| `family:plugin/browser` | 工部 / 刑部 | Localhost, file URL, in-app browser, screenshots, click/type, visual smoke tests | Use Browser, not shell `open`, for explicit in-app browser requests |
| `family:plugin/chrome` | 兵部 | Authenticated/profile-dependent Chrome tasks, existing tabs, uploads, external web workflows | Do not replace Chrome DevTools diagnostics |
| `family:plugin/computer-use` | 兵部 / 刑部 / 门下省 | Local Mac app UI control when no dedicated plugin or structured API can do the task | Prefer dedicated plugins first; direct UI actions follow Computer Use confirmation policy and need review for risky side effects |
| `family:plugin/github` | 兵部 | Repositories, PRs, issues, CI, publishing local changes | Follow GitHub skill and local git safety rules |
| `family:plugin/figma` | 礼部 | Figma URLs, FigJam, Slides, diagrams, design systems, Code Connect | Load mandatory Figma prerequisite skills before tool use |
| `family:plugin/product-design` | 礼部 / 工部 | Product context, ideation, audit, design QA, prototype, screenshot/live URL to code | Start with Product Design context gates when required |
| `family:plugin/canva` | 礼部 | Canva presentations, social resizing, design translation | Use only for Canva design workflows |
| `family:plugin/creative-production` | 礼部 | Campaign visuals, moodboards, ads, offers, positioning, scene/shot exploration | Exploration output is not canonical strategy without review |
| `family:plugin/documents` | 礼部 | Word/Google Docs-style document creation or editing | Use native document tools for required Office artifacts |
| `family:plugin/presentations` | 礼部 | PPT, slide decks, Google Slides-style decks | Use when deck artifact is the deliverable |
| `family:plugin/spreadsheets` | 户部 | Workbook creation, analysis, charts, Google Sheets-ready outputs | Data conclusions must stay evidence-bounded |
| `family:plugin/outlook-email` | 兵部 / 礼部 | Outlook triage, replies, task extraction, shared mailboxes, subscriptions | Draft/send boundaries follow Outlook skill rules |
| `family:plugin/zotero` | 户部 | Zotero search, metadata, BibTeX, citations, reading/research workflows | Library writes/imports require explicit confirmation |
| `family:plugin/pdf` | 礼部 / 户部 | Primary-runtime PDF reading, extraction, transformation, or creation surfaces exposed by the plugin cache | Prefer native `pdf` skill for existing-file edits unless the plugin is the dispatched route |
| `family:plugin/codex-security` | 刑部 | Security scan, diff scan, finding validation/fix, threat model, attack path | Use security skills only for security-scoped tasks |

## Personal Workflow Families

| Family | SXLB Positioning | Use When | Boundary |
|---|---|---|---|
| `family:obsidian` | 礼部 / 户部 | Markdown vault CLI, markdown, bases, canvas, defuddle, vault-native files | Respect nearest vault instructions |
| `family:daily-planning` | 太子 / 户部 | Daily review, weekly review, TickTick analytics, object scheduling | Do not replace user scheduling decisions |
| `family:toefl` | 礼部 / 户部 | TOEFL daily loop, item review, speaking score, writing sentence building | TOEFL evidence stays in TOEFL workflow surfaces |
| `family:communication` | 礼部 / 户部 | Person-centered communication evidence, timelines, source ingestion | Preserve source attribution and privacy boundaries |
| `family:gpt-record` | 礼部 | Route/digest chat record memos into the Markdown vault vault | Do not broaden into unrelated vault cleanup |
| `family:wiki` | 礼部 / 吏部 | Internal wiki candidates, harvest, calibration, weekly review | Candidate material is not canonical until promoted |
| `family:reading-research` | 户部 | Reading Lab notes, Zotero thinking sync, NotebookLM queries, chapter workbench | Keep bibliographic evidence explicit |

## Tool And Output Families

| Family | SXLB Positioning | Use When | Boundary |
|---|---|---|---|
| `family:documents-media-data` | 礼部 / 户部 | PDF, DOCX, PPTX, spreadsheet, CSV, conversion and extraction tasks | Prefer native parsers/tools over ad hoc text manipulation |
| `family:publishing-export` | 礼部 | Polished PDF, HTML/docs sites, slides, handouts, reports | Use Quarkdown when Markdown/Quarkdown can remain source |
| `family:design-frontend` | 礼部 / 工部 | Frontend design quality and UI implementation guidance | Follow app-specific design instructions |
| `family:creative-media` | 礼部 | Image generation/editing and raster creative outputs | Use image generation policy and show generated assets when useful |
| `family:writing-polish` | 礼部 | Chinese humanization, prose polish, user-facing clarity | Do not change factual claims during polish |
| `family:automation-integration` | 兵部 | Browser diagnostics, file organization, workflow orchestration, Spark mail, integrations | Avoid broad operational changes without dispatch |
| `family:reasoning-research` | 中书省 | Expert simulation and strategy framing | Use as analysis input, not final authority |
| `family:reference-experimental` | 吏部 | Ontology or experimental capability patterns | Default to reference-only until formally promoted |

## Family Versus Single-Skill Rule

Prefer family-level routing for stable workflows, even when a family currently
contains only one or two concrete skills. Promote a single skill as a named
daily route only when it has a unique safety boundary, mandatory prerequisite,
or repeated office-specific command surface that would be hidden by the family
label.

Current single-skill or small-family entries stay as families when they define a
domain lane, such as `family:creative-media`, `family:publishing-export`,
`family:writing-polish`, and `family:reasoning-research`.

## 翰林院 And Delete Gates

Send material to `翰林院` when it has reference value but should not auto-trigger:

- external agents, prompts, or platform ports;
- duplicated vendor copies such as nested multi-platform skill bundles;
- useful method patterns that lack a stable local workflow;
- experimental capabilities not yet appointed by `吏部`.

Delete only after all are true:

- no unique trigger or workflow remains;
- no current docs, scripts, or cases reference it;
- a replacement path is documented and migration is complete;
- the user has explicitly approved deletion.
