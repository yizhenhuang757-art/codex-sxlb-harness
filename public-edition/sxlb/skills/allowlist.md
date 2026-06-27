# Skill Allowlist

## Default Rule

Each office may use only its default canonical skills or family-level
capabilities unless one of these is true:

- `尚书省` explicitly names an additional already-allowlisted family or canonical skill in the dispatch order
- `吏部` updates the framework after a justified capability review
- a host-required process skill is already mandatory in the environment

Family entries are legal routing shorthands. A concrete skill inside a family is
callable only when it exists in `skill-inventory.generated.md`, matches the
task, and its own `SKILL.md` trigger/prerequisite rules are satisfied.

Reference patterns borrowed from external skill projects do not count as
allowlisted skills. Exact rule: reference patterns do not count as allowlisted skills.
They may inform checklists or terminology only when `吏部` has classified them
as a reference pattern. A reference pattern is not a callable skill and not a
change to any office allowlist.

## Precedence Rule

- Allowlist membership is the legality boundary.
- `skill-families.md` defines family meaning, lifecycle labels, `翰林院`, and delete gates.
- `skill-inventory.generated.md` is the audit surface for concrete `SKILL.md` files.
- `mapping.md` remains normative for priority and trigger conditions.
- Being on the allowlist does not mean "always use"; it means "may use when the mapping rules fit."

## Host-Level Families

These are environment-wide process constraints, not office-specific picks:

- `family:system`
- `family:superpowers`

## Province Allowlist

### 太子

- `family:sxlb-governance`
- `family:superpowers`

### 中书省

- `family:superpowers`
- `family:reasoning-research`
- `family:automation-integration`

### 门下省

- `family:superpowers`
- `family:sxlb-governance`

### 尚书省

- `family:superpowers`
- `family:sxlb-governance`

## Department Allowlist

### 工部

- `family:superpowers`
- `family:automation-integration`
- `family:design-frontend`
- `family:documents-media-data`
- `family:plugin/browser`
- `family:plugin/product-design`
- `family:skill-governance`

### 刑部

- `family:superpowers`
- `family:automation-integration`
- `family:plugin/browser`
- `family:plugin/codex-security`
- `family:sxlb-governance`

### 礼部

- `family:design-frontend`
- `family:documents-media-data`
- `family:publishing-export`
- `family:creative-media`
- `family:writing-polish`
- `family:obsidian`
- `family:gpt-record`
- `family:wiki`
- `family:communication`
- `family:toefl`
- `family:plugin/figma`
- `family:plugin/product-design`
- `family:plugin/canva`
- `family:plugin/creative-production`
- `family:plugin/documents`
- `family:plugin/pdf`
- `family:plugin/presentations`

### 户部

- `family:documents-media-data`
- `family:plugin/pdf`
- `family:daily-planning`
- `family:reading-research`
- `family:toefl`
- `family:communication`
- `family:plugin/spreadsheets`
- `family:plugin/zotero`

### 兵部

- `family:automation-integration`
- `family:plugin/chrome`
- `family:plugin/computer-use`
- `family:plugin/github`
- `family:plugin/outlook-email`

### 吏部

- `family:skill-governance`
- `family:sxlb-governance`
- `family:reference-experimental`
- `family:superpowers`

## Escalation Notes

- `吏部` may recommend new skills, but should not add them casually.
- `find-skills` should be used only when an actual office-level capability gap exists.
- `find-skills` results should be classified as `可用 / 需用 / 急用` before any install or allowlist change is proposed.
- Discovery alone does not authorize an office to self-expand its skill set.
- Installed plugins may be allowlisted at the family level after `吏部` ties them to a repeated or high-value workflow need and records the safety boundary.
- Concrete plugin skills stay in `skill-inventory.generated.md`; do not copy plugin cache contents into this daily allowlist.
- `self-improving-agent` should run after repeated review failures, repeated routing confusion, post-task retrospection, or framework maintenance cycles.
