# SXLB Public Edition Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Produce a GitHub-ready public edition of the `sxlb` Codex harness without leaking private paths, vault data, plugin caches, or personal workflow history.

**Architecture:** Build a staging repository, migrate sanitized reusable harness files, and publish portable workflow mechanisms with empty user-owned storage. Keep private data, private history, account stores, plugin caches, and personal-domain integrations outside the repository. Treat attribution, privacy, tests, and release blocking as first-class deliverables.

**Tech Stack:** Markdown, Python standard library scripts, unittest, GitHub CLI in a later release phase.

---

### Task 1: Confirm Public Workspace

**Files:**
- Verify: `$PUBLIC_WORKSPACE/README.md`
- Verify: `$PUBLIC_WORKSPACE/docs/`

**Step 1: List the workspace**

Run:

```bash
find "$PUBLIC_WORKSPACE" -maxdepth 3 -type f | sort
```

Expected: README and docs files are present.

**Step 2: Confirm no source migration has happened yet**

Run:

```bash
find "$PUBLIC_WORKSPACE/public-edition" -maxdepth 3 -type f | sort
```

Expected: empty or only intentional placeholder docs.

### Task 2: Migrate Sanitized Core Harness

Status: completed in this staging workspace.

**Files:**
- Copy from: `$PRIVATE_SXLB_SOURCE`
- Create under: `$PUBLIC_WORKSPACE/public-edition/sxlb`

**Step 1: Copy allowed source files**

Copy these directories only:

```text
SKILL.md
MODE.md
README.md
roles/
protocols/
templates/
hooks/
scripts/
tests/
examples/
skills/allowlist.md
skills/mapping.md
skills/skill-clans.md
skills/skill-families.md
skills/skill-clans.json
skills/family-trigger-index.json
```

Do not copy:

```text
__pycache__/
*.pyc
skill-inventory.generated.md as live data
private worklogs
plugin caches
```

**Step 2: Replace local paths**

Replace path-specific references with public placeholders:

```text
$PRIVATE_SXLB_SOURCE -> $SXLB_HOME
$PRIVATE_CASE_ROOT -> $SXLB_CASE_ROOT
$PRIVATE_SKILLS_HOME -> $CODEX_SKILLS_HOME
$PRIVATE_CODEX_SKILLS_HOME -> $CODEX_HOME/skills
```

**Step 3: Run path scan**

Run:

```bash
rg -n "personal-path|private-case-root|private-vault|private-chat-record" "$PUBLIC_WORKSPACE/public-edition"
```

Expected: no matches except intentional examples in privacy docs.

### Task 3: Add Companion Skill Strategy

**Files:**
- Create: `$PUBLIC_WORKSPACE/public-edition/companion-skills/README.md`
- Maybe copy later: `sxlb-agent-dispatch-check`

**Step 1: Document companion policy**

Record that `sxlb-agent-dispatch-check` is the only likely bundled companion skill in v0.1.0.

**Step 2: Separate portable workflows from private data**

Bundle `案卷体系`, `国史馆` index pattern, `起居郎`, `翰林院`, forced status boards, and strict external screening as protocols/templates/scripts. For `planning-with-files`, `memory-gateway`, and `guoshiguan-recall`, document optional interfaces rather than publishing private implementations or data stores.

### Task 4: Add Public Documentation

**Files:**
- Modify: `$PUBLIC_WORKSPACE/README.md`
- Create: `$PUBLIC_WORKSPACE/docs/install.md`
- Verify: `$PUBLIC_WORKSPACE/docs/attribution.md`
- Verify: `$PUBLIC_WORKSPACE/docs/privacy.md`
- Verify: `$PUBLIC_WORKSPACE/docs/skill-compatibility.md`

**Step 1: Write install notes**

Document manual skill install into a Codex skill directory and expected Python version.

**Step 2: Write attribution**

Use conservative inspiration wording for Edict/OpenClaw.

**Step 3: Write privacy and compatibility**

Separate publishable harness content from private local adapters.

### Task 5: Verify

Status: completed for the migrated source copy.

**Files:**
- Test: `$PUBLIC_WORKSPACE/public-edition/sxlb/tests`

**Step 1: Run tests**

Run:

```bash
PYTHONPATH="$PUBLIC_WORKSPACE/public-edition/sxlb/scripts" python3 -m unittest discover -s "$PUBLIC_WORKSPACE/public-edition/sxlb/tests"
```

Expected: tests pass after path rewrites are complete.

**Step 2: Run privacy scans**

Run:

```bash
rg -n "cookie|token|secret|password|api[_-]?key|personal-path|private-vault|private-case-root" "$PUBLIC_WORKSPACE"
```

Expected: only docs/checklists mention these as forbidden examples.

### Task 6: Prepare GitHub Release

**Files:**
- Create: `$PUBLIC_WORKSPACE/LICENSE`
- Create: `$PUBLIC_WORKSPACE/.github/workflows/test.yml`

**Step 1: Choose license**

MIT draft is staged as `LICENSE`; confirm final owner/name before publication.

**Step 2: Create private remote**

Completed after user confirmation:

```bash
gh repo create HYZ/codex-sxlb-harness --private --source "$PUBLIC_WORKSPACE" --remote origin --push
```

The first push was blocked by missing `workflow` scope, so the workflow was moved to `docs/ci/test-workflow.yml` as a draft and the repository was pushed without an active workflow file.
The target public path is `HYZ/codex-sxlb-harness`. If the authenticated GitHub account is not the `HYZ` namespace owner, use a private staging repository first and transfer or recreate only after logging in as an account that controls `HYZ`.

**Step 3: Public release gate**

Public switch requires:

```text
tests pass
privacy scan pass
license selected
attribution reviewed
user says publish
```

Status: ready for visibility switch after final verification. CI activation is a follow-up because it requires GitHub `workflow` scope.
