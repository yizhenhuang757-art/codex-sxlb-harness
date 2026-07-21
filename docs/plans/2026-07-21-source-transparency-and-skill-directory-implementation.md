# Source Transparency and Skill Directory Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Explain SXLB's verified inspiration and differences, then publish a complete bilingual searchable directory of office capabilities and source relationships.

**Architecture:** A public JSON source registry augments the existing public skill inventory. A Python generator validates that registry and writes matching English and Chinese directory pages; a small browser-side filter searches the static table. Home pages link to attribution, comparison, directory, and sources before installation.

**Tech Stack:** Markdown, Jekyll/Liquid, CSS, vanilla JavaScript, Python standard library, `@humanizer-zh`, `@humanizer-eng`.

---

### Task 1: Validate the extended bilingual documentation contract

**Files:**
- Modify: `tools/check_docs_site.py`
- Modify: `tools/tests/test_check_docs_site.py`

**Step 1:** Write failing tests for three new page pairs: `why-sxlb`, `skill-directory`, and `sources`. Add tests for `validate_source_records()`: external references require an HTTPS URL; host interfaces and plugin families without a URL require a nonempty source note.

**Step 2:** Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site` and confirm failure because the pairs and validator are absent.

**Step 3:** Add the new pairs to `REQUIRED_PAIRS` and implement `validate_source_records()` with the stated rules.

**Step 4:** Re-run the tests and confirm they pass.

**Step 5:** Commit `tools/check_docs_site.py` and `tools/tests/test_check_docs_site.py` with message `Validate documentation sources and page pairs`.

### Task 2: Generate the complete bilingual skills directory

**Files:**
- Create: `docs/data/skill-source-registry.json`
- Create: `tools/generate_skill_directory.py`
- Create: `tools/tests/test_generate_skill_directory.py`
- Create: `docs/skill-directory.md`
- Create: `docs/zh-CN/skill-directory.md`

**Step 1:** Write a failing generator test using a temporary registry. It must verify skill id, office, lifecycle, source relationship, and Markdown link output; an external record missing its URL or a host record missing its source note must raise `ValueError`.

**Step 2:** Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_generate_skill_directory` and confirm failure because the generator is absent.

**Step 3:** Add verified project records for `cft0808/edict`, its dispatch architecture, Agent-Reach, Humanizer-zh, blader/humanizer, stop-slop, and the public SXLB bundle. For every other one of the public inventory's records, label the source relation accurately as public bundle, host interface, plugin family, or source URL not declared. Do not infer a URL.

**Step 4:** Implement the generator to read `PUBLIC_RECORDS` plus registry metadata, validate all entries, and generate full matching tables for both languages. Each directory must include office, skill, lifecycle, delivery status, source relation, source link or explicit absence, and use note.

**Step 5:** Run the generator test and `PYTHONDONTWRITEBYTECODE=1 python3 tools/generate_skill_directory.py`; commit the registry, generator, test, and generated pages with message `Add generated bilingual skill directory`.

### Task 3: Add source pages and client-side directory search

**Files:**
- Create: `docs/sources.md`
- Create: `docs/zh-CN/sources.md`
- Create: `docs/assets/directory-filter.js`
- Modify: `docs/_layouts/default.html`
- Modify: `docs/assets/style.css`
- Modify: `tools/tests/test_generate_skill_directory.py`

**Step 1:** Add a failing test that requires a directory search marker and language-paired source-page links in the generated pages.

**Step 2:** Run the generator test and confirm failure.

**Step 3:** Add a text filter that hides nonmatching table rows and reports the visible count. Load it only when `directory_filter: true` front matter is present. Write matching source pages that classify each project as original inspiration, method reference, public bundle, host interface, or plugin family. State that compatibility or a listed interface does not establish code derivation.

**Step 4:** Re-run the test, generator, and `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs`; confirm all pass.

**Step 5:** Commit the pages, script, layout/style updates, generator changes, and tests with message `Document sources and add directory search`.

### Task 4: Restore source attribution and add a clear comparison

**Files:**
- Create: `docs/why-sxlb.md`
- Create: `docs/zh-CN/why-sxlb.md`
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `docs/zh-CN/index.md`
- Modify: `docs/attribution.md`
- Modify: `tools/tests/test_check_docs_site.py`

**Step 1:** Add failing assertions requiring the verified Edict URL and a comparison link on both home pages. Require the comparison pages to state `independent implementation` / `独立实现` and `does not vendor or fork` / `不内置或 fork`.

**Step 2:** Run the documentation test and confirm failure.

**Step 3:** Write complete corresponding comparison pages covering: what SXLB borrows from Edict; the difference between Edict's multi-agent orchestration and SXLB's Codex skill harness; why SXLB uses text-first default governance and reviewed optional delegation; and what SXLB does not claim. Restore direct attribution near the start of README and home pages, with links to the comparison, directory, and sources before installation.

**Step 4:** Re-run the documentation test and confirm it passes.

**Step 5:** Commit affected files with message `Restore SXLB attribution and comparison`.

### Task 5: Apply bilingual editorial review and publish

**Files:**
- Modify: public English and Chinese pages under `docs/`
- Modify: `docs/ci/test-workflow.yml`

**Step 1:** Apply `@humanizer-zh` to revised Chinese pages. Keep named projects, qualifications, source labels, and links intact; remove formulaic transitions, empty importance claims, and chatbot phrasing.

**Step 2:** Apply `@humanizer-eng` to matching English pages. Preserve a clear reference register; remove promotional language, vague attribution, generic conclusions, and em/en dashes.

**Step 3:** Add directory generation and source validation to the draft CI workflow. Regenerate generated pages after the editorial pass.

**Step 4:** Run:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site tools.tests.test_generate_skill_directory
PYTHONDONTWRITEBYTECODE=1 python3 tools/generate_skill_directory.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/public-edition/sxlb/scripts:$PWD/public-edition/sxlb/tests" python3 -m unittest discover -s public-edition/sxlb/tests
```

Also run the public-boundary scan and `git diff --check`.

**Step 5:** Commit, publish the branch, merge it, and fetch the deployed English and Chinese home, comparison, directory, and source pages to verify the content.
