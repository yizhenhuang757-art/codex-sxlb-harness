# Bilingual GitHub Pages Documentation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Publish a bilingual GitHub Pages documentation site that leads with SXLB installation and use, then explains its features, historical inspiration, and modern governance mapping.

**Architecture:** GitHub Pages builds the `docs/` directory on `main` with Jekyll. A small shared layout and stylesheet provide the same language-aware navigation for English and Simplified Chinese Markdown pages. A repository-local validator confirms language-pair structure and internal links before publishing.

**Tech Stack:** Markdown, Jekyll/GitHub Pages, Liquid templates, CSS, Python standard library.

---

### Task 1: Add a documentation-site structure validator

**Files:**
- Create: `tools/check_docs_site.py`
- Create: `tools/tests/test_check_docs_site.py`

**Step 1: Write the failing test**

Create a `unittest` case that imports `check_docs_site`, points it at a temporary incomplete docs tree, and asserts that `validate()` returns a failure mentioning a missing language counterpart. Add a second case that creates each required English/Chinese pair and verifies `validate()` succeeds.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: FAIL because `check_docs_site` does not exist.

**Step 3: Write minimal implementation**

Create `tools/check_docs_site.py` with `REQUIRED_PAIRS` containing:

```python
REQUIRED_PAIRS = (
    ("index.md", "zh-CN/index.md"),
    ("quickstart.md", "zh-CN/quickstart.md"),
    ("features.md", "zh-CN/features.md"),
    ("workflow-reference.md", "zh-CN/workflow-reference.md"),
    ("three-departments-six-ministries.md", "zh-CN/three-departments-six-ministries.md"),
    ("sxlb-mapping.md", "zh-CN/sxlb-mapping.md"),
)
```

Implement `validate(root: Path) -> list[str]` to report absent paths and empty Markdown files. Add a command-line entry point that prints each error and exits 1, otherwise prints `Documentation site structure: OK`.

**Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: PASS.

**Step 5: Commit**

```bash
git add tools/check_docs_site.py tools/tests/test_check_docs_site.py
git commit -m "Add documentation site validator"
```

### Task 2: Add the GitHub Pages shell and bilingual navigation

**Files:**
- Create: `docs/_config.yml`
- Create: `docs/_layouts/default.html`
- Create: `docs/assets/style.css`
- Create: `docs/index.md`
- Create: `docs/zh-CN/index.md`

**Step 1: Extend the failing structure test**

Add an assertion that the required pair list covers both landing pages and that the validator rejects a missing Chinese root page.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: FAIL because the Chinese landing page is absent.

**Step 3: Write minimal implementation**

Configure Jekyll in `docs/_config.yml`. The shared Liquid layout must render a compact site title, language switch link from front matter, and navigation in this order: Quick start, Outcomes, Features, Workflow reference, Historical model, SXLB mapping. The stylesheet must use readable system fonts, responsive single-column content, visible navigation focus states, and an unobtrusive callout treatment.

Write corresponding English and Chinese landing pages with front matter that selects the other language's index route. Put these sections in the same order in both pages: installation/quick start; expected outcome; feature path; deeper reading links. Link the existing `docs/install.md` from the quick-start action.

**Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs`

Expected: PASS after the remaining paired pages are added in Tasks 3–5; until then, use the validator output as the explicit missing-page checklist.

**Step 5: Commit**

```bash
git add docs/_config.yml docs/_layouts/default.html docs/assets/style.css docs/index.md docs/zh-CN/index.md
git commit -m "Add bilingual documentation site shell"
```

### Task 3: Write bilingual adoption-first documentation

**Files:**
- Create: `docs/quickstart.md`
- Create: `docs/zh-CN/quickstart.md`
- Create: `docs/features.md`
- Create: `docs/zh-CN/features.md`
- Modify: `README.md`

**Step 1: Extend the validator test**

Add a temporary docs tree fixture missing `features.md`; assert the reported error names that exact English page.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: FAIL until the validator reports the missing counterpart correctly.

**Step 3: Write minimal implementation**

Create complete, corresponding English and Simplified Chinese pages. `quickstart` covers prerequisites, copying the two bundled skills, starting a new thread, portable workspace variables, and the first governed case. `features` presents the text-first chain, status board, records, review gates, optional companion skill, and controlled multi-agent conversion. Keep the Chinese page a full counterpart, not a summary.

Change the repository README from a staging-oriented landing page to a concise public entry point. Put install and outcome links first, link to both language roots, and move long architecture explanation out to the site. Do not claim that optional GitHub Actions CI is active.

**Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs`

