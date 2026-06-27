# Skill Compatibility Matrix

This matrix records how the public edition should talk about skills and plugin families.

## Bundled

| Component | Public strategy | Reason |
| --- | --- | --- |
| `sxlb` | Bundle after sanitization | Core harness |
| `sxlb-agent-dispatch-check` | Bundle as companion package after sanitization | Required gate for real dispatch decisions |

## Portable Workflow Layer

These are not private add-ons. They are part of the public harness and should ship as protocols, templates, hooks, and tests with empty user-owned storage.

| Workflow | Public strategy | Reason |
| --- | --- | --- |
| 案卷体系 | Bundle | Core evidence, planning, dispatch, verification, and closure substrate |
| 国史馆 | Bundle protocol and index template | Re-entry/catalog pattern is reusable; private entries are not |
| 起居郎 | Bundle protocol and candidate format | Human-facing documentation writeback is reusable |
| 翰林院 | Bundle protocol and manifest template | External project screening and promotion flow is reusable |
| Forced status panels | Bundle scripts and checks | Required visible governance surface |
| Strict external screening | Bundle scanner/review scripts and protocols | Allows safe absorption of other projects without copying them into active authority |

## Stub Or Optional Interface

| Component | Public strategy | Reason |
| --- | --- | --- |
| `planning-with-files` | Document interface / optional dependency | Useful method, but not required because `sxlb` ships its own case templates |
| `memory-gateway` | Document interface / optional dependency | Private stores are excluded; public users can connect their own memory backend |
| `guoshiguan-recall` | Document interface / optional dependency | Private history is excluded; public `国史馆` starts from an empty index |
| `best-minds` | Document interface / optional dependency | Expert-framing can support `中书省`, but the public bundle does not ship a separate implementation |
| `superpowers:*` | Document host workflow interfaces / optional dependencies | Process skills such as TDD, debugging, planning, code review, worktrees, and verification are mapped so compatible hosts can use them; their source is not bundled |

## Compatible Plugin Families

These are compatibility surfaces, not bundled source:

| Family | Public docs stance |
| --- | --- |
| GitHub | Optional release / issue / PR integration |
| Browser / Chrome | Optional runtime verification |
| Figma / Product Design / Canva | Optional design workflow support |
| Documents / Presentations / Spreadsheets | Optional artifact workflow support |
| Outlook Email | Optional operational coordination, never publish mailbox data |
| Zotero | Optional citation/library workflow, never publish user library data |
| Codex Security | Optional security scan and validation workflow |

## Rule

Discovery or compatibility does not authorize bundled publication. Every bundled skill must pass privacy scan, license review, and usefulness review.

Protocol publication is allowed when the data is excluded. For example, publish the `国史馆` catalog pattern, but never publish the maintainer's private catalog entries.