Expected: Missing-page errors remain only for workflow, historical model, and mapping pages.

**Step 5: Commit**

```bash
git add README.md docs/quickstart.md docs/zh-CN/quickstart.md docs/features.md docs/zh-CN/features.md tools/tests/test_check_docs_site.py
git commit -m "Document bilingual SXLB quick start and features"
```

### Task 4: Write bilingual workflow and historical-model documentation

**Files:**
- Create: `docs/workflow-reference.md`
- Create: `docs/zh-CN/workflow-reference.md`
- Create: `docs/three-departments-six-ministries.md`
- Create: `docs/zh-CN/three-departments-six-ministries.md`

**Step 1: Extend the validator test**

Add an assertion that both historical-model paths are required, so a one-language historical explanation fails validation.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: FAIL until the required historical pair is recognized by the validator fixture.

**Step 3: Write minimal implementation**

Write complete language-paired workflow reference pages covering case creation, proposal, review, execution, verification, status, and closure. Then write the historical pages: explain the pedagogical model of 中书省 (drafting), 门下省 (review/remonstrance), 尚书省 (execution coordination), and 吏、户、礼、兵、刑、工部. State that detailed authority changed across periods and that the pages introduce a historical administrative model rather than treating it as a timeless fixed constitution.

**Step 4: Run test to verify it passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs`

Expected: Only the SXLB mapping pair remains missing.

**Step 5: Commit**

```bash
git add docs/workflow-reference.md docs/zh-CN/workflow-reference.md docs/three-departments-six-ministries.md docs/zh-CN/three-departments-six-ministries.md tools/tests/test_check_docs_site.py
git commit -m "Explain SXLB workflow and historical model"
```

### Task 5: Write bilingual SXLB mapping and validate the public site

**Files:**
- Create: `docs/sxlb-mapping.md`
- Create: `docs/zh-CN/sxlb-mapping.md`
- Modify: `docs/ci/test-workflow.yml`

**Step 1: Extend the validator test**

Add a fixture with every required page present but an empty Chinese mapping page; assert `validate()` reports it as empty.

**Step 2: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site`

Expected: FAIL until empty Markdown pages are rejected.

**Step 3: Write minimal implementation**

Create complete language-paired mapping pages. Explain that SXLB borrows a governed sequence—proposal, independent review, accountable execution, verification, and recordkeeping—rather than assigning an agent a literal historical office. Describe how the framework maps concepts such as drafting, review, dispatch, six-domain service boundaries, and recordkeeping; explain the optional multi-agent conversion path and why it is not the default.

Add the documentation validator to the existing draft CI workflow without moving it to `.github/workflows/`; the workflow remains a draft until the maintainer enables it with the required token scope.

**Step 4: Run validation**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tools.tests.test_check_docs_site
PYTHONDONTWRITEBYTECODE=1 python3 tools/check_docs_site.py docs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/public-edition/sxlb/scripts:$PWD/public-edition/sxlb/tests" python3 -m unittest discover -s public-edition/sxlb/tests
Run the repository's existing public-boundary scan using the split private-marker construction in `docs/ci/test-workflow.yml`.
```

Expected: all tests pass; validator reports `Documentation site structure: OK`; the scan reports no matches.

**Step 5: Commit**

```bash
git add docs/sxlb-mapping.md docs/zh-CN/sxlb-mapping.md docs/ci/test-workflow.yml tools/tests/test_check_docs_site.py
git commit -m "Add bilingual SXLB governance mapping"
```

### Task 6: Publish the Pages source and open review

**Files:**
- Modify: GitHub Pages repository setting for `main` / `docs`

**Step 1: Inspect the final diff and branch**

Run: `git status -sb && git diff origin/main...HEAD --check`

Expected: only the bilingual documentation site, validator, README, and draft CI updates are present.

**Step 2: Push and open a draft PR**

Push `agent/bilingual-github-pages-docs` and open a draft pull request targeting `main`.

**Step 3: Enable GitHub Pages after merge**

Configure GitHub Pages to deploy from `main` and `/docs`. Verify the deployed URL and the English/Chinese landing pages after GitHub completes its build.

**Step 4: Commit restart record**

Update the public-packaging restart note with the Pages URL and publication status.
